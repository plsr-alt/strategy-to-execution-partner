# auto_push.ps1 — 毎日23:00に差分をコミット＆プッシュ
$repoPath = "C:\Users\tshibasaki\Desktop\etc\work\task\strategy-to-execution-partner"
$logFile  = "$repoPath\.claude\auto_push.log"
$branch   = "master"

function Log($msg) {
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$ts] $msg"
    Write-Output $line
    Add-Content -Path $logFile -Value $line
}

Set-Location $repoPath

# 差分チェック
$status = git status --porcelain 2>&1
if (-not $status) {
    Log "No changes. Skip."
    exit 0
}

# ステージング（.gitignore が .env 等を除外）
git add .

# コミット
$date = Get-Date -Format "yyyy-MM-dd"
git commit -m "auto: $date daily sync" 2>&1 | ForEach-Object { Log $_ }

# プッシュ
git push origin $branch 2>&1 | ForEach-Object { Log $_ }

Log "Done."
