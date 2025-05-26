from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import requests
from config import Config
from utils.decorators import login_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/home')
def index():
    return render_template('home.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.index'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        try:
            headers = {'Content-Type': 'application/json'}
            response = requests.post(f"{Config.API_URL}/login", json=data, headers=headers)
            if response.status_code == 200:
                user_data = response.json().get('usuario')
                user_type = response.json().get('tipo_usuario')
                session['user_id'] = user_data['id']
                session['user_name'] = user_data['nombre']
                session['user_email'] = user_data['email']
            if response.status_code == 200:
                user_data = response.json().get('usuario')
                user_type = response.json().get('tipo_usuario')
                session['user_id'] = user_data['id']
                session['user_name'] = user_data['nombre']
                session['user_email'] = user_data['email']
                session['user_type'] = user_type
                flash('Login exitoso', 'success')
            else:
                flash('Error en el login', 'error')
        except requests.RequestException as e:
            flash(f'Error de conexión: {str(e)}', 'error')
    return render_template('auth/login.html')
