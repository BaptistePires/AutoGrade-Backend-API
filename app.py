from flask import Flask
from apis import api
from core.Utils.Utils import getSecretKey
from flask_jwt_extended import JWTManager
from flask_cors import CORS
app = Flask(__name__)
app.config["SECRET_KEY"] = getSecretKey()
api.init_app(app)
jwt = JWTManager(app)
CORS(app)


# @api.route('/Login')
# def login(password):
#     print(api.payload)

app.run(debug=True)