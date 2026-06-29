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

5. **Bitácora**: Los cambios se registran en `BITACORA_HISTORICO.md` (no en este archivo). Al finalizar cada sesión, agregar un resumen con fecha, descripción, archivos modificados y estado.

6. **Comando /end-session**: Antes de hacer `/compact`, ejecuta `/end-session` para que el agente registre automáticamente los cambios de la sesión en la bitácora. Luego corre `/compact` para liberar contexto.

7. **Bitácora máxima 30 entradas**: Cuando la tabla de `## Bitácora de Cambios` en `BITACORA_HISTORICO.md` llegue a 30 entradas, mover las más antiguas a una sección de histórico dentro del mismo archivo, dejando solo las más recientes. Mantener el formato de tabla exacto.

8. **Auto-recuperación en loops o glitches**: Si te quedas en un loop, se tilda, o algo no responde, reinicia automáticamente la acción que estabas ejecutando y continúa. No esperes a que el usuario te lo indique — detecta el bloqueo y resuelve solo.
