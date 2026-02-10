"""
Módulo compartido para gestión de operarios
Funciones comunes entre aplicaciones de materiales y herramientas
"""
import sqlite3
from typing import Optional, List, Dict, Any
from datetime import datetime

def get_operarios_db():
    """Obtiene conexión a la base de datos de operarios"""
    return sqlite3.connect("database/operarios.db")

def get_operario(numero: str) -> Optional[Dict[str, Any]]:
    """Obtiene un operario por número"""
    try:
        with get_operarios_db() as conn:
            c = conn.cursor()
            c.execute("SELECT numero, nombre, pin, activo FROM operarios WHERE numero=?", (numero,))
            row = c.fetchone()
            if row:
                return {
                    'numero': row[0],
                    'nombre': row[1], 
                    'pin': row[2],
                    'activo': bool(row[3])
                }
    except:
        pass
    return None

def get_all_operarios(solo_activos: bool = True) -> List[Dict[str, Any]]:
    """Obtiene todos los operarios"""
    try:
        with get_operarios_db() as conn:
            c = conn.cursor()
            if solo_activos:
                c.execute("SELECT numero, nombre, pin, activo FROM operarios WHERE activo=1 ORDER BY numero")
            else:
                c.execute("SELECT numero, nombre, pin, activo FROM operarios ORDER BY numero")
            
            operarios = []
            for row in c.fetchall():
                operarios.append({
                    'numero': row[0],
                    'nombre': row[1],
                    'pin': row[2], 
                    'activo': bool(row[3])
                })
            return operarios
    except:
        pass
    return []

def authenticate_operario(numero: str, pin: str = None) -> bool:
    """Autentica un operario por número y pin (opcional)"""
    operario = get_operario(numero)
    if not operario or not operario['activo']:
        return False
    
    # Si el operario tiene pin configurado, debe proporcionarlo
    if operario['pin']:
        return operario['pin'] == pin
    
    # Si no tiene pin, solo verificar que existe y está activo
    return True

def get_operario_role(numero: str) -> str:
    """Obtiene el rol de un operario basado en su número"""
    if numero == "admin":
        return "admin"
    elif numero == "almacen":
        return "almacenero" 
    else:
        return "operario"

def require_role(allowed_roles: List[str], current_numero: str) -> bool:
    """Verifica si el operario actual tiene uno de los roles permitidos"""
    if not current_numero:
        return False
    
    current_role = get_operario_role(current_numero)
    return current_role in allowed_roles