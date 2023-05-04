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
        for genre in genre_names:
            self.assertTrue(genre, Genre.objects.filter(name=genre).exists())
