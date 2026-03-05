# ============================================================
# 動画自動編集パイプライン — Windows ワンコマンド実行スクリプト
# Usage: .\run.ps1 [config.yaml]
# ============================================================

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

$Config = if ($args[0]) { $args[0] } else { "config.yaml" }

Write-Host "============================================"
Write-Host " 動画自動編集パイプライン"
Write-Host "============================================"
Write-Host "Config: $Config"
Write-Host "Working dir: $ScriptDir"
Write-Host ""

# --- 依存チェック ---
Write-Host "[Check] Python..."
$Python = $null
foreach ($cmd in @("python", "python3", "py")) {
    if (Get-Command $cmd -ErrorAction SilentlyContinue) {
        $Python = $cmd
        break
    }
}
if (-not $Python) {
    Write-Host "ERROR: Python not found. Install Python 3.10+"
    exit 1
}
& $Python --version

Write-Host "[Check] ffmpeg..."
if (-not (Get-Command "ffmpeg" -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: ffmpeg not found."
    Write-Host "Install: winget install ffmpeg / choco install ffmpeg / scoop install ffmpeg"
    exit 1
}
ffmpeg -version 2>&1 | Select-Object -First 1

Write-Host "[Check] pip packages..."
& $Python -m pip install -q -r requirements.txt 2>$null

# --- ディレクトリ準備 ---
foreach ($d in @("in", "out", "tmp", "dict", "assets")) {
    if (-not (Test-Path $d)) { New-Item -ItemType Directory -Path $d | Out-Null }
}

# --- 入力チェック ---
$InputFiles = Get-ChildItem -Path "in" -File -Include @("*.mp4","*.mov","*.avi","*.mkv","*.webm") -ErrorAction SilentlyContinue
$InputCount = ($InputFiles | Measure-Object).Count
if ($InputCount -eq 0) {
    Write-Host ""
    Write-Host "WARNING: No video files found in .\in\"
    Write-Host "Put your video files in the .\in\ directory and run again."
    exit 0
}
Write-Host ""
Write-Host "Found $InputCount video(s) in .\in\"
Write-Host ""

# --- 実行 ---
Write-Host "Starting pipeline..."
Write-Host "--------------------------------------------"
& $Python main.py --config $Config
$ExitCode = $LASTEXITCODE

Write-Host ""
Write-Host "============================================"
if ($ExitCode -eq 0) {
    Write-Host " OK! Output: .\out\"
} else {
    Write-Host " ERROR (exit=$ExitCode)"
    Write-Host "   Log: .\out\pipeline.log"
}
Write-Host "============================================"

exit $ExitCode
