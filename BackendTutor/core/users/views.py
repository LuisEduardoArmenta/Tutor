from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model, authenticate
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import check_password
from django.db.models import Q
import random

from .models import (
    PreguntaEvaluacion,
    EvaluacionDiagnostica,
    RespuestaEvaluacion
)
from .serializers import (
    UserSerializer,
    PreguntaEvaluacionSerializer,
    RespuestaEvaluacionSerializer,
    EvaluacionDiagnosticaSerializer
)
# Obtiene el modelo User personalizado
User = get_user_model()

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(request.data['password'])
            user.save()
            
            # Generamos el token JWT
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'user': UserSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        
        if user:
            # Generamos el token JWT
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'user': UserSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }
            })
        return Response({
            'error': 'Credenciales inválidas'
        }, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if hasattr(request.user, 'auth_token'):
            request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)

class IniciarEvaluacionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            nivel_seleccionado = request.data.get('nivel_seleccionado')
            
            # Crear nueva evaluación
            evaluacion = EvaluacionDiagnostica.objects.create(
                usuario=request.user,
                nivel_seleccionado=nivel_seleccionado,
                estado='EN_PROGRESO'
            )

            # Obtener preguntas según el nivel y ordenarlas aleatoriamente
            preguntas = list(PreguntaEvaluacion.objects.filter(nivel=nivel_seleccionado))
            random.shuffle(preguntas)  # Mezclar las preguntas aleatoriamente
            evaluacion.preguntas.set(preguntas)

            return Response({
                'id': evaluacion.id,
                'preguntas': [{
                    'id': p.id,
                    'pregunta': p.pregunta,
                    'opcion_a': p.opcion_a,
                    'opcion_b': p.opcion_b,
                    'opcion_c': p.opcion_c,
                    'opcion_d': p.opcion_d,
                } for p in preguntas]
            })
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class ResponderPreguntaView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            evaluacion_id = request.data.get('evaluacion_id')
            pregunta_id = request.data.get('pregunta_id')
            respuesta = request.data.get('respuesta')
            tiempo_respuesta = request.data.get('tiempo_respuesta')

            evaluacion = EvaluacionDiagnostica.objects.get(
                id=evaluacion_id,
                usuario=request.user
            )
            pregunta = PreguntaEvaluacion.objects.get(id=pregunta_id)

            respuesta = RespuestaEvaluacion.objects.create(
                evaluacion=evaluacion,
                pregunta=pregunta,
                respuesta_seleccionada=respuesta,
                tiempo_respuesta=float(tiempo_respuesta)
            )

            return Response({
                'es_correcta': respuesta.es_correcta
            })
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class FinalizarEvaluacionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            evaluacion_id = request.data.get('evaluacion_id')
            evaluacion = EvaluacionDiagnostica.objects.get(
                id=evaluacion_id,
                usuario=request.user
            )
            
            total_preguntas = evaluacion.preguntas.count()
            respuestas_correctas = evaluacion.respuestas.filter(es_correcta=True).count()
            porcentaje_correcto = (respuestas_correctas / total_preguntas) * 100

            # Niveles ordenados de menor a mayor
            niveles = ['NO_EXPERIENCIA', 'PRINCIPIANTE', 'INTERMEDIO', 'AVANZADO']
            nivel_seleccionado = evaluacion.nivel_seleccionado
            idx = niveles.index(nivel_seleccionado)

            # Si responde todas bien, se queda en el nivel seleccionado
            if respuestas_correctas == total_preguntas:
                nivel_asignado = nivel_seleccionado
            else:
                # Si falla alguna, baja un nivel (si no está en el más bajo)
                nivel_asignado = niveles[max(0, idx - 1)]

            evaluacion.estado = 'COMPLETADA'
            evaluacion.fecha_finalizacion = timezone.now()
            evaluacion.nivel_asignado = nivel_asignado
            evaluacion.save()

            # Actualizar el nivel del usuario
            evaluacion.usuario.programming_level = nivel_asignado
            evaluacion.usuario.save()

            return Response({
                'nivel_seleccionado': evaluacion.nivel_seleccionado,
                'nivel_asignado': nivel_asignado,
                'preguntas_correctas': respuestas_correctas,
                'preguntas_totales': total_preguntas
            })
        except EvaluacionDiagnostica.DoesNotExist:
            return Response({
                'error': 'Evaluación no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class ObtenerEstadoEvaluacionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            evaluacion = EvaluacionDiagnostica.objects.filter(
                usuario=request.user
            ).latest('fecha_inicio')

            if evaluacion.estado == 'EN_PROGRESO':
                preguntas = [{
                    'id': p.id,
                    'pregunta': p.pregunta,
                    'opcion_a': p.opcion_a,
                    'opcion_b': p.opcion_b,
                    'opcion_c': p.opcion_c,
                    'opcion_d': p.opcion_d,
                } for p in evaluacion.preguntas.all()]

                return Response({
                    'estado': 'en_progreso',
                    'evaluacion': {
                        'id': evaluacion.id,
                        'preguntas': preguntas
                    }
                })
            elif evaluacion.estado == 'COMPLETADA':
                return Response({
                    'estado': 'completada',
                    'nivel_asignado': evaluacion.nivel_asignado
                })

        except EvaluacionDiagnostica.DoesNotExist:
            return Response({'estado': 'no_iniciada'})

class AdministrarPreguntasView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Añadir una o múltiples preguntas"""
        preguntas_data = request.data
        if not isinstance(preguntas_data, list):
            preguntas_data = [preguntas_data]

        preguntas_creadas = []
        for pregunta_data in preguntas_data:
            pregunta = PreguntaEvaluacion.objects.create(
                nivel=pregunta_data['nivel'],
                pregunta=pregunta_data['pregunta'],
                opcion_a=pregunta_data['opcion_a'],
                opcion_b=pregunta_data['opcion_b'],
                opcion_c=pregunta_data['opcion_c'],
                opcion_d=pregunta_data['opcion_d'],
                respuesta_correcta=pregunta_data['respuesta_correcta'],
                explicacion=pregunta_data['explicacion']
            )
            preguntas_creadas.append(pregunta)

        serializer = PreguntaEvaluacionSerializer(preguntas_creadas, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request):
        """Obtener todas las preguntas"""
        preguntas = PreguntaEvaluacion.objects.all()
        serializer = PreguntaEvaluacionSerializer(preguntas, many=True)
        return Response(serializer.data)

class PerfilEstudianteView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CambiarPasswordView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')

        if not current_password or not new_password:
            return Response(
                {'error': 'Se requieren la contraseña actual y la nueva contraseña'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not check_password(current_password, user.password):
            return Response(
                {'error': 'La contraseña actual es incorrecta'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()
        return Response({'message': 'Contraseña actualizada correctamente'})