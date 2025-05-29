from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, Venta, Usuario # Asegúrate que Venta y Usuario estén definidos en models.py
from datetime import datetime
import requests
from bs4 import BeautifulSoup # Importar BeautifulSoup

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
        for venta in ventas:
            ventas_data.append({
                'id': venta.id,
                'fecha': venta.fecha.strftime('%Y-%m-%d %H:%M:%S') if venta.fecha else None, # Formatear fecha si existe
                'tipo_cafe': venta.tipo_cafe.value if venta.tipo_cafe else None, # Asumiendo que tipo_cafe es un Enum
                'cantidad': float(venta.cantidad) if venta.cantidad is not None else None,
                'precio_kg': float(venta.precio_kg) if venta.precio_kg is not None else None,
                'total': float(venta.total) if venta.total is not None else None, # Total es generado, debería existir
                'estado': venta.estado.value if venta.estado else None, # Asumiendo que estado es un Enum
                'comprador': venta.empresa.nombre if venta.empresa else 'CafExport' # Obtener nombre de la empresa o usar CafExport
            })

        return jsonify(ventas_data), 200

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