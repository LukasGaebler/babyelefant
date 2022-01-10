from flask_restx import Namespace, Resource
from flask import send_from_directory, send_file, request
import io
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.evaluate import evaluateImage

from . import r

api = Namespace('ressources', description='Ressources')

@api.route('/static/<path:path>')
class Static(Resource):
    def get(path):
        return send_from_directory('static', path)

@api.route('/video_feed/<id>')
class VideoFeed(Resource):
    @jwt_required()
    def get(id):
        """ userid = int(get_jwt_identity()['user_id'])
        try:
            schedule = schedules[int(id)]
        except BaseException:
            return "Camera not found", 404 

        if schedule.user != userid and not get_jwt_identity()['admin']:
            return "User not authorized", 401"""
            
        return send_file(io.BytesIO(r.get(str(id))), mimetype='image/png')

@api.route('/analyze')
class Analyze(Resource):
    @jwt_required
    def post():
        imgs = dict()
        for id, file in request.files.items():
            f = file.read()
            imgs[str(id)] = f
            r.set(str(id) + '-raw', f)
        
        evaluateImage(imgs,r)
            
        return "", 201
   