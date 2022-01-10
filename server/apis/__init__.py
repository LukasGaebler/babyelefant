from flask_restx import Api
from apis.User import api as user
from apis.Auth import api as auth
from apis.Camera import api as camera
from apis.Event import api as event
from apis.DistanceData import api as distance
from apis.Admin import api as admin
from apis.Ressources import api as ressources

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
