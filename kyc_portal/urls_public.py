from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.conf.urls.static import static
from django.urls import path, include
from django.conf import settings


urlpatterns = [
    path('api/v1/tenants/', include('customers.urls')),
    path('api/schema/', SpectacularAPIView.as_view(urlconf='kyc_portal.urls_public'), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)