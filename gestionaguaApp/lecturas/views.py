from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Lectura
from .serializer import LecturaSerializer

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


class ListarLecturas(APIView):
    def get(self, request):
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

class EditarLectura(APIView):
    def patch(self,request,pk):
        try:
            actualizar =Lectura.objects.get(pk=pk)
            serializer = LecturaSerializer(actualizar, data = request.data, context={'request': request}, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': 'los datos no son validos'},
                    status=status.HTTP_400_BAD_REQUEST)
        except Lectura.DoesNotExist:
            return Response({'error':'Lectura no encontrada'}, 
                            status=status.HTTP_404_NOT_FOUND)

