from rest_framework import serializers
from .models import programmer

# 1. Serializer para la ENTRADA (Request)
class ImageUploadSerializer(serializers.Serializer):
    """Valida la imagen y un ID de paciente opcional."""
    image = serializers.ImageField(required=True) 
    patient_id = serializers.CharField(required=False, allow_null=True, max_length=100)

# 2. Serializer para la RESPUESTA (Response)
class AnalysisResponseSerializer(serializers.Serializer):
    """Formatea la respuesta, incluyendo las imágenes Base64."""
    analysis_id = serializers.UUIDField()
    patient_id = serializers.CharField(required=False, allow_null=True)
    tumor_present = serializers.IntegerField()
    confidence = serializers.FloatField()
    tumor_description = serializers.CharField()
    message = serializers.CharField()
    
    # NUEVOS CAMPOS para las imágenes codificadas
    original_image_base64 = serializers.CharField(required=False)
    analyzed_image_base64 = serializers.CharField(required=False)

# Serializer del modelo existente
class programerSerializer(serializers.ModelSerializer):
    class Meta:
        model = programmer
        fields ='__all__'