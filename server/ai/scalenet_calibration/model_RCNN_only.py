import torch
import torch.nn as nn
from torchvision import models, transforms
# from torchvision import transforms as T
from torchvision.transforms import functional as F
import cv2
from ai.scalenet_calibration.utils.transforms import build_transforms_maskrcnn, build_transforms_yannick
from collections import namedtuple 
from termcolor import colored
import ai.scalenet_calibration.utils.model_utils as model_utils
from ai.scalenet_calibration.utils.utils_misc import *
from PIL import Image, ImageDraw
from ai.scalenet_calibration.ImageList import to_image_list
from ai.scalenet_calibration.dataset_cvpr import bins2roll, bins2vfov, bins2horizon, bins2pitch

#from ai.scalenet_calibration.utils.checkpointer import DetectronCheckpointer


class RCNN_only(nn.Module):
    """
    Main class for Generalized R-CNN. Currently supports boxes and masks.
    It consists of three main parts:
    - backbone
    - rpn
    - heads: takes the features + the proposals from the RPN and computes
        detections / masks from it.
    """

    def __init__(self, cfg, opt, printer, rank=-1):
        super(RCNN_only, self).__init__()

        self.opt = opt
        self.cfg = cfg
        self.if_print = self.opt.debug
        
        self.printer = printer
        self.rank = rank

        self.model = torch.jit.load('ai/traced/parameter_estimination.pt')
       
        self.device = self.cfg.MODEL.DEVICE
        self.rank = rank
        self.cpu_device = torch.device("cpu")
        # self.transforms = self.build_transform()
        self.palette = torch.tensor([2 ** 25 - 1, 2 ** 15 - 1, 2 ** 21 - 1])

        self.cls_names = ['horizon', 'pitch', 'roll', 'vfov', 'camH']
        self.evaltrain_trnfs_maskrcnn = build_transforms_maskrcnn(cfg, True)
        self.eval_trnfs_maskrcnn = build_transforms_maskrcnn(cfg, False)


        torch.manual_seed(12344)
        """ self.RCNN = GeneralizedRCNNRuiMod_cameraCalib(
            cfg, """ 
            #opt, modules_not_build=['roi_heads'], logger=self.logger, rank=self.rank)
   
   

    def forward(
            self,
            cv2_image):
        """
        :param images224: torch.Size([8, 3, 224, 224])
        :param image_batch_list: List(np.array)
        :return:
        """
        im_ori_RGB = Image.fromarray(cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB))

        # im_ori_RGB = Image.open(test_image_path).convert(
        #   'RGB')  # im_ori_RGB.size: [W, H]
        im = self.eval_trnfs_maskrcnn(im_ori_RGB)
        H_num, W_num = im_ori_RGB.size
        list_of_oneLargeBbox_list_cpu = model_utils.oneLargeBboxList([W_num], [
                                                                    H_num])
        list_of_oneLargeBbox_list = [bbox_list_array.to(
            self.device) for bbox_list_array in list_of_oneLargeBbox_list_cpu]
       
       
        images, image_sizes_after_transform = self.prepare_images([im])
        
        list_of_oneLargeBbox_list = [
            bbox_list.resize(size) for bbox_list, size in zip(
                list_of_oneLargeBbox_list, image_sizes_after_transform)]

        rois = convert_to_roi_format(list_of_oneLargeBbox_list)

        images = images.tensors

        output_horizon,output_pitch,output_roll,output_vfov = self.model(images,rois)

        #module = torch.jit.trace(self.RCNN,(images,rois))
        #torch.jit.save(module,'ai/traced/works2.pt')
        
        horizon_disc = output_horizon.detach().cpu().numpy().squeeze()
        pitch_disc = output_pitch.detach().cpu().numpy().squeeze()
        roll_disc = output_roll.detach().cpu().numpy().squeeze()
        vfov_disc = output_vfov.detach().cpu().numpy().squeeze()
        # distortion_disc = distortion_disc.detach().cpu().numpy().squeeze()
        vfov_disc[..., 0] = -35
        vfov_disc[..., -1] = -35

        horizon = bins2horizon(horizon_disc)
        pitch = bins2pitch(pitch_disc)
        roll = bins2roll(roll_disc)
        vfov = bins2vfov(vfov_disc)
        
        loss = namedtuple('loss',['output_horizon','output_pitch','output_roll','output_vfov'])  
    
        losses = loss(horizon,pitch,roll,vfov)

        return losses

    def prepare_images(self, inputCOCO_Image_maskrcnnTransform_list):
        # Transform so that the min size is no smaller than cfg.INPUT.MIN_SIZE_TRAIN, and the max size is no larger than cfg.INPUT.MIN_SIZE_TRAIN
        # image_batch = [self.transforms(original_image) for original_image in original_image_batch_list]
        image_batch = inputCOCO_Image_maskrcnnTransform_list
        image_sizes_after_transform = [
            (image_after.shape[2], image_after.shape[1]) for image_after in image_batch]
        # if self.training:
        #     for original_image, image_after, image_after_size in zip(inputCOCO_Image_maskrcnnTransform, image_batch, image_sizes_after_transform):
        #         self.printer.print('[generalized_rcnn_rui-prepare_images] Image sizes:', original_image.shape, '-->', image_after.shape, image_after_size)

        # [Rui] PADDING
        # convert to an ImageList, ``padded`` so that it is divisible by
        # cfg.DATALOADER.SIZE_DIVISIBILITY
        image_list = to_image_list(
            image_batch, self.cfg.DATALOADER.SIZE_DIVISIBILITY)
        # print(self.cfg.INPUT.MIN_SIZE_TRAIN, self.cfg.INPUT.MAX_SIZE_TRAIN, self.cfg.INPUT.MIN_SIZE_TEST, self.cfg.INPUT.MAX_SIZE_TEST)
        if self.training:
            self.printer.print(
                'PADDED: image_list.tensors, image_list.image_sizes (before pad):',
                image_list.tensors.shape,
                image_list.image_sizes)
        image_list = image_list.to(self.device)
        return image_list, image_sizes_after_transform

    def turn_off_print(self):
        self.if_print = False

    def turn_on_print(self):
        self.if_print = True



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


