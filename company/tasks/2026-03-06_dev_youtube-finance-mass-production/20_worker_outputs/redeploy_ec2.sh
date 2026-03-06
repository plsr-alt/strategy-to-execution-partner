#!/bin/bash
# ============================================================
# YouTube自動化パイプライン — EC2再デプロイスクリプト
# ============================================================
# Usage: bash redeploy_ec2.sh [IP_ADDRESS]
#
# 概要:
#   スポットインスタンス消失後、新しいEC2インスタンスに
#   YouTube自動化パイプラインの完全な環境を1コマンドで復旧。
#   冪等性を確保し、複数回実行時も安全。
#
# 例:
#   bash redeploy_ec2.sh                      # デフォルトIP（18.183.153.86）を使用
#   bash redeploy_ec2.sh 54.123.45.67        # 新しいIPを指定
#

set -e

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# ============================================================
# STEP 0: 環境変数定義
# ============================================================

# コマンドライン引数から EC2_IP を取得（デフォルト値あり）
EC2_IP="${1:-18.183.153.86}"
EC2_USER="ec2-user"
EC2_PASS="Welcome1234!"
EC2_HOME="/home/ec2-user"

# ローカルディレクトリ（ホストマシン側）— WSLパス形式
LOCAL_DIR="/mnt/c/Users/tshibasaki/Desktop/etc/work/task/03_PROJECTS/youtube_automation"

# リモートディレクトリ
REMOTE_DIR="~/youtube_automation"

# 転送対象ファイル一覧
TRANSFER_FILES=(
    "youtube_pipeline.py"
    "requirements.txt"
    "run_pipeline.sh"
    "groq_executor.py"
    "token.json"
    "batch_produce.sh"
    "setup_cron.sh"
)

log_info "============================================================"
log_info "EC2再デプロイスクリプト開始"
log_info "============================================================"
log_info "Target EC2 IP: $EC2_IP"
log_info "Local Directory: $LOCAL_DIR"
log_info "Remote Directory: $REMOTE_DIR"
log_info ""

# ============================================================
# STEP 1: 前提チェック
# ============================================================

log_step "前提チェックを実行中..."

# sshpass がインストール済みか確認
if ! command -v sshpass &> /dev/null; then
    log_error "sshpass がインストールされていません"
    log_info "インストール方法: apt-get install sshpass (Ubuntu/WSL)"
    exit 1
fi
log_info "✅ sshpass: $(sshpass -V | head -1)"

# EC2_IP が設定されているか
if [ -z "$EC2_IP" ]; then
    log_error "EC2_IP が設定されていません"
    exit 1
fi
log_info "✅ EC2_IP: $EC2_IP"

# LOCAL_DIR が存在するか確認
if [ ! -d "$LOCAL_DIR" ]; then
    log_error "ローカルディレクトリが存在しません: $LOCAL_DIR"
    exit 1
fi
log_info "✅ LOCAL_DIR: $LOCAL_DIR"

# 転送対象ファイルが存在するか確認
log_info "転送対象ファイルの確認..."
for file in "${TRANSFER_FILES[@]}"; do
    if [ "$file" = ".env" ]; then
        # .env は特別処理（SSH経由で転送）
        log_warn "  ⚠️  $file (SSH経由で転送予定)"
    elif [ ! -f "$LOCAL_DIR/$file" ]; then
        log_warn "  ⚠️  $file (見つかりません - scpスキップ)"
    else
        log_info "  ✅ $file"
    fi
done

log_info ""

# ============================================================
# STEP 2: EC2への接続確認
# ============================================================

log_step "EC2への接続確認..."

if sshpass -p "$EC2_PASS" ssh \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    "$EC2_USER@$EC2_IP" "echo OK" > /dev/null 2>&1; then
    log_info "✅ EC2接続確認: 成功"
else
    log_error "EC2接続失敗。以下を確認してください:"
    log_error "  1. EC2_IP (現在: $EC2_IP) が正しいか"
    log_error "  2. EC2インスタンスが起動しているか"
    log_error "  3. パスワード認証が有効になっているか"
    exit 1
fi

log_info ""

# ============================================================
# STEP 3: 転送前のクリーンアップ（冪等性確保）
# ============================================================

log_step "リモートディレクトリをクリーンアップ中..."

sshpass -p "$EC2_PASS" ssh \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    "$EC2_USER@$EC2_IP" \
    "mkdir -p $REMOTE_DIR && cd $REMOTE_DIR && rm -f youtube_pipeline.py requirements.txt run_pipeline.sh groq_executor.py token.json batch_produce.sh setup_cron.sh" \
    2>/dev/null || true

log_info "✅ リモートディレクトリをクリーンアップ"
log_info ""

# ============================================================
# STEP 4: ファイル転送（scp）
# ============================================================

log_step "ファイルをEC2に転送中..."

SUCCESS_TRANSFER=0
FAIL_TRANSFER=0

for file in "${TRANSFER_FILES[@]}"; do
    if [ "$file" = ".env" ]; then
        # .env は特別処理（後続ステップで実施）
        log_warn "  ⏭️  $file (後続ステップで転送)"
        continue
    fi

    if [ ! -f "$LOCAL_DIR/$file" ]; then
        log_warn "  ⏭️  $file (ローカルに見つかりません)"
        continue
    fi

    if sshpass -p "$EC2_PASS" scp \
        -o StrictHostKeyChecking=no \
        -o UserKnownHostsFile=/dev/null \
        "$LOCAL_DIR/$file" \
        "$EC2_USER@$EC2_IP:$REMOTE_DIR/" \
        > /dev/null 2>&1; then
        log_info "  ✅ $file"
        ((SUCCESS_TRANSFER++))
    else
        log_warn "  ⚠️  $file (転送失敗 - スキップ)"
        ((FAIL_TRANSFER++))
    fi
done

log_info "転送完了: $SUCCESS_TRANSFER個成功, $FAIL_TRANSFER個失敗"

# .env の転送（SSH経由のフォールバック）
log_info ""
log_step ".envファイルの転送（SSH経由）..."

if [ -f "$LOCAL_DIR/.env" ]; then
    # scpで転送を試みる
    if sshpass -p "$EC2_PASS" scp \
        -o StrictHostKeyChecking=no \
        -o UserKnownHostsFile=/dev/null \
        "$LOCAL_DIR/.env" \
        "$EC2_USER@$EC2_IP:$REMOTE_DIR/" \
        > /dev/null 2>&1; then
        log_info "✅ .env (scp転送成功)"
    else
        # scpが失敗した場合、SSH経由でcatで内容を転送
        log_warn "⚠️  scpが失敗。SSH経由での転送を試行中..."

        # ローカルから .env の内容を読み込んでSSH経由で転送
        ENV_CONTENT=$(cat "$LOCAL_DIR/.env" | sed 's/"/\\"/g' | sed "s/'/\\\\'/g")

        if sshpass -p "$EC2_PASS" ssh \
            -o StrictHostKeyChecking=no \
            -o UserKnownHostsFile=/dev/null \
            "$EC2_USER@$EC2_IP" \
            "cat > $REMOTE_DIR/.env << 'EOF'
$(cat "$LOCAL_DIR/.env")
EOF" \
            > /dev/null 2>&1; then
            log_info "✅ .env (SSH経由での転送成功)"
        else
            log_warn "⚠️  .env転送失敗 (手動で転送してください)"
        fi
    fi
else
    log_warn "⚠️  .env が見つかりません (後で手動で設定してください)"
fi

log_info ""

# ============================================================
# STEP 5: リモートディレクトリの初期化
# ============================================================

log_step "リモートディレクトリを初期化中..."

sshpass -p "$EC2_PASS" ssh \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    "$EC2_USER@$EC2_IP" \
    "mkdir -p $REMOTE_DIR/logs $REMOTE_DIR/out $REMOTE_DIR/tmp && chmod 755 $REMOTE_DIR/logs $REMOTE_DIR/out $REMOTE_DIR/tmp" \
    > /dev/null 2>&1

log_info "✅ logs/, out/, tmp/ ディレクトリを作成"
log_info ""

# ============================================================
# STEP 6: スクリプト実行権限を設定
# ============================================================

log_step "スクリプト実行権限を設定中..."

sshpass -p "$EC2_PASS" ssh \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    "$EC2_USER@$EC2_IP" \
    "chmod +x $REMOTE_DIR/youtube_pipeline.py $REMOTE_DIR/run_pipeline.sh $REMOTE_DIR/batch_produce.sh $REMOTE_DIR/setup_cron.sh" \
    > /dev/null 2>&1

log_info "✅ 実行権限を設定"
log_info ""

# ============================================================
# STEP 7: Python仮想環境構築とパッケージインストール
# ============================================================

log_step "Python仮想環境を構築中..."

sshpass -p "$EC2_PASS" ssh \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    "$EC2_USER@$EC2_IP" \
    "if [ ! -d ~/venv ]; then
        python3 -m venv ~/venv
        echo '✅ 仮想環境を作成'
    else
        echo '✅ 仮想環境は既に存在'
    fi" \
    2>/dev/null

log_step "Pythonパッケージをインストール中..."

sshpass -p "$EC2_PASS" ssh \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    "$EC2_USER@$EC2_IP" \
    "source ~/venv/bin/activate && pip install -r $REMOTE_DIR/requirements.txt" \
    > /dev/null 2>&1

log_info "✅ パッケージインストール完了"
log_info ""

# ============================================================
# STEP 8: VOICEVOX Dockerコンテナ確認・起動
# ============================================================

log_step "VOICEVOX Docker確認中..."

VOICEVOX_STATUS=$(sshpass -p "$EC2_PASS" ssh \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    "$EC2_USER@$EC2_IP" \
    "docker ps --filter 'name=voicevox' --format '{{.State}}' 2>/dev/null || echo 'not_found'" \
    2>/dev/null)

if [ "$VOICEVOX_STATUS" = "running" ]; then
    log_info "✅ VOICEVOX: 既に起動中"
else
    log_warn "⚠️  VOICEVOX: 起動していません。起動を試みます..."

    # docker start で既存コンテナを起動
    if sshpass -p "$EC2_PASS" ssh \
        -o StrictHostKeyChecking=no \
        -o UserKnownHostsFile=/dev/null \
        "$EC2_USER@$EC2_IP" \
        "docker start voicevox 2>/dev/null || docker run -d --name voicevox -p 50021:50021 voicevox/voicevox:latest" \
        > /dev/null 2>&1; then
        log_info "✅ VOICEVOX: 起動完了"
    else
        log_warn "⚠️  VOICEVOX: 起動失敗 (スクリプト実行時に検出されます)"
    fi
fi

log_info ""

# ============================================================
# STEP 9: 動作確認テスト
# ============================================================

log_step "動作確認テストを実行中..."

# Python version check
PYTHON_VERSION=$(sshpass -p "$EC2_PASS" ssh \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    "$EC2_USER@$EC2_IP" \
    "python3 --version" 2>/dev/null)
log_info "✅ Python: $PYTHON_VERSION"

# ffmpeg check
FFMPEG_VERSION=$(sshpass -p "$EC2_PASS" ssh \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    "$EC2_USER@$EC2_IP" \
    "ffmpeg -version 2>/dev/null | head -1" 2>/dev/null)
log_info "✅ ffmpeg: $FFMPEG_VERSION"

# venv activate check
VENV_CHECK=$(sshpass -p "$EC2_PASS" ssh \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    "$EC2_USER@$EC2_IP" \
    "source ~/venv/bin/activate && python3 -c 'import sys; print(sys.prefix)'" 2>/dev/null)
log_info "✅ venv: $VENV_CHECK"

# youtube_pipeline.py help
if sshpass -p "$EC2_PASS" ssh \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    "$EC2_USER@$EC2_IP" \
    "source ~/venv/bin/activate && python3 $REMOTE_DIR/youtube_pipeline.py --help" \
    > /dev/null 2>&1; then
    log_info "✅ youtube_pipeline.py: 実行可能"
else
    log_warn "⚠️  youtube_pipeline.py: ヘルプの実行に失敗"
fi

log_info ""

# ============================================================
# STEP 10: 完了ログ出力
# ============================================================

log_info "============================================================"
log_info "✅✅✅ EC2再デプロイが完了しました！！"
log_info "============================================================"
log_info ""
log_info "次のステップ:"
log_info "  1. .env ファイルが正しく転送されたか確認:"
log_info "     sshpass -p \"$EC2_PASS\" ssh $EC2_USER@$EC2_IP \"cat $REMOTE_DIR/.env\""
log_info ""
log_info "  2. Cron設定をセットアップ:"
log_info "     sshpass -p \"$EC2_PASS\" ssh $EC2_USER@$EC2_IP \"bash $REMOTE_DIR/setup_cron.sh\""
log_info ""
log_info "  3. 動作確認（手動テスト）:"
log_info "     sshpass -p \"$EC2_PASS\" ssh $EC2_USER@$EC2_IP \"source ~/venv/bin/activate && python3 $REMOTE_DIR/youtube_pipeline.py --help\""
log_info ""
log_info "スポット消失時の再実行:"
log_info "  bash redeploy_ec2.sh <新しいIP>"
log_info ""
log_info "実行時刻: $(date '+%Y-%m-%d %H:%M:%S')"
log_info "============================================================"
