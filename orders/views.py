from django.db import transaction
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer

from orders.models import Order
from orders import serializers


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = serializers.OrderSerializer
    # Close the endpoint with authentication (the user must be logged in)
    permission_classes = (IsAuthenticated,)
    # Update: BrowsableAPIRenderer is added to the list of renderers
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer]

    def get_queryset(self):
        # Users see only their own orders. Admin sees all.
        queryset = self.queryset.filter(user=self.request.user)

        # Reload related objects to avoid N+1 queries
        # when displaying tickets and journeys
        if self.action in ("list", "retrieve"):
            queryset = queryset.prefetch_related(
                "tickets__journey__route__source",
                "tickets__journey__route__destination",
                "tickets__journey__train",
            )
        return queryset

    # def get_queryset(self):
          # Orders are displayed only for the current authenticated user
    #     return Order.objects.filter(user=self.request.user).prefetch_related("tickets__journey")
            
    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return serializers.OrderListSerializer
        return serializers.OrderSerializer

    def perform_create(self, serializer):
        # Wrap the saving of the order and
        # tickets in a database transaction context
        with transaction.atomic():
            serializer.save(user=self.request.user)
