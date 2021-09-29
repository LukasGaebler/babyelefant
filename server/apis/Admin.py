from flask import jsonify, request, send_file
from flask_restx import Namespace, Resource
import model
from flask_jwt_extended import get_jwt_identity, jwt_required, create_access_token
from model.Event import Event
import datetime
from io import StringIO
bcrypt = model.bcrypt
db = model.db

api = Namespace('admin', description='Admin operations')


@api.route('/events/<int:id>')
class AdminEvents(Resource):
    @jwt_required()
    def get(self, id):
        if not get_jwt_identity()['admin']:
            return "not authorized", 405

        eventExists = db.session.query(
            db.session.query(Event).filter_by(e_u_user=id).exists()
        ).scalar()
        if eventExists is not None:
            events = db.session.query(Event).filter_by(e_u_user=id).all()
            return jsonify({'data': [i.serialize for i in events]})
        else:
            return 404
        
@api.route('/client/config')
class Client(Resource):
    @jwt_required()
    def post(self):
        if not get_jwt_identity()['admin']:
            return "not authorized", 405
        
        event = request.json.get('event')
        user = request.json.get('user')
        
        if user is None or event is None:
            return "value missing", 400
        
        payload = {"event": event, "user_id": user}
        token = create_access_token(
            identity=payload,
            expires_delta=datetime.timedelta(weeks=51000))
        
        remote = request.host_url[:-1].replace("http://", "https://")
        
        content = "token={token}\nevent={event}\nremote={remote}".format(token=token,event=event,remote=remote)
        
        return send_file(StringIO(content), mimetype="text/*", attachment_filename="babyelefant.env",as_attachment=True)