from flask import session
import requests
from config import Config

def get_user_data():
    """Obtiene los datos del usuario de la sesión"""
    return session.get('user', None)

def make_api_request(method, endpoint, data=None, timeout=5):
    """
    Helper para hacer peticiones a la API
    
    Args:
        method (str): GET, POST, PUT, DELETE
        endpoint (str): Endpoint de la API
        data (dict): Datos a enviar en la petición
        timeout (int): Tiempo máximo de espera en segundos
    
    Returns:
        tuple: (response_data, error_message)
    """
    try:
        url = f"{Config.API_URL}{endpoint}"
        
        if method == 'GET':
            response = requests.get(url, timeout=timeout)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=timeout)
        elif method == 'PUT':
            response = requests.put(url, json=data, timeout=timeout)
        elif method == 'DELETE':
            response = requests.delete(url, timeout=timeout)
            
        if response.status_code in [200, 201]:
            return response.json(), None
        else:
            return None, response.json().get('error', 'Error en la petición')
            
    except requests.exceptions.ConnectionError:
        return None, 'Error de conexión con el servidor'
    except requests.exceptions.Timeout:
        return None, 'El servidor está tardando demasiado en responder'
    except Exception as e:
        return None, str(e)

def format_currency(amount):
    """Formatea un número como moneda colombiana"""
    try:
        return f"${amount:,.0f} COP"
    except:
        return "N/A"

def format_date(date_str):
    """Formatea una fecha en formato legible"""
    try:
        from datetime import datetime
        date = datetime.fromisoformat(date_str)
        return date.strftime('%d/%m/%Y')
    except:
        return date_str