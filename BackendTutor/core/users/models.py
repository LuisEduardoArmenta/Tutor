from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    phone = models.CharField(max_length=15, blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    programming_level = models.CharField(
        max_length=20,
        choices=[
            ('NO_EXPERIENCIA', 'Sin Experiencia'),
            ('PRINCIPIANTE', 'Principiante'),
            ('INTERMEDIO', 'Intermedio'),
            ('AVANZADO', 'Avanzado')
        ],
        null=True,
        blank=True
    )
    puntos_experiencia = models.PositiveIntegerField(default=0, help_text="Experiencia acumulada en puntos")




class PreguntaEvaluacion(models.Model):
    NIVELES = [
        ('NO_EXPERIENCIA', 'Sin Experiencia'),
        ('PRINCIPIANTE', 'Principiante'),
        ('INTERMEDIO', 'Intermedio'),
        ('AVANZADO', 'Avanzado')
    ]

    nivel = models.CharField(max_length=20, choices=NIVELES)
    pregunta = models.TextField()
    opcion_a = models.CharField(max_length=200)
    opcion_b = models.CharField(max_length=200)
    opcion_c = models.CharField(max_length=200)
    opcion_d = models.CharField(max_length=200)
    respuesta_correcta = models.CharField(max_length=1)  # A, B, C, o D
    explicacion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Pregunta de nivel {self.nivel}: {self.pregunta[:50]}..."

class EvaluacionDiagnostica(models.Model):
    ESTADOS = [
        ('EN_PROGRESO', 'En Progreso'),
        ('COMPLETADA', 'Completada'),
        ('CANCELADA', 'Cancelada')
    ]

    NIVELES = [
        ('NO_EXPERIENCIA', 'Sin Experiencia'),
        ('PRINCIPIANTE', 'Principiante'),
        ('INTERMEDIO', 'Intermedio'),
        ('AVANZADO', 'Avanzado')
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='evaluaciones')
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_finalizacion = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='EN_PROGRESO')
    nivel_seleccionado = models.CharField(max_length=20, choices=NIVELES)
    nivel_asignado = models.CharField(max_length=20, choices=NIVELES, null=True, blank=True)
    preguntas = models.ManyToManyField(PreguntaEvaluacion)

    def __str__(self):
        return f"Evaluación de {self.usuario.username} - {self.get_estado_display()}"

class RespuestaEvaluacion(models.Model):
    evaluacion = models.ForeignKey(
        EvaluacionDiagnostica,
        on_delete=models.CASCADE,
        related_name='respuestas'
    )
    pregunta = models.ForeignKey(
        PreguntaEvaluacion,
        on_delete=models.CASCADE
    )
    respuesta_seleccionada = models.CharField(max_length=1)  # A, B, C, D
    tiempo_respuesta = models.FloatField()  # tiempo en segundos
    es_correcta = models.BooleanField(default=False)
    fecha_respuesta = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['fecha_respuesta']

    def save(self, *args, **kwargs):
        # Verificar si la respuesta es correcta antes de guardar
        self.es_correcta = self.respuesta_seleccionada == self.pregunta.respuesta_correcta
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Respuesta de {self.evaluacion.usuario.username} - Pregunta {self.pregunta.id}"
