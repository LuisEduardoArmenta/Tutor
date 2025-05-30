import torch
from transformers import RobertaTokenizer, RobertaForSequenceClassification, Trainer, TrainingArguments
from datasets import Dataset
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

# 1. Preparar datos de ejemplo
data = {
    'text': [
        'Este es un ejemplo positivo de texto',
        'Este es un ejemplo negativo de texto',
        # ... más ejemplos aquí
    ],
    'label': [1, 0]  # 1 para positivo, 0 para negativo
}

# Convertir a DataFrame y luego a Dataset de Hugging Face
df = pd.DataFrame(data)
dataset = Dataset.from_pandas(df)

# 2. Tokenización
tokenizer = RobertaTokenizer.from_pretrained('roberta-base')

def tokenize_function(examples):
    return tokenizer(examples['text'], padding='max_length', truncation=True, max_length=128)

tokenized_dataset = dataset.map(tokenize_function, batched=True)

# 3. Cargar modelo preentrenado
model = RobertaForSequenceClassification.from_pretrained('roberta-base', num_labels=2)

# 4. Configurar entrenamiento
training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=3,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir='./logs',
    logging_steps=10,
)

# 5. Función de métricas
def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='binary')
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

# 8. Ejemplo de inferencia
def predict(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=128)
    outputs = model(**inputs)
    predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
    return predictions.argmax().item()

# Ejemplo de uso
texto_ejemplo = "Este es un nuevo texto para clasificar"
prediccion = predict(texto_ejemplo)
print(f"Predicción: {'Positivo' if prediccion == 1 else 'Negativo'}") 