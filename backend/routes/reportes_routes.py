from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models import db, CompraEmpresa, Usuario
from sqlalchemy import func
from datetime import datetime, timedelta

reportes_bp = Blueprint('reportes', __name__, url_prefix='/empresa')

@reportes_bp.route('/reportes_empresa', methods=['GET'])
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
