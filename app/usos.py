from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.db import get_db, get_db_connection

usos_bp = Blueprint('usos', __name__)

@usos_bp.route('/uso_arbol', methods=['GET', 'POST'])
def uso_arbol():
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('auth.iniciar_sesion'))

    if request.method == 'POST':
        connection = get_db_connection()
        cursor = connection.cursor()
        try:
            # Iniciar transacción
            connection.begin()

            # Datos básicos del uso
            especie = request.form['especie']
            nombre = request.form['nombre']
            categoria = request.form['categoria']
            estado = request.form.get('estado', 1)  # Por defecto activo

            # Verificar si la columna Categoria existe en la tabla UsoArbol
            cursor.execute('''
                SELECT COUNT(*) AS column_exists
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'UsoArbol'
                  AND COLUMN_NAME = 'Categoria'
            ''')
            column_exists = cursor.fetchone()['column_exists'] > 0

            # Insertar en la tabla UsoArbol
            if column_exists:
                cursor.execute('''
                    INSERT INTO UsoArbol (Especie, Nombre, Categoria, Estado)
                    VALUES (%s, %s, %s, %s)
                ''', (especie, nombre, categoria, estado))
            else:
                cursor.execute('''
                    INSERT INTO UsoArbol (Especie, Nombre, Estado)
                    VALUES (%s, %s, %s)
                ''', (especie, nombre, estado))

            # Obtener el ID del uso recién insertado
            uso_id = cursor.lastrowid

            # Insertar en DetalleUso (tabla normalizada para todas las categorías)
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
            flash('Uso de árbol registrado exitosamente', 'success')
        except Exception as e:
            connection.rollback()
            flash(f'Error al registrar el uso de árbol: {str(e)}', 'error')
        finally:
            cursor.close()
            connection.close()
        return redirect(url_for('.uso_arbol'))

    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        # Obtener especies para el formulario
        cursor.execute('SELECT * FROM Especie')
        especies = cursor.fetchall()

        # Obtener usos de árbol con información de estado
        cursor.execute('''
            SELECT u.*, e.NombreCientifico as EspecieNombre, es.NombreEstado as EstadoNombre,
                   COALESCE(u.Categoria, '') as TipoUsoDetectado
            FROM UsoArbol u
            LEFT JOIN Especie e ON u.Especie = e.IDEspecie
            LEFT JOIN Estado es ON u.Estado = es.IDEstado
            ORDER BY u.IDUso DESC
        ''')
        usos = cursor.fetchall()

        # Obtener estados para el formulario
        cursor.execute('SELECT * FROM Estado')
        estados = cursor.fetchall()

    except Exception as e:
        flash(f'Error al cargar los usos de árbol: {str(e)}', 'error')
        usos = []
        especies = []
        estados = []
    finally:
        cursor.close()
        connection.close()
    return render_template('uso_arbol.html', usos=usos, especies=especies, estados=estados)


# Ruta para editar un uso de árbol
@usos_bp.route('/uso_arbol/editar/<int:id>', methods=['GET', 'POST'])
def editar_uso_arbol(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('auth.iniciar_sesion'))

    if request.method == 'POST':
        try:
            especie = request.form['especie']
            nombre = request.form['nombre']
            categoria = request.form['categoria']

            connection = get_db_connection()
            cursor = connection.cursor()

            # Verificar si la columna Categoria existe en la tabla UsoArbol
            cursor.execute('''
                SELECT COUNT(*) AS column_exists
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'UsoArbol'
                  AND COLUMN_NAME = 'Categoria'
            ''')
            column_exists = cursor.fetchone()['column_exists'] > 0

            # Actualizar el uso de árbol
            if column_exists:
                cursor.execute('''
                    UPDATE UsoArbol SET Especie = %s, Nombre = %s, Categoria = %s
                    WHERE IDUso = %s
                ''', (especie, nombre, categoria, id))
            else:
                cursor.execute('''
                    UPDATE UsoArbol SET Especie = %s, Nombre = %s
                    WHERE IDUso = %s
                ''', (especie, nombre, id))
            # Actualizar detalles en DetalleUso
            cursor.execute('''
                UPDATE DetalleUso SET
                    Dureza = %s, Resistencia = %s, UsoFinal = %s,
                    ParteComestible = %s, FormaConsumo = %s, ValorNutricional = %s,
                    ParteUtilizada = %s, Preparacion = %s, EnfermedadesTratadas = %s,
                    CaracteristicasEsteticas = %s, UbicacionRecomendada = %s, TipoJardineria = %s, ColoracionEstacional = %s,
                    TipoArtesania = %s, TecnicasElaboracion = %s, ComunidadesArtesanales = %s,
                    SistemaAgroforestal = %s, BeneficiosAsociados = %s, CultivosCompatibles = %s, FuncionPrincipal = %s,
                    EcosistemaObjetivo = %s, FuncionEcologica = %s, EspeciesAsociadas = %s, TasaCrecimiento = %s,
                    GrupoEtnico = %s, TipoCeremonia = %s, SignificadoCultural = %s,
                    TipoMiel = %s, EpocaFloracion = %s, CalidadPolen = %s, AtraccionPolinizadores = %s,
                    TipoProteccion = %s, BeneficiosAmbientales = %s, ZonasAplicacion = %s, CapacidadCapturaCarbon = %s,
                    ColorObtenido = %s, MetodoExtraccion = %s, UsosTintes = %s,
                    TipoAceite = %s, PropiedadesAceite = %s, AplicacionesAceite = %s,
                    TipoBiocombustible = %s, PoderCalorifico = %s, RendimientoPorHectarea = %s
                WHERE Uso = %s
            ''', (
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
                request.form.get('tipo_biocombustible', ''), request.form.get('poder_calorifico', ''), request.form.get('rendimiento_por_hectarea', ''),
                id
            ))

            connection.commit()
            cursor.close()
            connection.close()
            flash('Uso de árbol actualizado exitosamente', 'success')
        except Exception as e:
            flash(f'Error al actualizar el uso de árbol: {str(e)}', 'error')
        return redirect(url_for('.uso_arbol'))

    connection = get_db_connection()
    cursor = connection.cursor()

    # Obtener especies para el formulario
    cursor.execute('SELECT * FROM Especie WHERE Estado = 1')
    especies = cursor.fetchall()

    # Obtener el uso de árbol a editar
    cursor.execute('''
        SELECT u.*, COALESCE(u.Categoria, '') as TipoUsoDetectado
        FROM UsoArbol u
        WHERE u.IDUso = %s
    ''', (id,))
    uso_arbol = cursor.fetchone()

    # Obtener estados
    cursor.execute('SELECT * FROM Estado')
    estados = cursor.fetchall()

    # Obtener datos específicos desde DetalleUso
    cursor.execute('SELECT * FROM DetalleUso WHERE Uso = %s', (id,))
    datos_especificos = cursor.fetchone()

    cursor.close()
    connection.close()

    if not uso_arbol:
        flash('Uso de árbol no encontrado', 'error')
        return redirect(url_for('.uso_arbol'))

    return render_template('editar_uso_arbol.html', uso_arbol=uso_arbol, especies=especies, estados=estados, datos_especificos=datos_especificos)


# Ruta para editar los detalles de un uso (cualquier categoría)
@usos_bp.route('/uso_arbol/detalle/<int:id>', methods=['GET', 'POST'])
def editar_uso_detalle(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('auth.iniciar_sesion'))

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute('''
            SELECT u.*, e.NombreCientifico as EspecieNombre
            FROM UsoArbol u
            LEFT JOIN Especie e ON u.Especie = e.IDEspecie
            WHERE u.IDUso = %s
        ''', (id,))
        uso = cursor.fetchone()

        if not uso:
            flash('Uso de árbol no encontrado', 'error')
            return redirect(url_for('.uso_arbol'))

        cursor.execute('SELECT * FROM DetalleUso WHERE Uso = %s', (id,))
        detalle = cursor.fetchone()

        if request.method == 'POST':
            try:
                cursor.execute('''
                    UPDATE DetalleUso SET
                        Dureza=%s, Resistencia=%s, UsoFinal=%s,
                        ParteComestible=%s, FormaConsumo=%s, ValorNutricional=%s,
                        ParteUtilizada=%s, Preparacion=%s, EnfermedadesTratadas=%s,
                        CaracteristicasEsteticas=%s, UbicacionRecomendada=%s, TipoJardineria=%s, ColoracionEstacional=%s,
                        TipoArtesania=%s, TecnicasElaboracion=%s, ComunidadesArtesanales=%s,
                        SistemaAgroforestal=%s, BeneficiosAsociados=%s, CultivosCompatibles=%s, FuncionPrincipal=%s,
                        EcosistemaObjetivo=%s, FuncionEcologica=%s, EspeciesAsociadas=%s, TasaCrecimiento=%s,
                        GrupoEtnico=%s, TipoCeremonia=%s, SignificadoCultural=%s,
                        TipoMiel=%s, EpocaFloracion=%s, CalidadPolen=%s, AtraccionPolinizadores=%s,
                        TipoProteccion=%s, BeneficiosAmbientales=%s, ZonasAplicacion=%s, CapacidadCapturaCarbon=%s,
                        ColorObtenido=%s, MetodoExtraccion=%s, UsosTintes=%s,
                        TipoAceite=%s, PropiedadesAceite=%s, AplicacionesAceite=%s,
                        TipoBiocombustible=%s, PoderCalorifico=%s, RendimientoPorHectarea=%s
                    WHERE Uso=%s
                ''', (
                    request.form.get('dureza',''), request.form.get('resistencia',''), request.form.get('uso_final',''),
                    request.form.get('parte_comestible',''), request.form.get('forma_consumo',''), request.form.get('valor_nutricional',''),
                    request.form.get('parte_utilizada',''), request.form.get('preparacion',''), request.form.get('enfermedades_tratadas',''),
                    request.form.get('caracteristicas_esteticas',''), request.form.get('ubicacion_recomendada',''), request.form.get('tipo_jardineria',''), request.form.get('coloracion_estacional',''),
                    request.form.get('tipo_artesania',''), request.form.get('tecnicas_elaboracion',''), request.form.get('comunidades_artesanales',''),
                    request.form.get('sistema_agroforestal',''), request.form.get('beneficios_asociados',''), request.form.get('cultivos_compatibles',''), request.form.get('funcion_principal',''),
                    request.form.get('ecosistema_objetivo',''), request.form.get('funcion_ecologica',''), request.form.get('especies_asociadas',''), request.form.get('tasa_crecimiento',''),
                    request.form.get('grupo_etnico',''), request.form.get('tipo_ceremonia',''), request.form.get('significado_cultural',''),
                    request.form.get('tipo_miel',''), request.form.get('epoca_floracion',''), request.form.get('calidad_polen',''), request.form.get('atraccion_polinizadores',''),
                    request.form.get('tipo_proteccion',''), request.form.get('beneficios_ambientales',''), request.form.get('zonas_aplicacion',''), request.form.get('capacidad_captura_carbon',''),
                    request.form.get('color_obtenido',''), request.form.get('metodo_extraccion',''), request.form.get('usos_tintes',''),
                    request.form.get('tipo_aceite',''), request.form.get('propiedades_aceite',''), request.form.get('aplicaciones_aceite',''),
                    request.form.get('tipo_biocombustible',''), request.form.get('poder_calorifico',''), request.form.get('rendimiento_por_hectarea',''),
                    id
                ))
                connection.commit()
                flash('Detalles actualizados exitosamente', 'success')
                return redirect(url_for('.uso_arbol'))
            except Exception as e:
                connection.rollback()
                flash(f'Error al actualizar detalles: {str(e)}', 'error')

        categoria_baja = uso.get('Categoria', '').lower()
        template_map = {
            'maderable': 'editar_uso_maderable.html',
            'comestible': 'editar_uso_comestible.html',
            'medicinal': 'editar_uso_medicinal.html',
            'ornamental': 'editar_uso_ornamental.html',
        }
        template = template_map.get(categoria_baja, 'editar_uso_arbol.html')
        return render_template(template, uso=uso, uso_maderable=detalle, uso_comestible=detalle,
                               uso_medicinal=detalle, uso_ornamental=detalle)

    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('.uso_arbol'))
    finally:
        cursor.close()
        connection.close()


# Ruta para completar detalles específicos de un uso
@usos_bp.route('/uso_arbol/completar/<int:id>/<categoria>', methods=['GET', 'POST'])
def completar_uso_especifico(id, categoria):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('auth.iniciar_sesion'))

    return redirect(url_for('editar_uso_detalle', id=id))


# Ruta para editar los detalles de un uso ornamental
@usos_bp.route('/uso_arbol/ornamental/<int:id>', methods=['GET', 'POST'])
def editar_uso_ornamental(id):
    return redirect(url_for('editar_uso_detalle', id=id))


# Ruta para eliminar un uso de árbol
@usos_bp.route('/uso_arbol/eliminar/<int:id>')
def eliminar_uso_arbol(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('auth.iniciar_sesion'))

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Eliminar detalles desde DetalleUso (tabla normalizada)
        try:
            cursor.execute('DELETE FROM DetalleUso WHERE Uso = %s', (id,))
        except Exception as e:
            pass

        # Finalmente, eliminar el registro principal
        cursor.execute('DELETE FROM UsoArbol WHERE IDUso = %s', (id,))
        connection.commit()
        cursor.close()
        connection.close()
        flash('Uso de árbol eliminado exitosamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar el uso de árbol: {str(e)}', 'error')
    return redirect(url_for('.uso_arbol'))
