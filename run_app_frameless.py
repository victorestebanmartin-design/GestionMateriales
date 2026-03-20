"""
Ejecuta la aplicación de Gestión de Materiales en una ventana nativa
SIN BORDES - Para una apariencia más moderna y limpia
"""
import webview
import threading
import time
import socket
from app import app, init_db

def get_local_ip():
    """Obtiene la IP local del equipo"""
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return local_ip
    except:
        return "localhost"

def start_flask():
    """Inicia el servidor Flask en un thread separado"""
    print("🚀 Iniciando servidor Flask...")
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

def main():
    """Función principal que inicia la aplicación en ventana sin bordes"""
    print(f"{'='*60}")
    print(f"🚀 GESTIÓN DE MATERIALES - MODO VENTANA SIN BORDES")
    print(f"{'='*60}")
    
    # Iniciar Flask en un thread separado
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()
    
    # Esperar a que Flask esté listo
    print("⏳ Esperando a que el servidor esté listo...")
    time.sleep(2)
    
    local_ip = get_local_ip()
    print(f"🌐 Servidor ejecutándose:")
    print(f"   - Local: http://localhost:5000")
    print(f"   - Red local: http://{local_ip}:5000")
    print(f"{'='*60}")
    print("✅ Abriendo aplicación en ventana sin bordes...")
    print("⚠️  Para cerrar: presiona Ctrl+W o cierra esta consola")
    print(f"{'='*60}\n")
    
    # Crear ventana nativa sin bordes (frameless) - apariencia moderna
    window = webview.create_window(
        title='Gestión de Materiales',
        url='http://localhost:5000',
        width=1400,        # Ancho inicial
        height=900,        # Alto inicial
        resizable=True,    # Permite redimensionar
        frameless=True,    # SIN bordes de ventana
        easy_drag=True     # Permite arrastrar la ventana desde cualquier lugar
    )
    
    # Iniciar la ventana (esto es bloqueante)
    webview.start()
    
    print("\n👋 Aplicación cerrada")

if __name__ == '__main__':
    main()
