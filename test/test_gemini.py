# test_gemini.py
import os
import httpx
import json
from dotenv import load_dotenv

# Cargar las variables de entorno del archivo .env
print("Cargando archivo .env...")
load_dotenv()

# Obtener la API Key
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("\nERROR: No se encontró la variable GEMINI_API_KEY.")
    print("Asegúrate de que tu archivo .env existe en esta carpeta y tiene el formato correcto.")
    exit()

print("API Key encontrada. Preparando la petición...")

# --- Configuración de la Petición ---
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={API_KEY}"
HEADERS = {'Content-Type': 'application/json'}

# Un texto de ejemplo para la prueba
test_transcription = "El paciente se llama Carlos, tiene 40 años y reporta tos persistente."

# El payload que enviaremos, pidiendo una respuesta en formato JSON
PAYLOAD = {
    "contents": [{"parts": [{"text": f"Extrae el nombre y los síntomas de este texto: {test_transcription}"}]}],
    "generationConfig": {
        "response_mime_type": "application/json",
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "name": {"type": "STRING"},
                "symptoms": {"type": "ARRAY", "items": {"type": "STRING"}}
            }
        }
    }
}

# --- Ejecución de la Petición ---
print(f"Enviando petición a: {API_URL.split('?')[0]} ...")

try:
    # Usamos un cliente síncrono para este script simple
    with httpx.Client(timeout=30.0) as client:
        response = client.post(API_URL, json=PAYLOAD, headers=HEADERS)
        
        # Esta línea es clave: lanzará un error si la respuesta es 4xx o 5xx
        response.raise_for_status() 

        # Si todo fue bien (código 200)
        print("\n✅ ¡ÉXITO! La comunicación con la API de Gemini fue exitosa.")
        print("="*50)
        print("Respuesta recibida:")
        # Imprimimos la respuesta formateada para que sea fácil de leer
        print(json.dumps(response.json(), indent=2))
        print("="*50)

except httpx.HTTPStatusError as e:
    # Si la API devolvió un error (como 400, 403, 500)
    print(f"\n❌ ERROR: La API de Gemini devolvió un error HTTP {e.response.status_code}.")
    print("="*50)
    print("Detalles del error:")
    # Imprimimos el cuerpo del error, que suele tener información útil
    print(e.response.text)
    print("="*50)
    print("\nSugerencia: Un error 400 a menudo significa que la facturación no está habilitada en tu proyecto de Google Cloud.")
    
except Exception as e:
    # Para cualquier otro tipo de error (ej. problemas de red)
    print(f"\n❌ Ocurrió un error inesperado: {e}")

