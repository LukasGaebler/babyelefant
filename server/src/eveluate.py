from ai.src.persondetection import PersonDetection
from ai.src.maskdetection import MaskDetection
import model
from model.DistanceData import DistanceData
import cv2
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
                schedule.pixelpermeter))

        #boxes = maskDetection.merge_with_boxes(boxes, result[1])
        distances = maskDetection.merge_with_distances(distances, result[1])

        calibrationCache[evaluateIds[i]] = boxes

        if schedule.pixelpermeter != -1:
            addDistanceToDatabase(distances, schedule.id)

        if schedule.isSubscribed:
            drawn = personDetection.drawBoxes(
                images[i], distances, boxes)
            opencv_image = cv2.cvtColor(np.array(drawn), cv2.COLOR_RGB2BGR)
            schedule.set_cache(opencv_image)
            schedule.isSubscribed = False

    #threading.Timer(0.1, evaluateImages).start()


def addDistanceToDatabase(distances, camera_id):
    contactCache = []
    for distance in distances:
        print(distance)
    # for distance in distances:
    with db.app.app_context():
        db.session.add_all(contactCache)
        db.session.commit()
