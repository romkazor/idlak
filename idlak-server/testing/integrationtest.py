import sys
import os
import unittest
import json
import warnings
sys.path.append('/'.join(os.path.abspath(__file__).split('/')[:-2]))
from app import create_app, db                              # noqa
from auth import AuthTest                                   # noqa
from languages import LanguagesTest                         # noqa
from users import UsersTest                                 # noqa
from voices import VoicesTest                               # noqa
from speech import SpeechTest                               # noqa


def setup_app():
    warnings.simplefilter('ignore', category=ImportWarning)
    config = os.path.abspath('testing/test_config.ini')
    app = create_app(config)
    app.testing = True
    client = app.test_client()
    return app, client, db


if __name__ == "__main__":
    unittest.main()
