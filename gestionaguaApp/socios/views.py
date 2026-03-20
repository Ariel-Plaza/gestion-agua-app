from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Socio
from .serializer import SocioSerializer

# Create your views here.

class ListaSocios(APIView):
    def get(self, request):
        socios = Socio.objects.all()
        serializer = SocioSerializer(socios, many=True)
        return Response(serializer.data)
    
class ObtenerSocioNombreApellidos(APIView):
    def get(self,request,nombre,apellido,segundo_apellido):
        try:
            socio = Socio.objects.get(nombre = nombre)
            serializer = SocioSerializer(socio)
        except Socio.DoesNotExist:
            return Response(
                {'error': 'Socio no encontrado'},
                status=status.HTTP_404_NOT_FOUND    # retorna 404 si no existe
            )
        return Response(serializer.data)

