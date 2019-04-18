import unittest

from app import app
from app import db
from models.media_models import Movies, TVShows

class UnitTests(unittest.TestCase):
    def setUp(self):
        # creates a test client
        self.app = app.test_client()
        # propagate the exceptions to the test client
        self.app.testing = True

    def tearDown(self):
        pass

    def test_home_status_code(self):
        # sends HTTP GET request to the application
        # on the specified path
        result = self.app.get('/')

        # assert the status code of the response
        self.assertEqual(result.status_code, 200)

    def test_home_data(self):
        # sends HTTP GET request to the application
        # on the specified path
        result = self.app.get('/')

        # assert the response data
        self.assertEqual(result.data, b'Home Page')    def setUp(self):
        # creates a test client
        self.app = app.test_client()
        # propagate the exceptions to the test client
        self.app.testing = True

    def test_home_status_code(self):
        # sends HTTP GET request to the application
        # on the specified path
        result = self.app.get('/')

        # assert the status code of the response
        self.assertEqual(result.status_code, 200)

    def test_home_data(self):
        # sends HTTP GET request to the application
        # on the specified path
        result = self.app.get('/')

        # assert the response data
        self.assertEqual(result.data, b'Home Page')

    def test_post_movie(self):
        url = '/post_movie'

        # Should Return
        # "success": false,
        # "valid image_url": false,
        # "valid_description": true,
        # "valid_genre_type": true,
        # "valid_service": true,
        # "valid_tag": true,
        # "valid_title": false,
        # "valid_url": false,
        # "valid_year": true
        test_jsons = [{"title":"", "year" :"", "service":"","tag" :"", "url":"", "image_url":"", "genre_type": "", "description": ""},
                      {"title":"", "year" :"abc", "service":"","tag" :"", "url":"", "image_url":"", "genre_type": "", "description": ""},
                      {"title":"", "year" :"201", "service":"","tag" :"", "url":"", "image_url":"", "genre_type": "", "description": ""},
                      {"title":"", "year" :"", "service":"","tag" :"", "url":"", "image_url":"", "genre_type": "adven", "description": ""},
                      ]

        for test_json in test_jsons:
            result = self.app.post(url, json=test_json)
            expected = result.get_json()
            self.assertEqual(expected['valid image_url'], False)
            self.assertEqual(expected['valid_description'], False)
            self.assertEqual(expected['valid_genre_type'], False)
            self.assertEqual(expected['valid_service'], False)
            self.assertEqual(expected['valid_tag'], False)
            self.assertEqual(expected['valid_title'], False)
            self.assertEqual(expected['valid_url'], False)
            self.assertEqual(expected['valid_year'], False)
            self.assertEqual(expected['success'], False)
