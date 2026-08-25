from customers.Views.Auth.AuthView import LoginView, LogoutView, RefreshView

from .Views.Client.ClientViews import TenantListView, TenantDetailView, TenantSignUpView
from django.urls import path


urlpatterns = [
    path('', TenantListView.as_view()),
    path('<int:pk>/', TenantDetailView.as_view()),
    path('signup/', TenantSignUpView.as_view()),
    path('auth/login/', LoginView.as_view()),
    path('auth/refresh/', RefreshView.as_view()),
    path('auth/logout/', LogoutView.as_view()),
]