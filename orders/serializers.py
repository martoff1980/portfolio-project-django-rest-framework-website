from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from orders.models import Order, Ticket
from train_station.serializers import JourneyListSerializer


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("id", "cargo", "seat", "journey")

    def validate(self, attrs):
        """
        Валидация: проверяем, что выбранный вагон и место существуют в поезде,
        и что они не заняты (дополнительная проверка к unique_together).
        """
        data = super().validate(attrs)
        journey = attrs["journey"]
        train = journey.train

        # 1. Проверка существования вагона
        if attrs["cargo"] > train.cargo_num or attrs["cargo"] < 1:
            raise ValidationError(
                {"cargo": f"В этом поезде всего {train.cargo_num} вагонов(а)."}
            )

        # 2. Проверка существования места в вагоне
        if attrs["seat"] > train.places_in_cargo or attrs["seat"] < 1:
            raise ValidationError(
                {"seat": f"В каждом вагоне всего {train.places_in_cargo} мест(а)."}
            )

        # 3. Проверка занятости места на уровне бизнес-логики (для понятной ошибки)
        # UniqueTogetherValidator от DRF сработает автоматически, но ручной фильтр дает красивый JSON ошибки
        if Ticket.objects.filter(
            journey=journey, 
            cargo=attrs["cargo"], 
            seat=attrs["seat"]
        ).exists():
            raise ValidationError(
                "Это место уже забронировано другим пассажиром."
            )

        return data


class TicketListSerializer(TicketSerializer):
    """Используется для вывода билетов внутри деталей заказа"""
    journey = JourneyListSerializer(read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    # Заказ создается вместе со списком билетов (Writable Nested Serializer)
    tickets = TicketSerializer(many=True, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "tickets", "created_at")

    def create(self, validated_data):
        """
        Кастомный метод создания, так как мы используем вложенные билеты.
        Оборачивание в транзакцию atomic будет происходить во ViewSet.
        """
        tickets_data = validated_data.pop("tickets")
        order = Order.objects.create(**validated_data)
        
        try:
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
        except IntegrityError:
            raise ValidationError("Одно из выбранных мест уже занято. Попробуйте еще раз.")
            
        return order


class OrderListSerializer(OrderSerializer):
    """Для красивого просмотра истории заказов пользователя"""
    tickets = TicketListSerializer(many=True, read_only=True)