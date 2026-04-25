$ErrorActionPreference = "Stop"

$pluginRoot = Split-Path -Parent $PSScriptRoot
$skillsRoot = Join-Path $HOME ".codex\skills"

$skills = @(
    "graphic-brief-production",
    "graphic-delivery-audit"
)

foreach ($skill in $skills) {
    $source = Join-Path $pluginRoot "skills\$skill"
    $destination = Join-Path $skillsRoot $skill

    if (-not (Test-Path -LiteralPath $source)) {
        throw "Missing source skill: $source"
    }

    if (Test-Path -LiteralPath $destination) {
        Remove-Item -LiteralPath $destination -Recurse -Force
    }

    Copy-Item -LiteralPath $source -Destination $destination -Recurse -Force
    Write-Host "Synced $skill -> $destination"
}
