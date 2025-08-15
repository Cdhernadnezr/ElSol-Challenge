# app/api/v1/endpoints/transcription.py
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from app.services.whisper_service import whisper_service
from app.services.extraction_service import extraction_service
from app.services.vector_db_service import vector_db_service 
from app.core.config import settings
import os
import uuid
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
os.makedirs(settings.UPLOAD_DIRECTORY, exist_ok=True)

@router.post("/transcribe")
async def process_audio_and_store_endpoint(file: UploadFile = File(...)):
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Formato de archivo no válido.")

    start_time = time.time()
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(settings.UPLOAD_DIRECTORY, unique_filename)

    try:
        # Paso 1: Guardar archivo
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        
        # Paso 2: Transcribir
        transcription_result = whisper_service.transcribe_audio(file_path)
        transcription_text = transcription_result["transcription"]
        
        if not transcription_text or not transcription_text.strip():
            logger.warning(f"Transcripción vacía para {file.filename}.")
            return JSONResponse(status_code=200, content={"status": "Transcripción vacía, no se procesó."})

        # Paso 3: Extraer datos
        extracted_data = await extraction_service.extract_data_from_text(transcription_text)

        processing_metadata = {
            "filename": file.filename,
            "language": transcription_result["language"],
            "processing_time_seconds": round(time.time() - start_time, 2),
        }

        # --- Paso 4 (Nuevo): Almacenar en la base de datos vectorial ---
        record_id = vector_db_service.store_record(
            transcription=transcription_text,
            extracted_data=extracted_data,
            metadata=processing_metadata
        )

        logger.info(f"Proceso completo. Registro guardado con ID: {record_id}")

        return JSONResponse(
            status_code=201, # 201 Created es más apropiado ya que creamos un recurso
            content={
                "message": "Audio procesado y almacenado exitosamente.",
                "record_id": record_id,
                "data": {
                    "processing_metadata": processing_metadata,
                    "transcription": transcription_text,
                    "extracted_information": extracted_data
                }
            }
        )
    except RuntimeError as e:
        logger.error(f"Error de ejecución en un servicio: {e}")
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        raise HTTPException(status_code=500, detail=f"Ocurrió un error: {str(e)}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
