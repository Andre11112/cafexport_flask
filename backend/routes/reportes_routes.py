from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models import db, CompraEmpresa, Usuario, Venta
from sqlalchemy import func
from datetime import datetime, timedelta
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

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
        
        # Obtener precio promedio de compra por mes
        precio_promedio_por_mes = db.session.query(
            func.date_trunc('month', CompraEmpresa.fecha_orden).label('mes'),
            (func.sum(CompraEmpresa.total) / func.sum(CompraEmpresa.cantidad)).label('precio_promedio')
        ).filter_by(empresa_id=current_user_id)\
         .group_by('mes')\
         .order_by('mes')\
         .limit(12).all() or []
        
        # Obtener historial detallado de compras
        historial_compras = CompraEmpresa.query.filter_by(empresa_id=current_user_id).order_by(CompraEmpresa.fecha_orden.desc()).all()

        historial_compras_data = []
        for compra in historial_compras:
            historial_compras_data.append({
                'id': compra.id,
                'fecha_orden': compra.fecha_orden.strftime('%Y-%m-%d %H:%M:%S') if compra.fecha_orden else None,
                'tipo_cafe': compra.tipo_cafe.value if compra.tipo_cafe else None,
                'cantidad': float(compra.cantidad) if compra.cantidad is not None else None,
                'precio_kg': float(compra.precio_kg) if compra.precio_kg is not None else None,
                'total': float(compra.total) if compra.total is not None else None,
                'estado': compra.estado.value if compra.estado else None,
                'notas': compra.notas,
                'vendedor': compra.cafexport_vendedor.nombre if compra.cafexport_vendedor else 'N/A' # Asumiendo que CafExport es el vendedor
            })
        
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
            ],
            'precio_promedio_por_mes': [
                {
                    'mes': mes.strftime('%Y-%m'),
                    'precio_promedio': float(precio_promedio)
                } for mes, precio_promedio in precio_promedio_por_mes
            ],
            'historial_compras': historial_compras_data
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

# Nueva ruta para exportar reportes de compras a PDF para empresas
@reportes_bp.route('/empresa/exportar_reportes_pdf', methods=['GET', 'OPTIONS'])
@jwt_required()
def exportar_reportes_empresa_pdf():
    # Manejar solicitudes OPTIONS para CORS preflight
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    current_user_id = get_jwt_identity()
    empresa = Usuario.query.get(current_user_id)

    if not empresa or empresa.tipo != 'empresa':
        return jsonify({'msg': 'Acceso denegado'}), 403

    periodo = request.args.get('periodo', 'Último mes')

    # Calcular el rango de fechas basado en el período
    fecha_fin = datetime.utcnow()
    fecha_inicio = None

    if periodo == 'Último mes':
        # Calcular el inicio del mes actual o últimos 30 días para simplificar
        fecha_inicio = fecha_fin - timedelta(days=30)
    elif periodo == 'Últimos 3 meses':
        fecha_inicio = fecha_fin - timedelta(days=90)
    elif periodo == 'Último año':
        fecha_inicio = fecha_fin - timedelta(days=365)
    elif periodo == 'Todo el tiempo':
        fecha_inicio = datetime.min # Desde el inicio de los tiempos (o un fecha muy antigua)
    # Si el período no coincide con ninguno, podríamos devolver un error o usar un rango por defecto

    if not fecha_inicio:
         return jsonify({'error': 'Período no válido'}), 400

    try:
        # Obtener las compras de la empresa para el período, ordenadas por fecha
        compras = CompraEmpresa.query.filter(
            CompraEmpresa.empresa_id == empresa.id,
            CompraEmpresa.fecha_orden >= fecha_inicio,
            CompraEmpresa.fecha_orden <= fecha_fin
        ).options(db.joinedload(CompraEmpresa.cafexport_vendedor)).order_by(CompraEmpresa.fecha_orden.asc()).all()

        if not compras:
            return jsonify({'message': 'No hay información disponible para generar el reporte en este período.'}), 404 # Código 404 Not Found es apropiado aquí

        # Si hay compras, proceder a generar el PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        # Estilos
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='ReportTitle', fontSize=16, spaceAfter=14, alignment=1, bold=1))
        styles.add(ParagraphStyle(name='InfoStyle', fontSize=10, spaceAfter=6))
        styles.add(ParagraphStyle(name='SectionTitle', fontSize=14, spaceAfter=10, bold=1))

        # Título del reporte
        elements.append(Paragraph(f'Reporte de Compras - {periodo}', styles['ReportTitle']))
        elements.append(Paragraph(f'Empresa: {empresa.nombre}', styles['InfoStyle']))
        elements.append(Paragraph(f'Fecha de Generación: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', styles['InfoStyle']))
        elements.append(Spacer(1, 0.2*inch))

        # Calcular estadísticas de resumen para el período
        total_compras_periodo = sum(compra.total for compra in compras) if compras else 0
        total_cantidad_periodo = sum(compra.cantidad for compra in compras) if compras else 0
        precio_promedio_periodo = (total_compras_periodo / total_cantidad_periodo) if total_cantidad_periodo > 0 else 0

        # Calcular estadísticas por tipo de café
        compras_por_tipo = {}
        for compra in compras:
            tipo = compra.tipo_cafe.value if compra.tipo_cafe else 'N/A'
            if tipo not in compras_por_tipo:
                compras_por_tipo[tipo] = {
                    'cantidad_total': 0,
                    'valor_total': 0,
                    'precio_promedio': 0
                }
            compras_por_tipo[tipo]['cantidad_total'] += compra.cantidad if compra.cantidad else 0
            compras_por_tipo[tipo]['valor_total'] += compra.total if compra.total else 0

        # Calcular precio promedio por tipo
        for tipo in compras_por_tipo:
            if compras_por_tipo[tipo]['cantidad_total'] > 0:
                compras_por_tipo[tipo]['precio_promedio'] = (
                    compras_por_tipo[tipo]['valor_total'] / 
                    compras_por_tipo[tipo]['cantidad_total']
                )

        # Obtener evolución de precios por mes
        precios_por_mes = db.session.query(
            func.date_trunc('month', CompraEmpresa.fecha_orden).label('mes'),
            CompraEmpresa.tipo_cafe,
            func.avg(CompraEmpresa.precio_kg).label('precio_promedio')
        ).filter(
            CompraEmpresa.empresa_id == empresa.id,
            CompraEmpresa.fecha_orden >= fecha_inicio,
            CompraEmpresa.fecha_orden <= fecha_fin
        ).group_by(
            'mes',
            CompraEmpresa.tipo_cafe
        ).order_by('mes').all()

        # Añadir estadísticas de resumen al PDF
        elements.append(Paragraph('Resumen del Período:', styles['SectionTitle']))
        elements.append(Paragraph(f'Total Compras: {total_compras_periodo:,.0f} COP', styles['InfoStyle']))
        elements.append(Paragraph(f'Cantidad Total Comprada: {total_cantidad_periodo:.2f} kg', styles['InfoStyle']))
        elements.append(Paragraph(f'Precio Promedio: {precio_promedio_periodo:,.0f} COP/kg', styles['InfoStyle']))
        elements.append(Spacer(1, 0.2*inch))

        # Añadir estadísticas por tipo de café
        elements.append(Paragraph('Compras por Tipo de Café:', styles['SectionTitle']))
        for tipo, stats in compras_por_tipo.items():
            elements.append(Paragraph(f'Tipo: {tipo}', styles['InfoStyle']))
            elements.append(Paragraph(f'  Cantidad Total: {stats["cantidad_total"]:.2f} kg', styles['InfoStyle']))
            elements.append(Paragraph(f'  Valor Total: {stats["valor_total"]:,.0f} COP', styles['InfoStyle']))
            elements.append(Paragraph(f'  Precio Promedio: {stats["precio_promedio"]:,.0f} COP/kg', styles['InfoStyle']))
            elements.append(Spacer(1, 0.1*inch))

        elements.append(Spacer(1, 0.2*inch))

        # Añadir evolución de precios
        elements.append(Paragraph('Evolución de Precios por Mes:', styles['SectionTitle']))
        data_precios = [['Mes', 'Tipo Café', 'Precio Promedio (COP/kg)']]
        for mes, tipo, precio in precios_por_mes:
            data_precios.append([
                mes.strftime('%Y-%m'),
                tipo.value if tipo else 'N/A',
                f'{precio:,.0f}' if precio else 'N/A'
            ])

        # Crear tabla de evolución de precios
        table_precios = Table(data_precios)
        style_precios = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.Color(0.08, 0.44, 0.25, 1)),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.Color(0.95, 0.95, 0.95, 1)),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ])
        table_precios.setStyle(style_precios)
        elements.append(table_precios)
        elements.append(Spacer(1, 0.2*inch))

        # Detalles de las Compras (Tabla)
        elements.append(Paragraph('Detalle de Compras:', styles['SectionTitle']))
        data = [
            ['Fecha Orden', 'Tipo Café', 'Cantidad (kg)', 'Precio/kg (COP)', 'Total (COP)', 'Estado', 'Vendedor']
        ]
        for compra in compras:
            data.append([
                compra.fecha_orden.strftime('%Y-%m-%d') if compra.fecha_orden else '',
                compra.tipo_cafe.value if compra.tipo_cafe else '',
                f'{compra.cantidad:.2f}' if compra.cantidad is not None else '',
                f'{compra.precio_kg:,.0f}' if compra.precio_kg is not None else '',
                f'{compra.total:,.0f}' if compra.total is not None else '',
                compra.estado.value if compra.estado else '',
                compra.cafexport_vendedor.nombre if compra.cafexport_vendedor else 'N/A'
            ])

        # Crear la tabla y aplicar estilos (usando estilos similares a los del reporte del campesino para consistencia)
        table = Table(data)
        style = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.Color(0.08, 0.44, 0.25, 1)), # Verde oscuro
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.Color(0.95, 0.95, 0.95, 1)), # Gris muy claro para filas impares
            ('BACKGROUND', (0,2), (-1,-1), colors.Color(0.85, 0.95, 0.85, 1)), # Verde claro para filas pares (alternado)
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ])
        table.setStyle(style)
        elements.append(table)

        # Construir el PDF
        doc.build(elements)

        # Obtener el contenido del PDF y enviarlo
        pdf_content = buffer.getvalue()
        buffer.close()

        from flask import make_response
        response = make_response(pdf_content)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=reporte_compras_empresa_{periodo.replace(" ", "_").lower()}.pdf'
        response.headers['Access-Control-Expose-Headers'] = 'Content-Disposition' # Exponer header

        return response, 200

    except Exception as e:
        import traceback
        print("ERROR IN exportar_reportes_empresa_pdf:")
        traceback.print_exc()
        return jsonify({'error': f'Error interno al generar el reporte PDF de empresa: {e}'}), 500
