import json
import os
import sys
import django

# Añadir la ruta del proyecto al PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configura Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from users.models import PreguntaEvaluacion

def limpiar_preguntas():
    # Borra todas las preguntas existentes
    PreguntaEvaluacion.objects.all().delete()
    print("Preguntas anteriores eliminadas correctamente.")

def load_preguntas():
    # Primero limpiamos las preguntas existentes
    limpiar_preguntas()
    
    # Ruta al archivo JSON
    json_file_path = os.path.join(os.path.dirname(__file__), 'preguntas.json')
    
    # Lee el archivo JSON
    with open(json_file_path, 'r', encoding='utf-8') as file:
        preguntas = json.load(file)
    
    # Itera sobre cada pregunta y créala en la base de datos
    for pregunta in preguntas:
        PreguntaEvaluacion.objects.create(
            nivel=pregunta['fields']['nivel'],
            pregunta=pregunta['fields']['pregunta'],
            opcion_a=pregunta['fields']['opcion_a'],
            opcion_b=pregunta['fields']['opcion_b'],
            opcion_c=pregunta['fields']['opcion_c'],
            opcion_d=pregunta['fields']['opcion_d'],
            respuesta_correcta=pregunta['fields']['respuesta_correcta'],
            explicacion=pregunta['fields']['explicacion']
        )
    
    print("Nuevas preguntas cargadas correctamente.")

if __name__ == '__main__':
    load_preguntas()