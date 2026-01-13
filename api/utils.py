# api/utils.py (VERSIÓN FINAL Y ROBUSTA)

import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.resnet50 import preprocess_input
import cv2
import os
import base64
import io

# --- CONFIGURACIÓN ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'best_resnet_model.h5') 
IMAGE_SIZE = (224, 224) 

ML_MODEL = None


def encode_image_to_base64(image_np: np.ndarray) -> str:
    """
    Convierte un array de NumPy (imagen OpenCV) en una cadena Base64.
    """
    # 1. Codificar la imagen de NumPy a formato de archivo (ej. PNG)
    # Param: '.png' es la extensión, 'image_np' es el array
    # Retorna: un buffer de bytes
    _, buffer = cv2.imencode('.png', image_np)
    
    # 2. Convertir el buffer de bytes a Base64
    base64_encoded_bytes = base64.b64encode(buffer)
    
    # 3. Decodificar los bytes Base64 a una cadena (string) para JSON
    base64_string = base64_encoded_bytes.decode('utf-8')
    
    return base64_string
# ----------------------------------------------------------------------
# 1. FUNCIONES DE GESTIÓN DEL MODELO
# ----------------------------------------------------------------------

def load_ml_model():
    """Carga el modelo de Keras una sola vez."""
    global ML_MODEL
    # ... (código de carga omitido por brevedad, asumiendo que funciona) ...
    if ML_MODEL is None:
        print("Cargando modelo ML para ResNet50...")
        try:
            ML_MODEL = load_model(MODEL_PATH)
            print("Modelo ML cargado exitosamente.")
        except Exception as e:
            import sys
            print(f"ERROR: No se pudo cargar el modelo ML en {MODEL_PATH}. {e}", file=sys.stderr)
            ML_MODEL = False

def get_ml_model():
    """Retorna el modelo cargado."""
    if ML_MODEL is None:
        load_ml_model()
    return ML_MODEL

# ----------------------------------------------------------------------
# 2. FUNCIÓN PRINCIPAL DE PROCESAMIENTO Y PREDICCIÓN (SOLUCIÓN A IMÁGENES GRISES)
# ----------------------------------------------------------------------

def preprocess_and_predict(image_file):
    
    model = get_ml_model()
    if not model:
        raise Exception("El modelo ML no está disponible o no se pudo cargar.")

    # LECTURA DE IMAGEN
    image_data = image_file.read()
    np_arr = np.frombuffer(image_data, np.uint8)
    
    # IMPORTANTE: LEEMOS COMO ESCALA DE GRISES (-1) Y LUEGO CONVERTIMOS, ES MÁS SEGURO
    image_original_cv2 = cv2.imdecode(np_arr, cv2.IMREAD_UNCHANGED) 

    if image_original_cv2 is None:
        raise ValueError("No se pudo decodificar la imagen.")

    # --- CORRECCIÓN FINAL Y ROBUSTA PARA TIF/MRI (Asegurar 3 Canales) ---
    
    # 1. Redimensionar para el modelo (usando la imagen sin convertir aún)
    image_for_model = cv2.resize(image_original_cv2, IMAGE_SIZE)
    
    # 2. CONVERTIR A 3 CANALES (Si tiene 1 canal) o MANEJAR 4 CANALES
    if image_for_model.ndim == 2 or image_for_model.shape[2] == 1:
        # La imagen es 1 canal (Grayscale) -> Convertir a BGR para ResNet
        image_for_model = cv2.cvtColor(image_for_model, cv2.COLOR_GRAY2BGR)
    elif image_for_model.shape[2] == 4:
         # La imagen es 4 canales (RGBA/BGRA) -> Convertir a BGR
        image_for_model = cv2.cvtColor(image_for_model, cv2.COLOR_BGRA2BGR)


    # 3. Preprocesamiento ResNet y dimensión de batch
    image_for_model = np.expand_dims(image_for_model, axis=0) 
    processed_image = preprocess_input(image_for_model)

    # 4. Predicción
    predictions = model.predict(processed_image)
    
    probability = predictions[0][0]
    predicted_class = 1 if probability > 0.5 else 0

    # DEVOLVER LA IMAGEN ORIGINAL CONVERTIDA A 3 CANALES PARA VISUALIZACIÓN
    if image_original_cv2.ndim == 2 or image_original_cv2.shape[2] == 1:
        image_original_cv2_3ch = cv2.cvtColor(image_original_cv2, cv2.COLOR_GRAY2BGR)
    else:
        image_original_cv2_3ch = image_original_cv2
        
    return {
        'original_image_cv2': image_original_cv2_3ch, # Se asegura que esta imagen tenga 3 canales
        'tumor_present': predicted_class,
        'confidence': float(probability)
    }

# ----------------------------------------------------------------------
# 3. FUNCIÓN DE GENERACIÓN DE ANÁLISIS VISUAL
# ----------------------------------------------------------------------

def generate_analysis_image(original_image_cv2, tumor_present):
    """
    Genera una imagen visualizando el resultado, dibujando una ELIPSE ROJA 
    semi-transparente como una mancha de tumor detectado.
    """
    
    analyzed_image = original_image_cv2.copy()
    H, W, _ = analyzed_image.shape 
    center = (W // 2, H // 2)
    
    # Crea una capa transparente (máscara) para el dibujo
    overlay = analyzed_image.copy()
    alpha = 0.5  # Transparencia del 50%
    
    if tumor_present == 1:
        # --- Parámetros de la 'Mancha' (Elipse Roja) ---
        color = (0, 0, 255)  # Rojo (BGR)
        label = "POSIBLE TUMOR"
        
        # Definición de la elipse (simulando una mancha central grande)
        axes_length = (int(W * 0.35), int(H * 0.25))  # Ejes de la elipse
        angle = 160  # Ángulo de rotación (para que no sea perfectamente vertical/horizontal)
        
        # 1. Dibujar la elipse rellena en la capa de superposición (overlay)
        cv2.ellipse(
            img=overlay, 
            center=center, 
            axes=axes_length, 
            angle=angle, 
            startAngle=0, 
            endAngle=360, 
            color=color, 
            thickness=-1  # Rellena la elipse
        )
        
        # 2. Mezclar la capa de superposición con la imagen original para la transparencia
        analyzed_image = cv2.addWeighted(overlay, alpha, analyzed_image, 1 - alpha, 0)
        
        # 3. Dibujar texto (lo pongo en el color rojo final para mantener la coherencia)
        text_color = (0, 0, 255) # Rojo
    
    else:
        # Caso de NO TUMOR (solo texto o dejar sin mancha)
        label = "NO SE DETECTÓ TUMOR"
        text_color = (0, 255, 0) # Verde
        
    # Colocar el texto en la parte superior central
    text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
    text_x = center[0] - (text_size[0] // 2)
    text_y = int(H * 0.08) # Un poco más abajo del borde superior
    
    cv2.putText(
        img=analyzed_image, 
        text=label, 
        org=(text_x, text_y), 
        fontFace=cv2.FONT_HERSHEY_SIMPLEX, 
        fontScale=0.7, 
        color=text_color, 
        thickness=2
    )

    return analyzed_image