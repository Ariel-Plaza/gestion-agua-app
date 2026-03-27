from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Socio
from .serializer import SocioSerializer

# Create your views here.
class AgregarSocio(APIView):
    def post(self, request):
        # deserializar JSON
        serializer = SocioSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, 
                            status=status.HTTP_400_BAD_REQUEST)
            # return Response(exception=True,status=status.HTTP_404_NOT_FOUND,data=True)

class ListaSocios(APIView):
    def get(self, request):
        socios = Socio.objects.exclude(activo=False)
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
            socio = Socio.objects.filter(nombre=nombre,apellido=apellido, activo=True)
            # Si encuentra mas de un nombre y apellido igual
            if socio.count() > 1:
                if s_apellido is None:
                    # solicita segundo apellido
                    return Response({'error': 'existen múltiples socios, agrega el segundo apellido'})
                else:
                    socio = socio.filter(segundo_apellido = s_apellido, activo= True)
            # Si soy no existe
            if not socio.exists():
                return Response(
                    {'error': 'no existe un socio con el nombre buscado'},
                    status=status.HTTP_404_NOT_FOUND)
            
            serializer = SocioSerializer(socio, many=True)
            return Response(serializer.data)
                
class ActualizarSocio(APIView):
    def put(self,request,pk):
        try:
            actualizar =Socio.objects.get(pk=pk)
            serializer = SocioSerializer(actualizar, data = request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': 'los datos no son validos'},
                    status=status.HTTP_400_BAD_REQUEST)
        except Socio.DoesNotExist:
            return Response({'error':'Socio no encontrado'}, 
                            status=status.HTTP_404_NOT_FOUND)
            

class EliminarSocio(APIView):
    def delete(self,request,pk):
        try:
            socio =Socio.objects.get(pk=pk)
        except Socio.DoesNotExist:
            return Response({'error':'Socio no encontrado'}, 
                            status=status.HTTP_404_NOT_FOUND)
        socio.activo = False
        socio.save()
        return Response({'status':'Socio desactivado correctamente'},status=status.HTTP_200_OK)