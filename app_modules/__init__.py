import os
from flask import Flask
from flask_cors import CORS
from .models import db
from .views import view as view_blueprint

def create_app(config_file='settings.py'):
    frondend_folder = '../frontend'

    app = Flask(__name__, template_folder=frondend_folder, static_folder=frondend_folder + '/static')
    CORS(app)
    app.config.from_pyfile(config_file)
    db.init_app(app)

    app.register_blueprint(view_blueprint)
    return app