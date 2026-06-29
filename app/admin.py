from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.db import get_db, get_db_connection
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__)

# Ruta para la gestión de usuarios registrados
@admin_bp.route('/gestion_usuarios', methods=['GET', 'POST'])
def gestion_usuarios():
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('auth.iniciar_sesion'))

    if request.method == 'POST':
        try:
            nombres = request.form['nombres']
            correo = request.form['correo']
            telefono = request.form['telefono']
            contrasena = request.form['contrasena']
            rol = request.form['rol']

            # Verificar si el correo ya existe
            cursor = get_db().cursor()
            cursor.execute("SELECT IDUsuario FROM Usuario WHERE Correo = %s", (correo,))
            if cursor.fetchone():
                flash('El correo electrónico ya está registrado', 'error')
                return redirect(url_for('.gestion_usuarios'))

            # Insertar nuevo usuario
            cursor.execute("""
                INSERT INTO Usuario (Nombre, Correo, Telefono, Contrasena, Estado)
                VALUES (%s, %s, %s, %s, 1)
            """, (nombres, correo, telefono, contrasena))
            get_db().commit()

            # Obtener el ID del usuario recién creado
            id_usuario = cursor.lastrowid

            # Asignar rol al usuario
            cursor.execute("SELECT IDRol FROM Rol WHERE NombreRol = %s", (rol,))
            id_rol = cursor.fetchone()['IDRol']
            cursor.execute("""
                INSERT INTO UsuarioRol (Usuario, Rol)
                VALUES (%s, %s)
            """, (id_usuario, id_rol))
            get_db().commit()

            flash('Usuario registrado exitosamente', 'success')
            return redirect(url_for('.gestion_usuarios'))

        except Exception as e:
            get_db().rollback()
            flash(f'Error al registrar usuario: {str(e)}', 'error')
            return redirect(url_for('.gestion_usuarios'))

    # Obtener lista de usuarios con sus roles
    cursor = get_db().cursor()
    cursor.execute("""
        SELECT u.*, STRING_AGG(r.NombreRol, ',') as roles
        FROM Usuario u
        LEFT JOIN UsuarioRol ur ON u.IDUsuario = ur.IDUsuario
        LEFT JOIN Rol r ON ur.IDRol = r.IDRol
        GROUP BY u.IDUsuario
    """)
    usuarios = cursor.fetchall()

    # Obtener lista de roles disponibles
    cursor.execute("SELECT * FROM Rol")
    roles = cursor.fetchall()

    return render_template('registro_usuario.html', usuarios=usuarios, roles=roles)

# Ruta para la página de gestión (sidebar)
@admin_bp.route('/gestion')
def gestion():
    if 'usuario' not in session:
        flash('Por favor, inicia sesión para acceder a esta página.', 'warning')
        return redirect(url_for('auth.iniciar_sesion'))
    return render_template('gestion.html')

# Ruta para la página de sidebar (gestión)
@admin_bp.route('/sidebar')
def sidebar():
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('auth.iniciar_sesion'))
    return redirect(url_for('arboles.inicio'))

def actualizar_sugerencias_antiguas():
    try:
        # Calcular la fecha límite (1 mes atrás)
        fecha_limite = datetime.now() - timedelta(days=30)
        fecha_limite_str = fecha_limite.strftime('%Y-%m-%d %H:%M:%S')

        connection = get_db_connection()
        cursor = connection.cursor()

        # Actualizar sugerencias más antiguas que 1 mes a estado inactivo (2)
        cursor.execute('''
            UPDATE sugerencias
            SET Estado = 2
            WHERE Estado = 1 AND Fecha < %s
        ''', (fecha_limite_str,))

        num_actualizadas = cursor.rowcount
        connection.commit()
        cursor.close()
        connection.close()

        if num_actualizadas > 0:
            print(f"Se actualizaron {num_actualizadas} sugerencias antiguas a estado inactivo")

        return num_actualizadas
    except Exception as e:
        print(f"Error al actualizar sugerencias antiguas: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return 0

# Ruta para la gestión de sugerencias
@admin_bp.route('/sugerencias', methods=['GET', 'POST'])
def sugerencias():
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('auth.iniciar_sesion'))

    # Actualizar automáticamente las sugerencias antiguas
    num_actualizadas = actualizar_sugerencias_antiguas()
    if num_actualizadas > 0:
        flash(f'Se actualizaron {num_actualizadas} sugerencias antiguas a estado inactivo', 'info')

    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            email = request.form['email']
            sugerencia = request.form['sugerencia']
            estado = request.form['estado']

            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute('''
                INSERT INTO sugerencias (Nombre, Email, Sugerencia, Estado)
                VALUES (%s, %s, %s, %s)
            ''', (nombre, email, sugerencia, estado))
            connection.commit()
            cursor.close()
            connection.close()
            flash('Sugerencia registrada exitosamente', 'success')
        except Exception as e:
            flash(f'Error al registrar la sugerencia: {str(e)}', 'error')
        return redirect(url_for('.sugerencias'))

    # Obtener todas las sugerencias y estados para mostrar en la tabla
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        # Obtener los estados para el formulario
        cursor.execute('SELECT * FROM Estado')
        estados = cursor.fetchall()

        # Obtener todas las sugerencias con su estado
        cursor.execute('''
            SELECT s.*, e.NombreEstado as EstadoNombre
            FROM sugerencias s
            LEFT JOIN Estado e ON s.Estado = e.IDEstado
            ORDER BY s.Fecha DESC
        ''')
        sugerencias = cursor.fetchall()

    except Exception as e:
        flash(f'Error al obtener las sugerencias: {str(e)}', 'error')
        sugerencias = []
        estados = []
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return render_template('sugerencias.html', sugerencias=sugerencias, estados=estados)

# Ruta para eliminar una sugerencia
@admin_bp.route('/sugerencias/eliminar/<int:id>')
def eliminar_sugerencia(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('auth.iniciar_sesion'))

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('DELETE FROM sugerencias WHERE IDSugerencia = %s', (id,))
        connection.commit()
        cursor.close()
        connection.close()
        flash('Sugerencia eliminada exitosamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar la sugerencia: {str(e)}', 'error')
    return redirect(url_for('.sugerencias'))

# Ruta para actualizar el estado de una sugerencia
@admin_bp.route('/sugerencias/actualizar/<int:id>', methods=['POST'])
def actualizar_estado_sugerencia(id):
    if 'usuario' not in session:
        return jsonify({
            'success': False,
            'message': 'Debes iniciar sesión para realizar esta acción'
        }), 401

    try:
        nuevo_estado = request.form['estado']
        connection = get_db_connection()
        cursor = connection.cursor()

        # Obtener el nombre de la sugerencia para el mensaje
        cursor.execute('SELECT Nombre FROM sugerencias WHERE IDSugerencia = %s', (id,))
        sugerencia = cursor.fetchone()
        nombre_sugerencia = sugerencia['Nombre'] if sugerencia else 'desconocida'

        # Actualizar el estado
        cursor.execute('''
            UPDATE sugerencias SET Estado = %s
            WHERE IDSugerencia = %s
        ''', (nuevo_estado, id))
        connection.commit()

        # Obtener el nombre del estado
        cursor.execute('SELECT NombreEstado FROM Estado WHERE IDEstado = %s', (nuevo_estado,))
        estado = cursor.fetchone()
        estado_desc = estado['NombreEstado'] if estado else ('Activo' if nuevo_estado == '1' else 'Inactivo')

        cursor.close()
        connection.close()

        return jsonify({
            'success': True,
            'message': f'Estado de la sugerencia de {nombre_sugerencia} actualizado a {estado_desc}',
            'nuevoEstado': nuevo_estado,
            'estadoDescripcion': estado_desc
        })
    except Exception as e:
        print(f"Error al actualizar estado de sugerencia: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': f'Error al actualizar el estado: {str(e)}'
        }), 500

# Ruta para la gestión de curiosidades
@admin_bp.route('/curiosidades', methods=['GET', 'POST'])
def curiosidades():
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('auth.iniciar_sesion'))

    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        # Obtener especies para el formulario
        cursor.execute('SELECT * FROM Especie')
        especies = cursor.fetchall()

        if request.method == 'POST':
            try:
                especie = request.form['especie']
                descripcion = request.form['descripcion']
                estado = request.form.get('estado', 1)  # Por defecto activo

                cursor.execute('''
                    INSERT INTO CuriosidadesArbol (Especie, Descripcion, Estado)
                    VALUES (%s, %s, %s)
                ''', (especie, descripcion, estado))
                connection.commit()
                flash('Curiosidad registrada exitosamente', 'success')
                return redirect(url_for('.curiosidades'))
            except Exception as e:
                flash(f'Error al registrar curiosidad: {str(e)}', 'error')

        # Obtener todas las curiosidades con información de estado
        cursor.execute('''
            SELECT c.*, e.NombreCientifico as EspecieNombre, es.NombreEstado as EstadoNombre
            FROM CuriosidadesArbol c
            LEFT JOIN Especie e ON c.Especie = e.IDEspecie
            LEFT JOIN Estado es ON c.Estado = es.IDEstado
            ORDER BY c.IDCuriosidad DESC
        ''')
        curiosidades_list = cursor.fetchall()

        # Obtener estados para el formulario
        cursor.execute('SELECT * FROM Estado')
        estados = cursor.fetchall()

    except Exception as e:
        flash(f'Error al cargar las curiosidades: {str(e)}', 'error')
        curiosidades_list = []
        especies = []
        estados = []
    finally:
        cursor.close()
        connection.close()

    return render_template('curiosidades.html', curiosidades=curiosidades_list, especies=especies, estados=estados)

# Ruta para editar una curiosidad
@admin_bp.route('/curiosidades/editar/<int:id>', methods=['GET', 'POST'])
def editar_curiosidad(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('auth.iniciar_sesion'))

    connection = get_db_connection()
    cursor = connection.cursor()

    if request.method == 'POST':
        try:
            especie = request.form['especie']
            descripcion = request.form['descripcion']
            estado = request.form.get('estado', 1)  # Por defecto activo

            cursor.execute('''
                UPDATE CuriosidadesArbol SET Especie = %s, Descripcion = %s, Estado = %s
                WHERE IDCuriosidad = %s
            ''', (especie, descripcion, estado, id))
            connection.commit()
            flash('Curiosidad actualizada exitosamente', 'success')
            return redirect(url_for('.curiosidades'))
        except Exception as e:
            flash(f'Error al actualizar curiosidad: {str(e)}', 'error')

    # Obtener especies para el formulario
    cursor.execute('SELECT * FROM Especie')
    especies = cursor.fetchall()

    # Obtener la curiosidad a editar
    cursor.execute('SELECT * FROM CuriosidadesArbol WHERE IDCuriosidad = %s', (id,))
    curiosidad = cursor.fetchone()

    # Obtener estados para el formulario
    cursor.execute('SELECT * FROM Estado')
    estados = cursor.fetchall()

    cursor.close()
    connection.close()

    if not curiosidad:
        flash('Curiosidad no encontrada', 'error')
        return redirect(url_for('.curiosidades'))

    return render_template('editar_curiosidad.html', curiosidad=curiosidad, especies=especies, estados=estados)

# Ruta para eliminar una curiosidad
@admin_bp.route('/curiosidades/eliminar/<int:id>')
def eliminar_curiosidad(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('auth.iniciar_sesion'))

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('DELETE FROM CuriosidadesArbol WHERE IDCuriosidad = %s', (id,))
        connection.commit()
        cursor.close()
        connection.close()
        flash('Curiosidad eliminada exitosamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar curiosidad: {str(e)}', 'error')
    return redirect(url_for('.curiosidades'))

# Ruta para la gestión de interacciones ecológicas
@admin_bp.route('/interacciones', methods=['GET', 'POST'])
def interacciones():
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('auth.iniciar_sesion'))

    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        # Obtener especies para el formulario
        cursor.execute('SELECT * FROM Especie')
        especies = cursor.fetchall()

        if request.method == 'POST':
            try:
                especie = request.form['especie']
                tipo_interaccion = request.form['tipo_interaccion']
                descripcion = request.form['descripcion']
                estado = request.form.get('estado', 1)  # Por defecto activo

                cursor.execute('''
                    INSERT INTO InteraccionesEcologicas (Especie, TipoInteraccion, Descripcion, Estado)
                    VALUES (%s, %s, %s, %s)
                ''', (especie, tipo_interaccion, descripcion, estado))
                connection.commit()
                flash('Interacción ecológica registrada exitosamente', 'success')
                return redirect(url_for('.interacciones'))
            except Exception as e:
                flash(f'Error al registrar interacción ecológica: {str(e)}', 'error')

        # Obtener todas las interacciones ecológicas con información de estado
        cursor.execute('''
            SELECT i.*, e.NombreCientifico as EspecieNombre, es.NombreEstado as EstadoNombre
            FROM InteraccionesEcologicas i
            LEFT JOIN Especie e ON i.Especie = e.IDEspecie
            LEFT JOIN Estado es ON i.Estado = es.IDEstado
            ORDER BY i.IDInteraccion DESC
        ''')
        interacciones_list = cursor.fetchall()

        # Obtener estados para el formulario
        cursor.execute('SELECT * FROM Estado')
        estados = cursor.fetchall()

    except Exception as e:
        flash(f'Error al cargar las interacciones ecológicas: {str(e)}', 'error')
        interacciones_list = []
        especies = []
        estados = []
    finally:
        cursor.close()
        connection.close()

    return render_template('interacciones.html', interacciones=interacciones_list, especies=especies, estados=estados)

# Ruta para editar una interacción ecológica
@admin_bp.route('/interacciones/editar/<int:id>', methods=['GET', 'POST'])
def editar_interaccion(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('auth.iniciar_sesion'))

    connection = get_db_connection()
    cursor = connection.cursor()

    if request.method == 'POST':
        try:
            especie = request.form['especie']
            tipo_interaccion = request.form['tipo_interaccion']
            descripcion = request.form['descripcion']
            estado = request.form.get('estado', 1)  # Por defecto activo

            cursor.execute('''
                UPDATE InteraccionesEcologicas SET Especie = %s, TipoInteraccion = %s, Descripcion = %s, Estado = %s
                WHERE IDInteraccion = %s
            ''', (especie, tipo_interaccion, descripcion, estado, id))
            connection.commit()
            flash('Interacción ecológica actualizada exitosamente', 'success')
            return redirect(url_for('.interacciones'))
        except Exception as e:
            flash(f'Error al actualizar interacción ecológica: {str(e)}', 'error')

    # Obtener especies para el formulario
    cursor.execute('SELECT * FROM Especie')
    especies = cursor.fetchall()

    # Obtener la interacción ecológica a editar
    cursor.execute('SELECT * FROM InteraccionesEcologicas WHERE IDInteraccion = %s', (id,))
    interaccion = cursor.fetchone()

    # Obtener estados para el formulario
    cursor.execute('SELECT * FROM Estado')
    estados = cursor.fetchall()

    cursor.close()
    connection.close()

    if not interaccion:
        flash('Interacción ecológica no encontrada', 'error')
        return redirect(url_for('.interacciones'))

    return render_template('editar_interaccion.html', interaccion=interaccion, especies=especies, estados=estados)

# Ruta para eliminar una interacción ecológica
@admin_bp.route('/interacciones/eliminar/<int:id>')
def eliminar_interaccion(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('auth.iniciar_sesion'))

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('DELETE FROM InteraccionesEcologicas WHERE IDInteraccion = %s', (id,))
        connection.commit()
        cursor.close()
        connection.close()
        flash('Interacción ecológica eliminada exitosamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar interacción ecológica: {str(e)}', 'error')
    return redirect(url_for('.interacciones'))

# Ruta para editar usuario
@admin_bp.route('/usuario/editar/<int:id>', methods=['GET', 'POST'])
def editar_usuario(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('auth.iniciar_sesion'))

    cursor = get_db().cursor()

    if request.method == 'POST':
        try:
            nombres = request.form['nombres']
            apellidos = request.form['apellidos']
            correo = request.form['correo']
            telefono = request.form['telefono']
            rol = request.form.get('rol', 'Usuario')  # Por defecto es Usuario

            # Verificar si el correo ya existe (excluyendo el usuario actual)
            cursor.execute("""
                SELECT IDUsuario FROM Usuario
                WHERE Correo = %s AND IDUsuario != %s
            """, (correo, id))
            if cursor.fetchone():
                flash('El correo electrónico ya está registrado', 'error')
                return redirect(url_for('editar_usuario', id=id))

            # Actualizar datos del usuario
            cursor.execute("""
                UPDATE Usuario
                SET Nombre = %s, Correo = %s, Telefono = %s
                WHERE IDUsuario = %s
            """, (nombres + ' ' + apellidos, correo, telefono, id))

            # Actualizar rol del usuario
            cursor.execute("SELECT IDRol FROM Rol WHERE NombreRol = %s", (rol,))
            resultado = cursor.fetchone()
            if resultado:
                id_rol = resultado['IDRol']

                # Verificar si ya existe un rol para este usuario
                cursor.execute("SELECT COUNT(*) as count FROM UsuarioRol WHERE Usuario = %s", (id,))
                existe_rol = cursor.fetchone()['count'] > 0

                if existe_rol:
                    # Actualizar el rol existente
                    cursor.execute("UPDATE UsuarioRol SET Rol = %s WHERE Usuario = %s", (id_rol, id))
                else:
                    # Insertar nuevo rol
                    cursor.execute("INSERT INTO UsuarioRol (Usuario, Rol) VALUES (%s, %s)", (id, id_rol))

            get_db().commit()
            flash('Usuario actualizado exitosamente', 'success')
            return redirect(url_for('.gestion_usuarios'))

        except Exception as e:
            get_db().rollback()
            flash(f'Error al actualizar usuario: {str(e)}', 'error')
            return redirect(url_for('editar_usuario', id=id))

    # Obtener datos del usuario
    cursor.execute("""
        SELECT u.*, r.NombreRol as rol_actual
        FROM Usuario u
        LEFT JOIN UsuarioRol ur ON u.IDUsuario = ur.IDUsuario
        LEFT JOIN Rol r ON ur.IDRol = r.IDRol
        WHERE u.IDUsuario = %s
    """, (id,))
    usuario = cursor.fetchone()

    # Dividir el nombre completo en nombres y apellidos para la interfaz
    if usuario:
        nombre_completo = usuario['Nombre'] if usuario['Nombre'] else ''
        partes_nombre = nombre_completo.split(' ', 1)
        usuario['Nombres'] = partes_nombre[0] if len(partes_nombre) > 0 else ''
        usuario['Apellidos'] = partes_nombre[1] if len(partes_nombre) > 1 else ''

    # Obtener lista de roles disponibles
    cursor.execute("SELECT * FROM rol")
    roles = cursor.fetchall()

    return render_template('editar_usuario.html', usuario=usuario, roles=roles)

# Ruta para eliminar usuario
@admin_bp.route('/usuario/eliminar/<int:id>', methods=['GET', 'POST'])
def eliminar_usuario(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('auth.iniciar_sesion'))

    # Verificar si el usuario tiene rol de administrador
    cursor = get_db().cursor()
    cursor.execute("""
        SELECT r.NombreRol
        FROM UsuarioRol ur
        JOIN Rol r ON ur.IDRol = r.IDRol
        WHERE ur.IDUsuario = %s AND r.NombreRol = 'Administrador'
    """, (session['usuario']['IDUsuario'],))
    es_admin = cursor.fetchone() is not None

    # Si es una solicitud GET, vamos a mostrar una confirmación o redirigir directamente
    if request.method == 'GET':
        return redirect(url_for('.gestion_usuarios'))

    # Verificar si el usuario intenta eliminarse a sí mismo
    if id == session['usuario']['IDUsuario']:
        flash('No puede eliminarse a sí mismo', 'error')
        return redirect(url_for('.gestion_usuarios'))

    try:
        # Eliminar roles del usuario
        cursor.execute("DELETE FROM UsuarioRol WHERE IDUsuario = %s", (id,))

        # Eliminar el usuario
        cursor.execute("DELETE FROM Usuario WHERE IDUsuario = %s", (id,))

        get_db().commit()
        flash('Usuario eliminado exitosamente', 'success')

    except Exception as e:
        get_db().rollback()
        flash(f'Error al eliminar usuario: {str(e)}', 'error')

    return redirect(url_for('.gestion_usuarios'))
