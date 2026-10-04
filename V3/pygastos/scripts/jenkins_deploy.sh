#!/bin/bash

echo "The build ID of the job is ${BUILD_ID}."
echo "The build URL of the job is ${BUILD_URL}."

# Moverse al directorio del proyecto (suponiendo que $WORKSPACE está disponible)
# cd "$WORKSPACE"


# Leer el PID desde el archivo
if [ -f "main_flask_pid.txt" ]; then
    PID=$(cat main_flask_pid.txt)

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

# Usar JENKINS_NODE_COOKIE=dontKillMe para evitar que Jenkins termine el proceso
# JENKINS_NODE_COOKIE=dontKillMe python3 main.py --host=0.0.0.0 --port=8102 > main.log 2>&1 &
python3 main.py --host=0.0.0.0 --port=8102
sleep 10

# Obtener el PID del proceso y desasociarlo del job de Jenkins
PID=$!
disown $PID

# Guardar el PID en un archivo
echo $! > main_flask_pid.txt