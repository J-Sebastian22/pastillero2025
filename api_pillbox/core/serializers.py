from rest_framework import serializers
from .models import Usuario, Contacto, Dispositivo, Medicamento, Horario, Registro_Toma, Notificacion

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'


class ContactoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contacto
        fields = '__all__'


class DispositivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dispositivo
        fields = '__all__'


class MedicamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicamento
        fields = '__all__'


class HorarioSerializer(serializers.ModelSerializer):
    medicamento_nombre = serializers.CharField(source='id_medicamento.nombre', read_only=True)
    frecuencia = serializers.IntegerField(min_value=0)
    # `proxima_toma` es una propiedad del modelo; exponerla como campo solo lectura
    proxima_toma = serializers.ReadOnlyField()

    class Meta:
        model = Horario
        fields = ['id', 'hora_toma', 'frecuencia', 'id_medicamento', 'medicamento_nombre', 'proxima_toma']


class RegistroTomaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registro_Toma
        fields = '__all__'


class NotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacion
        fields = '__all__'
