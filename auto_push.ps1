# auto_push.ps1 — 毎日23:00に差分をコミット＆プッシュ
#
# 【重要】2026-03-01 以降、自動実行は GitHub Actions に移行しました。
# 本スクリプトは「ローカル手動実行用」として残しています。
# 定期実行は不要です（Windows Task Scheduler タスクは削除してください）。
#
# GitHub Actions ワークフロー: `.github/workflows/daily-auto-commit.yml`
# - feature/YYYY-MM-DD-daily-updates ブランチを自動作成
# - PR自動作成 → 自動マージ（Merge commit）
# - ログ: GitHub Actions UI + `06_OPERATIONS/auto_commit_logs.md`
$repoPath = "C:\Users\tshibasaki\Desktop\etc\work\task"
$logFile  = "$repoPath\auto_push.log"
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
