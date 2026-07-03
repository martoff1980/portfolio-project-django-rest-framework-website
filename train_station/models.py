from django.db import models


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class TrainType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Station(models.Model):
    name = models.CharField(max_length=255, unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.ForeignKey(
        Station, 
        on_delete=models.CASCADE, 
        related_name="route_sources"
    )
    destination = models.ForeignKey(
        Station, 
        on_delete=models.CASCADE, 
        related_name="route_destinations"
    )
    distance = models.IntegerField()

    def __str__(self):
        return f"{self.source.name} - {self.destination.name} ({self.distance} km)"


class Train(models.Model):
    name = models.CharField(max_length=255)
    cargo_num = models.IntegerField()
    places_in_cargo = models.IntegerField()
    train_type = models.ForeignKey(
        TrainType, 
        on_delete=models.CASCADE, 
        related_name="trains"
    )

    def __str__(self):
        return f"Train: {self.name} ({self.train_type.name})"


class Journey(models.Model):
    route = models.ForeignKey(
        Route, 
        on_delete=models.CASCADE, 
        related_name="journeys"
    )
    train = models.ForeignKey(
        Train, 
        on_delete=models.CASCADE, 
        related_name="journeys"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    # Connected to Crew via a many-to-many relationship, since multiple crew members can be assigned to a single journey,
    # and the related_name allows accessing all journeys associated with a specific crew member.
    crew = models.ManyToManyField(Crew, related_name="journeys")

    def __str__(self):
        return f"Journey {self.id}: {self.route} at {self.departure_time.strftime('%Y-%m-%d %H:%M')}"