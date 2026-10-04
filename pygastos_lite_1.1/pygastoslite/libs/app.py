from flask import Flask, render_template, request, redirect, url_for, session
from flask_limiter.util import get_remote_address
from werkzeug.security import check_password_hash
from libs.workbook import get_wb
from libs.logger import logger
import json5
import secrets
from datetime import datetime, timedelta


app = Flask(
    __name__,
    static_folder='../static',
    template_folder='../templates'
)

app.secret_key = secrets.token_hex(32)  # Needed for the sessions to work. Any string is valid.
app.permanent_session_lifetime = timedelta(weeks=1)  # Session duration. TODO: config, same for ban time
app.config['SESSION_REFRESH_EACH_REQUEST'] = False  # Session timeout not reset with each request

ip_adds = {
    'IP1': {
        'attemps': 3,
        'ban_time': datetime.now()
    }
}


# Create one key per IP
def rate_limit_key():
    return f"login-fail:{get_remote_address()}"


# Import configs
with open('config/common.json') as json_file:
    common_cfg = json5.load(json_file)
with open('config/workbooks.json') as json_file:
    workbooks_cfg = json5.load(json_file)

wb_cfg = workbooks_cfg['miguel']  # TODO: make configurable for several workbooks
concepts = [concept['name'] for concept in wb_cfg['concepts']]
months = common_cfg['sheet_names']

with open('private/secrets.json') as json_file:
    secrets = json5.load(json_file)

HASHED_PASSWORD = secrets['hashed_password']

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login routine made by me, as flask authentication did not work as desired. Current behabiour:
    - Login only with password.
    - If password failed 3 times, 1 hour ban.
    - Session expires after 1 week.
    """
    if request.method == 'GET':
        return render_template("login.html")

    ip_add = get_remote_address()
    password = request.form.get("password", "")

    # if ip_add in ip_adds.keys() and ip_adds[ip_add]['attempts'] >= 3 and :
    if ip_add not in ip_adds.keys():
        if check_password_hash(HASHED_PASSWORD, password) is True:
            session.permanent = True
            session['authenticated'] = True
            return redirect(url_for('index'))
        else:
            ip_adds[ip_add] = {
                'attempts': 1,
                'ban_time': None
            }
            return render_template("login.html", error="Contraseña incorrecta.")

    if ip_adds[ip_add]['attempts'] >= 3:
        time_since_ban = datetime.now() - ip_adds[ip_add]['ban_time']
        if time_since_ban < timedelta(hours=1):
            return render_template("login.html", error="Estás baneadito, inténtalo más tarde.")

        ip_adds[ip_add]['ban_time'] = None

        if check_password_hash(HASHED_PASSWORD, password) is True:
            ip_adds[ip_add]['attempts'] = 0
            session.permanent = True
            session['authenticated'] = True
            return redirect(url_for('index'))

        ip_adds[ip_add]['attempts'] = 1
        return render_template("login.html", error="Contraseña incorrecta.")

    if check_password_hash(HASHED_PASSWORD, password) is True:
        ip_adds[ip_add]['attempts'] = 0
        session.permanent = True
        session['authenticated'] = True
        return redirect(url_for('index'))

    ip_adds[ip_add]['attempts'] += 1
    if ip_adds[ip_add]['attempts'] >= 3:
        ip_adds[ip_add]['ban_time'] = datetime.now()
        return render_template("login.html", error="Estás baneadito, inténtalo más tarde.")
    return render_template("login.html", error="Contraseña incorrecta.")


def login_required(route_func):
    from functools import wraps

    @wraps(route_func)
    def wrapper(*args, **kwargs):
        if not session.get('authenticated'):
            return redirect(url_for('login'))
        return route_func(*args, **kwargs)
    return wrapper


@app.route('/')
@login_required
def index():
    return render_template("index.html")


@app.route('/add_entry')
@login_required
def add_entry():
    return render_template("add_entry.html", concepts=concepts)


@app.route('/add',  methods=['POST'])
@login_required
def add():
    logger.info(
        f"New entry request: concept: {request.form['concept']}; "
        f"value: {request.form['value']}; "
        f"description: {request.form['description']}."
    )
    curr_month = datetime.now().month - 1  # 0 for first month
    result = get_wb('miguel').add_entry(
        sheet_name=months[curr_month],
        concept=request.form['concept'],
        value=request.form['value'],
        description=request.form['description']
        )
    if result is False:
        return redirect(url_for('fail'))
    return redirect(url_for('confirm'))


@app.route('/confirm')
@login_required
def confirm():
    logger.info("New entry added.")
    return render_template("confirm.html")


@app.route('/fail')
@login_required
def fail():
    # TODO: implement better
    logger.info("New entry add failed.")
    return render_template("fail.html")
