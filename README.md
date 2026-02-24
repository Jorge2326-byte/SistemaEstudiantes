# SistemaEstudiantes — Mini CRUD con Flask, MySQL y Jinja2

## Requisitos
- Python 3.10+ (probado hasta 3.12)
- MySQL (XAMPP es válido)
- Pip para instalar dependencias

## Instalación
```bash
# 1) Crear y activar entorno (opcional pero recomendado)
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 2) Instalar dependencias
pip install -r requirements.txt

# 3) Crear base de datos
# Abre MySQL/PhpMyAdmin y ejecuta:
#   (puedes pegar el contenido de schema.sql)
```

## Variables de conexión (opcional)
Puedes definir variables de entorno si tu configuración difiere:
```
DB_HOST, DB_USER, DB_PASS, DB_NAME, DB_PORT
```
Por defecto:
```
host=localhost, user=root, password="", database=sistema_estudiantes, port=3306
```

## Ejecutar
```bash
python app.py
# Visita: http://127.0.0.1:5000
```

## Estructura
```
SistemaEstudiantes/
├─ app.py
├─ requirements.txt
├─ schema.sql
└─ templates/
   ├─ base.html
   ├─ index.html
   ├─ create.html
   └─ edit.html
```

## Notas
- Los mensajes de validación usan `flash`, por eso `app.secret_key` debe tener un valor seguro en producción.
- La ruta `/delete/<id>` requiere método POST y una confirmación en el navegador.
```