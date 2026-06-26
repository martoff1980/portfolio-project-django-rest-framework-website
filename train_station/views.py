from django.db.models import F, Count
from rest_framework import viewsets

from train_station.models import Crew, TrainType, Station, Route, Train, Journey
from train_station import serializers


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = serializers.CrewSerializer


class TrainTypeViewSet(viewsets.ModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = serializers.TrainTypeSerializer


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = serializers.StationSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related("source", "destination")
    serializer_class = serializers.RouteSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.RouteListCellSerializer
        return serializers.RouteSerializer


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.select_related("train_type")
    serializer_class = serializers.TrainSerializer

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return serializers.TrainListSerializer
        return serializers.TrainSerializer


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = Journey.objects.all()
    serializer_class = serializers.JourneySerializer

    def get_queryset(self):
        queryset = self.queryset

        # Оптимизация запросов для разных экшенов
        if self.action == "list":
            # Считаем количество доступных мест на уровне базы данных:
            # Общее количество мест = (кол-во вагонов * мест в вагоне) - кол-во купленных билетов
            total_places = F("train__cargo_num") * F("train__places_in_cargo")
            queryset = (
                queryset
                .select_related("route__source", "route__destination", "train")
                .annotate(tickets_available=total_places - Count("tickets"))
            )
        
        if self.action == "retrieve":
            queryset = queryset.select_related(
                "route__source", 
                "route__destination", 
                "train__train_type"
            ).prefetch_related("crew", "tickets")

        # Базовая фильтрация (опционально, можно расширить через django-filter)
        route_id = self.request.query_params.get("route")
        if route_id:
            queryset = queryset.filter(route_id=route_id)

        return queryset.order_by("departure_time")

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.JourneyListSerializer
        if self.action == "retrieve":
            return serializers.JourneyDetailSerializer
        return serializers.JourneySerializer