from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MovieViewSet, MovieNightViewSet


router = DefaultRouter()
router.register("movie-nights", MovieNightViewSet)
router.register("", MovieViewSet)


urlpatterns = [path("", include(router.urls))]
