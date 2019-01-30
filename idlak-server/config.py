import os
import configparser
import uuid
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, '{}.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    JWT_SECRET_KEY = str(uuid.uuid4())


def load_config_file(conf, config_name):
    config = configparser.ConfigParser()
    config.read(config_name)
    # JWT
    token_expiration = int(config['JWT']['TOKEN_EXPIRATION_DELTA'])
    conf['JWT_EXPIRATION_DELTA'] = timedelta(minutes=token_expiration)
    # load all default
    for key in config['DEFAULT']:
        conf[key.upper()] = config['DEFAULT'][key]
    # correct database value
    conf['SQLALCHEMY_DATABASE_URI'] = (conf['SQLALCHEMY_DATABASE_URI']
                                       .format(conf['DATABASE_NAME']))
    # correct AUTHENTICATION value
    if 'AUTHORIZATION' in conf:
        auth = conf['AUTHORIZATION']
        if auth.lower() in ("yes", "true", "t", "1"):
            conf['AUTHORIZATION'] = True
        elif auth.lower() in ("no", "false", "f", "0"):
            conf['AUTHORIZATION'] = False
        else:
            raise ValueError('AUTHORIZATION value in config is incorrect!')
    else:
        conf['AUTHORIZATION'] = True
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
