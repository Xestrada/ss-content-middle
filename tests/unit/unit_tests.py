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

    def test_recently_added(self):
        # Should Return
        # 'recently_added' is not None

        result = self.app.get('/recently_added')
        expected = result.get_json()
        assert expected['recently_added'] is not None

    def test_get_media_info(self):
        # Should Return
        # 'title': []

        test_values = [None, '', -1, 0]

        for i in range(len(test_values)):
            result = self.app.get('/title={title}/info'.format(title=test_values[i]))
            expected = result.get_json()
            self.assertEqual(expected['title'], [])

        # Should be Successful

        test_values = ['Game of Thrones', 'Seinfeld', 'The Punisher',
                       'Bird Box', 'Hunger Games', 'The Greatest Showman']

        for i in range(len(test_values)):
            result = self.app.get('/title={title}/info'.format(title=test_values[i]))
            expected = result.get_json()
            assert expected[test_values[i]] is not None
            assert len(expected[test_values[i]]) >= 1

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

        test_values = ['Bird Box', 'Toy Story', 'The Greatest Showman']
        for i in range(len(test_values)):
            result = self.app.get('/movies/title={title}/info'.format(title=test_values[i]))
            expected = result.get_json()
            assert expected[test_values[i]] is not None

    def test_get_movies_recent(self):
        # Should Return
        # 'movies' is not None

        result = self.app.get('/movies/recently_added')
        expected = result.get_json()
        assert expected['movies'] is not None

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

    def test_get_movies_by_genre(self):
        # Should Return
        # 'movies': []

        test_values = [None, '', -1, 0, 'happy']

        for i in range(len(test_values)):
            result = self.app.get('/movies/genre={genre}'.format(genre=test_values[i]))
            expected = result.get_json()
            self.assertEqual(expected['movies'], [])

        # Should Return Successfully

        test_values = ['thriller', 'horror']

        for i in range(len(test_values)):
            result = self.app.get('/movies/genre={genre}'.format(genre=test_values[i]))
            expected = result.get_json()
            assert len(expected['movies']) >= 1

    def test_get_movies_by_year(self):
        # Should Return
        # 'movies': []

        test_values = [None, '', -1, 0]

        for i in range(len(test_values)):
            result = self.app.get('/movies/year={year}'.format(year=test_values[i]))
            expected = result.get_json()
            self.assertEqual(expected['movies'], [])

        # Should Return Successfully

        test_values = [2012, '2012', 2017, '2017']

        for i in range(len(test_values)):
            result = self.app.get('/movies/year={year}'.format(year=test_values[i]))
            expected = result.get_json()
            assert len(expected['movies']) >= 1

    def test_get_movies_by_actor(self):
        # Should Return
        # 'movies': []

        test_values = [None, '', -1, 0]

        for i in range(len(test_values)):
            result = self.app.get('/movies/actor={actor}'.format(actor=test_values[i]))
            expected = result.get_json()
            self.assertEqual(expected['movies'], [])

        # Should Return Successfully

        test_values = ['tom hanks', 'sandra bullock']

        for i in range(len(test_values)):
            result = self.app.get('/movies/actor={actor}'.format(actor=test_values[i]))
            expected = result.get_json()
            assert len(expected['movies']) >= 1

    def test_get_movies_search_all(self):
        # Should Return
        # 'movies': []

        test_values = [None, '', -1, 0]

        for i in range(len(test_values)):
            result = self.app.get('/movies/all={query}'.format(query=test_values[i]))
            expected = result.get_json()
            self.assertEqual(expected['movies'], [])

        # Should Return Successfully

        test_values = ['bird', 'toy', 'story',
                       'netflix', 'hulu',
                       'thriller', 'horror',
                       2012, '2012', 2017, '2017'
                       ]

        for i in range(len(test_values)):
            result = self.app.get('/movies/all={query}'.format(query=test_values[i]))
            expected = result.get_json()
            assert len(expected['movies']) >= 1

    def test_get_tv_shows(self):
        # Should Return
        # 'tv_shows' is not None

        result = self.app.get('/tv_shows')
        expected = result.get_json()
        assert expected['tv_shows'] is not None

    def test_get_tv_show_info(self):
        # Should Return
        # 'title':  []

        test_values = [None, '', -1, 0, 'toy story']

        for i in range(len(test_values)):
            result = self.app.get('/tv_shows/title={title}/info'.format(title=test_values[i]))
            expected = result.get_json()
            self.assertEqual(expected['title'], [])

        # Should Return
        # 'title' is not None

        test_values = ['Game of Thrones', 'Seinfeld']
        for i in range(len(test_values)):
            result = self.app.get('/tv_shows/title={title}/info'.format(title=test_values[i]))
            expected = result.get_json()
            assert len(expected[test_values[i]]) >= 1

    def test_get_tv_shows_recent(self):
        # Should Return
        # 'tv_shows' is not None

        result = self.app.get('/tv_shows/recently_added')
        expected = result.get_json()
        assert expected['tv_shows'] is not None

    def test_get_tv_shows_by_title(self):
        # Should Return
        # 'tv_shows': []

        test_values = [None, '', -1, 0]

        for i in range(len(test_values)):
            result = self.app.get('/tv_shows/title={title}'.format(title=test_values[i]))
            expected = result.get_json()
            self.assertEqual(expected['tv_shows'], [])

        # Should Return Successfully

        test_values = ['game', 'thrones', 'flash']

        for i in range(len(test_values)):
            result = self.app.get('/tv_shows/title={title}'.format(title=test_values[i]))
            expected = result.get_json()
            assert len(expected['tv_shows']) >= 1

    def test_get_tv_shows_by_service(self):
        # Should Return
        # 'tv_shows': []

        test_values = [None, '', -1, 0]

        for i in range(len(test_values)):
            result = self.app.get('/tv_shows/service={service}'.format(service=test_values[i]))
            expected = result.get_json()
            self.assertEqual(expected['tv_shows'], [])

        # Should Return Successfully

        test_values = ['netflix', 'hulu', 'hbo now']

        for i in range(len(test_values)):
            result = self.app.get('/tv_shows/service={service}'.format(service=test_values[i]))
            expected = result.get_json()
            assert len(expected['tv_shows']) >= 1

    def test_get_tv_shows_by_genre(self):
        # Should Return
        # 'tv_shows': []

        test_values = [None, '', -1, 0]

        for i in range(len(test_values)):
            result = self.app.get('/tv_shows/genre={genre}'.format(genre=test_values[i]))
            expected = result.get_json()
            self.assertEqual(expected['tv_shows'], [])

        # Should Return Successfully

        test_values = ['thriller', 'action', 'romance']

        for i in range(len(test_values)):
            result = self.app.get('/tv_shows/genre={genre}'.format(genre=test_values[i]))
            expected = result.get_json()
            assert len(expected['tv_shows']) >= 1

    def test_get_tv_shows_by_year(self):
        # Should Return
        # 'tv_shows': []

        test_values = [None, '', -1, 0]

        for i in range(len(test_values)):
            result = self.app.get('/tv_shows/year={year}'.format(year=test_values[i]))
            expected = result.get_json()
            self.assertEqual(expected['tv_shows'], [])

        # Should Return Successfully

        test_values = [2012, '2012', 2014, '2014', 2020]

        for i in range(len(test_values)):
            result = self.app.get('/tv_shows/year={year}'.format(year=test_values[i]))
            expected = result.get_json()
            assert len(expected['tv_shows']) >= 1

    def test_get_tv_shows_by_actor(self):
        # Should Return
        # 'tv_shows': []

        test_values = [None, '', -1, 0]

        for i in range(len(test_values)):
            result = self.app.get('/tv_shows/actor={actor}'.format(actor=test_values[i]))
            expected = result.get_json()
            self.assertEqual(expected['tv_shows'], [])

        # Should Return Successfully

        test_values = ['peter dinklage', 'Julia Louis-Dreyfus']

        for i in range(len(test_values)):
            result = self.app.get('/tv_shows/actor={actor}'.format(actor=test_values[i]))
            expected = result.get_json()
            assert len(expected['tv_shows']) >= 1

    def test_get_tv_shows_search_all(self):
        # Should Return
        # 'tv_shows': []

        test_values = [None, '', -1, 0]

        for i in range(len(test_values)):
            result = self.app.get('/tv_shows/all={query}'.format(query=test_values[i]))
            expected = result.get_json()
            self.assertEqual(expected['tv_shows'], [])

        # Should Return Successfully

        test_values = ['game', 'thrones', 'flash', 'the punisher',
                       'netflix', 'hulu', 'hbo now',
                       'thriller', 'action', 'romance',
                       2012, '2012', 2014, '2014', 2020,
                       'peter dinklage', 'Julia Louis-Dreyfus'
                       ]

        for i in range(len(test_values)):
            result = self.app.get('/tv_shows/all={query}'.format(query=test_values[i]))
            expected = result.get_json()
            assert len(expected['tv_shows']) >= 1

    def test_get_all_results(self):
        # Should Return
        # 'all': []

        test_values = [None, '', -1, 0]

        for i in range(len(test_values)):
            result = self.app.get('/all={query}'.format(query=test_values[i]))
            expected = result.get_json()
            self.assertEqual(expected['all'], [])

        # Should Return
        # 'all' is not None

        test_values = ['bird', 'toy', 'story',
                       'thriller', 'horror', 'action', 'romance',
                       2012, '2012', 2014, '2014', 2017, '2017', 2020, '2020',
                       'game', 'thrones', 'flash',
                       'netflix', 'hulu', 'hbo now',
                       'peter dinklage', 'Julia Louis-Dreyfus'
                       ]

        for i in range(len(test_values)):
            result = self.app.get('/all={query}'.format(query=test_values[i]))
            expected = result.get_json()
            assert expected['all'] is not None
            assert len(expected['all']) >= 1
