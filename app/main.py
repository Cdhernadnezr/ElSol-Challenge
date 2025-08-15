# app/main.py
from fastapi import FastAPI
from app.api.v1.endpoints import transcription

# --- Inicialización de la Aplicación FastAPI ---
# Se crea la instancia principal de la aplicación.
app = FastAPI(
    title="API de Análisis de Conversaciones Médicas",
    description="Un sistema para transcribir, analizar y consultar conversaciones entre promotores y pacientes.",
    version="1.0.0",
)

# --- Inclusión de Routers ---
# Se incluye el router de la API de transcripción.
# Esto permite organizar los endpoints en módulos separados.
# Si en el futuro agregas un endpoint para 'chat', simplemente crearías
# un nuevo router y lo incluirías aquí.
app.include_router(transcription.router, prefix="/api/v1", tags=["Transcription"])

# --- Endpoint de Verificación (Health Check) ---
@app.get("/", tags=["Root"])
def read_root():
    """
    Endpoint raíz para verificar que el servicio está funcionando.
    """
    return {"status": "ok", "message": "Bienvenido a la API de Análisis de Conversaciones Médicas."}
