#!/bin/bash
# ============================================================
# YouTube自動化パイプライン — EC2再デプロイスクリプト
# ============================================================
# 実行場所: WSL / LocalMachine (Bash環境)
# 用途: スポットインスタンス消失後、新しいEC2に環境を復旧
#
# Usage: bash redeploy_ec2.sh [IP_ADDRESS]
#   bash redeploy_ec2.sh                   # AWS CLIでIP自動取得
#   bash redeploy_ec2.sh 54.123.45.67      # IP直接指定
#
# 前提条件:
#   - sshpass がインストール済み
#   - ec2-user / 該当パスワード が設定済み
#   - AWS CLIが設定済み（IP自動取得時）

set -e

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

EC2_INSTANCE_ID="i-02ae03f0b54d46ac1"
EC2_REGION="ap-northeast-1"
EC2_USER="ec2-user"
EC2_PASS="Welcome1234!"
EC2_HOME="/home/ec2-user"

# IP自動取得: 引数があればそれを使用、なければAWS CLIで取得
if [ -n "$1" ]; then
    EC2_IP="$1"
    log_info "IP指定: $EC2_IP"
else
    log_step "AWS CLIでEC2のIPを自動取得中..."
    EC2_IP=$(aws ec2 describe-instances \
        --instance-ids "$EC2_INSTANCE_ID" \
        --region "$EC2_REGION" \
        --query 'Reservations[0].Instances[0].PublicIpAddress' \
        --output text 2>/dev/null)

    if [ -z "$EC2_IP" ] || [ "$EC2_IP" = "None" ]; then
        log_error "EC2のパブリックIPが取得できません"
        log_error "インスタンス $EC2_INSTANCE_ID が停止中か、パブリックIPが割り当てられていません"
        log_info "手動指定: bash redeploy_ec2.sh <IP_ADDRESS>"
        exit 1
    fi
    log_info "IP自動取得: $EC2_IP (Instance: $EC2_INSTANCE_ID)"
fi

LOCAL_DIR="/mnt/c/Users/tshibasaki/Desktop/etc/work/task/03_PROJECTS/youtube_automation"
REMOTE_DIR="~/youtube_automation"

TRANSFER_FILES=(
    "youtube_pipeline.py"
    "requirements.txt"
    "run_pipeline.sh"
    "groq_executor.py"
    "token.json"
    "batch_produce.sh"
    "setup_cron.sh"
)

SSH_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"

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

if ! command -v sshpass &> /dev/null; then
    log_error "sshpass がインストールされていません"
    log_info "インストール方法: sudo apt-get install sshpass"
    exit 1
fi
log_info "✅ sshpass: OK"

if [ ! -d "$LOCAL_DIR" ]; then
    log_error "ローカルディレクトリが存在しません: $LOCAL_DIR"
    exit 1
fi
log_info "✅ LOCAL_DIR: $LOCAL_DIR"

if [ ! -f "$LOCAL_DIR/.env" ]; then
    log_warn ".env ファイルがローカルにありません: $LOCAL_DIR/.env"
    log_info "EC2上の既存 .env を確認します（スポット復旧時はSSH経由で作成）"
    ENV_LOCAL=false
else
    log_info "✅ .env ファイル: 存在確認済み"
    ENV_LOCAL=true
fi

log_info "転送対象ファイルの確認..."
for file in "${TRANSFER_FILES[@]}"; do
    if [ ! -f "$LOCAL_DIR/$file" ]; then
        log_warn "  ⚠️  $file (見つかりません - スキップ)"
    else
        log_info "  ✅ $file"
    fi
done
log_info ""

# ============================================================
# STEP 2: EC2への接続確認
# ============================================================

log_step "EC2への接続確認..."

if sshpass -p "$EC2_PASS" ssh $SSH_OPTS "$EC2_USER@$EC2_IP" "echo OK" > /dev/null 2>&1; then
    log_info "✅ EC2接続確認: 成功"
else
    log_error "EC2接続失敗。IP: $EC2_IP を確認してください"
    exit 1
fi
log_info ""

# ============================================================
# STEP 3: リモートディレクトリ初期化
# ============================================================

log_step "リモートディレクトリを初期化中..."

sshpass -p "$EC2_PASS" ssh $SSH_OPTS "$EC2_USER@$EC2_IP" \
    "mkdir -p $REMOTE_DIR/logs $REMOTE_DIR/out $REMOTE_DIR/tmp" 2>/dev/null

log_info "✅ logs/, out/, tmp/ ディレクトリを作成"
log_info ""

# ============================================================
# STEP 4: ファイル転送
# ============================================================

log_step "ファイルをEC2に転送中..."

SUCCESS_TRANSFER=0
FAIL_TRANSFER=0

for file in "${TRANSFER_FILES[@]}"; do
    if [ ! -f "$LOCAL_DIR/$file" ]; then
        continue
    fi

    if sshpass -p "$EC2_PASS" scp $SSH_OPTS \
        "$LOCAL_DIR/$file" "$EC2_USER@$EC2_IP:$REMOTE_DIR/" > /dev/null 2>&1; then
        log_info "  ✅ $file"
        SUCCESS_TRANSFER=$((SUCCESS_TRANSFER + 1))
    else
        log_warn "  ⚠️  $file (転送失敗)"
        FAIL_TRANSFER=$((FAIL_TRANSFER + 1))
    fi
done

log_info "転送完了: ${SUCCESS_TRANSFER}個成功, ${FAIL_TRANSFER}個失敗"

# .env の転送
log_info ""
log_step ".envファイルの転送..."

if [ "$ENV_LOCAL" = true ]; then
    if sshpass -p "$EC2_PASS" scp $SSH_OPTS \
        "$LOCAL_DIR/.env" "$EC2_USER@$EC2_IP:$REMOTE_DIR/" > /dev/null 2>&1; then
        log_info "✅ .env (scp転送成功)"
    else
        log_warn "⚠️  scp失敗。cat パイプで転送中..."
        if cat "$LOCAL_DIR/.env" | sshpass -p "$EC2_PASS" ssh $SSH_OPTS \
            "$EC2_USER@$EC2_IP" "cat > $REMOTE_DIR/.env" > /dev/null 2>&1; then
            log_info "✅ .env (パイプ転送成功)"
        else
            log_error ".env転送失敗。デプロイを中止します。"
            exit 1
        fi
    fi
else
    # ローカルに.envがない場合、EC2上に既存.envがあるか確認
    ENV_EXISTS=$(sshpass -p "$EC2_PASS" ssh $SSH_OPTS "$EC2_USER@$EC2_IP" \
        "test -f $REMOTE_DIR/.env && echo 'yes' || echo 'no'" 2>/dev/null)

    if [ "$ENV_EXISTS" = "yes" ]; then
        log_info "✅ EC2上に既存 .env が存在します（再利用）"
    else
        # .envをSSH経由で直接作成
        log_step "EC2上に .env を作成中..."
        sshpass -p "$EC2_PASS" ssh $SSH_OPTS "$EC2_USER@$EC2_IP" "cat > $REMOTE_DIR/.env" << 'ENVEOF'
GROQ_API_KEY=${GROQ_API_KEY:?Set GROQ_API_KEY env var}
YOUTUBE_API_KEY=${YOUTUBE_API_KEY:?Set YOUTUBE_API_KEY env var}
PEXELS_API_KEY=${PEXELS_API_KEY:?Set PEXELS_API_KEY env var}
TARGET_THEME=auto
VIDEO_DURATION_MIN=20
VIDEO_DURATION_MAX=25
CHANNEL_NAME=マネー研究所
LANGUAGE=ja
YOUTUBE_PUBLISH_MODE=SCHEDULE
YOUTUBE_PUBLISH_HOUR=6
LOG_LEVEL=INFO
OUTPUT_DIR=/home/ec2-user/youtube_automation/out
TEMP_DIR=/home/ec2-user/youtube_automation/tmp
ENVEOF
        log_info "✅ .env をEC2上に直接作成"
    fi
fi
log_info ""

# ============================================================
# STEP 5: タイムゾーン設定
# ============================================================

log_step "タイムゾーンを設定中..."

sshpass -p "$EC2_PASS" ssh $SSH_OPTS "$EC2_USER@$EC2_IP" \
    "sudo timedatectl set-timezone Asia/Tokyo" > /dev/null 2>&1 || \
    log_warn "⚠️  タイムゾーン設定スキップ"

CURRENT_TZ=$(sshpass -p "$EC2_PASS" ssh $SSH_OPTS "$EC2_USER@$EC2_IP" \
    "timedatectl | grep -i timezone | awk '{print \$3}'" 2>/dev/null || echo "unknown")

log_info "✅ タイムゾーン: $CURRENT_TZ"
log_info ""

# ============================================================
# STEP 6: 実行権限・所有権設定
# ============================================================

log_step "実行権限を設定中..."

sshpass -p "$EC2_PASS" ssh $SSH_OPTS "$EC2_USER@$EC2_IP" \
    "chmod +x $REMOTE_DIR/run_pipeline.sh $REMOTE_DIR/batch_produce.sh $REMOTE_DIR/setup_cron.sh && \
     chown -R ec2-user:ec2-user $REMOTE_DIR" > /dev/null 2>&1

log_info "✅ 実行権限・所有権を設定"
log_info ""

# ============================================================
# STEP 7: Python仮想環境 & パッケージインストール
# ============================================================

log_step "Python仮想環境を構築中..."

sshpass -p "$EC2_PASS" ssh $SSH_OPTS "$EC2_USER@$EC2_IP" \
    "if [ ! -d ~/venv ]; then python3 -m venv ~/venv; fi" 2>/dev/null

log_step "Pythonパッケージをインストール中..."

sshpass -p "$EC2_PASS" ssh $SSH_OPTS "$EC2_USER@$EC2_IP" \
    "source ~/venv/bin/activate && pip install -r $REMOTE_DIR/requirements.txt" > /dev/null 2>&1

log_info "✅ パッケージインストール完了"
log_info ""

# ============================================================
# STEP 8: Kokoro TTS 依存（espeak-ng + 日本語フォント）
# ============================================================

log_step "Kokoro TTS 依存パッケージを確認中..."

sshpass -p "$EC2_PASS" ssh $SSH_OPTS "$EC2_USER@$EC2_IP" \
    "sudo yum install -y espeak-ng google-noto-sans-cjk-ttc-fonts ffmpeg 2>/dev/null || \
     sudo apt-get install -y espeak-ng fonts-noto-cjk ffmpeg 2>/dev/null || \
     log_warn 'パッケージインストールスキップ'" > /dev/null 2>&1

log_info "✅ espeak-ng / Noto CJK フォント / ffmpeg 確認完了"
log_info ""

# ============================================================
# STEP 9: 動作確認
# ============================================================

log_step "動作確認テスト..."

PYTHON_VER=$(sshpass -p "$EC2_PASS" ssh $SSH_OPTS "$EC2_USER@$EC2_IP" "python3 --version" 2>/dev/null)
log_info "✅ Python: $PYTHON_VER"

FFMPEG_VER=$(sshpass -p "$EC2_PASS" ssh $SSH_OPTS "$EC2_USER@$EC2_IP" "ffmpeg -version 2>/dev/null | head -1" 2>/dev/null)
log_info "✅ ffmpeg: $FFMPEG_VER"

if sshpass -p "$EC2_PASS" ssh $SSH_OPTS "$EC2_USER@$EC2_IP" \
    "source ~/venv/bin/activate && python3 $REMOTE_DIR/youtube_pipeline.py --help" > /dev/null 2>&1; then
    log_info "✅ youtube_pipeline.py: 実行可能"
else
    log_warn "⚠️  youtube_pipeline.py: ヘルプ実行に失敗"
fi
log_info ""

# ============================================================
# STEP 10: Cron自動セットアップ
# ============================================================

log_step "Cron設定を自動セットアップ中..."

if sshpass -p "$EC2_PASS" ssh $SSH_OPTS "$EC2_USER@$EC2_IP" \
    "bash $REMOTE_DIR/setup_cron.sh" > /dev/null 2>&1; then
    log_info "✅ Cron設定: 完了"
else
    log_warn "⚠️  Cron設定: スキップ（手動実行してください）"
fi
log_info ""

# ============================================================
# 完了
# ============================================================

log_info "============================================================"
log_info "✅ EC2再デプロイが完了しました！！"
log_info "============================================================"
log_info ""
log_info "スポット消失時の再実行:"
log_info "  bash redeploy_ec2.sh <新しいIP>"
log_info ""
log_info "実行時刻: $(date '+%Y-%m-%d %H:%M:%S')"
