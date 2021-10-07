from ai.src.persondetection import PersonDetection
from ai.src.maskdetection import MaskDetection
import model
from model.DistanceData import DistanceData
import cv2
from loguru import logger
import numpy as np
import datetime

schedules = model.schedules
db = model.db
personDetection = PersonDetection('ai/weights/yolov5s.pt')
maskDetection = MaskDetection('ai/weights/mask.pt')
calibrationCache = {}


def evaluateImages():
    evaluate = []
    images = []
    evaluateIds = []
    for i, camera in list(schedules.items()):
        image = camera.get_frame()
        if camera.should_analyze():
            evaluate.append(image)
            images.append(image)
            evaluateIds.append(i)

    results = []
    if len(evaluate) > 0:
        results = list(zip(personDetection.detect(
            evaluate), maskDetection.detect(evaluate)))

    for i, result in enumerate(results):
        schedule = schedules[evaluateIds[i]]
        #ids = schedule.getIds(result[0], evaluate[i])
        distances, boxes = personDetection.calculateDistances(
            schedule.matrix, result[0], None, schedule.maxdistance, float(
                schedule.pixelpermeter), result[1])

        #boxes = maskDetection.merge_with_boxes(boxes, result[1])
        #distances = maskDetection.merge_with_distances(distances, result[1])

        calibrationCache[evaluateIds[i]] = boxes

        if schedule.pixelpermeter != -1 and len(distances) > 2:
            addDistanceToDatabase(distances, schedule.id, result)

        if schedule.isSubscribed:
            drawn = personDetection.drawBoxes(
                images[i], distances, boxes, result[1])
            opencv_image = cv2.cvtColor(np.array(drawn), cv2.COLOR_RGB2BGR)
            schedule.set_cache(opencv_image)
            schedule.isSubscribed = False

    #threading.Timer(0.1, evaluateImages).start()

def addDistanceToDatabase(distances, camera_id, data):
    d_numberofpeople = len(data[0])

    distances_list = list(map(lambda x: x['distance'],distances))
    d_maskedpople = sum(1 for x in data[1] if x[5].item() == 1)
    
    d_avg = np.mean(distances_list)
    d_min = min(distances_list)

    with db.app.app_context():
        db.session.add(DistanceData(d_min=d_min, d_avg=d_avg, d_numberofpeople=d_numberofpeople,
                           d_datetime=datetime.datetime.utcnow(), d_maskedpeople=d_maskedpople, d_c_id=camera_id))
        db.session.commit()
