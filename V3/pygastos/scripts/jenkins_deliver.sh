#!/bin/bash

echo "The build ID of the job is ${BUILD_ID}."
echo "The build URL of the job is ${BUILD_URL}."

# Moverse al directorio del proyecto (suponiendo que $WORKSPACE está disponible)
# cd "$WORKSPACE"


# Leer el PID desde el archivo
if [ -f "sqlite_web_pid.txt" ]; then
    PID=$(cat sqlite_web_pid.txt)

    # Matar el proceso
    kill $PID
    echo "---> Proceso con PID $PID terminado."
else
    echo "---> No se encontró el archivo de PID."
fi

# Crear el entorno virtual si no existe
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activar el entorno virtual
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar script de creación de la base de datos
python3 create_db.py
echo "---> DB creada."

# Usar JENKINS_NODE_COOKIE=dontKillMe para evitar que Jenkins termine el proceso
JENKINS_NODE_COOKIE=dontKillMe python3 -m sqlite_web static/db.sqlite --host 0.0.0.0 --port 8103 > sqlite_web.log 2>&1 &

# Obtener el PID del proceso y desasociarlo del job de Jenkins
PID=$!
disown $PID

# Guardar el PID en un archivo
echo $! > sqlite_web_pid.txt