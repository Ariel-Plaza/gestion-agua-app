from django.contrib import admin
from django.urls import path, include

from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenBlacklistView,
    TokenObtainPairView,
)

from usuarios.serializer import CustomTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

urlpatterns = [
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('admin/', admin.site.urls),
    path('boletas/', include('boletas.urls')),
    path('cortes/', include('cortes.urls')),
    # path('lecturas/', include('lecturas.urls')),
    # path('reportes/', include('reportes.urls')),
    path('socios/', include('socios.urls')),
    # path('usuarios/', include('usuarios.urls')),
    path('lecturas/', include('lecturas.urls')),
    
]