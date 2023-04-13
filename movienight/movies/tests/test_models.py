import pytest

from ..models import Movie
from .factories import MovieFactory, GenreFactory


@pytest.mark.django_db
class TestMovieModel:
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
        assert str(movie) == "The Matrix (1999)"

    def test_movie_model_genre_relationship(self):
        movie = MovieFactory()
        movie.genres.add(GenreFactory(name="Action"))
        movie.genres.add(GenreFactory(name="Sci-Fi"))
        assert movie.genres.count() == 2
        assert movie.genres.first().name == "Action"
        assert movie.genres.last().name == "Sci-Fi"

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
        assert len(movies) == 2
        assert movies[0] == movie1
        assert movies[1] == movie2
