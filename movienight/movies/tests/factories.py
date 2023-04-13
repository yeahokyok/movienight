import factory

from ..models import Genre, Movie


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
