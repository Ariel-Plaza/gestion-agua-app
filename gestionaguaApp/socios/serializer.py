from rest_framework import serializers
from .models import Ruta, Socio, Medidor

# Tiene la funcion de convertir los datos recibidos desde la BD a JSON(Serializacion) y convierte datos entrantes JSON los valida antes de guardar en la BD(deserialización)

class SocioSerializer(serializers.ModelSerializer):
    ruta_id = serializers.SlugRelatedField(
        # campo del modelo Ruta a mostrar
        slug_field='codigo',        
        queryset=Ruta.objects.all() # necesario para escritura
    )

    class Meta:
        model = Socio
        fields = '__all__'

class RutaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ruta
        fields = '__all__'

class MedidorSerializer(serializers.ModelSerializer):
    socio_id = serializers.PrimaryKeyRelatedField(queryset=Socio.objects.all())
    class Meta:
        model = Medidor
        fields = '__all__'