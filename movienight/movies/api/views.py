from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import Movie
from .serializers import MovieSerializer, MovieSearchSerializer
from ..omdb_integration import fill_movie_details, search_and_save


class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer

    def get_object(self):
        movie_obj = super().get_object()
        return fill_movie_details(movie_obj)

    @action(methods=["get"], detail=False)
    def search(self, request):
        search_serializer = MovieSearchSerializer(data=request.GET)

        if not search_serializer.is_valid():
            return Response(search_serializer.errors)

        term = search_serializer.data["term"]

        search_and_save(term)

        movies = self.get_queryset().filter(title__icontains=term)

        return Response(
            MovieSerializer(movies, many=True, context={"request": request}).data
        )
