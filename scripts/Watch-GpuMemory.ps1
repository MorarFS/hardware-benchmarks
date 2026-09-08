param(
    [Parameter(Mandatory)][System.Diagnostics.Process]$BenchmarkProcess,
    [Parameter(Mandatory)][string]$OutputCsv
)
# Called immediately after launching llama-bench. Requires English Windows counter names.
$memoryRows = [System.Collections.Generic.List[object]]::new()
$memoryClock = [System.Diagnostics.Stopwatch]::StartNew()
while (!$BenchmarkProcess.WaitForExit(5000)) {
    $memorySample = Get-Counter '\GPU Process Memory(*)\Dedicated Usage', '\GPU Process Memory(*)\Shared Usage', '\GPU Process Memory(*)\Local Usage', '\GPU Process Memory(*)\Non Local Usage' -ErrorAction SilentlyContinue
    foreach ($sample in $memorySample.CounterSamples) {
        if ($sample.InstanceName -like ('pid_' + $BenchmarkProcess.Id + '_*')) {
            $memoryRows.Add([pscustomobject]@{elapsed_seconds=$memoryClock.Elapsed.TotalSeconds; adapter=$sample.InstanceName; counter=($sample.Path -split '\\')[-1]; bytes=$sample.CookedValue})
        }
    }
}
$BenchmarkProcess.WaitForExit()
if (!$memoryRows.Count) { Write-Warning 'No GPU memory samples captured; counters may be unavailable.'; return }
# Match the recorded summary: select the adapter with the highest dedicated sample.
$primary = ($memoryRows | Where-Object counter -eq 'dedicated usage' | Sort-Object {[double]$_.bytes} -Descending | Select-Object -First 1).adapter
$labels = @{}
if ($primary) { $labels[$primary] = 'primary-benchmark-adapter' }
$otherIndex = 0
foreach ($row in $memoryRows) {
    if (!$labels.ContainsKey($row.adapter)) { $otherIndex++; $labels[$row.adapter] = 'other-adapter-' + $otherIndex }
    $row.adapter = $labels[$row.adapter]
}
$memoryRows | Export-Csv -LiteralPath $OutputCsv -NoTypeInformation
