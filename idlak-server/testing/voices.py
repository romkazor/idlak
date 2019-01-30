import sys
import os
import unittest
import uuid


def _create_random_voice(app):
    id = uuid.uuid4().hex[:3]
    name = 'vn_' + uuid.uuid4().hex[:4]
    lang = uuid.uuid4().hex[:2]
    acc = uuid.uuid4().hex[:2]
    gender = uuid.uuid4().hex[:5]
    directory = uuid.uuid4().hex[:5]
    with app.app_context():
        from app.models.voice import Voice
        voice = Voice.new_voice(id, name, lang, acc, gender, directory)
    return (id, name, lang, acc, gender, directory)


class VoicesTest(unittest.TestCase):
    def setUp(self):
        from integrationtest import setup_app
        self.app, self.client, self.db = setup_app()

    def tearDown(self):
        # delete the database data
        with self.app.app_context():
            from app.models.voice import Voice
            self.db.session.query(Voice).delete()
            self.db.session.commit()

    def test_voices_with_empty_db(self):
        # act
        resp = self.client.post('/voices')
        # assert
        self.assertEqual(resp.status_code, 204)

    def test_voices_with_non_empty_db(self):
        id, name, lang, acc, gender, dir = _create_random_voice(self.app)
        # act
        resp = self.client.post('/voices')
        # assert
        self.assertEqual(resp.status_code, 200)
        self.assertIn('voices', resp.json)
        self.assertEqual(id, resp.json['voices'][0]['id'])
        self.assertEqual(name, resp.json['voices'][0]['name'])
        self.assertEqual(lang, resp.json['voices'][0]['language'])
        self.assertEqual(acc, resp.json['voices'][0]['accent'])
        self.assertEqual(gender, resp.json['voices'][0]['gender'])
        with self.app.app_context():
            from app.models.voice import Voice
            self.assertEqual(dir, Voice.query.get(id).directory)

    def test_voices_params_with_acc_and_no_lang(self):
        acc = uuid.uuid4().hex[:2]
        # act
        resp = self.client.post('/voices', json={'accent': acc})
        # assert
        self.assertEqual(resp.status_code, 400, resp.data)
        self.assertIn('message', resp.json)
        self.assertIn('language has to be provided', resp.json['message'])

    def test_voices_params_with_wrong_gender(self):
        gender = uuid.uuid4().hex[:5]
        # act
        resp = self.client.post('/voices', json={'gender': gender})
        # assert
        self.assertEqual(resp.status_code, 422, resp.data)
        self.assertIn('message', resp.json)
        self.assertIn('Not a valid choice', resp.json['message'])
        self.assertIn('gender', resp.json['message'])

    def test_voicedetails_with_valid_voice(self):
        id, name, lang, acc, gender, dir = _create_random_voice(self.app)
        # act
        resp = self.client.get('/voices/' + id)
        # assert
        self.assertEqual(resp.status_code, 200)
        self.assertIn('id', resp.json)
        self.assertIn('name', resp.json)
        self.assertIn('language', resp.json)
        self.assertIn('accent', resp.json)
        self.assertIn('gender', resp.json)
        self.assertEqual(id, resp.json['id'])
        self.assertEqual(name, resp.json['name'])
        self.assertEqual(lang, resp.json['language'])
        self.assertEqual(acc, resp.json['accent'])
        self.assertEqual(gender, resp.json['gender'])

    def test_voicedetails_with_invalid_voice(self):
        id, name, lang, acc, gender, dir = _create_random_voice(self.app)
        # act
        resp = self.client.get('/voices/' + id + 'invalid')
        # assert
        self.assertEqual(resp.status_code, 404)
        self.assertIn('message', resp.json)
        self.assertIn('could not be found', resp.json['message'])
