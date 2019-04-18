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
        # 'valid_user': False
        # 'valid_movie': False
        # 'success': False
        test_jsons = [{'user_id': None, 'movie_id': None, 'rating': 5},
                      {'user_id': 0, 'movie_id': None, 'rating': 5},
                      {'user_id': None, 'movie_id': 0, 'rating': 5},
                      {'user_id': 0, 'movie_id': 0, 'rating': 5}
                      ]

        for test_json in test_jsons:
            result = self.app.post(url, json=test_json)
            expected = result.get_json()
            self.assertEqual(expected['valid_user'], False)
            self.assertEqual(expected['valid_movie'], False)
            self.assertEqual(expected['success'], False)
