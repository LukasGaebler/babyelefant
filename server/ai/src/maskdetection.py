import cv2
import numpy as np
import torch
from PIL import Image, ImageDraw, ImageFont
import itertools
import math
import torchvision.ops.boxes as bops
from utils.torch_utils import select_device
from models.experimental import attempt_load

class MaskDetection:
    """AI mask detection with distance measurement
    """

    def __init__(self, modelPath):
        device = select_device()
        half = device.type != 'cpu'
        # model = torch.load(modelPath, map_location=device)[
        #     'model'].float().fuse().eval()
        model = attempt_load(modelPath, map_location=device)

        # if half:
        # print("HALF")
        # model.half()

        self.half = half
        self.model = model.autoshape()
        self.modelPath = modelPath

    def detect(self, imageArray):
        # Predictions
        # if self.half:
        # for img in imageArray:
        #   img.half()
        pred = self.model(imageArray)
        res = [[] if v is None else v for v in pred.pred]
        return res

    def merge_with_boxes(self, boxes, predictions):
        for *box2, conf, predclass in predictions:
            for box in boxes:
                if box.get('mask') is None:
                    box1 = box['box']
                    overlap = max(box1[0], box2[0]) - min(box1[2], box2[2])
                    if overlap > 0.9:
                        box['mask'] = predclass.item()  # 1 = mask

        return boxes

    def merge_with_distances(self, distances, predictions):
        for *box2, conf, predclass in predictions:
            for box in distances:
                for name in ['box1', 'box2']:
                    box1 = box[name]
                    # overlap = (min(box1[0], box2[0]) - max(box1[2], box2[2])) * \
                    #   (min(box1[1], box2[1]) - max(box1[3], box2[3]))
                    if bops.box_iou(torch.tensor([box1]), torch.tensor([box2])) > 0.9:
                        box['mask_' + name] = predclass.item()  # 1 = mask

        return distances
