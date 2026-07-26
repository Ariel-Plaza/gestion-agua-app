from rest_framework import serializers
from .models import Lectura
from socios.models import Medidor


class LecturaSerializer(serializers.ModelSerializer):
    # medidor = Medidor FK
    # registrado_por = Usuario FK

    medidor = serializers.PrimaryKeyRelatedField(queryset=Medidor.objects.all())
    registrado_por = serializers.PrimaryKeyRelatedField(read_only=True)
    m3_consumidos = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    lectura_anterior = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Lectura
        fields = "__all__"

    def get_lectura_anterior(self, obj):
        anterior = obj.get_lectura_anterior()
        return anterior.lectura_actual if anterior else None

    def validate(self, data):
        if data.get("origen") == "socio" and not data.get("entregado_por"):
            raise serializers.ValidationError(
                "entregado_por es obligatorio cuando el origen es socio"
            )
        return data

    def create(self, validated_data):
        validated_data["registrado_por"] = self.context["request"].user
        return Lectura.objects.create(**validated_data)


class LecturaUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lectura
        fields = ["lectura_actual"]
