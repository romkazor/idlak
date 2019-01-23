import sys
import os
import unittest
import uuid


class UsersTest(unittest.TestCase):
    def setUp(self):
        from integrationtest import setup_app
        self.app, self.client, self.db = setup_app()

    def tearDown(self):
        # delete the database data
        with self.app.app_context():
            from app.models.user import User
            self.db.session.query(User).delete()
            self.db.session.commit()

    def test_users_get_with_admin_user_in_db(self):
        username = 'admin'
        with self.app.app_context():
            from flask_jwt_simple import create_jwt
            token = create_jwt(identity=username)
        # act
        resp = self.client.get('/users', headers=[('Authorization',
                                                   'Bearer ' + token)])
        # assert
        self.assertEqual(resp.status_code, 200)
        self.assertIn('users', resp.json)
        self.assertIn({"id": username, "admin": True}, resp.json['users'])

    def test_users_get_with_multi_users_in_db(self):
        username = 'admin'
        rand_users = [
            {"id": uuid.uuid4().hex[:8], "admin": True},
            {"id": uuid.uuid4().hex[:8], "admin": False},
            {"id": uuid.uuid4().hex[:8], "admin": False},
            {"id": uuid.uuid4().hex[:8], "admin": False},
        ]
        with self.app.app_context():
            # create some users
            from app.models.user import User
            for i in rand_users:
                User.new_user(user_id=i['id'], isAdmin=i['admin'])
            from flask_jwt_simple import create_jwt
            token = create_jwt(identity=username)
        # act
        resp = self.client.get('/users', headers=[('Authorization',
                                                   'Bearer ' + token)])
        # assert
        self.assertEqual(resp.status_code, 200)
        self.assertIn('users', resp.json)
        self.assertIn({"id": username, "admin": True}, resp.json['users'])
        for i in rand_users:
            self.assertIn(i, resp.json['users'])

    def test_users_create_with_valid_details_and_no_admin(self):
        username = uuid.uuid4().hex[:8]
        with self.app.app_context():
            from flask_jwt_simple import create_jwt
            token = create_jwt(identity='admin')
        # act
        resp = self.client.post('/users', json={"uid": username},
                                headers=[('Authorization', 'Bearer ' + token)])
        # assert
        self.assertEqual(resp.status_code, 200)
        self.assertIn('uid', resp.json)
        self.assertIn('admin', resp.json)
        self.assertIn('password', resp.json)
        self.assertEqual(resp.json['uid'], username)
        self.assertEqual(resp.json['admin'], False)

    def test_users_create_with_valid_details_and_admin(self):
        username = uuid.uuid4().hex[:8]
        with self.app.app_context():
            from flask_jwt_simple import create_jwt
            token = create_jwt(identity='admin')
        # act
        resp = self.client.post('/users',
                                json={"uid": username, "admin": True},
                                headers=[('Authorization', 'Bearer ' + token)])
        # assert
        self.assertEqual(resp.status_code, 200)
        self.assertIn('uid', resp.json)
        self.assertIn('admin', resp.json)
        self.assertIn('password', resp.json)
        self.assertEqual(resp.json['uid'], username)
        self.assertEqual(resp.json['admin'], True)
        # check if password is correct
        with self.app.app_context():
            from app.models.user import authenticate
            user = authenticate(username, resp.json['password'])
            self.assertIsNotNone(user)

    def test_users_create_with_invalid_username(self):
        username = 'admin'
        with self.app.app_context():
            # create some users
            from flask_jwt_simple import create_jwt
            token = create_jwt(identity='admin')
        # act
        resp = self.client.post('/users', json={"uid": username},
                                headers=[('Authorization', 'Bearer ' + token)])
        # assert
        self.assertEqual(resp.status_code, 422)
        self.assertIn('message', resp.json)
        self.assertIn('already exists', resp.json['message'])

    def test_users_create_with_invalid_admin(self):
        username = uuid.uuid4().hex[:8]
        admin = uuid.uuid4().hex[:8]
        with self.app.app_context():
            # create some users
            from flask_jwt_simple import create_jwt
            token = create_jwt(identity='admin')
        # act
        resp = self.client.post('/users', json={"uid": username,
                                                "admin": admin},
                                headers=[('Authorization', 'Bearer ' + token)])
        # assert
        self.assertEqual(resp.status_code, 422)
        self.assertIn('message', resp.json)
        self.assertIn('Not a valid boolean', resp.json['message'])

    def test_userspasswrd_create_with_valid_details(self):
        username = uuid.uuid4().hex[:8]
        with self.app.app_context():
            # create a new user
            from app.models.user import User
            User.new_user(user_id=username, isAdmin=True)
            from flask_jwt_simple import create_jwt
            token = create_jwt(identity='admin')
        # act
        resp = self.client.post('/users/{}/password'.format(username),
                                headers=[('Authorization', 'Bearer ' + token)])
        # assert
        self.assertEqual(resp.status_code, 200)
        self.assertIn('password', resp.json)
        # check if password is correct
        with self.app.app_context():
            from app.models.user import authenticate
            user = authenticate(username, resp.json['password'])
            self.assertIsNotNone(user)

    def test_userspasswrd_create_with_invalid_details(self):
        username = uuid.uuid4().hex[:8]
        with self.app.app_context():
            from flask_jwt_simple import create_jwt
            token = create_jwt(identity='admin')
        # act
        resp = self.client.post('/users/{}/password'.format(username),
                                headers=[('Authorization', 'Bearer ' + token)])
        # assert
        self.assertEqual(resp.status_code, 422)
        self.assertIn('message', resp.json)
        self.assertIn('does not exist', resp.json['message'])

    def test_users_delete_with_valid_details(self):
        username = uuid.uuid4().hex[:8]
        with self.app.app_context():
            # create a new user
            from app.models.user import User
            User.new_user(user_id=username, isAdmin=True)
            from flask_jwt_simple import create_jwt
            token = create_jwt(identity='admin')
        # act
        resp = self.client.delete('/users/{}'.format(username),
                                  headers=[('Authorization',
                                            'Bearer ' + token)])
        # assert
        self.assertEqual(resp.status_code, 200)
        self.assertIn('message', resp.json)
        self.assertIn('has been deleted', resp.json['message'])

    def test_users_delete_with_invalid_details(self):
        username = uuid.uuid4().hex[:8]
        with self.app.app_context():
            from flask_jwt_simple import create_jwt
            token = create_jwt(identity='admin')
        # act
        resp = self.client.delete('/users/{}'.format(username),
                                  headers=[('Authorization',
                                            'Bearer ' + token)])
        # assert
        self.assertEqual(resp.status_code, 422)
        self.assertIn('message', resp.json)
        self.assertIn('does not exist', resp.json['message'])

    def test_users_delete_with_only_admin(self):
        username = 'admin'
        with self.app.app_context():
            from flask_jwt_simple import create_jwt
            token = create_jwt(identity='admin')
        # act
        resp = self.client.delete('/users/{}'.format(username),
                                  headers=[('Authorization',
                                            'Bearer ' + token)])
        # assert
        self.assertEqual(resp.status_code, 422)
        self.assertIn('message', resp.json)
        self.assertIn('the only admin', resp.json['message'])

    def test_users_toggleadmin_with_valid_user(self):
        username = uuid.uuid4().hex[:8]
        isadmin = True
        with self.app.app_context():
            # create a new user
            from app.models.user import User
            User.new_user(user_id=username, isAdmin=isadmin)
            from flask_jwt_simple import create_jwt
            token = create_jwt(identity='admin')
        # act
        resp = self.client.post('/users/{}/admin'.format(username),
                                headers=[('Authorization',
                                          'Bearer ' + token)])
        # assert
        self.assertEqual(resp.status_code, 200)
        self.assertIn('uid', resp.json)
        self.assertIn('admin', resp.json)
        self.assertEqual(resp.json['uid'], username)
        self.assertNotEqual(resp.json['admin'], isadmin)

    def test_users_toggleadmin_with_invalid_user(self):
        username = uuid.uuid4().hex[:8]
        with self.app.app_context():
            from flask_jwt_simple import create_jwt
            token = create_jwt(identity='admin')
        # act
        resp = self.client.post('/users/{}/admin'.format(username),
                                headers=[('Authorization',
                                          'Bearer ' + token)])
        # assert
        self.assertEqual(resp.status_code, 422)
        self.assertIn('message', resp.json)
        self.assertIn('does not exist', resp.json['message'])

    def test_users_toggleadmin_with_only_admin(self):
        username = 'admin'
        with self.app.app_context():
            from flask_jwt_simple import create_jwt
            token = create_jwt(identity='admin')
        # act
        resp = self.client.post('/users/{}/admin'.format(username),
                                headers=[('Authorization',
                                          'Bearer ' + token)])
        # assert
        self.assertEqual(resp.status_code, 422)
        self.assertIn('message', resp.json)
        self.assertIn('the only admin', resp.json['message'])
