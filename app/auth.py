from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.db import get_db, get_db_connection
from app.utils import generar_token, obtener_avatar_predeterminado
from flask_mail import Message
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash, generate_password_hash
import re
import os

# mail is imported from the main app module where it's instantiated
from app import mail

auth_bp = Blueprint('auth', __name__)

# Expresión regular para validar la contraseña
PASSWORD_REGEX = re.compile(r'^(?=.*[A-Z]).{8,}$')

# Ruta para el registro de nuevos usuarios
@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombres = request.form['nombres']
        apellidos = request.form['apellidos']
        correo = request.form['correo']
        telefono = request.form['telefono']
        contrasena = request.form['contrasena']
        validar_contrasena = request.form['validar_contrasena']

        # Validar que las contraseñas coincidan
        if contrasena != validar_contrasena:
            return jsonify({
                'success': False,
                'message': 'Las contraseñas no coinciden'
            })

        # Validar la contraseña con la expresión regular
        if not PASSWORD_REGEX.match(contrasena):
            return jsonify({
                'success': False,
                'message': 'La contraseña debe tener al menos 8 caracteres y una letra mayúscula'
            })

        connection = get_db_connection()
        cursor = connection.cursor()
        try:
            # Verificar si el correo ya está registrado
            cursor.execute('SELECT * FROM Usuario WHERE Correo = %s', (correo,))
            if cursor.fetchone():
                return jsonify({
                    'success': False,
                    'message': 'El correo electrónico ya está registrado'
                })

            # Determinar el avatar predeterminado basado en el nombre
            avatar_predeterminado = obtener_avatar_predeterminado(nombres)

            # Insertar el nuevo usuario con contraseña hasheada
            contrasena_hash = generate_password_hash(contrasena)
            cursor.execute('''
                INSERT INTO Usuario (Nombre, Correo, Telefono, Contraseña, Estado, Imagen)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (nombres + ' ' + apellidos, correo, telefono, contrasena_hash, 1, avatar_predeterminado))  # Estado 1 = Activo
            connection.commit()
            flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
            return jsonify({
                'success': True,
                'message': 'Registro exitoso',
                'redirect': url_for('.iniciar_sesion')
            })
        except Exception as e:
            connection.rollback()
            return jsonify({
                'success': False,
                'message': f'Error al registrar el usuario: {str(e)}'
            })
        finally:
            cursor.close()
            connection.close()

    return render_template('registro.html')

# Ruta para la página de inicio de sesión
@auth_bp.route('/iniciar_sesion', methods=['GET', 'POST'])
def iniciar_sesion():
    if request.method == 'POST':
        correo = request.form['correo']
        contrasena = request.form['contrasena']

        if not correo or not contrasena:
            return jsonify({
                'success': False,
                'message': 'Por favor ingrese correo y contraseña'
            })

        cursor = get_db().cursor()
        try:
            # Verificar credenciales y obtener roles
            cursor.execute("""
                SELECT u.*, GROUP_CONCAT(r.NombreRol) as roles
                FROM Usuario u
                LEFT JOIN UsuarioRol ur ON u.IDUsuario = ur.Usuario
                LEFT JOIN Rol r ON ur.Rol = r.IDRol
                WHERE u.Correo = %s AND u.Estado = 1
                GROUP BY u.IDUsuario
            """, (correo,))
            usuario = cursor.fetchone()
            if not usuario or not check_password_hash(usuario['Contraseña'], contrasena):
                usuario = None

            if usuario:
                # Crear sesión con los roles como lista
                # Dividir el nombre completo en nombres y apellidos para mantener compatibilidad
                nombre_completo = usuario['Nombre'] if usuario['Nombre'] else ''
                partes_nombre = nombre_completo.split(' ', 1)
                nombres = partes_nombre[0] if len(partes_nombre) > 0 else ''
                apellidos = partes_nombre[1] if len(partes_nombre) > 1 else ''

                # Si el usuario no tiene imagen, asignar un avatar predeterminado
                imagen_usuario = usuario['Imagen']
                if not imagen_usuario:
                    # Determinar el avatar predeterminado basado en el nombre
                    imagen_usuario = obtener_avatar_predeterminado(nombres)

                    # Actualizar la imagen del usuario en la base de datos
                    try:
                        cursor.execute('UPDATE Usuario SET Imagen = %s WHERE IDUsuario = %s',
                                      (imagen_usuario, usuario['IDUsuario']))
                        get_db().commit()
                    except Exception as e:
                        print(f"Error al actualizar avatar predeterminado: {str(e)}")

                session['usuario'] = {
                    'IDUsuario': usuario['IDUsuario'],
                    'Nombre': nombre_completo,
                    'Nombres': nombres,
                    'Apellidos': apellidos,
                    'Correo': usuario['Correo'],
                    'Telefono': usuario['Telefono'],
                    'Imagen': imagen_usuario,
                    'roles': usuario['roles'].split(',') if usuario['roles'] else []
                }

                # Imprimir información de depuración
                print(f"Sesión de usuario creada: {session['usuario']}")

                # No usar flash aquí porque ya se muestra una notificación modal en el frontend
                return jsonify({
                    'success': True,
                    'message': 'Inicio de sesión exitoso',
                    'redirect': url_for('arboles.principal')
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Correo o contraseña incorrectos'
                })

        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error al iniciar sesión: {str(e)}'
            })
        finally:
            cursor.close()

    return render_template('iniciar_sesion.html')

# Ruta para cerrar sesión
@auth_bp.route('/cerrar_sesion')
def cerrar_sesion():
    session.clear()
    # Redirigir a inicio con un parámetro para mostrar notificación modal
    return redirect(url_for('arboles.inicio', logout_success=1))

# Ruta para olvidar contraseña
@auth_bp.route('/olvidar_contrasena', methods=['GET', 'POST'])
def olvidar_contrasena():
    if request.method == 'POST':
        correo = request.form['correo']

        # Verificar si el correo existe en la base de datos
        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            cursor.execute('SELECT IDUsuario, Nombre FROM Usuario WHERE Correo = %s AND Estado = 1', (correo,))
            usuario = cursor.fetchone()

            if not usuario:
                return jsonify({
                    'success': False,
                    'message': 'No existe una cuenta con este correo electrónico'
                })

            # Generar un token de 6 dígitos
            token = generar_token(6)

            # Calcular la fecha de expiración (30 minutos)
            fecha_expiracion = datetime.now() + timedelta(minutes=30)

            # Guardar el token en la base de datos
            cursor.execute('''
                INSERT INTO tokens_recuperacion (Usuario, Token, FechaExpiracion, Estado)
                VALUES (%s, %s, %s, 1)
            ''', (usuario['IDUsuario'], token, fecha_expiracion))
            connection.commit()

            # Enviar el correo electrónico con el token
            try:
                msg = Message(
                    'Recuperación de contraseña - VerdeQR',
                    recipients=[correo]
                )
                msg.body = f'''Hola {usuario['Nombre']},

Has solicitado restablecer tu contraseña en VerdeQR.

Tu código de verificación es: {token}

Este código expirará en 30 minutos.

Si no solicitaste este cambio, puedes ignorar este correo.

Saludos,
El equipo de VerdeQR
'''
                try:
                    mail.send(msg)
                except Exception as e:
                    print(f"Error al enviar correo (ignorado en modo prueba): {str(e)}")

                return jsonify({
                    'success': True,
                    'message': 'Se ha enviado un código de verificación a tu correo electrónico',
                    'redirect': url_for('.restablecer_contrasena')
                })
            except Exception as e:
                print(f"Error al enviar el correo: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': 'Error al enviar el correo electrónico. Por favor, intenta nuevamente.'
                })
        except Exception as e:
            connection.rollback()
            print(f"Error en olvidar_contrasena: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error al procesar la solicitud. Por favor, intenta nuevamente.'
            })
        finally:
            cursor.close()
            connection.close()

    return render_template('olvidar_contrasena.html')

# Ruta para restablecer contraseña
@auth_bp.route('/restablecer_contrasena', methods=['GET', 'POST'])
def restablecer_contrasena():
    if request.method == 'POST':
        print("Recibida solicitud POST para restablecer contraseña")

        # Verificar si la solicitud es JSON o form-data
        if request.is_json:
            data = request.get_json()
            codigo = data.get('codigo')
            contrasena = data.get('contrasena')
            confirmar_contrasena = data.get('confirmar_contrasena')
        else:
            codigo = request.form.get('codigo')
            contrasena = request.form.get('contrasena')
            confirmar_contrasena = request.form.get('confirmar_contrasena')

        print(f"Código: {codigo}, Contraseña: {contrasena}, Confirmar: {confirmar_contrasena}")

        # Verificar que las contraseñas coincidan
        if contrasena != confirmar_contrasena:
            return jsonify({
                'success': False,
                'message': 'Las contraseñas no coinciden'
            })

        # Validar la contraseña con la expresión regular
        if not PASSWORD_REGEX.match(contrasena):
            return jsonify({
                'success': False,
                'message': 'La contraseña debe tener al menos 8 caracteres y una letra mayúscula'
            })

        # Verificar que el código sea válido
        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            # Buscar el token en la base de datos
            cursor.execute('''
                SELECT tr.*, u.Correo
                FROM tokens_recuperacion tr
                JOIN Usuario u ON tr.Usuario = u.IDUsuario
                WHERE tr.Token = %s AND tr.Estado = 1 AND tr.FechaExpiracion > NOW()
            ''', (codigo,))
            token_info = cursor.fetchone()

            if not token_info:
                return jsonify({
                    'success': False,
                    'message': 'El código de verificación es inválido o ha expirado'
                })

            # Actualizar la contraseña del usuario con hash
            contrasena_hash = generate_password_hash(contrasena)
            cursor.execute('''
                UPDATE Usuario
                SET Contraseña = %s
                WHERE IDUsuario = %s
            ''', (contrasena_hash, token_info['Usuario']))

            # Marcar el token como usado
            cursor.execute('''
                UPDATE tokens_recuperacion
                SET Estado = 2
                WHERE IDToken = %s
            ''', (token_info['IDToken'],))

            connection.commit()

            return jsonify({
                'success': True,
                'message': 'Contraseña actualizada exitosamente',
                'redirect': url_for('.iniciar_sesion')
            })
        except Exception as e:
            connection.rollback()
            print(f"Error en restablecer_contrasena: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'Error al procesar la solicitud. Por favor, intenta nuevamente.'
            })
        finally:
            cursor.close()
            connection.close()

    return render_template('restablecer_contrasena.html')

# Ruta para la gestión de perfil
@auth_bp.route('/perfil', methods=['GET', 'POST'])
def perfil():
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('.iniciar_sesion'))

    connection = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Cargar la información actualizada del usuario desde la base de datos
        cursor.execute('SELECT * FROM Usuario WHERE IDUsuario = %s', (session['usuario']['IDUsuario'],))
        usuario_db = cursor.fetchone()

        if usuario_db:
            # Actualizar la sesión con los datos más recientes
            nombre_completo = usuario_db['Nombre'] if usuario_db['Nombre'] else ''
            partes_nombre = nombre_completo.split(' ', 1)
            nombres = partes_nombre[0] if len(partes_nombre) > 0 else ''
            apellidos = partes_nombre[1] if len(partes_nombre) > 1 else ''

            session['usuario']['Nombre'] = nombre_completo
            session['usuario']['Nombres'] = nombres
            session['usuario']['Apellidos'] = apellidos
            session['usuario']['Correo'] = usuario_db['Correo']
            session['usuario']['Telefono'] = usuario_db['Telefono']
            session['usuario']['Imagen'] = usuario_db['Imagen']

            # Imprimir información de depuración
            print(f"Información de usuario actualizada en sesión: {session['usuario']}")

        if request.method == 'POST':
            nombres = request.form['nombres']
            apellidos = request.form['apellidos']
            correo = request.form['correo']
            telefono = request.form['telefono']
            nombre_completo = nombres + ' ' + apellidos

            # Verificar si el correo ya existe (excluyendo el usuario actual)
            cursor.execute('''
                SELECT IDUsuario FROM Usuario
                WHERE Correo = %s AND IDUsuario != %s
            ''', (correo, session['usuario']['IDUsuario']))

            if cursor.fetchone():
                flash('El correo electrónico ya está registrado por otro usuario', 'error')
                return redirect(url_for('.perfil'))

            # Obtener la imagen actual del usuario
            cursor.execute('SELECT Imagen FROM Usuario WHERE IDUsuario = %s', (session['usuario']['IDUsuario'],))
            usuario_actual = cursor.fetchone()
            imagen_actual = usuario_actual['Imagen'] if usuario_actual else None

            # Procesar la imagen si se ha subido una nueva
            imagen_path = imagen_actual
            if 'avatar' in request.files and request.files['avatar'].filename != '':
                imagen = request.files['avatar']
                # Crear directorio para imágenes si no existe
                upload_folder = os.path.join('static', 'uploads', 'usuarios')
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)

                # Guardar la imagen con un nombre único basado en la fecha y el ID de usuario
                safe_filename = imagen.filename.replace(' ', '_').replace('%', '_').replace('\\', '_').replace('/', '_')
                filename = f"usuario_{session['usuario']['IDUsuario']}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{safe_filename}"
                # Usar rutas con barras normales para URLs
                imagen_path = f'uploads/usuarios/{filename}'
                imagen_full_path = os.path.join('static', imagen_path)

                imagen.save(imagen_full_path)

            cursor.execute('''
                UPDATE Usuario
                SET Nombre = %s, Correo = %s, Telefono = %s, Imagen = %s
                WHERE IDUsuario = %s
            ''', (nombre_completo, correo, telefono, imagen_path, session['usuario']['IDUsuario']))
            connection.commit()

            # Actualizar datos en la sesión solo después de la actualización exitosa
            session['usuario']['Nombre'] = nombre_completo
            session['usuario']['Correo'] = correo
            # Mantener nombres y apellidos separados en la sesión para la interfaz
            session['usuario']['Nombres'] = nombres
            session['usuario']['Apellidos'] = apellidos
            session['usuario']['Telefono'] = telefono
            session['usuario']['Imagen'] = imagen_path

            # Forzar la actualización de la sesión
            session.modified = True

            # Imprimir información de depuración
            print(f"Perfil actualizado en sesión: {session['usuario']}")

            flash('Perfil actualizado exitosamente', 'success')
    except Exception as e:
        flash(f'Error al actualizar el perfil: {str(e)}', 'error')
    finally:
        if connection:
            connection.close()

    # Obtener la fecha de registro del usuario
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('SELECT DATE_FORMAT(FechaRegistro, "%d/%m/%Y") as FechaRegistro FROM Usuario WHERE IDUsuario = %s',
                       (session['usuario']['IDUsuario'],))
        resultado = cursor.fetchone()
        fecha_registro = resultado['FechaRegistro'] if resultado and 'FechaRegistro' in resultado else 'No disponible'
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"Error al obtener fecha de registro: {str(e)}")
        fecha_registro = 'No disponible'

    return render_template('perfil.html', fecha_registro=fecha_registro)

# Ruta para cambiar contraseña
@auth_bp.route('/cambiar_contrasena', methods=['POST'])
def cambiar_contrasena():
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('.iniciar_sesion'))

    try:
        contrasena_actual = request.form['contrasena_actual']
        nueva_contrasena = request.form['nueva_contrasena']
        confirmar_contrasena = request.form['confirmar_contrasena']

        if nueva_contrasena != confirmar_contrasena:
            flash('Las contraseñas no coinciden', 'error')
            return redirect(url_for('.perfil'))

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('SELECT Contraseña FROM Usuario WHERE IDUsuario = %s', (session['usuario']['IDUsuario'],))
        usuario = cursor.fetchone()

        if not usuario or not check_password_hash(usuario['Contraseña'], contrasena_actual):
            flash('La contraseña actual es incorrecta', 'error')
            cursor.close()
            connection.close()
            return redirect(url_for('.perfil'))

        nueva_contrasena_hash = generate_password_hash(nueva_contrasena)
        cursor.execute('''
            UPDATE Usuario SET Contraseña = %s
            WHERE IDUsuario = %s
        ''', (nueva_contrasena_hash, session['usuario']['IDUsuario']))
        connection.commit()
        cursor.close()
        connection.close()

        flash('Contraseña actualizada exitosamente', 'success')
    except Exception as e:
        flash(f'Error al cambiar la contraseña: {str(e)}', 'error')
    return redirect(url_for('.perfil'))

# Ruta para actualizar el avatar del usuario
@auth_bp.route('/actualizar_avatar', methods=['POST'])
def actualizar_avatar():
    if 'usuario' not in session:
        return jsonify({
            'success': False,
            'message': 'Debes iniciar sesión para realizar esta acción'
        }), 401

    try:
        if 'avatar' not in request.files or request.files['avatar'].filename == '':
            return jsonify({
                'success': False,
                'message': 'No se ha seleccionado ninguna imagen'
            }), 400

        # Obtener la imagen actual del usuario
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('SELECT Imagen FROM Usuario WHERE IDUsuario = %s', (session['usuario']['IDUsuario'],))
        usuario_actual = cursor.fetchone()
        imagen_actual = usuario_actual['Imagen'] if usuario_actual else None

        # Procesar la nueva imagen
        imagen = request.files['avatar']
        # Crear directorio para imágenes si no existe
        upload_folder = os.path.join('static', 'uploads', 'usuarios')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        # Guardar la imagen con un nombre único
        safe_filename = imagen.filename.replace(' ', '_').replace('%', '_').replace('\\', '_').replace('/', '_')
        filename = f"usuario_{session['usuario']['IDUsuario']}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{safe_filename}"
        imagen_path = f'uploads/usuarios/{filename}'
        imagen_full_path = os.path.join('static', imagen_path)

        imagen.save(imagen_full_path)

        # Actualizar la base de datos
        cursor.execute('UPDATE Usuario SET Imagen = %s WHERE IDUsuario = %s',
                       (imagen_path, session['usuario']['IDUsuario']))
        connection.commit()

        # Actualizar la sesión
        session['usuario']['Imagen'] = imagen_path

        # Forzar la actualización de la sesión
        session.modified = True

        # Imprimir información de depuración
        print(f"Avatar actualizado en sesión: {session['usuario']['Imagen']}")

        cursor.close()
        connection.close()

        return jsonify({
            'success': True,
            'message': 'Avatar actualizado exitosamente',
            'imagen_path': url_for('static', filename=imagen_path) if imagen_path else ''
        })
    except Exception as e:
        print(f"Error al actualizar avatar: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': f'Error al actualizar el avatar: {str(e)}'
        }), 500

# Ruta para eliminar el avatar del usuario
@auth_bp.route('/eliminar_avatar', methods=['POST'])
def eliminar_avatar():
    if 'usuario' not in session:
        return jsonify({
            'success': False,
            'message': 'Debes iniciar sesión para realizar esta acción'
        }), 401

    try:
        # Determinar el avatar predeterminado basado en el nombre
        nombre = session['usuario']['Nombres']
        avatar_predeterminado = obtener_avatar_predeterminado(nombre)

        # Actualizar la base de datos
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('UPDATE Usuario SET Imagen = %s WHERE IDUsuario = %s',
                      (avatar_predeterminado, session['usuario']['IDUsuario']))
        connection.commit()

        # Actualizar la sesión
        session['usuario']['Imagen'] = avatar_predeterminado
        session.modified = True

        cursor.close()
        connection.close()

        # Imprimir información de depuración
        print(f"Avatar predeterminado: {avatar_predeterminado}")
        print(f"URL completa: {url_for('static', filename=avatar_predeterminado)}")

        # Asegurarnos de que la imagen exista
        imagen_path = url_for('static', filename=avatar_predeterminado)

        return jsonify({
            'success': True,
            'message': 'Avatar eliminado exitosamente',
            'imagen_path': imagen_path
        })
    except Exception as e:
        print(f"Error al eliminar avatar: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': f'Error al eliminar el avatar: {str(e)}'
        }), 500

# Ruta para eliminar cuenta
@auth_bp.route('/eliminar_cuenta', methods=['POST'])
def eliminar_cuenta():
    if 'usuario' not in session:
        flash('Debes iniciar sesión para acceder a esta página', 'error')
        return redirect(url_for('.iniciar_sesion'))

    try:
        contrasena = request.form['contrasena']

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('SELECT Contraseña FROM Usuario WHERE IDUsuario = %s', (session['usuario']['IDUsuario'],))
        usuario = cursor.fetchone()

        if usuario['Contraseña'] != contrasena:
            flash('Contraseña incorrecta', 'error')
            cursor.close()
            connection.close()
            return redirect(url_for('.perfil'))

        cursor.execute('DELETE FROM Usuario WHERE IDUsuario = %s', (session['usuario']['IDUsuario'],))
        connection.commit()
        cursor.close()
        connection.close()

        session.clear()
        flash('Cuenta eliminada exitosamente', 'success')
        return redirect(url_for('arboles.inicio'))
    except Exception as e:
        flash(f'Error al eliminar la cuenta: {str(e)}', 'error')
        return redirect(url_for('.perfil'))
