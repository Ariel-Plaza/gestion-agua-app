from rest_framework import serializers
from .models import Tarifa
from .models import Cobro


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
