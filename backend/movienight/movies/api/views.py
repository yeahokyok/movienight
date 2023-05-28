from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from ..models import Movie, MovieNight
from .serializers import (
    MovieNightSerializer,
    MovieSerializer,
    MovieSearchSerializer,
    MovieNightWriteSerializer,
)
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
            return Response(status=status.HTTP_400_BAD_REQUEST)
        term = search_serializer.data["term"]

        search_and_save(term)

        movies = self.get_queryset().filter(title__icontains=term)

        return Response(
            MovieSerializer(movies, many=True, context={"request": request}).data
        )


class MovieNightViewSet(viewsets.ModelViewSet):
    queryset = MovieNight.objects.all()
    serializer_class = MovieNightSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ["start_time"]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ["POST", "PUT"]:
            return MovieNightWriteSerializer
        return MovieNightSerializer

    def perform_update(self, serializer):
        if self.request.user != serializer.instance.creator:
            raise PermissionDenied()
        serializer.save()
