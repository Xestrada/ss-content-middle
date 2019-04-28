import unittest

from app import app


class UnitTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

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
        self.assertEqual(result.data, b'Home Page')

    def test_get_actors_by_page(self):
        # Should Return
        # 'actors' is not None

        result = self.app.get('/actors')
        expected = result.get_json()
        assert expected['actors'] is not None

    def test_get_actors_by_first_name(self):
        # Should Return
        # 'actors': []

        test_values = [None, '', -1, 0]

        for i in range(len(test_values)):
            result = self.app.get('/actors/fn={fn}'.format(fn=test_values[i]))
            expected = result.get_json()
            self.assertEqual(expected['actors'], [])

        # Should Return Successfully

        test_values = ['tom', 'john']

        for i in range(len(test_values)):
            result = self.app.get('/actors/fn={fn}'.format(fn=test_values[i]))
            expected = result.get_json()
            assert len(expected['actors']) >= 1

    def test_get_actors_by_last_name(self):
        # Should Return
        # 'actors': []

        test_values = [None, '', -1, 0]

        for i in range(len(test_values)):
            result = self.app.get('/actors/ln={ln}'.format(ln=test_values[i]))
            expected = result.get_json()
            self.assertEqual(expected['actors'], [])

        # Should Return Successfully

        test_values = ['hanks', 'd']

        for i in range(len(test_values)):
            result = self.app.get('/actors/ln={ln}'.format(ln=test_values[i]))
            expected = result.get_json()
            assert len(expected['actors']) >= 1

    def test_get_actors_by_full_name(self):
        # Should Return
        # 'actors': []

        test_values = [None, '', -1, 0]

        for i in range(len(test_values)):
            result = self.app.get('/actors/full={full_name}'.format(full_name=test_values[i]))
            expected = result.get_json()
            self.assertEqual(expected['actors'], [])

        # Should Return Successfully

        test_values = ['tom', 'john', 'hanks']

        for i in range(len(test_values)):
            result = self.app.get('/actors/full={full_name}'.format(full_name=test_values[i]))
            expected = result.get_json()
            assert len(expected['actors']) >= 1

    def test_get_actors_search_all(self):
        # Should Return
        # 'actors': []

        test_values = [None, '', -1, 0]

        for i in range(len(test_values)):
            result = self.app.get('/actors/all={query}'.format(query=test_values[i]))
            expected = result.get_json()
            self.assertEqual(expected['actors'], [])

        # Should Return Successfully

        test_values = ['tom', 'john', 'hanks', 'd', 't', 'sean penn']

        for i in range(len(test_values)):
            result = self.app.get('/actors/all={query}'.format(query=test_values[i]))
            expected = result.get_json()
            assert len(expected['actors']) >= 1
