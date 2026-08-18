from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from usuarios.permissions import EsPersonalDelComite
from .models import Lectura
from .serializer import LecturaSerializer, LecturaUpdateSerializer
from socios.models import Socio, Medidor
from socios.views import normalizar_rut

# Create your views here.
class AgregarLectura(APIView):
    permission_classes = [EsPersonalDelComite]

    def post(self, request):
        # deserializar JSON
        # context pasamos el usuario autenticado si corresponde
        serializer = LecturaSerializer(data = request.data, context={'request': request})
        if serializer.is_valid():
            try:
                serializer.save()
            except ValueError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class ListaLecturas(APIView):
    def get(self, request):
        # Un socio solo ve sus propias lecturas, sin importar el rut que mande
        if request.user.rol == 'socio':
            if not request.user.socio:
                return Response(
                    {'error': 'Tu usuario no está vinculado a un socio'},
                    status=status.HTTP_403_FORBIDDEN)
            medidores = Medidor.objects.filter(socio_id=request.user.socio.pk)
            medidor_ids = [medidor.pk for medidor in medidores]
            lecturas = [
                lectura for lectura in Lectura.objects.all()
                if lectura.medidor_id in medidor_ids
            ]
            serializer = LecturaSerializer(lecturas, context={'request': request}, many=True)
            return Response(serializer.data)

        rut = request.query_params.get('rut')
        if rut:
            try:
                socio = Socio.objects.get(rut=normalizar_rut(rut))
            except Socio.DoesNotExist:
                return Response(
                    {'error': 'no existe un socio con el RUT buscado'},
                    status=status.HTTP_404_NOT_FOUND)
            medidores = Medidor.objects.filter(socio_id=socio.pk)
            medidor_ids = [medidor.pk for medidor in medidores]
            lecturas = [
                lectura for lectura in Lectura.objects.all()
                if lectura.medidor_id in medidor_ids
            ]
        else:
            lecturas = Lectura.objects.all()
        serializer = LecturaSerializer(lecturas,context={'request': request}, many=True)
        return Response(serializer.data)

# Modififcar para obtener lectura por nombre y apellido socio

# 1 obtener el nombre y apellido y segundo apellido


class ObtenerLecturaPorId(APIView):
    def get(self,request,pk):
        try:
            lectura = Lectura.objects.get(id=pk)
        except Lectura.DoesNotExist:
            return Response({'error':'Lectura no encontradda'}, status=status.HTTP_404_NOT_FOUND)

        # Un socio solo puede ver sus propias lecturas
        if request.user.rol == 'socio':
            if not request.user.socio:
                return Response(
                    {'error': 'Tu usuario no está vinculado a un socio'},
                    status=status.HTTP_403_FORBIDDEN)
            if lectura.medidor.socio_id != request.user.socio_id:
                return Response(
                    {'error': 'No tienes permiso para ver esta lectura'},
                    status=status.HTTP_403_FORBIDDEN)

        serializer = LecturaSerializer(lectura)
        return Response(serializer.data)

class ActualizarLectura(APIView):
    permission_classes = [EsPersonalDelComite]

    def patch(self,request,pk):
        try:
            lectura =Lectura.objects.get(pk=pk)
            serializer = LecturaUpdateSerializer(lectura, data = request.data, partial=True)

            if serializer.is_valid():
                try:
                    serializer.save()
                except ValueError as e:
                    return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': 'los datos no son validos', 'detalles': serializer.errors},
    status=status.HTTP_400_BAD_REQUEST)
        except Lectura.DoesNotExist:
            return Response({'error':'Lectura no encontrada'},
                            status=status.HTTP_404_NOT_FOUND)
