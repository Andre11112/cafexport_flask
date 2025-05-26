import subprocess
import sys
import os
import time
import webbrowser
import logging
import requests
from requests.exceptions import ConnectionError

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def kill_process_on_port(port):
    """Mata el proceso que está usando un puerto específico"""
    try:
        cmd = f'for /f "tokens=5" %%a in (\'netstat -aon ^| find ":{port}" ^| find "LISTENING"\') do taskkill /F /PID %%a'
        subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(1)
        return True
    except Exception as e:
        logger.error(f"Error al matar proceso en puerto {port}: {e}")
        return False

def wait_for_server(url, timeout=30):
    """Espera hasta que el servidor esté disponible"""
    start_time = time.time()
    logger.info(f"Esperando respuesta de {url}")
    
    while True:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                logger.info(f"✅ Servidor en {url} respondió correctamente")
                return True
        except requests.exceptions.ConnectionError:
            if time.time() - start_time > timeout:
                logger.error(f"❌ Tiempo de espera agotado para {url}")
                return False
            time.sleep(2)
            continue

def run_backend():
    """Inicia el servidor backend"""
    try:
        # Limpiar puerto 5000
        kill_process_on_port(5000)
        
        # Iniciar backend como módulo
        project_root = os.path.dirname(os.path.abspath(__file__))
        backend_module_path = 'backend.app' # Usamos el nombre del módulo
        
        # Iniciar el proceso del backend
        process = subprocess.Popen(
            [sys.executable, '-m', backend_module_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            cwd=project_root
        )
        
        # Esperar a que el backend esté listo
        if wait_for_server('http://127.0.0.1:5000/api/health'):
            logger.info("✅ Backend iniciado correctamente en http://127.0.0.1:5000")
            return process
        else:
            logger.error("❌ El backend no respondió al health check")
            process.terminate()
            return None
            
    except Exception as e:
        logger.error(f"❌ Error al iniciar backend: {str(e)}")
        return None

def run_frontend():
    """Inicia el servidor frontend"""
    try:
        # Limpiar puerto 5001
        kill_process_on_port(5001)
        
        # Iniciar frontend
        frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend')
        app_path = os.path.join(frontend_dir, 'app.py')
        
        if not os.path.exists(app_path):
            logger.error(f"❌ No se encuentra el archivo {app_path}")
            return None
        
        logger.info("🚀 Iniciando frontend...")
        process = subprocess.Popen(
            [sys.executable, app_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            cwd=frontend_dir
        )
        
        # Esperar a que el frontend esté listo
        if wait_for_server('http://127.0.0.1:5001/health'):
            logger.info("✅ Frontend iniciado correctamente en http://127.0.0.1:5001")
            return process
        else:
            logger.error("❌ El frontend no respondió al health check")
            process.terminate()
            return None
            
    except Exception as e:
        logger.error(f"❌ Error al iniciar frontend: {str(e)}")
        return None

if __name__ == '__main__':
    logger.info("🚀 Iniciando servicios...")
    
    # Iniciar backend
    backend_process = run_backend()
    if not backend_process:
        sys.exit(1)
    
    time.sleep(2)
    
    # Iniciar frontend
    frontend_process = run_frontend()
    if not frontend_process:
        backend_process.terminate()
        sys.exit(1)
    
    # Abrir navegador
    webbrowser.open('http://localhost:5001')
    
    try:
        # Mantener los procesos corriendo y mostrar sus logs
        while True:
            # Verificar si los procesos siguen vivos
            if backend_process.poll() is not None:
                logger.error("❌ El proceso backend se detuvo")
                frontend_process.terminate()
                break
                
            if frontend_process.poll() is not None:
                logger.error("❌ El proceso frontend se detuvo")
                backend_process.terminate()
                break
            
            # Mostrar logs
            backend_output = backend_process.stdout.readline()
            if backend_output:
                print(f"[Backend] {backend_output.strip()}")
            
            frontend_output = frontend_process.stdout.readline()
            if frontend_output:
                print(f"[Frontend] {frontend_output.strip()}")
            
            time.sleep(0.1)
                
    except KeyboardInterrupt:
        logger.info("\n🛑 Deteniendo servicios...")
        backend_process.terminate()
        frontend_process.terminate()
        sys.exit(0)