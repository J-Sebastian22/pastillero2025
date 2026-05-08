from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta


class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.nombre


class Contacto(models.Model):
    nombre = models.CharField(max_length=100)
    correo = models.EmailField()
    telefono = models.CharField(max_length=15)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='contactos')

    def __str__(self):
        return self.nombre


class Dispositivo(models.Model):
    nombre = models.CharField(max_length=100)
    ip_esp32 = models.CharField(max_length=100)
    estado_conexion = models.BooleanField(default=False)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='dispositivos')

    def __str__(self):
        return self.nombre


class Medicamento(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    dosis = models.CharField(max_length=50)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='medicamentos')

    def __str__(self):
        return self.nombre


class Horario(models.Model):
    hora_toma = models.TimeField()
    # frecuencia: número de horas entre tomas (ej: 4, 6, 8, 12, 24)
    # default=0 para migraciones de datos existentes (ver instrucciones).
    frecuencia = models.PositiveIntegerField(default=0)
    id_medicamento = models.ForeignKey(Medicamento, on_delete=models.CASCADE, related_name='horarios')

    def __str__(self):
        return f"{self.id_medicamento.nombre} - {self.hora_toma}"

    @property
    def proxima_toma(self):
        """Devuelve el siguiente DateTime (timezone-aware) estrictamente mayor a ahora.

        Implementación corregida:
        - Usa `timezone.localtime()` para obtener la hora actual en la zona local.
        - Construye un `datetime` consciente (aware) en la zona local combinando la
          fecha local con `hora_toma`.
        - Si `frecuencia` > 0, itera sumando `timedelta(hours=frecuencia)` hasta
          encontrar el primer momento estrictamente mayor que `now`.
        - Si `frecuencia` == 0, devuelve la próxima ocurrencia diaria.
        """
        # ahora en zona local
        now_local = timezone.localtime()
        tz = timezone.get_current_timezone()

        # construir datetime para la hora de toma de hoy en la zona local
        naive_today_time = datetime.combine(now_local.date(), self.hora_toma)
        if timezone.is_naive(naive_today_time):
            initial_local = timezone.make_aware(naive_today_time, tz)
        else:
            initial_local = naive_today_time.astimezone(tz)

        # Si frecuencia > 0, sumar iterativamente hasta obtener > now_local
        if self.frecuencia and self.frecuencia > 0:
            next_dt = initial_local
            # si la hora de hoy ya pasó, avanzar
            while not (next_dt > now_local):
                next_dt = next_dt + timedelta(hours=self.frecuencia)

            # normalizar a la zona local y devolver
            return timezone.localtime(next_dt)

        # frecuencia == 0: próxima ocurrencia diaria
        if initial_local > now_local:
            return initial_local
        return initial_local + timedelta(days=1)


class Registro_Toma(models.Model):
    fecha_hora_programada = models.DateTimeField()
    fecha_hora_real = models.DateTimeField(null=True, blank=True)
    id_horario = models.ForeignKey(Horario, on_delete=models.CASCADE, related_name='registros')
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='registros')

    def __str__(self):
        return f"{self.id_usuario.nombre} - {self.fecha_hora_programada}"


class Notificacion(models.Model):
    mensaje = models.CharField(max_length=255)
    fecha_envio = models.DateTimeField(auto_now_add=True)
    id_registro = models.ForeignKey(Registro_Toma, on_delete=models.CASCADE, related_name='notificaciones')
    id_contacto = models.ForeignKey(Contacto, on_delete=models.CASCADE, related_name='notificaciones')

    def __str__(self):
        return f"Notif: {self.mensaje}"
