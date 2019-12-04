from flask import Flask
from apis import api
from core.Utils.Utils import getSecretKey

app = Flask(__name__)
app.config["SECRET_KEY"] = getSecretKey()
api.init_app(app)


# @api.route('/Login')
# def login(password):
#     print(api.payload)

app.run(debug=True)