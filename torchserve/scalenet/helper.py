import torch
import torch.nn as nn
from torchvision import models, transforms
# from torchvision import transforms as T
from torchvision.transforms import functional as F
import cv2
# from ai.scalenet_calibration.utils.transforms import build_transforms_maskrcnn, build_transforms_yannick
from collections import namedtuple 
from termcolor import colored
import random
import numpy as np
from scipy.stats import norm
# import ai.scalenet_calibration.utils.model_utils as model_utils
# from ai.scalenet_calibration.utils.utils_misc import *
from PIL import Image, ImageDraw
import torchvision
import os

def cat(tensors, dim=0):
    """
    Efficient version of torch.cat that avoids a copy if there is only a single element in a list
    """
    assert isinstance(tensors, (list, tuple))
    if len(tensors) == 1:
        return tensors[0]
    return torch.cat(tensors, dim)

def convert_to_roi_format(boxes):
    concat_boxes = cat([b.bbox for b in boxes], dim=0)
    device, dtype = concat_boxes.device, concat_boxes.dtype
    ids = cat(
        [
            torch.full((len(b), 1), i, dtype=dtype, device=device)
            for i, b in enumerate(boxes)
        ],
        dim=0,
    )
    rois = torch.cat([ids, concat_boxes], dim=1)
    return rois


def build_transforms_maskrcnn():

    min_size = 600
    max_size = 1000
    # flip_horizontal_prob = 0.0
    # flip_vertical_prob = 0.0
    brightness = 0.0
    contrast = 0.0
    saturation = 0.0
    hue = 0.0

    to_bgr255 = True
    normalize_transform = Normalize(
        mean=[103.53, 116.28, 123.675], std=[57.375, 57.12, 58.395], to_bgr255=to_bgr255
    )
    color_jitter = ColorJitter(
        brightness=brightness,
        contrast=contrast,
        saturation=saturation,
        hue=hue,
    )

    transform = Compose(
        [
            color_jitter,
            Resize(min_size, max_size),
            # T.RandomHorizontalFlip(flip_horizontal_prob),
            # T.RandomVerticalFlip(flip_vertical_prob),
            ToTensor(),
            normalize_transform,
        ]
    )
    return transform

def select_device(device='', batch_size=None):
    # device = 'cpu' or '0' or '0,1,2,3'
    s = f'YOLOv5 torch {torch.__version__} '  # string
    cpu = device.lower() == 'cpu'
    if cpu:
        # force torch.cuda.is_available() = False
        os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
    elif device:  # non-cpu device requested
        os.environ['CUDA_VISIBLE_DEVICES'] = device  # set environment variable
        assert torch.cuda.is_available(
        ), f'CUDA unavailable, invalid device {device} requested'  # check availability

    cuda = not cpu and torch.cuda.is_available()
    if cuda:
        n = torch.cuda.device_count()
        if n > 1 and batch_size:  # check that batch_size is compatible with device_count
            assert batch_size % n == 0, f'batch-size {batch_size} not multiple of GPU count {n}'
        space = ' ' * len(s)
        for i, d in enumerate(device.split(',') if device else range(n)):
            p = torch.cuda.get_device_properties(i)
            # bytes to MB
            s += f"{'' if i == 0 else space}CUDA:{d} ({p.name}, {p.total_memory / 1024 ** 2}MB)\n"
    else:
        s += 'CPU\n'

    return torch.device('cuda:0' if cuda else 'cpu')

class Compose(object):
    def __init__(self, transforms):
        self.transforms = transforms

    def __call__(self, image, target=None):
        if target is not None:
            for t in self.transforms:
                image, target = t(image, target)
            return image, target
        else:
            for t in self.transforms:
                image = t(image)
            return image

    def __repr__(self):
        format_string = self.__class__.__name__ + "("
        for t in self.transforms:
            format_string += "\n"
            format_string += "    {0}".format(t)
        format_string += "\n)"
        return format_string
    
class ColorJitter(object):
    def __init__(self,
                 brightness=None,
                 contrast=None,
                 saturation=None,
                 hue=None,
                 ):
        self.color_jitter = torchvision.transforms.ColorJitter(
            brightness=brightness,
            contrast=contrast,
            saturation=saturation,
            hue=hue,)

    def __call__(self, image, target=None):
        image = self.color_jitter(image)
        if target is None:
            return image
        return image, target
    
class Resize(object):
    def __init__(self, min_size, max_size):
        if not isinstance(min_size, (list, tuple)):
            min_size = (min_size,)
        self.min_size = min_size
        self.max_size = max_size

    # modified from torchvision to add support for max size
    def get_size(self, image_size):
        w, h = image_size
        size = random.choice(self.min_size)
        max_size = self.max_size
        if max_size is not None:
            min_original_size = float(min((w, h)))
            max_original_size = float(max((w, h)))
            if max_original_size / min_original_size * size > max_size:
                size = int(
                    round(
                        max_size *
                        min_original_size /
                        max_original_size))

        if (w <= h and w == size) or (h <= w and h == size):
            return (h, w)

        if w < h:
            ow = size
            oh = int(size * h / w)
        else:
            oh = size
            ow = int(size * w / h)

        return (oh, ow)

    def __call__(self, image, target=None):
        size = self.get_size(image.size)
        image = F.resize(image, size)
        if target is None:
            return image
        target = target.resize(image.size)
        return image, target
    
class ToTensor(object):
    def __call__(self, image, target=None):
        if target is None:
            return F.to_tensor(image)
        return F.to_tensor(image), target


class Normalize(object):
    def __init__(self, mean, std, to_bgr255=True):
        self.mean = mean
        self.std = std
        self.to_bgr255 = to_bgr255

    def __call__(self, image, target=None):
        if self.to_bgr255:
            image = image[[2, 1, 0]] * 255
        image = F.normalize(image, mean=self.mean, std=self.std)
        if target is None:
            return image
        return image, target
    
def oneLargeBboxList(W_batch_array, H_batch_array):
    bbox_list_list = []
    for W, H in zip(W_batch_array, H_batch_array):
        # Following COCO annotations: (box coordinates are measured from the
        # top left image corner and are 0-indexed) #
        # http://cocodataset.org/#format-data
        bbox_list = BoxList(np.asarray([[0, 0, W, H]]), (W, H), "xywh")
        bbox_list = bbox_list.convert('xyxy')
        bbox_list_list.append(bbox_list)
    return bbox_list_list

class BoxList(object):
    """
    This class represents a set of bounding boxes.
    The bounding boxes are represented as a Nx4 Tensor.
    In order to uniquely determine the bounding boxes with respect
    to an image, we also store the corresponding image dimensions.
    They can contain extra information that is specific to each bounding box, such as
    labels.
    """

    def __init__(self, bbox, image_size, mode="xyxy"):
        device = bbox.device if isinstance(
            bbox, torch.Tensor) else torch.device("cpu")
        bbox = torch.as_tensor(bbox, dtype=torch.float32, device=device)
        if bbox.ndimension() != 2:
            raise ValueError(
                "bbox should have 2 dimensions, got {}".format(
                    bbox.ndimension()))
        if bbox.size(-1) != 4:
            raise ValueError(
                "last dimension of bbox should have a "
                "size of 4, got {}".format(bbox.size(-1))
            )
        if mode not in ("xyxy", "xywh"):
            raise ValueError("mode should be 'xyxy' or 'xywh'")

        self.bbox = bbox
        self.size = image_size  # (image_width, image_height)
        self.mode = mode
        self.extra_fields = {}

    def add_field(self, field, field_data):
        self.extra_fields[field] = field_data

    def get_field(self, field):
        return self.extra_fields[field]

    def has_field(self, field):
        return field in self.extra_fields

    def fields(self):
        return list(self.extra_fields.keys())

    def _copy_extra_fields(self, bbox):
        for k, v in bbox.extra_fields.items():
            self.extra_fields[k] = v

    def convert(self, mode):
        if mode not in ("xyxy", "xywh"):
            raise ValueError("mode should be 'xyxy' or 'xywh'")
        if mode == self.mode:
            return self
        # we only have two modes, so don't need to check
        # self.mode
        xmin, ymin, xmax, ymax = self._split_into_xyxy()
        if mode == "xyxy":
            bbox = torch.cat((xmin, ymin, xmax, ymax), dim=-1)
            bbox = BoxList(bbox, self.size, mode=mode)
        else:
            TO_REMOVE = 1
            bbox = torch.cat(
                (xmin,
                 ymin,
                 xmax -
                 xmin +
                 TO_REMOVE,
                 ymax -
                 ymin +
                 TO_REMOVE),
                dim=-
                1)
            bbox = BoxList(bbox, self.size, mode=mode)
        bbox._copy_extra_fields(self)
        return bbox

    def _split_into_xyxy(self):
        if self.mode == "xyxy":
            xmin, ymin, xmax, ymax = self.bbox.split(1, dim=-1)
            return xmin, ymin, xmax, ymax
        elif self.mode == "xywh":
            TO_REMOVE = 1
            xmin, ymin, w, h = self.bbox.split(1, dim=-1)
            return (
                xmin,
                ymin,
                xmin + (w - TO_REMOVE).clamp(min=0),
                ymin + (h - TO_REMOVE).clamp(min=0),
            )
        else:
            raise RuntimeError("Should not be here")

    def resize(self, size, *args, **kwargs):
        """
        Returns a resized copy of this bounding box

        :param size: The requested size in pixels, as a 2-tuple:
            (width, height).
        """

        ratios = tuple(float(s) / float(s_orig)
                       for s, s_orig in zip(size, self.size))
        if ratios[0] == ratios[1]:
            ratio = ratios[0]
            scaled_box = self.bbox * ratio
            bbox = BoxList(scaled_box, size, mode=self.mode)
            # bbox._copy_extra_fields(self)
            for k, v in self.extra_fields.items():
                if not isinstance(v, torch.Tensor):
                    v = v.resize(size, *args, **kwargs)
                bbox.add_field(k, v)
            return bbox

        ratio_width, ratio_height = ratios
        xmin, ymin, xmax, ymax = self._split_into_xyxy()
        scaled_xmin = xmin * ratio_width
        scaled_xmax = xmax * ratio_width
        scaled_ymin = ymin * ratio_height
        scaled_ymax = ymax * ratio_height
        scaled_box = torch.cat(
            (scaled_xmin, scaled_ymin, scaled_xmax, scaled_ymax), dim=-1
        )
        bbox = BoxList(scaled_box, size, mode="xyxy")
        # bbox._copy_extra_fields(self)
        for k, v in self.extra_fields.items():
            if not isinstance(v, torch.Tensor):
                v = v.resize(size, *args, **kwargs)
            bbox.add_field(k, v)

        return bbox.convert(self.mode)

    def transpose(self, method):
        """
        Transpose bounding box (flip or rotate in 90 degree steps)
        :param method: One of :py:attr:`PIL.Image.FLIP_LEFT_RIGHT`,
          :py:attr:`PIL.Image.FLIP_TOP_BOTTOM`, :py:attr:`PIL.Image.ROTATE_90`,
          :py:attr:`PIL.Image.ROTATE_180`, :py:attr:`PIL.Image.ROTATE_270`,
          :py:attr:`PIL.Image.TRANSPOSE` or :py:attr:`PIL.Image.TRANSVERSE`.
        """
        if method not in (FLIP_LEFT_RIGHT, FLIP_TOP_BOTTOM):
            raise NotImplementedError(
                "Only FLIP_LEFT_RIGHT and FLIP_TOP_BOTTOM implemented"
            )

        image_width, image_height = self.size
        xmin, ymin, xmax, ymax = self._split_into_xyxy()
        if method == FLIP_LEFT_RIGHT:
            TO_REMOVE = 1
            transposed_xmin = image_width - xmax - TO_REMOVE
            transposed_xmax = image_width - xmin - TO_REMOVE
            transposed_ymin = ymin
            transposed_ymax = ymax
        elif method == FLIP_TOP_BOTTOM:
            transposed_xmin = xmin
            transposed_xmax = xmax
            transposed_ymin = image_height - ymax
            transposed_ymax = image_height - ymin

        transposed_boxes = torch.cat(
            (transposed_xmin,
             transposed_ymin,
             transposed_xmax,
             transposed_ymax),
            dim=-1)
        bbox = BoxList(transposed_boxes, self.size, mode="xyxy")
        # bbox._copy_extra_fields(self)
        for k, v in self.extra_fields.items():
            if not isinstance(v, torch.Tensor):
                v = v.transpose(method)
            bbox.add_field(k, v)
        return bbox.convert(self.mode)

    def crop(self, box):
        """
        Cropss a rectangular region from this bounding box. The box is a
        4-tuple defining the left, upper, right, and lower pixel
        coordinate.
        """
        xmin, ymin, xmax, ymax = self._split_into_xyxy()
        w, h = box[2] - box[0], box[3] - box[1]
        cropped_xmin = (xmin - box[0]).clamp(min=0, max=w)
        cropped_ymin = (ymin - box[1]).clamp(min=0, max=h)
        cropped_xmax = (xmax - box[0]).clamp(min=0, max=w)
        cropped_ymax = (ymax - box[1]).clamp(min=0, max=h)

        # TODO should I filter empty boxes here?
        if False:
            is_empty = (
                cropped_xmin == cropped_xmax) | (
                cropped_ymin == cropped_ymax)

        cropped_box = torch.cat(
            (cropped_xmin, cropped_ymin, cropped_xmax, cropped_ymax), dim=-1
        )
        bbox = BoxList(cropped_box, (w, h), mode="xyxy")
        # bbox._copy_extra_fields(self)
        for k, v in self.extra_fields.items():
            if not isinstance(v, torch.Tensor):
                v = v.crop(box)
            bbox.add_field(k, v)
        return bbox.convert(self.mode)

    # Tensor-like methods

    def to(self, device):
        bbox = BoxList(self.bbox.to(device), self.size, self.mode)
        for k, v in self.extra_fields.items():
            if hasattr(v, "to"):
                v = v.to(device)
            bbox.add_field(k, v)
        return bbox

    def __getitem__(self, item):
        bbox = BoxList(self.bbox[item], self.size, self.mode)
        for k, v in self.extra_fields.items():
            bbox.add_field(k, v[item])
        return bbox

    def __len__(self):
        return self.bbox.shape[0]

    def clip_to_image(self, remove_empty=True):
        TO_REMOVE = 1
        self.bbox[:, 0].clamp_(min=0, max=self.size[0] - TO_REMOVE)
        self.bbox[:, 1].clamp_(min=0, max=self.size[1] - TO_REMOVE)
        self.bbox[:, 2].clamp_(min=0, max=self.size[0] - TO_REMOVE)
        self.bbox[:, 3].clamp_(min=0, max=self.size[1] - TO_REMOVE)
        if remove_empty:
            box = self.bbox
            keep = (box[:, 3] > box[:, 1]) & (box[:, 2] > box[:, 0])
            return self[keep]
        return self

    def area(self):
        box = self.bbox
        if self.mode == "xyxy":
            TO_REMOVE = 1
            area = (box[:, 2] - box[:, 0] + TO_REMOVE) * \
                (box[:, 3] - box[:, 1] + TO_REMOVE)
        elif self.mode == "xywh":
            area = box[:, 2] * box[:, 3]
        else:
            raise RuntimeError("Should not be here")

        return area

    def copy_with_fields(self, fields, skip_missing=False):
        bbox = BoxList(self.bbox, self.size, self.mode)
        if not isinstance(fields, (list, tuple)):
            fields = [fields]
        for field in fields:
            if self.has_field(field):
                bbox.add_field(field, self.get_field(field))
            elif not skip_missing:
                raise KeyError(
                    "Field '{}' not found in {}".format(
                        field, self))
        return bbox

    def __repr__(self):
        s = self.__class__.__name__ + "("
        s += "num_boxes={}, ".format(len(self))
        s += "image_width={}, ".format(self.size[0])
        s += "image_height={}, ".format(self.size[1])
        s += "mode={})".format(self.mode)
        return s

class ImageList(object):
    """
    Structure that holds a list of images (of possibly
    varying sizes) as a single tensor.
    This works by padding the images to the same size,
    and storing in a field the original sizes of each image
    """

    def __init__(self, tensors, image_sizes):
        """
        Arguments:
            tensors (tensor)
            image_sizes (list[tuple[int, int]])
        """
        self.tensors = tensors
        self.image_sizes = image_sizes

    def to(self, *args, **kwargs):
        cast_tensor = self.tensors.to(*args, **kwargs)
        return ImageList(cast_tensor, self.image_sizes)

    # note: _jit_wrap/_jit_unwrap only work if the sizes don't change in between
    def _jit_unwrap(self):
        return self.tensors

    def _jit_wrap(self, input_stream):
        self.tensors = input_stream[0]
        return self, input_stream[1:]


def to_image_list(tensors, size_divisible=0):
    """
    tensors can be an ImageList, a torch.Tensor or
    an iterable of Tensors. It can't be a numpy array.
    When tensors is an iterable of Tensors, it pads
    the Tensors with zeros so that they have the same
    shape
    """
    if isinstance(tensors, torch.Tensor) and size_divisible > 0:
        tensors = [tensors]

    if isinstance(tensors, ImageList):
        return tensors
    elif isinstance(tensors, torch.Tensor):
        # single tensor shape can be inferred
        if tensors.dim() == 3:
            tensors = tensors[None]
        assert tensors.dim() == 4
        image_sizes = [tensor.shape[-2:] for tensor in tensors]
        return ImageList(tensors, image_sizes)
    elif isinstance(tensors, (tuple, list)):
        max_size = tuple(max(s) for s in zip(*[img.shape for img in tensors]))

        # TODO Ideally, just remove this and let me model handle arbitrary
        # input sizs
        if size_divisible > 0:
            import math

            stride = size_divisible
            max_size = list(max_size)
            max_size[1] = int(math.ceil(max_size[1] / stride) * stride)
            max_size[2] = int(math.ceil(max_size[2] / stride) * stride)
            max_size = tuple(max_size)

        batch_shape = (len(tensors),) + max_size
        batched_imgs = tensors[0].new(*batch_shape).zero_()
        for img, pad_img in zip(tensors, batched_imgs):
            pad_img[: img.shape[0], : img.shape[1], : img.shape[2]].copy_(img)

        image_sizes = [im.shape[-2:] for im in tensors]

        return ImageList(batched_imgs, image_sizes)
    else:
        raise TypeError("Unsupported type for to_image_list: {}".format(type(tensors)))


def getBins(minval, maxval, sigma, alpha, beta, kappa):
    """Remember, bin 0 = below value! last bin mean >= maxval"""
    x = np.linspace(minval, maxval, 255)

    rv = norm(0, sigma)
    pdf = rv.pdf(x)
    pdf /= (pdf.max())
    pdf *= alpha
    pdf = pdf.max() * beta - pdf
    cumsum = np.cumsum(pdf)
    cumsum = cumsum / cumsum.max() * kappa
    cumsum -= cumsum[pdf.size // 2]

    return cumsum

pitch_bins = np.linspace(-0.6, 0.6, 255)
pitch_bins_centers = pitch_bins.copy()
pitch_bins_centers[:-1] += np.diff(pitch_bins_centers) / 2
pitch_bins_centers = np.append(pitch_bins_centers, pitch_bins[-1])

horizon_bins = np.linspace(-0.5, 0.9, 255)
horizon_bins_centers = horizon_bins.copy()
horizon_bins_centers[:-1] += np.diff(horizon_bins_centers) / 2
horizon_bins_centers = np.append(horizon_bins_centers, horizon_bins[-1])

roll_bins = getBins(-np.pi / 6, np.pi / 6, 0.5, 0.04, 1.1, np.pi)
roll_bins_centers = roll_bins.copy()
roll_bins_centers[:-1] += np.diff(roll_bins_centers) / 2
roll_bins_centers = np.append(roll_bins_centers, roll_bins[-1])

vfov_bins = np.linspace(0.2389, 1.6, 255)
vfov_bins_centers = vfov_bins.copy()
vfov_bins_centers[:-1] += np.diff(vfov_bins_centers) / 2
vfov_bins_centers = np.append(vfov_bins_centers, vfov_bins[-1])

def bins2horizon(bins):
    idxes = np.argmax(bins, axis=bins.ndim - 1)
    return horizon_bins_centers[idxes]


def bins2pitch(bins):
    idxes = np.argmax(bins, axis=bins.ndim - 1)
    return pitch_bins_centers[idxes]


def bins2roll(bins):
    idxes = np.argmax(bins, axis=bins.ndim - 1)
    return roll_bins_centers[idxes]


def bins2vfov(bins):
    idxes = np.argmax(bins, axis=bins.ndim - 1)
    return vfov_bins_centers[idxes]