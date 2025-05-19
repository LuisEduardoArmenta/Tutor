from users.models import PreguntaEvaluacion

preguntas_adicionales = [
    # Nivel PRINCIPIANTE (muy básica)
    {
        "nivel": "PRINCIPIANTE",
        "pregunta": "¿Cómo se comenta una sola línea en C++?",
        "opcion_a": "// Esto es un comentario",
        "opcion_b": "/* Esto es un comentario */",
        "opcion_c": "# Esto es un comentario",
        "opcion_d": "<!-- Esto es un comentario -->",
        "respuesta_correcta": "A",
        "explicacion": "En C++, las líneas que comienzan con // son comentarios de una sola línea."
    },

    # Nivel INTERMEDIO (práctica con variables)
    {
        "nivel": "INTERMEDIO",
        "pregunta": "¿Cuál es el resultado de este código?\nint x = 3;\nx = x + 2;\ncout << x;",
        "opcion_a": "3",
        "opcion_b": "2",
        "opcion_c": "5",
        "opcion_d": "Error",
        "respuesta_correcta": "C",
        "explicacion": "x comienza con 3, luego se le suma 2. El resultado es 5, que se imprime en pantalla."
    },

    # Nivel AVANZADO (conceptual pero sencilla)
    {
        "nivel": "AVANZADO",
        "pregunta": "¿Cuál es la principal ventaja de usar clases en C++?",
        "opcion_a": "Permiten usar comentarios",
        "opcion_b": "Permiten repetir instrucciones",
        "opcion_c": "Permiten agrupar datos y funciones relacionadas",
        "opcion_d": "Hacen que el programa sea más rápido",
        "respuesta_correcta": "C",
        "explicacion": "Las clases agrupan datos (atributos) y funciones (métodos) en una estructura organizada."
    },
    {
        "nivel": "AVANZADO",
        "pregunta": "¿Para qué sirve un constructor en una clase en C++?",
        "opcion_a": "Para imprimir mensajes",
        "opcion_b": "Para eliminar objetos",
        "opcion_c": "Para inicializar objetos cuando se crean",
        "opcion_d": "Para copiar archivos",
        "respuesta_correcta": "C",
        "explicacion": "Un constructor se ejecuta automáticamente al crear un objeto y sirve para inicializar sus valores."
    }
]

def cargar_preguntas_adicionales():
    for pregunta_data in preguntas_adicionales:
        # Verificar si la pregunta ya existe para evitar duplicados
        if not PreguntaEvaluacion.objects.filter(
            pregunta=pregunta_data['pregunta'],
            nivel=pregunta_data['nivel']
        ).exists():
            PreguntaEvaluacion.objects.create(**pregunta_data)
            print(f"Pregunta cargada: {pregunta_data['pregunta'][:50]}...")
        else:
            print(f"Pregunta ya existe: {pregunta_data['pregunta'][:50]}...")
    
    print("Proceso de carga de preguntas adicionales completado") 