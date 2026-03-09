import os
from datetime import timedelta
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_DIR = os.path.join(BASE_DIR, 'database')
DATABASE_PATH = os.path.join(DATABASE_DIR, 'horarios.db')

os.makedirs(DATABASE_DIR, exist_ok=True)

class Config:
    # Seguridad: clave desde variable de entorno, nunca hardcodeada
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise RuntimeError(
            "\n\n[ERROR] SECRET_KEY no está definida.\n"
            "Crea un archivo .env en la raíz del proyecto con:\n"
            "  SECRET_KEY=tu-clave-secreta-aqui\n"
        )

    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)

    TURNOS_MANANA = [
        {'id': 1, 'nombre': 'Mañana 1', 'hora_inicio': '08:15', 'hora_fin': '09:45'},
        {'id': 2, 'nombre': 'Mañana 2', 'hora_inicio': '09:50', 'hora_fin': '11:20'},
        {'id': 3, 'nombre': 'Mañana 3', 'hora_inicio': '11:35', 'hora_fin': '13:05'}
    ]

    TURNOS_TARDE = [
        {'id': 4, 'nombre': 'Tarde 1', 'hora_inicio': '13:10', 'hora_fin': '14:40'},
        {'id': 5, 'nombre': 'Tarde 2', 'hora_inicio': '14:45', 'hora_fin': '16:15'},
        {'id': 6, 'nombre': 'Tarde 3', 'hora_inicio': '16:30', 'hora_fin': '18:00'}
    ]

    @staticmethod
    def mostrar_rutas():
        print("📍 RUTAS CONFIGURADAS:")
        print(f"   Base Directory: {BASE_DIR}")
        print(f"   Database Path:  {DATABASE_PATH}")
        print(f"   Database Exists: {os.path.exists(DATABASE_PATH)}")

if __name__ == '__main__':
    Config.mostrar_rutas()