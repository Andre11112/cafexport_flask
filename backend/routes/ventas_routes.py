from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, Venta, Usuario # Asegúrate que Venta y Usuario estén definidos en models.py
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup # Importar BeautifulSoup

# Importaciones para PDF
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer
import io

# Importaciones para gráficos
import matplotlib
matplotlib.use('Agg') # Usar backend no interactivo
import matplotlib.pyplot as plt
from reportlab.platypus import Image

ventas_bp = Blueprint('ventas', __name__)

@ventas_bp.route('/ventas', methods=['POST'])
@jwt_required() # Protege esta ruta para que solo usuarios autenticados puedan acceder
def registrar_venta():
    current_user_id = get_jwt_identity() # Obtiene el ID del usuario del token JWT
    campesino = Usuario.query.get(current_user_id)

    if not campesino:
        return jsonify({'msg': 'Acceso denegado'}), 403

    data = request.get_json()

    print(f"Received data: {data}") # Línea de depuración

    if not data or not all(k in data for k in ('cantidad', 'tipo_cafe', 'precio_kg')):
        return jsonify({'error': 'Datos incompletos'}), 400

    try:
        # Limpiar y convertir la cantidad y el precio a float, manejando comas como separador decimal y puntos como separador de miles
        # Eliminar separadores de miles (puntos), y reemplazar separador decimal (coma) por punto
        cantidad_str = str(data['cantidad']).replace('.', '').replace(',', '.')
        precio_kg_str = str(data['precio_kg']).replace('.', '').replace(',', '.')

        cantidad = float(cantidad_str)
        precio_kg = float(precio_kg_str)

        print(f"Cantidad procesada: {cantidad}, Precio_kg procesado: {precio_kg}") # Línea de depuración añadida

        # Calcular el total (asegúrate de que sea Decimal si es necesario para precisión monetaria)
        # El total es generado por la BD, no se inserta directamente
        # total = cantidad * precio_kg # Esto no es necesario ya que la BD lo calcula

        nueva_venta = Venta(
            fecha=datetime.utcnow(),
            campesino_id=campesino.id,
            tipo_cafe=data['tipo_cafe'],
            cantidad=cantidad,
            precio_kg=precio_kg,
            estado='Pendiente' # Eliminamos el campo total ya que es generado automáticamente
        )

        db.session.add(nueva_venta)
        db.session.commit()

        return jsonify({'mensaje': 'Venta registrada con éxito', 'venta': nueva_venta.to_dict()}), 201

    except ValueError:
        return jsonify({'error': 'Cantidad o precio_kg deben ser números válidos'}), 400
    except Exception as e:
        db.session.rollback()
        import traceback
        print("ERROR IN registrar_venta:")
        traceback.print_exc()
        return jsonify({'error': f'Error interno al registrar venta: {e}'}), 500

@ventas_bp.route('/ventas', methods=['GET'])
@jwt_required()
def obtener_ventas():
    current_user_id = get_jwt_identity()
    campesino = Usuario.query.get(current_user_id)

    if not campesino or campesino.tipo != 'campesino':
        return jsonify({'msg': 'Acceso denegado'}), 403

    try:
        # Obtener las ventas del campesino, cargando eagermente la relación con la empresa (comprador)
        ventas = Venta.query.filter_by(campesino_id=campesino.id).options(db.joinedload(Venta.empresa)).order_by(Venta.fecha.desc()).all()

        # Preparar los datos para la respuesta JSON
        ventas_data = []
        total_ventas = 0
        completadas = 0
        pendientes = 0
        total_ingresos = 0.0

        for venta in ventas:
            ventas_data.append({
                'id': venta.id,
                'fecha': venta.fecha.strftime('%Y-%m-%d %H:%M:%S') if venta.fecha else None,
                'tipo_cafe': venta.tipo_cafe.value if venta.tipo_cafe else None,
                'cantidad': float(venta.cantidad) if venta.cantidad is not None else None,
                'precio_kg': float(venta.precio_kg) if venta.precio_kg is not None else None,
                'total': float(venta.total) if venta.total is not None else None,
                'estado': venta.estado.value if venta.estado else None,
                'comprador': venta.empresa.nombre if venta.empresa else 'CafExport'
            })

            # Calcular estadísticas
            total_ventas += 1
            if venta.estado and venta.estado.value == 'Completada':
                completadas += 1
            elif venta.estado and venta.estado.value == 'Pendiente':
                pendientes += 1
            if venta.total is not None:
                total_ingresos += float(venta.total)

        # Calcular promedio
        promedio = total_ingresos / total_ventas if total_ventas > 0 else 0

        # Preparar respuesta con ventas y estadísticas
        response_data = {
            'ventas': ventas_data,
            'estadisticas': {
                'total_ventas': total_ventas,
                'completadas': completadas,
                'pendientes': pendientes,
                'total_ingresos': total_ingresos,
                'promedio': promedio
            }
        }

        return jsonify(response_data), 200

    except Exception as e:
        import traceback
        print("ERROR IN obtener_ventas:")
        traceback.print_exc()
        return jsonify({'error': f'Error interno al obtener ventas: {e}'}), 500

@ventas_bp.route('/precios_cafe', methods=['GET'])
def obtener_precios_cafe():
    url = 'https://federaciondecafeteros.org/wp/estadisticas-cafeteras/'
    try:
        response = requests.get(url)
        response.raise_for_status() # Lanza una excepción para códigos de estado de error

        soup = BeautifulSoup(response.content, 'html.parser')

        # Buscar los precios en el HTML (ajustar selectores si es necesario)
        # Esto es un ejemplo basado en la estructura común, puede requerir ajuste
        precio_pergamino_tag = soup.find(string='Precio interno de referencia:')
        precio_pasilla_tag = soup.find(string='Pasilla de finca:')
        tasa_cambio_tag = soup.find(string='Tasa de cambio:')

        precio_pergamino_carga = 'N/A'
        precio_pasilla_arroba = 'N/A'
        tasa_cambio_valor = 'N/A'

        if precio_pergamino_tag:
            precio_pergamino_carga = precio_pergamino_tag.find_next('strong').get_text() if precio_pergamino_tag.find_next('strong') else 'N/A'
        if precio_pasilla_tag:
            precio_pasilla_arroba = precio_pasilla_tag.find_next('strong').get_text() if precio_pasilla_tag.find_next('strong') else 'N/A'
        if tasa_cambio_tag:
             tasa_cambio_valor = tasa_cambio_tag.find_next('strong').get_text() if tasa_cambio_tag.find_next('strong') else 'N/A'

        # Revertir para solo devolver el texto crudo
        precios = {
            'precio_pergamino': precio_pergamino_carga,
            'precio_pasilla': precio_pasilla_arroba,
            'tasa_cambio': tasa_cambio_valor,
            'fecha_actualizacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S') # O intentar extraer la fecha de la web
        }

        return jsonify(precios), 200

    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Error al obtener datos de la Federación: {e}'}), 500
    except Exception as e:
        # Log the full traceback for debugging
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': f'Error al parsear datos: {e}'}), 500

# Nueva ruta para exportar reportes de ventas a PDF para campesinos
@ventas_bp.route('/campesino/exportar_reportes_pdf', methods=['GET'])
@jwt_required()
def exportar_reportes_campesino_pdf():
    current_user_id = get_jwt_identity()
    campesino = Usuario.query.get(current_user_id)

    if not campesino or campesino.tipo != 'campesino':
        return jsonify({'msg': 'Acceso denegado'}), 403

    periodo = request.args.get('periodo', 'Último mes')

    # Calcular el rango de fechas basado en el período
    fecha_fin = datetime.utcnow()
    fecha_inicio = None

    if periodo == 'Último mes':
        fecha_inicio = fecha_fin - timedelta(days=30) # Aproximación de 30 días para último mes
    elif periodo == 'Últimos 3 meses':
        fecha_inicio = fecha_fin - timedelta(days=90) # Aproximación de 90 días para 3 meses
    elif periodo == 'Último año':
        fecha_inicio = fecha_fin - timedelta(days=365) # Aproximación de 365 días para último año
    # Si el período no coincide con ninguno, podríamos devolver un error o usar un rango por defecto

    if not fecha_inicio:
         return jsonify({'error': 'Período no válido'}), 400

    try:
        # Obtener las ventas del campesino para el período, ordenadas por fecha
        ventas = Venta.query.filter(
            Venta.campesino_id == campesino.id,
            Venta.fecha >= fecha_inicio,
            Venta.fecha <= fecha_fin
        ).options(db.joinedload(Venta.empresa)).order_by(Venta.fecha.asc()).all()

        if not ventas:
            return jsonify({'message': 'No hay información disponible para generar el reporte en este período.'}), 404 # Código 404 Not Found es apropiado aquí

        # Si hay ventas, proceder a generar el PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        # Estilo para el título
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import Paragraph
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='ReportTitle', fontSize=16, spaceAfter=14, alignment=1, bold=1))
        styles.add(ParagraphStyle(name='InfoStyle', fontSize=10, spaceAfter=6))

        # Título del reporte
        elements.append(Paragraph(f'Reporte de Ventas - {periodo} ({campesino.nombre})', styles['ReportTitle']))

        # Información del Campesino
        elements.append(Paragraph(f'Finca: {campesino.direccion_finca}', styles['InfoStyle']))
        elements.append(Paragraph(f"Fecha de Generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['InfoStyle']))
        elements.append(Spacer(1, 0.2*inch))

        # Calcular estadísticas de resumen
        total_ventas_periodo = sum(venta.total for venta in ventas) if ventas else 0
        total_cantidad_periodo = sum(venta.cantidad for venta in ventas) if ventas else 0

        precio_promedio_periodo = (total_ventas_periodo / total_cantidad_periodo) if total_cantidad_periodo > 0 else 0

        # Añadir estadísticas de resumen al PDF
        elements.append(Paragraph(f'Total Ventas ({periodo}): {total_ventas_periodo:,.0f} COP', styles['InfoStyle']))
        elements.append(Paragraph(f'Precio Promedio ({periodo}): {precio_promedio_periodo:,.0f} COP/kg', styles['InfoStyle']))
        elements.append(Spacer(1, 0.2*inch))

        # Preparar datos para la tabla
        data = [['Fecha', 'Tipo Café', 'Cantidad (kg)', 'Precio/kg (COP)', 'Total (COP)', 'Comprador', 'Estado']]
        for venta in ventas:
            data.append([
                venta.fecha.strftime('%Y-%m-%d') if venta.fecha else '',
                venta.tipo_cafe.value if venta.tipo_cafe else '',
                f'{venta.cantidad:.2f}' if venta.cantidad is not None else '',
                f'{venta.precio_kg:,.0f}' if venta.precio_kg is not None else '',
                f'{venta.total:,.0f}' if venta.total is not None else '',
                venta.empresa.nombre if venta.empresa else 'CafExport',
                venta.estado.value if venta.estado else ''
            ])

        # Crear la tabla y aplicar estilos
        table = Table(data)
        style = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.Color(0.08, 0.44, 0.25, 1)), # Un verde oscuro similar al sidebar
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

        # Añadir la tabla a los elementos del documento
        elements.append(table)

        # Generar gráfico de ventas por tipo de café
        ventas_por_tipo = {}
        for venta in ventas:
            tipo = venta.tipo_cafe.value if venta.tipo_cafe else 'Desconocido'
            ventas_por_tipo[tipo] = ventas_por_tipo.get(tipo, 0) + (float(venta.total) if venta.total is not None else 0)

        if ventas_por_tipo:
            fig1, ax1 = plt.subplots()
            labels = ventas_por_tipo.keys()
            sizes = ventas_por_tipo.values()
            ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=['#16a34a', '#86efac', '#dcfce7', '#34d399'])
            ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

            # Guardar gráfico en buffer
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png')
            img_buffer.seek(0)
            plt.close(fig1) # Cerrar la figura para liberar memoria

            # Añadir gráfico al PDF
            elements.append(Spacer(1, 0.4*inch))
            elements.append(Paragraph('Ventas por Tipo de Café', styles['ReportTitle'])) # Título para el gráfico
            img = Image(img_buffer)
            # Ajustar tamaño de la imagen si es necesario
            img.drawWidth = 4*inch
            img.drawHeight = 4*inch
            elements.append(img)

        # Construir el PDF
        doc.build(elements)

        # Obtener el contenido del PDF desde el buffer
        pdf_content = buffer.getvalue()
        buffer.close()

        # Configurar y enviar la respuesta HTTP con el PDF
        from flask import make_response
        response = make_response(pdf_content)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f"attachment; filename=reporte_ventas_campesino_{periodo.replace(' ', '_').lower()}.pdf"
        response.headers['Access-Control-Expose-Headers'] = 'Content-Disposition' # Exponer header para que JS pueda leer el nombre del archivo

        return response, 200

    except Exception as e:
        import traceback
        print("ERROR IN exportar_reportes_campesino_pdf:")
        traceback.print_exc()
        return jsonify({'error': f'Error interno al generar el reporte PDF: {e}'}), 500

# Nueva ruta para descargar factura de venta específica
@ventas_bp.route('/ventas/<int:venta_id>/factura', methods=['GET', 'OPTIONS'])
@jwt_required()
def descargar_factura_venta(venta_id):
    # Manejar solicitudes OPTIONS para CORS preflight
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    current_user_id = get_jwt_identity()
    campesino = Usuario.query.get(current_user_id)

    if not campesino or campesino.tipo != 'campesino':
        return jsonify({'msg': 'Acceso denegado'}), 403

    try:
        # Obtener la venta específica y verificar que pertenezca al campesino autenticado
        venta = Venta.query.filter_by(id=venta_id, campesino_id=campesino.id).options(db.joinedload(Venta.empresa)).first()

        if not venta:
            return jsonify({'message': 'Factura no encontrada o no tienes permiso para descargarla.'}), 404

        # Si la venta existe y pertenece al usuario, generar el PDF de la factura
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        # Estilos
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='FacturaTitle', fontSize=18, spaceAfter=20, alignment=1, bold=1))
        styles.add(ParagraphStyle(name='SectionTitle', fontSize=14, spaceAfter=10, bold=1))
        styles.add(ParagraphStyle(name='InfoText', fontSize=10, spaceAfter=5))

        # Título de la Factura
        elements.append(Paragraph(f'Factura de Venta #{venta.id}', styles['FacturaTitle']))

        # Información del Vendedor (Campesino)
        elements.append(Paragraph('Información del Vendedor (Campesino):', styles['SectionTitle']))
        elements.append(Paragraph(f'Nombre: {campesino.nombre}', styles['InfoText']))
        elements.append(Paragraph(f'Finca: {campesino.direccion_finca if campesino.direccion_finca else "N/A"}', styles['InfoText']))
        elements.append(Paragraph(f'Cédula: {campesino.cedula if campesino.cedula else "N/A"}', styles['InfoText']))
        elements.append(Spacer(1, 0.2*inch))

        # Información del Comprador (CafExport)
        elements.append(Paragraph('Información del Comprador:', styles['SectionTitle']))
        # Asumo que CafExport es una entidad fija o representada de alguna manera
        elements.append(Paragraph('Nombre Empresa: CafExport', styles['InfoText']))
        # Puedes añadir más detalles de CafExport si están disponibles en tu modelo de usuario o configuración
        elements.append(Spacer(1, 0.2*inch))

        # Detalles de la Venta
        elements.append(Paragraph('Detalles de la Venta:', styles['SectionTitle']))
        data = [
            ['Concepto', 'Cantidad (kg)', 'Precio/kg (COP)', 'Total (COP)']
        ]
        data.append([
            f'Venta de {venta.tipo_cafe.value if venta.tipo_cafe else "Café"}',
            f'{venta.cantidad:.2f}' if venta.cantidad is not None else '',
            f'{venta.precio_kg:,.0f}' if venta.precio_kg is not None else '',
            f'{venta.total:,.0f}' if venta.total is not None else ''
        ])

        table = Table(data)
        style = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.Color(0.08, 0.44, 0.25, 1)), # Verde oscuro
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.beige),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ])
        table.setStyle(style)
        elements.append(table)

        elements.append(Spacer(1, 0.2*inch))

        # Total de la Factura
        elements.append(Paragraph(f"<b>Total Factura:</b> {venta.total:,.0f} COP", styles['InfoText']))
        elements.append(Paragraph(f"Fecha de Venta: {venta.fecha.strftime('%Y-%m-%d') if venta.fecha else 'N/A'}", styles['InfoText']))

        # Construir el PDF
        doc.build(elements)

        # Obtener el contenido del PDF y enviarlo
        pdf_content = buffer.getvalue()
        buffer.close()

        from flask import make_response
        response = make_response(pdf_content)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=factura_venta_{venta.id}.pdf'
        response.headers['Access-Control-Expose-Headers'] = 'Content-Disposition' # Exponer header

        return response, 200

    except Exception as e:
        import traceback
        print("ERROR IN descargar_factura_venta:")
        traceback.print_exc()
        return jsonify({'error': f'Error interno al generar la factura: {e}'}), 500 