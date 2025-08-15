# app/api/v1/endpoints/chat.py
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.chatbot_service import chatbot_service

logger = logging.getLogger(__name__)
router = APIRouter()

# Usamos Pydantic para definir y validar el cuerpo de la petición
class ChatQuery(BaseModel):
    question: str

@router.post("/chat")
async def handle_chat_query(query: ChatQuery):
    """
    Endpoint para recibir preguntas de los usuarios y devolver respuestas generadas por el chatbot.
    """
    try:
        if not query.question:
            raise HTTPException(status_code=400, detail="La pregunta no puede estar vacía.")
        
        logger.info(f"Recibida nueva pregunta para el chat: '{query.question}'")
        
        # Llama al servicio de chatbot para obtener la respuesta
        response = await chatbot_service.answer_question(query.question)
        
        return response
        
    except Exception as e:
        logger.error(f"Error inesperado en el endpoint de chat: {e}")
        raise HTTPException(status_code=500, detail="Ocurrió un error interno al procesar la pregunta.")
