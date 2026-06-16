#!/bin/bash

set -e

echo "======================================"
echo "  HealthAnalytics IPS - Starting up  "
echo "======================================"

# Esperar a que la base de datos esté lista
echo "[INFO] Esperando conexión a la base de datos..."
until python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.db import connection
connection.ensure_connection()
print('DB conectada.')
" 2>/dev/null; do
  echo "[WAIT] Base de datos no disponible, reintentando en 2s..."
  sleep 2
done

echo "[OK] Base de datos disponible."

# Ejecutar migraciones
echo "[INFO] Aplicando migraciones..."
python manage.py migrate --noinput

# Crear superusuario si no existe
echo "[INFO] Verificando superusuario..."
python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@healthanalytics.com',
        password='Admin1234!',
        rol='Administrador'
    )
    print("Superusuario creado: admin / Admin1234!")
else:
    print("Superusuario ya existe.")
EOF

echo "[OK] Inicialización completada."
echo "[INFO] Iniciando servidor Gunicorn en 0.0.0.0:8000..."

exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --access-logfile /app/logs/access.log \
    --error-logfile /app/logs/error.log \
    --log-level info