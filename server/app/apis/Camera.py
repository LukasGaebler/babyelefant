from flask_jwt_extended import get_jwt_identity
from flask_restx import Namespace, Resource
from flask import jsonify, request
from app.model.Event import Event
from app.model.Camera import Camera
#from ai.birdseyeview.birdseyeview import getBirdsEyeViewHomography
from flask_jwt_extended import jwt_required
import app.model as model
from app.ai.src.persondetection import compute_point_perspective_transformation
from app.grpc_client.grpc_client import get_inference_stub,infer
import math
import json
import numpy as np
from loguru import logger
from PIL import Image
import io
from app.ai.scalenet_calibration.utils.matrix import get_overhead_hmatrix_from_4cameraparams, get_scaled_homography
db = model.db
schedules = model.schedules

api = Namespace('camera', description='Camera operations')

from app import r


@api.route('/')
class Cameras(Resource):
    @jwt_required()
    def post(self):
        link = request.json.get('c_link')
        event = request.json.get('c_e_event')
        maxdistance = request.json.get('c_maxdistance')
        downtime_start = request.json.get('c_start')
        downtime_end = request.json.get('c_end')
        if link is None or event is None or maxdistance is None or downtime_start is None or downtime_end is None:
            return "parameters missing", 400

        eventExists = db.session.query(Event).filter_by(
            e_id=event).first()
        if eventExists is not None:
            if eventExists.e_u_user != int(
                    get_jwt_identity()['user_id']) and not get_jwt_identity()['admin']:
                return "User cannot add a camera to this event", 405
            camera = Camera(c_link=link,
                            c_e_event=int(event),
                            c_homography=np.array([[0,
                                                    0,
                                                    0],
                                                   [0,
                                                    0,
                                                    0],
                                                   [0,
                                                    0,
                                                    0]]),
                            c_maxdistance=maxdistance,
                            c_pixelpermeter=-1,
                            c_public=False,
                            c_downtime_end=downtime_end,
                            c_downtime_start=downtime_start)
            db.session.add(camera)
            db.session.commit()

            return 200
        return "Event not Found", 404


@ api.route('/<int:id>')
class CamerasId(Resource):
    @ jwt_required()
    def get(self, id):
        eventExists = db.session.query(Event).filter_by(e_id=id).first()

        if eventExists is not None:
            if eventExists.e_u_user != int(
                    get_jwt_identity()['user_id']) and not get_jwt_identity()['admin']:
                return "Not allowed", 405

            # eventHasCameras = db.session.query(
            #     db.session.query(Camera).filter_by(c_e_event=id).filter(
            #         Camera.c_id.in_(tuple(schedules.keys()))).exists()
            # ).scalar()

            # if eventHasCameras is not False:
            if not get_jwt_identity()['admin']:
                cameras = db.session.query(Camera).filter_by(
                    c_e_event=id).filter(
                    Camera.c_id.in_(
                        tuple(
                            schedules.keys()))).all()
            else:
                cameras = db.session.query(Camera).filter_by(
                    c_e_event=id).all()
            if cameras is not None:
                return jsonify({'cameras': [i.serialize for i in cameras]})
            else:
                return "Not found", 404
        else:
            return "Event not found", 400

    @ jwt_required()
    def post(self, id):
        try:
            distance = float(request.json['distance'])
        except BaseException:
            return "Distance parameter not found or not a number", 400

        cameraExists = db.session.query(
            Camera,
            Event).join(
            Event,
            Event.e_id == Camera.c_e_event).filter(
            Camera.c_id == id).first()

        if cameraExists is None:
            return "Camera not found", 404

        if cameraExists[1].e_u_user != int(
                get_jwt_identity()['user_id']) and not get_jwt_identity()['admin']:
            return "Not allowed", 405

        image = r.get(str(id) + '-raw')
        
        if image is None:
            return "Camera image not found", 400

        matrix, pixel_per_meter = calibrate(image, id, distance)

        cameraExists[0].c_homography = {'matrix': matrix.tolist()}
        cameraExists[0].c_pixelpermeter = pixel_per_meter

        db.session.commit()

        return "success", 200

    @ jwt_required()
    def delete(self, id):
        cameraExists = db.session.query(
            Camera,
            Event).join(
            Event,
            Event.e_id == Camera.c_e_event).filter(
            Camera.c_id == id).first()

        if cameraExists is not None:
            if cameraExists[1].e_u_user != int(
                    get_jwt_identity()['user_id']) and not get_jwt_identity()['admin']:
                return "User cannot add a camera to this event", 405

            camera = db.session.query(Camera).filter_by(c_id=id).one()
            db.session.delete(camera)
            db.session.commit()

            try:
                del schedules[int(id)]
            except BaseException:
                pass

            return 200
        else:
            return 404

    @ jwt_required()
    def put(self, id):
        cameraExists = db.session.query(
            Camera,
            Event).join(
            Event,
            Event.e_id == Camera.c_e_event).filter(
            Camera.c_id == id).first()

        if cameraExists is not None:
            if cameraExists[1].e_u_user != int(
                    get_jwt_identity()['user_id']) and not get_jwt_identity()['admin']:
                return "User cannot edit this camera", 405

            camera = cameraExists[0]

            link = request.json.get('c_link')
            event = request.json.get('c_e_event')

            if link is not None:
                camera.c_link = link
            if event is not None:
                eventExists = db.session.query(
                    Event).filter_by(e_id=event).first()
                if eventExists is not None:
                    if eventExists.e_u_user != int(
                            get_jwt_identity()['user_id']):
                        return "User cannot add a camera to this event", 405
                    camera.c_e_event = event
                else:
                    return "Event doesn't exist", 404
            db.session.commit()

            return "Updated successfully", 200

        else:
            return "Camera doesn't exists", 404


def calibrate(image, id, distance):
    data = (json.loads(infer(get_inference_stub(),'scalenet',{str(id): image})))[0]
    
    print(data)
    
    pitch = data.get('output_pitch')
    roll = data.get('output_roll')
    vfov = data.get('output_vfov')

    w, h = Image.open(io.BytesIO(image)).size
    f_pix = h / 2. / np.tan(vfov / 2.)

    sensor_size = 24 
    f_pix / h * sensor_size

    overhead_hmatrix, est_range_u, est_range_v = get_overhead_hmatrix_from_4cameraparams(
        fx=f_pix, fy=f_pix, my_tilt=pitch, my_roll=-roll, img_dims=(w, h), verbose=False)

    matrix, target_dim = get_scaled_homography(
        overhead_hmatrix, 1080 * 2, est_range_u, est_range_v)
    
    boxes = (json.loads(infer(get_inference_stub(),'yolov5',{str(id): image})))[0]

    box1 = boxes[0].get('boxes')
    box2 = boxes[1].get('boxes')
    x1 = (box1[0] + box1[2]) / 2
    x2 = (box2[0] + box2[2]) / 2

    transformed = compute_point_perspective_transformation(
        matrix, [[x1, box1[3]], [x2, box2[3]]])

    pixel = math.sqrt((transformed[1][0] - transformed[0][0])
                      ** 2 + (transformed[1][1] - transformed[0][1])**2)

    logger.info("Distance: ", round(distance, 2), "m;", pixel / distance, pixel)

    pixel_per_meter = pixel / distance

    return matrix, pixel_per_meter
