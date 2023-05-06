import factory
from django.utils import timezone

from ..models import Genre, Movie, MovieNight
from movienight.accounts.tests.factories import UserFactory


class GenreFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Genre

    name = factory.Sequence(lambda n: f"Genre {n}")


class MovieFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Movie

    title = factory.Sequence(lambda n: f"Movie {n}")
    year = factory.Faker("pyint", min_value=1990, max_value=2020)
    runtime_minutes = factory.Faker("pyint", min_value=30, max_value=240)
    imdb_id = factory.Sequence(lambda n: f"tt{n}")
    plot = factory.Faker("text", max_nb_chars=200)
    is_full_record = factory.Faker("pybool")


class MovieNightFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MovieNight

    movie = factory.SubFactory(MovieFactory)
    start_time = factory.Faker(
        "date_time_this_month", tzinfo=timezone.get_current_timezone()
    )
    creator = factory.SubFactory(UserFactory)
