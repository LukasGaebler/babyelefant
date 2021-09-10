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
from src.eveluate import evaluateImages
from model.Event import Event
from model.Camera import Camera
from model.DistanceData import DistanceData
from apis import api
import model
import decimal
import flask.json
import torch

from dotenv import load_dotenv
load_dotenv()


db = model.db
bcrypt = model.bcrypt
schedules = model.schedules

#image_hub = imagezmq.ImageHub()

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

print(app.config['SQLALCHEMY_DATABASE_URI'])

class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Retrieve context where the logging call occurred, this happens to be in the 6th frame upward
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelno, record.getMessage())
handler = InterceptHandler()
handler.setLevel(0)
app.logger.addHandler(handler)

class DecimalEncoder(flask.json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


app.json_encoder = DecimalEncoder

deepsort_model = torch.load('ai/deep_sort_pytorch/deep_sort/deep/checkpoint/model.pt')

CORS(app)
socketio = SocketIO(app,engineio_logger=app.logger,logger=app.logger)

# socketio.init_app(app, cors_allowed_origins="*")
db.init_app(app)
db.app = app
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
        'app_name': 'Babyelefeant REST API'
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


@db.event.listens_for(Camera, "after_insert")
@db.event.listens_for(Camera, 'after_delete')
@db.event.listens_for(Camera, "after_update")
def after_insert_listener(mapper, connection, target):
    emit("changedCameras", room=target.c_e_event, namespace="/")


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
    return send_file(io.BytesIO(schedule.cache), mimetype='image/png')



with app.app_context():
    cameras = getAllCameras()
    logger.info('Initializing schedules')
    for cameraEvent in cameras:
        camera = cameraEvent[0].data
        logger.debug('Initializing schedule for camera id: {id}', id=camera['c_id'])
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
                camera['c_downtime_end'],
                deepsort_model)
        except ValueError:
            logger.error("Error occured while creating camera with id: {id}",id=camera['c_id'])
            
    logger.info('Finished initializing schedules')


def evaluateImagesLoop():
    logger.info('Starting evaluation loop')
    while True:
        evaluateImages()
        time.sleep(0.1)

## SOCKETIO ##


def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return f(*args, **kwargs)
        except BaseException:
            disconnect()
    return wrapped


@socketio.on('addedCameras')
def addedCameras(cameras):
    logger.info('Added cameras from clients')
    db_cameras = db.session.query(
        Camera, Event).join(
        Event, Camera.c_e_event == Event.e_id).filter(
            Event.e_id == Camera.c_e_event).filter(
                Camera.c_id.in_(
                    tuple(
                        map(
                            lambda x: x['id'], cameras)))).all()
    for cameraEvent in db_cameras:
        camera = cameraEvent[0].data
        schedule = schedules.get(int(camera['c_id']))
       
        # If schedule already exists, just update the link
        if schedule is None:
            logger.debug('Create schedule for camera id: {id} from client', id=camera['c_id'])
            schedules[int(camera['c_id'])] = Schedule(
                camera['c_id'],
                None,
                #next(i for i in cameras if i['id'] == camera['c_id'])['link'],
                camera['c_homography'],
                (cameraEvent[1]).e_u_user,
                camera['c_maxdistance'],
                camera['c_pixelpermeter'],
                (cameraEvent[1]).e_id,
                camera['c_downtime_start'],
                camera['c_downtime_end'],
                deepsort_model)


@socketio.on('images')
def images(images):
    for id, image in images.items():
        schedule = schedules.get(int(id))
        if schedule is not None:
            schedule.setInternalCache(image)


@socketio.on('getCameras')
@authenticated_only
def getCameras():
    current_user = get_jwt_identity()
    room = rooms()[1]  # 0 is client id room
    joins = db.session.query(
        Camera,
        Event).join(
        Event,
        Camera.c_e_event == Event.e_id).filter(
            Event.e_id == Camera.c_e_event).filter(
                Event.e_u_user == current_user['user_id']).filter(
                    Event.e_id == room).filter(
                        Camera.c_public == False).all()
    logger.debug('Get cameras for event: {id} for client', id=room)
    cameras = list(map(lambda e: e[0].serialize, joins))
    emit('setCameras', {'data': cameras})


@socketio.on('joinEvent')
@authenticated_only
def join(data):
    current_user = get_jwt_identity()
    event = db.session.query(Event).filter(
        Event.e_id == int(data['id'])).first()
    if event.e_u_user == current_user['user_id']:
        logger.debug('Joined client to event: {id}', id=data['id'])
        join_room(data['id'])
        emit('joined')
    else:
        logger.warning('Client unautorized to join event')


@socketio.on('connect')
@authenticated_only
def connect():
    logger.info('New client connected')


threading.Thread(target=evaluateImagesLoop, daemon=True).start()
# threading.Thread(target=getImageZMQImages).start()

if(__name__) == "__main__":
    # app.run(host='0.0.0.0', port=8000, debug=True)
    socketio.run(app, debug=False, host='0.0.0.0', port=8000)
