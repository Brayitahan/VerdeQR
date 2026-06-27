# VerdeQR - Documentación Técnica Completa

## Resumen Ejecutivo

**VerdeQR** es una aplicación web educativa que funciona como "un dendrólogo en tu bolsillo". Permite a los usuarios identificar y aprender sobre árboles silvestres mediante códigos QR, proporcionando información científica detallada sobre especies, características, usos y curiosidades.

## Arquitectura del Sistema

### Stack Tecnológico

**Backend:**
- **Framework**: Flask 2.3.2 (Python)
- **Base de Datos**: MySQL con PyMySQL 1.1.0
- **ORM**: Consultas SQL nativas (sin ORM)
- **Servidor**: Gunicorn 21.2.0 para producción
- **Auth**: Flask sessions + werkzeug scrypt (hash de contraseñas)

**Frontend:**
- **Templates**: Jinja2 2.1.2
- **Estilos**: CSS3 puro con diseño responsive
- **JavaScript**: Vanilla JS para interactividad
- **QR Scanner**: jsQR library para lectura de códigos

**Funcionalidades Especiales:**
- **Generación QR**: qrcode 7.4.2 + Pillow 10.1.0 (auto al crear árbol)
- **Email**: Flask-Mail 0.9.1 para recuperación de contraseñas
- **Gestión de archivos**: Subida y procesamiento de imágenes

### Patrón de Arquitectura

```
  Frontend               Backend              Base de Datos
 (Templates)             (Flask)                 (MySQL)
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ HTML/CSS/JS  │◄───►│ 7 Blueprints │◄───►│ 10 Tablas    │
│ QR Scanner   │     │ Rutas/Lógica │     │ + 2 Soporte  │
│ Responsive   │     │ Auth/Roles   │     │ Relaciones   │
└──────────────┘     └──────────────┘     └──────────────┘
```

### Blueprints del Sistema

| Blueprint | Archivo | Rutas |
|-----------|---------|-------|
| `auth_bp` | `app/auth.py` | Registro, login, perfil, recuperación |
| `arboles_bp` | `app/arboles.py` | Árboles (CRUD + vista pública), centros, búsqueda |
| `admin_bp` | `app/admin.py` | Panel admin, usuarios, sugerencias, curiosidades, interacciones |
| `especies_bp` | `app/especies.py` | Especies, usos por especie, tipos de bosque |
| `usos_bp` | `app/usos.py` | Gestión de usos con DetalleUso (12 categorías) |
| `qr_bp` | `app/qr.py` | Generación y visualización de QR |
| `info_bp` | `app/info.py` | Páginas estáticas (contacto, FAQ, privacidad) |

## Estructura de Base de Datos

### Tablas

**Entidades Core (7):**
- `Estado` - Catálogo de estados (1=Activo, 2=Inactivo)
- `Rol` - Roles de usuario (Administrador, Visitante)
- `Usuario` - Gestión de usuarios (contraseña hasheada con scrypt, VARCHAR(255))
- `UsuarioRol` - Relación N:N entre usuarios y roles
- `Especie` - Información científica de especies arbóreas
- `Centro` - Ubicaciones donde se encuentran los árboles
- `TipoBosque` - Tipos de ecosistemas forestales

**Entidades de Negocio (4):**
- `Arbol` - Instancias específicas de árboles registrados
- `UsoArbol` - Categorización de usos por especie (12 categorías)
- `DetalleUso` - Unifica todos los tipos de uso en una sola tabla (reemplaza 13 tablas antiguas)
- `CodigoQR` - Códigos QR generados para cada árbol (imagen en base64 LONGTEXT)

**Contenido (2):**
- `CuriosidadesArbol` - Datos interesantes sobre especies
- `InteraccionesEcologicas` - Relaciones ecológicas

**Soporte (2):**
- `tokens_recuperacion` - Tokens para recuperación de contraseñas (expiran 30 min)
- `sugerencias` - Sistema de feedback de usuarios

### Relaciones Clave

```
Estado (1) ──── (N) [Usuario, Especie, Arbol, UsoArbol, ...]
Rol (1) ──── (N) UsuarioRol ──── (N) Usuario
Especie (1) ──── (N) Arbol ──── (1) Centro
                     ├── (1) TipoBosque
                     └── (1) CodigoQR
Especie (1) ──── (N) UsoArbol ──── (1) DetalleUso
Especie (1) ──── (N) CuriosidadesArbol
Especie (1) ──── (N) InteraccionesEcologicas
```

### DetalleUso - Campos Unificados

La tabla `DetalleUso` contiene campos para 12 categorías de uso en una sola estructura:

| Categoría | Campos en DetalleUso |
|-----------|---------------------|
| Maderable | Dureza, Resistencia, UsoFinal |
| Comestible | ParteComestible, FormaConsumo, ValorNutricional |
| Medicinal | ParteUtilizada, Preparacion, EnfermedadesTratadas |
| Ornamental | CaracteristicasEsteticas, UbicacionRecomendada, TipoJardineria, ColoracionEstacional |
| Artesanal | TipoArtesania, TecnicasElaboracion, ComunidadesArtesanales |
| Agroforestal | SistemaAgroforestal, BeneficiosAsociados, CultivosCompatibles, FuncionPrincipal |
| RestauracionEcologica | EcosistemaObjetivo, FuncionEcologica, EspeciesAsociadas, TasaCrecimiento |
| CulturalCeremonial | GrupoEtnico, TipoCeremonia, SignificadoCultural |
| Melifero | TipoMiel, EpocaFloracion, CalidadPolen, AtraccionPolinizadores |
| ProteccionAmbiental | TipoProteccion, BeneficiosAmbientales, ZonasAplicacion, CapacidadCapturaCarbon |
| Tintoreo | ColorObtenido, MetodoExtraccion, UsosTintes |
| Oleaginoso | TipoAceite, PropiedadesAceite, AplicacionesAceite |
| Biocombustible | TipoBiocombustible, PoderCalorifico, RendimientoPorHectarea |

## Funcionalidades Principales

### 1. Sistema de Autenticación
- **Registro de usuarios** con validación de contraseñas (mín. 8 chars + 1 mayúscula)
- **Hash de contraseñas** con werkzeug scrypt (VARCHAR(255))
- **Inicio de sesión** con roles diferenciados (Administrador, Visitante) vía UsuarioRol
- **Recuperación de contraseñas** vía email con tokens temporales (6 dígitos, 30 min)
- **Gestión de sesiones** con Flask sessions (dict con ID, nombre, correo, roles)
- **Perfil de usuario** con avatar, cambio de contraseña, eliminación de cuenta

### 2. Gestión de Árboles
- **CRUD completo** para árboles, especies y centros
- **Subida de imágenes** con procesamiento automático (timestamp + nombre)
- **Generación automática de QR** al crear un árbol
- **Búsqueda avanzada** por múltiples criterios (texto, especie, centro)
- **Mediciones** (CAP, DAP, Altura, Área Basal)
- **Vista pública** con mapa, usos, curiosidades e interacciones

### 3. Sistema QR
- **Generación automática** de códigos QR únicos al registrar árbol
- **Almacenamiento** en base64 (LONGTEXT) en tabla CodigoQR
- **Scanner web** usando cámara del dispositivo (jsQR)
- **Información detallada** al escanear (redirige a /ver_arbol/<id>)

### 4. Panel de Administración
- **Dashboard principal** con estadísticas (árboles, usuarios, centros)
- **Gestión de usuarios** y roles (solo Administrador)
- **Administración de contenido** (especies, usos 12 categorías, curiosidades, interacciones)
- **Sistema de sugerencias** con auto-desactivación (>30 días)
- **Nav lateral** (hamburger menu) con perfil y enlaces

### 5. Características Técnicas
- **Responsive design** optimizado para móviles
- **Paginación** (10 ítems por página con offset)
- **Validación de datos** en frontend y backend
- **Manejo de errores** robusto con flash messages y JSON para AJAX
- **Limpieza de texto UTF-8** para caracteres especiales
- **Footer verde** con logo, enlaces y copyright
- **Menú hamburger deslizable** desde la izquierda con overlay

## Estructura del Proyecto

```
VerdeQR/
├── app.py                 # Entry point Flask (crea app con create_app())
├── app/                   # Paquete Flask (10 módulos)
│   ├── __init__.py        # App factory + registro de blueprints
│   ├── app.py
│   ├── db.py              # Conexión MySQL (PyMySQL + g context)
│   ├── auth.py            # Autenticación (656 líneas, 10 rutas)
│   ├── arboles.py         # Árboles CRUD (1282 líneas, 16 rutas)
│   ├── admin.py           # Admin panel (616 líneas, 12 rutas)
│   ├── especies.py        # Especies (408 líneas, 10 rutas)
│   ├── usos.py            # Usos CRUD (383 líneas, 7 rutas)
│   ├── qr.py              # QR generation (320 líneas, 3 rutas)
│   ├── info.py            # Páginas estáticas (162 líneas, 10 rutas)
│   └── utils.py           # Utilidades (get_base_url, token, género)
├── static/                # Archivos estáticos
│   ├── css/              # 28 hojas de estilo
│   ├── js/               # 12 scripts JS (incl. jsQR)
│   └── uploads/          # Imágenes subidas (usuarios/ + arboles/)
├── templates/             # 53 plantillas Jinja2
│   ├── base.html         # Plantilla base (con sidebar)
│   ├── base_sin_menu.html# Plantilla sin sidebar (hamburger menu)
│   ├── inicio.html       # Página de inicio pública
│   ├── principal.html    # Dashboard (post-login)
│   └── [49+ templates]   # Plantillas específicas
├── schema.sql            # Esquema completo de BD (223 líneas)
├── requirements.txt      # 14 dependencias Python
├── Procfile              # web: gunicorn app:app
├── railway.json          # Config Railway.app (Nixpacks)
├── README.md             # Documentación básica
├── DOCUMENTACION_TECNICA.md # Este archivo
├── AGENTS.md             # Instrucciones para agente IA + bitácora
├── BITACORA_HISTORICO.md # Historial de cambios (archivado)
├── migracion_2026.sql    # Migración: 13 tablas de uso → DetalleUso
└── venv/                 # Entorno virtual Python
```

## 🚀 Configuración y Despliegue

### Desarrollo Local

```bash
# 1. Clonar repositorio
git clone [repositorio]
cd VerdeQR_Nuevo

# 2. Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar base de datos
# Crear BD MySQL 'VerdeQR'
# Importar schema.sql

# 5. Ejecutar aplicación
python app.py
```

### Producción (Railway.app)

El proyecto está configurado para despliegue automático en Railway.app con Nixpacks.

**Variables de entorno requeridas:**
```
# Opción 1: URL completa (Railway MySQL)
DATABASE_URL=mysql://user:pass@host:port/db

# Opción 2: Variables separadas (compatibilidad)
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=VerdeQR

# Generales
SECRET_KEY=clave_secreta_segura
FLASK_ENV=production

# Email (recuperación de contraseñas)
MAIL_USERNAME=verdeqr.app@gmail.com
MAIL_PASSWORD=clave_aplicacion_gmail
```

**Archivos de configuración:**
- `Procfile`: `web: gunicorn app:app`
- `railway.json`: Nixpacks builder (auto-detecta Flask/Python)
- `requirements.txt`: Dependencias exactas con versiones

## Seguridad

### Medidas Implementadas
- **Hash de contraseñas**: werkzeug scrypt (VARCHAR(255)) - `generate_password_hash`/`check_password_hash`
- **Validación de contraseñas**: Regex `^(?=.*[A-Z]).{8,}$` (mín. 8 chars + 1 mayúscula)
- **Sanitización de datos**: Limpieza de caracteres UTF-8 problemáticos
- **Gestión de sesiones**: Flask sessions con datos de usuario + roles
- **Tokens temporales**: Para recuperación de contraseñas (6 dígitos, expiran 30 min, Estado=2 una vez usados)
- **Validación de archivos**: Procesamiento seguro de imágenes (Pillow)
- **SQL preparado**: Prevención de inyección SQL (parámetros con %s)
- **Eliminación suave**: Sistema de estados (1=Activo, 2=Inactivo) en todas las tablas

### Roles y Permisos (UsuarioRol)
| Rol | Acceso |
|-----|--------|
| **Administrador** | CRUD completo en todas las entidades, gestión de usuarios, panel admin |
| **Visitante** | Solo lectura pública, puede enviar sugerencias y contactar |

- Los roles se asignan por registro en `UsuarioRol` (relación N:N)
- La sesión almacena `roles` como string separado por comas via `GROUP_CONCAT`
- Los templates verifican permisos con `session['usuario']['roles']`

## UX/UI

### Diseño Responsive
- **Mobile-first**: Optimizado para dispositivos móviles
- **CSS Grid/Flexbox**: Layout moderno y flexible
- **Breakpoints**: Adaptación a diferentes tamaños de pantalla
- **28 hojas CSS** para componentes específicos (más algunas huérfanas por limpiar)

### Navegación
- **Header**: Logo izquierdo (48px) + hamburger (base_sin_menu.html) o menú superior (base.html)
- **Hamburger menu**: Panel deslizable desde izquierda (300px, gradiente verde), overlay con backdrop-filter
- **Nav panel**: Perfil (avatar + nombre + correo), enlaces del sistema, cerrar sesión
- **Footer verde** (`#1e5631`) con logo 120px, enlaces 3 columnas, copyright (`#143d22`)
- **Avatar usuario**: 36px en header, nombre/correo en nav panel

### Interactividad
- **Scanner QR**: Acceso directo desde cámara (jsQR.js)
- **Búsqueda en tiempo real**: Autocompletado vía API `/api/sugerencias_busqueda`
- **Notificaciones**: Sistema de mensajes flash con animaciones
- **Carrusel de imágenes**: Navegación visual atractiva con transiciones CSS

## 🔄 Flujo de Datos Principal

```
Usuario escanea QR → Aplicación lee código → 
Consulta BD por ID árbol → Obtiene información completa →
Muestra datos: especie, características, usos, curiosidades
```

## Métricas y Estadísticas

El sistema incluye dashboard con:
- Total de árboles registrados
- Número de usuarios activos
- Centros disponibles
- Sugerencias recientes

## Escalabilidad y Futuras Mejoras

### Arquitectura Preparada Para:
- **API REST**: Estructura modular permite fácil conversión
- **Microservicios**: Separación clara de responsabilidades (7 blueprints)
- **Cache**: Implementación de Redis para optimización
- **CDN**: Para servir imágenes estáticamente

### Posibles Extensiones:
- App móvil nativa
- Geolocalización de árboles (campo lat/lng ya en tabla Centro)
- Sistema de favoritos
- Comunidad de usuarios
- Machine Learning para identificación automática
- Limpieza de CSS/JS huérfanos (~20 CSS, ~12 JS sin referencia)

## Detalles de Implementación

### Rutas Completas del Sistema

**Autenticación (`auth_bp`):**
| Método | Ruta | Función | Descripción |
|--------|------|---------|-------------|
| GET, POST | `/registro` | `registro()` | Registrar usuario (hash scrypt) |
| GET, POST | `/iniciar_sesion` | `iniciar_sesion()` | Login con verificación de roles |
| GET | `/cerrar_sesion` | `cerrar_sesion()` | Logout, redirect a `/` |
| GET, POST | `/olvidar_contrasena` | `olvidar_contrasena()` | Enviar token 6 dígitos por email |
| GET, POST | `/restablecer_contrasena` | `restablecer_contrasena()` | Cambiar password con token |
| GET, POST | `/perfil` | `perfil()` | Ver/editar perfil + avatar |
| POST | `/cambiar_contrasena` | `cambiar_contrasena()` | Cambiar password desde perfil |
| POST | `/actualizar_avatar` | `actualizar_avatar()` | AJAX: subir avatar |
| POST | `/eliminar_avatar` | `eliminar_avatar()` | AJAX: reset avatar por defecto |
| POST | `/eliminar_cuenta` | `eliminar_cuenta()` | Eliminar cuenta de usuario |

**Árboles (`arboles_bp`):**
| Método | Ruta | Función | Descripción |
|--------|------|---------|-------------|
| GET | `/` | `inicio()` | Home público (8 árboles pop, 6 especies, 4 centros) |
| GET | `/inicio` | `inicio_redirect()` | Redirect a `/` |
| GET | `/index` | `index()` | Index legacy |
| GET | `/buscar_arbol` | `buscar_arbol()` | Búsqueda por texto/especie/centro |
| GET | `/todos_los_arboles` | `todos_los_arboles()` | Lista paginada (10/page) |
| GET | `/principal` | `principal()` | Dashboard (requiere login) |
| GET, POST | `/arbol` | `arbol()` | Crear árbol + auto QR |
| GET, POST | `/arbol/editar/<id>` | `editar_arbol()` | Editar árbol |
| GET | `/arbol/eliminar/<id>` | `eliminar_arbol()` | Eliminar árbol (cascade) |
| GET, POST | `/medidas_arbol` | `medidas_arbol()` | CRUD mediciones (CAP, DAP, Altura, Área Basal) |
| GET, POST | `/medidas_arbol/editar/<id>` | `editar_medida_arbol()` | Editar medición |
| GET | `/medidas_arbol/eliminar/<id>` | `eliminar_medida_arbol()` | Eliminar medición |
| GET | `/ver_arbol/<id>` | `ver_arbol()` | Vista pública detallada (QR, usos, curiosidades, mapa) |
| GET, POST | `/centro` | `centro_view()` | CRUD centros |
| GET, POST | `/centro/editar/<id>` | `editar_centro_view()` | Editar centro |
| GET | `/centro/eliminar/<id>` | `eliminar_centro_view()` | Eliminar centro (bloquea si tiene árboles) |

**Admin (`admin_bp`):**
| Método | Ruta | Función | Descripción |
|--------|------|---------|-------------|
| GET, POST | `/gestion_usuarios` | `gestion_usuarios()` | CRUD usuarios con roles |
| GET | `/gestion` | `gestion()` | Panel admin sidebar |
| GET | `/sidebar` | `sidebar()` | Redirect a `/inicio` |
| GET, POST | `/sugerencias` | `sugerencias()` | CRUD sugerencias + auto-desactivación |
| GET | `/sugerencias/eliminar/<id>` | `eliminar_sugerencia()` | Eliminar sugerencia |
| POST | `/sugerencias/actualizar/<id>` | `actualizar_estado_sugerencia()` | AJAX cambiar estado |
| GET, POST | `/curiosidades` | `curiosidades()` | CRUD curiosidades por especie |
| GET, POST | `/curiosidades/editar/<id>` | `editar_curiosidad()` | Editar curiosidad |
| GET | `/curiosidades/eliminar/<id>` | `eliminar_curiosidad()` | Eliminar curiosidad |
| GET, POST | `/interacciones` | `interacciones()` | CRUD interacciones ecológicas |
| GET, POST | `/interacciones/editar/<id>` | `editar_interaccion()` | Editar interacción |
| GET | `/interacciones/eliminar/<id>` | `eliminar_interaccion()` | Eliminar interacción |
| GET, POST | `/usuario/editar/<id>` | `editar_usuario()` | Editar usuario + rol |
| GET, POST | `/usuario/eliminar/<id>` | `eliminar_usuario()` | Eliminar usuario (no a sí mismo) |

**Especies (`especies_bp`):**
| Método | Ruta | Función | Descripción |
|--------|------|---------|-------------|
| GET, POST | `/especie` | `especie()` | CRUD especies |
| GET, POST | `/especie/editar/<id>` | `editar_especie()` | Editar especie |
| GET | `/especie/eliminar/<id>` | `eliminar_especie()` | Eliminar especie (cascade) |
| GET | `/usos_por_especie` | `usos_por_especie()` | Usos agrupados por especie |
| GET, POST | `/agregar_uso/<especie_id>` | `agregar_uso()` | Agregar uso a especie |
| GET, POST | `/tipo_bosque` | `tipo_bosque()` | CRUD tipos de bosque |
| GET, POST | `/tipo_bosque/editar/<id>` | `editar_tipo_bosque()` | Editar tipo bosque |
| GET | `/tipo_bosque/eliminar/<id>` | `eliminar_tipo_bosque()` | Eliminar tipo bosque |

**Usos (`usos_bp`):**
| Método | Ruta | Función | Descripción |
|--------|------|---------|-------------|
| GET, POST | `/uso_arbol` | `uso_arbol()` | CRUD usos + DetalleUso |
| GET, POST | `/uso_arbol/editar/<id>` | `editar_uso_arbol()` | Editar uso |
| GET, POST | `/uso_arbol/detalle/<id>` | `editar_uso_detalle()` | Editar detalle por categoría |
| GET | `/uso_arbol/eliminar/<id>` | `eliminar_uso_arbol()` | Eliminar uso (cascade DetalleUso) |

**QR (`qr_bp`):**
| Método | Ruta | Función | Descripción |
|--------|------|---------|-------------|
| GET, POST | `/qr` | `qr()` | Generar QR para árbol (base64) |
| GET | `/ver_qr/<id>` | `ver_qr()` | Ver QR con info del árbol |
| POST | `/eliminar_qr/<id>` | `eliminar_qr()` | Soft-delete QR (Estado=2) |

**Info (`info_bp`):**
| Método | Ruta | Función | Descripción |
|--------|------|---------|-------------|
| GET | `/politica-privacidad` | `politica_privacidad()` | Política de privacidad |
| GET | `/terminos-condiciones` | `terminos_condiciones()` | Términos y condiciones |
| GET | `/contacto` | `contacto()` | Página de contacto |
| GET | `/acerca-de` | `acerca_de()` | Acerca de |
| GET | `/soporte-tecnico` | `soporte_tecnico()` | Soporte técnico |
| GET | `/preguntas-frecuentes` | `preguntas_frecuentes()` | FAQ |
| GET | `/reportar-problema` | `reportar_problema()` | Reportar problema |
| POST | `/enviar-contacto` | `enviar_contacto()` | Procesar formulario contacto |
| POST | `/registrar_sugerencia` | `registrar_sugerencia()` | AJAX: enviar sugerencia |
| GET | `/api/sugerencias_busqueda` | `sugerencias_busqueda()` | API autocompletado (JSON)

### Funciones Utilitarias Clave

```python
def get_base_url()
    """Detecta automáticamente la URL base (localhost/túnel/dominio)"""

def limpiar_texto_utf8(texto)
    """Limpia caracteres problemáticos UTF-8"""

def determinar_genero(nombre)
    """Determina género para avatar predeterminado"""

def generar_token(longitud=6)
    """Genera tokens aleatorios para recuperación"""
```

### Configuración de Base de Datos

```python
def get_db_config():
    """Configuración automática para desarrollo/producción"""
    # Detecta DATABASE_URL (Railway) o variables separadas (local)
    # Retorna configuración PyMySQL con charset utf8mb4
```

### Manejo de Imágenes

- **Subida**: Validación y renombrado automático con timestamp
- **Almacenamiento**: `static/css/js/img/` para compatibilidad
- **Procesamiento**: Pillow para manipulación de imágenes
- **Rutas**: Normalización de barras para compatibilidad cross-platform

### Sistema de Paginación

```python
# Implementación en /todos_los_arboles
page = request.args.get('page', 1, type=int)
per_page = 10
offset = (page - 1) * per_page

# Cálculo de metadatos de paginación
total_pages = (total_arboles + per_page - 1) // per_page
has_prev = page > 1
has_next = page < total_pages
```

## 🔍 Características Técnicas Avanzadas

### Búsqueda Inteligente

El sistema implementa búsqueda en múltiples niveles:

1. **Búsqueda exacta** por ID de especie/centro
2. **Búsqueda por texto** en múltiples campos:
   - Nombre científico y vulgar
   - Características del árbol
   - Servicios ecosistémicos
   - Descripción general
3. **Búsqueda parcial** por palabras clave (>3 caracteres)

### Generación de QR

```python
# Proceso automático al registrar árbol
qr = qrcode.QRCode(version=1, box_size=10, border=5)
qr.add_data(f"{base_url}/ver_arbol/{arbol_id}")
qr.make(fit=True)

# Conversión a base64 para almacenamiento
img_buffer = io.BytesIO()
qr_img.save(img_buffer, format='PNG')
qr_base64 = base64.b64encode(img_buffer.getvalue()).decode()
```

### Sistema de Estados

Todas las entidades principales manejan estados:
- `1` = Activo
- `2` = Inactivo/Usado (tokens)
- Permite "eliminación suave" manteniendo integridad referencial

### Validaciones Implementadas

**Frontend (JavaScript):**
- Validación en tiempo real de formularios
- Confirmación de eliminaciones
- Validación de archivos de imagen

**Backend (Python):**
- Regex para contraseñas: `^(?=.*[A-Z]).{8,}$`
- Validación de correos únicos
- Sanitización de datos UTF-8
- Verificación de tokens temporales

## 🌐 Configuración de Despliegue

### Variables de Entorno

```bash
# Desarrollo Local
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=VerdeQR
SECRET_KEY=desarrollo_key

# Producción Railway
DATABASE_URL=mysql://user:pass@host:port/db
SECRET_KEY=production_key_muy_segura
MAIL_USERNAME=verdeqr.app@gmail.com
MAIL_PASSWORD=app_specific_password
```

### Configuración de Email

```python
# Flask-Mail (app/__init__.py)
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'verdeqr.app@gmail.com'
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
MAIL_SUPPRESS_SEND = True  # Modo dev (deshabilitar en prod)
```

### Conexión a Base de Datos

La configuración se realiza en `app/db.py`:
1. Si existe `DATABASE_URL` (formato `mysql://user:pass@host:port/db`), se parsea automáticamente (Railway.app)
2. Si no, usa variables individuales: `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
3. Siempre usa `pymysql.cursors.DictCursor` para resultados como diccionarios
4. Conexiones cacheadas por request en `flask.g` via `get_db()`

### Optimizaciones de Producción

- **Gunicorn**: Servidor WSGI para producción (Procfile)
- **Conexiones DB**: Cache por request con Flask `g` context
- **Manejo de errores**: Try-catch comprehensivo con rollback automático
- **Logging**: Prints estratégicos para debugging en desarrollo

## Rendimiento

### Consultas Optimizadas

- **JOINs eficientes**: LEFT JOIN para datos relacionados
- **Índices**: Claves foráneas automáticamente indexadas por MySQL
- **Paginación**: LIMIT/OFFSET (10 por página) para grandes datasets
- **Agregaciones**: COUNT(), GROUP_CONCAT para estadísticas y roles

### Carga de Archivos

- **Validación**: Extensiones permitidas (jpg, png, gif)
- **Almacenamiento**: `static/uploads/usuarios/` para avatares, `static/css/js/img/` para árboles
- **Nombres únicos**: Timestamp + nombre original (ej. `1701234567_foto.jpg`)
- **Avatar por defecto**: Determina género del nombre (`avatarf.jpg` / `avatarm.jpg`)

## Herramientas de Desarrollo

### AGENTS.md - Sistema de Asistencia IA

El proyecto incluye `AGENTS.md` con instrucciones para agentes de IA:
- **Reglas**: Preguntar antes de cambios, no hacer push sin permiso, explicar modificaciones
- **Bitácora**: Registro de cambios en tabla con fecha, descripción, archivos y estado
- **Límite**: Máximo 30 entradas en AGENTS.md; las antiguas pasan a `BITACORA_HISTORICO.md`
- **Comandos**: `/end-session` registra cambios, `/compact` libera contexto

### Scripts PowerShell

- `clean_templates.ps1`, `convert_templates.ps1`, `convert_and_clean.ps1` - Utilidades de mantenimiento
- `fix_bom.ps1` - Corrección de BOM en archivos
- `remove_consolidated_refs.ps1` - Limpieza de referencias

## Mantenimiento y Debugging

### Logs del Sistema

```python
# Información de conexión DB (app/db.py)
print("Conexión a la base de datos establecida correctamente")

# Debugging de sesiones (app/auth.py)
print(f"Sesión de usuario creada: {session['usuario']}")

# Errores con traceback completo
import traceback
print(traceback.format_exc())
```

### Estructura de Errores

- **Flash messages**: Notificaciones al usuario (categorías: success, error, warning, info)
- **JSON responses**: Para peticiones AJAX (contacto, sugerencias, avatar)
- **Rollback automático**: `connection.rollback()` en transacciones fallidas
- **Redirecciones**: Manejo de estados de error con redirect + flash

---

**Desarrollado para la educación ambiental y la conservación forestal**

## Información de Contacto Técnico

**Proyecto**: VerdeQR - Un dendrólogo en tu bolsillo
**Tecnologías**: Flask 2.3 + MySQL + QR + Responsive Design
**Despliegue**: Railway.app con auto-deploy desde GitHub
**Repo**: GitHub (master branch)
**Admin**: jhon123@gmail.com (contraseña en gestor de contraseñas)
**BD Local**: XAMPP MySQL puerto 3306, root sin contraseña, BD `VerdeQR`
**Licencia**: MIT License
