# Usar la imagen oficial de Python 3.12 como base
FROM python:3.12-slim

# Establecer el directorio de trabajo en /app
WORKDIR /app

# Copiar el contenido del proyecto al contenedor
COPY . /app

# Instalar las dependencias desde el archivo requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto en el que correrá la aplicación (por ejemplo, 8080)
EXPOSE 8080

# Definir el comando para ejecutar la aplicación (usando Gunicorn para Flask)
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]