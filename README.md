Proyecto de Transcripción y Análisis de Conversaciones Médicas
Este repositorio contiene el MVP (Producto Mínimo Viable) para un sistema capaz de transcribir conversaciones de audio y prepararlas para un futuro análisis mediante un chatbot con IA.

✅ Instrucciones para Correr el Proyecto (con Docker)
Este proyecto está containerizado con Docker, lo que facilita su ejecución en cualquier entorno.

Prerrequisitos
Tener Docker instalado y en ejecución.

Pasos para Ejecutar
Clona el repositorio:

git clone <URL_DEL_REPOSITORIO>
cd <NOMBRE_DEL_REPOSITORIO>

Crea los archivos:
Asegúrate de tener los siguientes archivos en la raíz de tu proyecto:

main.py (con el código de la API)

Dockerfile

requirements.txt

Construye la imagen de Docker:
Este comando crea la imagen del contenedor, instalando todas las dependencias. La primera vez que se ejecute, descargará el modelo de transcripción, por lo que puede tardar unos minutos.

docker build -t transcripcion-api .

Ejecuta el contenedor:
Este comando inicia la aplicación.

docker run -p 8000:8000 --name transcripcion-container transcripcion-api

-p 8000:8000: Mapea el puerto 8000 de tu máquina al puerto 8000 del contenedor.

--name transcripcion-container: Le da un nombre al contenedor para que sea fácil de gestionar.

¡Listo! La API estará corriendo y accesible en http://localhost:8000.

✅ Descripción de los Endpoints Disponibles
1. GET /
Descripción: Endpoint de "health check" para verificar si la API está en línea.

Respuesta Exitosa (200 OK):

{
  "status": "ok",
  "message": "Bienvenido a la API de Transcripción de Audio."
}

2. POST /transcribe/
Descripción: Sube un archivo de audio (.wav, .mp3, etc.) para ser transcrito.

Cuerpo de la Petición: multipart/form-data con un campo file que contiene el archivo de audio.

Respuesta Exitosa (200 OK):

{
  "filename": "nombre_del_archivo.mp3",
  "language": "es",
  "transcription": "Hola, soy Juan Pérez y he tenido fiebre y dolor de cabeza durante los últimos tres días.",
  "processing_time_seconds": 15.78
}

Respuesta de Error (400, 500):

{
  "detail": "Mensaje de error descriptivo."
}

✅ Cómo Testear la Funcionalidad
Puedes probar el endpoint /transcribe/ de varias maneras:

1. Usando la Documentación Interactiva de FastAPI
Abre tu navegador y ve a http://localhost:8000/docs. FastAPI genera automáticamente una interfaz Swagger UI donde puedes probar el endpoint directamente desde el navegador.

2. Usando curl (Línea de Comandos)
Abre una terminal y ejecuta el siguiente comando, reemplazando ruta/a/tu/audio.mp3 con la ruta real de tu archivo de audio.

curl -X POST "http://localhost:8000/transcribe/" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@ruta/a/tu/audio.mp3"

✅ Supuestos Hechos (MVP)
Un solo hablante: El modelo de transcripción actual no diferencia entre hablantes (promotor vs. paciente). La transcripción es un texto continuo.

Procesamiento post-grabación: La transcripción se realiza sobre un archivo de audio completo, no en tiempo real.

Entorno de desarrollo: La configuración actual (--reload en el Dockerfile) es ideal para desarrollo. Para producción, se harían ajustes.

Seguridad: No se ha implementado autenticación ni autorización en los endpoints. Son públicos.

✅ Buenas Prácticas Aplicadas
Containerización con Docker: Facilita la portabilidad y el despliegue.

Carga de modelo en el arranque: El modelo de IA se carga una sola vez al iniciar la aplicación para optimizar el rendimiento y evitar latencia en la primera petición.

Manejo de archivos temporales: Los audios se guardan temporalmente y se eliminan de forma segura después del procesamiento para no ocupar espacio en disco.

Código documentado: El código incluye comentarios que explican las decisiones y el flujo.

API autodocumentada: Gracias a FastAPI, la API genera su propia documentación interactiva.

Manejo de errores: Se incluyen validaciones y manejo de excepciones para devolver errores claros al cliente.