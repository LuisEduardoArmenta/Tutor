from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    PerfilEstudianteView,
    CambiarPasswordView,
    IniciarEvaluacionView,
    ResponderPreguntaView,
    FinalizarEvaluacionView,
    ObtenerEstadoEvaluacionView
)
from . import views

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('estudiante/perfil/', PerfilEstudianteView.as_view(), name='perfil_estudiante'),
    path('estudiante/cambiar-password/', CambiarPasswordView.as_view(), name='cambiar_password'),
    path('evaluacion/iniciar/', IniciarEvaluacionView.as_view(), name='iniciar_evaluacion'),
    path('evaluacion/responder/', ResponderPreguntaView.as_view(), name='responder_pregunta'),
    path('evaluacion/finalizar/', FinalizarEvaluacionView.as_view(), name='finalizar_evaluacion'),
    path('evaluacion/estado/', ObtenerEstadoEvaluacionView.as_view(), name='obtener_estado'),
    path('auth/forgot-password/', views.ForgotPasswordView.as_view(), name='forgot-password'),
    path('auth/reset-password/', views.ResetPasswordView.as_view(), name='reset-password'),
]
