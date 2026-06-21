from rest_framework import serializers
from .models import Tarifa, Cobro, Pago


class TarifaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarifa
        fields = '__all__'

        
class TarifaUpdateSerializer(serializers.ModelSerializer):
    # Solo se permite modificar precio_m3.
    # PATCH bloqueado si existen Cobros asociados a la Tarifa (validado en la vista).
    # PATCH restringido a rol 'admin' (validado en la vista).
    class Meta:
        model = Tarifa
        fields = ['precio_m3']


class CobroSerializer(serializers.ModelSerializer):
    # 'estado', 'saldo_pendiente' y 'total_pagado' son @property en el modelo.
    # No se persisten en la BD — se calculan en tiempo real desde los Pagos asociados.
    # Se usan SerializerMethodField porque DRF no expone @property automáticamente.
    # Son de solo lectura por definición: no pueden ser escritos desde el request.
    estado = serializers.SerializerMethodField()
    saldo_pendiente = serializers.SerializerMethodField()
    total_pagado = serializers.SerializerMethodField()

    class Meta:
        model = Cobro
        fields = [
            'id',
            'socio',
            'lectura',
            'tarifa',
            'periodo',
            'cargo_fijo',       # Snapshooteado desde Tarifa al momento de emisión
            'costo_m3_consumido',  # Snapshooteado desde Tarifa al momento de emisión
            'corte_reposicion', # Nullable: solo aplica si hubo corte en el período
            'interes_mora',     # Nullable: reservado para IPC, no implementado en MVP
            'total',
            'numero_boleta',    # Nullable: se asigna al generar el cobro (día 30)
            'fecha_emision',
            'fecha_vencimiento',
            'estado',           # Calculado: 'pendiente' / 'pagado' / 'vencido'
            'saldo_pendiente',  # Calculado: total - sum(pagos)
            'total_pagado',     # Calculado: sum(monto_pagado) de Pagos asociados
        ]

    def get_estado(self, obj):
        return obj.estado

    def get_saldo_pendiente(self, obj):
        return obj.saldo_pendiente

    def get_total_pagado(self, obj):
        return obj.total_pagado


class PagoSerializer(serializers.ModelSerializer):
    # Los pagos se asignan al Cobro más antiguo con saldo pendiente (lógica FIFO).
    # Un Cobro puede tener múltiples Pagos (abonos parciales).
    # El saldo_pendiente del Cobro se recalcula automáticamente al consultar.
    class Meta:
        model = Pago
        fields = '__all__'