from rest_framework import serializers
from .models import Lectura
from socios.models import Medidor

class LecturaSerializer(serializers.ModelSerializer):
    # medidor = Medidor FK
    # registrado_por = Usuario FK
    
    medidor = serializers.PrimaryKeyRelatedField(queryset = Medidor.objects.all())
    registrado_por = serializers.PrimaryKeyRelatedField(read_only=True)
    m3_consumidos = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Lectura
        fields = '__all__'
        
    def validate(self, data):
        if data.get('origen') == 'socio' and not data.get('entregado_por'):
            raise serializers.ValidationError("entregado_por es obligatorio cuando el origen es socio")
        return data    
        
    def create(self, validated_data):
        medidor = validated_data.get('medidor')
        lectura_anterior = Lectura.objects.filter(medidor=medidor).order_by('-periodo').first()

        if lectura_anterior is None:
            m3_consumidos = 0
        else:
            m3_consumidos = validated_data['lectura_actual'] - lectura_anterior.lectura_actual

        validated_data['m3_consumidos'] = m3_consumidos
        validated_data['registrado_por'] = self.context['request'].user
        return Lectura.objects.create(**validated_data)
    
class LecturaUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lectura
        fields = ['lectura_actual']
    
    def validate_lectura_actual(self, value):
        # 'self.instance' existe porque es un update (partial o no)
        if self.instance and value < self.instance.lectura_actual:
            raise serializers.ValidationError(
                f"La nueva lectura ({value}) no puede ser menor que la actual ({self.instance.lectura_actual})"
            )
        return value