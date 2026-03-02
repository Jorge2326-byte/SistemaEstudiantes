# -*- coding: utf-8 -*-
"""
SistemaEstudiantes - Mini CRUD con Flask, MySQL y Jinja2
Descripción:
  Aplicación web básica para gestionar estudiantes y cursos:
  - Listar, crear, editar y eliminar estudiantes.
  - Inscribir y desinscribir cursos.
  - Mostrar relaciones entre estudiantes y cursos.
Requisitos: ver requirements.txt
"""

from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
import os

# Inicializar la aplicación Flask
app = Flask(__name__)
app.secret_key = "cambia-esta-clave"  # Cambiar por una clave segura en producción

# Configuración de conexión a MySQL
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASS", ""),
    "database": os.getenv("DB_NAME", "b5ry5yh5mics4u97jcfv"),
    "port": int(os.getenv("DB_PORT", "3306")),
}

# Función para obtener conexión a la base de datos
def get_db_connection():
    """Abre una conexión a MySQL."""
    return mysql.connector.connect(**DB_CONFIG)

# ------------------- RUTAS PRINCIPALES -------------------

@app.route("/")
def index():
    """Listar todos los estudiantes."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, correo FROM estudiantes ORDER BY id DESC")
    estudiantes = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("index.html", estudiantes=estudiantes)


@app.route("/create", methods=["GET", "POST"])
def create():
    """Crear nuevo estudiante."""
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        correo = request.form.get("correo", "").strip()

        if not nombre or not correo:
            flash("Por favor completa todos los campos.")
            return redirect(url_for("create"))

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO estudiantes (nombre, correo) VALUES (%s, %s)",
            (nombre, correo),
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash("Estudiante creado correctamente.")
        return redirect(url_for("index"))

    return render_template("create.html")


@app.route("/edit/<int:estudiante_id>", methods=["GET", "POST"])
def edit(estudiante_id):
    """Editar estudiante existente."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, correo FROM estudiantes WHERE id=%s", (estudiante_id,))
    estudiante = cursor.fetchone()

    if estudiante is None:
        cursor.close()
        conn.close()
        flash("Estudiante no encontrado.")
        return redirect(url_for("index"))

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        correo = request.form.get("correo", "").strip()

        if not nombre or not correo:
            flash("Por favor completa todos los campos.")
            cursor.close()
            conn.close()
            return redirect(url_for("edit", estudiante_id=estudiante_id))

        cursor.execute(
            "UPDATE estudiantes SET nombre=%s, correo=%s WHERE id=%s",
            (nombre, correo, estudiante_id),
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash("Estudiante actualizado correctamente.")
        return redirect(url_for("index"))

    cursor.close()
    conn.close()
    return render_template("edit.html", estudiante=estudiante)


@app.route("/delete/<int:estudiante_id>", methods=["POST"])
def delete(estudiante_id):
    """Eliminar estudiante."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM estudiantes WHERE id=%s", (estudiante_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Estudiante eliminado.")
    return redirect(url_for("index"))

# ------------------- RUTAS DE CURSOS -------------------

@app.route("/cursos")
def listar_cursos():
    """Listar todos los cursos disponibles."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, codigo, creditos FROM cursos ORDER BY nombre")
    cursos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("lista_cursos.html", cursos=cursos)


@app.route("/estudiante/<int:estudiante_id>/cursos")
def cursos_estudiante(estudiante_id):
    """Mostrar cursos inscritos y disponibles para un estudiante."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, nombre FROM estudiantes WHERE id=%s", (estudiante_id,))
    estudiante = cursor.fetchone()

    if estudiante is None:
        cursor.close()
        conn.close()
        flash("Estudiante no encontrado.")
        return redirect(url_for("index"))

    # Cursos en los que está inscrito
    cursor.execute('''
        SELECT c.id, c.nombre, c.codigo, c.creditos
        FROM cursos c
        INNER JOIN estudiante_curso ec ON c.id = ec.curso_id
        WHERE ec.estudiante_id = %s
        ORDER BY c.nombre
    ''', (estudiante_id,))
    cursos_inscritos = cursor.fetchall()

    # Cursos disponibles (no inscritos)
    cursor.execute('''
        SELECT c.id, c.nombre, c.codigo, c.creditos
        FROM cursos c
        WHERE c.id NOT IN (
            SELECT curso_id FROM estudiante_curso WHERE estudiante_id = %s
        )
        ORDER BY c.nombre
    ''', (estudiante_id,))
    cursos_disponibles = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "cursos_estudiante.html",
        estudiante=estudiante,
        cursos_inscritos=cursos_inscritos,
        cursos_disponibles=cursos_disponibles
    )


@app.route("/estudiante/<int:estudiante_id>/inscribir/<int:curso_id>", methods=["POST"])
def inscribir_curso(estudiante_id, curso_id):
    """Inscribir estudiante en un curso."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO estudiante_curso (estudiante_id, curso_id) VALUES (%s, %s)",
            (estudiante_id, curso_id)
        )
        conn.commit()
        flash("Estudiante inscrito en el curso correctamente.")
    except mysql.connector.IntegrityError:
        flash("El estudiante ya está inscrito en ese curso.")
    cursor.close()
    conn.close()
    return redirect(url_for("cursos_estudiante", estudiante_id=estudiante_id))


@app.route("/estudiante/<int:estudiante_id>/desinscribir/<int:curso_id>", methods=["POST"])
def desinscribir_curso(estudiante_id, curso_id):
    """Desinscribir estudiante de un curso."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM estudiante_curso WHERE estudiante_id=%s AND curso_id=%s",
        (estudiante_id, curso_id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    flash("Estudiante desinscrito del curso.")
    return redirect(url_for("cursos_estudiante", estudiante_id=estudiante_id))


@app.route("/curso/<int:curso_id>/estudiantes")
def estudiantes_curso(curso_id):
    """Mostrar estudiantes inscritos en un curso."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, nombre, codigo FROM cursos WHERE id=%s", (curso_id,))
    curso = cursor.fetchone()

    if curso is None:
        cursor.close()
        conn.close()
        flash("Curso no encontrado.")
        return redirect(url_for("listar_cursos"))

    # ❗ ERROR ORIGINAL CORREGIDO: faltaba el placeholder %s
    cursor.execute('''
        SELECT e.id, e.nombre, e.correo
        FROM estudiantes e
        INNER JOIN estudiante_curso ec ON e.id = ec.estudiante_id
        WHERE ec.curso_id = %s
        ORDER BY e.nombre
    ''', (curso_id,))
    estudiantes_inscritos = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "estudiantes_curso.html",
        curso=curso,
        estudiantes_inscritos=estudiantes_inscritos
    )


# ------------------- MAIN -------------------
if __name__ == "__main__":
    app.run(debug=True)
