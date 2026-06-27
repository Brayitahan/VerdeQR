# Remove BOM from all template files and re-write without BOM
$templatesDir = "C:\Users\yaira daniela\Downloads\verdeqr-main\templates"

Get-ChildItem "$templatesDir\*.html" | ForEach-Object {
    $path = $_.FullName
    # Read as bytes
    $bytes = [System.IO.File]::ReadAllBytes($path)
    
    $hasBom = $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF
    
    if ($hasBom) {
        # Read content without BOM
        $content = [System.Text.Encoding]::UTF8.GetString($bytes, 3, $bytes.Length - 3)
        # Write without BOM
        $utf8NoBom = New-Object System.Text.UTF8Encoding $false
        [System.IO.File]::WriteAllText($path, $content, $utf8NoBom)
        Write-Host "Fixed BOM: $($_.Name)" -ForegroundColor Green
    } else {
        Write-Host "No BOM: $($_.Name)" -ForegroundColor Gray
    }
}

Write-Host "Done fixing BOMs" -ForegroundColor Cyan
