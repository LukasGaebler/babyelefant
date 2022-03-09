import threading
from loguru import logger
import time
import requests
from schedule import Schedule
import io
from PIL import Image
import cv2
from circuitbreaker import circuit

token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY0MTczNTcyNiwianRpIjoiZTA5MzlkOTAtMGE5Zi00YWRlLTg0OTItN2JkYmFiOTRjNmYwIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6eyJ1c2VyX2lkIjoxLCJleHAiOiJNb24sIDEwIEphbiAyMDIyIDEzOjQyOjA2IEdNVCIsImFkbWluIjp0cnVlfSwibmJmIjoxNjQxNzM1NzI2LCJleHAiOjE2NDE4MjIxMjZ9.Ydi4lMm-U0aBx4VgDGrHtoVEcS7nW7AKl8SGFu1NXz4"
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
