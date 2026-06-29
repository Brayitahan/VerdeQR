from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.db import get_db, get_db_connection
from app.utils import get_base_url
from datetime import datetime

info_bp = Blueprint('info', __name__)


@info_bp.route('/politica-privacidad')
def politica_privacidad():
    return render_template('politica_privacidad.html')


@info_bp.route('/terminos-condiciones')
def terminos_condiciones():
    return render_template('terminos_condiciones.html')


@info_bp.route('/contacto')
def contacto():
    return render_template('contacto.html')


@info_bp.route('/acerca-de')
def acerca_de():
    return render_template('acerca_de.html')


@info_bp.route('/soporte-tecnico')
def soporte_tecnico():
    return render_template('soporte_tecnico.html')


@info_bp.route('/preguntas-frecuentes')
def preguntas_frecuentes():
    return render_template('preguntas_frecuentes.html')


@info_bp.route('/reportar-problema')
def reportar_problema():
    return render_template('reportar_problema.html')


@info_bp.route('/enviar-contacto', methods=['POST'])
def enviar_contacto():
    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            email = request.form['email']
            telefono = request.form.get('telefono', '')
            asunto = request.form['asunto']
            mensaje = request.form['mensaje']

            flash('Mensaje enviado correctamente. Nos pondremos en contacto contigo pronto.', 'success')
        except Exception as e:
            flash(f'Error al enviar el mensaje: {str(e)}', 'error')

        return redirect(url_for('.contacto'))


@info_bp.route('/registrar_sugerencia', methods=['POST'])
def registrar_sugerencia():
    if not session.get('usuario'):
        return jsonify({
            'success': False,
            'message': 'Debes iniciar sesion para enviar sugerencias'
        }), 401

    connection = None
    cursor = None
    try:
        sugerencia = request.form.get('sugerencia')

        if not sugerencia:
            return jsonify({
                'success': False,
                'message': 'El campo sugerencia es requerido'
            }), 400

        nombre = session['usuario']['Nombres']
        email = session['usuario']['Correo']

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute('''
            INSERT INTO sugerencias (Nombre, Email, Sugerencia, Estado)
            VALUES (%s, %s, %s, %s)
        ''', (nombre, email, sugerencia, 1))
        connection.commit()

        fecha_actual = datetime.now().strftime('%d/%m/%Y')

        nuevo_id = cursor.lastrowid
        return jsonify({
            'success': True,
            'message': 'Gracias por tu sugerencia!',
            'nuevaSugerencia': {
                'ID': nuevo_id,
                'Nombre': nombre,
                'Fecha': fecha_actual,
                'Sugerencia': sugerencia
            }
        })

    except Exception as e:
        if connection:
            connection.rollback()
        print(f"Error al registrar sugerencia: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al guardar en la base de datos: {str(e)}'
        }), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@info_bp.route('/eliminar_sugerencia/<int:id>', methods=['POST'])
def eliminar_sugerencia_usuario(id):
    if not session.get('usuario'):
        return jsonify({'success': False, 'message': 'Debes iniciar sesion'}), 401
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute('SELECT Email FROM sugerencias WHERE IDSugerencia=%s', (id,))
        s = cursor.fetchone()
        if not s:
            return jsonify({'success': False, 'message': 'Sugerencia no encontrada'}), 404
        if s['Email'] != session['usuario']['Correo']:
            return jsonify({'success': False, 'message': 'No puedes eliminar sugerencias de otros usuarios'}), 403
        cursor.execute('DELETE FROM sugerencias WHERE IDSugerencia=%s', (id,))
        connection.commit()
        return jsonify({'success': True, 'message': 'Sugerencia eliminada'})
    except Exception as e:
        connection.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@info_bp.route('/editar_sugerencia/<int:id>', methods=['POST'])
def editar_sugerencia_usuario(id):
    if not session.get('usuario'):
        return jsonify({'success': False, 'message': 'Debes iniciar sesion'}), 401
    nuevo_texto = request.form.get('sugerencia', '').strip()
    if not nuevo_texto:
        return jsonify({'success': False, 'message': 'El texto no puede estar vacio'}), 400
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute('SELECT Email FROM sugerencias WHERE IDSugerencia=%s', (id,))
        s = cursor.fetchone()
        if not s:
            return jsonify({'success': False, 'message': 'Sugerencia no encontrada'}), 404
        if s['Email'] != session['usuario']['Correo']:
            return jsonify({'success': False, 'message': 'No puedes editar sugerencias de otros usuarios'}), 403
        cursor.execute('UPDATE sugerencias SET Sugerencia=%s WHERE IDSugerencia=%s', (nuevo_texto, id))
        connection.commit()
        return jsonify({'success': True, 'message': 'Sugerencia actualizada'})
    except Exception as e:
        connection.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@info_bp.route('/api/sugerencias_busqueda')
def sugerencias_busqueda():
    query = request.args.get('q', '')
    if not query or len(query) < 2:
        return jsonify([])

    connection = get_db_connection()
    cursor = connection.cursor()
    sugerencias = []

    try:
        cursor.execute('''
            SELECT NombreCientifico, NombreVulgar FROM Especie
            WHERE NombreCientifico LIKE %s OR NombreVulgar LIKE %s
            LIMIT 5
        ''', (f'%{query}%', f'%{query}%'))
        especies = cursor.fetchall()

        for especie in especies:
            if especie['NombreCientifico'] and query.lower() in especie['NombreCientifico'].lower():
                sugerencias.append(especie['NombreCientifico'])
            if especie['NombreVulgar'] and query.lower() in especie['NombreVulgar'].lower():
                sugerencias.append(especie['NombreVulgar'])

        cursor.execute('''
            SELECT NombreCentro FROM Centro
            WHERE NombreCentro LIKE %s
            LIMIT 3
        ''', (f'%{query}%',))
        centros = cursor.fetchall()

        for centro in centros:
            if centro['NombreCentro'] and query.lower() in centro['NombreCentro'].lower():
                sugerencias.append(centro['NombreCentro'])

        sugerencias = list(set(sugerencias))[:8]

    except Exception as e:
        print(f"Error al obtener sugerencias: {str(e)}")
    finally:
        cursor.close()
        connection.close()

    return jsonify(sugerencias)
