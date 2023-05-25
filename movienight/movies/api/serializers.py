from rest_framework import serializers
from django.utils import timezone


from movienight.accounts.api.serializers import UserSerializer
from ..models import Movie, MovieNight


class GenreField(serializers.SlugRelatedField):
    def to_internal_value(self, data):
        try:
            return self.get_queryset().get_or_create(name=data)[0]
        except (TypeError, ValueError):
            self.fail(f"Tag value {data} is invalid")


class MovieSerializer(serializers.ModelSerializer):
    genres = GenreField(slug_field="name", many=True, read_only=True)

    class Meta:
        model = Movie
        fields = "genres", "id", "imdb_id", "plot", "runtime_minutes", "title", "year"


class MovieSearchSerializer(serializers.Serializer):
    term = serializers.CharField()


class MovieNightSerializer(serializers.ModelSerializer):
    movie = MovieSerializer()
    creator = UserSerializer()

    class Meta:
        model = MovieNight
        fields = "id", "movie", "start_time", "creator"


class MovieNightCreateSerializer(serializers.ModelSerializer):
    movie = serializers.HyperlinkedRelatedField(
        view_name="movie-detail", queryset=Movie.objects.all()
    )
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = MovieNight
        fields = "id", "movie", "start_time", "creator"
        read_only_fields = ("id",)

    def validate_start_time(self, value):
        """
        Checks if the provided start_time is not in the past.
        """
        if value < timezone.now():
            raise serializers.ValidationError("Start time must be in the future.")
        return value
