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
        s_apellido = request.query_params.get('s_apellido', None) # opcional
        
        if(nombre is None or apellido is None):
                return Response(
                    {'error': 'debes ingresar un nombre y un apellido'},
                                status=status.HTTP_404_NOT_FOUND)
        else:
            # Filtra por nombre y apellido
            socio = Socio.objects.filter(nombre=nombre,apellido=apellido)
            # Si encuentra mas de un nombre y apellido igual
            if socio.count() > 1:
                if s_apellido is None:
                    # solicita segundo apellido
                    return Response({'error': 'existen múltiples socios, agrega el segundo apellido'})
                else:
                    socio = socio.filter(segundo_apellido = s_apellido)
            # verifica que socio existe
            if socio.exists():
                serializer = SocioSerializer(socio, many=True)
                return Response(serializer.data)
            else:
                return Response(
                    {'error': 'no existe un socio con el nombre buscado'},
                    status=status.HTTP_404_NOT_FOUND)