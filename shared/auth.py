"""
Módulo compartido para autenticación y sesiones
"""
from flask import session, request, redirect, url_for, flash
from typing import Optional
from .operarios_db import authenticate_operario, get_operario_role, require_role as _require_role

def current_user() -> Optional[str]:
    """Obtiene el usuario actual de la sesión"""
    return session.get("user")

def current_role() -> Optional[str]:
    """Obtiene el rol del usuario actual"""
    user = current_user()
    if user:
        return get_operario_role(user)
    return None

def require_role(allowed_roles: list):
    """Decorator/función para requerir ciertos roles"""
    user = current_user()
    if not user:
        flash("Debes iniciar sesión para acceder.", "error")
        return False
    
    if not _require_role(allowed_roles, user):
        flash("No tienes permisos para realizar esta acción.", "error") 
        return False
    
    return True

def login_operario(numero: str, pin: str = None) -> bool:
    """Inicia sesión de un operario"""
    if authenticate_operario(numero, pin):
        session["user"] = numero
        session.permanent = True
        return True
    return False

def logout_operario():
    """Cierra sesión del operario"""
    session.pop("user", None)

def is_logged_in() -> bool:
    """Verifica si hay un usuario logueado"""
    return current_user() is not None