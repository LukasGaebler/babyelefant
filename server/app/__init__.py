import sys  # nopep8
sys.path.append('./app/ai/pt')  # nopep8

from flask import Flask
from flask.json import JSONEncoder
import app.model as model
import logging
import os
from loguru import logger
import decimal
from flask_cors import CORS
from redis import Redis
from flask_jwt_extended import JWTManager
from flask_swagger_ui import get_swaggerui_blueprint
from numpy import ndarray
from dotenv import load_dotenv
load_dotenv()

r = Redis(host='redis',port=6379,db=0)

SECRET_KEY = "hkBxrbZ9Td4QEwgRewV6gZSVH4q78vBia4GBYuqd09SsiMsIjH"
app = Flask(__name__)
DATABASE_USERNAME = os.getenv('DATABASE_USERNAME')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
DATABASE_HOST = os.getenv('DATABASE_HOST')
DATABASE_PORT = os.getenv('DATABASE_PORT')
DATABASE_TABLE = os.getenv('DATABASE_TABLE')
    
SWAGGER_URL = '/api/swagger'
API_URL = '/api/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Babyelefant REST API'
    }
)
    
class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Retrieve context where the logging call occurred, this happens to be in the 6th frame upward
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelno, record.getMessage())


handler = InterceptHandler()
handler.setLevel(0)

class DecimalEncoder(JSONEncoder):

    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        if isinstance(obj,ndarray):
            return obj.tolist()
        return super(DecimalEncoder, self).default(obj)

def init_app():
    
    db = model.db
    bcrypt = model.bcrypt
    schedules = model.schedules

    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.config['JWT_TOKEN_LOCATION'] = ['query_string', 'headers']
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://' + DATABASE_USERNAME + ':' + \
    DATABASE_PASSWORD + '@' + DATABASE_HOST + \
    ':' + DATABASE_PORT + '/' + DATABASE_TABLE
    
    from app.apis import api
    
    with app.app_context():
        app.logger.addHandler(handler)
        
        CORS(app)
        
        db.init_app(app)
        db.app = app
        
        api.init_app(app)
        bcrypt.init_app(app)
        jwt = JWTManager(app)
        
        app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
        
        return app