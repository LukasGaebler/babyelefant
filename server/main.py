import sys  # nopep8
sys.path.append('./ai/pt')  # nopep8

import asyncio
import logging
from loguru import logger
import functools
from flask import Flask, send_from_directory, request
from flask_swagger_ui import get_swaggerui_blueprint
from src.schedule import Schedule
from flask_cors import CORS
import time
import threading
import json
from flask import send_file
import os
from flask_jwt_extended import (
    JWTManager, get_jwt_identity, jwt_required, verify_jwt_in_request
)
from flask_socketio import SocketIO, emit, disconnect, join_room, rooms
from flask_sqlalchemy import models_committed
import io
from src.evaluate import evaluateImage
from model.Event import Event
from model.Camera import Camera
from model.DistanceData import DistanceData
from apis import api
import model
import decimal
import flask.json
from PIL import Image
import redis
from numpy import ndarray





# image_hub = imagezmq.ImageHub()

SECRET_KEY = "hkBxrbZ9Td4QEwgRewV6gZSVH4q78vBia4GBYuqd09SsiMsIjH"
app = Flask(__name__)
DATABASE_USERNAME = os.getenv('DATABASE_USERNAME')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
DATABASE_HOST = os.getenv('DATABASE_HOST')
DATABASE_PORT = os.getenv('DATABASE_PORT')
DATABASE_TABLE = os.getenv('DATABASE_TABLE')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://' + DATABASE_USERNAME + ':' + \
    DATABASE_PASSWORD + '@' + DATABASE_HOST + \
    ':' + DATABASE_PORT + '/' + DATABASE_TABLE
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['JWT_TOKEN_LOCATION'] = ['query_string', 'headers']








app.json_encoder = DecimalEncoder

CORS(app)

db.init_app(app)
db.app = app
r = redis.Redis(host='redis',port=6379,db=0)

api.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)

jwt._set_error_handler_callbacks(api)

SWAGGER_URL = '/api/swagger'
API_URL = '/api/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Babyelefant REST API'
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


def getAllCameras():
    cameras = db.session.query(
        Camera,
        Event).join(
        Event,
        Camera.c_e_event == Event.e_id).filter(
            Event.e_id == Camera.c_e_event).filter(Camera.c_public).all()
    return cameras
    # return [i[0].serialize for i in cameras]


@app.route("/api/static/<path:path>")
def send_static(path):
    return send_from_directory('static', path)


@app.route('/api/video_feed/<id>')
@jwt_required()
def video_feed(id):
    userid = int(get_jwt_identity()['user_id'])
    try:
        schedule = schedules[int(id)]
    except BaseException:
        return "Camera not found", 404

    if schedule.user != userid and not get_jwt_identity()['admin']:
        return "User not authorized", 401

    schedule.isSubscribed = True
    return send_file(io.BytesIO(r.get(str(id))), mimetype='image/png')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    imgs = dict()
    for id, file in request.files.items():
        f = file.read()
        imgs[str(id)] = f
        r.set(str(id) + '-raw', f)
    
    evaluateImage(imgs,r)
        
    return "", 201
    


with app.app_context():
    cameras = getAllCameras()
    logger.info('Initializing schedules')
    for cameraEvent in cameras:
        camera = cameraEvent[0].data
        logger.debug(
            'Initializing schedule for camera id: {id}', id=camera['c_id'])
        try:
            schedules[int(camera['c_id'])] = Schedule(
                camera['c_id'],
                camera['c_link'],
                camera['c_homography'],
                (cameraEvent[1]).e_u_user,
                camera['c_maxdistance'],
                camera['c_pixelpermeter'],
                (cameraEvent[1]).e_id,
                camera['c_downtime_start'],
                camera['c_downtime_end'])
            logger.debug(
                'Succesfully initialized schedule for camera id: {id}', id=camera['c_id'])
        except ValueError:
            logger.error(
                "Error occured while creating camera with id: {id}", id=camera['c_id'])

    logger.info('Finished initializing schedules')

if(__name__) == "__main__":
    logger.info("Start server")
    app.run(host='0.0.0.0', port=8000, debug=True)
