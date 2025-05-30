from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from .gemini_client import analizar_codigo
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView, RetrieveAPIView
from .models import Ejercicio, Evaluacion, ExperienciaEstudiante
from .serializers import EvaluacionSerializer, EjercicioSerializer, ExperienciaSerializer
from .gemini_client import analizar_codigo
from users.models import User
import re
import google.generativeai as genai
from django.conf import settings

# Configura la API key directamente desde settings
genai.configure(api_key=settings.GEMINI_API_KEY)

class EjercicioListView(ListAPIView):
    queryset = Ejercicio.objects.all()
    serializer_class = EjercicioSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Ejercicio.objects.all().select_related('modulo')

class EjercicioDetailView(RetrieveAPIView):
    queryset = Ejercicio.objects.all()
    serializer_class = EjercicioSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Ejercicio.objects.all().select_related('modulo')

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ejercicios_por_nivel(request, nivel):
    nivel = nivel.upper()
    ejercicios = Ejercicio.objects.filter(nivel=nivel).select_related('modulo')
    serializer = EjercicioSerializer(ejercicios, many=True)
    return Response(serializer.data)

class EvaluarCodigoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = request.data.get("codigo")
        ejercicio_id = request.data.get("ejercicio_id")
        
        if not code or not ejercicio_id:
            return Response(
                {"error": "Código y ejercicio_id son requeridos"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            ejercicio = Ejercicio.objects.get(id=ejercicio_id)
        except Ejercicio.DoesNotExist:
            return Response(
                {"error": "Ejercicio no encontrado"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        resultado = analizar_codigo(code)
        return Response({"resultado": resultado})

class EnviarCodigoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        ejercicio_id = request.data.get('ejercicio_id')
        codigo = request.data.get('codigo')

        if not ejercicio_id or not codigo:
            return Response({"error": "Faltan datos."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            ejercicio = Ejercicio.objects.get(id=ejercicio_id)
        except Ejercicio.DoesNotExist:
            return Response({"error": "Ejercicio no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        # ✅ Llamada a Gemini con JSON estructurado
        resultado = analizar_codigo(codigo, ejercicio)

        evaluacion = Evaluacion.objects.create(
            estudiante=user,
            ejercicio=ejercicio,
            codigo_enviado=codigo,
            puntaje=resultado.get("puntaje", 0),
            aprobado=resultado.get("aprobado", False),
            retroalimentacion=resultado.get("retroalimentacion", "Sin retroalimentación")
        )

        # ✅ Si aprueba, asignar XP
        if evaluacion.aprobado:
            xp = ejercicio.puntos_xp
            experiencia, _ = ExperienciaEstudiante.objects.get_or_create(estudiante=user)
            experiencia.experiencia += xp
            experiencia.save()

        serializer = EvaluacionSerializer(evaluacion)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ExperienciaEstudianteView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        experiencia, _ = ExperienciaEstudiante.objects.get_or_create(estudiante=request.user)
        serializer = ExperienciaSerializer(experiencia)
        return Response(serializer.data)