param(
    [ValidateSet('qwen3-8b','nemotron-49b')][string]$ModelId = 'qwen3-8b',
    [string]$Destination = (Join-Path $PSScriptRoot '../work')
)
$ErrorActionPreference = 'Stop'
$spec = (Get-Content (Join-Path $PSScriptRoot 'models.json') -Raw | ConvertFrom-Json).$ModelId
$revision = $spec.revision
$name = $spec.filename
$expected = $spec.sha256
New-Item -ItemType Directory -Path $Destination -Force | Out-Null
$target = Join-Path $Destination $name
if (!(Test-Path -LiteralPath $target)) {
    Invoke-WebRequest "https://huggingface.co/$($spec.repository)/resolve/$revision/$name" -OutFile ($target + '.partial')
    if ((Get-FileHash -LiteralPath ($target + '.partial') -Algorithm SHA256).Hash -ne $expected) { throw 'Downloaded model SHA-256 mismatch.' }
    Move-Item -LiteralPath ($target + '.partial') -Destination $target
}
if ((Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash -ne $expected) { throw 'Existing model SHA-256 mismatch.' }
Write-Host "Verified $name"
