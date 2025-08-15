# Sistema de Análisis de Conversaciones Médicas con IA (ElSol-Challenge)

Este proyecto es una solución integral para grabar, transcribir y analizar conversaciones entre personal de salud y pacientes. Utiliza un pipeline de IA para procesar archivos de audio, extraer información relevante, almacenarla en una base de datos vectorial y permitir consultas en lenguaje natural a través de un chatbot.

## Arquitectura General
```
Usuario -> [Audio .mp3] -> API (FastAPI)
                                |
                                v
                        [1. Transcripción] -> WhisperService
                                |
                                v
                        [2. Extracción] -> Gemini API (JSON)
                                |
                                v
                        [3. Embedding y Almacenamiento] -> VectorDBService (Qdrant)
                                |
                                v
Usuario -> [Pregunta] -> API (FastAPI) -> ChatbotService -> [Búsqueda en Qdrant] -> [Generación con Gemini] -> [Respuesta]
```
---
## Características Implementadas
- **Ingesta de Audio:** Endpoint para subir archivos de audio (`.wav`, `.mp3`).
- **Transcripción Automática:** Utiliza `faster-whisper` para una transcripción rápida y precisa.
- **Extracción de Entidades:** Usa la API de Google Gemini (debido a que se me hizo sencillo obtener su API) en modo JSON para extraer de forma fiable información estructurada (nombre, edad) y no estructurada (síntomas, observaciones).
- **Almacenamiento Vectorial:** Convierte las conversaciones en embeddings y las almacena en una base de datos vectorial **Qdrant** para búsquedas semánticas.
- **Chatbot con RAG:** Implementa un endpoint de chat que utiliza el patrón **Retrieval-Augmented Generation (RAG)** para responder preguntas basándose únicamente en la información almacenada.

---
## Stack Tecnológico
- **Backend:** Python 3.10
- **Framework API:** FastAPI
- **Servidor:** Uvicorn
- **Orquestación:** Docker & Docker Compose
- **Transcripción:** `faster-whisper`
- **Extracción y Generación:** Google Gemini API (`gemini-2.5-flash-preview-05-20`)
- **Base de Datos Vectorial:** Qdrant
- **Generación de Embeddings:** `sentence-transformers`

---
## Instrucciones para Correr el Proyecto
#### Prerrequisitos
- [Docker](https://www.docker.com/get-started) instalado y corriendo.
- [Docker Compose](https://docs.docker.com/compose/install/) instalado.

#### Configuración
1.  **Clonar el Repositorio:**
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd <NOMBRE_DEL_REPOSITORIO>
    ```

2.  **Crear el Archivo de Entorno:**
    Crea un archivo llamado `.env` en la raíz del proyecto. Ábrelo y añade tu clave de API de Google Gemini:
    ```
    # .env
    GEMINI_API_KEY="AIzaSy...tu_clave_aqui"
    ```

3.  **Iniciar la Aplicación:**
    Usa Docker Compose para construir las imágenes e iniciar todos los servicios (API y base de datos Qdrant) con un solo comando:
    ```bash
    docker-compose up --build
    ```
    La primera vez, la construcción puede tardar varios minutos mientras se descargan los modelos de IA. Las siguientes veces será casi instantáneo. La API estará disponible en `http://localhost:8000`.

---
## Descripción de los Endpoints Disponibles
Puedes probar todos los endpoints desde la documentación interactiva en **`http://localhost:8000/docs`**.

#### `POST /api/v1/transcribe`
- **Descripción:** Procesa un archivo de audio. Lo transcribe, extrae la información y la almacena en la base de datos vectorial.
- **Cuerpo de la Petición:** `multipart/form-data` con un campo `file` que contiene el audio.
- **Respuesta Exitosa (201 Created):**
  ```json
  {
    "message": "Audio procesado y almacenado exitosamente.",
    "record_id": "a1b2c3d4-...",
    "data": { ... }
  }
  ```

#### `POST /api/v1/chat`
- **Descripción:** Envía una pregunta en lenguaje natural para consultar la información de las conversaciones almacenadas.
- **Cuerpo de la Petición:** `application/json`
  ```json
  {
    "question": "¿Qué síntomas tiene el paciente Juan Pérez?"
  }
  ```
- **Respuesta Exitosa (200 OK):**
  ```json
  {
    "question": "¿Qué síntomas tiene el paciente Juan Pérez?",
    "answer": "Juan Pérez presenta fiebre y tos.",
    "retrieved_context": [ ... ]
  }
  ```

---
## Supuestos y Buenas Prácticas
#### Supuestos:
- Las conversaciones tienen un solo hablante principal (el paciente).
- El procesamiento se realiza post-grabación (no en tiempo real).
- La seguridad (autenticación/autorización) está fuera del alcance de este MVP.

#### Buenas Prácticas:
- **Arquitectura Modular:** El código está organizado en servicios, endpoints y configuración, facilitando su mantenimiento y escalabilidad.
- **Containerización Completa:** `Docker Compose` gestiona todo el ciclo de vida de la aplicación y sus dependencias.
- **Manejo de Dependencias:** El servicio de API espera a que la base de datos esté saludable (`depends_on`) para evitar errores de conexión al inicio.
- **Gestión de Secretos:** La clave de API se gestiona de forma segura a través de variables de entorno (`.env`).
- **Código Asíncrono:** Se aprovechan las capacidades `async` de FastAPI para un manejo eficiente de las peticiones.
