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


# Serializer for Route model
class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteListCellSerializer(RouteSerializer):
    """Used for displaying routes in a list with source and destination names"""
    source = serializers.CharField(source="source.name", read_only=True)
    destination = serializers.CharField(source="destination.name", read_only=True)


# Serializer for Train model
class TrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = ("id", "name", "cargo_num", "places_in_cargo", "train_type")


class TrainListSerializer(TrainSerializer):
    train_type = serializers.CharField(source="train_type.name", read_only=True)


# Serializer for Journey model
class JourneySerializer(serializers.ModelSerializer):
    class Meta:
        model = Journey
        fields = ("id", "route", "train", "departure_time", "arrival_time", "crew")


class JourneyListSerializer(serializers.ModelSerializer):
    """For displaying a list of journeys with brief information"""
    route_title = serializers.CharField(source="route.__str__", read_only=True)
    train_name = serializers.CharField(source="train.name", read_only=True)
    # Count the number of available tickets at the ViewSet level through annotation later
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
    """For detailed viewing of a journey with all nested information"""
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
        """Returns a list of already purchased tickets (cargo, seat)"""
        return [
            {"cargo": ticket.cargo, "seat": ticket.seat}
            for ticket in obj.tickets.all()
        ]