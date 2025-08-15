# app/api/v1/endpoints/transcription.py
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from app.services.whisper_service import whisper_service
from app.services.extraction_service import extraction_service # <-- Importamos el nuevo servicio
from app.core.config import settings
import os
import uuid
import time
import logging

# Configuración del logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

os.makedirs(settings.UPLOAD_DIRECTORY, exist_ok=True)

# Nota: El endpoint se llama 'transcribe' pero ahora hace más que eso.
# En una futura versión (v2), podría renombrarse a '/process_audio' para mayor claridad.
@router.post("/transcribe")
async def transcribe_and_extract_endpoint(file: UploadFile = File(...)):
    """
    Endpoint para subir un archivo de audio, transcribirlo y extraer
    información estructurada y no estructurada.
    """
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Formato de archivo no válido. Se esperaba un archivo de audio.")

    start_time = time.time()
    
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(settings.UPLOAD_DIRECTORY, unique_filename)

    try:
        # --- Paso 1: Guardar el archivo ---
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        logger.info(f"Archivo '{unique_filename}' guardado temporalmente.")

        # --- Paso 2: Transcribir el audio ---
        transcription_result = whisper_service.transcribe_audio(file_path)
        transcription_text = transcription_result["transcription"]
        
        if not transcription_text or not transcription_text.strip():
             # Si la transcripción está vacía o solo contiene espacios en blanco, detenemos el proceso.
            logger.warning(f"La transcripción para el archivo {file.filename} resultó vacía.")
            # Devolvemos una respuesta parcial exitosa sin intentar la extracción.
            return JSONResponse(
                status_code=200,
                content={
                    "processing_metadata": {
                        "filename": file.filename,
                        "language": transcription_result.get("language", "unknown"),
                        "processing_time_seconds": round(time.time() - start_time, 2),
                        "status": "Transcription complete, extraction skipped due to empty text."
                    },
                    "transcription": "",
                    "extracted_information": {}
                }
            )

        # --- Paso 3: Extraer información del texto ---
        logger.info("Iniciando la extracción de información de la transcripción.")
        extracted_data = await extraction_service.extract_data_from_text(transcription_text)

        processing_time = time.time() - start_time
        logger.info(f"Procesamiento completo en {processing_time:.2f} segundos.")

        # --- Paso 4: Devolver la respuesta combinada ---
        return JSONResponse(
            status_code=200,
            content={
                "processing_metadata": {
                    "filename": file.filename,
                    "language": transcription_result["language"],
                    "processing_time_seconds": round(processing_time, 2),
                },
                "transcription": transcription_text,
                "extracted_information": extracted_data
            }
        )

    except RuntimeError as e:
        logger.error(f"Error de ejecución en un servicio: {e}")
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Error inesperado al procesar el archivo: {e}")
        raise HTTPException(status_code=500, detail=f"Ocurrió un error al procesar el archivo: {str(e)}")

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Archivo temporal '{file_path}' eliminado.")
