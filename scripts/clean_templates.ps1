# Script to remove ALL old CSS/JS references from templates and keep only consolidated files
# Also converts to extends pattern

$templatesDir = "C:\Users\yaira daniela\Downloads\verdeqr-main\templates"

# Template -> base mapping (same as before)
$baseSinMenu = @(
    "inicio.html", "principal.html", "perfil.html",
    "registro.html", "iniciar_sesion.html", "olvidar_contrasena.html",
    "restablecer_contrasena.html", "registro_usuario.html",
    "acerca_de.html", "contacto.html", "politica_privacidad.html",
    "terminos_condiciones.html", "preguntas_frecuentes.html",
    "soporte_tecnico.html", "reportar_problema.html",
    "resultados_busqueda.html", "todos_los_arboles.html",
    "busqueda_arboles.html"
)

$baseConMenu = @(
    "arbol.html", "editar_arbol.html",
    "especie.html", "editar_especie.html",
    "tipo_arbol.html", "editar_tipo_arbol.html",
    "tipo_bosque.html", "editar_tipo_bosque.html",
    "usos_por_especie.html",
    "uso_arbol.html", "editar_uso_arbol.html",
    "agregar_uso.html",
    "editar_uso_comestible.html", "editar_uso_maderable.html",
    "editar_uso_medicinal.html", "editar_uso_ornamental.html",
    "centro.html", "editar_centro.html",
    "qr.html", "ver_qr.html",
    "curiosidades.html", "editar_curiosidad.html",
    "interacciones.html", "editar_interaccion.html",
    "sugerencias.html", "gestion.html",
    "editar_usuario.html"
)

$skipFiles = @(
    "base.html", "base_sin_menu.html",
    "ver_arbol.html", "flash_messages.html",
    "sidebar.html", "loading_scripts.html",
    "index.html"
)

$baseMap = @{}
foreach ($f in $baseSinMenu) { $baseMap[$f] = "base_sin_menu.html" }
foreach ($f in $baseConMenu) { $baseMap[$f] = "base.html" }

Get-ChildItem "$templatesDir\*.html" | ForEach-Object {
    $filename = $_.Name
    $path = $_.FullName

    if ($skipFiles -contains $filename) { return }
    if (-not $baseMap.ContainsKey($filename)) { return }

    Write-Host "Processing: $filename" -ForegroundColor Green
    $content = Get-Content $path -Raw -Encoding UTF8
    $baseTemplate = $baseMap[$filename]

    # Extract Title
    $title = "VerdeQR"
    $titleMatch = [regex]::Match($content, '<title>(.*?)</title>')
    if ($titleMatch.Success) { $title = $titleMatch.Groups[1].Value.Trim() }

    # Find body boundaries
    $bodyOpenMatch = [regex]::Match($content, '<body[^>]*>')
    $bodyCloseIdx = $content.LastIndexOf('</body>')
    if ((-not $bodyOpenMatch.Success) -or ($bodyCloseIdx -eq -1)) {
        Write-Host "  ERROR: No body tags" -ForegroundColor Red
        return
    }

    $bodyOpenIdx = $bodyOpenMatch.Index + $bodyOpenMatch.Length

    # Extract <style> blocks from head (keep only these, remove all <link> CSS)
    $headSection = $content.Substring(0, $bodyOpenMatch.Index)
    $styleBlocks = [regex]::Matches($headSection, '<style>.*?</style>', [Text.RegularExpressions.RegexOptions]::Singleline)

    # Body content
    $bodyContent = $content.Substring($bodyOpenIdx, $bodyCloseIdx - $bodyOpenIdx)
    $bodyContent = $bodyContent -replace "{%-?\s*include\s+['`"](flash_messages\.html)['`"]\s*-?%}\s*", ""

    # Remove ALL <script src=...> from body (base provides consolidated JS)
    $bodyContent = $bodyContent -replace '<script[^>]*src="[^"]*"[^>]*></script>\s*', ""

    # Remove HTML comments around CSS/JS sections that might have been left
    $bodyContent = $bodyContent -replace "<!-- Original CSS references -->", ""
    $bodyContent = $bodyContent -replace "<!-- Original JS references -->", ""
    $bodyContent = $bodyContent.Trim()

    # Remove duplicate <style> blocks in body (keep only if they have unique content)
    # Some templates have <style> in body too (like principal.html media queries)
    # We keep those since they're usually responsive overrides specific to that template

    # Build new content
    $sb = New-Object System.Text.StringBuilder
    $null = $sb.AppendLine("{% extends ""$baseTemplate"" %}")
    $null = $sb.AppendLine("{% block title %}$title{% endblock %}")
    $null = $sb.AppendLine("")

    # Add extra_css only if there are <style> blocks from head
    if ($styleBlocks.Count -gt 0) {
        $null = $sb.AppendLine("{% block extra_css %}")
        foreach ($m in $styleBlocks) {
            $null = $sb.AppendLine("    $($m.Value)")
        }
        $null = $sb.AppendLine("{% endblock %}")
        $null = $sb.AppendLine("")
    }

    $null = $sb.AppendLine("{% block content %}")
    $null = $sb.AppendLine($bodyContent)
    $null = $sb.AppendLine("{% endblock %}")

    [System.IO.File]::WriteAllText($path, $sb.ToString(), [System.Text.Encoding]::UTF8)
    Write-Host "  OK - $baseTemplate" -ForegroundColor Cyan
}
