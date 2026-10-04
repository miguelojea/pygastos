#!/bin/bash

echo "WORKSPACE: $WORKSPACE"

cd "$WORKSPACE"

. venv/bin/activate

# Leer el PID desde el archivo
if [ -f "$WORKSPACE/sqlite_web_pid.txt" ]; then
    PID=$(cat $WORKSPACE/sqlite_web_pid.txt)

    # Matar el proceso
    kill $PID
    echo "---> Proceso con PID $PID terminado."
else
    echo "---> No se encontró el archivo de PID."
fi

echo "Intentando iniciar sqlite_web..."
BUILD_ID=dontKillMe python3 -m sqlite_web static/db.sqlite --host 0.0.0.0 --port 8102 > $WORKSPACE/sqlite_web.log 2>&1 &

echo "Revisando logs de sqlite_web..."
cat $WORKSPACE/sqlite_web.log

# Verificar si el proceso realmente comenzó
if [ $? -eq 0 ]; then
    echo "Proceso iniciado correctamente."
    echo $! > $WORKSPACE/sqlite_web_pid.txt
else
    echo "Hubo un error al intentar iniciar el proceso."
    cat $WORKSPACE/sqlite_web.log
fi

echo "Revisando logs de sqlite_web2..."
cat $WORKSPACE/sqlite_web.log


# # Usar BUILD_ID=dontKillMe para evitar que Jenkins termine el proceso
# BUILD_ID=dontKillMe python3 -m sqlite_web static/db.sqlite --host 0.0.0.0 --port 8102 > $WORKSPACE/sqlite_web.log 2>&1 &

# # Guardar el PID en un archivo
# echo $! > $WORKSPACE/sqlite_web_pid.txt
