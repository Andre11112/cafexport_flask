from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from backend.models import db, CompraEmpresa, TipoCafeEnum, EstadoVentaEnum, EstadoCompraEnum, Usuario, PrecioCafe
from sqlalchemy import func
from datetime import datetime
from functools import wraps
import requests # Importar la librería requests

compra_bp = Blueprint('compra', __name__, url_prefix='/empresa')

def empresa_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        user = Usuario.query.get(current_user_id)
        
        if not user or user.tipo != 'empresa':
            return jsonify({'msg': 'Acceso denegado: Se requiere perfil de empresa'}), 403
        return fn(*args, **kwargs)
    return wrapper

# Función para obtener el ID del usuario de CafExport
def get_cafexport_user_id():
    cafexport_user = Usuario.query.filter_by(tipo='admin').first()
    if cafexport_user:
        return cafexport_user.id
    return None

@compra_bp.route('/compras', methods=['GET'])
@jwt_required()
@empresa_required
def get_compras_empresa():
    try:
        current_user_id = get_jwt_identity()
        print(f"Obteniendo compras para empresa_id: {current_user_id}") # Debug

        compras = db.session.query(CompraEmpresa, Usuario.nombre.label('vendedor_nombre'))\
            .join(Usuario, CompraEmpresa.cafexport_vendedor_id == Usuario.id)\
            .filter(CompraEmpresa.empresa_id == current_user_id)\
            .order_by(CompraEmpresa.fecha_orden.desc())\
            .all()
        
        print(f"Compras encontradas: {len(compras)}") # Debug
        
        compras_list = []
        for compra, vendedor_nombre in compras:
            compra_dict = compra.to_dict()
            compra_dict['vendedor_nombre'] = vendedor_nombre
            compras_list.append(compra_dict)
            print(f"Compra procesada: {compra_dict}") # Debug

        return jsonify({'compras': compras_list}), 200

    except Exception as e:
        print(f"Error al obtener compras de empresa: {e}")
        return jsonify({'message': 'Error interno del servidor al obtener compras'}), 500

@compra_bp.route('/estadisticas_compras', methods=['GET'])
@jwt_required()
@empresa_required
def get_estadisticas_compras():
    try:
        current_user_id = get_jwt_identity()
        print(f"Obteniendo estadísticas para empresa_id: {current_user_id}") # Debug

        total_compras_cantidad = db.session.query(func.sum(CompraEmpresa.cantidad))\
            .filter_by(empresa_id=current_user_id).scalar() or 0
        total_inversion = db.session.query(func.sum(CompraEmpresa.total))\
            .filter_by(empresa_id=current_user_id).scalar() or 0
        total_compras_count = db.session.query(func.count(CompraEmpresa.id))\
            .filter_by(empresa_id=current_user_id).scalar() or 0

        completadas_count = db.session.query(func.count(CompraEmpresa.id))\
            .filter_by(empresa_id=current_user_id, estado=EstadoCompraEnum.Completada.value).scalar() or 0
        en_transito_count = db.session.query(func.count(CompraEmpresa.id))\
            .filter_by(empresa_id=current_user_id, estado=EstadoCompraEnum.Pendiente.value).scalar() or 0
        confirmadas_count = db.session.query(func.count(CompraEmpresa.id))\
            .filter_by(empresa_id=current_user_id, estado=EstadoCompraEnum.Confirmadas.value).scalar() or 0

        precio_promedio = (total_inversion / total_compras_count) if total_compras_count > 0 else 0

        estadisticas = {
            'total_compras_cantidad': float(total_compras_cantidad),
            'total_inversion': float(total_inversion),
            'total_compras_count': total_compras_count,
            'completadas_count': completadas_count,
            'en_transito_count': en_transito_count,
            'confirmadas_count': confirmadas_count,
            'precio_promedio': float(precio_promedio)
        }

        print(f"Estadísticas calculadas: {estadisticas}") # Debug
        return jsonify({'estadisticas': estadisticas}), 200

    except Exception as e:
        print(f"Error al obtener estadísticas de compras: {e}")
        return jsonify({'message': 'Error interno del servidor al obtener estadísticas de compras'}), 500

@compra_bp.route('/registrar_compra', methods=['POST'])
@jwt_required()
@empresa_required
def registrar_compra():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        print(f"Registrando compra para empresa_id: {current_user_id}") # Debug
        print(f"Datos recibidos: {data}") # Debug

        cafexport_id = get_cafexport_user_id()
        if not cafexport_id:
            return jsonify({'message': 'Error: No se encontró el usuario de CafExport.'}), 500

        # Validar datos requeridos
        required_fields = ['tipo_cafe', 'cantidad', 'precio_kg', 'fecha_orden']
        for field in required_fields:
            if field not in data:
                return jsonify({'message': f'Campo requerido faltante: {field}'}), 400

        try:
            tipo_cafe = TipoCafeEnum[data['tipo_cafe']]
            cantidad = float(data['cantidad'])
            precio_kg = float(data['precio_kg'])
            fecha_orden = datetime.strptime(data['fecha_orden'], '%Y-%m-%d')
            fecha_entrega = datetime.strptime(data['fecha_entrega'], '%Y-%m-%d') if data.get('fecha_entrega') else None
        except (ValueError, KeyError) as e:
            return jsonify({'message': f'Error en el formato de los datos: {str(e)}'}), 400

        nueva_compra = CompraEmpresa(
            empresa_id=current_user_id,
            cafexport_vendedor_id=cafexport_id,
            tipo_cafe=tipo_cafe,
            cantidad=cantidad,
            precio_kg=precio_kg,
            fecha_orden=fecha_orden,
            fecha_entrega=fecha_entrega,
            notas=data.get('notas'),
            estado=EstadoCompraEnum.Pendiente
        )

        db.session.add(nueva_compra)
        db.session.commit()

        print(f"Compra registrada exitosamente: {nueva_compra.to_dict()}") # Debug
        return jsonify({'message': 'Compra registrada con éxito', 'compra': nueva_compra.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        print(f"Error al registrar compra: {e}")
        return jsonify({'message': 'Error interno del servidor al registrar compra'}), 500

@compra_bp.route('/precios_cafe', methods=['GET'])
def get_precios_cafe():
    # Esta ruta ahora llamará a la API de precios del campesino
    # en lugar de consultar la base de datos local.
    ventas_api_url = 'http://127.0.0.1:5000/api/precios_cafe'
    try:
        response = requests.get(ventas_api_url)
        response.raise_for_status() # Lanza una excepción para códigos de estado de error
        precios_data = response.json()
        print(f"Precios de café obtenidos de la API de ventas: {precios_data}") # Debug

        # La API de ventas devuelve precio_pergamino y precio_pasilla
        # Si el frontend espera 'arabica' y 'pasilla' (sin 'precio_'),
        # podemos mapearlos aquí o manejarlo en el frontend.
        # Por ahora, mapearemos a los nombres que usa el frontend para mostrar.
        # Nota: La API de ventas devuelve strings con formato (ej. "$2.763.000"),
        # el frontend deberá limpiarlos para usarlos en cálculos.

        return jsonify({
            'arabica': precios_data.get('precio_pergamino'),
            'pasilla': precios_data.get('precio_pasilla'),
            'fecha_actualizacion': precios_data.get('fecha_actualizacion')
        }), 200

    except requests.exceptions.RequestException as e:
        print(f"Error al obtener precios de la API de ventas: {e}")
        return jsonify({'message': 'Error al obtener precios de café de la fuente externa'}), 500
    except Exception as e:
        print(f"Error inesperado al procesar precios: {e}")
        return jsonify({'message': 'Error interno al procesar precios de café'}), 500 