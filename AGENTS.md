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

7. **Bitácora máxima 30 entradas**: Cuando la tabla de `## Bitácora de Cambios` llegue a 30 entradas, mover las más antiguas a `BITACORA_HISTORICO.md` (crearlo si no existe), dejando solo las más recientes en `AGENTS.md`. Mantener el formato de tabla exacto.

8. **Auto-recuperación en loops o glitches**: Si te quedas en un loop, se tilda, o algo no responde, reinicia automáticamente la acción que estabas ejecutando y continúa. No esperes a que el usuario te lo indique — detecta el bloqueo y resuelve solo.

## Bitácora de Cambios

| Fecha | Descripción | Archivos | Estado |
|-------|------------|----------|--------|
| 2026-06-26 | Eliminadas 14 tablas de usos viejas (usoagroforestal, usocomestible, etc.) que estaban vacías. | BD: 14 tablas DROP | Completado |
| 2026-06-26 | Implementado hash de contraseñas con werkzeug (scrypt). Agrandada columna Contraseña a VARCHAR(255). Actualizados login, registro, cambio y restablecimiento de contraseña. Migradas contraseñas existentes a hash. Admin email cambiado a jhon123@gmail.com para usuario 2. | app/auth.py, BD: ALTER TABLE Usuario | Completado |
| 2026-06-26 | Asignados roles Administrador a ambos usuarios en UsuarioRol. Reemplazadas 17 referencias a admin por email (jhon123@gmail.com) por verificación de roles en 9 templates. Actualizado schema.sql (Contraseña VARCHAR(255)). Recreada tabla UsoArbol que fue eliminada por error. Agregada FK DetalleUso.Uso -> UsoArbol.IDUso. | UsuarioRol (INSERT), templates/*.html (9), schema.sql, BD: CREATE TABLE UsoArbol | Completado |
| 2026-06-26 | Corregido fallback de Árboles Populares en inicio.html: href=\"#\" reemplazado por url_for('arboles.principal') y agregados overlay-links a las 4 tarjetas estáticas. Insertados datos de ejemplo en BD: 4 tipos de bosque, 2 centros, 4 especies y 4 árboles (Ceiba, Guayacán, Roble, Palma de Cera). | templates/inicio.html, BD: INSERTs en TipoBosque, Centro, Especie, Arbol | Completado |
| 2026-06-26 | Insertados datos complementarios en BD: 13 usos con detalles (UsoArbol + DetalleUso), 18 curiosidades y 14 interacciones ecológicas para las 4 especies. | BD: INSERTs en UsoArbol, DetalleUso, CuriosidadesArbol, InteraccionesEcologicas | Completado |
| 2026-06-26 | Corregidas categorías de usos en UsoArbol para que coincidan con el template (RestauracionEcologica, CulturalCeremonial, ProteccionAmbiental). Generados QR para 4 árboles existentes. Agregada generación automática de QR al crear árbol en app/arboles.py. | BD: UPDATE UsoArbol, app/arboles.py | Completado |
| 2026-06-26 | Arreglado footer de ver_arbol.html: agregados estilos CSS para .footer-verde, .bg-dark-green, .logo-container-footer, .footer-links. | templates/ver_arbol.html | Completado |
| 2026-06-26 | Corregido error en animations.js: handleMenuScroll accedía a classList de elemento null. Agregado guard null check. | static/js/animations.js | Completado |
| 2026-06-26 | Agregado menú de navegación lateral (hamburger menu) a base_sin_menu.html con panel deslizable, overlay, perfil de usuario y enlaces del sistema. Corregido layout del header (flex horizontal con avatar 36px). | templates/base_sin_menu.html | Completado |
| 2026-06-26 | Corregido cierre de sesión: url_for('inicio') cambiado a url_for('arboles.inicio'). | app/auth.py | Completado |
| 2026-06-26 | Corregido layout del header: hamburger movido a la izquierda con .header-left (flex). Items del nav panel cambiados a borde izquierdo sin márgenes ni border-radius. | templates/base_sin_menu.html | Completado |
| 2026-06-26 | Commit y push a GitHub (c6d2abc). Creado BITACORA_HISTORICO.md con entradas antiguas. Límite de bitácora reducido a 30. | AGENTS.md, BITACORA_HISTORICO.md | Completado |
| 2026-06-27 | Documentación técnica actualizada (DOCUMENTACION_TECNICA.md, README.md). Creados y eliminados archivos Docker. Intento de deploy a PythonAnywhere — MySQL no disponible gratis. Instalado MCP Touchpoint (touchpoint-py v0.3.0 + opencode.json). Instalado y configurado ngrok (túnel activo en https://effective-brutishly-spooky.ngrok-free.dev). Creado DB_DIAGRAMA.md (diagrama ER Mermaid). Pendiente elegir hosting: Railway.app, db4free.net o Azure for Students. | DOCUMENTACION_TECNICA.md, README.md, opencode.json, DB_DIAGRAMA.md, Dockerfile (creado/eliminado), docker-compose.yml (creado/eliminado), .dockerignore (creado/eliminado) | Completado |
| 2026-06-27 | Agregada tarjeta de bienvenida cerrable en inicio.html (público sin login). Responsive mobile: compactada a layout horizontal con X visible, stats ocultos, párrafo oculto, padding mínimo. Verificada con Touchpoint + Brave (414x896). | templates/inicio.html | Completado |
| 2026-06-27 | Agregado responsive CSS para welcome modal en móvil (padding reducido, fonts más pequeños, decoraciones ocultas, breakpoint 400px). Compactada bienvenida-card con X más visible. | templates/inicio.html | Completado |
| 2026-06-27 | Rotada contraseña admin en BD + docs (contraseña antigua eliminada de README.md y DOCUMENTACION_TECNICA.md). Limpiado historial git con filter-repo + force push. Scripts .ps1 movidos a /scripts/. templates_backup/ ignorado. MAIL_SUPPRESS_SEND configurable por entorno. skills-lock.json y *.mwb agregados a .gitignore. | BD, README.md, DOCUMENTACION_TECNICA.md, .gitignore, app/__init__.py, scripts/ | Completado |
| 2026-06-28 | Welcome modal ya no se auto-muestra (solo con clic en logo). Bienvenida-card simplificada (stats en columna, icono 50px). Welcome modal responsive: features en fila horizontal en móvil, fonts/padding reducidos. | templates/inicio.html | Completado |
| 2026-06-28 | get_base_url ahora acepta variable de entorno BASE_URL. QRs regenerados con URL pública de ngrok. Verificadas consultas SQL parametrizadas (sin inyección). | app/utils.py, BD: UPDATE CodigoQR | Completado |
| 2026-06-28 | Agregada librería jsQR faltante en principal.html (botón Identificar QR no funcionaba). | templates/principal.html | Completado |
| 2026-06-28 | Agregados botones editar/eliminar sugerencias para el propio usuario visitante + endpoints backend. | app/info.py, templates/principal.html | Completado |
