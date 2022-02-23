from flask import Flask
from flask_cors import CORS
from .models import db
from .views import view as view_blueprint

def create_app(config_file='settings.py'):
    app = Flask(__name__)
    CORS(app)
    app.config.from_pyfile(config_file)
    db.init_app(app)

    app.register_blueprint(view_blueprint)
    return app