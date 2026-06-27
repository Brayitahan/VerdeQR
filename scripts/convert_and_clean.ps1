# Step 1: Convert to Jinja2 extends + remove ALL old CSS/JS files (keep only consolidated)
$templatesDir = "C:\Users\yaira daniela\Downloads\verdeqr-main\templates"

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

$results = @()

Get-ChildItem "$templatesDir\*.html" | ForEach-Object {
    $filename = $_.Name
    $path = $_.FullName

    if ($skipFiles -contains $filename) { return }
    if (-not $baseMap.ContainsKey($filename)) { return }

    Write-Host "=== $filename ===" -ForegroundColor Green
    $content = Get-Content $path -Raw -Encoding UTF8
    $baseTemplate = $baseMap[$filename]

    # 1. Extract Title
    $title = "VerdeQR"
    $m = [regex]::Match($content, '<title>(.*?)</title>')
    if ($m.Success) { $title = $m.Groups[1].Value.Trim() }

    # 2. Find body boundaries (this is raw HTML before conversion)
    $bodyOpen = [regex]::Match($content, '<body[^>]*>')
    $bodyCloseIdx = $content.LastIndexOf('</body>')
    if ((-not $bodyOpen.Success) -or ($bodyCloseIdx -eq -1)) {
        Write-Host "  SKIP: no body tags" -ForegroundColor Yellow
        return
    }
    $bodyStartIdx = $bodyOpen.Index + $bodyOpen.Length

    # 3. Extract head <style> blocks only (NOT CSS file links)
    $headSection = $content.Substring(0, $bodyOpen.Index)
    $headStyleBlocks = [regex]::Matches($headSection, '<style>.*?</style>', [Text.RegularExpressions.RegexOptions]::Singleline)
    $headInlineStyles = @()
    foreach ($s in $headStyleBlocks) { $headInlineStyles += $s.Value }

    # 4. Extract body content
    $bodyContent = $content.Substring($bodyStartIdx, $bodyCloseIdx - $bodyStartIdx)

    # 5. Clean body content
    # Remove flash messages include
    $bodyContent = $bodyContent -replace "{%-?\s*include\s+['`"](flash_messages\.html)['`"]\s*-?%}\s*", ""
    # Remove ALL <link rel="stylesheet" ...> tags from body (shouldn't be there but just in case)
    $bodyContent = $bodyContent -replace '<link[^>]*rel="stylesheet"[^>]*>\s*', ""
    # Remove ALL <script src=...> tags (base provides consolidated JS)
    $bodyContent = $bodyContent -replace '<script[^>]*src="[^"]*"[^>]*></script>\s*', ""
    $bodyContent = $bodyContent.Trim()

    # 6. Build new Jinja2 template
    $sb = New-Object System.Text.StringBuilder
    $null = $sb.AppendLine("{% extends ""$baseTemplate"" %}")
    $null = $sb.AppendLine("{% block title %}$title{% endblock %}")
    $null = $sb.AppendLine("")

    if ($headInlineStyles.Count -gt 0) {
        $null = $sb.AppendLine("{% block extra_css %}")
        foreach ($st in $headInlineStyles) { $null = $sb.AppendLine($st) }
        $null = $sb.AppendLine("{% endblock %}")
        $null = $sb.AppendLine("")
    }

    $null = $sb.AppendLine("{% block content %}")
    $null = $sb.AppendLine($bodyContent)
    $null = $sb.AppendLine("{% endblock %}")

    [System.IO.File]::WriteAllText($path, $sb.ToString(), [System.Text.Encoding]::UTF8)
    $results += "$filename -> $baseTemplate (inline styles: $($headInlineStyles.Count))"
    Write-Host "  OK" -ForegroundColor Cyan
}

Write-Host "`n==== RESULTADOS ====" -ForegroundColor Magenta
$results | ForEach-Object { Write-Host $_ }
Write-Host "Total: $($results.Count) templates" -ForegroundColor Magenta
