# Usar la imagen oficial de Python 3.12 como base
FROM python:3.12-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia el archivo ejecutable y otros archivos necesarios
COPY app.py /app/app.py
COPY requirements.txt ./

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Especifica el comando para ejecutar tu aplicación
CMD ["./app.py"]