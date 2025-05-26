from flask import Flask, jsonify, redirect, url_for, render_template, flash, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token
from datetime import timedelta
import os
from dotenv import load_dotenv
from .models import db
from .routes.auth_routes import auth_bp
from .routes.ventas_routes import ventas_bp
from flask_login import LoginManager, login_required, logout_user, login_user
from .models import Usuario
from werkzeug.security import generate_password_hash, check_password_hash

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuración de la clave secreta
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'una_clave_super_secreta_por_defecto')

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuración de JWT
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', app.config['SECRET_KEY'])
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
jwt = JWTManager(app)

# Inicializar la base de datos
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Registrar blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(ventas_bp, url_prefix='/api')

@app.route('/api/health')
def health_check():
    return jsonify({"status": "ok"}), 200

@app.route('/')
def index():
    from flask_login import current_user # Importar dentro de la función si no está globalmente disponible
    if current_user.is_authenticated:
        if current_user.tipo == 'empresa':
            return redirect(url_for('empresa_dashboard')) # Asumiendo que 'empresa_dashboard' es la función/ruta
        elif current_user.tipo == 'campesino':
            return redirect(url_for('campesino_dashboard')) # Asumiendo que 'campesino_dashboard' es la función/ruta
        else:
             # Tipo de usuario desconocido, cerrar sesión
            logout_user()
            flash('Tipo de usuario desconocido.', 'error')
            return redirect(url_for('index'))
            
    return render_template('home.html') # Renderizar la página de inicio si no está autenticado

# Helper functions to process login attempts
def process_login_campesino(cedula, password):
    usuario = Usuario.query.filter_by(cedula=cedula, tipo='campesino').first()

    if usuario and check_password_hash(usuario.password_hash, password):
        login_user(usuario)
        access_token = create_access_token(identity=usuario.id)
        return jsonify({
            'token': access_token,
            'usuario': {
                'id': usuario.id,
                'cedula': usuario.cedula,
                'nombre': usuario.nombre,
                'tipo': usuario.tipo
            }
        }), 200
    else:
        return jsonify({'error': 'Cédula o contraseña incorrecta'}), 401

def process_login_empresa(nit, password):
    usuario = Usuario.query.filter_by(nit=nit, tipo='empresa').first()

    if usuario and check_password_hash(usuario.password_hash, password):
        login_user(usuario)
        access_token = create_access_token(identity=usuario.id)
        return jsonify({
            'token': access_token,
            'usuario': {
                'id': usuario.id,
                'nit': usuario.nit,
                'nombre': usuario.nombre,
                'tipo': usuario.tipo
            }
        }), 200
    else:
        return jsonify({'error': 'NIT o contraseña incorrecta'}), 401

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not all(k in data for k in ('identificador', 'password', 'tipo_usuario')):
        return jsonify({'error': 'Datos incompletos'}), 400

    try:
        if data['tipo_usuario'] == 'campesino':
            return process_login_campesino(data['identificador'], data['password'])
        elif data['tipo_usuario'] == 'empresa':
            return process_login_empresa(data['identificador'], data['password'])
        else:
            return jsonify({'error': 'Tipo de usuario no válido'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('index')) # Redirigir a la página de inicio después de cerrar sesión

@app.route('/campesino/dashboard')
@login_required
# Asegurarse de que el usuario logueado sea campesino para acceder a este dashboard
def campesino_dashboard():
    from flask_login import current_user # Importar dentro de la función
    if current_user.tipo != 'campesino':
        flash('Acceso denegado. Por favor, inicie sesión como campesino.', 'warning')
        return redirect(url_for('index')) # O redirigir a una página de error/acceso denegado
    return render_template('campesino/dashboard_campesino.html', user=current_user)

@app.route('/empresa/dashboard')
@login_required
# Asegurarse de que el usuario logueado sea empresa para acceder a este dashboard
def empresa_dashboard():
    from flask_login import current_user # Importar dentro de la función
    if current_user.tipo != 'empresa':
        flash('Acceso denegado. Por favor, inicie sesión como empresa.', 'warning')
        return redirect(url_for('index')) # O redirigir a una página de error/acceso denegado
    return render_template('empresa/dashboard_empresa.html', user=current_user)

@app.route('/campesino/login', methods=['GET', 'POST'])
def campesino_login():
    if request.method == 'POST':
        cedula = request.form.get('cedula')
        password = request.form.get('password')
        return process_login_campesino(cedula, password)
    return render_template('campesino/login_campesino.html')
    
@app.route('/empresa/login', methods=['GET', 'POST'])
def empresa_login():
    if request.method == 'POST':
        nit = request.form.get('nit')
        password = request.form.get('password')
        return process_login_empresa(nit, password)
    return render_template('empresa/login_empresa.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='127.0.0.1', port=5000, debug=True)
