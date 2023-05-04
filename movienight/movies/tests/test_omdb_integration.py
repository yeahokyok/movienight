from unittest.mock import patch
from django.test import TestCase

from ..models import Genre
from ..omdb_integration import get_or_create_genres, fill_movie_details
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
