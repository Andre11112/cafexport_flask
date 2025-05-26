from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, Usuario

empresa_auth_bp = Blueprint('empresa_auth', __name__)

@empresa_auth_bp.route('/registro', methods=['POST'])
def registro_empresa():
    data = request.get_json()
    
    # Validar campos requeridos
    required_fields = ['nombre', 'nit', 'email', 'password', 'direccion_empresa']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Campo {field} es requerido'}), 400
    
    # Verificar si la empresa ya existe
    if Usuario.query.filter_by(nit=data['nit']).first():
        return jsonify({'error': 'Ya existe una empresa con este NIT'}), 400
    
    if Usuario.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Ya existe un usuario con este email'}), 400
    
    # Crear nueva empresa
    nueva_empresa = Usuario(
        tipo='empresa',
        nombre=data['nombre'],
        nit=data['nit'],
        email=data['email'],
        direccion_empresa=data['direccion_empresa']
    )
    nueva_empresa.set_password(data['password'])
    
    try:
        db.session.add(nueva_empresa)
        db.session.commit()
        return jsonify({'mensaje': 'Empresa registrada exitosamente'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al registrar empresa'}), 500

@empresa_auth_bp.route('/login', methods=['POST'])
def login_empresa():
    data = request.get_json()
    
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email y contraseña son requeridos'}), 400
    
    usuario = Usuario.query.filter_by(email=data['email'], tipo='empresa').first()
    
    if not usuario or not usuario.check_password(data['password']):
        return jsonify({'error': 'Credenciales inválidas'}), 401
    
    # Crear token de acceso
    access_token = create_access_token(identity=usuario.id)
    
    return jsonify({
        'access_token': access_token,
        'usuario': usuario.to_dict()
    }), 200

@empresa_auth_bp.route('/perfil', methods=['GET'])
@jwt_required()
def obtener_perfil_empresa():
    usuario_id = get_jwt_identity()
    usuario = Usuario.query.filter_by(id=usuario_id, tipo='empresa').first()
    
    if not usuario:
        return jsonify({'error': 'Empresa no encontrada'}), 404
    
    return jsonify(usuario.to_dict()), 200

@empresa_auth_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def obtener_dashboard_empresa():
    usuario_id = get_jwt_identity()
    usuario = Usuario.query.filter_by(id=usuario_id, tipo='empresa').first()

    if not usuario:
        return jsonify({'error': 'Usuario empresa no encontrado'}), 404

    # Aquí iría la lógica para obtener datos reales del dashboard
    # Por ahora, retornamos datos de ejemplo
    dashboard_data = {
        'stats': {
            'total_compras': 85750000,
            'meta_trimestral': 65,
            'proxima_entrega': '2025-05-22'
        },
        'compras_recientes': [
            {'tipo_cafe': 'Pergamino', 'cantidad': 120, 'proveedor': 'Juan Pérez', 'total': 10200000}
        ]
    }

    return jsonify(dashboard_data), 200 