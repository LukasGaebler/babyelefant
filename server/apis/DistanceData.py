from model.DistanceDataPerEvent import DistanceDataPerEvent
from flask_restx import Namespace, Resource
from flask import jsonify
from model.Event import Event
from model.Camera import Camera
from model.DistanceData import DistanceData as DistanceDataModel
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.sql import text
import model
db = model.db

api = Namespace('distanceData', description='DistanceData operations')


@api.route("/")
class DistanceData(Resource):
    @jwt_required()
    def get(self):
        dataExists = db.session.query(
            db.session.query(DistanceDataPerEvent).exists()
        ).scalar()
        if dataExists is not None:
            data = db.session.query(DistanceDataPerEvent).join(
                Event, DistanceDataPerEvent.d_e_event == Event.e_id).filter(
                Event.e_u_user == int(
                    get_jwt_identity()['user_id'])).order_by(
                DistanceDataPerEvent.d_datetime).all()
            return jsonify(data=[i.serialize for i in data])
        else:
            return 404


@api.route("/<int:id>")
class DistanceDataId(Resource):
    @jwt_required()
    def get(self, id):
        event = db.session.query(Event).filter_by(e_id=id).first()
        if event is not None:
            if event.e_u_user != int(get_jwt_identity()['user_id']):
                return "User cannot add a camera to this event", 405
            data = db.session.query(DistanceDataPerEvent).filter_by(
                d_e_event=id).order_by(DistanceDataPerEvent.d_datetime).all()
            if data is not None:
                return jsonify(data=[i.serialize for i in data])
            else:
                return 404, "Event has no data"
        return 404, "Event doesn't exist"


@api.route("/camera/<int:id>")
class DistanceDataId(Resource):
    @jwt_required()
    def get(self, id):
        event = db.session.query(Event).join(
            Camera, Camera.c_e_event == Event.e_id).filter_by(c_id=id).first()
        if event is not None:
            if event.e_u_user != int(get_jwt_identity()['user_id']):
                return "User cannot add a camera to this event", 405
            data = db.session.query(DistanceDataModel).filter_by(
                d_c_id=id).order_by(DistanceDataModel.d_datetime).all()
            if data is not None:
                return jsonify(data=[i.serialize for i in data])
            else:
                return 404, "Event has no data"
        return 404, "Event doesn't exist"


@api.route("/info")
class DistanceDataInfo(Resource):
    @jwt_required()
    def get(self):
        user_id = int(get_jwt_identity()['user_id'])
        result = db.engine.execute(text(
            """SELECT avg(d_avg), min(d_min), sum(d_numberofpeople) as people, sum(d_maskedpeople) as maskedpeople, count(distinct e_id) as events
                            FROM public.d_distancedataperevent inner join e_events on d_e_event = e_id
                            where e_u_user = :id
                            group by e_u_user;"""), id=user_id)
        return jsonify(dict(result.fetchone().items()))
