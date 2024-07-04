"""
URL mapping for the orders app
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import MetricsViewSet

router = DefaultRouter()
router.register(r'metrics', MetricsViewSet, basename='metrics')

urlpatterns = [
    path('', include(router.urls)),
]
