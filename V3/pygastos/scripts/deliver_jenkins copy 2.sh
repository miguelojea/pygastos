#!/bin/bash

echo "The build ID of the job is ${BUILD_ID}."
echo "The build URL of the job is ${BUILD_URL}."
echo "ls -ltr brefore WORKSPACE:"
ls -ltr

# Moverse al directorio del proyecto (suponiendo que $WORKSPACE está disponible)
cd "$WORKSPACE"

echo "ls -ltr after WORKSPACE:"
ls -ltr

# Leer el PID desde el archivo
if [ -f "$WORKSPACE/sqlite_web_pid.txt" ]; then
    PID=$(cat $WORKSPACE/sqlite_web_pid.txt)

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
source env/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar script de creación de la base de datos
python3 create_db.py
echo "---> DB creada."

echo "---> WORKSPACE A: $WORKSPACE."

# Usar BUILD_ID=dontKillMe para evitar que Jenkins termine el proceso
# BUILD_ID=dontKillMe python3 -m sqlite_web static/db.sqlite --host 0.0.0.0 --port 8102 > $WORKSPACE/sqlite_web.log 2>&1 &
# BUILD_ID=dontKillMe nohup python3 -m sqlite_web static/db.sqlite --host 0.0.0.0 --port 8102 > $WORKSPACE/sqlite_web.log 2>&1 &
# nohup python3 -m sqlite_web static/db.sqlite --host 0.0.0.0 --port 8102 > $WORKSPACE/sqlite_web.log 2>&1 &
# nohup python3 -m sqlite_web static/db.sqlite --host 0.0.0.0 --port 8102 > $WORKSPACE/sqlite_web.log 2>&1 & disown
JENKINS_NODE_COOKIE=dontKillMe python3 -m sqlite_web static/db.sqlite --host 0.0.0.0 --port 8102 > $WORKSPACE/sqlite_web.log 2>&1 &

# sleep 10

# Obtener el PID del proceso y desasociarlo del job de Jenkins
PID=$!
disown $PID

# Guardar el PID en un archivo
echo $! > $WORKSPACE/sqlite_web_pid.txt