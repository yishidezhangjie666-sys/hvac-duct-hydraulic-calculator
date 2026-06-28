$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $ProjectRoot

$PythonExe = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $PythonExe)) {
    Write-Error "Python not found at $PythonExe. Create .venv and install requirements.txt first."
}

& $PythonExe -m compileall app.py modules utils
& $PythonExe -m pytest tests
git diff --check
git status --short
