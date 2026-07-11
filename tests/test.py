from django.utils import timezone
from train_station.models import Station, Route, TrainType, Train, Journey
from orders.models import Order, Ticket

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model

ORDER_URL = reverse("orders:order-list")


class OrderAndTicketTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="passenger@test.com", password="password123"
        )
        self.client.force_authenticate(user=self.user)

        # Create stations, route, train type, train, and journey
        self.station1 = Station.objects.create(
            name="Kyiv",
            latitude=50.4,
            longitude=30.5
        )
        self.station2 = Station.objects.create(
            name="Lviv",
            latitude=49.8,
            longitude=24.0
        )
        self.route = Route.objects.create(
            source=self.station1,
            destination=self.station2,
            distance=540
        )

        self.train_type = TrainType.objects.create(name="Intercity")
        # Train: 2 cargos, 10 seats in each cargo
        self.train = Train.objects.create(
            name="Test Train",
            cargo_num=2,
            places_in_cargo=10,
            train_type=self.train_type
        )

        self.journey = Journey.objects.create(
            route=self.route,
            train=self.train,
            departure_time=timezone.now() + timezone.timedelta(days=1),
            arrival_time=timezone.now() + timezone.timedelta(days=1, hours=5),
        )

    def test_create_valid_ticket_order(self):
        """Successful creation of an order for a free seat"""
        payload = {
            "tickets": [
                {"cargo": 1, "seat": 5, "journey": self.journey.id}
            ]
        }
        response = self.client.post(ORDER_URL, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Ticket.objects.count(), 1)

    def test_cannot_book_taken_seat(self):
        """
        Create an order and a ticket for the
        same journey, cargo, and seat
        """
        existing_order = Order.objects.create(user=self.user)
        Ticket.objects.create(
            cargo=1,
            seat=5,
            journey=self.journey,
            order=existing_order
        )

        # try to book the same seat again
        payload = {
            "tickets": [
                {"cargo": 1, "seat": 5, "journey": self.journey.id}
            ]
        }
        response = self.client.post(ORDER_URL, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_book_non_existing_cargo_or_seat(self):
        """
        Validator should reject the request if the cargo number
        or seat number exceeds the train's capacity.
        """
        payload = {
            "tickets": [
                {"cargo": 5, "seat": 5, "journey": self.journey.id}
            ]
        }
        response = self.client.post(ORDER_URL, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
