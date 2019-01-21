import sys
import os
import unittest
import uuid


class AuthTest(unittest.TestCase):
    def setUp(self):
        from integrationtest import setup_app
        self.app, self.client, self.db = setup_app()

    def tearDown(self):
        # delete the database data
        with self.app.app_context():
            from app.models.user import User
            self.db.session.query(User).delete()
            self.db.session.commit()

    def test_auth_with_no_username(self):
        password = 'admin'
        # act
        resp = self.client.post('/auth', json={'password': password})
        # assert
        self.assertEqual(resp.status_code, 422, resp.data)
        self.assertIn('message', resp.json)
        self.assertIn('Missing data', resp.json['message'])
        self.assertIn('uid', resp.json['message'])

    def test_auth_with_no_password(self):
        username = 'admin'
        # act
        resp = self.client.post('/auth', json={'uid': username})
        # assert
        self.assertEqual(resp.status_code, 422, resp.data)
        self.assertIn('message', resp.json)
        self.assertIn('Missing data', resp.json['message'])
        self.assertIn('password', resp.json['message'])

    def test_auth_with_valid_details(self):
        username = 'admin'
        password = 'admin'
        # act
        resp = self.client.post('/auth', json={"uid": username,
                                               "password": password})
        # assert
        self.assertEqual(resp.status_code, 200, resp.data)
        self.assertIn('access_token', resp.json)
        # checking if the access token is correct
        with self.app.app_context():
            from flask_jwt_simple import decode_jwt
            user = decode_jwt(resp.json['access_token'])
            self.assertEqual(user['sub'], username)

    def test_auth_with_invalid_uid(self):
        username = 'notadmin'
        password = 'badpassword'
        # act
        resp = self.client.post('/auth', json={"uid": username,
                                               "password": password})
        # assert
        self.assertEqual(resp.status_code, 401, resp.data)
        self.assertIn('message', resp.json)

    def test_auth_with_invalid_pass(self):
        username = 'admin'
        password = 'badpassword'
        # act
        resp = self.client.post('/auth', json={"uid": username,
                                               "password": password})
        # assert
        self.assertEqual(resp.status_code, 401, resp.data)
        self.assertIn('message', resp.json)

    def test_authexpire_with_valid_token(self):
        # get a valid token
        username = 'admin' + uuid.uuid4().hex[:4]
        with self.app.app_context():
            # create an admin user
            from app.models.user import User
            User.new_user(user_id=username, isAdmin=True)
            from flask_jwt_simple import create_jwt, decode_jwt
            token = create_jwt(identity=username)
        # act
        before_expire = self.client.get('/users',
                                        headers=[('Authorization',
                                                  'Bearer ' + token)])
        expire = self.client.post('/auth/expire',
                                  headers=[('Authorization',
                                            'Bearer ' + token)])
        test_expire = self.client.get('/users',
                                      headers=[('Authorization',
                                                'Bearer ' + token)])

        # assert
        self.assertEqual(before_expire.status_code, 200, before_expire.data)
        self.assertIn('users', before_expire.json)
        self.assertEqual(expire.status_code, 200, expire.data)
        self.assertIn('message', expire.json)
        self.assertIn('manually expired', expire.json['message'])
        self.assertEqual(test_expire.status_code, 401, test_expire.data)
        self.assertIn('message', test_expire.json)
        self.assertIn('token has expired', test_expire.json['message'])

    def test_authexpire_with_invalid_token(self):
        # get a valid token
        username = 'admin'
        with self.app.app_context():
            from flask_jwt_simple import create_jwt
            invalid_token = create_jwt(identity=username)
        invalid_token = invalid_token[:-7] + 'invalid'
        # act
        expire = self.client.post('/auth/expire',
                                  headers=[('Authorization',
                                            'Bearer ' + invalid_token)])

        # assert
        self.assertEqual(expire.status_code, 401, expire.data)
        self.assertIn('message', expire.json)
        self.assertIn('token is invalid', expire.json['message'])

    def test_authexpire_with_expired_token(self):
        # get a valid token
        username = 'admin' + uuid.uuid4().hex[:4]
        with self.app.app_context():
            # create an admin user
            from app.models.user import User
            User.new_user(user_id=username, isAdmin=True)
            from flask_jwt_simple import create_jwt
            token = create_jwt(identity=username)
        # act
        before_expire = self.client.get('/users',
                                        headers=[('Authorization',
                                                  'Bearer ' + token)])
        first_expire = self.client.post('/auth/expire',
                                        headers=[('Authorization',
                                                  'Bearer ' + token)])
        secnd_expire = self.client.post('/auth/expire',
                                        headers=[('Authorization',
                                                  'Bearer ' + token)])

        # assert
        self.assertEqual(before_expire.status_code, 200, before_expire.data)
        self.assertIn('users', before_expire.json)
        self.assertEqual(first_expire.status_code, 200, first_expire.data)
        self.assertIn('message', first_expire.json)
        self.assertIn('manually expired', first_expire.json['message'])
        self.assertEqual(secnd_expire.status_code, 401, secnd_expire.data)
        self.assertIn('message', secnd_expire.json)
        self.assertIn('token has expired', secnd_expire.json['message'])

    def test_jwt_with_invalid_token(self):
        # get a valid token
        username = 'admin'
        with self.app.app_context():
            from flask_jwt_simple import create_jwt
            invalid_token = create_jwt(identity=username)
        invalid_token = invalid_token[:-7] + 'invalid'
        # act
        expire = self.client.get('/users',
                                 headers=[('Authorization',
                                           'Bearer ' + invalid_token)])

        # assert
        self.assertEqual(expire.status_code, 401, expire.data)
        self.assertIn('message', expire.json)
        self.assertIn('token is invalid', expire.json['message'])

    def test_jwt_with_no_token(self):
        # act
        expire = self.client.get('/users')
        # assert
        self.assertEqual(expire.status_code, 401, expire.data)
        self.assertIn('message', expire.json)
        self.assertIn('Missing Authorization Header', expire.json['message'])

    def test_jwt_with_not_admin(self):
        # get a valid token without admin permissions
        username = 'not_admin' + uuid.uuid4().hex[:4]
        with self.app.app_context():
            # create an admin user
            from app.models.user import User
            User.new_user(user_id=username, isAdmin=False)
            from flask_jwt_simple import create_jwt, decode_jwt
            token = create_jwt(identity=username)
        # act
        expire = self.client.get('/users',
                                 headers=[('Authorization',
                                           'Bearer ' + token)])
        # assert
        self.assertEqual(expire.status_code, 401, expire.data)
        self.assertIn('message', expire.json)
        self.assertIn('Admin permissions required', expire.json['message'])
