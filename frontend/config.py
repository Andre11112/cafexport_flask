import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Configuración general
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-1234')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # URLs base de la API
    API_URL = os.getenv('API_URL', 'http://127.0.0.1:5000')
    
    # Endpoints específicos de la API
    # Usar API_URL para construir las URLs completas
    API_ENDPOINTS = {
        # Autenticación
        'registro_campesino': f'{API_URL}/api/campesino/registro',
        'registro_empresa': f'{API_URL}/api/empresa/registro',
        'login_campesino': f'{API_URL}/api/campesino/login',
        'login_empresa': f'{API_URL}/api/empresa/login',
        
        # Campesino
        'dashboard_campesino': f'{API_URL}/api/campesino/dashboard',
        'perfil_campesino': f'{API_URL}/api/campesino/perfil',
        'ventas_campesino': f'{API_URL}/api/campesino/ventas',
        'productos_campesino': f'{API_URL}/api/campesino/productos',
        
        # Empresa
        'dashboard_empresa': f'{API_URL}/api/empresa/dashboard',
        'perfil_empresa': f'{API_URL}/api/empresa/perfil',
        'compras_empresa': f'{API_URL}/api/empresa/compras',
        'reportes_empresa': f'{API_URL}/empresa/reportes_empresa',
    }
    
    # Configuración de templates
    TEMPLATES_AUTO_RELOAD = True
    
    # Configuración de sesión
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hora

    @staticmethod
    def init_app(app):
        pass

# Crear una instancia de Config que se pueda importar directamente si es necesario
config = Config()

# Exportar API_URL directamente para facilitar su uso en otros módulos si es necesario
API_URL = Config.API_URL