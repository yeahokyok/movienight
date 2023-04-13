from django.db import models


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
