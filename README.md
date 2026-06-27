# VerdeQR - Un dendrólogo en tu bolsillo

Aplicación web educativa para identificar árboles silvestres mediante códigos QR, desarrollada con Flask y MySQL.

## Características

- **Identificación por QR**: Escanea códigos QR para obtener información detallada de árboles
- **Base de datos completa**: Información científica de especies, características, usos y curiosidades
- **12 categorías de uso**: Maderable, medicinal, comestible, ornamental, artesanal, agroforestal, restauración ecológica, cultural/ceremonial, melífero, protección ambiental, tintóreo, oleaginoso, biocombustible
- **Gestión de usuarios**: Registro, autenticación con hash scrypt, roles (Administrador/Visitante)
- **Recuperación de contraseñas**: Vía email con tokens temporales de 6 dígitos
- **Panel de administración**: Gestión completa de árboles, especies, centros, usos, curiosidades, interacciones
- **Generación automática de QR**: Al crear un árbol
- **Responsive**: Optimizado para dispositivos móviles
- **Menú hamburger**: Navegación lateral con perfil de usuario
- **Paginación**: Visualización eficiente de grandes volúmenes de datos

## Tecnologías

- **Backend**: Flask 2.3 (Python)
- **Base de datos**: MySQL con PyMySQL
- **Frontend**: HTML5, CSS3, JavaScript vanilla, Jinja2
- **QR**: qrcode + Pillow (generación), jsQR (lectura)
- **Email**: Flask-Mail (Gmail SMTP)
- **Servidor**: Gunicorn (producción)
- **Despliegue**: Railway.app (Nixpacks)

## Instalación Local

1. Clona el repositorio:
```bash
git clone https://github.com/tu-usuario/verdeqr.git
cd verdeqr
```

2. Crea un entorno virtual:
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

3. Instala las dependencias:
```bash
pip install -r requirements.txt
```

4. Configura la base de datos:
- Crea una base de datos MySQL llamada `VerdeQR`
- Importa el archivo `schema.sql`
- Las credenciales se configuran vía variables de entorno (ver sección abajo)

5. Ejecuta la aplicación:
```bash
python app.py
```

## Despliegue en Railway.app

Configurado para despliegue automático con Nixpacks:

### Variables de entorno

**Opción 1 - DATABASE_URL (Railway MySQL):**
```
DATABASE_URL=mysql://user:pass@host:port/verdeqr
SECRET_KEY=clave_secreta_segura
FLASK_ENV=production
```

**Opción 2 - Variables separadas (local/otros):**
```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=VerdeQR
SECRET_KEY=clave_secreta
FLASK_ENV=production
```

**Email (recuperación de contraseñas):**
```
MAIL_USERNAME=verdeqr.app@gmail.com
MAIL_PASSWORD=clave_app_gmail
```

## Uso

1. **Registro**: Crea una cuenta de usuario (válida contraseña ≥8 chars + 1 mayúscula)
2. **Explorar**: Navega por los árboles disponibles en `/todos_los_arboles`
3. **Escanear QR**: Usa la cámara para escanear códigos QR de árboles
4. **Aprender**: Descubre información detallada sobre cada especie
5. **Administrar**: Los usuarios con rol Administrador gestionan contenido

## Credenciales por Defecto

- **Admin**: jhon123@gmail.com (contraseña en gestor de contraseñas)
- Los nuevos usuarios se registran con rol Visitante

## Licencia

MIT License

## Contacto

- **Proyecto**: VerdeQR - Un dendrólogo en tu bolsillo
- **Stack**: Flask + MySQL + QR + Responsive Design
- **Despliegue**: Railway.app
