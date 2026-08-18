from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from usuarios.permissions import EsPersonalDelComite
from .models import Cortes
from socios.models import Socio
from .serializers import CorteSerializer, CorteReposicionSerializer


class RegistrarCorte(APIView):
    permission_classes = [EsPersonalDelComite]

    def post(self, request):
        data = request.data.copy()
        data['operador_corte'] = request.user.id
        serializer = CorteSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegistrarReposicion(APIView):
    permission_classes = [EsPersonalDelComite]

    def patch(self, request, pk):
        try:
            corte = Cortes.objects.get(pk=pk)
        except Cortes.DoesNotExist:
            return Response({'error': 'Corte no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        # No se puede reponer un corte que ya fue repuesto
        if corte.estado == 'repuesto':
            return Response({'error': 'Este corte ya fue repuesto'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CorteReposicionSerializer(corte, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            # Cambio de estado a 'repuesto' en la vista, no en el serializer
            corte.estado = 'repuesto'
            corte.save()
            return Response(CorteSerializer(corte).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListaCortesPorSocio(APIView):
    def get(self, request):
        # Un socio solo ve sus propios cortes, sin importar el rut que mande
        if request.user.rol == 'socio':
            if not request.user.socio:
                return Response(
                    {'error': 'Tu usuario no está vinculado a un socio'},
                    status=status.HTTP_403_FORBIDDEN)
            socio = request.user.socio
        else:
            rut = request.query_params.get('rut')
            if not rut:
                return Response({'error': 'Debes indicar el RUT del socio'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                socio = Socio.objects.get(rut=rut)
            except Socio.DoesNotExist:
                return Response({'error': 'Socio no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        # Si el socio existe pero no tiene cortes, se devuelve lista vacía
        cortes = Cortes.objects.filter(socio=socio)
        serializer = CorteSerializer(cortes, many=True)
        return Response(serializer.data)


class DetalleCorte(APIView):
    def get(self, request, pk):
        try:
            corte = Cortes.objects.get(pk=pk)
        except Cortes.DoesNotExist:
            return Response({'error': 'Corte no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        # Un socio solo puede ver el detalle de sus propios cortes
        if request.user.rol == 'socio':
            if not request.user.socio:
                return Response(
                    {'error': 'Tu usuario no está vinculado a un socio'},
                    status=status.HTTP_403_FORBIDDEN)
            if corte.socio_id != request.user.socio_id:
                return Response(
                    {'error': 'No tienes permiso para ver este corte'},
                    status=status.HTTP_403_FORBIDDEN)

        serializer = CorteSerializer(corte)
        return Response(serializer.data)
