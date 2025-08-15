# app/core/config.py
import os
from dotenv import load_dotenv

# Carga las variables de entorno desde un archivo .env
# Esto es ideal para el desarrollo local.
load_dotenv()

class Settings:
    """
    Clase para gestionar las configuraciones de la aplicación.
    Lee las variables desde el entorno (o desde el archivo .env).
    """
    # Configuración del modelo Whisper
    MODEL_SIZE: str = os.getenv("MODEL_SIZE", "base")
    COMPUTE_TYPE: str = os.getenv("COMPUTE_TYPE", "cpu")
    COMPUTE_DEVICE: str = os.getenv("COMPUTE_DEVICE", "cpu")

    # Configuración de directorios
    UPLOAD_DIRECTORY: str = "/tmp/audio_uploads"
    
    # API Key para el servicio de extracción (Gemini)
    # os.getenv buscará la variable 'GEMINI_API_KEY' en el entorno.
    # Gracias a load_dotenv(), ahora la encontrará en tu archivo .env.
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")

    # Verificación para asegurar que la API Key fue cargada
    if not GEMINI_API_KEY:
        print("ADVERTENCIA: La variable de entorno GEMINI_API_KEY no está configurada.")
        # Podrías lanzar un error si es crítico para el arranque:
        # raise ValueError("GEMINI_API_KEY no encontrada. Asegúrate de que tu archivo .env está configurado correctamente.")


settings = Settings()
