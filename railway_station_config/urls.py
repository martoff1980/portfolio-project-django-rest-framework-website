from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Import the necessary views for Swagger documentation
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # Endpoints for our applications
    path(
        "api/train-station/",
        include("train_station.urls", namespace="train_station")
    ),
    path("api/orders/", include("orders.urls", namespace="orders")),
    # Add the following two lines to enable JWT authentication endpoints
    path(
        "api/user/token/",
        TokenObtainPairView.as_view(),
        name="token_obtain_pair"
    ),
    path(
        "api/user/token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh"
    ),
    # Add the following two lines to enable Swagger documentation
    path("api/doc/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/doc/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]
