# backend/models.py - VERSIÓN CORREGIDA
from datetime import datetime

# Eliminamos las importaciones problemáticas
# db se inicializará separadamente

class Usuario:
    def __init__(self, id, username, email, password, role, activo=True):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.role = role
        self.activo = activo
        self.fecha_registro = datetime.utcnow()
    
    def is_active(self):
        return self.activo
    
    def get_id(self):
        return str(self.id)
    
    def is_authenticated(self):
        return True
    
    def is_anonymous(self):
        return False

# Mantenemos las definiciones de modelos pero sin SQLAlchemy inicializado aquí
# Esto lo moveremos a otro archivo