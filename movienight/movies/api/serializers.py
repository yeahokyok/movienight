from rest_framework import serializers

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
        fields = "__all__"


class MovieSearchSerializer(serializers.Serializer):
    term = serializers.CharField()


class MovieNightSerializer(serializers.ModelSerializer):
    movie = MovieSerializer()

    class Meta:
        model = MovieNight
        fields = "__all__"
