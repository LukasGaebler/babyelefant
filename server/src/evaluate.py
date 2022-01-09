import io
from typing import List

from PIL import Image
from ai.src.persondetection import PersonDetection
from ai.src.maskdetection import MaskDetection
import model
from model.DistanceData import DistanceData
import cv2
from loguru import logger
import numpy as np
import datetime
from grpc_client.grpc_client import infer,get_inference_stub
import json

schedules = model.schedules
db = model.db
stub = get_inference_stub()
#personDetection = PersonDetection('ai/weights/yolov5s.pt')
#maskDetection = MaskDetection('ai/weights/mask.pt')
calibrationCache = {}
    
def evaluateImage(imgs,r):
    evaluateIds = []
    
    for id, img in imgs.items():
        evaluateIds.append(int(id))

    results = []
    if len(imgs) > 0:
        results = json.loads(infer(stub,'yolov5', imgs))

    for i, result in enumerate(results):
        schedule = schedules[evaluateIds[i]]
        distances, boxes = PersonDetection.calculateDistances(
            schedule.matrix, result, schedule.maxdistance, float(
                schedule.pixelpermeter))

        calibrationCache[evaluateIds[i]] = boxes

        if schedule.pixelpermeter != -1 and len(distances) > 0:
            addDistanceToDatabase(distances, schedule.id, result)

        drawn = PersonDetection.drawBoxes(
            Image.open(io.BytesIO(imgs[str(evaluateIds[i])])), distances, boxes)

        imgByteArr = io.BytesIO()
        drawn.save(imgByteArr, format=drawn.format)
        r.set(evaluateIds[i],imgByteArr.getvalue())

    #threading.Timer(0.1, evaluateImages).start()

def addDistanceToDatabase(distances, camera_id, data):
    d_numberofpeople = len(data)

    distances_list = list(map(lambda x: x['distance'],distances))
    d_maskedpeople = sum(1 for x in data if x['class'] == 'mask')
    
    d_avg = np.mean(distances_list)
    d_min = min(distances_list)

    with db.app.app_context():
        db.session.add(DistanceData(d_min=d_min, d_avg=d_avg, d_numberofpeople=d_numberofpeople,
                           d_datetime=datetime.datetime.utcnow(), d_maskedpeople=d_maskedpeople, d_c_id=camera_id))
        db.session.commit()
