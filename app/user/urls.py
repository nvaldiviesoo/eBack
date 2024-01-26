"""
URL mapping for the user app
"""

from django.urls import path
from user import views

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='custom_user_login'),
    path('signup/', views.UserRegistrationView.as_view(), name="sign_up"),
]
