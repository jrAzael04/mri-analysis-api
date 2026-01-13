# api/urls.py

from django.urls import path
from .views import ScanAnalysisView # Importa tu vista de la API

urlpatterns = [
    # Mapea la ruta 'classify/' a la vista ScanAnalysisView
    # La URL final será: /api/v1/ + classify/
    path('classify/', ScanAnalysisView.as_view(), name='scan-analysis'),
]