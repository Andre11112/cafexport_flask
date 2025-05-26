from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, Venta, Usuario # Asegúrate que Venta y Usuario estén definidos en models.py
from datetime import datetime
import requests
from bs4 import BeautifulSoup # Importar BeautifulSoup
# import re # No necesitamos re si no limpiamos números

ventas_bp = Blueprint('ventas', __name__)

@ventas_bp.route('/ventas', methods=['POST'])
@jwt_required() # Protege esta ruta para que solo usuarios autenticados puedan acceder
def registrar_venta():
    current_user_id = get_jwt_identity() # Obtiene el ID del usuario del token JWT
    campesino = Usuario.query.get(current_user_id)

    if not campesino or campesino.tipo != 'campesino':
        return jsonify({'msg': 'Acceso denegado'}), 403

    data = request.get_json()

    if not data or not all(k in data for k in ('cantidad', 'tipo_cafe', 'precio_kg')):
        return jsonify({'error': 'Datos incompletos'}), 400

    try:
        cantidad = float(data['cantidad'])
        precio_kg = float(data['precio_kg'])
        tipo_cafe = data['tipo_cafe']
        # Puedes añadir validación adicional aquí si es necesario (ej. cantidad > 0)

        total = cantidad * precio_kg

        nueva_venta = Venta(
            fecha=datetime.now(),
            comprador='Pendiente', # O podrías obtener el comprador de los datos si el flujo lo permite
            tipo_cafe=tipo_cafe,
            cantidad=cantidad,
            precio_kg=precio_kg,
            total=total,
            estado='Pendiente', # Estado inicial de la venta
            campesino_id=campesino.id
        )

        db.session.add(nueva_venta)
        db.session.commit()

        return jsonify({
            'mensaje': 'Venta registrada con éxito',
            'venta': {
                'id': nueva_venta.id,
                'fecha': nueva_venta.fecha.strftime('%Y-%m-%d %H:%M:%S'),
                'comprador': nueva_venta.comprador,
                'tipo_cafe': nueva_venta.tipo_cafe,
                'cantidad': nueva_venta.cantidad,
                'precio_kg': nueva_venta.precio_kg,
                'total': nueva_venta.total,
                'estado': nueva_venta.estado,
                'campesino_id': nueva_venta.campesino_id
            }
        }), 201

    except ValueError:
        return jsonify({'error': 'Cantidad o precio_kg deben ser números válidos'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

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