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


class LanguagesTest(unittest.TestCase):
    def setUp(self):
        from integrationtest import setup_app
        self.app, self.client, self.db = setup_app()

    def tearDown(self):
        # delete the database data
        with self.app.app_context():
            from app.models.voice import Voice
            self.db.session.query(Voice).delete()
            self.db.session.commit()

    def test_languages_with_empty_db(self):
        # act
        resp = self.client.get('/languages')
        # assert
        self.assertEqual(resp.status_code, 204)

    def test_languages_with_non_empty_db(self):
        lang = _create_random_voice(self.app)[2]
        # act
        resp = self.client.get('/languages')
        # assert
        self.assertEqual(resp.status_code, 200)
        self.assertIn('languages', resp.json)
        self.assertEqual(lang, resp.json['languages'][0])

    def test_accents_with_non_existing_language(self):
        lang = uuid.uuid4().hex[:2]
        # act
        resp = self.client.get('/languages/'+lang+'/accents')
        # assert
        self.assertEqual(resp.status_code, 404)
        self.assertIn('message', resp.json)
        self.assertIn('Language could not be found', resp.json['message'])

    def test_accents_with_existing_language(self):
        lang, acc = _create_random_voice(self.app)[2:4]
        # act
        resp = self.client.get('/languages/'+lang+'/accents')
        # assert
        self.assertEqual(resp.status_code, 200)
        self.assertIn('language', resp.json)
        self.assertEqual(resp.json['language'], lang)
        self.assertIn('accents', resp.json)
        self.assertIn(acc, resp.json['accents'])
