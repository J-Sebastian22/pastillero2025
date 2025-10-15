from django.db import models

class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15)

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
    frecuencia = models.CharField(max_length=50)
    id_medicamento = models.ForeignKey(Medicamento, on_delete=models.CASCADE, related_name='horarios')

    def __str__(self):
        return f"{self.id_medicamento.nombre} - {self.hora_toma}"


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
