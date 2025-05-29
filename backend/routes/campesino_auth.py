from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ..models import db, Usuario, Venta

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

@campesino_auth_bp.route('/login', methods=['POST', 'GET'])
def login_campesino():
    # Esta ruta es solo para POST, la lógica de GET se eliminó
    data = request.get_json()

    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email y contraseña son requeridos'}), 400
    
    usuario = Usuario.query.filter_by(email=data['email'], tipo='campesino').first()
    
    if not usuario or not usuario.check_password(data['password']):
        return jsonify({'error': 'Credenciales inválidas'}), 401
    
    # Si el login es exitoso para un campesino, redirigir al dashboard o retornar éxito (ajustar según flujo deseado)
    # Si quieres retornar un token JWT aquí, descomenta la sección de creación y retorno de token

    # access_token = create_access_token(identity=usuario.id)
    # return jsonify({'access_token': access_token}), 200

    # Alternativamente, si Flask-Login maneja la sesión web
    # login_user(usuario) # Esto establece la sesión de Flask-Login
    # return jsonify({'mensaje': 'Login exitoso'}), 200 # O redirigir en el frontend

    # Por ahora, retornemos un mensaje de éxito simple
    return jsonify({'mensaje': 'Login exitoso (manejo de sesión/token a definir)'}), 200 # Ajustar según el flujo de autenticación

@campesino_auth_bp.route('/perfil', methods=['GET'])
@jwt_required()
def obtener_perfil_campesino():
    usuario_id = get_jwt_identity()
    usuario = Usuario.query.filter_by(id=usuario_id, tipo='campesino').first()

    if not usuario:
        return jsonify({'error': 'Usuario campesino no encontrado o acceso denegado'}), 404

    return jsonify(usuario.to_dict()), 200

@campesino_auth_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def obtener_dashboard_campesino():
    try:
        usuario_id = get_jwt_identity()
        usuario = Usuario.query.filter_by(id=usuario_id, tipo='campesino').first()

        if not usuario:
            return jsonify({'error': 'Usuario campesino no encontrado o acceso denegado'}), 404

        # Obtener las 5 ventas más recientes del campesino de la base de datos
        ventas_recientes = Venta.query.filter_by(campesino_id=usuario.id).order_by(Venta.fecha.desc()).limit(5).all()

        # Preparar los datos de ventas recientes para la respuesta JSON
        ventas_recientes_data = []
        for venta in ventas_recientes:
            ventas_recientes_data.append({
                'id': venta.id,
                'fecha': venta.fecha.strftime('%Y-%m-%d %H:%M:%S') if venta.fecha else None, # Formato estándar ISO para JavaScript
                'tipo_cafe': venta.tipo_cafe.value if venta.tipo_cafe else None, # Asumiendo que tipo_cafe es un Enum
                'cantidad': float(venta.cantidad) if venta.cantidad is not None else None,
                'precio_kg': float(venta.precio_kg) if venta.precio_kg is not None else None,
                'total': float(venta.total) if venta.total is not None else None, # Total es generado, debería existir
                'estado': venta.estado.value if venta.estado else None, # Asumiendo que estado es un Enum
                'comprador': venta.empresa.nombre if venta.empresa else 'CafExport' # Obtener nombre de la empresa o usar CafExport
            })

        # Aquí iría la lógica para obtener otras estadísticas reales si las hubiera
        # Por ahora, usamos datos de estadísticas de ejemplo o calculamos básicos si es posible
        # Puedes reemplazar esto con cálculos reales basados en las ventas obtenidas
        stats_data = {
             'total_ventas': len(ventas_recientes), # Ejemplo: contar ventas recientes
             'completadas': len([v for v in ventas_recientes if v.estado.value == 'Completada']), # Ejemplo: contar completadas
             'pendientes': len([v for v in ventas_recientes if v.estado.value == 'Pendiente']), # Ejemplo: contar pendientes
             # Sumar totales si necesitas el ingreso total reciente
             'total_ingresos': sum([v.total for v in ventas_recientes if v.total is not None]) if ventas_recientes else 0.0,
             'promedio': (sum([v.total for v in ventas_recientes if v.total is not None]) / len(ventas_recientes)) if ventas_recientes and sum([v.total for v in ventas_recientes if v.total is not None]) > 0 else 0.0,
             #'meta_mensual': 80,
             #'proxima_cosecha': '2025-06-15'
         }


        # Devolver los datos reales obtenidos de la base de datos
        dashboard_data = {
            'stats': stats_data,
            'ventas_recientes': ventas_recientes_data
        }

        return jsonify(dashboard_data), 200
    except Exception as e:
        import traceback
        print("ERROR IN obtener_dashboard_campesino:")
        traceback.print_exc()
        return jsonify({'error': f'Error interno del dashboard: {e}'}), 500

# Nueva ruta para obtener las ventas de un campesino autenticado
@campesino_auth_bp.route('/ventas', methods=['GET'])
@jwt_required()
def obtener_ventas_campesino():
    try:
        # Este bloque try-except capturará errores inmediatamente después de jwt_required
        usuario_id = get_jwt_identity()
        campesino = Usuario.query.filter_by(id=usuario_id, tipo='campesino').first()

        if not campesino:
            return jsonify({'error': 'Usuario campesino no encontrado o acceso denegado'}), 404

        # Obtener ventas para este campesino, ordenadas por fecha descendente
        ventas = Venta.query.filter_by(campesino_id=campesino.id).order_by(Venta.fecha.desc()).all()

        # Preparar datos de ventas para la respuesta JSON
        ventas_data = []
        for venta in ventas:
            ventas_data.append({
                'id': venta.id,
                'fecha': venta.fecha.strftime('%Y-%m-%d'), # Formatear fecha
                'comprador': venta.comprador,
                'tipo_cafe': venta.tipo_cafe.value, # Obtener el valor string del Enum
                'cantidad': str(venta.cantidad), # Convertir Decimal a string para JSON
                'precio_kg': str(venta.precio_kg), # Convertir Decimal a string para JSON
                'total': str(venta.total), # Convertir Decimal a string para JSON
                'estado': venta.estado.value # Obtener el valor string del Enum
                # No incluir campesino_id por seguridad, ya está implícito por la ruta
            })

        return jsonify(ventas_data), 200
    except Exception as e:
        import traceback
        print("ERROR IN obtener_ventas_campesino:")
        traceback.print_exc()
        return jsonify({'error': f'Error interno al obtener ventas: {e}'}), 500 