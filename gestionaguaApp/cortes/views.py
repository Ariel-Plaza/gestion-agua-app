from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .models import Cortes
from socios.models import Socio
from .serializers import CorteSerializer, CorteReposicionSerializer


class RegistrarCorte(APIView):
    def post(self, request):
        data = request.data.copy()
        data['operador_corte'] = request.user.id
        serializer = CorteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegistrarReposicion(APIView):
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
    def get(self, request, rut):
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
            serializer = CorteSerializer(corte)
            return Response(serializer.data)
        except Cortes.DoesNotExist:
            return Response({'error': 'Corte no encontrado'}, status=status.HTTP_404_NOT_FOUND)