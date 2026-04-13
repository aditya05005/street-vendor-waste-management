# users/urls.py

from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('auth/register/', views.register),
    path('auth/login/', views.login),
    path('auth/refresh/', TokenRefreshView.as_view()),  # refresh token built-in

    path('vendors/', views.vendor_list),
    path('vendors/qr/<str:qr_code>/', views.vendor_by_qr),

    path('pickups/', views.create_pickup),
    path('pickups/mine/', views.my_pickups),
]
