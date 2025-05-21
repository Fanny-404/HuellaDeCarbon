# Usa una imagen base de Python sobre Debian
# Es robusta y permite la instalación fácil de paquetes Linux.
FROM python:3.10-slim-buster

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instala las dependencias necesarias para el controlador ODBC de SQL Server
# 1. Instala curl para descargar la clave del repositorio.
# 2. Añade la clave GPG de Microsoft.
# 3. Añade el repositorio de paquetes de Microsoft para SQL Server.
# 4. Actualiza la lista de paquetes.
# 5. Instala 'unixodbc-dev' (herramientas de desarrollo ODBC) y 'msodbcsql17' (el controlador ODBC de SQL Server 17).
#    'ACCEPT_EULA=Y' acepta la licencia de Microsoft.
RUN apt-get update && \
    apt-get install -y curl && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y unixodbc-dev msodbcsql17

# Copia el archivo requirements.txt e instala las dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de tu código de aplicación al contenedor
COPY . .

# Comando para iniciar la aplicación Flask con Gunicorn
# Asegúrate de que 'app:app' sea correcto (ej. si tu aplicación Flask se llama 'app' en el archivo 'app.py')
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]