from django.db import models

# Create your models here.

class Modulo(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre
    
class Ejercicio(models.Model):
    NIVEL_CHOICES = [
        ('NO_EXPERIENCIA', 'No experiencia'),
        ('PRINCIPIANTE', 'Principiante'),
        ('INTERMEDIO', 'Intermedio'),
        ('AVANZADO', 'Avanzado'),
    ]

    titulo = models.CharField(max_length=100)
    enunciado = models.TextField()
    nivel = models.CharField(max_length=20, choices=NIVEL_CHOICES)
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE, related_name='ejercicios')
    solucion_esperada = models.TextField(help_text="Código correcto para comparar si es necesario")
    puntos_xp = models.PositiveIntegerField(default=10)

    def __str__(self):
        return f"{self.titulo} ({self.nivel})"

from django.contrib.auth import get_user_model

User = get_user_model()

class Evaluacion(models.Model):
    estudiante = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='evaluaciones_tutor'  # Cambiamos esto para evitar conflicto
    )
    ejercicio = models.ForeignKey(Ejercicio, on_delete=models.CASCADE, related_name='evaluaciones')
    codigo_enviado = models.TextField()
    puntaje = models.PositiveIntegerField(default=0)
    aprobado = models.BooleanField(default=False)
    retroalimentacion = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.estudiante.username} - {self.ejercicio.titulo} ({self.puntaje} pts)"



class ExperienciaEstudiante(models.Model):
    estudiante = models.OneToOneField(User, on_delete=models.CASCADE, related_name='experiencia')
    experiencia = models.PositiveIntegerField(default=0)

    def nivel_actual(self):
        if self.experiencia < 50:
            return 'No experiencia'
        elif self.experiencia < 150:
            return 'Principiante'
        elif self.experiencia < 400:
            return 'Intermedio'
        else:
            return 'Avanzado'

    def __str__(self):
        return f"{self.estudiante.username} - {self.nivel_actual()} ({self.experiencia} XP)"
