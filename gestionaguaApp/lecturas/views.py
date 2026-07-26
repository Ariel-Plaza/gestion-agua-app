from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Lectura
from .serializer import LecturaSerializer, LecturaUpdateSerializer
from socios.models import Socio, Medidor
from socios.views import normalizar_rut

# Create your views here.
class AgregarLectura(APIView):
    def post(self, request):
        # deserializar JSON
        # context pasamos el usuario autenticado si corresponde
        serializer = LecturaSerializer(data = request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, 
                            status=status.HTTP_400_BAD_REQUEST)


class ListaLecturas(APIView):
    def get(self, request):
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
            serializer = LecturaSerializer(lectura)
            return Response(serializer.data)
        except Lectura.DoesNotExist:
            return Response({'error':'Lectura no encontradda'}, status=status.HTTP_404_NOT_FOUND)

class ActualizarLectura(APIView):
    def patch(self,request,pk):
        try:
            lectura =Lectura.objects.get(pk=pk)
            serializer = LecturaUpdateSerializer(lectura, data = request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': 'los datos no son validos', 'detalles': serializer.errors},
    status=status.HTTP_400_BAD_REQUEST)
        except Lectura.DoesNotExist:
            return Response({'error':'Lectura no encontrada'}, 
                            status=status.HTTP_404_NOT_FOUND)
