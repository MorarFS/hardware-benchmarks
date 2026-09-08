param(
    [Parameter(Mandatory)][string]$Executable,
    [Parameter(Mandatory)][string]$Device,
    [Parameter(Mandatory)][ValidatePattern('^[a-z0-9-]+$')][string]$RunName,
    [ValidateSet('qwen3-8b','nemotron-49b')][string]$ModelId = 'qwen3-8b',
    [string]$Model,
    [string]$OutputRoot = (Join-Path $PSScriptRoot '../local-results'),
    [ValidateRange(1,100)][int]$Repetitions = 5
)
$ErrorActionPreference = 'Stop'
$spec = (Get-Content (Join-Path $PSScriptRoot 'models.json') -Raw | ConvertFrom-Json).$ModelId
if (!$Model) { $Model = Join-Path $PSScriptRoot ('../work/' + $spec.filename) }
$Executable = (Resolve-Path -LiteralPath $Executable).Path
$Model = (Resolve-Path -LiteralPath $Model).Path
$expected = $spec.sha256
if ((Get-FileHash -LiteralPath $Model -Algorithm SHA256).Hash -ne $expected) { throw 'Model SHA-256 mismatch.' }
$resultDirectory = Join-Path $OutputRoot ($RunName + '-' + (Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
New-Item -ItemType Directory -Path $resultDirectory | Out-Null
& $Executable --list-devices
if ($LASTEXITCODE -ne 0) { throw 'Device enumeration failed.' }
foreach ($depth in @(0,2048)) {
    $promptLength = if ($depth -eq 0) { 512 } else { 0 }
    $stem = Join-Path $resultDirectory ($RunName + '-depth' + $depth)
    $benchArgs = @('-m',$Model,'-dev',$Device,'-sm','none','-ngl','99','-fa','on','-b','512','-ub','512','-t','10','-ctk','f16','-ctv','f16','-p',"$promptLength",'-n','256','-d',"$depth",'-r',"$Repetitions",'-o','json','--progress')
    & $Executable @benchArgs 1> ($stem + '.json') 2> ($stem + '.log')
    if ($LASTEXITCODE -ne 0) { throw "Benchmark failed; inspect local log: $stem.log" }
    if ($ModelId -eq 'nemotron-49b') {
        $offload = [regex]::Match((Get-Content -LiteralPath ($stem + '.log') -Raw), 'offloaded\s+(\d+)/(\d+)\s+layers to GPU')
        if (!$offload.Success -or [int]$offload.Groups[1].Value -eq 0 -or $offload.Groups[1].Value -ne $offload.Groups[2].Value) {
            throw 'Full GPU layer offload was not confirmed. Do not report this as a full-GPU capacity result.'
        }
    }
    $entries = @(Get-Content -LiteralPath ($stem + '.json') -Raw | ConvertFrom-Json)
    if (!$entries.Count) { throw 'No measured results.' }
    foreach ($entry in $entries) { $entry.model_filename = Split-Path $Model -Leaf }
    ConvertTo-Json -InputObject $entries -Depth 10 | Set-Content -LiteralPath ($stem + '.json') -Encoding utf8
}
Write-Host "Results: $resultDirectory. Inspect logs to verify the selected GPU handled the workload before publishing."
