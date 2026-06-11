param(
  [switch]$DryRun,
  [switch]$Send,
  [string]$Fixture
)

$ErrorActionPreference = "Stop"
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$env:PYTHONPATH = Join-Path $repoRoot "src"

$argsList = @(
  "-m", "jeonseloop.run",
  "--watchlist", (Join-Path $repoRoot "config\watchlist.yaml"),
  "--data-dir", (Join-Path $repoRoot "data"),
  "--logs-dir", (Join-Path $repoRoot "logs")
)

if ($DryRun) {
  $argsList += "--dry-run"
}
if ($Send) {
  $argsList += "--send"
}
if ($Fixture) {
  $argsList += @("--fixture", $Fixture)
}

python @argsList
