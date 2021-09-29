from flask_restx import Namespace, Resource
from model.User import User
from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
import model
bcrypt = model.bcrypt
db = model.db

api = Namespace('user', description='User operations')


@api.route('/')
class Users(Resource):
    @jwt_required()
    def get(self):
        if get_jwt_identity()['admin']:
            users = db.session.query(User).all()
            return jsonify({'data': [i.serialize for i in users]})
        else:
            return "not authorized", 403

    @jwt_required()
    def post(self):
        if not get_jwt_identity()['admin']:
            return "not authorized", 403

        newUserName = request.json.get('u_name')
        password = request.json.get('u_pwd')

        if newUserName is None or password is None:
            return "parameters missing", 400

        newUserPassword = bcrypt.generate_password_hash(
            password.encode('utf-8')).decode('utf-8')
        exists = db.session.query(
            db.session.query(User).filter_by(u_name=newUserName).exists()
        ).scalar()
        if exists is False:
            user = User(u_name=newUserName, u_pwd=str(newUserPassword))
            db.session.add(user)
            db.session.commit()
            return "success", 200
        return "username already taken", 409


@api.route("/<int:id>")
class UserId(Resource):
    @jwt_required()
    def delete(self, id):
        if not get_jwt_identity()['admin']:
            return "not authorized", 403

        userExists = db.session.query(
            db.session.query(User).filter_by(u_id=id).exists()
        ).scalar()
        if userExists is not None:
            user = db.session.query(User).filter_by(u_id=id).one()
            db.session.delete(user)
            db.session.commit()
            return 'user got deleted', 200
        else:
            return 'user not found', 404

    @jwt_required()
    def put(self, id):
        if not get_jwt_identity()['admin']:
            return "not authorized", 403

        user = db.session.query(User).filter_by(u_id=id).first()

        if user is not None:
            password = request.json.get('u_pwd')

            if password is None:
                return "parameters missing", 400

            newUserPassword = bcrypt.generate_password_hash(
                password.encode('utf-8')).decode('utf-8')

            user.u_pwd = newUserPassword
            db.session.commit()
            return "success", 200
        else:
            return 'user not found', 404
