from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.utils import timezone

from movienight.accounts.models import User
from movienight.movies.models import Movie, MovieNight
from movienight.movies.tests.factories import (
    MovieFactory,
    MovieNightFactory,
)


class MovieNightListAPITest(APITestCase):
    def setUp(self):
        self.movie_nights = MovieNightFactory.create_batch(5)

        self.user = User.objects.create_user(
            email="test@example.com", password="testpassword"
        )
        self.client.force_authenticate(self.user)

    def test_list(self):
        url = reverse("movienight-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.movie_nights))
        for i in range(len(self.movie_nights)):
            self.assertEqual(len(response.data[i].keys()), 4)
            self.assertEqual(response.data[i]["id"], self.movie_nights[i].id)
            self.assertEqual(
                response.data[i]["movie"]["id"], self.movie_nights[i].movie.id
            )
            self.assertEqual(
                response.data[i]["movie"]["title"], self.movie_nights[i].movie.title
            )
            self.assertEqual(
                response.data[i]["movie"]["imdb_id"], self.movie_nights[i].movie.imdb_id
            )
            self.assertEqual(
                response.data[i]["movie"]["year"], self.movie_nights[i].movie.year
            )
            self.assertEqual(
                response.data[i]["movie"]["runtime_minutes"],
                self.movie_nights[i].movie.runtime_minutes,
            )
            self.assertEqual(
                response.data[i]["movie"]["plot"], self.movie_nights[i].movie.plot
            )
            self.assertEqual(len(response.data[i]["movie"].keys()), 7)
            self.assertEqual(
                response.data[i]["start_time"],
                self.movie_nights[i].start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            )
            self.assertEqual(
                response.data[i]["creator"]["email"], self.movie_nights[i].creator.email
            )
            self.assertEqual(
                response.data[i]["creator"]["first_name"],
                self.movie_nights[i].creator.first_name,
            )
            self.assertEqual(
                response.data[i]["creator"]["last_name"],
                self.movie_nights[i].creator.last_name,
            )
            self.assertEqual(len(response.data[i]["creator"].keys()), 3)

    def test_list_sorted_by_start_time(self):
        url = f"{reverse('movienight-list')}?ordering=start_time"

        response = self.client.get(url)

        start_times = [movie_night.start_time for movie_night in self.movie_nights]
        sorted_start_times = sorted(start_times)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i, movie_night_data in enumerate(response.data):
            self.assertEqual(
                movie_night_data["start_time"],
                sorted_start_times[i].strftime("%Y-%m-%dT%H:%M:%SZ"),
            )

    def test_list_movie_night_unauthenticated(self):
        url = reverse("movienight-list")
        self.client.logout()  # Unauthenticate the client
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class MovieNightCreateAPITest(APITestCase):
    def setUp(self):
        self.movie_nights = MovieNightFactory.create_batch(5)
        self.user = User.objects.create_user(
            email="test@example.com", password="testpassword"
        )
        self.client.force_authenticate(self.user)

    def test_create_movie_night(self):
        url = reverse("movienight-list")
        movie = MovieFactory()
        start_time = timezone.now() + timezone.timedelta(days=7)

        data = {
            "movie": reverse("movie-detail", args=[movie.id]),
            "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MovieNight.objects.count(), len(self.movie_nights) + 1)
        created_movie_night = MovieNight.objects.latest("id")
        self.assertEqual(created_movie_night.movie, movie)
        self.assertEqual(
            created_movie_night.start_time.strftime("%Y-%m-%dT%H:%M:%S"),
            start_time.strftime("%Y-%m-%dT%H:%M:%S"),
        )

        self.assertEqual(created_movie_night.creator, self.user)

    def test_create_movie_night_with_nonexistent_movie(self):
        url = reverse("movienight-list")
        start_time = timezone.now() + timezone.timedelta(days=7)
        nonexistent_movie_id = 99999  # not exist in database

        data = {
            "movie": reverse("movie-detail", args=[nonexistent_movie_id]),
            "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Verify that no new MovieNight objects have been created
        self.assertEqual(MovieNight.objects.count(), len(self.movie_nights))

    def test_create_movie_night_with_past_start_time(self):
        url = reverse("movienight-list")
        # Set the start time to a day in the past
        past_start_time = timezone.now() - timezone.timedelta(days=1)

        data = {
            "movie": reverse("movie-detail", args=[self.movie_nights[0].movie.id]),
            "start_time": past_start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Verify that no new MovieNight objects have been created
        self.assertEqual(MovieNight.objects.count(), len(self.movie_nights))

    def test_create_movie_night_unauthenticated(self):
        url = reverse("movienight-list")
        start_time = timezone.now() + timezone.timedelta(days=7)

        data = {
            "movie": reverse("movie-detail", args=[self.movie_nights[0].movie.id]),
            "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
        }

        self.client.logout()  # Unauthenticate the client
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Verify that no new MovieNight objects have been created
        self.assertEqual(MovieNight.objects.count(), len(self.movie_nights))


class MovieNightRetrieveAPITest(APITestCase):
    def setUp(self):
        self.movie_nights = MovieNightFactory.create_batch(5)

        self.user = User.objects.create_user(
            email="test@example.com", password="testpassword"
        )
        self.client.force_authenticate(self.user)

    def test_retrieve(self):
        url = reverse("movienight-detail", args=[self.movie_nights[0].id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.movie_nights[0].id)
        self.assertEqual(response.data["movie"]["id"], self.movie_nights[0].movie.id)
        self.assertEqual(
            response.data["movie"]["title"], self.movie_nights[0].movie.title
        )
        self.assertEqual(
            response.data["movie"]["imdb_id"], self.movie_nights[0].movie.imdb_id
        )
        self.assertEqual(
            response.data["movie"]["year"], self.movie_nights[0].movie.year
        )
        self.assertEqual(
            response.data["movie"]["runtime_minutes"],
            self.movie_nights[0].movie.runtime_minutes,
        )
        self.assertEqual(
            response.data["movie"]["plot"], self.movie_nights[0].movie.plot
        )
        self.assertEqual(len(response.data["movie"].keys()), 7)
        self.assertEqual(
            response.data["start_time"],
            self.movie_nights[0].start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        )
        self.assertEqual(
            response.data["creator"]["email"], self.movie_nights[0].creator.email
        )
        self.assertEqual(
            response.data["creator"]["first_name"],
            self.movie_nights[0].creator.first_name,
        )
        self.assertEqual(
            response.data["creator"]["last_name"],
            self.movie_nights[0].creator.last_name,
        )
        self.assertEqual(len(response.data["creator"].keys()), 3)

    def test_retrieve_nonexistent_movie_night(self):
        non_existent_id = max(mn.id for mn in self.movie_nights) + 1
        url = reverse("movienight-detail", args=[non_existent_id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_movie_night_unauthenticated(self):
        url = reverse("movienight-detail", args=[self.movie_nights[0].id])

        self.client.logout()  # Unauthenticate the client
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class MovieNightUpdateAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="testpassword"
        )
        self.movie_night = MovieNightFactory(
            start_time=timezone.now() + timezone.timedelta(days=7), creator=self.user
        )
        self.update_movie = Movie.objects.create(
            title="test_movie_title", year=2021, runtime_minutes=120
        )
        self.client.force_authenticate(self.user)

        self.start_time = timezone.now() + timezone.timedelta(days=7)
        self.update_data = {
            "id": self.movie_night.id,
            "movie": reverse("movie-detail", args=[self.update_movie.id]),
            "start_time": self.start_time.strftime("%Y-%m-%dT%H:%M:%S"),
        }

    def test_update_movie_night(self):
        url = reverse("movienight-detail", kwargs={"pk": self.movie_night.id})
        start_time = timezone.now() + timezone.timedelta(days=7)

        response = self.client.put(url, self.update_data, format="json")

        self.movie_night.refresh_from_db()
        updated_start_time = self.movie_night.start_time
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            updated_start_time.strftime("%Y-%m-%dT%H:%M:%S"),
            start_time.strftime("%Y-%m-%dT%H:%M:%S"),
        )

    def test_update_unauthorized_user(self):
        url = reverse("movienight-detail", kwargs={"pk": self.movie_night.id})

        self.client.logout()
        response = self.client.put(url, self.update_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_non_existent_id(self):
        url = reverse("movienight-detail", kwargs={"pk": 9999})
        response = self.client.put(url, self.update_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_user_not_creator(self):
        new_user = User.objects.create_user(
            email="other@example.com", password="testpassword"
        )
        self.client.force_authenticate(user=new_user)

        url = reverse("movienight-detail", kwargs={"pk": self.movie_night.id})
        response = self.client.put(url, self.update_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_past_start_time(self):
        past_time = (timezone.now() - timezone.timedelta(days=7)).strftime(
            "%Y-%m-%dT%H:%M:%S"
        )
        update_data = {
            "id": self.movie_night.id,
            "movie": reverse("movie-detail", args=[self.update_movie.id]),
            "start_time": past_time,
        }

        url = reverse("movienight-detail", kwargs={"pk": self.movie_night.id})
        response = self.client.put(url, update_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("start_time", response.data)

    def test_update_invalid_time_format(self):
        invalid_time_format = {"start_time": "2023-06-02 04:30"}

        update_data = {
            "id": self.movie_night.id,
            "movie": reverse("movie-detail", args=[self.update_movie.id]),
            "start_time": invalid_time_format,
        }

        url = reverse("movienight-detail", kwargs={"pk": self.movie_night.id})
        response = self.client.put(url, update_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("start_time", response.data)

    def test_update_non_existent_movie(self):
        non_existent_movie_url = reverse("movie-detail", kwargs={"pk": 9999})
        invalid_data = {
            "movie": non_existent_movie_url,
            "id": self.movie_night.id,
            "start_time": self.start_time.strftime("%Y-%m-%dT%H:%M:%S"),
        }

        url = reverse("movienight-detail", kwargs={"pk": self.movie_night.id})
        response = self.client.put(url, invalid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("movie", response.data)
