from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.utils import timezone


from ..models import Genre, SearchTerm, Movie
from ..omdb_integration import get_or_create_genres, fill_movie_details, search_and_save
from .factories import MovieFactory


class TestGetOrCreateGenres(TestCase):
    def test_create_new_genre(self):
        genre_names = ["Action", "Sci-Fi"]

        # Consume the generator by converting it to a list
        genres = list(get_or_create_genres(genre_names))

        self.assertEqual(len(genre_names), len(genres))
        self.assertEqual(len(genre_names), Genre.objects.count())
        for genre in genres:
            self.assertTrue(Genre.objects.filter(pk=genre.pk).exists())
            self.assertIn(genre.name, genre_names)

    def test_get_existing_genre(self):
        genre_names = ["Action", "Sci-Fi"]
        created_genres = [
            Genre.objects.create(name=genre_name) for genre_name in genre_names
        ]

        genres = list(get_or_create_genres(genre_names))

        self.assertEqual(len(genre_names), len(genres))
        self.assertEqual(len(genre_names), Genre.objects.count())
        for genre in genres:
            self.assertIn(genre, created_genres)

    def test_get_existing_and_create_new_genre(self):
        new_genre_names = ["Action", "Sci-Fi"]
        existing_genre_names = ["Comedy", "Drama"]
        created_genres = [
            Genre.objects.create(name=name) for name in existing_genre_names
        ]
        genre_names = new_genre_names + existing_genre_names

        genres = list(get_or_create_genres(genre_names))

        self.assertEqual(len(genre_names), len(genres))
        self.assertEqual(len(genre_names), Genre.objects.count())

        for genre in genres:
            self.assertTrue(Genre.objects.filter(pk=genre.pk).exists())
            self.assertIn(genre.name, genre_names)


class TestFillMovieDetails(TestCase):
    @patch("movienight.movies.omdb_integration.get_client_from_settings")
    def test_no_fetch_for_full_record_movie(self, mock_get_client_from_settings):
        full_record_movie = MovieFactory.create(is_full_record=True)

        fill_movie_details(full_record_movie)

        mock_get_client_from_settings.assert_not_called()

    @patch("movienight.movies.omdb_integration.get_client_from_settings")
    def test_fill_movie_details_return_movie(self, mock_get_client_from_settings):
        movie = MovieFactory.create(is_full_record=False)
        omdb_client_mock = MagicMock()
        omdb_client_mock.get_by_imdb_id.return_value = MagicMock(
            title="The Matrix",
            year=1999,
            plot="just a test movie",
            runtime_minutes=120,
            genres=["Action", "Sci-Fi"],
        )
        mock_get_client_from_settings.return_value = omdb_client_mock

        returned_movie = fill_movie_details(movie)

        self.assertEqual(returned_movie.is_full_record, True)
        self.assertEqual(returned_movie.title, "The Matrix")
        self.assertEqual(returned_movie.year, 1999)
        self.assertEqual(returned_movie.plot, "just a test movie")
        self.assertEqual(returned_movie.runtime_minutes, 120)
        for genre in returned_movie.genres.all():
            self.assertIn(genre.name, ["Action", "Sci-Fi"])

    @patch("movienight.movies.omdb_integration.get_client_from_settings")
    def test_fill_movie_details_save_movie_in_db(self, mock_get_client_from_settings):
        movie = MovieFactory.create(is_full_record=False)
        omdb_client_mock = MagicMock()
        omdb_client_mock.get_by_imdb_id.return_value = MagicMock(
            title="The Matrix",
            year=1999,
            plot="just a test movie",
            runtime_minutes=120,
            genres=["Action", "Sci-Fi"],
        )
        mock_get_client_from_settings.return_value = omdb_client_mock

        fill_movie_details(movie)

        self.assertEqual(movie.is_full_record, True)
        self.assertEqual(movie.title, "The Matrix")
        self.assertEqual(movie.year, 1999)
        self.assertEqual(movie.plot, "just a test movie")
        self.assertEqual(movie.runtime_minutes, 120)
        for genre in movie.genres.all():
            self.assertIn(genre.name, ["Action", "Sci-Fi"])


class TestSearchAndSave(TestCase):
    @patch("movienight.movies.omdb_integration.get_client_from_settings")
    def test_normalized_search_term(self, mock_get_client_from_settings):
        omdb_client_mock = MagicMock()
        omdb_client_mock.search.return_value = []
        mock_get_client_from_settings.return_value = omdb_client_mock

        search_term = "  TeSt   SEaRCh   TERM  "
        expected_normalized_search_term = "test search term"

        search_and_save(search_term)

        self.assertTrue(
            SearchTerm.objects.filter(term=expected_normalized_search_term).exists()
        )
        omdb_client_mock.search.assert_called_once_with(expected_normalized_search_term)

    @patch("movienight.movies.omdb_integration.get_client_from_settings")
    @patch("movienight.movies.omdb_integration.now")
    def test_update_search_term_last_searched(
        self, mock_now, mock_get_client_from_settings
    ):
        omdb_client_mock = MagicMock()
        omdb_client_mock.search.return_value = []
        mock_get_client_from_settings.return_value = omdb_client_mock

        mock_now.return_value = timezone.now()

        search_term = SearchTerm.objects.create(term="test search term")
        original_last_search = search_term.last_search

        # time passed
        mock_now.return_value += timezone.timedelta(days=2)

        search_and_save(search_term.term)

        # refresh from db to get last_search from db
        search_term.refresh_from_db()

        self.assertNotEqual(search_term.last_search, original_last_search)
