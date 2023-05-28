from datetime import timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from ..models import Movie, MovieNight
from .factories import MovieFactory, GenreFactory, MovieNightFactory
from movienight.accounts.tests.factories import UserFactory


UserModel = get_user_model()


class TestMovieModel(TestCase):
    def test_movie_model_str_method(self):
        movie = MovieFactory(
            title="The Matrix",
            year=1999,
            runtime_minutes=136,
            imdb_id="tt0133093",
            plot="A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.",
            is_full_record=True,
        )
        movie.genres.add(GenreFactory(name="Action"))
        self.assertEqual(str(movie), "The Matrix (1999)")

    def test_movie_model_genre_relationship(self):
        movie = MovieFactory()
        movie.genres.add(GenreFactory(name="Action"))
        movie.genres.add(GenreFactory(name="Sci-Fi"))
        self.assertEqual(movie.genres.count(), 2)
        self.assertEqual(movie.genres.first().name, "Action")
        self.assertEqual(movie.genres.last().name, "Sci-Fi")

    def test_movie_model_default_ordering(self):
        movie1 = MovieFactory(
            title="Inception",
            year=2010,
            runtime_minutes=148,
            imdb_id="tt1375666",
            is_full_record=True,
        )
        movie2 = MovieFactory(
            title="The Matrix",
            year=1999,
            runtime_minutes=136,
            imdb_id="tt0133093",
            is_full_record=True,
        )
        movies = list(Movie.objects.all())
        self.assertEqual(len(movies), 2)
        self.assertEqual(movies[0], movie1)
        self.assertEqual(movies[1], movie2)


class TestMovieNight(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.movie = MovieFactory(
            imdb_id="tt0111161",
            title="The Shawshank Redemption",
            year=1994,
            runtime_minutes=142,
        )

    def test_movie_night_end_time(self):
        start_time = timezone.now()
        movie_night = MovieNightFactory(
            movie=self.movie, start_time=start_time, creator=self.user
        )
        expected_end_time = start_time + timedelta(minutes=self.movie.runtime_minutes)
        self.assertEqual(movie_night.end_time, expected_end_time)

    def test_movie_night_end_time_no_runtime(self):
        self.movie.runtime_minutes = None
        self.movie.save()
        start_time = timezone.now()
        movie_night = MovieNightFactory(
            movie=self.movie, start_time=start_time, creator=self.user
        )
        self.assertIsNone(movie_night.end_time)

    def test_movie_night_str_representation(self):
        movie_night = MovieNightFactory(movie=self.movie, creator=self.user)
        expected_str_representation = (
            f"{self.movie.title} ({self.movie.year}) - {self.user.email}"
        )
        self.assertEqual(str(movie_night), expected_str_representation)
