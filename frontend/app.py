from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import requests
import os
from config import Config
from werkzeug.routing import BuildError
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

def create_app():
    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')

    # Cargar configuración
    app.config.from_object(Config)
    # Asegurarse de que SECRET_KEY se carga desde la configuración
    app.config['SECRET_KEY'] = 'dev-key-1234' # Restaurar clave secreta original

    # Registrar blueprints
    try:
        # Restaurar importaciones originales (asumiendo que eran relativas)
        from routes.campesino_routes import campesino_bp
        from routes.empresa_routes import empresa_bp
        from routes.auth_routes import auth_bp
        app.register_blueprint(campesino_bp, url_prefix='/campesino')
        app.register_blueprint(empresa_bp, url_prefix='/empresa')
        app.register_blueprint(auth_bp)
    except ImportError as e:
        app.logger.warning(f"No se pudieron registrar blueprints de frontend: {e}")
        # Considerar si esto debería ser un error fatal en lugar de una advertencia

    @app.route('/')
    def index():
        # Siempre renderizar la página principal
        return render_template('home.html')

    @app.route('/health')
    def health_check():
        return {'status': 'healthy'}, 200

    @app.route('/registro/<tipo>', methods=['GET', 'POST'])
    def registro(tipo):
        if request.method == 'POST':
            data = {
                'nombre': request.form.get('nombre'),
                'email': request.form.get('email'),
                'password': request.form.get('password')
            }

            # Agregar campos específicos según el tipo
            if tipo == 'empresa':
                data['nit'] = request.form.get('identificacion')
                data['direccion_empresa'] = request.form.get('direccion', '')
            else:  # campesino
                data['cedula'] = request.form.get('identificacion')
                data['direccion_finca'] = request.form.get('direccion', '')

            try:
                # Usar API_ENDPOINTS para la URL
                api_url = Config.API_ENDPOINTS.get(f'registro_{tipo}')
                if not api_url:
                    flash(f'Error: Endpoint de registro para {tipo} no configurado.', 'error')
                    return render_template('registro.html', tipo=tipo)

                response = requests.post(
                    api_url,
                    json=data
                )

                if response.status_code == 201:
                    flash('Registro exitoso')
                    return redirect(url_for('login'))
                else:
                    error_data = response.json()
                    flash(error_data.get('error', 'Error en el registro'))
            except requests.exceptions.RequestException as e:
                flash(f'Error de conexión con el servidor: {e}', 'error')
            except Exception as e:
                 flash(f'Error inesperado durante el registro: {e}', 'error')

        return render_template('registro.html', tipo=tipo)

    @app.route('/logout')
    def logout():
        session.clear()
        flash('Sesión cerrada exitosamente', 'success')
        return redirect(url_for('index'))

    @app.route('/dashboard')
    def dashboard():
        # Manually check if user is logged in via session
        if 'user_type' not in session:
            flash('Por favor, inicia sesión para acceder a esta página.', 'info')
            return redirect(url_for('login')) # Redirigir al login si no hay sesión

        # Determinar el tipo de usuario loggeado y redirigir al dashboard específico
        user_type = session.get('user_type')
        if user_type == 'empresa':
            return render_template('empresa/dashboard_empresa.html')
        elif user_type == 'campesino':
            return render_template('campesino/dashboard_campesino.html')
        else:
            # Esto no debería pasar si 'user_type' está en la sesión, pero es una precaución.
            flash("Tipo de usuario desconocido o sesión inválida.", "error")
            session.clear()
            return redirect(url_for('index'))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5001)
