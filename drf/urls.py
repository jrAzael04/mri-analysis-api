from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Ruta de administración
    path('admin/', admin.site.urls),
    
    # ----------------------------------------------------
    # CORRECCIÓN: Usamos 'include' para las rutas de la app 'api'
    # Esto le dice a Django: busca el archivo api/urls.py
    # ----------------------------------------------------
    path('api/v1/', include('api.urls')),
]