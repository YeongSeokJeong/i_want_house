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

$pythonCommand = $null
$pythonArgsPrefix = @()
if ($env:PYTHON) {
  $pythonCommand = $env:PYTHON
} else {
  $python = Get-Command python -ErrorAction SilentlyContinue
  if ($python) {
    $pythonCommand = $python.Source
  } else {
    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) {
      $pythonCommand = $py.Source
      $pythonArgsPrefix = @("-3")
    }
  }
}

if (-not $pythonCommand) {
  throw "Python interpreter not found. Install Python, add it to PATH, or set the PYTHON environment variable."
}

& $pythonCommand @pythonArgsPrefix @argsList
