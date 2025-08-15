# app/main.py
from fastapi import FastAPI
# Importamos los routers de ambos endpoints
from app.api.v1.endpoints import transcription, chat

# --- Inicialización de la Aplicación FastAPI ---
app = FastAPI(
    title="API de Análisis de Conversaciones Médicas",
    description="Un sistema para transcribir, analizar y consultar conversaciones entre promotores y pacientes.",
    version="1.0.0",
)

# --- Inclusión de Routers ---
# Incluimos el router de transcripción
app.include_router(transcription.router, prefix="/api/v1", tags=["1. Procesamiento de Audio"])
# Incluimos el nuevo router del chatbot
app.include_router(chat.router, prefix="/api/v1", tags=["2. Chatbot de Consultas"])


# --- Endpoint de Verificación (Health Check) ---
@app.get("/", tags=["Root"])
def read_root():
    """
    Endpoint raíz para verificar que el servicio está funcionando.
    """
    return {"status": "ok", "message": "Bienvenido a la API de Análisis de Conversaciones Médicas."}
