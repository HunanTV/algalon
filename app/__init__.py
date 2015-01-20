import json

from flask import Flask, request, g
from flask.ext.bootstrap import Bootstrap
from flask.ext.mail import Mail
from flask.ext.moment import Moment
from flask.ext.sqlalchemy import SQLAlchemy
from config import config

from .ext import openid2

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    openid2.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    from .models import User

    @app.before_request
    def init_global_vars():
        user_dict = json.loads(request.cookies.get(app.config['OPENID2_PROFILE_COOKIE_NAME'], '{}'))
        g.user = user_dict and User.get_or_create(user_dict['username'], user_dict['email']) or None
    return app
