import cv2
import numpy as np
from PIL import Image
from threading import Thread
import pafy
import torch
from time import sleep
#from ai.deep_sort_pytorch.deep_sort import DeepSort
from datetime import datetime
from vidgear.gears import CamGear
import base64
import os

os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;0"

def bbox_rel(*xyxy):
    """" Calculates the relative bounding box from absolute pixel values. """
    bbox_left = min([xyxy[0].item(), xyxy[2].item()])
    bbox_top = min([xyxy[1].item(), xyxy[3].item()])
    bbox_w = abs(xyxy[0].item() - xyxy[2].item())
    bbox_h = abs(xyxy[1].item() - xyxy[3].item())
    x_c = (bbox_left + bbox_w / 2)
    y_c = (bbox_top + bbox_h / 2)
    w = bbox_w
    h = bbox_h
    return x_c, y_c, w, h


class Schedule:

    def __init__(self, id, link, matrix, user, maxdistance, pixelpermeter, event_id, downtime_start, downtime_end, deepsort_model):
        self.event_id = event_id
        self.maxdistance = maxdistance
        self.pixelpermeter = pixelpermeter
        self.id = id
        self.user = user
        self.link = link
        self.downtime_start = datetime.strptime(downtime_start, "%H:%M").time()
        self.downtime_end = datetime.strptime(downtime_end, "%H:%M").time()
        self.stream_mode = "youtube.com" in self.link

        """ self.deepsort = DeepSort(
            "ai/deep_sort_pytorch/deep_sort/deep/checkpoint/ckpt.t7",
            max_dist=0.2,
            min_confidence=0.3,
            nms_max_overlap=0.5,
            max_iou_distance=0.7,
            max_age=70,
            n_init=3,
            nn_budget=100,
            use_cuda=True,
            model=deepsort_model) """

        if self.link is not None:
            try:
                if self.link == "0":
                    self.link = 0
                self.video = CamGear(source=self.link,THREADED_QUEUE_MODE=False, stream_mode=self.stream_mode).start()

                # init cache to show when starting a stream
                image = self.video.read()
            except Exception as e:
                print(e)
                raise ValueError("Video URL not working")

            if image is None:
                image = np.zeros((720, 1280, 3), np.uint8)
        else:
            image = np.zeros((720, 1280, 3), np.uint8)

        self.set_cache(image)
        self.internal_cache = image
        self.lastAnalyze = True
        self.isSubscribed = False
        self.matrix = matrix

    def getRawImage(self):
        return self.internal_cache

    def setLink(self, link):
        if link != self.link:
            self.link = link
            self.video = CamGear(source=self.link,THREADED_QUEUE_MODE=False, stream_mode=self.stream_mode).start()

    """ def getIds(self, det, image):
        if det is not None and len(det):
            bbox_xywh = []
            confs = []
            for *xyxy, conf, cls in det:
                if cls == 0:
                    x_c, y_c, bbox_w, bbox_h = bbox_rel(*xyxy)
                    obj = [x_c, y_c, bbox_w, bbox_h]
                    bbox_xywh.append(obj)
                    confs.append([conf.item()])

                xywhs = torch.Tensor(bbox_xywh)
                confss = torch.Tensor(confs)

            if len(bbox_xywh) == 0:
                self.deepsort.increment_ages()
            else:
                xywhs = torch.Tensor(bbox_xywh)
                confss = torch.Tensor(confs)

                outputs = self.deepsort.update(
                    xywhs, confss, cv2.cvtColor(
                        np.array(image), cv2.COLOR_RGB2BGR))
                return outputs
        else:
            self.deepsort.increment_ages() """


    def __del__(self):
        if hasattr(self, 'video'):
            self.video.stop()

    def get_frame(self):
        if hasattr(self, 'video'):
            image = self.video.read()
            
            if image is None:
                self.video = CamGear(source=self.link,THREADED_QUEUE_MODE=False, stream_mode=self.stream_mode).start()
            else:
                self.internal_cache = image
                
        img = cv2.cvtColor(self.internal_cache, cv2.COLOR_BGR2RGB)
        im_pil = Image.fromarray(img)
        return im_pil

    def should_analyze(self):
        now = datetime.now().time()
        if hasattr(self, 'video') or not self.lastAnalyze:
            if (now < self.downtime_start and now > self.downtime_end):
                self.lastAnalyze = True
                return True
            else:
                return False
        else:
            return False
        
    def setInternalCache(self, image):
        self.internal_cache = cv2.imdecode(np.fromstring(
            base64.b64decode(image), np.uint8), cv2.IMREAD_COLOR)
        self.lastAnalyze = False

    def set_cache(self, image):
        ret, jpeg = cv2.imencode('.jpg', image)
        self.lastAnalyze = False
        self.cache = jpeg.tobytes()

