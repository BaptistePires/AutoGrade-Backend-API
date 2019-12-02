from flask import Flask
from apis import api

app = Flask(__name__)
api.init_app(app)


# @api.route('/Login')
# def login(password):
#     print(api.payload)

app.run(debug=True)