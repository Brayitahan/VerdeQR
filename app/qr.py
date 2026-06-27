from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.db import get_db, get_db_connection
from app.utils import get_base_url
import qrcode
import io
import base64
from datetime import datetime

qr_bp = Blueprint('qr', __name__)

@qr_bp.route('/qr', methods=['GET', 'POST'])
def qr():
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('auth.iniciar_sesion'))

    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute('''
            SELECT DISTINCT
                a.IDArbol,
                e.NombreCientifico,
                e.NombreVulgar,
                c.NombreCentro
            FROM Arbol a
            JOIN Especie e ON a.Especie = e.IDEspecie
            JOIN Centro c ON a.Centro = c.IDCentro
            WHERE a.Estado = 1
            ORDER BY e.NombreCientifico, a.IDArbol
        ''')
        arboles = cursor.fetchall()
        print(f"Se encontraron {len(arboles)} arboles para mostrar en el formulario")
        for arbol in arboles:
            print(f"ID: {arbol['IDArbol']}, Nombre: {arbol['NombreCientifico']}")
    except Exception as e:
        print(f"Error al obtener la lista de arboles: {str(e)}")
        arboles = []
    finally:
        cursor.close()

    if request.method == 'POST':
        try:
            arbol_id = request.form.get('arbol_id')
            tamano = int(request.form.get('tamano', 200))

            print(f"Formulario recibido: arbol_id={arbol_id}, tamano={tamano}")
            print(f"Todos los campos del formulario: {request.form}")

            if not arbol_id:
                flash('Por favor seleccione un arbol', 'error')
                return redirect(url_for('.qr'))

            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute('''
                SELECT
                    a.*,
                    e.NombreCientifico,
                    e.NombreVulgar,
                    c.NombreCentro
                FROM Arbol a
                JOIN Especie e ON a.Especie = e.IDEspecie
                JOIN Centro c ON a.Centro = c.IDCentro
                WHERE a.IDArbol = %s
            ''', (arbol_id,))
            arbol = cursor.fetchone()
            cursor.close()
            connection.close()

            if not arbol:
                flash('Arbol no encontrado', 'error')
                return redirect(url_for('.qr'))

            try:
                import qrcode
                from io import BytesIO
                import base64
                from PIL import Image

                base_url = get_base_url()
                arbol_url = f"{base_url}/ver_arbol/{arbol_id}"
                print(f"Generando codigo QR para URL: {arbol_url}")
                print(f"URL base detectada: {base_url}")
                print(f"Headers de request: Host={request.headers.get('Host')}, X-Forwarded-Host={request.headers.get('X-Forwarded-Host')}, X-Original-Host={request.headers.get('X-Original-Host')}")

                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(arbol_url)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")

                buffered = BytesIO()
                img.save(buffered, format="PNG")
                qr_data = base64.b64encode(buffered.getvalue()).decode()
            except Exception as qr_error:
                print(f"Error during QR code generation: {str(qr_error)}")
                import traceback
                print(traceback.format_exc())
                raise

            fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

            connection = get_db_connection()
            cursor = connection.cursor()
            try:
                cursor.execute('SELECT * FROM CodigoQR WHERE Arbol = %s AND Estado = 1', (arbol_id,))
                qr_existente = cursor.fetchone()
                print(f"QR existente: {qr_existente}")
                print(f"Longitud de qr_data: {len(qr_data)} caracteres")

                try:
                    cursor.execute('SELECT IDArbol FROM Arbol WHERE IDArbol = %s', (arbol_id,))
                    arbol_existe = cursor.fetchone()
                    if not arbol_existe:
                        print(f"Error: El arbol con ID {arbol_id} no existe en la base de datos")
                        flash(f'Error: El arbol con ID {arbol_id} no existe en la base de datos', 'error')
                        return redirect(url_for('.qr'))

                    print(f"Tamano de la imagen en base64: {len(qr_data)} bytes")

                    if qr_existente:
                        print(f"Actualizando QR existente con ID {qr_existente['IDQR']} para el arbol {arbol_id}")
                        cursor.execute('''
                            UPDATE CodigoQR
                            SET Codigo = %s,
                                Imagen = %s,
                                FechaGeneracion = NOW()
                            WHERE IDQR = %s
                        ''', (arbol_url, qr_data, qr_existente['IDQR']))
                        connection.commit()
                        flash('Codigo QR actualizado exitosamente', 'success')
                    else:
                        cursor.execute('''
                            INSERT INTO CodigoQR
                            (Arbol, Codigo, Imagen, FechaGeneracion, Estado)
                            VALUES (%s, %s, %s, NOW(), 1)
                        ''', (arbol_id, arbol_url, qr_data))
                        connection.commit()
                        flash('Codigo QR guardado exitosamente', 'success')
                except Exception as db_insert_error:
                    connection.rollback()
                    print(f"Error al guardar el QR en la base de datos: {str(db_insert_error)}")
                    import traceback
                    print(traceback.format_exc())
                    flash(f'Error al guardar el QR: {str(db_insert_error)}', 'error')
                    return redirect(url_for('.qr'))

                cursor.execute('''
                    SELECT
                        qr.IDQR,
                        qr.Arbol,
                        qr.Codigo,
                        qr.Imagen,
                        qr.FechaGeneracion,
                        qr.Estado,
                        e.NombreCientifico,
                        e.NombreVulgar,
                        es.NombreEstado as EstadoNombre
                    FROM CodigoQR qr
                    JOIN Arbol a ON qr.Arbol = a.IDArbol
                    JOIN Especie e ON a.Especie = e.IDEspecie
                    LEFT JOIN Estado es ON qr.Estado = es.IDEstado
                    ORDER BY qr.IDQR DESC
                ''')
                qrs_guardados = cursor.fetchall()
                print(f"Se encontraron {len(qrs_guardados)} QRs guardados")

            except Exception as db_error:
                connection.rollback()
                print(f"Error al guardar el QR en la base de datos: {str(db_error)}")
                flash(f'Error al guardar el QR: {str(db_error)}', 'error')
                qrs_guardados = []

            cursor.execute('SELECT * FROM Arbol')
            arboles = cursor.fetchall()
            cursor.close()
            connection.close()

            return render_template('qr.html',
                                arboles=arboles,
                                qr_data=qr_data,
                                arbol_seleccionado=arbol,
                                fecha_actual=fecha_actual,
                                qrs_guardados=qrs_guardados)

        except Exception as e:
            import traceback
            print(f"Error al generar QR: {str(e)}")
            print(traceback.format_exc())

            if "No module named 'PIL'" in str(e):
                flash('Error al generar el QR: Falta la biblioteca PIL. Por favor, instale Pillow con "pip install Pillow".', 'error')
            else:
                flash(f'Error al generar el QR: {str(e)}', 'error')
            return redirect(url_for('.qr'))

    try:
        print("Obteniendo QRs guardados...")
        connection_qrs = get_db_connection()
        cursor_qrs = connection_qrs.cursor()

        cursor_qrs.execute('''
            SELECT
                qr.IDQR,
                qr.Arbol,
                qr.Codigo,
                qr.Imagen,
                qr.FechaGeneracion,
                qr.Estado,
                e.NombreCientifico,
                e.NombreVulgar,
                es.NombreEstado as EstadoNombre
            FROM CodigoQR qr
            JOIN Arbol a ON qr.Arbol = a.IDArbol
            JOIN Especie e ON a.Especie = e.IDEspecie
            LEFT JOIN Estado es ON qr.Estado = es.IDEstado
            WHERE qr.Estado = 1
            ORDER BY qr.IDQR DESC
        ''')
        qrs_guardados = cursor_qrs.fetchall()
        print(f"Se encontraron {len(qrs_guardados)} QRs guardados en la consulta GET")

        cursor_qrs.close()
        connection_qrs.close()

    except Exception as db_error:
        print(f"Error al obtener los QRs guardados: {str(db_error)}")
        import traceback
        print(traceback.format_exc())
        qrs_guardados = []

    cursor.close()
    connection.close()
    return render_template('qr.html', arboles=arboles, qrs_guardados=qrs_guardados)


@qr_bp.route('/ver_qr/<int:id>')
def ver_qr(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesion para acceder a esta pagina', 'error')
        return redirect(url_for('auth.iniciar_sesion'))

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute('''
            SELECT
                qr.IDQR,
                qr.Arbol,
                qr.Codigo,
                qr.Imagen,
                qr.FechaGeneracion,
                e.NombreCientifico,
                e.NombreVulgar,
                a.Caracteristicas
            FROM CodigoQR qr
            JOIN Arbol a ON qr.Arbol = a.IDArbol
            JOIN Especie e ON a.Especie = e.IDEspecie
            WHERE qr.IDQR = %s
        ''', (id,))
        qr_info = cursor.fetchone()

        cursor.close()
        connection.close()

        if not qr_info:
            flash('Codigo QR no encontrado', 'error')
            return redirect(url_for('.qr'))

        fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        return render_template('ver_qr.html', qr_info=qr_info, fecha_actual=fecha_actual)

    except Exception as e:
        flash(f'Error al obtener el QR: {str(e)}', 'error')
        return redirect(url_for('.qr'))


@qr_bp.route('/eliminar_qr/<int:id>', methods=['POST'])
def eliminar_qr(id):
    if 'usuario' not in session:
        flash('Debes iniciar sesion para acceder a esta pagina', 'error')
        return redirect(url_for('auth.iniciar_sesion'))

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute('SELECT * FROM CodigoQR WHERE IDQR = %s', (id,))
        qr_info = cursor.fetchone()

        if not qr_info:
            flash('Codigo QR no encontrado', 'error')
            return redirect(url_for('.qr'))

        print(f"Eliminando codigo QR con ID: {id}, asociado al arbol ID: {qr_info['Arbol']}")

        cursor.execute('UPDATE CodigoQR SET Estado = 2 WHERE IDQR = %s', (id,))
        connection.commit()

        print(f"Codigo QR eliminado exitosamente")

        cursor.close()
        connection.close()

        flash(f'Codigo QR eliminado exitosamente. Ahora puedes generar un nuevo codigo QR para el arbol.', 'success')
        return redirect(url_for('.qr'))

    except Exception as e:
        print(f"Error al eliminar el QR: {str(e)}")
        import traceback
        print(traceback.format_exc())
        flash(f'Error al eliminar el QR: {str(e)}', 'error')
        return redirect(url_for('.qr'))
