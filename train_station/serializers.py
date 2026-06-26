from rest_framework import serializers

from train_station.models import Crew, TrainType, Station, Route, Train, Journey


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")


class TrainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = ("id", "name")


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ("id", "name", "latitude", "longitude")


# Сериализаторы для Route
class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteListCellSerializer(RouteSerializer):
    """Используется для красивого отображения маршрутов списком"""
    source = serializers.CharField(source="source.name", read_only=True)
    destination = serializers.CharField(source="destination.name", read_only=True)


# Сериализаторы для Train
class TrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = ("id", "name", "cargo_num", "places_in_cargo", "train_type")


class TrainListSerializer(TrainSerializer):
    train_type = serializers.CharField(source="train_type.name", read_only=True)


# Сериализаторы для Journey
class JourneySerializer(serializers.ModelSerializer):
    class Meta:
        model = Journey
        fields = ("id", "route", "train", "departure_time", "arrival_time", "crew")


class JourneyListSerializer(serializers.ModelSerializer):
    """Для вывода списка рейсов с краткой информацией"""
    route_title = serializers.CharField(source="route.__str__", read_only=True)
    train_name = serializers.CharField(source="train.name", read_only=True)
    # Посчитаем количество доступных мест на уровне ViewSet через аннотацию позже
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Journey
        fields = (
            "id", 
            "route_title", 
            "train_name", 
            "departure_time", 
            "arrival_time", 
            "tickets_available"
        )


class JourneyDetailSerializer(serializers.ModelSerializer):
    """Для детального просмотра рейса со всей вложенной информацией"""
    route = RouteListCellSerializer(read_only=True)
    train = TrainListSerializer(read_only=True)
    crew = CrewSerializer(many=True, read_only=True)
    taken_places = serializers.SerializerMethodField()

    class Meta:
        model = Journey
        fields = (
            "id", 
            "route", 
            "train", 
            "departure_time", 
            "arrival_time", 
            "crew", 
            "taken_places"
        )

    def get_taken_places(self, obj):
        """Возвращает список уже купленных билетов (вагон, место)"""
        return [
            {"cargo": ticket.cargo, "seat": ticket.seat}
            for ticket in obj.tickets.all()
        ]