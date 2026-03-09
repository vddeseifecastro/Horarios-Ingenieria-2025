#!/usr/bin/env python3
"""
SISTEMA DE HORARIOS - INGENIERÍA INFORMÁTICA
"""

import os
import sys

print("=" * 48)
print("   SISTEMA DE HORARIOS - INGENIERÍA INFORMÁTICA")
print("=" * 48)

# Agregar 'backend' al path de Python
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Crear carpetas necesarias
carpetas = ['database', 'uploads/excel', 'uploads/pdf']
for carpeta in carpetas:
    try:
        os.makedirs(carpeta, exist_ok=True)
        print(f"✅ Carpeta verificada: {carpeta}")
    except Exception as e:
        print(f"⚠️  Error con carpeta '{carpeta}': {e}")

try:
    print("\n🔍 IMPORTANDO MÓDULOS...")

    import config
    from config import Config
    cfg = Config()
    cfg.mostrar_rutas()

    # Verificar permisos de escritura
    test_file = os.path.join('database', 'test_permissions.txt')
    with open(test_file, 'w') as f:
        f.write('test')
    os.remove(test_file)
    print("✅ Permisos de escritura verificados")

    from app import app, inicializar_base_datos
    print("✅ Módulo 'app' importado")

    print("\n🚀 INICIALIZANDO SISTEMA...")

    with app.app_context():
        inicializar_base_datos()

    print("✅ Base de datos inicializada")
    print("🌐 Servidor listo en: http://localhost:5000")
    print("   (Las credenciales iniciales se imprimen al crear la BD por primera vez)")
    print("=" * 48)

    # debug=False en producción; True solo si DEBUG=1 en .env
    debug_mode = os.environ.get('DEBUG', 'false').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)

except ImportError as e:
    print(f"\n❌ ERROR DE IMPORTACIÓN: {e}")
    print("\n📋 SOLUCIONES:")
    print(f"1. ¿Existe 'backend/config.py'?  {'✅' if os.path.exists(os.path.join(backend_path, 'config.py')) else '❌ NO'}")
    print(f"2. ¿Existe 'backend/__init__.py'? {'✅' if os.path.exists(os.path.join(backend_path, '__init__.py')) else '❌ NO'}")
    print(f"3. ¿Existe '.env' en la raíz?     {'✅' if os.path.exists('.env') else '❌ NO — Crea .env con SECRET_KEY=...'}")
    import traceback
    traceback.print_exc()

except RuntimeError as e:
    # Captura el error de SECRET_KEY faltante con mensaje claro
    print(str(e))

except Exception as e:
    print(f"\n❌ ERROR INESPERADO: {e}")
    import traceback
    traceback.print_exc()