from rest_framework import APIView, status
from rest_framework.response import Response
from .models import Tarifa, Cobro
from .serializer import TarifaSerializer, TarifaUpdateSerializer

# Crear Tarifa
class AgregarTarifa(APIView):
    def post(self, request):
        serializer = TarifaSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Listar
class ListaTarifas(APIView):
    def get(self, request):
        tarifas = Tarifa.objects.filter(activo=True)
        serializer = TarifaSerializer(tarifas, many=True)
        return Response(serializer.data)

# Mostrar tarifa segun fecha
class MostrarTarifaPorAnno(APIView):
    def get(self,request,fecha):
        tarifa = Tarifa.objects.filter(vigente_desde__year=fecha)
        if tarifa.exists():
            serializer = TarifaSerializer(tarifa, many=True)
            return Response(serializer.data)    
        else:
            return Response({'error':'Tarifa no encontrada'}, status= status.HTTP_404_NOT_FOUND)

# Actualizar tarifa(monto)

class ActualizarTarifa(APIView):
    def patch(self,request,pk):
        try:
            tarifa = Tarifa.objects.get(pk=pk)
            if request.user.rol != 'admin':
                return Response({'error': 'Usuario no tiene permitido modificar'},status=status.HTTP_403_FORBIDDEN)
                
            if Cobro.objects.filter(tarifa=tarifa).exists():
                return Response({'error':'No se puede modificar, existen cobros asociados'}, status=status.HTTP_400_BAD_REQUEST)   
            
            serializer = TarifaUpdateSerializer(tarifa, data = request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': 'los datos no son validos', 'detalles': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)
        except Tarifa.DoesNotExist:
            return Response({'error':'Tarifa no encontrada'}, 
                            status=status.HTTP_404_NOT_FOUND)

# Desactivar

class EliminarTarifa(APIView):
    def delete(self,request,pk):
        try:
            tarifa =Tarifa.objects.get(pk=pk)
        except Tarifa.DoesNotExist:
            return Response({'error':'Tarifa no encontrado'}, 
                            status=status.HTTP_404_NOT_FOUND)
        tarifa.activo = False
        tarifa.save()
        return Response({'status':'Tarifa desactivado correctamente'},status=status.HTTP_200_OK)