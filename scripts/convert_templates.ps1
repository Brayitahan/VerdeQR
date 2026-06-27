# Script to convert standalone templates to Jinja2 extends pattern
$templatesDir = "C:\Users\yaira daniela\Downloads\verdeqr-main\templates"

# Mapping: template -> base template to extend
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

$consolidatedCSS = @("base.css", "components.css", "pages.css", "responsive.css", "animations.css")
$consolidatedJS = @("main.js", "carousel.js", "qr.js", "animations.js")

$baseMap = @{}
foreach ($f in $baseSinMenu) { $baseMap[$f] = "base_sin_menu.html" }
foreach ($f in $baseConMenu) { $baseMap[$f] = "base.html" }

$log = @()

Get-ChildItem "$templatesDir\*.html" | ForEach-Object {
    $filename = $_.Name
    $path = $_.FullName

    if ($skipFiles -contains $filename) {
        Write-Host "SKIP: $filename" -ForegroundColor Yellow
        return
    }
    if (-not $baseMap.ContainsKey($filename)) {
        Write-Host "SKIP: $filename (no mapping)" -ForegroundColor Yellow
        return
    }

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
    $headSection = $content.Substring(0, $bodyOpenMatch.Index)

    # Extract CSS links from head
    $extraCssLines = @()
    $cssPattern = '<link[^>]*rel="stylesheet"[^>]*>'
    $cssMatches = [regex]::Matches($headSection, $cssPattern)
    foreach ($m in $cssMatches) {
        $href = $m.Value
        $keep = $true
        if ($href -match 'bootstrap') { $keep = $false }
        if ($href -match 'font-awesome') { $keep = $false }
        if ($href -match 'fonts\.googleapis') { $keep = $false }
        foreach ($c in $consolidatedCSS) {
            if ($href -match [regex]::Escape($c)) { $keep = $false; break }
        }
        if ($keep) { $extraCssLines += $m.Value }
    }

    # Extract <style> blocks from head
    $styleMatches = [regex]::Matches($headSection, '<style>.*?</style>', [Text.RegularExpressions.RegexOptions]::Singleline)
    foreach ($m in $styleMatches) {
        $extraCssLines += $m.Value
    }

    # Body content
    $bodyContent = $content.Substring($bodyOpenIdx, $bodyCloseIdx - $bodyOpenIdx)

    # Remove flash messages include
    $bodyContent = $bodyContent -replace "{%-?\s*include\s+['`"](flash_messages\.html)['`"]\s*-?%}\s*", ""

    # Remove duplicate consolidated JS from body
    $jsPattern = '<script[^>]*src="([^"]*)"[^>]*></script>'
    $jsMatches = [regex]::Matches($bodyContent, $jsPattern)
    $extraJsLines = @()
    $bodyContentClean = $bodyContent

    foreach ($m in $jsMatches) {
        $src = $m.Groups[1].Value
        $isBootstrap = $src -match 'bootstrap'
        $isConsolidated = $false
        foreach ($j in $consolidatedJS) {
            if ($src -match [regex]::Escape($j)) { $isConsolidated = $true; break }
        }
        if ($isBootstrap -or $isConsolidated) {
            $bodyContentClean = $bodyContentClean.Replace($m.Value, '')
        } else {
            $extraJsLines += $m.Value
            $bodyContentClean = $bodyContentClean.Replace($m.Value, '')
        }
    }

    $bodyContentClean = $bodyContentClean.Trim()

    # Build new content using StringBuilder
    $sb = New-Object System.Text.StringBuilder
    $null = $sb.AppendLine("{% extends ""$baseTemplate"" %}")
    $null = $sb.AppendLine("{% block title %}$title{% endblock %}")
    $null = $sb.AppendLine("")
    $null = $sb.AppendLine("{% block extra_css %}")
    if ($extraCssLines.Count -gt 0) {
        $null = $sb.AppendLine("    <!-- Original CSS references -->")
        foreach ($line in $extraCssLines) {
            $null = $sb.AppendLine("    $line")
        }
    }
    $null = $sb.AppendLine("{% endblock %}")
    $null = $sb.AppendLine("")
    $null = $sb.AppendLine("{% block content %}")
    $null = $sb.AppendLine($bodyContentClean)
    $null = $sb.AppendLine("{% endblock %}")
    $null = $sb.AppendLine("")
    $null = $sb.AppendLine("{% block extra_js %}")
    if ($extraJsLines.Count -gt 0) {
        $null = $sb.AppendLine("    <!-- Original JS references -->")
        foreach ($line in $extraJsLines) {
            $null = $sb.AppendLine("    $line")
        }
    }
    $null = $sb.AppendLine("{% endblock %}")

    $newContent = $sb.ToString()
    [System.IO.File]::WriteAllText($path, $newContent, [System.Text.Encoding]::UTF8)

    $log += "$filename -> $baseTemplate (CSS:$($extraCssLines.Count) JS:$($extraJsLines.Count))"
    Write-Host "  OK" -ForegroundColor Cyan
}

Write-Host "`n===== SUMMARY =====" -ForegroundColor Magenta
$log | ForEach-Object { Write-Host $_ }
Write-Host "Total: $($log.Count) templates" -ForegroundColor Magenta
