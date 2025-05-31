from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, jsonify
import requests
from functools import wraps
from config import API_URL, Config
from utils.decorators import login_required, campesino_required

campesino_bp = Blueprint('campesino', __name__, url_prefix='/campesino')

@campesino_bp.route('/registro', methods=['GET'])
def registro_campesino():
    # Solo renderizar la plantilla para solicitudes GET
    return render_template('campesino/registro_campesino.html')

@campesino_bp.route('/login', methods=['GET', 'POST'])
def login_campesino():
    # Renderizar la plantilla de login específica para campesinos
    return render_template('campesino/login_campesino.html')

@campesino_bp.route('/logout')
@login_required
def logout_campesino():
    return redirect(url_for('logout'))

@campesino_bp.route('/dashboard')
@login_required
@campesino_required
def dashboard():
    try:
        headers = {'Authorization': f'Bearer {session.get("token")}'}
        response = requests.get(
            Config.API_ENDPOINTS['dashboard_campesino'],
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            return render_template(
                'campesino/dashboard_campesino.html',
                campesino=session.get('user'),
                stats=data.get('stats', {}),
                ventas_recientes=data.get('ventas_recientes', [])
            )
        else:
            flash('Error al cargar el dashboard', 'error')
            return render_template(
                'campesino/dashboard_campesino.html',
                campesino=session.get('user'),
                stats={},
                ventas_recientes=[]
            )
    except requests.exceptions.RequestException as e:
        flash('Error de conexión con el servidor', 'error')
        return render_template(
            'campesino/dashboard_campesino.html',
            campesino=session.get('user'),
            stats={},
            ventas_recientes=[]
        )

@campesino_bp.route('/dashboard_render')
@login_required
@campesino_required
def render_dashboard():
    try:
        headers = {'Authorization': f'Bearer {session.get("token")}'}
        response = requests.get(
            Config.API_ENDPOINTS['dashboard_campesino'],
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            return render_template(
                'campesino/dashboard_campesino.html',
                campesino=session.get('user'),
                stats=data.get('stats', {}),
                ventas_recientes=data.get('ventas_recientes', [])
            )
        else:
            flash('Error al cargar el dashboard', 'error')
            return render_template(
                'campesino/dashboard_campesino.html',
                campesino=session.get('user'),
                stats={},
                ventas_recientes=[]
            )
    except requests.exceptions.RequestException as e:
        flash('Error de conexión con el servidor', 'error')
        return render_template(
            'campesino/dashboard_campesino.html',
            campesino=session.get('user'),
            stats={},
            ventas_recientes=[]
        )

@campesino_bp.route('/opciones')
def opciones_campesino():
    return render_template('campesino/opciones_campesino.html')

@campesino_bp.route('/perfil')
@login_required
@campesino_required
def perfil():
    try:
        headers = {'Authorization': f'Bearer {session.get("token")}'}
        response = requests.get(
            Config.API_ENDPOINTS['perfil_campesino'],
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            return render_template('campesino/perfil.html', campesino=data)
        else:
            flash('Error al cargar el perfil', 'error')
            return render_template('campesino/perfil.html', campesino=session.get('user'))
    except requests.exceptions.RequestException as e:
        flash('Error de conexión con el servidor', 'error')
        return render_template('campesino/perfil.html', campesino=session.get('user'))

@campesino_bp.route('/ventas')
@login_required
@campesino_required
def ventas():
    return render_template('campesino/ventas_campesino.html', ventas=[], estadisticas={})

@campesino_bp.route('/reportes')
@login_required
@campesino_required
def reportes():
    try:
        headers = {'Authorization': f'Bearer {session.get("token")}'}
        response = requests.get(
            f"{Config.API_URL}/campesino/reportes_campesino",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            return render_template('campesino/reportes_campesino.html', 
                                campesino=session.get('user'),
                                data=data)
        else:
            flash('Error al cargar los reportes', 'error')
            return render_template('campesino/reportes_campesino.html', 
                                campesino=session.get('user'),
                                data=None)
            
    except Exception as e:
        flash('Error al cargar los reportes', 'error')
        return render_template('campesino/reportes_campesino.html', 
                             campesino=session.get('user'),
                             data=None)

@campesino_bp.route('/campesinos')
def lista_campesinos():
    try:
        response = requests.get(f"{Config.API_URL}/api/campesinos")
        campesinos = response.json()
        return render_template('campesinos/lista.html', campesinos=campesinos)
    except requests.exceptions.RequestException as e:
        return f"Error al conectar con el backend: {str(e)}", 500

@campesino_bp.route('/')
def index():
    pass

@campesino_bp.route('/productos')
@login_required
@campesino_required
def productos():
    try:
        headers = {'Authorization': f'Bearer {session.get("token")}'}
        response = requests.get(
            Config.API_ENDPOINTS['productos_campesino'],
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            return render_template('campesino/productos.html', productos=data.get('productos', []))
        else:
            flash('Error al cargar los productos', 'error')
            return render_template('campesino/productos.html', productos=[])
    except requests.exceptions.RequestException as e:
        flash('Error de conexión con el servidor', 'error')
        return render_template('campesino/productos.html', productos=[])

@campesino_bp.route('/set_session', methods=['POST'])
def set_session():
    data = request.get_json()
    session['user_type'] = data['user_type']
    session['user'] = data['user_data']
    # Guardar token en la sesión también si es necesario para otros decoradores o lógica
    if 'token' in data:
        session['token'] = data['token']
    return jsonify({'message': 'Sesión establecida correctamente'}), 200
