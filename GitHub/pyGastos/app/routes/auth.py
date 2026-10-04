# app/routes/auth.py

from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from werkzeug.security import check_password_hash
from datetime import datetime, timedelta
from flask_limiter.util import get_remote_address
from app.config.secrets import secrets
from app.config.config import Config
from app.libs.logger import logger
auth = Blueprint('auth', __name__)

HASHED_PASSWORD = secrets.hashed_password

# Attempts and ban per IP control. TODO: Use Redis or similar for real persistence
ip_adds = {}
"""
ip_adds = {
    'IP1': {
        'attemps': 3,
        'ban_time': datetime.now()
    }
}
"""


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")

    ip_add = get_remote_address()
    password = request.form.get("password", "")

    logger.info(f'New login requested from IP {ip_add}.')

    if ip_add not in ip_adds:
        ip_adds[ip_add] = {'attempts': 0, 'ban_time': None}

    # Check if banned
    ban_time = ip_adds[ip_add]['ban_time']
    if ban_time:
        time_since_ban = datetime.now() - ban_time
        if time_since_ban < timedelta(hours=Config.BAN_TIME):
            logger.warning('Login failed. User is already banned.')
            flash('Estás baneadito, inténtalo más tarde anda.', 'error')
            return redirect(url_for('auth.login'))
        else:
            # Remove ban after Config.BAN_TIME
            ip_adds[ip_add]['ban_time'] = None
            ip_adds[ip_add]['attempts'] = 0

    if check_password_hash(HASHED_PASSWORD, password):
        ip_adds[ip_add]['attempts'] = 0
        session.permanent = True
        session['authenticated'] = True
        logger.info('Login successfull.')
        flash('Contraseña correcta', 'success')
        return redirect(url_for('main.index'))
    else:
        ip_adds[ip_add]['attempts'] += 1
        if ip_adds[ip_add]['attempts'] >= 3:
            ip_adds[ip_add]['ban_time'] = datetime.now()
            logger.warning('Wrong password, 3rd failed login attempt, user banned.')
            flash('3º intento fallido, inténtalo más tarde.', 'error')  # in {Config.BAN_TIME} hour(s)
            return redirect(url_for('auth.login'))
        logger.warning(f'Wrong password, attempts number {ip_adds[ip_add]["attempts"]}.')
        flash('Contraseña incorrecta, inténtalo de nuevo', 'warning')
        return redirect(url_for('auth.login'))


def login_required(route_func):
    from functools import wraps

    @wraps(route_func)
    def wrapper(*args, **kwargs):
        if not session.get('authenticated'):
            return redirect(url_for('auth.login'))
        return route_func(*args, **kwargs)
    return wrapper
