from rest_framework import serializers
from .models import Tarifa

class TarifaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarifa
        fields = '__all__'
        
class TarifaUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarifa
        fields = ['precio_m3']
    
