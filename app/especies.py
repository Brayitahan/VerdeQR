from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.db import get_db, get_db_connection

especies_bp = Blueprint('especies', __name__)

# Ruta para redireccionar tipo_arbol a especie
@especies_bp.route('/tipo_arbol', methods=['GET', 'POST'])
def tipo_arbol():
    return redirect(url_for('.especie'))

# Ruta para la gestión de especies
@especies_bp.route('/especie', methods=['GET', 'POST'])
def especie():
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('auth.iniciar_sesion'))

    if request.method == 'POST':
        try:
            nombre_cientifico = request.form['nombre_cientifico']
            nombre_vulgar = request.form['nombre_vulgar']
            estado = request.form.get('estado', 1)  # Por defecto activo

            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute('''
                INSERT INTO Especie (NombreCientifico, NombreVulgar, Estado)
                VALUES (%s, %s, %s)
            ''', (nombre_cientifico, nombre_vulgar, estado))
            connection.commit()
            cursor.close()
            connection.close()
            flash('Especie registrada exitosamente', 'success')
        except Exception as e:
            flash(f'Error al registrar la especie: {str(e)}', 'error')
        return redirect(url_for('.especie'))

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('''
        SELECT e.*, es.NombreEstado as EstadoNombre
        FROM Especie e
        LEFT JOIN Estado es ON e.Estado = es.IDEstado
        ORDER BY e.IDEspecie DESC
    ''')
    especies = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('especie.html', especies=especies)

# Ruta para redireccionar editar_tipo_arbol a editar_especie
@especies_bp.route('/tipo_arbol/editar/<int:id>', methods=['GET', 'POST'])
def editar_tipo_arbol(id):
    return redirect(url_for('editar_especie', id=id))

# Ruta para editar una especie
@especies_bp.route('/especie/editar/<int:id>', methods=['GET', 'POST'])
def editar_especie(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('auth.iniciar_sesion'))

    if request.method == 'POST':
        try:
            nombre_cientifico = request.form['nombre_cientifico']
            nombre_vulgar = request.form['nombre_vulgar']
            estado = request.form.get('estado', 1)  # Por defecto activo

            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute('''
                UPDATE Especie SET NombreCientifico = %s, NombreVulgar = %s, Estado = %s
                WHERE IDEspecie = %s
            ''', (nombre_cientifico, nombre_vulgar, estado, id))
            connection.commit()
            cursor.close()
            connection.close()
            flash('Especie actualizada exitosamente', 'success')
        except Exception as e:
            flash(f'Error al actualizar la especie: {str(e)}', 'error')
        return redirect(url_for('.especie'))

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM Especie WHERE IDEspecie = %s', (id,))
    especie_data = cursor.fetchone()

    # Obtener estados para el formulario
    cursor.execute('SELECT * FROM Estado')
    estados = cursor.fetchall()

    cursor.close()
    connection.close()
    return render_template('editar_especie.html', especie=especie_data, estados=estados)

# Ruta para redireccionar eliminar_tipo_arbol a eliminar_especie
@especies_bp.route('/tipo_arbol/eliminar/<int:id>')
def eliminar_tipo_arbol(id):
    return redirect(url_for('eliminar_especie', id=id))

# Ruta para eliminar una especie
@especies_bp.route('/especie/eliminar/<int:id>')
def eliminar_especie(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('auth.iniciar_sesion'))

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Verificar si la especie está siendo utilizada en árboles
        cursor.execute('SELECT COUNT(*) as total FROM Arbol WHERE Especie = %s', (id,))
        result = cursor.fetchone()
        if result and result['total'] > 0:
            flash(f'No se puede eliminar la especie porque está siendo utilizada en {result["total"]} árboles', 'error')
            return redirect(url_for('.especie'))

        # Iniciar transacción para eliminar todos los registros relacionados
        connection.begin()

        # Eliminar usos asociados a esta especie
        cursor.execute('SELECT COUNT(*) as total FROM UsoArbol WHERE Especie = %s', (id,))
        result = cursor.fetchone()
        if result and result['total'] > 0:
            cursor.execute('DELETE FROM UsoArbol WHERE Especie = %s', (id,))
            flash(f'Se eliminaron {result["total"]} usos asociados a la especie', 'info')

        # Eliminar curiosidades asociadas a esta especie
        cursor.execute('SELECT COUNT(*) as total FROM CuriosidadesArbol WHERE Especie = %s', (id,))
        result = cursor.fetchone()
        if result and result['total'] > 0:
            cursor.execute('DELETE FROM CuriosidadesArbol WHERE Especie = %s', (id,))
            flash(f'Se eliminaron {result["total"]} curiosidades asociadas a la especie', 'info')

        # Eliminar interacciones ecológicas asociadas a esta especie
        cursor.execute('SELECT COUNT(*) as total FROM InteraccionesEcologicas WHERE Especie = %s', (id,))
        result = cursor.fetchone()
        if result and result['total'] > 0:
            cursor.execute('DELETE FROM InteraccionesEcologicas WHERE Especie = %s', (id,))
            flash(f'Se eliminaron {result["total"]} interacciones ecológicas asociadas a la especie', 'info')

        # Finalmente, eliminar la especie
        cursor.execute('DELETE FROM Especie WHERE IDEspecie = %s', (id,))
        connection.commit()
        cursor.close()
        connection.close()
        flash('Especie eliminada exitosamente junto con todos sus registros relacionados', 'success')
    except Exception as e:
        flash(f'Error al eliminar la especie: {str(e)}', 'error')
    return redirect(url_for('.especie'))

# Ruta para mostrar los usos agrupados por especie
@especies_bp.route('/usos_por_especie')
def usos_por_especie():
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('auth.iniciar_sesion'))

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Obtener todas las especies
        cursor.execute('SELECT * FROM Especie ORDER BY NombreCientifico')
        especies = cursor.fetchall()

        # Para cada especie, obtener sus usos
        for especie in especies:
            cursor.execute('''
                SELECT u.*, COALESCE(u.Categoria, '') as TipoUsoDetectado
                FROM UsoArbol u
                LEFT JOIN Especie e ON u.Especie = e.IDEspecie
                WHERE u.Especie = %s
                ORDER BY TipoUsoDetectado, u.Nombre
            ''', (especie['IDEspecie'],))
            especie['usos'] = cursor.fetchall()

        return render_template('usos_por_especie.html', especies=especies)
    except Exception as e:
        flash(f'Error al cargar los usos por especie: {str(e)}', 'error')
        return redirect(url_for('usos.uso_arbol'))
    finally:
        cursor.close()
        connection.close()

# Ruta para agregar un nuevo uso a una especie específica
@especies_bp.route('/agregar_uso/<int:especie_id>', methods=['GET', 'POST'])
def agregar_uso(especie_id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('auth.iniciar_sesion'))

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Obtener información de la especie
        cursor.execute('SELECT * FROM Especie WHERE IDEspecie = %s', (especie_id,))
        especie = cursor.fetchone()

        if not especie:
            flash('Especie no encontrada', 'error')
            return redirect(url_for('.usos_por_especie'))

        if request.method == 'POST':
            # Iniciar transacción
            connection.begin()

            # Datos básicos del uso
            nombre = request.form['nombre']
            categoria = request.form['categoria']

            # Verificar si la columna Categoria existe en la tabla UsoArbol
            cursor.execute('''
            SELECT COUNT(*) AS column_exists
            FROM information_schema.COLUMNS
            WHERE TABLE_NAME = 'UsoArbol'
              AND COLUMN_NAME = 'Categoria'
            ''')
            column_exists = cursor.fetchone()['column_exists'] > 0

            # Insertar en la tabla UsoArbol
            if column_exists:
                cursor.execute('''
                    INSERT INTO UsoArbol (Especie, Nombre, Categoria, Estado)
                    VALUES (%s, %s, %s, 1)
                    RETURNING IDUsoArbol
                ''', (especie_id, nombre, categoria))
            else:
                cursor.execute('''
                    INSERT INTO UsoArbol (Especie, Nombre, Estado)
                    VALUES (%s, %s, 1)
                    RETURNING IDUsoArbol
                ''', (especie_id, nombre))

            # Obtener el ID del uso recién insertado
            uso_id = cursor.fetchone()['IDUsoArbol']

            # Insertar en DetalleUso (tabla normalizada)
            cursor.execute('''
                INSERT INTO DetalleUso (
                    Uso, Estado,
                    Dureza, Resistencia, UsoFinal,
                    ParteComestible, FormaConsumo, ValorNutricional,
                    ParteUtilizada, Preparacion, EnfermedadesTratadas,
                    CaracteristicasEsteticas, UbicacionRecomendada, TipoJardineria, ColoracionEstacional,
                    TipoArtesania, TecnicasElaboracion, ComunidadesArtesanales,
                    SistemaAgroforestal, BeneficiosAsociados, CultivosCompatibles, FuncionPrincipal,
                    EcosistemaObjetivo, FuncionEcologica, EspeciesAsociadas, TasaCrecimiento,
                    GrupoEtnico, TipoCeremonia, SignificadoCultural,
                    TipoMiel, EpocaFloracion, CalidadPolen, AtraccionPolinizadores,
                    TipoProteccion, BeneficiosAmbientales, ZonasAplicacion, CapacidadCapturaCarbon,
                    ColorObtenido, MetodoExtraccion, UsosTintes,
                    TipoAceite, PropiedadesAceite, AplicacionesAceite,
                    TipoBiocombustible, PoderCalorifico, RendimientoPorHectarea
                ) VALUES (
                    %s, 1,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s
                )
            ''', (
                uso_id,
                request.form.get('dureza', ''), request.form.get('resistencia', ''), request.form.get('uso_final', ''),
                request.form.get('parte_comestible', ''), request.form.get('forma_consumo', ''), request.form.get('valor_nutricional', ''),
                request.form.get('parte_utilizada', ''), request.form.get('preparacion', ''), request.form.get('enfermedades_tratadas', ''),
                request.form.get('caracteristicas_esteticas', ''), request.form.get('ubicacion_recomendada', ''), request.form.get('tipo_jardineria', ''), request.form.get('coloracion_estacional', ''),
                request.form.get('tipo_artesania', ''), request.form.get('tecnicas_elaboracion', ''), request.form.get('comunidades_artesanales', ''),
                request.form.get('sistema_agroforestal', ''), request.form.get('beneficios_asociados', ''), request.form.get('cultivos_compatibles', ''), request.form.get('funcion_principal', ''),
                request.form.get('ecosistema_objetivo', ''), request.form.get('funcion_ecologica', ''), request.form.get('especies_asociadas', ''), request.form.get('tasa_crecimiento', ''),
                request.form.get('grupo_etnico', ''), request.form.get('tipo_ceremonia', ''), request.form.get('significado_cultural', ''),
                request.form.get('tipo_miel', ''), request.form.get('epoca_floracion', ''), request.form.get('calidad_polen', ''), request.form.get('atraccion_polinizadores', ''),
                request.form.get('tipo_proteccion', ''), request.form.get('beneficios_ambientales', ''), request.form.get('zonas_aplicacion', ''), request.form.get('capacidad_captura_carbon', ''),
                request.form.get('color_obtenido', ''), request.form.get('metodo_extraccion', ''), request.form.get('usos_tintes', ''),
                request.form.get('tipo_aceite', ''), request.form.get('propiedades_aceite', ''), request.form.get('aplicaciones_aceite', ''),
                request.form.get('tipo_biocombustible', ''), request.form.get('poder_calorifico', ''), request.form.get('rendimiento_por_hectarea', '')
            ))

            # Confirmar transacción
            connection.commit()
            flash('Uso agregado exitosamente', 'success')
            return redirect(url_for('.usos_por_especie'))

        # Si es GET, mostrar el formulario
        return render_template('agregar_uso.html', especie=especie)
    except Exception as e:
        connection.rollback()
        flash(f'Error al agregar uso: {str(e)}', 'error')
        return redirect(url_for('.usos_por_especie'))
    finally:
        cursor.close()
        connection.close()

# Ruta para la gestión de tipos de bosque
@especies_bp.route('/tipo_bosque', methods=['GET', 'POST'])
def tipo_bosque():
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('auth.iniciar_sesion'))

    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            descripcion = request.form['descripcion']
            estado = request.form['estado']

            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute('''
                INSERT INTO tipobosque (Nombre, Descripcion, Estado)
                VALUES (%s, %s, %s)
            ''', (nombre, descripcion, estado))
            connection.commit()
            cursor.close()
            connection.close()
            flash('Tipo de bosque registrado exitosamente', 'success')
        except Exception as e:
            flash(f'Error al registrar el tipo de bosque: {str(e)}', 'error')
        return redirect(url_for('.tipo_bosque'))

    connection = get_db_connection()
    cursor = connection.cursor()

    # Obtener tipos de bosque con información de estado
    cursor.execute('''
        SELECT tb.*
        FROM TipoBosque tb
        ORDER BY tb.IDTipoBosque DESC
    ''')
    tipos = cursor.fetchall()

    # Obtener estados para el formulario
    cursor.execute('SELECT * FROM Estado')
    estados = cursor.fetchall()

    cursor.close()
    connection.close()
    return render_template('tipo_bosque.html', tipos=tipos, estados=estados)

# Ruta para editar un tipo de bosque
@especies_bp.route('/tipo_bosque/editar/<int:id>', methods=['GET', 'POST'])
def editar_tipo_bosque(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('auth.iniciar_sesion'))

    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            descripcion = request.form['descripcion']
            estado = request.form['estado']

            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute('''
                UPDATE tipobosque SET Nombre = %s, Descripcion = %s, Estado = %s
                WHERE IDTipoBosque = %s
            ''', (nombre, descripcion, estado, id))
            connection.commit()
            cursor.close()
            connection.close()
            flash('Tipo de bosque actualizado exitosamente', 'success')
        except Exception as e:
            flash(f'Error al actualizar el tipo de bosque: {str(e)}', 'error')
        return redirect(url_for('.tipo_bosque'))

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM tipobosque WHERE IDTipoBosque = %s', (id,))
    tipo_bosque = cursor.fetchone()

    # Obtener estados para el formulario
    cursor.execute('SELECT * FROM Estado')
    estados = cursor.fetchall()

    cursor.close()
    connection.close()
    return render_template('editar_tipo_bosque.html', tipo_bosque=tipo_bosque, estados=estados)

# Ruta para eliminar un tipo de bosque
@especies_bp.route('/tipo_bosque/eliminar/<int:id>')
def eliminar_tipo_bosque(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('auth.iniciar_sesion'))

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('DELETE FROM tipobosque WHERE IDTipoBosque = %s', (id,))
        connection.commit()
        cursor.close()
        connection.close()
        flash('Tipo de bosque eliminado exitosamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar el tipo de bosque: {str(e)}', 'error')
    return redirect(url_for('.tipo_bosque'))
