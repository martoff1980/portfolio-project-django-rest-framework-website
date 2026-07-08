from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from orders.models import Order, Ticket
from train_station.serializers import JourneyListSerializer


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("id", "cargo", "seat", "journey")
        validators = []

    def validate(self, attrs):
        """
        Validation:
        Check that the selected cargo and seat exist in the train,
        and that they are not already booked
        (additional check to unique_together)
        """
        data = super().validate(attrs)
        journey = attrs["journey"]
        train = journey.train

        # Checking if the cargo number is valid for the given train.
        # The cargo number must be between 1
        # and the total number of cargos in the train.
        if attrs["cargo"] > train.cargo_num or attrs["cargo"] < 1:
            raise ValidationError(
                {"cargo": f"Total {train.cargo_num} cargos in this train."}
            )

        # Checking if the seat number is valid for the given cargo.
        # The seat number must be between 1
        # and the number of seats in the cargo.
        if attrs["seat"] > train.places_in_cargo or attrs["seat"] < 1:
            raise ValidationError(
                {
                    "seat":
                        f"In each cargo,"
                        f"there are only {train.places_in_cargo} seats."
                }
            )

        # Chacking if the seat is already booked for
        # the given journey, cargo, and seat.
        # UniqueTogetherValidator from DRF will trigger automatically,
        # but the manual filter provides a nicer JSON error message.
        if Ticket.objects.filter(
            journey=journey, cargo=attrs["cargo"], seat=attrs["seat"]
        ).exists():
            raise ValidationError(
                "This seat is already booked by another passenger."
                "Please choose a different seat."
            )

        return data


class TicketListSerializer(TicketSerializer):
    """Used for displaying tickets within order details"""
    journey = JourneyListSerializer(read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    # Order is created along with a list of tickets
    # (Writable Nested Serializer)
    tickets = TicketSerializer(many=True, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "tickets", "created_at")

    def create(self, validated_data):
        """
        Custom create method to handle nested ticket creation.
        The atomic transaction is handled in the ViewSet
        """
        tickets_data = validated_data.pop("tickets")
        order = Order.objects.create(**validated_data)

        try:
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
        except IntegrityError:
            raise ValidationError(
                "Selected seat is already taken. Please try again."
            )

        return order

    def update(self, instance, validated_data):
        tickets_data = validated_data.pop("tickets", None)

        # Send current order to the ticket context so that
        # the validator can exclude them
        self.context["order"] = instance

        if tickets_data is not None:
            # This is a simple PUT logic:
            # we delete the old tickets of the order
            # and create the sent ones again
            instance.tickets.all().delete()
            for ticket_data in tickets_data:
                Ticket.objects.create(order=instance, **ticket_data)

        return super().update(instance, validated_data)


class OrderListSerializer(OrderSerializer):
    """
    Read-only serializer for listing orders
    with their tickets and journeys
    """
    tickets = TicketListSerializer(many=True, read_only=True)
