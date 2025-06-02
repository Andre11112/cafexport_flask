from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os


db = SQLAlchemy()

def create_app():
    app = Flask(__name__, 
                template_folder='templates',  # Actualizar la ruta de templates
                static_folder='static')
    
    # Cargar configuración
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:andres3333@localhost:5432/cafexport"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'dev-key-1234'
    
    # Inicializar extensiones
    db.init_app(app)
    
    # Registrar blueprints
    from frontend.routes.campesino_routes import campesino_bp
    from frontend.routes.empresa_routes import empresa_bp
    from backend.routes.admin_routes import admin_bp
    
    app.register_blueprint(campesino_bp, url_prefix='/campesino')
    app.register_blueprint(empresa_bp, url_prefix='/empresa')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    @app.route('/api/health')
    def health_check():
        return {'status': 'healthy'}, 200
    
    @app.route('/')
    def index():
        if session.get('user_type') == 'empresa':
            return redirect(url_for('empresa.dashboard'))
        elif session.get('user_type') == 'campesino':
            return redirect(url_for('campesino.dashboard'))
        return render_template('home.html')

    return app

app = create_app()
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'



# Modelos
class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20))  # 'campesino' o 'empresa'
    identificacion = db.Column(db.String(20), unique=True)  # NIT o cédula
    nombre = db.Column(db.String(100))
    email = db.Column(db.String(120), nullable=True)
    password_hash = db.Column(db.String(128))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Rutas
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/registro/<tipo>', methods=['GET', 'POST'])
def registro(tipo):
    if request.method == 'POST':
        identificacion = request.form.get('identificacion')
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        password = request.form.get('password')

        if Usuario.query.filter_by(identificacion=identificacion).first():
            flash('Esta identificación ya está registrada')
            return redirect(url_for('registro', tipo=tipo))

        usuario = Usuario(
            tipo=tipo,
            identificacion=identificacion,
            nombre=nombre,
            email=email
        )
        usuario.set_password(password)
        db.session.add(usuario)
        db.session.commit()
        flash('Registro exitoso')
        return redirect(url_for('login'))

    return render_template('registro.html', tipo=tipo)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identificacion = request.form.get('identificacion')
        password = request.form.get('password')
        usuario = Usuario.query.filter_by(identificacion=identificacion).first()

        if usuario and usuario.check_password(password):
            login_user(usuario)
            return redirect(url_for('dashboard'))
        flash('Identificación o contraseña incorrecta')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print('RUTAS REGISTRADAS:')
        for rule in app.url_map.iter_rules():
            print(rule)
    app.run(debug=True, port=5000)