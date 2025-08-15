# app/core/config.py
import os

class Settings:
    """
    Clase para gestionar las configuraciones de la aplicación.
    Centralizar la configuración aquí facilita la gestión de diferentes entornos
    (desarrollo, pruebas, producción) usando variables de entorno.
    """
    # Configuración del modelo Whisper
    MODEL_SIZE: str = os.getenv("MODEL_SIZE", "base")
    COMPUTE_TYPE: str = os.getenv("COMPUTE_TYPE", "cpu") # "cuda" para GPU, "cpu" para CPU
    COMPUTE_DEVICE: str = os.getenv("COMPUTE_DEVICE", "cpu") # "cuda" o "cpu"

    # Configuración de directorios
    UPLOAD_DIRECTORY: str = "/tmp/audio_uploads"

# Se crea una instancia única de la configuración para ser importada en otros módulos.
settings = Settings()
