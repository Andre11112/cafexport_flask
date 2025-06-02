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
        # Permitir solicitudes OPTIONS sin verificar JWT
        if request.method == 'OPTIONS':
            # Dejar que el siguiente decorador o la función maneje la respuesta OPTIONS
            return fn(*args, **kwargs)

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
        print(f"Obteniendo estadísticas para empresa_id: {current_user_id}")  # Debug

        total_compras_cantidad = db.session.query(func.sum(CompraEmpresa.cantidad))\
            .filter_by(empresa_id=current_user_id).scalar() or 0
        total_inversion = db.session.query(func.sum(CompraEmpresa.total))\
            .filter_by(empresa_id=current_user_id).scalar() or 0
        total_compras_count = db.session.query(func.count(CompraEmpresa.id))\
            .filter_by(empresa_id=current_user_id).scalar() or 0

        # Calcular conteos por estado
        completadas_count = db.session.query(func.count(CompraEmpresa.id))\
            .filter_by(empresa_id=current_user_id, estado=EstadoCompraEnum.Completada).scalar() or 0
        pendientes_count = db.session.query(func.count(CompraEmpresa.id))\
            .filter_by(empresa_id=current_user_id, estado=EstadoCompraEnum.Pendiente).scalar() or 0
        confirmadas_count = db.session.query(func.count(CompraEmpresa.id))\
            .filter_by(empresa_id=current_user_id, estado=EstadoCompraEnum.Confirmadas).scalar() or 0

        # Calcular precio promedio por kg
        precio_promedio = (float(total_inversion) / float(total_compras_cantidad)) if float(total_compras_cantidad) > 0 else 0.0

        # Obtener la próxima entrega (suponiendo que es la fecha de entrega más cercana)
        proxima_entrega = db.session.query(func.min(CompraEmpresa.fecha_entrega))\
            .filter(CompraEmpresa.empresa_id == current_user_id, CompraEmpresa.fecha_entrega != None).scalar()

        # Calcular días restantes hasta la próxima entrega
        if proxima_entrega:
            dias_restantes = (proxima_entrega - datetime.now()).days
            proxima_entrega_str = proxima_entrega.strftime('%d %B, %Y')
        else:
            dias_restantes = None
            proxima_entrega_str = None

        estadisticas = {
            'total_compras_cantidad': float(total_compras_cantidad),
            'total_inversion': float(total_inversion),
            'total_compras_count': total_compras_count,
            'completadas_count': completadas_count,
            'pendientes_count': pendientes_count,
            'confirmadas_count': confirmadas_count,
            'precio_promedio': precio_promedio,
            'proxima_entrega': {
                'fecha': proxima_entrega_str,
                'dias': dias_restantes
            }
        }

        print(f"Estadísticas calculadas: {estadisticas}")  # Debug
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
        print(f"Error interno al procesar precios de café: {e}")
        return jsonify({'message': 'Error interno al procesar precios de café'}), 500

# Nueva ruta para descargar la factura de una compra específica
@compra_bp.route('/compras/<int:compra_id>/factura', methods=['GET', 'OPTIONS'])
@jwt_required()
@empresa_required
def descargar_factura_compra(compra_id):
     # Manejar solicitudes OPTIONS para CORS preflight
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    current_user_id = get_jwt_identity()
    empresa = Usuario.query.get(current_user_id)

    # Asegurarse de que la compra pertenezca a la empresa loggeada
    compra = CompraEmpresa.query.filter_by(id=compra_id, empresa_id=empresa.id).first()

    if not compra:
        return jsonify({'message': 'Compra no encontrada o no pertenece a esta empresa'}), 404

    try:
        # Importaciones para PDF (ReportLab)
        import io
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from datetime import datetime
        
        # Buffer para el PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        # Estilos
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='InvoiceTitle', fontSize=18, spaceAfter=18, alignment=1, bold=1))
        styles.add(ParagraphStyle(name='HeaderInfo', fontSize=10, spaceAfter=6))
        styles.add(ParagraphStyle(name='SectionTitle', fontSize=12, spaceAfter=8, bold=1))
        styles.add(ParagraphStyle(name='DetailText', fontSize=10, spaceAfter=4))

        # Información de la Factura
        elements.append(Paragraph('Factura de Compra', styles['InvoiceTitle']))
        elements.append(Paragraph(f'Factura No. {compra.id}', styles['HeaderInfo']))
        elements.append(Paragraph(f'Fecha de Orden: {compra.fecha_orden.strftime("%Y-%m-%d") if compra.fecha_orden else "N/A"}', styles['HeaderInfo']))
        elements.append(Paragraph(f'Fecha de Emisión: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', styles['HeaderInfo']))
        elements.append(Spacer(1, 0.3*inch))

        # Información de la Empresa (Comprador)
        elements.append(Paragraph('Comprador:', styles['SectionTitle']))
        elements.append(Paragraph(f'Empresa: {empresa.nombre}', styles['DetailText']))
        # Asumiendo que el modelo Usuario tiene campos como direccion, ciudad, etc.
        # elements.append(Paragraph(f'Dirección: {empresa.direccion}', styles['DetailText']))
        # elements.append(Paragraph(f'Ciudad: {empresa.ciudad}', styles['DetailText']))
        elements.append(Spacer(1, 0.2*inch))

        # Información del Vendedor
        vendedor_nombre = compra.cafexport_vendedor.nombre if compra.cafexport_vendedor else 'N/A'
        elements.append(Paragraph('Vendedor:', styles['SectionTitle']))
        elements.append(Paragraph(f'Nombre: {vendedor_nombre}', styles['DetailText']))
        # Asumiendo que el modelo Usuario tiene campos como direccion, ciudad, etc.
        # elements.append(Paragraph(f'Dirección: {compra.cafexport_vendedor.direccion}', styles['DetailText']))
        # elements.append(Paragraph(f'Ciudad: {compra.cafexport_vendedor.ciudad}', styles['DetailText']))
        elements.append(Spacer(1, 0.3*inch))

        # Detalles de la Compra (Tabla)
        elements.append(Paragraph('Detalle de la Compra:', styles['SectionTitle']))
        data = [
            ['Tipo Café', 'Cantidad (kg)', 'Precio/kg (COP)', 'Total (COP)', 'Estado']
        ]
        data.append([
             compra.tipo_cafe.value if compra.tipo_cafe else 'N/A',
             f'{compra.cantidad:.2f}' if compra.cantidad is not None else 'N/A',
             f'{compra.precio_kg:,.0f}' if compra.precio_kg is not None else 'N/A',
             f'{compra.total:,.0f}' if compra.total is not None else 'N/A',
             compra.estado.value if compra.estado else 'N/A'
        ])

        table = Table(data)
        style = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.Color(0.08, 0.44, 0.25, 1)), # Verde oscuro
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.Color(0.95, 0.95, 0.95, 1)), # Gris muy claro para filas impares
             #('BACKGROUND', (0,2), (-1,-1), colors.Color(0.85, 0.95, 0.85, 1)), # Verde claro para filas pares (alternado)
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('BOX', (0,0), (-1,-1), 1, colors.black)
        ])
        table.setStyle(style)
        elements.append(table)

        elements.append(Spacer(1, 0.3*inch))

        # Notas (si existen)
        if compra.notas:
            elements.append(Paragraph('Notas:', styles['SectionTitle']))
            elements.append(Paragraph(compra.notas, styles['DetailText']))
            elements.append(Spacer(1, 0.2*inch))

        # Construir el PDF
        doc.build(elements)

        # Obtener el contenido del PDF y enviarlo
        pdf_content = buffer.getvalue()
        buffer.close()

        from flask import make_response
        response = make_response(pdf_content)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=factura_compra_{compra_id}.pdf'
        response.headers['Access-Control-Expose-Headers'] = 'Content-Disposition' # Exponer header

        return response, 200

    except Exception as e:
        import traceback
        print("ERROR IN descargar_factura_compra:")
        traceback.print_exc()
        return jsonify({'error': f'Error interno al generar la factura PDF de compra: {e}'}), 500 