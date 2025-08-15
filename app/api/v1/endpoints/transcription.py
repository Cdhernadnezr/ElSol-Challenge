# app/api/v1/endpoints/transcription.py
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from app.services.whisper_service import whisper_service
from app.core.config import settings
import os
import uuid
import time
import logging

# Configuración del logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# APIRouter permite definir endpoints en archivos separados.
router = APIRouter()

# Asegura que el directorio de subida exista.
os.makedirs(settings.UPLOAD_DIRECTORY, exist_ok=True)

@router.post("/transcribe")
async def transcribe_audio_endpoint(file: UploadFile = File(...)):
    """
    Endpoint para subir un archivo de audio y obtener su transcripción.

    - **file**: Archivo de audio en formato .wav, .mp3, etc.
    """
    # Valida el tipo de contenido del archivo.
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Formato de archivo no válido. Se esperaba un archivo de audio.")

    start_time = time.time()
    
    # Genera un nombre de archivo único para guardarlo temporalmente.
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(settings.UPLOAD_DIRECTORY, unique_filename)

    try:
        # Guarda el archivo en el disco.
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        logger.info(f"Archivo '{unique_filename}' guardado temporalmente en '{file_path}'.")

        # Llama al servicio de transcripción para procesar el audio.
        result = whisper_service.transcribe_audio(file_path)
        
        processing_time = time.time() - start_time
        logger.info(f"Procesamiento completado en {processing_time:.2f} segundos.")

        return JSONResponse(
            status_code=200,
            content={
                "filename": file.filename,
                "language": result["language"],
                "transcription": result["transcription"],
                "processing_time_seconds": round(processing_time, 2),
            }
        )

    except RuntimeError as e:
        logger.error(f"Error de ejecución: {e}")
        raise HTTPException(status_code=503, detail=str(e)) # 503 Service Unavailable
    except Exception as e:
        logger.error(f"Error inesperado al procesar el archivo: {e}")
        raise HTTPException(status_code=500, detail=f"Ocurrió un error al procesar el archivo: {str(e)}")

    finally:
        # Limpieza: se asegura de que el archivo temporal sea eliminado.
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Archivo temporal '{file_path}' eliminado.")
