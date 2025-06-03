from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
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

@auth_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('identificador')
        password = request.form.get('password')
        
        # Datos a enviar al backend API
        login_data = {
            'identificador': email,
            'password': password,
            'tipo_usuario': 'admin'
        }
        
        try:
            # Llamar al backend API para autenticar
            backend_url = f"{Config.API_URL}/api/auth/login"
            headers = {'Content-Type': 'application/json'}
            response = requests.post(backend_url, json=login_data, headers=headers)
            
            if response.status_code == 200:
                # Login exitoso en el backend, establecer sesión en el frontend
                user_data = response.json().get('usuario')
                session['user_id'] = user_data['id']
                session['user_name'] = user_data['nombre']
                session['user_email'] = user_data['email']
                session['user_type'] = user_data['tipo'] # Guardar el tipo de usuario
                flash('Inicio de sesión de administrador exitoso', 'success')
                return redirect(url_for('auth.admin_dashboard'))
            else:
                # Error en el login según el backend
                error_message = response.json().get('error', 'Error desconocido en el backend')
                flash(f'Error en el login: {error_message}', 'error')
                
        except requests.RequestException as e:
            # Error de conexión con el backend
            flash(f'Error de conexión con el servidor de autenticación: {e}', 'error')
        except Exception as e:
            # Otros errores inesperados
            flash(f'Ocurrió un error inesperado: {e}', 'error')
            
    # Renderizar el template para GET o si el POST falla
    return render_template('admin/admin_login.html')

@auth_bp.route('/admin/dashboard')
def admin_dashboard():
    # Aquí podrías añadir lógica para cargar datos del dashboard
    return render_template('admin/admin_dashboard.html')

@auth_bp.route('/admin/reportes')
@login_required # Protect the route if needed
def admin_reportes():
    return render_template('admin/admin_reporte.html')
