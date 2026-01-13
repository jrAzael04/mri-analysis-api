# api/apps.py (CORREGIDO)

from django.apps import AppConfig

class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api"

    def ready(self):
        # Importación LOCAL para evitar problemas de importación circular
        from .utils import load_ml_model 
        
        # Llamar a la función de carga del modelo al iniciar la app
        # Esto asegura que el modelo esté cargado para la primera solicitud
        load_ml_model()