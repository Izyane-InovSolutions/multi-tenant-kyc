from django.urls import path
from .views import TenantListCreateView, TenantDetailView

urlpatterns = [
    path('', TenantListCreateView.as_view()),
    path('<int:pk>/', TenantDetailView.as_view()),
]