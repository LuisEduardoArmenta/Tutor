from rest_framework import serializers
from .models import Ejercicio, Evaluacion, ExperienciaEstudiante

class EjercicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ejercicio
        fields = '__all__'

class EvaluacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluacion
        fields = '__all__'
        read_only_fields = ['puntaje', 'aprobado', 'retroalimentacion', 'fecha']


class ExperienciaSerializer(serializers.ModelSerializer):
    nivel = serializers.SerializerMethodField()

    class Meta:
        model = ExperienciaEstudiante
        fields = ['experiencia', 'nivel']

    def get_nivel(self, obj):
        return obj.nivel_actual()
