#!/bin/bash
# ============================================================
# YouTube自動化パイプライン — 実行スクリプト
# ============================================================
# 用途: EC2 上で Cron から定期実行（毎日 6:00）
#
# Usage: ./run_pipeline.sh
# または crontab で: 0 6 * * * /path/to/run_pipeline.sh

set -e

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR${NC} $1"
}

# ============================================================
# 環境設定
# ============================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
LOG_DIR="$PROJECT_DIR/out"
LOG_FILE="$LOG_DIR/pipeline_$(date +%Y%m%d_%H%M%S).log"

# ログディレクトリ作成
mkdir -p "$LOG_DIR"
mkdir -p "$PROJECT_DIR/tmp"

# ============================================================
# 仮想環境を有効化
# ============================================================
log_info "仮想環境を初期化中..."

# ホームディレクトリを自動検出
if [ -d "/home/ec2-user" ]; then
    HOME_DIR="/home/ec2-user"
elif [ -d "/home/ubuntu" ]; then
    HOME_DIR="/home/ubuntu"
else
    log_error "ホームディレクトリが見つかりません"
    exit 1
fi

if [ -f "$HOME_DIR/venv/bin/activate" ]; then
    source "$HOME_DIR/venv/bin/activate"
    log_info "仮想環境: $HOME_DIR/venv"
else
    log_error "仮想環境が見つかりません: $HOME_DIR/venv"
    exit 1
fi

# ============================================================
# .env ファイル確認
# ============================================================
if [ ! -f "$PROJECT_DIR/.env" ]; then
    log_error ".env ファイルが見つかりません"
    log_error "以下を実行してください: cp .env.example .env && nano .env"
    log_error "パス: $PROJECT_DIR/.env"
    exit 1
fi

# 環境変数ロード
set -a
source "$PROJECT_DIR/.env"
set +a

log_info "✅ 環境変数をロード完了"

# ============================================================
# Dependency チェック
# ============================================================
log_info "依存関係をチェック中..."

if ! command -v ffmpeg &> /dev/null; then
    log_error "ffmpeg が見つかりません"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    log_error "python3 が見つかりません"
    exit 1
fi

log_info "✅ 依存関係チェック完了"

# ============================================================
# パイプライン実行
# ============================================================
log_info "=================================================="
log_info "YouTube自動化パイプラインを開始..."
log_info "=================================================="
log_info ""

cd "$PROJECT_DIR"

# メインスクリプト実行（ログに全出力を記録）
if python3 youtube_pipeline.py \
    --output "$LOG_DIR" \
    --log-file "$LOG_FILE" \
    >> "$LOG_FILE" 2>&1; then

    log_info "=================================================="
    log_info "✅ パイプライン完了！！"
    log_info "=================================================="
    log_info ""
    log_info "📹 出力ファイル:"
    ls -lh "$LOG_DIR"/final_*.mp4 2>/dev/null || log_info "   (動画ファイル生成待機中)"
    log_info ""
    log_info "ログファイル: $LOG_FILE"

    # ============================================================
    # S3 にバックアップ（オプション）
    # ============================================================
    if [ ! -z "$AWS_S3_BUCKET" ]; then
        log_info ""
        log_info "S3 にバックアップ中..."
        if aws s3 sync "$LOG_DIR" "s3://$AWS_S3_BUCKET/youtube_automation/$(date +%Y%m%d)/" \
            --region "$AWS_REGION" \
            >> "$LOG_FILE" 2>&1; then
            log_info "✅ S3 バックアップ完了"
            log_info "  s3://$AWS_S3_BUCKET/youtube_automation/$(date +%Y%m%d)/"
        else
            log_error "S3 バックアップに失敗しました（スキップ）"
        fi
    fi

    exit 0
else
    log_error "=================================================="
    log_error "❌ パイプラインが失敗しました"
    log_error "=================================================="
    log_error ""
    log_error "ログを確認してください: $LOG_FILE"
    log_error ""
    tail -n 50 "$LOG_FILE"
    exit 1
fi
