# GatherAgent — Windows Installation Script
# Run: powershell -ExecutionPolicy Bypass -File install.ps1

Write-Host "Installing GatherAgent..." -ForegroundColor Cyan

# Check Python version (requires 3.11+)
$pythonCmd = $null
foreach ($cmd in @("python3", "python")) {
    try {
        $version = & $cmd --version 2>&1
        if ($version -match "Python (\d+)\.(\d+)") {
            $major = [int]$Matches[1]
            $minor = [int]$Matches[2]
            if ($major -ge 3 -and $minor -ge 11) {
                $pythonCmd = $cmd
                Write-Host "Python $major.$minor found [OK]" -ForegroundColor Green
                break
            }
        }
    } catch {}
}

if (-not $pythonCmd) {
    Write-Host "Error: Python 3.11+ is required but not found." -ForegroundColor Red
    Write-Host "Install: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Check optional system deps
foreach ($cmd in @("git")) {
    if (Get-Command $cmd -ErrorAction SilentlyContinue) {
        Write-Host "$cmd found [OK]" -ForegroundColor Green
    } else {
        Write-Host "$cmd not found (optional - some features may be limited)" -ForegroundColor Yellow
    }
}

# Check for ripgrep (optional but recommended)
if (Get-Command rg -ErrorAction SilentlyContinue) {
    Write-Host "ripgrep found [OK]" -ForegroundColor Green
} else {
    Write-Host "ripgrep not found (optional - search will use fallback)" -ForegroundColor Yellow
}

& $pythonCmd -m pip install -e ".[all]"
& gather doctor
Write-Host "Done! Run: gather" -ForegroundColor Green
