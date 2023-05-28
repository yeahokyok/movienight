from datetime import timedelta
from django.db import models
from django.contrib.auth import get_user_model


UserModel = get_user_model()


class SearchTerm(models.Model):
    class Meta:
        ordering = ["id"]

    term = models.TextField(unique=True)
    last_search = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.term


class Genre(models.Model):
    name = models.TextField(unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.TextField()
    year = models.PositiveIntegerField()
    runtime_minutes = models.PositiveIntegerField(null=True)
    imdb_id = models.SlugField(unique=True)
    genres = models.ManyToManyField(Genre, related_name="movies")
    plot = models.TextField(null=True, blank=True)
    is_full_record = models.BooleanField(default=False)

    class Meta:
        ordering = ["title", "year"]

    def __str__(self):
        return f"{self.title} ({self.year})"


class MovieNight(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.PROTECT)
    start_time = models.DateTimeField()
    creator = models.ForeignKey(UserModel, on_delete=models.PROTECT)

    class Meta:
        ordering = ["creator", "start_time"]

    @property
    def end_time(self):
        return (
            self.start_time + timedelta(minutes=self.movie.runtime_minutes)
            if self.movie.runtime_minutes
            else None
        )

    def __str__(self):
        return f"{self.movie.title} ({self.movie.year}) - {self.creator.email}"
