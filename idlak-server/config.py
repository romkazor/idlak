import os
import configparser
import uuid
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    JWT_SECRET_KEY = str(uuid.uuid4())


def load_config_file(conf):
    config = configparser.ConfigParser()
    config.read('config.ini')
    # JWT
    token_expiration = int(config['JWT']['TOKEN_EXPIRATION_DELTA'])
    conf['JWT_EXPIRATION_DELTA'] = timedelta(minutes=token_expiration)
    # load all default
    for key in config['DEFAULT']:
        conf[key.upper()] = config['DEFAULT'][key]
    # correct AUTHENTICATION value
    if 'AUTHENTICATION' in conf:
        auth = conf['AUTHENTICATION']
        if auth.lower() in ("yes", "true", "t", "1"):
            conf['AUTHENTICATION'] = True
        elif auth.lower() in ("no", "false", "f", "0"):
            conf['AUTHENTICATION'] = False
        else:
            raise ValueError('AUTHENTICATION value in config is incorrect!')
    else:
        conf['AUTHENTICATION'] = True
    return conf
    # set logging value
    if 'LOGGING' in conf:
        log = conf['LOGGING']
        if log == 'DEBUG':
            conf['LOGGING'] = logging.DEBUG
        elif log == 'INFO':
            conf['LOGGING'] = logging.INFO
        elif log == 'WARNING':
            conf['LOGGING'] = logging.WARNING
        elif log == 'ERROR':
            conf['LOGGING'] = logging.ERROR
        elif log == 'CRITICAL':
            conf['LOGGING'] = logging.CRITICAL
        else:
            conf['LOGGING'] = logging.NOTSET
    else:
        conf['LOGGING'] = logging.NOTSET
    return conf
