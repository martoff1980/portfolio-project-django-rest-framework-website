from django.urls import path, include
from rest_framework.routers import DefaultRouter

from train_station.views import (
    CrewViewSet,
    TrainTypeViewSet,
    StationViewSet,
    RouteViewSet,
    TrainViewSet,
    JourneyViewSet,
)

router = DefaultRouter()
router.register("crews", CrewViewSet)
router.register("train-types", TrainTypeViewSet)
router.register("stations", StationViewSet)
router.register("routes", RouteViewSet)
router.register("trains", TrainViewSet)
router.register("journeys", JourneyViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "train_station"
