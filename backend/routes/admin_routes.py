from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from ..models import Usuario, Venta, CompraEmpresa, db # Import Venta, CompraEmpresa and db
from flask_login import login_required, current_user # Assuming Flask-Login is used for admin session
from sqlalchemy import func # Import func for sum

admin_bp = Blueprint('admin', __name__)

# Ruta para obtener estadísticas del dashboard de admin
# Requiere que el usuario esté logueado y sea administrador
@admin_bp.route('/api/admin/stats', methods=['GET'])
# @login_required # Asegurar que se requiere login
# @admin_required # Asegurar que el usuario es admin (necesitarías crear este decorador)
def get_admin_stats():
    # Obtener conteos
    total_campesinos = Usuario.query.filter_by(tipo='campesino').count()
    total_empresas = Usuario.query.filter_by(tipo='empresa').count()
    total_admins = Usuario.query.filter_by(tipo='admin').count()

    # Calcular Volumen Total (Suma de cantidad en Ventas y ComprasEmpresa)
    volumen_ventas = db.session.query(func.sum(Venta.cantidad)).scalar() or 0
    volumen_compras = db.session.query(func.sum(CompraEmpresa.cantidad)).scalar() or 0
    volumen_total_cafe = float(volumen_ventas) + float(volumen_compras)

    # Calcular Valor Total (Suma de total en Ventas y ComprasEmpresa)
    valor_ventas = db.session.query(func.sum(Venta.total)).scalar() or 0
    valor_compras = db.session.query(func.sum(CompraEmpresa.total)).scalar() or 0
    valor_total_transacciones = float(valor_ventas) + float(valor_compras)

    return jsonify({
        'total_campesinos': total_campesinos,
        'total_empresas': total_empresas,
        'total_admins': total_admins,
        'volumen_total_cafe': round(volumen_total_cafe, 2), # Redondear si es necesario
        'valor_total_transacciones': round(valor_total_transacciones, 2) # Redondear si es necesario
    }), 200

# Ruta para obtener todas las ventas (para la tabla en el dashboard de admin)
@admin_bp.route('/api/admin/ventas', methods=['GET'])
# @login_required # Consider adding authentication/authorization
# @admin_required
def get_all_ventas():
    try:
        ventas = Venta.query.all()
        # Convertir objetos Venta a diccionarios para jsonify
        ventas_list = [{
            'id': venta.id,
            'fecha': venta.fecha.isoformat() if venta.fecha else None, # Formatear fecha
            'campesino_nombre': venta.campesino.nombre if venta.campesino else 'N/A', # Asumiendo relación con Campesino
            'tipo_cafe': str(venta.tipo_cafe) if venta.tipo_cafe else None, # Convertir Enum a string
            'cantidad': float(venta.cantidad), # Convertir Decimal a float
            'precio_kg': float(venta.precio_kg), # Convertir Decimal a float
            'total': float(venta.total), # Convertir Decimal a float
            'estado': str(venta.estado) if venta.estado else None, # Convertir Enum a string
            # Añadir otros campos si son necesarios
        } for venta in ventas]
        return jsonify(ventas_list), 200
    except Exception as e:
        print(f"Error fetching all ventas: {e}")
        return jsonify({'error': 'Error al obtener ventas'}), 500

# Ruta para obtener todas las compras de empresa (para la tabla en el dashboard de admin)
@admin_bp.route('/api/admin/compras', methods=['GET'])
# @login_required # Consider adding authentication/authorization
# @admin_required
def get_all_compras_empresa():
    try:
        compras = CompraEmpresa.query.all()
        # Convertir objetos CompraEmpresa a diccionarios para jsonify
        compras_list = [{
            'id': compra.id,
            'fecha_orden': compra.fecha_orden.isoformat() if compra.fecha_orden else None, # Formatear fecha
            'empresa_nombre': compra.empresa.nombre if compra.empresa else 'N/A', # Asumiendo relación con Empresa
            'tipo_cafe': str(compra.tipo_cafe) if compra.tipo_cafe else None, # Convertir Enum a string
            'cantidad': float(compra.cantidad), # Convertir Decimal a float
            'precio_kg': float(compra.precio_kg), # Convertir Decimal a float
            'total': float(compra.total), # Convertir Decimal a float
            'estado': str(compra.estado) if compra.estado else None, # Convertir Enum a string
            # Añadir otros campos si son necesarios
        } for compra in compras]
        return jsonify(compras_list), 200
    except Exception as e:
        print(f"Error fetching all compras empresa: {e}")
        return jsonify({'error': 'Error al obtener compras de empresa'}), 500

# Puedes añadir más rutas aquí para obtener listas de usuarios, ventas, compras, etc.
# @admin_bp.route('/api/admin/users/<user_type>', methods=['GET'])
# def get_users_by_type(user_type):
#     users = Usuario.query.filter_by(tipo=user_type).all()
#     return jsonify([user.to_dict() for user in users]), 200 