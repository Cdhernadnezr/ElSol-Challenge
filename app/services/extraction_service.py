import httpx
import json
import logging
from app.core.config import settings

# Configuración del logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExtractionService:
    """
    Servicio para extraer información estructurada y no estructurada de un texto
    utilizando un Modelo de Lenguaje Grande (LLM).
    """
    # La URL de la API de Gemini. En un entorno real, esto estaría en config.py
    # El modelo gemini-2.5-flash-preview-05-20 es rápido y eficiente para esta tarea.
    API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={settings.GEMINI_API_KEY}"

    # Definimos el esquema JSON que esperamos que el LLM nos devuelva.
    # Esto es crucial para obtener una salida consistente y fiable.
    JSON_SCHEMA = {
        "type": "OBJECT",
        "properties": {
            "patient_name": {"type": "STRING", "description": "Nombre completo del paciente. Si no se menciona, dejar como null."},
            "patient_age": {"type": "NUMBER", "description": "Edad del paciente en años. Si no se menciona, dejar como null."},
            "consultation_date": {"type": "STRING", "description": "Fecha de la consulta mencionada en formato AAAA-MM-DD. Si no se menciona, dejar como null."},
            "symptoms": {
                "type": "ARRAY",
                "items": {"type": "STRING"},
                "description": "Lista de todos los síntomas mencionados por el paciente (ej: 'fiebre', 'dolor de cabeza', 'tos seca')."
            },
            "preliminary_diagnosis": {"type": "STRING", "description": "Diagnóstico preliminar o enfermedad mencionada. Si no se menciona, dejar como null."},
            "observations": {"type": "STRING", "description": "Resumen de cualquier otra información relevante, contexto o notas adicionales del promotor."}
        },
        "required": ["patient_name", "symptoms", "observations"]
    }

    def _build_prompt(self, transcription: str) -> str:
        """Construye el prompt para el LLM."""
        return f"""
        Analiza la siguiente transcripción de una conversación entre un promotor de salud y un paciente.
        Tu tarea es extraer la información clave y devolverla estrictamente en formato JSON.

        Transcripción:
        ---
        {transcription}
        ---

        Extrae la siguiente información:
        - Nombre del paciente.
        - Edad del paciente.
        - Fecha de la consulta.
        - Una lista de todos los síntomas descritos.
        - Cualquier diagnóstico preliminar mencionado.
        - Un resumen de observaciones o contexto adicional importante.

        Si alguna información no está presente, usa el valor null.
        """

    async def extract_data_from_text(self, transcription: str) -> dict:
        """
        Se comunica con la API de Gemini para extraer datos de la transcripción.

        Args:
            transcription (str): El texto transcrito de la conversación.

        Returns:
            dict: Los datos extraídos en formato de diccionario.
        """
        prompt = self._build_prompt(transcription)
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "response_mime_type": "application/json",
                "response_schema": self.JSON_SCHEMA
            }
        }
        
        headers = {'Content-Type': 'application/json'}

        logger.info("Enviando petición a la API de Gemini para extracción de datos...")
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(self.API_URL, json=payload, headers=headers)
                response.raise_for_status()  # Lanza una excepción para códigos de error HTTP (4xx o 5xx)

                response_data = response.json()
                
                # Extrae el contenido JSON de la respuesta de la API
                content = response_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "{}")
                
                logger.info("Datos extraídos exitosamente.")
                return json.loads(content)

            except httpx.HTTPStatusError as e:
                logger.error(f"Error en la petición a la API de Gemini: {e.response.text}")
                raise RuntimeError(f"Error al comunicarse con el servicio de IA: {e.response.status_code}")
            except (json.JSONDecodeError, IndexError, KeyError) as e:
                logger.error(f"Error al procesar la respuesta de la API de Gemini: {e}")
                raise RuntimeError("La respuesta del servicio de IA no tuvo el formato esperado.")

# Instancia única del servicio
extraction_service = ExtractionService()
