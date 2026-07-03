from django.db.models import F, Count

from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly

from train_station.models import Crew, TrainType, Station, Route, Train, Journey
from train_station import serializers


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = serializers.CrewSerializer


class TrainTypeViewSet(viewsets.ModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = serializers.TrainTypeSerializer
    
    def get_queryset(self):
        queryset = self.queryset
        # Фильтрация поездов по типу (например: ?train_type=1)
        train_type_id = self.request.query_params.get("train_type")
        if train_type_id:
            queryset = queryset.filter(train_type_id=train_type_id)
        return queryset
    
    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return serializers.TrainListSerializer
        return serializers.TrainSerializer    


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = serializers.StationSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,) 
    # Свойство IsAuthenticatedOrReadOnly в сочетании с глобальными настройками 
    # или явная проверка на Admin при записи обеспечит нужный уровень безопасности.
    
    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAdminUser()]
        return [IsAuthenticatedOrReadOnly()]


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

        # Optimization of queries for different actions
        if self.action == "list":
            # Counting tickets for each journey and calculating available seats
            # Total seats = (number of cargo cars * seats in cargo)
            # - number of purchased tickets
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

        # Filtering journeys by route ID if provided in query parameters
        route_id = self.request.query_params.get("route")
        if route_id:
            queryset = queryset.filter(route_id=route_id)

        # Filtering journeys by source station name if provided in query parameters
        source_station = self.request.query_params.get("source")
        if source_station:
            queryset = queryset.filter(route__source__name__icontains=source_station)

        # Filtering journeys by destination station name if provided in query parameters
        destination_station = self.request.query_params.get("destination")
        if destination_station:
            queryset = queryset.filter(route__destination__name__icontains=destination_station)
        return queryset.order_by("departure_time")


    def get_serializer_class(self):
        if self.action == "list":
            return serializers.JourneyListSerializer
        if self.action == "retrieve":
            return serializers.JourneyDetailSerializer
        return serializers.JourneySerializer