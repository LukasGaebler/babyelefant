import cv2
import numpy as np
import torch
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import itertools
import math
from utils.torch_utils import select_device
from models.experimental import attempt_load
import torchvision.ops.boxes as bops

device = select_device()


class PersonDetection:
    """AI mask detection with distance measurement
    """

    def __init__(self, modelPath):
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
        #imageArray = imageArray.to(device)
        pred = self.model(imageArray)
        res = [[] if v is None else v for v in pred.pred]
        return res

    @staticmethod
    def calculateDistances(
            matrix,
            predictions,
            min_distance,
            pixelpermeter):
        distances = []
        boxes = []

        masks_tensor = []
        
        for item in predictions:
            box = item['boxes']
            measurePoint = [(box[0] + box[2]) / 2,
                                box[3]]
            transPoint = compute_point_perspective_transformation(matrix, [
                measurePoint])
            distances.append(
                {"box": box, "point": transPoint[0], "mask": item['class']})
            boxes.append({"box": box})

        """ for *box, conf, predclass in predictions:
            if predclass == 0:
                mask = None
                box_tensor = torch.tensor([box])
                #personId = None
                for i, idbox in enumerate(ids):
                    overlap = max(box[0], idbox[0]) - min(box[2], idbox[2])
                    if overlap > 0.8:
                        ids = np.delete(ids, i, 0)
                        personId = idbox[4]
                        break

                for item in masks_tensor:
                    if bops.box_iou(item[0], box_tensor) > 0.05:
                        mask = item[1]
                        break

                measurePoint = [(box[0] + box[2]) / 2,
                                box[3]]
                transPoint = compute_point_perspective_transformation(matrix, [
                    measurePoint])
                distances.append(
                    {"box": box, "point": transPoint[0], "mask": mask})
                boxes.append({"box": box}) """

        output = []

        for i, pair in enumerate(itertools.combinations(distances, r=2)):
            distance = (math.sqrt((pair[0]['point'][0] -
                                   pair[1]['point'][0])**2 +
                                  (pair[0]['point'][1] -
                                   pair[1]['point'][1])**2)) / pixelpermeter
            if distance < min_distance:
                output.append({"box1": pair[0]['box'],
                               "box2": pair[1]['box'],
                               "distance": distance,
                               "mask_box1": pair[0]['mask'],
                               "mask_box2": pair[1]['mask']})

        return output, boxes

    @staticmethod
    def drawBoxes(image, distances, boxes):
        font = ImageFont.truetype("arial.ttf", 20)
        alreadyDrawn = []

        """ for *box, conf, predclass in masks:
            mask = Image.new('L', image.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.rectangle([ (box[0],box[1]), (box[2],box[3]) ], fill=255)
            blurred = image.filter(ImageFilter.GaussianBlur(50))
            image.paste(blurred, mask=mask)
            #ImageDraw.Draw(image).rectangle(box, fill=(
            #        255, 0, 0, 255)) """

        width, height = image.size

        for distance in distances:
            # Skip if box is bigger than half the screen
            if ((distance['box1'][2] -
                 distance['box1'][0]) > (width /
                                         2)) or ((distance['box2'][2] -
                                                  distance['box2'][0]) > (width /
                                                                          2)):
                continue

            box1Middle = [(distance['box1'][0] + distance['box1'][2]) / 2,
                          (distance['box1'][1] + distance['box1'][3]) / 2]

            box2Middle = [(distance['box2'][0] + distance['box2'][2]) / 2,
                          (distance['box2'][1] + distance['box2'][3]) / 2]

            ImageDraw.Draw(image).line(
                (box1Middle[0], box1Middle[1], box2Middle[0], box2Middle[1]), fill=(
                    255, 0, 0, 255), width=5)

            for name in ['box1', 'box2']:
                if distance[name] not in alreadyDrawn:
                    if distance.get('mask_' + name) is not None:
                        if distance['mask_' + name] == 1:
                            ImageDraw.Draw(image).rectangle(
                                distance[name], fill=(255, 165, 0, 255))
                            alreadyDrawn.append(distance[name])
                        else:
                            ImageDraw.Draw(image).rectangle(
                                distance[name], fill=(255, 0, 0, 255))
                            alreadyDrawn.append(distance[name])
                    else:
                        ImageDraw.Draw(image).rectangle(distance[name], fill=(
                            255, 0, 0, 255))
                        alreadyDrawn.append(distance[name])


        for box in boxes:
            if box['box'] not in alreadyDrawn and (
                    (box['box'][2] - box['box'][0]) < (width / 2)):
                ImageDraw.Draw(image).rectangle(box['box'], fill=(
                    0, 255, 0, 255))
                alreadyDrawn.append(box['box'])

        return image


def compute_point_perspective_transformation(matrix, list_downoids):
    list_points_to_detect = np.float32(torch.tensor(
        list_downoids, device='cpu')).reshape(-1, 1, 2)
    transformed_points = cv2.perspectiveTransform(
        list_points_to_detect, matrix)

    transformed_points_list = list()
    for i in range(0, transformed_points.shape[0]):
        transformed_points_list.append(
            [transformed_points[i][0][0], transformed_points[i][0][1]])
    return transformed_points_list
