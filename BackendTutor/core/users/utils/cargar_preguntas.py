from users.models import PreguntaEvaluacion

preguntas_iniciales = [
    # Nivel PRINCIPIANTE
    {
        "nivel": "PRINCIPIANTE",
        "pregunta": "¿Qué instrucción se usa para mostrar texto en C++?",
        "opcion_a": "System.out.println()",
        "opcion_b": "printf()",
        "opcion_c": "cout <<",
        "opcion_d": "echo",
        "respuesta_correcta": "C",
        "explicacion": "cout << se utiliza en C++ para imprimir información en pantalla."
    },
    {
        "nivel": "PRINCIPIANTE",
        "pregunta": "¿Cuál de los siguientes es un tipo de dato entero en C++?",
        "opcion_a": "int",
        "opcion_b": "double",
        "opcion_c": "char",
        "opcion_d": "float",
        "respuesta_correcta": "A",
        "explicacion": "int se usa para declarar variables enteras."
    },
    {
        "nivel": "PRINCIPIANTE",
        "pregunta": "¿Qué símbolo se usa para terminar una línea de código en C++?",
        "opcion_a": ".",
        "opcion_b": ":",
        "opcion_c": ";",
        "opcion_d": ",",
        "respuesta_correcta": "C",
        "explicacion": "En C++, cada instrucción termina con un punto y coma ;."
    },
    
    # Nivel INTERMEDIO
    {
        "nivel": "INTERMEDIO",
        "pregunta": "¿Qué ciclo se utiliza para repetir instrucciones un número específico de veces?",
        "opcion_a": "while",
        "opcion_b": "for",
        "opcion_c": "do",
        "opcion_d": "if",
        "respuesta_correcta": "B",
        "explicacion": "for se usa para repetir un bloque un número determinado de veces."
    },
    {
        "nivel": "INTERMEDIO",
        "pregunta": "¿Cuál es la salida del siguiente código?\nint a = 5, b = 2;\ncout << a / b;",
        "opcion_a": "2.5",
        "opcion_b": "2",
        "opcion_c": "3",
        "opcion_d": "Error",
        "respuesta_correcta": "B",
        "explicacion": "Al dividir dos enteros en C++, se realiza una división entera: 5 / 2 = 2."
    },
    {
        "nivel": "INTERMEDIO",
        "pregunta": "¿Cuál es la función principal que debe tener todo programa en C++?",
        "opcion_a": "main()",
        "opcion_b": "inicio()",
        "opcion_c": "start()",
        "opcion_d": "program()",
        "respuesta_correcta": "A",
        "explicacion": "main() es la función obligatoria de entrada en C++."
    },
    
    # Nivel AVANZADO
    {
        "nivel": "AVANZADO",
        "pregunta": "¿Qué palabra clave se usa para definir una clase en C++?",
        "opcion_a": "object",
        "opcion_b": "class",
        "opcion_c": "struct",
        "opcion_d": "define",
        "respuesta_correcta": "B",
        "explicacion": "En C++, se utiliza class para definir clases."
    },
    {
        "nivel": "AVANZADO",
        "pregunta": "¿Cuál es el operador para acceder a miembros de un puntero a objeto?",
        "opcion_a": ".",
        "opcion_b": "::",
        "opcion_c": "->",
        "opcion_d": "*",
        "respuesta_correcta": "C",
        "explicacion": "-> se usa para acceder a miembros de un objeto a través de un puntero."
    },
    {
        "nivel": "AVANZADO",
        "pregunta": "¿Qué concepto permite reutilizar código mediante herencia en C++?",
        "opcion_a": "Polimorfismo",
        "opcion_b": "Encapsulamiento",
        "opcion_c": "Herencia",
        "opcion_d": "Modularidad",
        "respuesta_correcta": "C",
        "explicacion": "La herencia permite que una clase hija reutilice los atributos y métodos de una clase padre."
    }
]

def cargar_preguntas_iniciales():
    for pregunta_data in preguntas_iniciales:
        PreguntaEvaluacion.objects.create(**pregunta_data)
    print("Preguntas cargadas exitosamente")
