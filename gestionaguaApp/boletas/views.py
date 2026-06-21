from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .models import Tarifa, Cobro, Pago
from socios.models import Socio
from .serializer import TarifaSerializer, TarifaUpdateSerializer, CobroSerializer, PagoSerializer


# ─── TARIFA ───────────────────────────────────────────────────────────────────

class AgregarTarifa(APIView):
    def post(self, request):
        serializer = TarifaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListaTarifas(APIView):
    def get(self, request):
        # Solo se listan tarifas activas (borrado lógico)
        tarifas = Tarifa.objects.filter(activo=True)
        serializer = TarifaSerializer(tarifas, many=True)
        return Response(serializer.data)


class MostrarTarifaPorAnno(APIView):
    def get(self, request, fecha):
        # Múltiples tarifas por año son posibles (asambleas no ocurren en fecha fija)
        # Se usa filter() + exists() en lugar de get() para evitar MultipleObjectsReturned
        tarifas = Tarifa.objects.filter(vigente_desde__year=fecha)
        if tarifas.exists():
            serializer = TarifaSerializer(tarifas, many=True)
            return Response(serializer.data)
        return Response({'error': 'Tarifa no encontrada'}, status=status.HTTP_404_NOT_FOUND)


class ActualizarTarifa(APIView):
    def patch(self, request, pk):
        try:
            tarifa = Tarifa.objects.get(pk=pk)
        except Tarifa.DoesNotExist:
            return Response({'error': 'Tarifa no encontrada'}, status=status.HTTP_404_NOT_FOUND)

        # Solo el rol 'admin' puede modificar tarifas
        if request.user.rol != 'administrador':
            return Response({'error': 'No tienes permisos para modificar tarifas'}, status=status.HTTP_403_FORBIDDEN)

        # No se puede modificar una tarifa si ya tiene cobros asociados
        # Los valores históricos en Cobro quedarían inconsistentes
        if Cobro.objects.filter(tarifa=tarifa).exists():
            return Response({'error': 'No se puede modificar: existen cobros asociados a esta tarifa'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = TarifaUpdateSerializer(tarifa, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'error': 'Datos no válidos', 'detalles': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class EliminarTarifa(APIView):
    def delete(self, request, pk):
        try:
            tarifa = Tarifa.objects.get(pk=pk)
        except Tarifa.DoesNotExist:
            return Response({'error': 'Tarifa no encontrada'}, status=status.HTTP_404_NOT_FOUND)

        # Borrado lógico: se desactiva en lugar de eliminar físicamente
        tarifa.activo = False
        tarifa.save()
        return Response({'status': 'Tarifa desactivada correctamente'}, status=status.HTTP_200_OK)


# ─── COBRO ────────────────────────────────────────────────────────────────────

class GenerarCobro(APIView):
    def post(self, request):
        # El total se calcula en la vista para no depender del cliente
        # Fórmula: cargo_fijo + costo_m3_consumido + corte_reposicion (si aplica)
        cargo_fijo = request.data.get('cargo_fijo', 0)
        costo_m3_consumido = request.data.get('costo_m3_consumido', 0)
        corte_reposicion = request.data.get('corte_reposicion', 0) or 0

        data = request.data.copy()
        data['total'] = int(cargo_fijo) + int(costo_m3_consumido) + int(corte_reposicion)

        serializer = CobroSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListaCobrosPorSocio(APIView):
    def get(self, request, rut):
        try:
            socio = Socio.objects.get(rut=rut)
        except Socio.DoesNotExist:
            return Response({'error': 'Socio no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        # Si el socio existe pero no tiene cobros, se devuelve lista vacía
        # 404 sería incorrecto: el recurso (socio) existe, solo no tiene cobros aún
        cobros = Cobro.objects.filter(socio=socio)
        serializer = CobroSerializer(cobros, many=True)
        return Response(serializer.data)


class DetalleCobro(APIView):
    def get(self, request, pk):
        try:
            cobro = Cobro.objects.get(pk=pk)
            serializer = CobroSerializer(cobro)
            return Response(serializer.data)
        except Cobro.DoesNotExist:
            return Response({'error': 'Cobro no encontrado'}, status=status.HTTP_404_NOT_FOUND)


# ─── PAGO ─────────────────────────────────────────────────────────────────────

class RegistrarPago(APIView):
    def post(self, request):
        # El pago se registra contra un Cobro específico
        # La lógica FIFO (pagar el cobro más antiguo primero) se aplica
        # en el management command de generación, no aquí
        serializer = PagoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListaPagosPorCobro(APIView):
    def get(self, request, cobro_id):
        try:
            cobro = Cobro.objects.get(pk=cobro_id)
        except Cobro.DoesNotExist:
            return Response({'error': 'Cobro no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        # Si el cobro existe pero no tiene pagos, se devuelve lista vacía
        # Un cobro recién generado válido puede no tener pagos aún
        pagos = Pago.objects.filter(cobro=cobro)
        serializer = PagoSerializer(pagos, many=True)
        return Response(serializer.data)