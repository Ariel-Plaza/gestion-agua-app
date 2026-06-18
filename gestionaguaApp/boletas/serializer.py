from rest_framework import serializers
from .models import Tarifa, Cobro, Pago


class TarifaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarifa
        fields = '__all__'
        
class TarifaUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarifa
        fields = ['precio_m3']
    
# Cobro
class CobroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cobro
        fields = '__all__'


class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = '__all__'