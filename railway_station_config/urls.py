from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
# Импорты для Swagger (drf-spectacular — современный стандарт для DRF)
from drf_spectacular.views import (
    DrfSpectacularAPIView,
    DrfSpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # Эндпоинты наших приложений
    path("api/train-station/", include("train_station.urls", namespace="train_station")),
    path("api/orders/", include("orders.urls", namespace="orders")),
    
    # Аутентификация по JWT токенам
    path("api/user/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/user/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    
    # Автоматическая документация API (Swagger)
    path("api/schema/", DrfSpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger-ui/", DrfSpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]