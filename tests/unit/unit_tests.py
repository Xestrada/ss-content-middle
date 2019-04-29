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

    def test_get_movies(self):
        # Should Return
        # 'movies' is not None

        result = self.app.get('/movies')
        expected = result.get_json()
        assert expected['movies'] is not None

    def test_get_movie_info(self):
        # Should Return
        # 'title':  None

        test_values = [None, '', -1, 0]

        for i in range(len(test_values)):
            result = self.app.get('/movies/title={title}/info'.format(title=test_values[i]))
            expected = result.get_json()
            self.assertEqual(expected['title'], None)

        # Should Return
        # 'title' is not None

        test_values = ['Bird Box', 'Toy Story']
        for i in range(len(test_values)):
            result = self.app.get('/movies/title={title}/info'.format(title=test_values[i]))
            expected = result.get_json()
            assert expected[test_values[i]] is not None

    def test_get_movies_by_title(self):
        # Should Return
        # 'movies': []

        test_values = [None, '', -1, 0]

        for i in range(len(test_values)):
            result = self.app.get('/movies/title={title}'.format(title=test_values[i]))
            expected = result.get_json()
            self.assertEqual(expected['movies'], [])

        # Should Return Successfully

        test_values = ['bird', 'toy', 'story']

        for i in range(len(test_values)):
            result = self.app.get('/movies/title={title}'.format(title=test_values[i]))
            expected = result.get_json()
            assert len(expected['movies']) >= 1

    def test_get_movies_by_service(self):
        # Should Return
        # 'movies': []

        test_values = [None, '', -1, 0]

        for i in range(len(test_values)):
            result = self.app.get('/movies/service={service}'.format(service=test_values[i]))
            expected = result.get_json()
            self.assertEqual(expected['movies'], [])

        # Should Return Successfully

        test_values = ['netflix', 'hulu']

        for i in range(len(test_values)):
            result = self.app.get('/movies/service={service}'.format(service=test_values[i]))
            expected = result.get_json()
            assert len(expected['movies']) >= 1
