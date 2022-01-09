from flask_jwt_extended import get_jwt_identity
from flask_restx import Namespace, Resource
from flask import jsonify, request
from model.Event import Event
from model.Camera import Camera
#from ai.birdseyeview.birdseyeview import getBirdsEyeViewHomography
from flask_jwt_extended import jwt_required
import model
from src.evaluate import calibrationCache
from ai.src.persondetection import compute_point_perspective_transformation
# from math import degrees
# from math import atan
# from math import radians
# from math import sin
import math
# import cv2
from ai.scalenet_calibration.scalenet import calibration
import numpy as np
db = model.db
schedules = model.schedules

api = Namespace('camera', description='Camera operations')


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

        try:
            image = schedules[int(id)].getRawImage()
        except BaseException:
            return "Camera not in evaluation state", 400

        matrix, pixel_per_meter = calibrate(image, id, distance)

        try:
            schedules[int(id)].pixelpermeter = pixel_per_meter
            schedules[int(id)].matrix = matrix
        except BaseException:
            return "Camera not in evaluation state", 400

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
        
@ api.route('/<int:id>/details')
class CamerasDetails(Resource):
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
                return jsonify({'cameras': [i.data for i in cameras]})
            else:
                return "Not found", 404
        else:
            return "Event not found", 400


def calibrate(image, id, distance):
    #orig_height, orig_width, orig_channels = image.shape

    matrix = calibration(image)

    # matrix, fy, fx, my_tilt = getBirdsEyeViewHomography(image)
    # fov = degrees(atan((orig_width/2)/fy)*2)
    # fovx = degrees(atan((orig_height/2)/fx)*2)
    box1 = calibrationCache[int(id)][0]['box']
    box2 = calibrationCache[int(id)][1]['box']

    x1 = (box1[0] + box1[2]) / 2
    x2 = (box2[0] + box2[2]) / 2

    transformed = compute_point_perspective_transformation(
        matrix, [[x1, box1[3]], [x2, box2[3]]])

    pixel = math.sqrt((transformed[1][0] - transformed[0][0])
                      ** 2 + (transformed[1][1] - transformed[0][1])**2)

    # fovxPerPixel = (fovx/orig_height)

    # downDegress = degrees(my_tilt) - (fovx / 2)

    # deg1 = downDegress + (fovxPerPixel * box1[3].item())
    # deg2 = downDegress + (fovxPerPixel * box2[3].item())

    # camera = db.session.query(Camera).filter_by(c_id=id).first()
    # height = float(camera.c_cameraheight)

    # h1 = (height / sin(radians(90 - deg1))) * sin(radians(deg1))
    # h2 = (height / sin(radians(90 - deg2))) * sin(radians(deg2))

    # dif = abs(x2-x1) * (fov/orig_width)

    # distance = (math.sqrt(h1**2 + h2**2 - 2*h1*h2*math.cos(radians(dif))))
    #distance = 2
    print("Distance: ", round(distance, 2), "m;", pixel / distance, pixel)

    pixel_per_meter = pixel / distance

    # cv2.rectangle(image, (box1[0].item(),box1[1]),(box1[2],box1[3]))
    # cv2.rectangle(image,(box2[0],box2[1]),(box2[2],box2[3]))

    # cv2.line(image, (math.trunc(x1.item()), math.trunc(box1[3].item())), (math.trunc(
    #     x2.item()), math.trunc(box2[3].item())), (255, 255, 255), 10)

    # cv2.imwrite("test.png", image)

    return matrix, pixel_per_meter
