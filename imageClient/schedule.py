import cv2
import numpy as np
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

    def __init__(self, id, link, downtime_start, downtime_end):
        self.id = id
        self.link = link
        self.downtime_start = datetime.strptime(downtime_start, "%H:%M").time()
        self.downtime_end = datetime.strptime(downtime_end, "%H:%M").time()
        self.stream_mode = "youtube.com" in self.link
        
        self.video = CamGear(source=self.link,THREADED_QUEUE_MODE=False, logging=True, stream_mode=self.stream_mode).start()
        image = self.video.read()
        image = image if image is not None else np.zeros((720, 1280, 3), np.uint8)

        self.set_cache(image)
        self.internal_cache = image
        self.lastAnalyze = True
        self.isSubscribed = False

    def getRawImage(self):
        return self.internal_cache

    def setLink(self, link):
        if link != self.link:
            self.link = link
            self.video = CamGear(source=self.link,THREADED_QUEUE_MODE=False, logging=True, stream_mode=self.stream_mode).start()

    def get_frame(self):
        if hasattr(self, 'video'):
            image = self.video.read()
            
            if image is None:
                self.video = CamGear(source=self.link,THREADED_QUEUE_MODE=False, logging=True, stream_mode=self.stream_mode).start()
            else:
                self.internal_cache = image
                
        return self.internal_cache

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

