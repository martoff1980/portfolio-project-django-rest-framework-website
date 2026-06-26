from django.contrib import admin
from orders.models import Order, Ticket


class TicketInline(admin.TabularInline):
    """Позволяет просматривать и редактировать билеты прямо внутри страницы заказа"""
    model = Ticket
    extra = 1  # Количество пустых строк для добавления новых билетов вручную
    fields = ("cargo", "seat", "journey")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at")
    list_display_links = ("id", "user")
    list_filter = ("created_at",)
    search_fields = ("user__email",)
    # Подключаем вложенное отображение билетов
    inlines = [TicketInline]


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("id", "journey", "cargo", "seat", "order")
    list_display_links = ("id", "journey")
    list_filter = ("journey", "cargo")
    search_fields = ("order__user__email", "journey__route__source__name")