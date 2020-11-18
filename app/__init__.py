from flask import Flask

from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import LoginManager
from flask_googlemaps import GoogleMaps



app = Flask(__name__)
CORS(app)
cors = CORS(app,resources={
    r"/*":{
        "origins":"*"
        }
    })


app.config.from_object('config')
db = SQLAlchemy(app)

# you can set key as config
app.config['GOOGLEMAPS_KEY'] = "AIzaSyAqzuYOHxHAsgriFKzbe7oHX_h5i2l-Q9o"
# Initialize the extension
GoogleMaps(app)


lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

from app import views
