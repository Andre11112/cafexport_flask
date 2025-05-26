from functools import wraps
from flask import session, redirect, url_for, flash, request

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_type' not in session:
            flash('Por favor, inicia sesión para acceder a esta página.', 'info')
            # Redirigir a la página de login correspondiente según la URL
            if 'campesino' in request.path:
                return redirect(url_for('campesino.login_campesino'))
            elif 'empresa' in request.path:
                return redirect(url_for('empresa.login_empresa'))
            else:
                return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def campesino_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_type') != 'campesino':
            flash('Acceso no autorizado para campesinos.', 'error')
            # Puedes redirigir a una página de error o a la página principal
            return redirect(url_for('index')) 
        return f(*args, **kwargs)
    return decorated_function

def empresa_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_type') != 'empresa':
            flash('Acceso no autorizado para empresas.', 'error')
            # Puedes redirigir a una página de error o a la página principal
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function