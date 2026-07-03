from django.contrib import admin
from train_station.models import Crew, TrainType, Station, Route, Train, Journey


@admin.register(Crew)
class CrewAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name")
    list_display_links = ("id", "first_name", "last_name")
    search_fields = ("first_name", "last_name")


@admin.register(TrainType)
class TrainTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "latitude", "longitude")
    list_display_links = ("id", "name")
    search_fields = ("name",)


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("id", "source", "destination", "distance")
    list_display_links = ("id", "source", "destination")
    list_filter = ("source", "destination")
    search_fields = ("source__name", "destination__name")


@admin.register(Train)
class TrainAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "cargo_num", "places_in_cargo", "train_type")
    list_display_links = ("id", "name")
    list_filter = ("train_type",)
    search_fields = ("name",)


@admin.register(Journey)
class JourneyAdmin(admin.ModelAdmin):
    list_display = ("id", "route", "train", "departure_time", "arrival_time")
    list_display_links = ("id", "route")
    # Filters for departure time and route for easy filtering in the admin interface
    list_filter = ("departure_time", "route")
    # Find journeys by source station name, destination station name, or train name
    search_fields = (
        "route__source__name", 
        "route__destination__name", 
        "train__name"
    )
    # Horizontal interface for selecting multiple crew members (ManyToManyField)
    filter_horizontal = ("crew",)