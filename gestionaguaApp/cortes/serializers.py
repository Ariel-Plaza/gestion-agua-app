from rest_framework import serializers
from .models import Cortes


class CorteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cortes
        fields = '__all__'


class CorteReposicionSerializer(serializers.ModelSerializer):
    # Solo se permite actualizar fecha_reposicion y lectura_reposicion
    # El estado se cambia automáticamente a 'repuesto' en la vista
    class Meta:
        model = Cortes
        fields = ['fecha_reposicion', 'lectura_reposicion']