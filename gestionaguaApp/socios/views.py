from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Socio, Ruta, Medidor
from .serializer import SocioSerializer, RutaSerializer, MedidorSerializer

# Normalizar el rut recibido en el formato que acepta la BD ########-# (sin puntos, sin espacios, con guion)
def normalizar_rut(rut):
    return rut.replace('.', '').replace(' ', '').strip().upper()


def validar_rut(rut):
    """Valida que el RUT chileno tenga un dígito verificador correcto.
    Espera el RUT ya normalizado (formato ########-#)."""
    if '-' not in rut:
        return False
    cuerpo, dv = rut.rsplit('-', 1)
    if not cuerpo.isdigit():
        return False
    suma = 0
    multiplicador = 2
    for digito in reversed(cuerpo):
        suma += int(digito) * multiplicador
        multiplicador = multiplicador + 1 if multiplicador < 7 else 2
    resto = 11 - (suma % 11)
    if resto == 11:
        dv_esperado = '0'
    elif resto == 10:
        dv_esperado = 'K'
    else:
        dv_esperado = str(resto)
    return dv == dv_esperado

# -- Socios
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
        try:
            socios = Socio.objects.exclude(activo=False)
            serializer = SocioSerializer(socios, many=True)
            return Response(serializer.data)
        except Exception:
            return Response(
                {'error': 'No se pudo obtener el listado de socios'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ObtenerSocioNombreApellidos(APIView):
    def get(self,request):
        # busqueda por rut
        rut = request.query_params.get('rut')
        if rut:
            rut_normalizado = normalizar_rut(rut)
            if not validar_rut(rut_normalizado):
                return Response(
                    {'error': 'El RUT ingresado no es válido'},
                    status=status.HTTP_400_BAD_REQUEST)
            socio = Socio.objects.filter(
                rut = rut_normalizado, activo=True)
            if not socio.exists():
                return Response(
                    {'error': 'no existe un socio con el RUT buscado'},
                    status=status.HTTP_404_NOT_FOUND)
            serializer = SocioSerializer(socio, many=True)
            return Response(serializer.data)
        # busqueda por nombre y apellidos
        nombre = request.query_params.get('nombre')
        apellido = request.query_params.get('apellido')
        s_apellido = request.query_params.get('s_apellido', None)
        
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
            # Si socio no existe
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

#-- Rutas

class ListaRutas(APIView):
    def get(self, request):
        rutas = Ruta.objects.all()
        serializer = RutaSerializer(rutas, many=True)
        return Response(serializer.data)

class AgregarRuta(APIView):
    def post(self, request):
        serializer = RutaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ActualizarRuta(APIView):
    def put(self, request, pk):
        try:
            ruta = Ruta.objects.get(pk=pk)
        except Ruta.DoesNotExist:
            return Response({'error': 'Ruta no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        serializer = RutaSerializer(ruta, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EliminarRuta(APIView):
    def delete(self, request, pk):
        try:
            ruta = Ruta.objects.get(pk=pk)
        except Ruta.DoesNotExist:
            return Response({'error': 'Ruta no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        ruta.delete()
        return Response({'status': 'Ruta eliminada correctamente'}, status=status.HTTP_200_OK)

#--- Medidores

class ListaMedidores(APIView):
    def get(self, request):
        medidores = Medidor.objects.exclude(estado_servicio='retirado')
        
        rut = request.query_params.get('rut')
        if rut:
            rut_normalizado = normalizar_rut(rut)
            if not validar_rut(rut_normalizado):
                return Response(
                    {'error': 'El RUT ingresado no es válido'},
                    status=status.HTTP_400_BAD_REQUEST)
            try:
                socio = Socio.objects.get(rut=rut_normalizado)
            except Socio.DoesNotExist:
                return Response(
                    {'error': 'no existe un socio con el RUT buscado'},
                    status = status.HTTP_404_NOT_FOUND)
            medidores = medidores.filter(
                socio_id = socio.pk
            )
        
        serializer = MedidorSerializer(medidores, many=True)
        return Response(serializer.data)

class AgregarMedidor(APIView):
    def post(self, request):
        data = request.data.copy()
        rut = data.pop('rut', None)
        if rut:
            rut_normalizado = normalizar_rut(rut)
            if not validar_rut(rut_normalizado):
                return Response(
                    {'error': 'El RUT ingresado no es válido'},
                    status=status.HTTP_400_BAD_REQUEST)
            try:
                socio = Socio.objects.get(rut=rut_normalizado)
                data['socio_id'] = socio.pk
            except Socio.DoesNotExist:
                return Response({'error': 'No existe un socio con ese RUT'}, status=status.HTTP_404_NOT_FOUND)
        serializer = MedidorSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ObtenerMedidorPorSocio(APIView):
    def get(self, request, socio_id):
        medidores = Medidor.objects.filter(socio_id=socio_id).exclude(estado_servicio='retirado')
        if not medidores.exists():
            return Response({'error': 'No se encontraron medidores para este socio'}, status=status.HTTP_404_NOT_FOUND)
        serializer = MedidorSerializer(medidores, many=True)
        return Response(serializer.data)

class ActualizarMedidor(APIView):
    def put(self, request, pk):
        try:
            medidor = Medidor.objects.get(pk=pk)
        except Medidor.DoesNotExist:
            return Response({'error': 'Medidor no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        rut = data.pop('rut', None)
        if rut:
            rut_normalizado = normalizar_rut(rut)
            if not validar_rut(rut_normalizado):
                return Response(
                    {'error': 'El RUT ingresado no es válido'},
                    status=status.HTTP_400_BAD_REQUEST)
            try:
                socio = Socio.objects.get(rut=rut_normalizado)
                data['socio_id'] = socio.pk
            except Socio.DoesNotExist:
                return Response({'error': 'No existe un socio con ese RUT'}, status=status.HTTP_404_NOT_FOUND)

        serializer = MedidorSerializer(medidor, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EliminarMedidor(APIView):
    def delete(self, request, pk):
        try:
            medidor = Medidor.objects.get(pk=pk)
        except Medidor.DoesNotExist:
            return Response({'error': 'Medidor no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        medidor.estado_servicio = 'retirado'
        medidor.save()
        return Response({'status': 'Medidor retirado correctamente'}, status=status.HTTP_200_OK)