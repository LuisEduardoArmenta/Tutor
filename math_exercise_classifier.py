# Primero, ejecuta estas instalaciones en Colab en este orden específico:
"""
# Limpiar instalaciones anteriores
!pip uninstall -y torch torchvision torchaudio transformers datasets
!pip cache purge

# Instalar PyTorch y sus dependencias (versión CPU)
!pip install torch==1.12.1+cpu --index-url https://download.pytorch.org/whl/cpu
!pip install torchvision==0.13.1+cpu --index-url https://download.pytorch.org/whl/cpu
!pip install torchaudio==0.12.1+cpu --index-url https://download.pytorch.org/whl/cpu

# Instalar transformers y datasets con versiones compatibles
!pip install transformers==4.26.1
!pip install datasets==2.9.0
!pip install pandas numpy scikit-learn
!pip install ipywidgets

# IMPORTANTE: Después de ejecutar estas instalaciones, reinicia el runtime de Colab
# (Runtime -> Restart runtime) y luego ejecuta el resto del código
"""

import os
import torch
from transformers import BertTokenizer, BertForSequenceClassification, Trainer, TrainingArguments
from datasets import Dataset
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import re

# Deshabilitar wandb
os.environ["WANDB_DISABLED"] = "true"

# Verificar que PyTorch está instalado correctamente
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")

# 1. Preparar datos de ejemplo con diferentes niveles de dificultad
data = {
    'text': [
        # Ejercicios fáciles (sumas simples)
        '5 + 3 = 8',
        '2 + 2 = 4',
        '1 + 1 = 2',
        
        # Ejercicios intermedios (sumas y restas)
        '10 - 5 = 5',
        '8 + 7 = 15',
        '12 - 6 = 6',
        
        # Ejercicios difíciles (múltiples operaciones)
        '5 + 3 - 2 = 6',
        '10 - 5 + 3 = 8',
        '8 + 7 - 4 = 11',
        
        # Ejercicios con error
        '5 + 3 = 9',  # Error en suma simple
        '10 - 5 = 6',  # Error en resta
        '8 + 7 - 4 = 10'  # Error en operación múltiple
    ],
    'label': [0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3]  # 0: fácil, 1: intermedio, 2: difícil, 3: error
}

# Convertir a DataFrame y luego a Dataset de Hugging Face
df = pd.DataFrame(data)
dataset = Dataset.from_pandas(df)

# 2. Tokenización
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

def tokenize_function(examples):
    return tokenizer(examples['text'], padding='max_length', truncation=True, max_length=128)

tokenized_dataset = dataset.map(tokenize_function, batched=True)

# 3. Cargar modelo preentrenado
model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=4)

# 4. Configurar entrenamiento
training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=3,
    per_device_train_batch_size=4,  # Reducido para BERT que es más pesado
    per_device_eval_batch_size=4,
    warmup_steps=50,
    weight_decay=0.01,
    logging_dir='./logs',
    logging_steps=10,
    save_strategy="no",
    evaluation_strategy="no",
    no_cuda=True,  # Forzar uso de CPU
    report_to="none",
)

# 5. Función de métricas
def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='weighted')
    acc = accuracy_score(labels, preds)
    return {
        'accuracy': acc,
        'f1': f1,
        'precision': precision,
        'recall': recall
    }

# 6. Crear trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    compute_metrics=compute_metrics,
)

# 7. Entrenar modelo
trainer.train()

# 8. Función para evaluar ejercicios y dar retroalimentación
def evaluate_exercise(exercise: str) -> dict:
    # Tokenizar y predecir
    inputs = tokenizer(exercise, return_tensors="pt", padding=True, truncation=True, max_length=128)
    outputs = model(**inputs)
    predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
    predicted_class = predictions.argmax().item()
    confidence = predictions[0][predicted_class].item()
    
    # Extraer números y operadores del ejercicio
    numbers = [int(n) for n in re.findall(r'\d+', exercise)]
    operators = re.findall(r'[+\-]', exercise)
    
    # Calcular resultado real
    result = numbers[0]
    for i, op in enumerate(operators):
        if op == '+':
            result += numbers[i + 1]
        else:
            result -= numbers[i + 1]
    
    # Extraer resultado del ejercicio
    exercise_result = int(re.findall(r'=\s*(\d+)', exercise)[0])
    
    # Determinar si el ejercicio está correcto
    is_correct = result == exercise_result
    
    # Generar retroalimentación
    feedback = {
        'ejercicio': exercise,
        'clasificación': ['Fácil', 'Intermedio', 'Difícil', 'Error'][predicted_class],
        'confianza': f"{confidence:.2%}",
        'correcto': is_correct,
        'resultado_real': result,
        'resultado_ejercicio': exercise_result,
        'puntaje': 0,
        'retroalimentación': ''
    }
    
    # Asignar puntaje y retroalimentación
    if is_correct:
        if predicted_class == 0:  # Fácil
            feedback['puntaje'] = 1
            feedback['retroalimentación'] = "¡Excelente! Has resuelto correctamente este ejercicio básico."
        elif predicted_class == 1:  # Intermedio
            feedback['puntaje'] = 2
            feedback['retroalimentación'] = "¡Muy bien! Has dominado las operaciones intermedias."
        else:  # Difícil
            feedback['puntaje'] = 3
            feedback['retroalimentación'] = "¡Impresionante! Has resuelto correctamente un ejercicio complejo."
    else:
        feedback['puntaje'] = 0
        if predicted_class == 3:  # Error
            feedback['retroalimentación'] = f"El resultado correcto es {result}. Revisa tus operaciones paso a paso."
        else:
            feedback['retroalimentación'] = f"El resultado correcto es {result}. Intenta resolverlo nuevamente."
    
    return feedback

# 9. Interfaz interactiva para probar ejercicios
def create_exercise_interface():
    import ipywidgets as widgets
    from IPython.display import display, HTML
    
    # Crear widgets
    exercise_input = widgets.Text(
        value='',
        description='Ejercicio:',
        placeholder='Ejemplo: 5 + 3 = 8'
    )
    
    evaluate_button = widgets.Button(description='Evaluar')
    output = widgets.Output()
    
    def on_evaluate_button_clicked(b):
        with output:
            output.clear_output()
            if not exercise_input.value:
                print("Por favor, ingresa un ejercicio.")
                return
                
            result = evaluate_exercise(exercise_input.value)
            
            # Mostrar resultados
            print(f"\nEjercicio: {result['ejercicio']}")
            print(f"Clasificación: {result['clasificación']} (Confianza: {result['confianza']})")
            print(f"¿Correcto?: {'Sí' if result['correcto'] else 'No'}")
            print(f"Puntaje: {result['puntaje']}/3")
            print(f"\nRetroalimentación: {result['retroalimentación']}")
    
    evaluate_button.on_click(on_evaluate_button_clicked)
    
    # Mostrar interfaz
    display(HTML("<h2>Evaluador de Ejercicios Matemáticos</h2>"))
    display(HTML("<p>Ingresa un ejercicio en el formato: número operador número = resultado</p>"))
    display(exercise_input)
    display(evaluate_button)
    display(output)

# Para usar en Colab:
# create_exercise_interface()

# Ejemplos de uso:
"""
ejercicios = [
    "5 + 3 = 8",
    "10 - 5 + 3 = 8",
    "8 + 7 - 4 = 10"
]

for ejercicio in ejercicios:
    resultado = evaluate_exercise(ejercicio)
    print(f"\nEjercicio: {resultado['ejercicio']}")
    print(f"Clasificación: {resultado['clasificación']}")
    print(f"Puntaje: {resultado['puntaje']}/3")
    print(f"Retroalimentación: {resultado['retroalimentación']}")
""" 