import sys
import os
import unittest
import uuid


def _create_existing_voice(app):
    id = 'alk'
    name = 'Melanie'
    lang = 'en'
    acc = 'ga'
    gender = 'female'
    directory = '../idlak-egs/tts_tangle_arctic/s2/slt_pmdl/'
    with app.app_context():
        from app.models.voice import Voice
        voice = Voice.new_voice(id, name, lang, acc, gender, directory)
    return (id, name, lang, acc, gender, directory)


class SpeechTest(unittest.TestCase):
    def setUp(self):
        from integrationtest import setup_app
        self.app, self.client, self.db = setup_app()

    def tearDown(self):
        # delete the database data
        with self.app.app_context():
            from app.models.voice import Voice
            self.db.session.query(Voice).delete()
            self.db.session.commit()

    def test_speech_with_empty_db(self):
        voice_id = uuid.uuid4().hex[:3]
        with self.app.app_context():
            from flask_jwt_simple import create_jwt
            token = create_jwt(identity='admin')
        # act
        resp = self.client.post('/speech', json={'voice_id': voice_id,
                                                 'text': ''},
                                headers=[('Authorization',
                                          'Bearer ' + token)])
        # assert
        self.assertEqual(resp.status_code, 400, resp.data)
        self.assertIn('message', resp.json)
        self.assertIn('could not be found', resp.json['message'])

    def test_speech_with_wrong_audio_format(self):
        voice_id = uuid.uuid4().hex[:3]
        audf = uuid.uuid4().hex[:4]
        with self.app.app_context():
            from flask_jwt_simple import create_jwt
            token = create_jwt(identity='admin')
        # act
        resp = self.client.post('/speech', json={'voice_id': voice_id,
                                                 'audio_format': audf,
                                                 'text': ''},
                                headers=[('Authorization',
                                          'Bearer ' + token)])
        # assert
        self.assertEqual(resp.status_code, 422, resp.data)
        self.assertIn('message', resp.json)
        self.assertIn('Not a valid choice', resp.json['message'])

    def test_speech_with_no_voice(self):
        with self.app.app_context():
            from flask_jwt_simple import create_jwt
            token = create_jwt(identity='admin')
        # act
        resp = self.client.post('/speech', json={'text': ''},
                                headers=[('Authorization',
                                          'Bearer ' + token)])
        # assert
        self.assertEqual(resp.status_code, 422, resp.data)
        self.assertIn('message', resp.json)
        self.assertIn('Missing data', resp.json['message'])
        self.assertIn('voice id', resp.json['message'])

    def test_speech_with_no_text(self):
        voice_id = uuid.uuid4().hex[:3]
        with self.app.app_context():
            from flask_jwt_simple import create_jwt
            token = create_jwt(identity='admin')
        # act
        resp = self.client.post('/speech', json={'voice_id': voice_id},
                                headers=[('Authorization',
                                          'Bearer ' + token)])
        # assert
        self.assertEqual(resp.status_code, 422, resp.data)
        self.assertIn('message', resp.json)
        self.assertIn('Missing data', resp.json['message'])
        self.assertIn('text', resp.json['message'])

    @unittest.skipIf(not os.path.isdir('../idlak-egs/tts_tangle_arctic/' +
                                       's2/slt_pmdl'),
                     'No built voice files')
    def test_speech_with_valid_data(self):
        voice = _create_existing_voice(self.app)
        text = 'Hello, this is text for testing the speech endpoint.'
        with self.app.app_context():
            from flask_jwt_simple import create_jwt
            token = create_jwt(identity='admin')
        # act
        resp = self.client.post('/speech', json={'voice_id': voice[0],
                                                 'text': text},
                                headers=[('Authorization',
                                          'Bearer ' + token)])
        for i in resp.headers:
            if i[0] == 'Content-Type':
                content_type = i[1]
            if i[0] == 'Content-Length':
                content_length = int(i[1])
        # assert
        self.assertEqual(resp.status_code, 200, resp.json)
        self.assertEqual(content_type, 'audio/wav')
        self.assertGreater(content_length, len(text)*7000)

    @unittest.skipIf(not os.path.isdir('../idlak-egs/tts_tangle_arctic/' +
                                       's2/slt_pmdl'),
                     'No built voice files')
    def test_speech_with_valid_data_and_mp3(self):
        voice = _create_existing_voice(self.app)
        audf = 'mp3'
        text = 'Hello, this is text for testing the speech endpoint.'
        with self.app.app_context():
            from flask_jwt_simple import create_jwt
            token = create_jwt(identity='admin')
        # act
        resp = self.client.post('/speech', json={'voice_id': voice[0],
                                                 'audio_format': audf,
                                                 'text': text},
                                headers=[('Authorization',
                                          'Bearer ' + token)])
        for i in resp.headers:
            if i[0] == 'Content-Type':
                content_type = i[1]
            if i[0] == 'Content-Length':
                content_length = int(i[1])
        # assert
        self.assertEqual(resp.status_code, 200, resp.json)
        self.assertEqual(content_type, 'audio/'+audf)
        self.assertGreater(content_length, len(text)*600)
