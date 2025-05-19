from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import PreguntaEvaluacion, EvaluacionDiagnostica, RespuestaEvaluacion

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone', 'birth_date', 'programming_level')
        read_only_fields = ('id',)
        extra_kwargs = {
            'password': {'write_only': True}
        }

class PreguntaEvaluacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreguntaEvaluacion
        fields = ('id', 'nivel', 'pregunta', 'opcion_a', 'opcion_b', 'opcion_c', 'opcion_d')

class RespuestaEvaluacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RespuestaEvaluacion
        fields = ('id', 'evaluacion', 'pregunta', 'respuesta_seleccionada', 'tiempo_respuesta', 'es_correcta')

class EvaluacionDiagnosticaSerializer(serializers.ModelSerializer):
    preguntas = PreguntaEvaluacionSerializer(many=True, read_only=True)
    respuestas = RespuestaEvaluacionSerializer(many=True, read_only=True)

    class Meta:
        model = EvaluacionDiagnostica
        fields = ('id', 'usuario', 'fecha_inicio', 'fecha_finalizacion', 'estado', 
                 'nivel_seleccionado', 'nivel_asignado', 'preguntas', 'respuestas')
        read_only_fields = ('fecha_inicio', 'fecha_finalizacion', 'estado', 'nivel_asignado')