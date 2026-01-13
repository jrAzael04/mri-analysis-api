# api/views.py

# Importaciones de Django/DRF
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser 
import uuid 

# Importaciones para procesamiento de imágenes
import base64
from io import BytesIO
from PIL import Image
import cv2 
import numpy as np # Necesario para la manipulación de arrays de CV2

# Importa tus funciones utilitarias y Serializers
from .utils import preprocess_and_predict, generate_analysis_image
from .serializers import ImageUploadSerializer, AnalysisResponseSerializer 


# --------------------------------------------------------------------------
# --- Función Auxiliar para Codificación Base64 (CORREGIDA Y ROBUSTA) ---
# --------------------------------------------------------------------------
# api/views.py

# ... (otras importaciones) ...
import base64
from io import BytesIO
from PIL import Image
import cv2 
import numpy as np
# ... (otras importaciones) ...

# --------------------------------------------------------------------------
# --- Función Auxiliar para Codificación Base64 (VERSIÓN CORREGIDA) ---
# --------------------------------------------------------------------------
def encode_cv2_image_to_base64(img_cv2):

    if img_cv2.ndim == 3 and img_cv2.shape[2] == 3:
        # Convertir de BGR a RGB
        img_rgb = cv2.cvtColor(img_cv2, cv2.COLOR_BGR2RGB)
    else:
        img_rgb = img_cv2
        
    is_success, buffer = cv2.imencode(".png", img_rgb)

    if not is_success:
        raise ValueError("Error al codificar la imagen con cv2.imencode.")
    
    # 3. Convertir el buffer de NumPy a Base64 string
    base64_encoded = base64.b64encode(buffer).decode("utf-8")
    
    return base64_encoded


# --------------------------------------------------------------------------
# --- Vista Principal (ScanAnalysisView) ---
# --------------------------------------------------------------------------
class ScanAnalysisView(APIView):
    """
    Vista de la API que maneja la petición POST para analizar una resonancia magnética.
    """
    parser_classes = (MultiPartParser, FormParser)

    # MÉTODO POST: INDENTADO CORRECTAMENTE DENTRO DE LA CLASE
    def post(self, request, *args, **kwargs):
        
        serializer = ImageUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # DEFINICIÓN DE VARIABLES CRÍTICAS
        image_file = request.FILES.get('image') 
        patient_id = serializer.validated_data.get('patient_id')

        try:
            # 1. Preprocesamiento y Predicción
            results = preprocess_and_predict(image_file)
            
            # 2. Generación de Imagen Analizada
            analyzed_image_cv2 = generate_analysis_image(
                results['original_image_cv2'], 
                results['tumor_present']
            )

            # 3. Codificación de Imágenes a Base64
            original_base64 = encode_cv2_image_to_base64(results['original_image_cv2'])
            analyzed_base64 = encode_cv2_image_to_base64(analyzed_image_cv2)

            # 4. Construcción de la Respuesta Final
            tumor_present = results['tumor_present']
            confidence = results['confidence']

            response_data = {
                "analysis_id": str(uuid.uuid4()),
                "patient_id": patient_id,
                "tumor_present": tumor_present,
                "confidence": confidence,
                "tumor_description": "Posible tumor detectado" if tumor_present == 1 else "No se detectó tumor",
                "message": "Análisis ML y generación de imagen completados.",
                "original_image_base64": original_base64,
                "analyzed_image_base64": analyzed_base64,
            }

            response_serializer = AnalysisResponseSerializer(response_data)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            # Bloque de error para debug y respuesta 500
            import traceback
            print("--- ERROR FATAL EN LA API (DEBUG) ---")
            traceback.print_exc()
            print(f"Mensaje de error: {e}")
            print("--------------------------------------")
            
            return Response(
                {"error": "Error interno del servidor", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )