from django.db import transaction
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from orders.models import Order
from orders import serializers


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = serializers.OrderSerializer
    # Закрываем эндпоинт авторизацией (пользователь должен войти в систему)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        # Обычные пользователи видят только свои заказы. Admin видит все.
        queryset = self.queryset.filter(user=self.request.user)
        
        # Предзагрузка данных, чтобы избежать N+1 при выводе билетов и рейсов
        if self.action in ("list", "retrieve"):
            queryset = queryset.prefetch_related(
                "tickets__journey__route__source",
                "tickets__journey__route__destination",
                "tickets__journey__train"
            )
        return queryset

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return serializers.OrderListSerializer
        return serializers.OrderSerializer

    def perform_create(self, serializer):
        # Оборачиваем сохранение заказа и билетов в контекст транзакции базы данных
        with transaction.atomic():
            serializer.save(user=self.request.user)