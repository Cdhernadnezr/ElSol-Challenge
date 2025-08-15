# app/services/whisper_service.py
import faster_whisper
from app.core.config import settings
import logging


# Configuración del logger para este módulo
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WhisperService:
    """
    Servicio para manejar la lógica de transcripción con el modelo Whisper.
    Esta clase carga el modelo una sola vez (patrón Singleton) y proporciona
    un método para realizar la transcripción.
    """
    _instance = None
    _model = None

    # El método __new__ controla la creación de la instancia.
    def __new__(cls):
        if cls._instance is None:
            logger.info("Creando instancia de WhisperService...")
            cls._instance = super(WhisperService, cls).__new__(cls)
            try:
                logger.info(f"Cargando modelo Whisper '{settings.MODEL_SIZE}' en dispositivo '{settings.COMPUTE_DEVICE}'...")
                cls._model = faster_whisper.WhisperModel(
                    settings.MODEL_SIZE, 
                    device=settings.COMPUTE_DEVICE, 
                    compute_type="int8" # Optimización para CPU
                )
                logger.info("Modelo Whisper cargado exitosamente.")
            except Exception as e:
                logger.error(f"Error fatal al cargar el modelo Whisper: {e}")
                cls._model = None
        return cls._instance

    def transcribe_audio(self, file_path: str) -> dict:
        """
        Transcribe un archivo de audio y devuelve la transcripción y metadatos.

        Args:
            file_path (str): La ruta al archivo de audio.

        Returns:
            dict: Un diccionario con la transcripción y la información del idioma.
        """
        if not self._model:
            raise RuntimeError("El modelo de transcripción no está disponible.")
        
        try:
            logger.info(f"Iniciando transcripción para el archivo: {file_path}")
            segments, info = self._model.transcribe(file_path, beam_size=5)
            
            logger.info(f"Lenguaje detectado: {info.language} (probabilidad: {info.language_probability:.2f})")
            
            transcription = "".join(segment.text for segment in segments)
            
            return {
                "transcription": transcription.strip(),
                "language": info.language
            }
        except Exception as e:
            logger.error(f"Ocurrió un error durante la transcripción: {e}")
            raise

# Instancia única del servicio para ser importada en los endpoints.
whisper_service = WhisperService()