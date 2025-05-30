# evaluador/urls.py
from django.urls import path
from .views import (
    EvaluarCodigoView, 
    EnviarCodigoView, 
    ejercicios_por_nivel, 
    ExperienciaEstudianteView,
    EjercicioDetailView,
    EjercicioListView
)

urlpatterns = [
    path('evaluar/', EvaluarCodigoView.as_view(), name='evaluar-codigo'),
    path('enviar-codigo/', EnviarCodigoView.as_view(), name='enviar-codigo'),
    path('ejercicios/nivel/', EjercicioListView.as_view(), name='ejercicios-list'),
    path('ejercicios/nivel/<str:nivel>/', ejercicios_por_nivel, name='ejercicios-por-nivel'),
    path('ejercicios/<int:pk>/', EjercicioDetailView.as_view(), name='ejercicio-detail'),
    path('experiencia/', ExperienciaEstudianteView.as_view(), name='experiencia-estudiante'),
]
