import os
import torch
from transformers import RobertaTokenizer, RobertaModel
from tree_sitter import Language, Parser
import numpy as np

def setup_tree_sitter():
    """Configura TreeSitter para el análisis de código C++"""
    if not os.path.exists('build/my-languages.so'):
        if not os.path.exists('tree-sitter-cpp'):
            os.system('git clone https://github.com/tree-sitter/tree-sitter-cpp')
        Language.build_library(
            'build/my-languages.so',
            ['tree-sitter-cpp']
        )
    
    CPP_LANGUAGE = Language('build/my-languages.so', 'cpp')
    parser = Parser()
    parser.set_language(CPP_LANGUAGE)
    return parser

def setup_codebert():
    """Configura el modelo CodeBERT"""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tokenizer = RobertaTokenizer.from_pretrained("microsoft/codebert-base")
    model = RobertaModel.from_pretrained("microsoft/codebert-base")
    model = model.to(device)
    return tokenizer, model, device

def analyze_ast(parser, code):
    """Analiza el AST del código usando TreeSitter"""
    try:
        tree = parser.parse(bytes(code, "utf8"))
        return tree.root_node
    except Exception as e:
        print(f"Error al analizar el AST: {e}")
        return None

def get_codebert_representation(tokenizer, model, device, code):
    """Obtiene la representación del código usando CodeBERT"""
    try:
        inputs = tokenizer(code, return_tensors="pt", padding=True, truncation=True)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = model(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1).squeeze().cpu().numpy()
        return embeddings
    except Exception as e:
        print(f"Error al obtener la representación de CodeBERT: {e}")
        return None

def evaluar_codigo(code):
    """Evalúa el código usando AST y CodeBERT"""
    try:
        # Inicializar componentes
        parser = setup_tree_sitter()
        tokenizer, model, device = setup_codebert()
        
        # Análisis
        ast = analyze_ast(parser, code)
        embedding = get_codebert_representation(tokenizer, model, device, code)

        score = 0
        feedback = []

        # Verificaciones básicas
        if "return" in code:
            score += 30
        else:
            feedback.append("⚠️ No se encontró una sentencia de retorno. ¿Olvidaste devolver el resultado?")

        if "+" in code:
            score += 40
        elif "-" in code:
            score += 10
            feedback.append("❌ Parece que estás restando en lugar de sumar.")
        else:
            feedback.append("⚠️ No se detectó ninguna operación aritmética clara.")

        # Verificación de estructura
        if ast:
            func = [n for n in ast.children if n.type == 'function_definition']
            if func:
                score += 30
            else:
                feedback.append("⚠️ No se detectó una función definida correctamente.")

        score = min(100, score)
        return score, feedback
    except Exception as e:
        print(f"Error durante la evaluación: {e}")
        return 0, ["❌ Error durante la evaluación del código"]

if __name__ == "__main__":
    # Pruebas
    codigos = {
        "✅ Bien hecho": """int suma(int a, int b) {
        return a + b;
    }""",
        "❌ Incorrecto": """int suma(int a, int b) {
        return a - b;
    }""",
        "⚠️ Intermedio": """void suma(int a, int b) {
        cout << a + b;
    }""",
    }

    for descripcion, codigo in codigos.items():
        print(f"\n--- {descripcion} ---")
        print("Código:")
        print(codigo)
        puntaje, retro = evaluar_codigo(codigo)
        print(f"🎯 Puntaje: {puntaje}/100")
        print("📝 Retroalimentación:")
        for f in retro:
            print(f" - {f}") 