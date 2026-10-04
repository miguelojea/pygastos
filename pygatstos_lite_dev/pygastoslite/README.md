# pyGastosLite

## Info

Web to manage incomes and expenses to Google Sheets with Python + Flask.

## Features

TODO: add features implemented through the development cycle. E.g. Add entry (expense/income) to DB.

## Objetivos:

* Guardar entradas en un BD.
* Añadir entradas manualmente a través de web Flask.
* Añadir entradas automatizadamente subiendo excel / txt / PDF a web Flask. Cuidado de no volver a añadir entradas ya añadidas manualmente.
* Añadir gastos manualmente a través de Google Sheets.
* Sincronización BD - Google Sheets:

  * Cuando se añada una entrada a la BD, tiene un campo sync con valor False por defecto.
  * Al final de cada día (o cuando se desee), se añaden esas nuevas entradas a Google Sheets y se pone el campo sync a True.
  * Al final de cada día (o cuando se desee), también se sincroniza la BD con Google Sheets, comparando cada entrada (teniendo en cuenta todos los campos, ya que se puede modificar solo 1 (ej. descripción). Manda Google Sheets:

    * Si hay una entrada en Google Sheets que no está en DB: se añade a la BD (marcada como sync = True). Es el caso en el que se añaden entradas manuales a Google Sheets.
    * Si hay una entrada en la DB con sync = True que no está en Google Sheets: se elimina de la BD. Es el caso en el que se eliminan entradas manualmente en Google Sheets.

Beneficio de usar BD: Más rápido que conecar con Google Sheets para cada cambio.

## Getting started

Execute locally:

- Create and activate venv, install  requirements.
- `python main.py` (in root directory)

Execute in production (gunicorn):

- Make sure to have the DB created and migrated beforehand (in the environment where you launch it).
- Asegúrate de tener la base de datos creada y migrada antes (en el entorno donde lo lances).
- `pip install gunicorn`
- `gunicorn -w 4 -b 0.0.0.0:8101 'app:create_app()'`
  - This launches 4 workers in port 8101.

Testing:

* `pip install gunicorn`
* `pytest `(in root directory)

## TODOs:

Bugfix:

- Fecha en formato de mierda en HTML MM/DD/YYYY
- Lío para automatizar CSV. Actualizar para hacer solo cosas fáciles: supermercados. Y poner en el concepto solo lo básico, no concepto completo con nºs y mrdas.
- Para reducir tiempo de sync, acualizar Google Sheets por rangos y no celdas individuales. Ver en detalle límite de requests por minuto de la API.

Para V1:

* [ ] CSV upload seq. Ignorar valores positivos en tarjeta (amortización deuda y devol. gasolina). Añadir en descripción lo que ponga en el CONCEPTO del csv.
* [ ] En sync, ordenar entradas de Google Sheets por fecha. Si es posible. Cuidado con entrada especial, debe ser siempre la primera y no se modificada.
* [ ] Unificar Google Sheets 2024-2025 (conceptos, columna fecha...) y añadir entradas antiguas (meses anteriores y 2024) a DB para tenerlo todo.

Detallles CSV:

- Bizums a mí de comidas pagadas por mí.
- Garaje -> poner a mano y quitar 90 de mi transferencia.
- Gas -> Separar en agua caliente y calefacción. Info viene en Concepto ampliado.
- Detectar que conceptos no se detectaron. Añadirlos al final sin concepto, solo descripción para completar manualmente.
- Para cada WB, permitir subir un CSV de CC y otro de tarjeta. Admitir que no se suba ningún CSV de algún WB y que no de error.

Next:

* [X] Execute in production server.
* [X] Update templates
* [X] Add css and logo
* [ ] Implement add entry feature
* [X] Login

- [X] Flask complete template
- [ ] Add entry feature.
- [ ] Add separate configs per environment (`FLASK_ENV`) - DevConfig, ProdConfig, TestConfig...
- [ ] Use different reqirements.txt for development, testing (pytest), and production (gunicorn).
- [ ] Add tests with pytest

  - [ ] Tests for all asserts in DB.
- [ ] Implement DB approach (see below).
- [ ] CI/CD (GitLAB + Jenkins)
- [ ] Docker?
- [ ] Undo last entry added. To do so, set last updated entry info after any add.
- [ ] Tab to add notes. E.g. I pay something by card but the concept on the bank app will not be intuitive, so a note is added. Or add directly the entry?
- [ ] Seccurity:

  - [ ] Basic security to make public -> Password + WSGI (gunicorn)
  - [ ] Nginx (proxy inverso)
  - [ ] Hash password
  - [ ] HTTPS
  - [ ] Security against brute force if someone constantly changes IPs:
    - [ ] CAPTCHA after X attempts (of any user)
    - [ ] Log in with a unique token (harder to guess).
- [ ] Docker
- [ ] Opción para marcar entradas añadidas manualmente en amarillo para revisión posterior. Haría falta nuevo campo en BD.
- [ ] Ordenar cada día entradas de Google Sheets por fecha.
- [ ] Si hay algún error con la sync Google Sheets - BD, notificación por correo o de alguna forma.
- [ ] Backup periódico de DB y Google Sheets.
- [ ] API REST? Para ver entradas de un WB en un mes por ejemplo.
- [ ] HTML page que muestre todos los logs de logs/, con desplegable y tal.
- [ ] Que cada vez que se ejecute la app, se borren todos los log files y DB backup excepto las últimas 10.
- [ ] Actualizar pestaña para mostrar tablas. Ahora mismo se cargan las tablas completas cada vez que se abre la pestaña. Idealmente se deben cargar solo los desplegables y cargar el contenido de cada uno cuando se abra. Hasta unas 10.000 entradas (8 años de entradas) es aceptable seguir con este modelo.
- [ ] Nuevo WB de viajes. 1 hoja por viaje y añadir un campo en Miguel que no se tenga en cuenta.
- [ ] Download/Upload DB. Para facilitar cambios manuales desde mi PC.
- [ ] Poder ver estadísticas por concepto. Por ejemplo media de gastos de tipo "Ocio" en el año actual, o en los últimos 6 meses...
- [ ] Actualizar y añadir a DB los WBs de Google Sheets de 2024.
- [ ] CSS no está cargando en Nginx.
- [ ] Notificar por correo si alguna IP es baneada por fallar la contraseña.
- [ ] Mejorar interfaz en movil (se ve como en navegador, muy pequeño).

TODO 2026:

* [ ] Usar DD/MM/YY en Google Sheets en lugar de DD/MM/YYYY.

DB approach:

* Usar Base de datos.
* Cuando se quiera editar en manual, generar un libro de Google Sheets a partir de una plantilla de Google Sheets y la base de datos.
* Al terminar de editar el libro de Google Sheets, se comparará con la base de datos y esta se actualizará.
* O si no usar una misma Sheet pero que se elimine y reescriba todo el contenido cada vez que se quiera usar. Para evitar tener que crear nuevas hojas, dar permisos, etc.

## **Seguridad adicional**

* No uses `app.run(...)` para producción. Usa un servidor WSGI como gunicorn.
* **HTTPS obligatorio**: Delante del servidor WSGI, usa un proxy reverso (como NGINX con Let's Encrypt) si expones el servidor públicamente.
* **Variables sensibles** en `.env` + `python-dotenv` (por ejemplo, la clave secreta).
* **Hashea las contraseñas**: Usa `werkzeug.security.generate_password_hash()` para generar los hash que guardas.
* Mejora app.secret_key para producción.

Esto sigue siendo inseguro frente a fuerza bruta si alguien cambia IPs constantemente. Si quisieras robustecer más:

* Usar CAPTCHA tras X intentos.
* Bloquear IPs a nivel de proxy o nginx.
* Hacer login con token único para ti (más difícil de adivinar).

## Test and Deploy

Use the built-in continuous integration in GitLab.

- [ ] [Get started with GitLab CI/CD](https://docs.gitlab.com/ee/ci/quick_start/)
- [ ] [Analyze your code for known vulnerabilities with Static Application Security Testing (SAST)](https://docs.gitlab.com/ee/user/application_security/sast/)
- [ ] [Deploy to Kubernetes, Amazon EC2, or Amazon ECS using Auto Deploy](https://docs.gitlab.com/ee/topics/autodevops/requirements.html)
- [ ] [Use pull-based deployments for improved Kubernetes management](https://docs.gitlab.com/ee/user/clusters/agent/)
- [ ] [Set up protected environments
  ](https://docs.gitlab.com/ee/ci/environments/protected_environments.html)

# Link with Google Sheets Workbook

1. Create service account: [https://console.cloud.google.com/apis/api/sheets.googleapis.com/credentials](https://console.cloud.google.com/apis/api/sheets.googleapis.com/credentials)
2. Get the credential json from  the created service account: Select desired account -> Keys -> Add key -> Json will be downloaded. Add them to private\credentials.json.
3. Share the Google Sheets Workbook with the service account.
4. Use the Workbook id in the project. E.g. In the following Workbook URL, the ID is the bold characters: https://docs.google.com/spreadsheets/d/**1AI_f9J6vV0sYp65XkeKzFYMdsZYzB0jCaLKatTbzKJE**/edit?gid=768902382#gid=768902382

---

# Flask template info

```
my_flask_app/
├── main.py                   # Punto de entrada
├── config.py                 # Configuraciones por entorno
├── requirements.txt          # Dependencias
├── run.sh                    # Script para lanzar la app si quieres
├── app/                      # Código de la aplicación Flask
│   ├── __init__.py           # App factory (create_app) (*1)(*6)
│   ├── routes/               # Rutas (blueprints) (*5)
│   │   ├── __init__.py       # Paquete de routes (*7)
│   │   └── main.py
│   ├── models/               # Modelos (si usas SQLAlchemy) (*3)
│   ├── templates/            # HTML templates
│   ├── static/               # CSS, JS, imágenes
│   └── extensions.py         # Inicialización de extensiones (DB, login, etc.)
└── tests/                    # Tests unitarios
    └── test_basic.py
```

*1: creates Flask app, add config, add extensions (*4) and add routes.

*2: Flask tiene un núcleo muy simple. Para añadir cosas como bases de datos, autenticación o migraciones, se usan **extensiones** como:

* `Flask-SQLAlchemy` → para usar bases de datos relacionales como SQLite o PostgreSQL.
* `Flask-Login` → para autenticación de usuarios.
* `Flask-Migrate` → para migraciones de base de datos.

Estas extensiones se inicializan **fuera de la app** y luego se **asocian a la app** dentro de `create_app()`.

*3: Register all the models.

*4: Important to import the models before db.create_all(). If not, a model table will not be created if the model is not used in any other place.

*5: Un `Blueprint` permite  **organizar las rutas por módulos** . En vez de tener un `app.py` enorme con todas las rutas, puedes tener:

* `auth.py` con rutas de login/registro.
* `main.py` con las rutas principales.
* `api.py` con endpoints tipo REST.

Y luego registrarlas en tu app principal con:

`app.register_blueprint(auth_blueprint)`

`app.register_blueprint(api_blueprint)`

Es como tener múltiples mini-apps que se integran en una sola.

*6: Una **Application Factory** es un **patrón de diseño** recomendado por Flask para crear la aplicación de forma  **modular y reutilizable** .

En lugar de hacer esto:

`app = Flask(`

al inicio de todo el proyecto (por ejemplo en `app.py`), el patrón App Factory define una **función** que crea y devuelve una nueva instancia de `Flask`.

| Ventaja                                          | Explicación                                                                                |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------- |
| **Flexibilidad**                           | Puedes crear múltiples instancias con distinta configuración (producción, testing, etc). |
| **Testabilidad**                           | En los tests puedes crear un entorno aislado (`create_app(test_config)`).                 |
| **Evita errores de orden de importación** | Permite inicializar extensiones después de cargar la app.                                  |
| **Más limpio**                            | No todo está en un solo archivo. Cada parte está en su módulo correspondiente.           |

*7: Usar `__init.py__` en un directorio lo convierte en un paquete. Usar paquetes en lugar de módulos (un simple archivo .py) tiene beneficios cuando la aplicación escala y quieres agrupar módulos para simplificar la lógica.
