from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import timedelta
from datetime import datetime
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
            'frecuencia': h.frecuencia,
            # incluir la próxima toma como ISO 8601 (timezone-aware)
            'proxima_toma': timezone.localtime(h.proxima_toma).isoformat() if getattr(h, 'proxima_toma', None) else None
        }
        for h in horarios
    ]
    return Response(data)



@api_view(['GET'])
def alarma_esp32(request):

    id_usuario = request.query_params.get('id_usuario')

    if not id_usuario:
        return Response(
            {'error': 'Falta id_usuario'},
            status=400
        )

    ahora = timezone.localtime()

    margen_minutos = 1

    horarios = Horario.objects.filter(
        id_medicamento__id_usuario=id_usuario
    )

    for horario in horarios:

        hora_programada = horario.hora_toma

        hora_actual = ahora.time()

        diferencia = abs(
            datetime.combine(datetime.today(), hora_actual) -
            datetime.combine(datetime.today(), hora_programada)
        )

        if diferencia <= timedelta(minutes=margen_minutos):

            return Response({

                'alarma': True,

                'medicamento':
                horario.id_medicamento.nombre,

                'casilla': 1,

                'horario_id': horario.id,

                'hora':
                horario.hora_toma.strftime('%H:%M')
            })

    return Response({
        
        'alarma': False,

        'medicamento':
        horario.id_medicamento.nombre,

        'dosis':
        horario.id_medicamento.dosis,

        'casilla': 1,

        'horario_id': horario.id,

        'hora':
        horario.hora_toma.strftime('%H:%M')

    })



@api_view(['POST'])
def confirmar_toma(request):

    horario_id = request.data.get('horario_id')

    if not horario_id:

        return Response({
            'error': 'Falta horario_id'
        }, status=400)

    try:

        horario = Horario.objects.get(id=horario_id)

        Registro_Toma.objects.create(
            id_horario=horario,
            fecha_hora=timezone.now(),
            estado='confirmada'
        )

        return Response({
            'mensaje': 'Toma confirmada'
        })

    except Horario.DoesNotExist:

        return Response({
            'error': 'Horario no encontrado'
        }, status=404)