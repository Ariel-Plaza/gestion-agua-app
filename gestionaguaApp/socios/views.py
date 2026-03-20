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
    def get(self,request):
            
        nombre = request.query_params.get('nombre')
        apellido = request.query_params.get('apellido')
        segundo_apellido = request.query_params.get('segundo_apellido', None)  # opcional
        if(nombre is None):
                return Response(
                    {'error': 'debes ingresar un nombre'},
                                status=status.HTTP_404_NOT_FOUND)

        socio = Socio.objects.filter(nombre=nombre)
        if(socio.count() > 1):
                 socio = socio.filter(apellido = apellido)
                 if(socio.count()>1):
                      socio = socio.filter(segundo_apellido = segundo_apellido)
                 
        if(socio.exists()):
                serializer = SocioSerializer(socio, many=True)
                return Response(serializer.data)
        else:
                return Response(
                    {'error': 'no existe un socio con el nombre buscado'},
                                status=status.HTTP_404_NOT_FOUND)
    

