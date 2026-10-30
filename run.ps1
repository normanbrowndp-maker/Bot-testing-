$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$botDir = Join-Path $root 'bot-python'
$envFile = Join-Path $botDir '.env'

if (-not (Test-Path -LiteralPath $envFile)) {
    Copy-Item -LiteralPath (Join-Path $botDir '.env.example') -Destination $envFile
    notepad $envFile
    Write-Host 'Заполни TELEGRAM_BOT_TOKEN и ADMIN_ID, сохрани файл и запусти снова.'
    exit
}

Get-Content -LiteralPath $envFile | ForEach-Object {
    $line = $_.Trim()
    if ($line -and -not $line.StartsWith('#') -and $line.Contains('=')) {
        $parts = $line.Split('=', 2)
        $value = $parts[1].Trim()
        if (($value.StartsWith('"') -and $value.EndsWith('"')) -or ($value.StartsWith("'") -and $value.EndsWith("'"))) {
            $value = $value.Substring(1, $value.Length - 2)
        }
        [Environment]::SetEnvironmentVariable($parts[0].Trim(), $value, 'Process')
    }
}

if (-not $env:TELEGRAM_BOT_TOKEN -or -not $env:ADMIN_ID) {
    throw 'В .env укажи TELEGRAM_BOT_TOKEN и ADMIN_ID.'
}

Push-Location $botDir
try {
    python bot.py
} finally {
    Pop-Location
}
