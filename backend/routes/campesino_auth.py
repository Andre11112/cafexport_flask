from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, Usuario

campesino_auth_bp = Blueprint('campesino_auth', __name__)

@campesino_auth_bp.route('/registro', methods=['POST'])
def registro_campesino():
    data = request.get_json()
    
    # Validar campos requeridos
    required_fields = ['nombre', 'cedula', 'email', 'password', 'direccion_finca']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Campo {field} es requerido'}), 400
    
    # Verificar si el usuario ya existe
    if Usuario.query.filter_by(cedula=data['cedula']).first():
        return jsonify({'error': 'Ya existe un usuario con esta cédula'}), 400
    
    if Usuario.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Ya existe un usuario con este email'}), 400
    
    # Crear nuevo usuario campesino
    nuevo_campesino = Usuario(
        tipo='campesino',
        nombre=data['nombre'],
        cedula=data['cedula'],
        email=data['email'],
        direccion_finca=data['direccion_finca']
    )
    nuevo_campesino.set_password(data['password'])
    
    try:
        db.session.add(nuevo_campesino)
        db.session.commit()
        return jsonify({'mensaje': 'Usuario campesino registrado exitosamente'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al registrar usuario campesino'}), 500

@campesino_auth_bp.route('/login', methods=['POST'])
def login_campesino():
    data = request.get_json()
    
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email y contraseña son requeridos'}), 400
    
    usuario = Usuario.query.filter_by(email=data['email'], tipo='campesino').first()
    
    if not usuario or not usuario.check_password(data['password']):
        return jsonify({'error': 'Credenciales inválidas'}), 401
    
    # Crear token de acceso
    access_token = create_access_token(identity=usuario.id)
    
    return jsonify({
        'access_token': access_token,
        'usuario': usuario.to_dict()
    }), 200

@campesino_auth_bp.route('/perfil', methods=['GET'])
@jwt_required()
def obtener_perfil_campesino():
    usuario_id = get_jwt_identity()
    usuario = Usuario.query.filter_by(id=usuario_id, tipo='campesino').first()
    
    if not usuario:
        return jsonify({'error': 'Usuario campesino no encontrado'}), 404
    
    return jsonify(usuario.to_dict()), 200

@campesino_auth_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def obtener_dashboard_campesino():
    usuario_id = get_jwt_identity()
    usuario = Usuario.query.filter_by(id=usuario_id, tipo='campesino').first()

    if not usuario:
        return jsonify({'error': 'Usuario campesino no encontrado'}), 404

    # Aquí iría la lógica para obtener datos reales del dashboard
    # Por ahora, retornamos datos de ejemplo
    dashboard_data = {
        'stats': {
            'total_ventas': 15000000,
            'meta_mensual': 80,
            'proxima_cosecha': '2025-06-15'
        },
        'ventas_recientes': [
            {'tipo_cafe': 'Pergamino', 'cantidad': 10, 'precio_kg': 85000, 'total': 850000},
            {'tipo_cafe': 'Verde', 'cantidad': 15, 'precio_kg': 75000, 'total': 1125000}
        ]
    }

    return jsonify(dashboard_data), 200 