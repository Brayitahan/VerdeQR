from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from app.db import get_db, get_db_connection, CaseInsensitiveDictRow
import os
from datetime import datetime, timedelta

arboles_bp = Blueprint('arboles', __name__)

@arboles_bp.route('/')
def inicio():
    # Obtener los árboles, especies y centros para mostrar en la página de inicio
    connection = get_db_connection()
    cursor = connection.cursor()
    arboles_populares = []
    especies_destacadas = []
    centros = []

    try:
        # Obtener los primeros 8 árboles registrados (en orden de registro)
        cursor.execute('''
            SELECT
                a.*,
                e.NombreCientifico as NombreCientifico,
                e.NombreVulgar as NombreVulgar,
                c.NombreCentro as NombreCentro,
                tb.Nombre as TipoBosqueNombre
            FROM Arbol a
            LEFT JOIN Especie e ON a.Especie = e.IDEspecie
            LEFT JOIN Centro c ON a.Centro = c.IDCentro
            LEFT JOIN TipoBosque tb ON a.TipoBosque = tb.IDTipoBosque
            WHERE a.Estado = 1
            ORDER BY a.IDArbol ASC
            LIMIT 8
        ''')
        arboles_populares = cursor.fetchall()

        # Imprimir informaciÃ³n de depuraciÃ³n
        print(f"NÃºmero de Ã¡rboles populares encontrados: {len(arboles_populares)}")

        # Corregir las rutas de las imÃ¡genes para que usen barras normales
        for arbol in arboles_populares:
            if arbol.get('Imagen'):
                # Reemplazar barras invertidas por barras normales
                arbol['Imagen'] = arbol['Imagen'].replace('\\', '/')

        # Obtener todas las especies (hasta 6)
        cursor.execute('''
            SELECT e.*,
                   (SELECT COUNT(*) FROM Arbol a WHERE a.Especie = e.IDEspecie) as NumArboles
            FROM Especie e
            WHERE e.Estado = 1
            ORDER BY NumArboles DESC, e.NombreVulgar ASC
            LIMIT 6
        ''')
        especies_destacadas = cursor.fetchall()

        # Imprimir informaciÃ³n de depuraciÃ³n
        print(f"NÃºmero de especies encontradas: {len(especies_destacadas)}")
        for especie in especies_destacadas:
            print(f"Especie: {especie['NombreVulgar']} (ID: {especie['IDEspecie']})")

        # Obtener usos para cada especie
        for especie in especies_destacadas:
            cursor.execute('''
                SELECT
                    ua.Categoria as TipoUso
                FROM UsoArbol ua
                WHERE ua.Especie = %s AND ua.Estado = 1
                GROUP BY ua.Categoria
            ''', (especie['IDEspecie'],))
            usos = cursor.fetchall()
            especie['Usos'] = [uso['TipoUso'] for uso in usos] if usos else []

        # Obtener los centros con Ã¡rboles registrados
        cursor.execute('''
            SELECT
                c.*,
                COUNT(a.IDArbol) as NumeroArboles
            FROM Centro c
            LEFT JOIN Arbol a ON c.IDCentro = a.Centro
            WHERE c.Estado = 1
            GROUP BY c.IDCentro
            ORDER BY NumeroArboles DESC
            LIMIT 4
        ''')
        centros = cursor.fetchall()

        # Imprimir informaciÃ³n de depuraciÃ³n
        print(f"NÃºmero de centros encontrados: {len(centros)}")
        for centro in centros:
            print(f"Centro: {centro['NombreCentro']} (ID: {centro['IDCentro']})")

    except Exception as e:
        print(f"Error al obtener datos para la pÃ¡gina de inicio: {str(e)}")
        arboles_populares = []
        especies_destacadas = []
        centros = []
    finally:
        cursor.close()
        connection.close()

    return render_template('inicio.html', arboles_populares=arboles_populares, especies_destacadas=especies_destacadas, centros=centros)


@arboles_bp.route('/inicio')
def inicio_redirect():
    return redirect(url_for('.inicio'))


@arboles_bp.route('/index')
def index():
    return render_template('index.html')


@arboles_bp.route('/buscar_arbol')
def buscar_arbol():
    if 'usuario' not in session:
        flash('Debes iniciar sesiÃ³n para buscar Ã¡rboles', 'error')
        return redirect(url_for('auth.iniciar_sesion'))

    query = request.args.get('q', '')
    especie_id = request.args.get('especie_id')
    centro_id = request.args.get('centro_id')

    if not query and not especie_id and not centro_id:
        return redirect(url_for('.principal'))

    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        # Si se proporciona un ID de especie, buscar Ã¡rboles de esa especie
        if especie_id:
            cursor.execute('''
                SELECT
                    a.*,
                    e.NombreCientifico as EspecieNombreCientifico,
                    e.NombreVulgar as EspecieNombreVulgar,
                    c.NombreCentro as CentroNombre,
                    tb.Nombre as TipoBosqueNombre
                FROM Arbol a
                LEFT JOIN Especie e ON a.Especie = e.IDEspecie
                LEFT JOIN Centro c ON a.Centro = c.IDCentro
                LEFT JOIN TipoBosque tb ON a.TipoBosque = tb.IDTipoBosque
                WHERE a.Estado = 1 AND a.Especie = %s
                ORDER BY a.IDArbol DESC
            ''', (especie_id,))
            arboles = cursor.fetchall()

            # Obtener informaciÃ³n de la especie para mostrar en los resultados
            cursor.execute('SELECT * FROM Especie WHERE IDEspecie = %s', (especie_id,))
            especie_info = cursor.fetchone()
            if especie_info:
                query = f"{especie_info['NombreVulgar']} ({especie_info['NombreCientifico']})"

        # Si se proporciona un ID de centro, buscar Ã¡rboles de ese centro
        elif centro_id:
            cursor.execute('''
                SELECT
                    a.*,
                    e.NombreCientifico as EspecieNombreCientifico,
                    e.NombreVulgar as EspecieNombreVulgar,
                    c.NombreCentro as CentroNombre,
                    tb.Nombre as TipoBosqueNombre
                FROM Arbol a
                LEFT JOIN Especie e ON a.Especie = e.IDEspecie
                LEFT JOIN Centro c ON a.Centro = c.IDCentro
                LEFT JOIN TipoBosque tb ON a.TipoBosque = tb.IDTipoBosque
                WHERE a.Estado = 1 AND a.Centro = %s
                ORDER BY a.IDArbol DESC
            ''', (centro_id,))
            arboles = cursor.fetchall()

            # Obtener informaciÃ³n del centro para mostrar en los resultados
            cursor.execute('SELECT * FROM Centro WHERE IDCentro = %s', (centro_id,))
            centro_info = cursor.fetchone()
            if centro_info:
                query = f"Centro: {centro_info['NombreCentro']}"

        # Si se proporciona una consulta de bÃºsqueda, buscar Ã¡rboles que coincidan
        elif query:
            cursor.execute('''
                SELECT
                    a.*,
                    e.NombreCientifico as EspecieNombreCientifico,
                    e.NombreVulgar as EspecieNombreVulgar,
                    c.NombreCentro as CentroNombre,
                    tb.Nombre as TipoBosqueNombre
                FROM Arbol a
                LEFT JOIN Especie e ON a.Especie = e.IDEspecie
                LEFT JOIN Centro c ON a.Centro = c.IDCentro
                LEFT JOIN TipoBosque tb ON a.TipoBosque = tb.IDTipoBosque
                WHERE a.Estado = 1 AND (
                    e.NombreCientifico LIKE %s OR
                    e.NombreVulgar LIKE %s OR
                    a.Caracteristicas LIKE %s OR
                    a.ServiciosEcosistemicos LIKE %s OR
                    a.Descripcion LIKE %s OR
                    tb.Nombre LIKE %s OR
                    c.NombreCentro LIKE %s
                )
                ORDER BY a.IDArbol DESC
            ''', (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
            arboles = cursor.fetchall()

        # Si no hay resultados exactos, buscar resultados similares
        if not arboles:
            # Buscar con tÃ©rminos parciales
            palabras = query.split()
            condiciones = []
            parametros = []

            for palabra in palabras:
                if len(palabra) > 3:  # Solo considerar palabras con mÃ¡s de 3 caracteres
                    condiciones.append("e.NombreCientifico LIKE %s OR e.NombreVulgar LIKE %s OR a.Descripcion LIKE %s")
                    parametros.extend([f'%{palabra}%', f'%{palabra}%', f'%{palabra}%'])

            if condiciones:
                sql_query = f'''
                    SELECT
                        a.*,
                        e.NombreCientifico as EspecieNombreCientifico,
                        e.NombreVulgar as EspecieNombreVulgar,
                        c.NombreCentro as CentroNombre,
                        tb.Nombre as TipoBosqueNombre
                    FROM Arbol a
                    LEFT JOIN Especie e ON a.Especie = e.IDEspecie
                    LEFT JOIN Centro c ON a.Centro = c.IDCentro
                    LEFT JOIN TipoBosque tb ON a.TipoBosque = tb.IDTipoBosque
                    WHERE a.Estado = 1 AND ({" OR ".join(condiciones)})
                    ORDER BY a.IDArbol DESC
                '''
                cursor.execute(sql_query, parametros)
                arboles = cursor.fetchall()

        # Corregir las rutas de las imÃ¡genes
        for arbol in arboles:
            if arbol.get('Imagen'):
                arbol['Imagen'] = arbol['Imagen'].replace('\\', '/')
    except Exception as e:
        print(f"Error al buscar Ã¡rboles: {str(e)}")
        arboles = []
    finally:
        cursor.close()
        connection.close()

    return render_template('resultados_busqueda.html', arboles=arboles, query=query)


@arboles_bp.route('/todos_los_arboles')
def todos_los_arboles():
    if 'usuario' not in session:
        flash('Debes iniciar sesiÃ³n para acceder a esta pÃ¡gina', 'error')
        return redirect(url_for('auth.iniciar_sesion'))

    page = request.args.get('page', 1, type=int)
    per_page = 10

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute('SELECT COUNT(*) as total FROM Arbol WHERE Estado = 1')
        total_arboles = cursor.fetchone()['total']

        offset = (page - 1) * per_page

        cursor.execute('''
            SELECT
                a.*,
                e.NombreCientifico as EspecieNombreCientifico,
                e.NombreVulgar as EspecieNombreVulgar,
                c.NombreCentro as CentroNombre
            FROM Arbol a
            LEFT JOIN Especie e ON a.Especie = e.IDEspecie
            LEFT JOIN Centro c ON a.Centro = c.IDCentro
            WHERE a.Estado = 1
            ORDER BY a.IDArbol DESC
            LIMIT %s OFFSET %s
        ''', (per_page, offset))
        arboles = cursor.fetchall()

        for arbol in arboles:
            if arbol.get('Imagen'):
                arbol['Imagen'] = arbol['Imagen'].replace('\\', '/')

        total_pages = (total_arboles + per_page - 1) // per_page
        has_prev = page > 1
        has_next = page < total_pages

        pagination_info = {
            'page': page,
            'per_page': per_page,
            'total': total_arboles,
            'total_pages': total_pages,
            'has_prev': has_prev,
            'has_next': has_next,
            'prev_num': page - 1 if has_prev else None,
            'next_num': page + 1 if has_next else None
        }

    except Exception as e:
        print(f"Error al obtener todos los Ã¡rboles: {str(e)}")
        arboles = []
        pagination_info = {
            'page': 1,
            'per_page': per_page,
            'total': 0,
            'total_pages': 0,
            'has_prev': False,
            'has_next': False,
            'prev_num': None,
            'next_num': None
        }
    finally:
        cursor.close()
        connection.close()

    return render_template('todos_los_arboles.html', arboles=arboles, pagination=pagination_info)


@arboles_bp.route('/principal')
def principal():
    if 'usuario' not in session:
        flash('Debes iniciar sesiÃ³n para acceder a esta pÃ¡gina', 'error')
        return redirect(url_for('auth.iniciar_sesion'))

    actualizar_sugerencias_antiguas()

    connection = get_db_connection()
    cursor = connection.cursor()
    sugerencias = []
    arboles = []
    total_arboles = 0
    total_usuarios = 0
    total_centros = 0

    try:
        cursor.execute('''
            SELECT s.*, e.NombreEstado as EstadoDescripcion
            FROM sugerencias s
            LEFT JOIN Estado e ON s.Estado = e.IDEstado
            WHERE s.Estado = 1
            ORDER BY s.Fecha DESC
            LIMIT 15
        ''')
        sugerencias = cursor.fetchall()

        cursor.execute('''
            SELECT
                a.*,
                e.NombreCientifico as EspecieNombreCientifico,
                e.NombreVulgar as EspecieNombreVulgar,
                c.NombreCentro as CentroNombre
            FROM Arbol a
            LEFT JOIN Especie e ON a.Especie = e.IDEspecie
            LEFT JOIN Centro c ON a.Centro = c.IDCentro
            ORDER BY a.IDArbol DESC
            LIMIT 12
        ''')
        arboles = cursor.fetchall()

        cursor.execute('SELECT COUNT(*) as total FROM Arbol')
        total_arboles = cursor.fetchone()['total']

        cursor.execute('SELECT COUNT(*) as total FROM Usuario WHERE Activo = TRUE')
        total_usuarios = cursor.fetchone()['total']

        cursor.execute('SELECT COUNT(*) as total FROM Centro')
        total_centros = cursor.fetchone()['total']

        for arbol in arboles:
            if arbol.get('Imagen'):
                arbol['Imagen'] = arbol['Imagen'].replace('\\', '/')

    except Exception as e:
        print(f"Error al obtener datos para la pÃ¡gina principal: {str(e)}")
        sugerencias = []
        arboles = []
        total_arboles = 0
        total_usuarios = 0
        total_centros = 0
    finally:
        cursor.close()
        connection.close()

    return render_template('principal.html', sugerencias=sugerencias, arboles=arboles,
                           total_arboles=total_arboles, total_usuarios=total_usuarios, total_centros=total_centros)


@arboles_bp.route('/arbol', methods=['GET', 'POST'])
def arbol():
    if 'usuario' not in session:
        flash('Debes iniciar sesiÃ³n para acceder a esta pÃ¡gina', 'error')
        return redirect(url_for('auth.iniciar_sesion'))

    if request.method == 'POST':
        try:
            especie = request.form['especie']
            caracteristicas = request.form['caracteristicas']
            servicios_ecosistemicos = request.form['servicios_ecosistemicos']
            tipo_bosque = request.form['tipo_bosque']
            centro = request.form['centro']
            estado = request.form['estado']
            descripcion = request.form.get('descripcion', '')

            imagen_path = None
            if 'imagen' in request.files and request.files['imagen'].filename != '':
                imagen = request.files['imagen']
                upload_folder = os.path.join('static', 'uploads', 'arboles')
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)

                safe_filename = imagen.filename.replace(' ', '_').replace('%', '_').replace('\\', '_').replace('/', '_')
                filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{safe_filename}"
                imagen_path = 'css/js/img/' + filename
                imagen_full_path = os.path.join('static', imagen_path.replace('/', os.sep))

                imagen.save(imagen_full_path)

            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute('''
                INSERT INTO Arbol (Especie, Caracteristicas, ServiciosEcosistemicos, TipoBosque, Centro, Imagen, Descripcion, Estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING IDArbol
            ''', (especie, caracteristicas, servicios_ecosistemicos, tipo_bosque, centro, imagen_path, descripcion, estado))

            arbol_id = cursor.fetchone()['IDArbol']

            try:
                import qrcode
                from io import BytesIO
                import base64
                from app.utils import get_base_url

                base_url = get_base_url()
                arbol_url = f"{base_url}/ver_arbol/{arbol_id}"
                qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
                qr.add_data(arbol_url)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                buffered = BytesIO()
                img.save(buffered, format="PNG")
                qr_data = base64.b64encode(buffered.getvalue()).decode()

                cursor.execute('''
                    INSERT INTO CodigoQR (Arbol, Codigo, Imagen, FechaGeneracion, Estado)
                    VALUES (%s, %s, %s, NOW(), 1)
                ''', (arbol_id, arbol_url, qr_data))
            except Exception as qr_error:
                print(f"Error al generar QR automÃ¡tico: {str(qr_error)}")

            connection.commit()
            cursor.close()
            connection.close()
            flash('Ãrbol registrado exitosamente', 'success')
        except Exception as e:
            flash(f'Error al registrar el Ã¡rbol: {str(e)}', 'error')
            import traceback
            print(f"Error en registro de Ã¡rbol: {str(e)}")
            print(traceback.format_exc())
        return redirect(url_for('.arbol'))

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM Especie WHERE Estado = 1')
    especies = cursor.fetchall()
    cursor.execute('SELECT * FROM TipoBosque')
    tipos_bosque = cursor.fetchall()
    cursor.execute('SELECT * FROM Centro')
    centros = cursor.fetchall()
    cursor.execute('SELECT * FROM Estado')
    estados = cursor.fetchall()

    cursor.execute('''
        SELECT
            a.*,
            e.NombreCientifico as EspecieNombreCientifico,
            e.NombreVulgar as EspecieNombreVulgar,
            tb.Nombre as TipoBosqueNombre,
            c.NombreCentro as CentroNombre,
            es.NombreEstado as EstadoNombre
        FROM Arbol a
        LEFT JOIN Especie e ON a.Especie = e.IDEspecie
        LEFT JOIN TipoBosque tb ON a.TipoBosque = tb.IDTipoBosque
        LEFT JOIN Centro c ON a.Centro = c.IDCentro
        LEFT JOIN Estado es ON a.Estado = es.IDEstado
        ORDER BY a.IDArbol DESC
    ''')
    arboles = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('arbol.html', especies=especies,
                         tipos_bosque=tipos_bosque, centros=centros, estados=estados, arboles=arboles)


@arboles_bp.route('/arbol/editar/<int:id>', methods=['GET', 'POST'])
def editar_arbol(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesiÃ³n para acceder a esta pÃ¡gina', 'error')
        return redirect(url_for('auth.iniciar_sesion'))

    if request.method == 'POST':
        try:
            especie = request.form['especie']
            caracteristicas = request.form['caracteristicas']
            servicios_ecosistemicos = request.form['servicios_ecosistemicos']
            tipo_bosque = request.form['tipo_bosque']
            centro = request.form['centro']
            estado = request.form['estado']
            descripcion = request.form.get('descripcion', '')

            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute('SELECT Imagen FROM Arbol WHERE IDArbol = %s', (id,))
            arbol_actual = cursor.fetchone()
            imagen_actual = arbol_actual['Imagen'] if arbol_actual else None

            imagen_path = imagen_actual
            if 'imagen' in request.files and request.files['imagen'].filename != '':
                imagen = request.files['imagen']
                upload_folder = os.path.join('static', 'uploads', 'arboles')
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)

                safe_filename = imagen.filename.replace(' ', '_').replace('%', '_').replace('\\', '_').replace('/', '_')
                filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{safe_filename}"
                imagen_path = 'css/js/img/' + filename
                imagen_full_path = os.path.join('static', imagen_path.replace('/', os.sep))

                imagen.save(imagen_full_path)

            cursor.execute('''
                UPDATE Arbol SET Especie = %s, Caracteristicas = %s, ServiciosEcosistemicos = %s,
                TipoBosque = %s, Centro = %s, Estado = %s, Imagen = %s, Descripcion = %s
                WHERE IDArbol = %s
            ''', (especie, caracteristicas, servicios_ecosistemicos, tipo_bosque, centro, estado,
                  imagen_path, descripcion, id))
            connection.commit()
            cursor.close()
            connection.close()
            flash('Ãrbol actualizado exitosamente', 'success')
        except Exception as e:
            flash(f'Error al actualizar el Ã¡rbol: {str(e)}', 'error')
            import traceback
            print(f"Error en ediciÃ³n de Ã¡rbol: {str(e)}")
            print(traceback.format_exc())
        return redirect(url_for('.arbol'))

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('''
        SELECT a.*, e.NombreCientifico as EspecieNombreCientifico, e.NombreVulgar as EspecieNombreVulgar
        FROM Arbol a
        LEFT JOIN Especie e ON a.Especie = e.IDEspecie
        WHERE a.IDArbol = %s
    ''', (id,))
    arbol = cursor.fetchone()

    cursor.execute('SELECT * FROM Especie')
    especies = cursor.fetchall()
    cursor.execute('SELECT * FROM UsoArbol')
    usos_arbol = cursor.fetchall()
    cursor.execute('SELECT * FROM TipoBosque')
    tipos_bosque = cursor.fetchall()
    cursor.execute('SELECT * FROM Centro')
    centros = cursor.fetchall()
    cursor.execute('SELECT * FROM Estado')
    estados = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('editar_arbol.html', arbol=arbol, especies=especies,
                         usos_arbol=usos_arbol, tipos_bosque=tipos_bosque, centros=centros, estados=estados)


@arboles_bp.route('/arbol/eliminar/<int:id>')
def eliminar_arbol(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesiÃ³n para acceder a esta pÃ¡gina', 'error')
        return redirect(url_for('auth.iniciar_sesion'))

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        connection.begin()

        try:
            cursor.execute('SELECT COUNT(*) as total FROM MedidasArbol WHERE Arbol = %s', (id,))
            result = cursor.fetchone()
            if result and result['total'] > 0:
                cursor.execute('DELETE FROM MedidasArbol WHERE Arbol = %s', (id,))
                flash(f'Se eliminaron {result["total"]} medidas asociadas al Ã¡rbol', 'info')
        except Exception as medidas_error:
            print(f"Error al verificar medidas del Ã¡rbol: {str(medidas_error)}")

        try:
            cursor.execute('SELECT COUNT(*) as total FROM CodigoQR WHERE Arbol = %s', (id,))
            result = cursor.fetchone()
            if result and result['total'] > 0:
                cursor.execute('DELETE FROM CodigoQR WHERE Arbol = %s', (id,))
                flash(f'Se eliminaron {result["total"]} cÃ³digos QR asociados al Ã¡rbol', 'info')
        except Exception as qr_error:
            pass

        try:
            cursor.execute('UPDATE Arbol SET TipoArbol = NULL WHERE TipoArbol = %s AND IDArbol != %s', (id, id))
            cursor.execute('UPDATE Arbol SET UsoArbol = NULL WHERE UsoArbol = %s AND IDArbol != %s', (id, id))
        except Exception as rel_error:
            pass

        cursor.execute('DELETE FROM Arbol WHERE IDArbol = %s', (id,))

        connection.commit()
        cursor.close()
        connection.close()
        flash('Ãrbol eliminado exitosamente', 'success')
    except Exception as e:
        if 'connection' in locals():
            connection.rollback()
        flash(f'Error al eliminar el Ã¡rbol: {str(e)}', 'error')
        import traceback
        print(traceback.format_exc())

    return redirect(url_for('.arbol'))


@arboles_bp.route('/medidas_arbol', methods=['GET', 'POST'])
def medidas_arbol():
    if 'usuario' not in session:
        flash('Debes iniciar sesiÃ³n para acceder a esta pÃ¡gina', 'error')
        return redirect(url_for('auth.iniciar_sesion'))

    if request.method == 'POST':
        connection = None
        cursor = None
        try:
            arbol = request.form['arbol']
            cap = request.form['cap']
            dap = request.form['dap']
            altura_comercial = request.form['altura_comercial']
            altura_total = request.form['altura_total']
            area_basal = request.form['area_basal']
            estado = request.form['estado']

            if not arbol or not cap or not dap or not altura_comercial or not altura_total or not area_basal or not estado:
                flash('Todos los campos son obligatorios', 'error')
                return redirect(url_for('.medidas_arbol'))

            try:
                cap = float(cap)
                dap = float(dap)
                altura_comercial = float(altura_comercial)
                altura_total = float(altura_total)
                area_basal = float(area_basal)
                arbol_id = int(arbol)
                estado_id = int(estado)
            except ValueError:
                flash('Los valores numÃ©ricos son invÃ¡lidos', 'error')
                return redirect(url_for('.medidas_arbol'))

            connection = get_db_connection()
            cursor = connection.cursor()
            connection.begin()

            cursor.execute('SELECT IDArbol FROM Arbol WHERE IDArbol = %s', (arbol_id,))
            arbol_existe = cursor.fetchone()
            if not arbol_existe:
                flash('El Ã¡rbol seleccionado no existe', 'error')
                return redirect(url_for('.medidas_arbol'))

            cursor.execute('SELECT IDEstado FROM Estado WHERE IDEstado = %s', (estado_id,))
            estado_existe = cursor.fetchone()
            if not estado_existe:
                flash('El estado seleccionado no existe', 'error')
                return redirect(url_for('.medidas_arbol'))

            insert_query = '''
                INSERT INTO MedidasArbol (Arbol, CAP, DAP, AlturaComercial, AlturaTotal, AreaBasal, Estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            '''
            cursor.execute(insert_query, (arbol_id, cap, dap, altura_comercial, altura_total, area_basal, estado_id))

            connection.commit()
            flash('Medidas de Ã¡rbol registradas exitosamente', 'success')

        except Exception as e:
            if connection:
                connection.rollback()
            flash(f'Error al registrar las medidas de Ã¡rbol: {str(e)}', 'error')
            import traceback
            print(f"Error en medidas_arbol: {str(e)}")
            print(traceback.format_exc())
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

        return redirect(url_for('.medidas_arbol'))

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute('SELECT IDArbol, NombreCientifico FROM Arbol WHERE Estado = 1')
        arboles = cursor.fetchall()

        cursor.execute('''
            SELECT
                m.IDMedida,
                m.CAP,
                m.DAP,
                m.AlturaComercial,
                m.AlturaTotal,
                m.AreaBasal,
                m.Arbol,
                m.Estado,
                a.NombreCientifico,
                e.Descripcion as EstadoDescripcion
            FROM MedidasArbol m
            LEFT JOIN Arbol a ON m.Arbol = a.IDArbol
            LEFT JOIN Estado e ON m.Estado = e.IDEstado
            ORDER BY m.IDMedida DESC
        ''')
        medidas = cursor.fetchall()

        cursor.execute('SELECT IDEstado, Descripcion FROM Estado')
        estados = cursor.fetchall()

        cursor.close()
        connection.close()

        return render_template('medidas_arbol.html', medidas=medidas, arboles=arboles, estados=estados)

    except Exception as e:
        flash(f'Error al cargar la pÃ¡gina: {str(e)}', 'error')
        return redirect(url_for('admin.gestion'))


@arboles_bp.route('/medidas_arbol/editar/<int:id>', methods=['GET', 'POST'])
def editar_medida_arbol(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesiÃ³n para acceder a esta pÃ¡gina', 'error')
        return redirect(url_for('auth.iniciar_sesion'))

    if request.method == 'POST':
        connection = None
        cursor = None
        try:
            arbol = request.form['arbol']
            cap = request.form['cap']
            dap = request.form['dap']
            altura_comercial = request.form['altura_comercial']
            altura_total = request.form['altura_total']
            area_basal = request.form['area_basal']
            estado = request.form['estado']

            if not arbol or not cap or not dap or not altura_comercial or not altura_total or not area_basal or not estado:
                flash('Todos los campos son obligatorios', 'error')
                return redirect(url_for('editar_medida_arbol', id=id))

            try:
                cap = float(cap)
                dap = float(dap)
                altura_comercial = float(altura_comercial)
                altura_total = float(altura_total)
                area_basal = float(area_basal)
                arbol_id = int(arbol)
                estado_id = int(estado)
            except ValueError:
                flash('Los valores numÃ©ricos son invÃ¡lidos', 'error')
                return redirect(url_for('editar_medida_arbol', id=id))

            connection = get_db_connection()
            cursor = connection.cursor()
            connection.begin()

            update_query = '''
                UPDATE MedidasArbol SET
                Arbol = %s,
                CAP = %s,
                DAP = %s,
                AlturaComercial = %s,
                AlturaTotal = %s,
                AreaBasal = %s,
                Estado = %s
                WHERE IDMedida = %s
            '''
            cursor.execute(update_query, (arbol_id, cap, dap, altura_comercial, altura_total, area_basal, estado_id, id))

            connection.commit()
            flash('Medidas de Ã¡rbol actualizadas exitosamente', 'success')
        except Exception as e:
            if connection:
                connection.rollback()
            flash(f'Error al actualizar las medidas de Ã¡rbol: {str(e)}', 'error')
            import traceback
            print(f"Error en editar_medida_arbol: {str(e)}")
            print(traceback.format_exc())
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

        return redirect(url_for('.medidas_arbol'))

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute('SELECT * FROM MedidasArbol WHERE IDMedida = %s', (id,))
        medida = cursor.fetchone()

        if not medida:
            flash('Medida no encontrada', 'error')
            return redirect(url_for('.medidas_arbol'))

        cursor.execute('SELECT IDArbol, NombreCientifico FROM Arbol')
        arboles = cursor.fetchall()

        cursor.execute('SELECT IDEstado, Descripcion FROM Estado')
        estados = cursor.fetchall()

        cursor.close()
        connection.close()

        return render_template('editar_medida_arbol.html', medida=medida, arboles=arboles, estados=estados)
    except Exception as e:
        flash(f'Error al cargar la pÃ¡gina: {str(e)}', 'error')
        return redirect(url_for('.medidas_arbol'))


@arboles_bp.route('/medidas_arbol/eliminar/<int:id>')
def eliminar_medida_arbol(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesiÃ³n para acceder a esta pÃ¡gina', 'error')
        return redirect(url_for('auth.iniciar_sesion'))

    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        connection.begin()

        cursor.execute('DELETE FROM MedidasArbol WHERE IDMedida = %s', (id,))

        connection.commit()
        flash('Medidas de Ã¡rbol eliminadas exitosamente', 'success')
    except Exception as e:
        if connection:
            connection.rollback()
        flash(f'Error al eliminar las medidas de Ã¡rbol: {str(e)}', 'error')
        import traceback
        print(f"Error en eliminar_medida_arbol: {str(e)}")
        print(traceback.format_exc())
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return redirect(url_for('.medidas_arbol'))


def actualizar_sugerencias_antiguas():
    try:
        fecha_limite = datetime.now() - timedelta(days=30)
        fecha_limite_str = fecha_limite.strftime('%Y-%m-%d %H:%M:%S')

        connection = get_db_connection()
        cursor = connection.cursor()

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


@arboles_bp.route('/ver_arbol/<int:id>')
def ver_arbol(id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute('''
            SELECT * FROM Arbol WHERE IDArbol = %s
        ''', (id,))

        arbol_base = cursor.fetchone()

        if not arbol_base:
            flash('Ãrbol no encontrado', 'error')
            return redirect(url_for('.principal'))

        cursor.execute('''
            SELECT
                e.NombreCientifico as NombreCientifico,
                e.NombreVulgar as NombreVulgar,
                e.NombreCientifico as EspecieNombreCientifico,
                e.NombreVulgar as EspecieNombreVulgar,
                tb.Nombre as TipoBosqueNombre,
                tb.Descripcion as TipoBosqueDescripcion,
                c.NombreCentro as CentroNombre,
                est.NombreEstado as EstadoDescripcion
            FROM Especie e, TipoBosque tb, Centro c, Estado est
            WHERE e.IDEspecie = %s
            AND tb.IDTipoBosque = %s
            AND c.IDCentro = %s
            AND est.IDEstado = %s
        ''', (arbol_base['Especie'], arbol_base['TipoBosque'], arbol_base['Centro'], arbol_base['Estado']))

        datos_relacionados = cursor.fetchone()

        arbol = CaseInsensitiveDictRow(arbol_base)

        for campo, valor in arbol_base.items():
            arbol[campo] = valor

        arbol['Descripcion'] = arbol_base.get('Descripcion')
        arbol['Caracteristicas'] = arbol_base.get('Caracteristicas')
        arbol['ServiciosEcosistemicos'] = arbol_base.get('ServiciosEcosistemicos')

        if datos_relacionados:
            for campo, valor in datos_relacionados.items():
                arbol[campo] = valor

        descripcion_valor = arbol.get('Descripcion')
        if descripcion_valor is None or descripcion_valor == '':
            descripcion_valor = 'No hay descripciÃ³n disponible para este Ã¡rbol.'

        caracteristicas_valor = arbol.get('Caracteristicas')
        if caracteristicas_valor is None or caracteristicas_valor == '':
            caracteristicas_valor = 'No hay caracterÃsticas disponibles para este Ã¡rbol.'

        servicios_valor = arbol.get('ServiciosEcosistemicos')
        if servicios_valor is None or servicios_valor == '':
            servicios_valor = 'No hay servicios ecosistÃ©micos disponibles para este Ã¡rbol.'

        arbol['DescripcionHTML'] = f'<div class="text-full"><h6 class="text-center mb-3">DescripciÃ³n</h6><p>{descripcion_valor}</p></div>'
        arbol['CaracteristicasHTML'] = f'<div class="text-full"><h6 class="text-center mb-3">CaracterÃsticas</h6><p>{caracteristicas_valor}</p></div>'
        arbol['ServiciosHTML'] = f'<div class="text-full"><h6 class="text-center mb-3">Servicios EcosistÃ©micos</h6><p>{servicios_valor}</p></div>'

        if arbol and arbol['Imagen']:
            arbol['Imagen'] = arbol['Imagen'].replace('\\', '/')
            print(f"Imagen del Ã¡rbol {id}: {arbol['Imagen']}")

        if arbol and 'Centro' in arbol and arbol['Centro']:
            cursor.execute('SELECT COUNT(*) as total FROM Arbol WHERE Centro = %s', (arbol['Centro'],))
            centro_count = cursor.fetchone()
            arbol['ArbolesEnCentro'] = centro_count['total'] if centro_count else 0
        else:
            arbol['ArbolesEnCentro'] = 0

        if arbol and 'Especie' in arbol and arbol['Especie']:
            cursor.execute('''
                SELECT
                    ua.IDUso,
                    ua.Categoria,
                    ua.Nombre
                FROM UsoArbol ua
                WHERE ua.Especie = %s AND ua.Estado = 1
            ''', (arbol['Especie'],))
            usos = cursor.fetchall()

            usos_detallados = []

            for uso in usos:
                uso_detalle = {
                    'IDUso': uso['IDUso'],
                    'Categoria': uso['Categoria'],
                    'Nombre': uso['Nombre'],
                    'Detalles': {}
                }

                cursor.execute('''
                    SELECT * FROM DetalleUso WHERE Uso = %s AND Estado = 1
                ''', (uso['IDUso'],))
                detalle = cursor.fetchone()
                if detalle:
                    uso_detalle['Detalles'] = detalle

                usos_detallados.append(uso_detalle)

            arbol['Usos'] = usos_detallados
        else:
            arbol['Usos'] = []

        if arbol and 'Especie' in arbol and arbol['Especie']:
            cursor.execute('''
                SELECT * FROM CuriosidadesArbol
                WHERE Especie = %s AND Estado = 1
            ''', (arbol['Especie'],))
            curiosidades = cursor.fetchall()
            arbol['Curiosidades'] = curiosidades
        else:
            arbol['Curiosidades'] = []

        if arbol and 'Especie' in arbol and arbol['Especie']:
            cursor.execute('''
                SELECT * FROM InteraccionesEcologicas
                WHERE Especie = %s AND Estado = 1
            ''', (arbol['Especie'],))
            interacciones = cursor.fetchall()
            print(f"Interacciones ecolÃ³gicas para la especie {arbol['Especie']}: {interacciones}")

            for i, interaccion in enumerate(interacciones):
                print(f"InteracciÃ³n {i+1}:")
                print(f"  - IDInteraccion: {interaccion.get('IDInteraccion', 'No disponible')}")
                print(f"  - TipoInteraccion: {interaccion.get('TipoInteraccion', 'No disponible')}")
                print(f"  - Descripcion: {interaccion.get('Descripcion', 'No disponible')}")
            arbol['Interacciones'] = interacciones
        else:
            arbol['Interacciones'] = []

        centros_coordenadas = {
            1: {
                'nombre': '',
                'lat': 10.4631,
                'lng': -73.2532,
                'direccion': ''
            },
            2: {
                'nombre': '',
                'lat': 10.4795,
                'lng': -73.2396,
                'direccion': ''
            }
        }

        centro_id = arbol.get('Centro') if 'Centro' in arbol else None

        cursor.execute('SELECT * FROM Centro WHERE IDCentro = %s', (centro_id,))
        centro_db = cursor.fetchone()

        if centro_db:
            coordenadas_precisas = {
                1: {
                    'lat': 10.4634,
                    'lng': -73.2532,
                    'direccion_precisa': 'Cl. 39 #5-130, Valledupar, Cesar, Colombia'
                },
                2: {
                    'lat': 10.4795,
                    'lng': -73.2396,
                    'direccion_precisa': 'Km 7 VÃ­a a La Paz, Valledupar, Cesar, Colombia'
                }
            }

            coordenadas = coordenadas_precisas.get(centro_id, centros_coordenadas.get(centro_id, {
                'lat': 10.4634,
                'lng': -73.2532
            }))

            direccion = centro_db['Direccion'] if centro_db['Direccion'] else 'DirecciÃ³n no disponible'

            siglas_centro = ''.join([c[0] for c in centro_db['NombreCentro'].split() if c[0].isupper()])

            arbol['CentroInfo'] = {
                'nombre': centro_db['NombreCentro'],
                'siglas': siglas_centro,
                'lat': coordenadas['lat'],
                'lng': coordenadas['lng'],
                'direccion': direccion
            }

            print(f"Centro desde BD: {centro_db['NombreCentro']}")
            print(f"DirecciÃ³n usada: {direccion}")
            print(f"Coordenadas: {coordenadas['lat']}, {coordenadas['lng']}")
        else:
            arbol['CentroInfo'] = {
                'nombre': 'Desconocido',
                'lat': 2.4448,
                'lng': -76.6147,
                'direccion': 'UbicaciÃ³n no disponible'
            }

        cursor.execute('SELECT IDCentro, NombreCentro FROM Centro')
        centros = cursor.fetchall()

        arbol['CentrosArboles'] = {}

        for centro in centros:
            centro_id = centro['IDCentro']
            centro_nombre = centro['NombreCentro']

            cursor.execute('SELECT COUNT(*) as total FROM Arbol WHERE Centro = %s', (centro_id,))
            count = cursor.fetchone()
            total = count['total'] if count else 0

            arbol['CentrosArboles'][centro_id] = {
                'nombre': centro_nombre,
                'total': total,
                'siglas': ''.join([c[0] for c in centro_nombre.split() if c[0].isupper()])
            }

            if centro_id == 2:
                arbol['ArbolesEnCBC'] = total
            elif centro_id == 1:
                arbol['ArbolesEnCIGEC'] = total

        try:
            cursor.execute('SELECT * FROM CodigoQR WHERE Arbol = %s AND Estado = 1', (id,))
            qr_info = cursor.fetchone()
            if qr_info:
                print(f"QR encontrado para el Ã¡rbol {id}: {qr_info['IDQR']}")
                arbol['QR'] = qr_info['Imagen']
            else:
                print(f"No se encontrÃ³ QR activo para el Ã¡rbol {id}")
                arbol['QR'] = None
        except Exception as qr_error:
            print(f"Error al buscar QR para el Ã¡rbol {id}: {str(qr_error)}")
            arbol['QR'] = None

        medidas = []
        try:
            cursor.execute("SELECT COUNT(*) AS table_exists FROM information_schema.tables WHERE TABLE_NAME = 'MedidasArbol'")
            if cursor.fetchone()['table_exists'] > 0:
                cursor.execute('''
                    SELECT *
                    FROM MedidasArbol
                    WHERE Arbol = %s
                    ORDER BY IDMedida DESC
                ''', (id,))
                medidas = cursor.fetchall()
                print(f"Se encontraron {len(medidas)} medidas para el Ã¡rbol {id}")
            else:
                print(f"La tabla MedidasArbol no existe en la base de datos")
        except Exception as medidas_error:
            print(f"Error al buscar medidas para el Ã¡rbol {id}: {str(medidas_error)}")

        cursor.close()
        connection.close()

        print("\n==== VALORES FINALES ANTES DE RENDERIZAR ====\n")
        print(f"Descripcion: {arbol.get('Descripcion', 'NO EXISTE')}")
        print(f"Caracteristicas: {arbol.get('Caracteristicas', 'NO EXISTE')}")
        print(f"ServiciosEcosistemicos: {arbol.get('ServiciosEcosistemicos', 'NO EXISTE')}")

        if arbol.get('Descripcion') is None or arbol.get('Descripcion') == '':
            arbol['Descripcion'] = 'No hay descripciÃ³n disponible para este Ã¡rbol.'
            print("Forzando valor predeterminado para Descripcion en la verificaciÃ³n final")

        if arbol.get('Caracteristicas') is None or arbol.get('Caracteristicas') == '':
            arbol['Caracteristicas'] = 'No hay caracterÃsticas disponibles para este Ã¡rbol.'
            print("Forzando valor predeterminado para Caracteristicas en la verificaciÃ³n final")

        if arbol.get('ServiciosEcosistemicos') is None or arbol.get('ServiciosEcosistemicos') == '':
            arbol['ServiciosEcosistemicos'] = 'No hay servicios ecosistÃ©micos disponibles para este Ã¡rbol.'
            print("Forzando valor predeterminado para ServiciosEcosistemicos en la verificaciÃ³n final")

        return render_template('ver_arbol.html', arbol=arbol, medidas=medidas)
    except Exception as e:
        flash(f'Error al cargar el Ã¡rbol: {str(e)}', 'error')
        return redirect(url_for('.principal'))


@arboles_bp.route('/centro', methods=['GET', 'POST'], endpoint='centro')
def centro_view():
    if 'usuario' not in session:
        flash('Debes iniciar sesiÃ³n para acceder a esta pÃ¡gina', 'error')
        return redirect(url_for('auth.iniciar_sesion'))

    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            direccion = request.form['direccion']
            estado = request.form['estado']

            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute('''
                INSERT INTO Centro (NombreCentro, Direccion, Estado)
                VALUES (%s, %s, %s)
            ''', (nombre, direccion, estado))
            connection.commit()
            cursor.close()
            connection.close()
            flash('Centro registrado exitosamente', 'success')
        except Exception as e:
            flash(f'Error al registrar el centro: {str(e)}', 'error')
        return redirect(url_for('centro'))

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute('''
        SELECT c.*, e.NombreEstado as EstadoNombre
        FROM Centro c
        LEFT JOIN Estado e ON c.Estado = e.IDEstado
        ORDER BY c.IDCentro DESC
    ''')
    centros = cursor.fetchall()

    cursor.execute('SELECT * FROM Estado')
    estados = cursor.fetchall()

    cursor.close()
    connection.close()
    return render_template('centro.html', centros=centros, estados=estados)


@arboles_bp.route('/centro/editar/<int:id>', methods=['GET', 'POST'], endpoint='editar_centro')
def editar_centro_view(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesiÃ³n para acceder a esta pÃ¡gina', 'error')
        return redirect(url_for('auth.iniciar_sesion'))

    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            direccion = request.form['direccion']
            estado = request.form['estado']

            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute('''
                UPDATE Centro SET NombreCentro = %s, Direccion = %s, Estado = %s
                WHERE IDCentro = %s
            ''', (nombre, direccion, estado, id))
            connection.commit()
            cursor.close()
            connection.close()
            flash('Centro actualizado exitosamente', 'success')
        except Exception as e:
            flash(f'Error al actualizar el centro: {str(e)}', 'error')
        return redirect(url_for('centro'))

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM Centro WHERE IDCentro = %s', (id,))
    centro = cursor.fetchone()

    cursor.execute('SELECT * FROM Estado')
    estados = cursor.fetchall()

    cursor.close()
    connection.close()
    return render_template('editar_centro.html', centro=centro, estados=estados)


@arboles_bp.route('/centro/eliminar/<int:id>', endpoint='eliminar_centro')
def eliminar_centro_view(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesiÃ³n para acceder a esta pÃ¡gina', 'error')
        return redirect(url_for('auth.iniciar_sesion'))

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute('SELECT COUNT(*) as total FROM Arbol WHERE Centro = %s', (id,))
        result = cursor.fetchone()
        if result and result['total'] > 0:
            flash(f'No se puede eliminar el centro porque estÃ¡ siendo utilizado en {result["total"]} Ã¡rboles. Primero debe reasignar o eliminar estos Ã¡rboles.', 'error')
            return redirect(url_for('centro'))

        cursor.execute('DELETE FROM Centro WHERE IDCentro = %s', (id,))
        connection.commit()
        cursor.close()
        connection.close()
        flash('Centro eliminado exitosamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar el centro: {str(e)}', 'error')
    return redirect(url_for('centro'))
