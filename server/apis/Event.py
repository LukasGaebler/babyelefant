from flask_restx import Namespace, Resource
from flask import jsonify, request
from model.Event import Event as DBEvent
from flask_jwt_extended import get_jwt_identity, jwt_required
import model
db = model.db

api = Namespace('event', description='Event operations')


@api.route("/")
class EventRoute(Resource):
    @jwt_required()
    def get(self):
        id = int(get_jwt_identity()['user_id'])
        eventExists = db.session.query(
            db.session.query(DBEvent).filter_by(e_u_user=id).exists()
        ).scalar()
        if eventExists is not None:
            events = db.session.query(DBEvent).filter_by(e_u_user=id).all()
            return jsonify({'data': [i.serialize for i in events]})
        else:
            return 404

    @jwt_required()
    def post(self):
        if not get_jwt_identity()['admin']:
            return "Operation not allowed", 401

        EventName = request.json.get('e_name')
        eUserID = request.json.get('e_u_user')
        eventAdress = request.json.get('e_adress')

        if EventName is None or eUserID is None or eventAdress is None:
            return "required parameter missing", 400

        event = DBEvent(e_name=EventName, e_u_user=eUserID, e_adress=eventAdress)
        db.session.add(event)
        db.session.commit()

        return "success", 200


@api.route("/<int:id>")
class EventId(Resource):
    @jwt_required()
    def get(self, id):
        event = db.session.query(DBEvent).filter_by(e_id=id).first()

        if event.e_u_user != int(get_jwt_identity()['user_id']):
            return "Operation not allowed", 401

        if event is not None:
            return jsonify({"data": event.serialize})
        else:
            return "event not found", 404

    @jwt_required()
    def put(self, id):
        event = db.session.query(DBEvent).filter_by(e_id=id).first()

        if event is not None:
            if event.e_u_user != int(get_jwt_identity()['user_id']):
                return "Operation not allowed", 401

            newName = request.json.get('e_name')
            newAdress = request.json.get('e_adress')

            if newName is None and newAdress is None:
                return "at least one parameter should be set", 400

            if newName is not None:
                event.e_name = newName
            if newAdress is not None:
                event.e_adress = newAdress

            db.session.commit()

            return "success", 200
        else:
            return 'event not found', 404

    @jwt_required()
    def delete(self, id):
        event = db.session.query(DBEvent).filter_by(e_id=id).first()
        if event is not None:
            if event.e_u_user != int(get_jwt_identity()['user_id']):
                return "Operation not allowed", 401

            db.session.delete(DBEvent)
            db.session.commit()
            return 'Event wurde gelöscht', 200
        return 'Event existiert nicht', 404
