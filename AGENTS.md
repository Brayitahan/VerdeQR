# AGENTS.md - VerdeQR

## Información del Proyecto

- **Nombre**: VerdeQR - Un dendrólogo en tu bolsillo
- **Stack**: Flask (Python), MySQL, HTML/CSS/JS vanilla, QR Code
- **Base de datos**: MySQL con PyMySQL (sin ORM)
- **Frontend**: Jinja2 templates, CSS3 responsive, JavaScript vanilla
- **Despliegue**: Railway.app (Gunicorn)
- **Auth**: Sistema de registro/login con roles (Administrador, Visitante)
- **Email**: Flask-Mail para recuperación de contraseñas
- **Estructura**: `app.py` (entrada principal), `static/` (css/js/uploads), `templates/` (~40+ HTML)

## Reglas para el Agente

1. **Preguntar antes de realizar cualquier cambio**: No modificar nada sin antes consultarme y obtener mi aprobación explícita.

2. **Si no estás al 80% de seguridad, no realizar el ajuste**: Si tienes dudas sobre el impacto o la correctitud de un cambio, detente y valida conmigo primero.

3. **No subir nada automático a GitHub**: No hacer commits, push, ni ninguna operación en GitHub a menos que yo lo solicite explícitamente.

4. **Explicar qué modificaste y su funcionamiento**: Después de cada cambio, describir claramente qué archivos se modificaron, qué se agregó/eliminó y cómo funciona.

5. **Bitácora**: Al finalizar cada sesión, agregar un resumen de los cambios realizados en la sección `## Bitácora de Cambios` al final de este archivo, con fecha, descripción, archivos modificados y estado.

6. **Comando /end-session**: Antes de hacer `/compact`, ejecuta `/end-session` para que el agente registre automáticamente los cambios de la sesión en la bitácora. Luego corre `/compact` para liberar contexto.

## Bitácora de Cambios

| Fecha | Descripción | Archivos | Estado |
|-------|------------|----------|--------|
| 2026-06-26 | Creación inicial de AGENTS.md con reglas del proyecto | AGENTS.md | Completado |
| 2026-06-26 | Instalación de skills ui-ux-pro-max y frontend-design | .agents/skills/ | Completado |
| 2026-06-26 | Normalización de BD: 13 tablas de usos unificadas en DetalleUso. Se agregó FechaRegistro a Usuario y Descripcion a Estado. Se actualizó app.py eliminando los JOINs masivos de 13 tablas y las cadenas if/elif de INSERT/UPDATE/DELETE. Se unificaron 4 rutas individuales en editar_uso_detalle. Se actualizaron 3 templates. Se creó script de migración migracion_2026.sql. | schema.sql, app.py, templates/editar_uso_maderable.html, templates/editar_uso_medicinal.html, templates/editar_uso_comestible.html, migracion_2026.sql | Completado |
| 2026-06-26 | Creación de comando /end-session para registrar automáticamente la bitácora antes de compactar. Se agregó regla #6 en AGENTS.md y se creó .opencode/commands/end-session.md | AGENTS.md, .opencode/commands/end-session.md | Completado |
| 2026-06-26 | División de app.py (~4074 líneas) en 7 blueprints: auth, admin, arboles, especies, usos, qr, info. Se creó app/ como paquete con __init__.py (factory create_app), db.py, utils.py. app.py quedó como entry point (~10 líneas). Se actualizaron url_for en 49 templates .html. | app.py, app/__init__.py, app/db.py, app/utils.py, app/auth.py, app/admin.py, app/arboles.py, app/especies.py, app/usos.py, app/qr.py, app/info.py, templates/*.html | Completado |
| 2026-06-26 | Consolidación CSS/JS: 28 CSS → 5 (base, components, pages, responsive, animations), 12 JS → 4 (main, carousel, qr, animations). Se actualizaron los 50 templates para usar los nuevos archivos. Se agregaron design tokens CSS (variables) con paleta verde/blanco/negro/azul. Se reemplazaron colores hardcodeados por variables en base.css, pages.css y components.css. | static/css/base.css, components.css, pages.css, responsive.css, animations.css, static/js/main.js, carousel.js, qr.js, animations.js, templates/*.html (50) | Completado |
| 2026-06-26 | Reversión consolidación CSS/JS: eliminados 5 CSS y 3 JS consolidados que causaban conflictos. Templates restaurados a standalone (sin herencia Jinja2), cargando CSS/JS originales. | static/css/base.css, components.css, pages.css, responsive.css, animations.css, static/js/main.js, carousel.js, qr.js, templates/*.html | Completado |
| 2026-06-26 | Agregadas 3 rutas de centros (centro, editar_centro, eliminar_centro) a app/arboles.py con endpoint explícito. Corregidas 26 referencias a endpoints sin prefijo de blueprint en 38 templates (93 reemplazos). Reparada corrupción Jinja2/HTML en editar_especie.html. | app/arboles.py, templates/*.html (38) | Completado |
| 2026-06-26 | Corregidas referencias a endpoints sin prefijo en perfil.html (eliminar_avatar, actualizar_avatar). | templates/perfil.html | Completado |
| 2026-06-26 | Arreglado hover de tarjetas que se escondían: cambiada animación pulseGlow por transition en box-shadow en layout_improvements.css. | static/css/layout_improvements.css | Completado |
| 2026-06-26 | Eliminadas 14 tablas de usos viejas (usoagroforestal, usocomestible, etc.) que estaban vacías. | BD: 14 tablas DROP | Completado |
| 2026-06-26 | Implementado hash de contraseñas con werkzeug (scrypt). Agrandada columna Contraseña a VARCHAR(255). Actualizados login, registro, cambio y restablecimiento de contraseña. Migradas contraseñas existentes a hash. Admin email cambiado a jhon123@gmail.com para usuario 2. | app/auth.py, BD: ALTER TABLE Usuario | Completado |
| 2026-06-26 | Asignados roles Administrador a ambos usuarios en UsuarioRol. Reemplazadas 17 referencias a admin por email (jhon123@gmail.com) por verificación de roles en 9 templates. Actualizado schema.sql (Contraseña VARCHAR(255)). Recreada tabla UsoArbol que fue eliminada por error. Agregada FK DetalleUso.Uso -> UsoArbol.IDUso. | UsuarioRol (INSERT), templates/*.html (9), schema.sql, BD: CREATE TABLE UsoArbol | Completado |
| 2026-06-26 | Corregido fallback de Árboles Populares en inicio.html: href=\"#\" reemplazado por url_for('arboles.principal') y agregados overlay-links a las 4 tarjetas estáticas. Insertados datos de ejemplo en BD: 4 tipos de bosque, 2 centros, 4 especies y 4 árboles (Ceiba, Guayacán, Roble, Palma de Cera). | templates/inicio.html, BD: INSERTs en TipoBosque, Centro, Especie, Arbol | Completado |
| 2026-06-26 | Insertados datos complementarios en BD: 13 usos con detalles (UsoArbol + DetalleUso), 18 curiosidades y 14 interacciones ecológicas para las 4 especies. | BD: INSERTs en UsoArbol, DetalleUso, CuriosidadesArbol, InteraccionesEcologicas | Completado |
