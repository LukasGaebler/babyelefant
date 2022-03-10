import io
from typing import List

from PIL import Image
from app.ai.src.persondetection import PersonDetection
from app.ai.src.maskdetection import MaskDetection
import app.model as model
from app.model.DistanceData import DistanceData
from flask import current_app
import cv2
from loguru import logger
import numpy as np
import datetime
from app.grpc_client.grpc_client import infer,get_inference_stub
import json
from app.model.Camera import Camera

count = 0
schedules = model.schedules
db = model.db
stub = get_inference_stub()
#personDetection = PersonDetection('ai/weights/yolov5s.pt')
#maskDetection = MaskDetection('ai/weights/mask.pt')
calibrationCache = {}
    
def evaluateImage(imgs,r):
    global count
    evaluateIds = []
    
    for id, img in imgs.items():
        evaluateIds.append(int(id))
        
    with current_app.app_context():
        cameras_db = db.session.query(Camera.c_id,Camera.c_homography,Camera.c_maxdistance,Camera.c_pixelpermeter).filter(Camera.c_id.in_(tuple(evaluateIds))).all()

    cameras = {int(c.c_id):c for c in cameras_db}
    
    results = []
    if len(imgs) > 0:
        results = json.loads(infer(stub,'yolov5', imgs))

    for i, result in enumerate(results):
        schedule = cameras[evaluateIds[i]]
        distances, boxes = PersonDetection.calculateDistances(
            np.array(schedule.c_homography['matrix']), result, schedule.c_maxdistance, float(
                schedule.c_pixelpermeter))

        if schedule.c_pixelpermeter != -1 and len(distances) > 0:
            addDistanceToDatabase(distances, schedule.c_id, result)

        drawn = PersonDetection.drawBoxes(
            Image.open(io.BytesIO(imgs[str(evaluateIds[i])])), distances, boxes)
        
        drawn.save('/video/image' + str(count) + '.jpg')
        count = count + 1

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
