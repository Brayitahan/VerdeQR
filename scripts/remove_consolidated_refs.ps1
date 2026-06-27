# Remove references to the 5 consolidated CSS and 4 consolidated JS from all templates
# (They were added by our earlier CSS consolidation and cause conflicts with old CSS files)

$dir = "C:\Users\yaira daniela\Downloads\verdeqr-main\templates"
$count = 0

Get-ChildItem "$dir\*.html" | ForEach-Object {
    $path = $_.FullName
    $content = Get-Content $path -Raw -Encoding UTF8
    $original = $content

    # Remove consolidated CSS links (base.css, components.css, pages.css, responsive.css, animations.css)
    $content = $content -replace '<link[^>]*rel="stylesheet"[^>]*base\.css[^>]*>\s*', ""
    $content = $content -replace '<link[^>]*rel="stylesheet"[^>]*components\.css[^>]*>\s*', ""
    $content = $content -replace '<link[^>]*rel="stylesheet"[^>]*pages\.css[^>]*>\s*', ""
    $content = $content -replace '<link[^>]*rel="stylesheet"[^>]*responsive\.css[^>]*>\s*', ""
    $content = $content -replace '<link[^>]*rel="stylesheet"[^>]*animations\.css[^>]*>\s*', ""

    # Remove consolidated JS links (main.js, carousel.js, qr.js, animations.js)
    # Only if they are not next to a bootstrap script (bootstrap is kept)
    $content = $content -replace '<script[^>]*src="[^"]*main\.js"[^>]*></script>\s*', ""
    $content = $content -replace '<script[^>]*src="[^"]*carousel\.js"[^>]*></script>\s*', ""
    $content = $content -replace '<script[^>]*src="[^"]*qr\.js"[^>]*></script>\s*', ""
    $content = $content -replace '<script[^>]*src="[^"]*animations\.js"[^>]*></script>\s*', ""

    if ($content -ne $original) {
        # Write without BOM
        $utf8 = New-Object System.Text.UTF8Encoding $false
        [System.IO.File]::WriteAllText($path, $content, $utf8)
        $count++
        Write-Host "Fixed: $($_.Name)" -ForegroundColor Green
    }
}

Write-Host "Processed $count files" -ForegroundColor Cyan
