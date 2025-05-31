from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models import db, CompraEmpresa, Usuario, Venta
from sqlalchemy import func
from datetime import datetime, timedelta

reportes_bp = Blueprint('reportes', __name__)

@reportes_bp.route('/empresa/reportes_empresa', methods=['GET'])
@jwt_required()
def get_reportes_empresa():
    try:
        current_user_id = get_jwt_identity()
        
        # Obtener estadísticas generales
        total_compras = db.session.query(func.sum(CompraEmpresa.total))\
            .filter_by(empresa_id=current_user_id).scalar() or 0
        
        total_cantidad = db.session.query(func.sum(CompraEmpresa.cantidad))\
            .filter_by(empresa_id=current_user_id).scalar() or 0
        
        # Obtener compras del último mes
        ultimo_mes = datetime.now() - timedelta(days=30)
        compras_ultimo_mes = db.session.query(func.sum(CompraEmpresa.total))\
            .filter(CompraEmpresa.empresa_id == current_user_id,
                   CompraEmpresa.fecha_orden >= ultimo_mes).scalar() or 0
        
        # Obtener compras del mes anterior
        mes_anterior = datetime.now() - timedelta(days=60)
        compras_mes_anterior = db.session.query(func.sum(CompraEmpresa.total))\
            .filter(CompraEmpresa.empresa_id == current_user_id,
                   CompraEmpresa.fecha_orden >= mes_anterior,
                   CompraEmpresa.fecha_orden < ultimo_mes).scalar() or 0
        
        # Calcular variación porcentual
        variacion_porcentual = 0
        if compras_mes_anterior > 0:
            variacion_porcentual = ((compras_ultimo_mes - compras_mes_anterior) / compras_mes_anterior) * 100
        
        # Obtener compras por tipo de café
        compras_por_tipo = db.session.query(
            CompraEmpresa.tipo_cafe,
            func.sum(CompraEmpresa.cantidad).label('cantidad_total'),
            func.sum(CompraEmpresa.total).label('valor_total')
        ).filter_by(empresa_id=current_user_id)\
         .group_by(CompraEmpresa.tipo_cafe).all()
        
        # Obtener compras por mes
        compras_por_mes = db.session.query(
            func.date_trunc('month', CompraEmpresa.fecha_orden).label('mes'),
            func.sum(CompraEmpresa.total).label('total')
        ).filter_by(empresa_id=current_user_id)\
         .group_by('mes')\
         .order_by('mes')\
         .limit(12).all()
        
        # Formatear datos para la respuesta
        reportes = {
            'estadisticas': {
                'total_compras': float(total_compras),
                'total_cantidad': float(total_cantidad),
                'precio_promedio': float(total_compras / total_cantidad) if total_cantidad > 0 else 0,
                'compras_ultimo_mes': float(compras_ultimo_mes),
                'variacion_porcentual': float(variacion_porcentual)
            },
            'compras_por_tipo': [
                {
                    'tipo': tipo.value,
                    'cantidad': float(cantidad),
                    'valor': float(valor)
                } for tipo, cantidad, valor in compras_por_tipo
            ],
            'compras_por_mes': [
                {
                    'mes': mes.strftime('%Y-%m'),
                    'total': float(total)
                } for mes, total in compras_por_mes
            ]
        }
        
        return jsonify(reportes), 200
        
    except Exception as e:
        print(f"Error al obtener reportes: {e}")
        return jsonify({'message': 'Error al obtener reportes', 'error': str(e)}), 500

@reportes_bp.route('/campesino/reportes_campesino', methods=['GET'])
@jwt_required()
def get_reportes_campesino():
    try:
        current_user_id = get_jwt_identity()
        
        # Obtener estadísticas generales
        total_ventas = db.session.query(func.sum(Venta.total))\
            .filter_by(campesino_id=current_user_id).scalar() or 0
        
        cantidad_kg = db.session.query(func.sum(Venta.cantidad))\
            .filter_by(campesino_id=current_user_id).scalar() or 0
        
        # Calcular precio promedio
        # Asegurarse de que total_ventas y cantidad_kg sean números antes de la división
        total_ventas_float = float(total_ventas) if total_ventas is not None else 0
        cantidad_kg_float = float(cantidad_kg) if cantidad_kg is not None else 0
        precio_promedio = total_ventas_float / cantidad_kg_float if cantidad_kg_float > 0 else 0
        
        # Obtener ventas del mes actual
        inicio_mes_actual = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        mes_actual = db.session.query(func.sum(Venta.total))\
            .filter(Venta.campesino_id == current_user_id,
                   Venta.fecha >= inicio_mes_actual).scalar() or 0
        
        # Obtener ventas del mes anterior
        inicio_mes_anterior = (inicio_mes_actual - timedelta(days=1)).replace(day=1)
        fin_mes_anterior = inicio_mes_actual - timedelta(days=1)
        mes_anterior = db.session.query(func.sum(Venta.total))\
            .filter(Venta.campesino_id == current_user_id,
                   Venta.fecha >= inicio_mes_anterior,
                   Venta.fecha <= fin_mes_anterior).scalar() or 0
        
        # Calcular variación porcentual mensual
        mes_actual_float = float(mes_actual) if mes_actual is not None else 0
        mes_anterior_float = float(mes_anterior) if mes_anterior is not None else 0
        mes_diferencia = 0
        if mes_anterior_float > 0:
            mes_diferencia = ((mes_actual_float - mes_anterior_float) / mes_anterior_float) * 100
        
        # Obtener ventas del año actual
        inicio_anio_actual = datetime.now().replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        anio_actual = db.session.query(func.sum(Venta.total))\
            .filter(Venta.campesino_id == current_user_id,
                   Venta.fecha >= inicio_anio_actual).scalar() or 0
        
        # Obtener ventas del año anterior
        inicio_anio_anterior = inicio_anio_actual.replace(year=inicio_anio_actual.year - 1)
        fin_anio_anterior = inicio_anio_actual - timedelta(days=1)
        anio_anterior = db.session.query(func.sum(Venta.total))\
            .filter(Venta.campesino_id == current_user_id,
                   Venta.fecha >= inicio_anio_anterior,
                   Venta.fecha <= fin_anio_anterior).scalar() or 0
        
        # Calcular variación porcentual anual
        anio_actual_float = float(anio_actual) if anio_actual is not None else 0
        anio_anterior_float = float(anio_anterior) if anio_anterior is not None else 0
        anio_diferencia = 0
        if anio_anterior_float > 0:
            anio_diferencia = ((anio_actual_float - anio_anterior_float) / anio_anterior_float) * 100
        
        # Obtener ventas por tipo de café
        ventas_por_tipo = db.session.query(
            Venta.tipo_cafe,
            func.sum(Venta.cantidad).label('cantidad_total'),
            func.sum(Venta.total).label('valor_total')
        ).filter_by(campesino_id=current_user_id)\
         .group_by(Venta.tipo_cafe).all() or [] # Asegurarse de que sea una lista incluso si no hay resultados
        
        # Obtener ventas por mes
        ventas_por_mes = db.session.query(
            func.date_trunc('month', Venta.fecha).label('mes'),
            func.sum(Venta.total).label('total')
        ).filter_by(campesino_id=current_user_id)\
         .group_by('mes')\
         .order_by('mes')\
         .limit(12).all() or [] # Asegurarse de que sea una lista incluso si no hay resultados
        
        # Formatear datos para la respuesta
        reportes = {
            'total_ventas': float(total_ventas_float),
            'cantidad_kg': float(cantidad_kg_float),
            'precio_promedio': float(precio_promedio),
            'mes_actual': float(mes_actual_float),
            'mes_diferencia': float(mes_diferencia),
            'anio_actual': float(anio_actual_float),
            'anio_diferencia': float(anio_diferencia),
            'ventas_por_tipo': {
                'labels': [tipo.value for tipo, _, _ in ventas_por_tipo],
                'data': [float(valor) for _, _, valor in ventas_por_tipo]
            },
            'ventas_por_mes': {
                'labels': [mes.strftime('%Y-%m') for mes, _ in ventas_por_mes],
                'data': [float(total) for _, total in ventas_por_mes]
            }
        }
        
        return jsonify(reportes), 200
        
    except Exception as e:
        import traceback
        print(f"Error detallado al obtener reportes del campesino: {e}")
        traceback.print_exc()
        return jsonify({'message': 'Error al obtener reportes', 'error': str(e)}), 500
