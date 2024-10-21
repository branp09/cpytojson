# Usar la imagen oficial de Python 3.12 como base
FROM python:3.12-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia el archivo ejecutable y otros archivos necesarios
COPY app.exe /app/app.exe
COPY requirements.txt ./

# Asegura permisos de ejecución para el archivo ejecutable
RUN chmod +x /app/app.exe

# No necesitas instalar dependencias si ya están incluidas en el .exe
RUN pip install --no-cache-dir -r requirements.txt

# Especifica el comando para ejecutar tu aplicación .exe directamente
CMD ["python", "./app.py"]