from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from movienight.accounts.models import User
from movienight.movies.models import Movie, MovieNight
from movienight.movies.tests.factories import MovieFactory, GenreFactory, MovieNightFactory
from movienight.movies.api.serializers import MovieNightSerializer



class MovieNightViewSetTest(APITestCase):
    def setUp(self):
        self.movie_nights = MovieNightFactory.create_batch(5)
        self.url = reverse("movienight-list")

    def test_list(self):
        # Test that GET to list endpoint returns expected data
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.movie_nights))
        for i in range(len(self.movie_nights)):
            self.assertEqual(len(response.data[i].keys()), 4) 
            self.assertEqual(response.data[i]['id'], self.movie_nights[i].id)
            self.assertEqual(response.data[i]['movie']['id'], self.movie_nights[i].movie.id)
            self.assertEqual(response.data[i]['movie']['title'], self.movie_nights[i].movie.title)
            self.assertEqual(response.data[i]['movie']['imdb_id'], self.movie_nights[i].movie.imdb_id)
            self.assertEqual(response.data[i]['movie']['year'], self.movie_nights[i].movie.year)
            self.assertEqual(response.data[i]['movie']['runtime_minutes'], self.movie_nights[i].movie.runtime_minutes)
            self.assertEqual(response.data[i]['movie']['plot'], self.movie_nights[i].movie.plot)
            self.assertEqual(len(response.data[i]['movie'].keys()), 7) 
            self.assertEqual(response.data[i]['start_time'], self.movie_nights[i].start_time.strftime('%Y-%m-%dT%H:%M:%SZ'))
            self.assertEqual(response.data[i]['creator']['email'], self.movie_nights[i].creator.email)
            self.assertEqual(response.data[i]['creator']['first_name'], self.movie_nights[i].creator.first_name)
            self.assertEqual(response.data[i]['creator']['last_name'], self.movie_nights[i].creator.last_name)
            self.assertEqual(len(response.data[i]['creator'].keys()), 3) 
            
    def test_list_sorted_by_start_time(self):
        url = f"{self.url}?ordering=start_time"
        response = self.client.get(url)

        start_times = [movie_night.start_time for movie_night in self.movie_nights]
        sorted_start_times = sorted(start_times)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for i, movie_night_data in enumerate(response.data):
            self.assertEqual(movie_night_data['start_time'], sorted_start_times[i].strftime('%Y-%m-%dT%H:%M:%SZ'))
  


