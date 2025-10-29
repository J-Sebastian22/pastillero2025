from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import timedelta
from django.utils import timezone

from rest_framework import viewsets
from .models import *
from .serializers import *




@api_view(['POST'])
def registrar_usuario(request):
    serializer = UsuarioSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login_usuario(request):
    correo = request.data.get('correo')
    password = request.data.get('password')

    try:
        usuario = Usuario.objects.get(correo=correo, password=password)
        serializer = UsuarioSerializer(usuario)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Usuario.DoesNotExist:
        return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)





class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

class ContactoViewSet(viewsets.ModelViewSet):
    queryset = Contacto.objects.all()
    serializer_class = ContactoSerializer

class DispositivoViewSet(viewsets.ModelViewSet):
    queryset = Dispositivo.objects.all()
    serializer_class = DispositivoSerializer

class MedicamentoViewSet(viewsets.ModelViewSet):
    queryset = Medicamento.objects.all()
    serializer_class = MedicamentoSerializer

class HorarioViewSet(viewsets.ModelViewSet):
    queryset = Horario.objects.all()
    serializer_class = HorarioSerializer

    def get_queryset(self):
        id_usuario = self.request.query_params.get('id_usuario')
        if id_usuario:
            return Horario.objects.filter(id_medicamento__id_usuario=id_usuario)
        return super().get_queryset()

class RegistroTomaViewSet(viewsets.ModelViewSet):
    queryset = Registro_Toma.objects.all()
    serializer_class = RegistroTomaSerializer

class NotificacionViewSet(viewsets.ModelViewSet):
    queryset = Notificacion.objects.all()
    serializer_class = NotificacionSerializer


@api_view(['GET'])
def proximos_horarios(request):
    id_usuario = request.query_params.get('id_usuario')
    if not id_usuario:
        return Response({'error': 'Falta id_usuario'}, status=400)

    horarios = Horario.objects.filter(id_medicamento__id_usuario=id_usuario).order_by('hora_toma')[:5]

    data = [
        {
            'medicamento': h.id_medicamento.nombre,
            'hora_toma': h.hora_toma.strftime('%H:%M'),
            'frecuencia': h.frecuencia
        }
        for h in horarios
    ]
    return Response(data)