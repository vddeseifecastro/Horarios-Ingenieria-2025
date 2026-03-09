# backend/database.py - SOLO MODELOS
from datetime import datetime

# Clases de modelos (sin inicialización de db aquí)
class Usuario:
    def __init__(self, id=None, username=None, email=None, password=None, role='user', activo=True):
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
        return str(self.id) if self.id else None
    
    def is_authenticated(self):
        return True
    
    def is_anonymous(self):
        return False

# Solo definiciones de estructura para referencia
# Los modelos reales estarán en app.py