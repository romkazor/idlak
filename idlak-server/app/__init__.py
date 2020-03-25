import logging
import os
import sys
import subprocess
import shutil
from logging.handlers import RotatingFileHandler
from flask import Flask, current_app
from config import Config, load_config_file
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, request
from flask_jwt_simple import JWTManager
from datetime import datetime

db = SQLAlchemy()
api = None
jwt = JWTManager()


def create_app(config_name):
    global api, jwt
    app = Flask(__name__)
    app.config.from_object(Config())
    load_config_file(app.config, config_name)

    with app.app_context():
        db.init_app(app)
        db.app = app
        jwt.init_app(app)

    api = Api(app)
    current_app = app

    logging.basicConfig()
    handler = RotatingFileHandler('idlak-server.log', maxBytes=100000,
                                  backupCount=1)
    handler.setLevel(app.config['LOGGING'])
    app.logger.addHandler(handler)
    app.logger.setLevel(app.config['LOGGING'])

    if not app.config['AUTHORIZATION']:
        app.logger.warning('AUTHORIZATION is turned off, this should only ' +
                           'be used during debugging!!! Turn it back on in ' +
                           'the config file!')

    with app.app_context():
        from app import models, endpoints, reqlogging       # noqa
        from app.models.user import User                    # noqa
        from app.models.voice import Voice                    # noqa

        # if database is not created
        if not os.path.isfile(app.config['DATABASE_NAME']+'.db'):
            db.create_all()

        # check if there are any users, if there are none, create an admin
        if len(User.query.all()) == 0:
            admin_user = User.new_user_full('admin', 'admin', True)
            app.logger.info("An initial admin user has been created: {}"
                            .format(admin_user))
            
        # load all voices from config
        if 'VOICE_CONFIG' in app.config:
            for v in app.config['VOICE_CONFIG']['voices']:
                voice = Voice.new_voice(v['vid'], v['name'], v['lang'], v['acc'],
                                        v['gender'], v['dir'])
                if 'error' in voice and 'Voice already exists' not in voice['error']:
                    app.logger.error(voice['error'])
                    sys.exit()
            app.logger.info("Voices from configuration file have been loaded")

    # url endpoints
    from app.endpoints.auth import Auth, Auth_Expire
    api.add_resource(Auth, '/auth')
    api.add_resource(Auth_Expire, '/auth/expire')
    from app.endpoints.language import Languages, Accents
    api.add_resource(Languages, '/languages')
    api.add_resource(Accents, '/languages/<lang_iso>/accents')
    from app.endpoints.speech import Speech
    api.add_resource(Speech, '/speech')
    from app.endpoints.user import Users, Users_Password, Users_Delete, Toggle_Admin
    api.add_resource(Users, '/users')
    api.add_resource(Users_Password, '/users/<user_id>/password')
    api.add_resource(Users_Delete, '/users/<user_id>')
    api.add_resource(Toggle_Admin, '/users/<user_id>/admin')
    from app.endpoints.voice import Voices, VoiceDetails
    api.add_resource(Voices, '/voices')
    api.add_resource(VoiceDetails, '/voices/<voice_id>')

    return app
