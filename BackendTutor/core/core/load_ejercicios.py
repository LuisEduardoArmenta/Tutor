import json
import os
import sys
import django

# Añadir la ruta del proyecto al PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configura Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from evaluador.models import Ejercicio, Modulo

def limpiar_ejercicios():
    # Borra todos los ejercicios existentes
    Ejercicio.objects.all().delete()
    print("Ejercicios anteriores eliminados correctamente.")

def load_ejercicios():
    # Primero limpiamos los ejercicios existentes
    limpiar_ejercicios()
    
    # Ruta al archivo JSON
    json_file_path = os.path.join(os.path.dirname(__file__), 'ejercicios.json')
    
    # Lee el archivo JSON
    with open(json_file_path, 'r', encoding='utf-8') as file:
        ejercicios = json.load(file)
    
    # Obtiene o crea el módulo básico
    modulo_basico, created = Modulo.objects.get_or_create(
        nombre="Módulo Básico",
        descripcion="Ejercicios básicos de C++"
    )
    
    # Itera sobre cada ejercicio y créalo en la base de datos
    for ejercicio in ejercicios:
        Ejercicio.objects.create(
            titulo=ejercicio['fields']['titulo'],
            enunciado=ejercicio['fields']['enunciado'],
            nivel=ejercicio['fields']['nivel'],
            modulo=modulo_basico,
            solucion_esperada=ejercicio['fields']['solucion_esperada'],
            puntos_xp=ejercicio['fields']['puntos_xp']
        )
    
    print("Nuevos ejercicios cargados correctamente.")

if __name__ == '__main__':
    load_ejercicios() 