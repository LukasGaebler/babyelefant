from flask_restx import Api
from app.apis.User import api as user
from app.apis.Auth import api as auth
from app.apis.Camera import api as camera
from app.apis.Event import api as event
from app.apis.DistanceData import api as distance
from app.apis.Admin import api as admin
from app.apis.Ressources import api as ressources

api = Api(
    title='Babyelefant API',
    version='1.0',
    description='Backend for the Babyelefant Project',
    # All API metadatas
)

api.add_namespace(user, path="/api/users")
api.add_namespace(auth, path='/api/auth')
api.add_namespace(camera, path='/api/cameras')
api.add_namespace(event, path="/api/events")
api.add_namespace(distance, path="/api/distanceData")
api.add_namespace(admin, path="/api/admin")
api.add_namespace(ressources, path="/api")
