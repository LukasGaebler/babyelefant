import threading
from loguru import logger
import time
import requests
from schedule import Schedule
import io
from PIL import Image
import cv2
from circuitbreaker import circuit

token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY0NjkwNDk3OCwianRpIjoiN2I5YWZlMGMtNTUyOC00MTkxLWI5ZWYtMGQ1NDRjMjljY2IxIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6eyJ1c2VyX2lkIjoxLCJleHAiOiJGcmksIDExIE1hciAyMDIyIDA5OjM2OjE4IEdNVCIsImFkbWluIjp0cnVlfSwibmJmIjoxNjQ2OTA0OTc4LCJleHAiOjE2NDY5OTEzNzh9.xtA3wLl9UPMiAPSRnF8eRJHCn8RGH5Bmo37lchXQz8s"
server = 'http://server:8000'
event = '1'

schedules = dict()

r = requests.get(server + '/api/cameras/' + event, headers={'Authorization': 'Bearer ' + token})
for camera in r.json().get('cameras'):
    schedules[int(camera['c_id'])] = Schedule(
                camera['c_id'],
                camera['c_link'],
                camera['c_downtime_start'],
                camera['c_downtime_end'])


def evaluateImagesLoop():
    logger.info('Starting evaluation loop')
    while True:
        logger.info('Sending images')
        images = {}
        for id,schedule in schedules.items():
            image = Image.fromarray(cv2.cvtColor(schedule.get_frame(), cv2.COLOR_BGR2RGB))
            imgByteArr = io.BytesIO()
            image.save(imgByteArr, format="png")
            images[str(id)] = (str(id),imgByteArr.getvalue(),'multipart/form-data')
            
        requests.post(server + "/api/analyze",headers={'Authorization': 'Bearer ' + token}, files=images)
        time.sleep(0.2) 

evaluateImagesLoop()
