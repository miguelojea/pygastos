#!/bin/bash

# Moverse al directorio del proyecto (suponiendo que $WORKSPACE está disponible)
cd "$WORKSPACE"

# Crear el entorno virtual si no existe
if [ ! -d "env" ]; then
    python3 -m venv env
fi

# Activar el entorno virtual
source env/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar script de creación de la base de datos
python3 create_db.py
echo "---> DB creada."

# # Ejecutar la aplicación en segundo plano
# nohup python3 app.py > $WORKSPACE/app.log 2>&1 &
# echo "---> app.py ejecutado."

# Ejecutar sqlite_web en segundo plano
# python3 -m sqlite_web static/db.sqlite --host 0.0.0.0 --port 8002 > $WORKSPACE/sqlite_web.log 2>&1
# nohup python3 -m sqlite_web static/db.sqlite --host 0.0.0.0 --port 8002 > $WORKSPACE/sqlite_web.log 2>&1 &
# nohup python3 -m sqlite_web static/db.sqlite --host 0.0.0.0 --port 8002 > $WORKSPACE/sqlite_web.log 2>&1 & disown
nohup python3 -m sqlite_web static/db.sqlite --host 0.0.0.0 --port 8002 > $WORKSPACE/sqlite_web.log 2>&1 & disown
# echo "---> sqlite_web ejecutado."

# echo "AAAAAAAAAAAAAAA"
# echo "Iniciando sqlite_web..." >> $WORKSPACE/jenkins_debug.log
# nohup python3 -m sqlite_web static/db.sqlite --host 0.0.0.0 --port 8002 > $WORKSPACE/sqlite_web.log 2>&1 &
# disown
# echo "sqlite_web debería estar ejecutándose..." >> $WORKSPACE/jenkins_debug.log


# #!/bin/bash

# # Moverse al directorio del workspace
# cd "$WORKSPACE"

# # Crear el entorno virtual si no existe
# if [ ! -d "env" ]; then
#     python3 -m venv env
# fi

# # Activar el entorno virtual
# source env/bin/activate

# # Instalar dependencias
# pip install -r requirements.txt

# # Ejecutar script de creación de DB
# python3 create_db.py
# echo "---> DB creada."

# # Ejecutar la aplicación en segundo plano
# # nohup python3 app.py > app.log 2>&1 &

# # Ejecutar sqlite_web en segundo plano
# # python3 -m sqlite_web static/db.sqlite --host 0.0.0.0 --port 8002
# # nohup python3 -m sqlite_web static/db.sqlite --host 0.0.0.0 --port 8002 > sqlite_web.log 2>&1 &
# # nohup python3 -m sqlite_web static/db.sqlite --host 0.0.0.0 --port 8002 > sqlite_web.log 2>&1 & disown
# # setsid python3 -m sqlite_web static/db.sqlite --host 0.0.0.0 --port 8002 > sqlite_web.log 2>&1 &
# # nohup python3 -m sqlite_web static/db.sqlite --host 0.0.0.0 --port 8002 > /var/log/sqlite_web.log 2>&1 &
# nohup python3 -m sqlite_web static/db.sqlite --host 0.0.0.0 --port 8002 > $WORKSPACE/sqlite_web.log 2>&1 &

# echo "---> sqlite_web ejecutado."