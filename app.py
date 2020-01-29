from flask import Flask
from apis import api
from core.Utils.Utils import getSecretKey
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from waitress import serve
app = Flask(__name__)
app.config["SECRET_KEY"] = getSecretKey()
api.init_app(app)
jwt = JWTManager(app)
CORS(app, resources={r'/*': {'origins': '*'}})

serve(app, host='127.0.0.1', port=5000)
