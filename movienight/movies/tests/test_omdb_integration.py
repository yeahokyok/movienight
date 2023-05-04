from django.test import TestCase

from ..models import Genre
from ..omdb_integration import get_or_create_genres


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
