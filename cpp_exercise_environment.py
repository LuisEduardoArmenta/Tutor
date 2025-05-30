import subprocess
import tempfile
import os
from IPython.display import display, HTML
import ipywidgets as widgets
from typing import List, Dict, Tuple

class CppExerciseEnvironment:
    def __init__(self):
        self.test_cases = []
        self.current_exercise = None
        self.hints = []
        
    def add_test_case(self, input_data: str, expected_output: str, points: int = 1):
        self.test_cases.append({
            'input': input_data,
            'expected': expected_output,
            'points': points
        })
    
    def add_hint(self, hint: str):
        self.hints.append(hint)
    
    def compile_and_run(self, code: str, input_data: str) -> Tuple[bool, str]:
        with tempfile.NamedTemporaryFile(suffix='.cpp', delete=False) as temp_file:
            temp_file.write(code.encode())
            temp_file_path = temp_file.name
        
        try:
            # Compilar
            compile_result = subprocess.run(
                ['g++', temp_file_path, '-o', temp_file_path + '.exe'],
                capture_output=True,
                text=True
            )
            
            if compile_result.returncode != 0:
                return False, f"Error de compilación:\n{compile_result.stderr}"
            
            # Ejecutar
            run_result = subprocess.run(
                [temp_file_path + '.exe'],
                input=input_data,
                capture_output=True,
                text=True
            )
            
            return True, run_result.stdout
            
        except Exception as e:
            return False, str(e)
        finally:
            os.unlink(temp_file_path)
            if os.path.exists(temp_file_path + '.exe'):
                os.unlink(temp_file_path + '.exe')
    
    def evaluate_solution(self, code: str) -> Dict:
        total_points = 0
        max_points = sum(test['points'] for test in self.test_cases)
        results = []
        
        for i, test in enumerate(self.test_cases):
            success, output = self.compile_and_run(code, test['input'])
            
            if not success:
                results.append({
                    'case': i + 1,
                    'status': 'Error',
                    'message': output,
                    'points': 0
                })
                continue
            
            if output.strip() == test['expected'].strip():
                total_points += test['points']
                results.append({
                    'case': i + 1,
                    'status': 'Correcto',
                    'message': '¡Caso de prueba pasado!',
                    'points': test['points']
                })
            else:
                results.append({
                    'case': i + 1,
                    'status': 'Incorrecto',
                    'message': f'Esperado: {test["expected"]}\nObtenido: {output}',
                    'points': 0
                })
        
        return {
            'total_points': total_points,
            'max_points': max_points,
            'results': results
        }

# Ejemplo de uso
def create_exercise_interface():
    env = CppExerciseEnvironment()
    
    # Configurar ejercicio de ejemplo
    env.add_test_case("5\n3", "8", 1)  # Suma de dos números
    env.add_test_case("10\n20", "30", 1)
    env.add_hint("Recuerda que puedes usar cin para leer la entrada")
    env.add_hint("La suma se puede hacer con el operador +")
    
    # Crear widgets
    code_input = widgets.Textarea(
        value='#include <iostream>\nusing namespace std;\n\nint main() {\n    // Tu código aquí\n    return 0;\n}',
        description='Código:',
        layout=widgets.Layout(width='100%', height='300px')
    )
    
    run_button = widgets.Button(description='Ejecutar')
    output = widgets.Output()
    
    def on_run_button_clicked(b):
        with output:
            output.clear_output()
            results = env.evaluate_solution(code_input.value)
            
            # Mostrar resultados
            print(f"Puntuación: {results['total_points']}/{results['max_points']}\n")
            
            for result in results['results']:
                print(f"Caso {result['case']}: {result['status']}")
                print(f"Mensaje: {result['message']}")
                print(f"Puntos: {result['points']}\n")
    
    run_button.on_click(on_run_button_clicked)
    
    # Mostrar pistas
    hints_button = widgets.Button(description='Mostrar Pistas')
    hints_output = widgets.Output()
    
    def on_hints_button_clicked(b):
        with hints_output:
            hints_output.clear_output()
            for i, hint in enumerate(env.hints, 1):
                print(f"Pista {i}: {hint}")
    
    hints_button.on_click(on_hints_button_clicked)
    
    # Mostrar interfaz
    display(HTML("<h2>Entorno de Ejercicios C++</h2>"))
    display(code_input)
    display(widgets.HBox([run_button, hints_button]))
    display(output)
    display(hints_output)

# Para usar en Colab:
# create_exercise_interface() 