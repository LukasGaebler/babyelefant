from flask_restx import Namespace, Resource
from model.User import User
from flask import jsonify, request
import model
import os
import datetime
from flask_jwt_extended import create_access_token
bcrypt = model.bcrypt
db = model.db

api = Namespace('auth', description='Authentication operations')



@api.route('/login')
class Login(Resource):
    def post(self):
        loginUsername = request.json['username']
        loginPassword = request.json['password']

        try:
            user = db.session.query(User).filter_by(u_name=loginUsername).one()

        except BaseException:
            return "Sie haben den falschen Usernamen oder das falsche Passwort eingegeben", 401

        auth = bcrypt.check_password_hash(
            user.u_pwd.encode('utf-8'), loginPassword)

        if auth:

            timeLimit = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            payload = {"user_id": user.u_id,
                       "exp": timeLimit, "admin": user.u_isadmin}
            token = create_access_token(
                identity=payload,
                expires_delta=datetime.timedelta(
                    hours=24))

            return_data = {
                "error": "0",
                "massage": "Successful",
                "token": token,
                "Elapse_time": f"{timeLimit}"}
            return jsonify(return_data)

        else:
            return "Sie haben den falschen Usernamen oder das falsche Passwort eingegeben", 401
