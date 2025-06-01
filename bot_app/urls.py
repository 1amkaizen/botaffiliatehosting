
from django.urls import path
from . import views

urlpatterns = [
    path('', views.logs_dashboard, name='logs_dashboard'),
    path('webhook/', views.webhook, name='webhook'),
    path('health/', views.health_check, name='health_check'),
    path('api/stats/', views.api_stats, name='api_stats'),
    path('test/', views.test_bot, name='test_bot'),
]
