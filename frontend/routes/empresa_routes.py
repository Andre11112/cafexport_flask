from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from utils.decorators import login_required, empresa_required
import requests
from config import Config

empresa_bp = Blueprint('empresa', __name__, url_prefix='/empresa')

@empresa_bp.route('/')
def index_empresa():
    pass

@empresa_bp.route('/opciones')
def opciones_empresa():
    return render_template('empresa/opciones_empresa.html')

@empresa_bp.route('/registro', methods=['GET'])
def registro_empresa():
    # Solo renderizar la plantilla para solicitudes GET
    return render_template('empresa/registro_empresa.html')

@empresa_bp.route('/login', methods=['GET', 'POST'])
def login_empresa():
    # Renderizar la plantilla de login específica para empresas
    return render_template('empresa/login_empresa.html')

@empresa_bp.route('/logout')
@login_required
def logout_empresa():
    return redirect(url_for('logout'))

@empresa_bp.route('/dashboard')
@login_required
@empresa_required
def dashboard():
    try:
        headers = {'Authorization': f'Bearer {session.get("token")}'}
        response = requests.get(
            Config.API_ENDPOINTS['dashboard_empresa'],
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            return render_template(
                'empresa/dashboard_empresa.html',
                empresa=session.get('user'),
                stats=data.get('stats', {}),
                compras_recientes=data.get('compras_recientes', [])
            )
        else:
            flash('Error al cargar el dashboard', 'error')
            return render_template(
                'empresa/dashboard_empresa.html',
                empresa=session.get('user'),
                stats={},
                compras_recientes=[]
            )
    except requests.exceptions.RequestException as e:
        flash('Error de conexión con el servidor', 'error')
        return render_template(
            'empresa/dashboard_empresa.html',
            empresa=session.get('user'),
            stats={},
            compras_recientes=[]
        )

@empresa_bp.route('/dashboard_render')
@login_required
@empresa_required
def render_dashboard():
    try:
        headers = {'Authorization': f'Bearer {session.get("token")}'}
        response = requests.get(
            Config.API_ENDPOINTS['dashboard_empresa'],
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            return render_template(
                'empresa/dashboard_empresa.html',
                empresa=session.get('user'),
                stats=data.get('stats', {}),
                compras_recientes=data.get('compras_recientes', [])
            )
        else:
            flash('Error al cargar el dashboard', 'error')
            return render_template(
                'empresa/dashboard_empresa.html',
                empresa=session.get('user'),
                stats={},
                compras_recientes=[]
            )
    except requests.exceptions.RequestException as e:
        flash('Error de conexión con el servidor', 'error')
        return render_template(
            'empresa/dashboard_empresa.html',
            empresa=session.get('user'),
            stats={},
            compras_recientes=[]
        )

@empresa_bp.route('/perfil')
@login_required
@empresa_required
def perfil_empresa():
    try:
        headers = {'Authorization': f'Bearer {session.get("token")}'}
        response = requests.get(
            Config.API_ENDPOINTS['perfil_empresa'],
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            return render_template('empresa/perfil.html', empresa=data)
        else:
            flash('Error al cargar el perfil', 'error')
            return render_template('empresa/perfil.html', empresa=session.get('user'))
    except requests.exceptions.RequestException as e:
        flash('Error de conexión con el servidor', 'error')
        return render_template('empresa/perfil.html', empresa=session.get('user'))

@empresa_bp.route('/compras')
@login_required
@empresa_required
def compras_empresa():
    try:
        headers = {'Authorization': f'Bearer {session.get("token")}'}
        response = requests.get(
            Config.API_ENDPOINTS['compras_empresa'],
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            return render_template(
                'empresa/compras.html',
                compras=data.get('compras', []),
                estadisticas=data.get('estadisticas', {})
            )
        else:
            flash('Error al cargar las compras', 'error')
            return render_template('empresa/compras.html', compras=[], estadisticas={})
    except requests.exceptions.RequestException as e:
        flash('Error de conexión con el servidor', 'error')
        return render_template('empresa/compras.html', compras=[], estadisticas={})

@empresa_bp.route('/reportes')
@login_required
@empresa_required
def reportes_empresa():
    try:
        headers = {'Authorization': f'Bearer {session.get("token")}'}
        response = requests.get(
            Config.API_ENDPOINTS['reportes_empresa'],
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            return render_template('empresa/reportes.html', data=data)
        else:
            flash('Error al cargar los reportes', 'error')
            return render_template('empresa/reportes.html', data=None)
    except requests.exceptions.RequestException as e:
        flash('Error de conexión con el servidor', 'error')
        return render_template('empresa/reportes.html', data=None)

@empresa_bp.route('/set_session', methods=['POST'])
def set_session():
    data = request.get_json()
    session['user_type'] = data['user_type']
    session['user'] = data['user_data']
    # Guardar token en la sesión también si es necesario para otros decoradores o lógica
    if 'token' in data:
        session['token'] = data['token']
    return jsonify({'message': 'Sesión establecida correctamente'}), 200
