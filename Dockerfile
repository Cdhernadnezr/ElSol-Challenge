# Dockerfile
# Usar una imagen base de Python delgada
FROM python:3.10-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema si fueran necesarias
# Por ejemplo: RUN apt-get update && apt-get install -y ffmpeg

# Copiar el archivo de requerimientos y instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip -r requirements.txt

# Copiar toda la aplicación al directorio de trabajo
COPY ./app /app/app

# Exponer el puerto
EXPOSE 8000

# Comando para iniciar la aplicación
# Apunta al objeto 'app' dentro del archivo 'app/main.py'
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
