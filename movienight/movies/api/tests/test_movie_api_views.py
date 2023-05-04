from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch, MagicMock

from movienight.movies.models import Movie
from movienight.movies.tests.factories import MovieFactory, GenreFactory


class TestMovieViewSet(APITestCase):
    @classmethod
    def setUpTestData(cls):
        for _ in range(20):
            genre = GenreFactory.create()
            movie = MovieFactory.create()
            movie.genres.set([genre])

    def test_list_movie(self):
        url = reverse("movie-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 20)

    @patch("movienight.movies.api.views.fill_movie_details")
    def test_get_movie(self, mock_fill_movie_details):
        movie = Movie.objects.first()
        mock_fill_movie_details.return_value = movie

        url = reverse("movie-detail", kwargs={"pk": movie.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], movie.title)
        self.assertEqual(response.data["year"], movie.year)
        self.assertEqual(response.data["imdb_id"], movie.imdb_id)
        self.assertEqual(response.data["plot"], movie.plot)
        self.assertEqual(response.data["runtime_minutes"], movie.runtime_minutes)
        self.assertEqual(
            set(response.data["genres"]),
            {genre.name for genre in movie.genres.all()},
        )

    @patch("movienight.movies.api.views.fill_movie_details")
    def test_get_movie_call_fill_movie_details(self, mock_fill_movie_details):
        movie = Movie.objects.first()
        url = reverse("movie-detail", kwargs={"pk": movie.id})
        response = self.client.get(url)

        mock_fill_movie_details.assert_called_once()

    def test_get_movie_not_found(self):
        url = reverse("movie-detail", kwargs={"pk": 99999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch("movienight.movies.api.views.search_and_save")
    @patch("movienight.movies.api.views.MovieSearchSerializer")
    def test_search_movie_search_and_save_called(
        self, mock_search_serializer, mock_search_and_save
    ):
        serializer_instance = MagicMock()
        serializer_instance.is_valid.return_value = True
        serializer_instance.data = {"term": "test"}
        mock_search_serializer.return_value = serializer_instance

        url = reverse("movie-search")
        response = self.client.get(url, {"term": "test"})
        mock_search_and_save.assert_called_once()

    @patch("movienight.movies.api.serializers.MovieSearchSerializer.is_valid")
    def test_search_movie_invalid_search_term(self, mock_search_serializer_is_valid):
        mock_search_serializer_is_valid.return_value = False

        url = reverse("movie-search")
        response = self.client.get(url, {"term": "test"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("movienight.movies.api.views.search_and_save")
    def test_search_movie(self, search_and_save_mock):
        for i in range(5):
            genre = GenreFactory.create()
            movie = MovieFactory.create(title=f"test {i}")
            movie.genres.set([genre])
        url = reverse("movie-search")
        response = self.client.get(url, {"term": "test"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)
        for i in range(5):
            self.assertEqual(response.data[i]["title"], f"test {i}")

    @patch("movienight.movies.api.views.search_and_save")
    def test_search_movie_no_results(self, search_and_save_mock):
        url = reverse("movie-search")
        response = self.client.get(url, {"term": "test"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
