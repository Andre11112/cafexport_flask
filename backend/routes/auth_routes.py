from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ..models import db, Usuario

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No se recibieron datos'}), 400
    
    # Validar campos comunes
    required_fields = ['nombre', 'email', 'password', 'tipo_usuario']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Campo {field} es requerido'}), 400
    
    tipo_usuario = data['tipo_usuario']
    
    # Verificar si el email ya existe
    if Usuario.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Ya existe un usuario con este email'}), 400
    
    # Crear usuario según el tipo
    if tipo_usuario == 'campesino':
        # Validar campos específicos de campesino
        if 'cedula' not in data:
            # Si no viene cedula, usar un valor por defecto o generarlo
            data['cedula'] = f"CC{data['email'].split('@')[0]}"
        
        # Verificar si la cédula ya existe
        if Usuario.query.filter_by(cedula=data['cedula']).first():
            return jsonify({'error': 'Ya existe un usuario con esta cédula'}), 400
        
        nuevo_usuario = Usuario(
            tipo='campesino',
            nombre=data['nombre'],
            cedula=data['cedula'],
            email=data['email'],
            direccion_finca=data.get('finca', ''),  # Mapear 'finca' a 'direccion_finca'
        )
        
    elif tipo_usuario == 'empresa':
        # Validar campos específicos de empresa
        if 'nit' not in data:
            # Si no viene nit, usar un valor por defecto o generarlo
            data['nit'] = f"NIT{data['email'].split('@')[0]}"
        
        # Verificar si el NIT ya existe
        if Usuario.query.filter_by(nit=data['nit']).first():
            return jsonify({'error': 'Ya existe una empresa con este NIT'}), 400
        
        nuevo_usuario = Usuario(
            tipo='empresa',
            nombre=data['nombre'],
            nit=data['nit'],
            email=data['email'],
            direccion_empresa=data.get('direccion', ''),  # Mapear 'direccion' a 'direccion_empresa'
        )
    else:
        return jsonify({'error': 'Tipo de usuario no válido'}), 400
    
    nuevo_usuario.set_password(data['password'])
    
    try:
        db.session.add(nuevo_usuario)
        db.session.commit()
        return jsonify({'mensaje': f'{tipo_usuario.capitalize()} registrado exitosamente'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al registrar {tipo_usuario}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or 'identificador' not in data or 'password' not in data:
        return jsonify({'error': 'Identificador y contraseña son requeridos'}), 400
    
    tipo_usuario = data.get('tipo_usuario')
    if not tipo_usuario:
        return jsonify({'error': 'Tipo de usuario es requerido'}), 400
    
    # Buscar usuario según el tipo y el identificador correspondiente
    if tipo_usuario == 'campesino':
        usuario = Usuario.query.filter_by(cedula=data['identificador'], tipo='campesino').first()
    elif tipo_usuario == 'empresa':
        usuario = Usuario.query.filter_by(nit=data['identificador'], tipo='empresa').first()
    else:
        return jsonify({'error': 'Tipo de usuario no válido'}), 400
    
    if not usuario or not usuario.check_password(data['password']):
        return jsonify({'error': 'Credenciales inválidas'}), 401
    
    # Crear token de acceso
    access_token = create_access_token(identity=str(usuario.id))
    
    # Preparar datos del usuario para el frontend
    usuario_data = {
        'id': usuario.id,
        'nombre': usuario.nombre,
        'email': usuario.email,
        'tipo': usuario.tipo
    }
    
    # Añadir campos específicos según el tipo de usuario
    if usuario.tipo == 'campesino':
        usuario_data['cedula'] = usuario.cedula
        usuario_data['direccion_finca'] = usuario.direccion_finca
    elif usuario.tipo == 'empresa':
        usuario_data['nit'] = usuario.nit
        usuario_data['direccion_empresa'] = usuario.direccion_empresa
    
    return jsonify({
        'token': access_token,
        'usuario': usuario_data,
        'tipo_usuario': usuario.tipo
    }), 200

@auth_bp.route('/perfil', methods=['GET'])
@jwt_required()
def obtener_perfil():
    usuario_id = get_jwt_identity()
    usuario = Usuario.query.get(usuario_id)
    
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    return jsonify(usuario.to_dict()), 200
