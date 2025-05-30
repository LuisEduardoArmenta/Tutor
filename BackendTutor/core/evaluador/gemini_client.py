# evaluador/gemini_client.py
import google.generativeai as genai
from django.conf import settings
import json

genai.configure(api_key=settings.GEMINI_API_KEY)


def analizar_codigo(code, ejercicio=None):
    prompt = f"""
Eres un profesor de programación que enseña a estudiantes novatos no seas muy estricto. Analiza el siguiente código en C++ y responde solo en el siguiente formato JSON:

{{
  "puntaje": int (0 a 100),
  "aprobado": bool (true si puntaje >= 60),
  "retroalimentacion": "comentarios detallados aquí"
}}

Código del estudiante:
{code}
"""
    model = genai.GenerativeModel("models/gemini-1.5-flash")
    try:
        response = model.generate_content(prompt)
        text = response.text

        # Intentar convertir la respuesta en JSON
        json_start = text.find('{')
        json_end = text.rfind('}') + 1
        json_str = text[json_start:json_end]

        data = json.loads(json_str)
        return data  # ✅ Retorna como diccionario
    except Exception as e:
        return {
            "puntaje": 0,
            "aprobado": False,
            "retroalimentacion": f"Error al analizar el código: {str(e)}\nRespuesta:\n{text if 'text' in locals() else 'N/A'}"
        }
