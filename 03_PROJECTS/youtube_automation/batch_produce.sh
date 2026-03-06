#!/bin/bash
# ============================================================
# YouTube自動化パイプライン — 量産バッチ実行スクリプト
# ============================================================
# 実行場所: EC2 (Linux)
# 用途: Cron から定期実行（毎日複数本の動画を順番に生成・アップロード）
#
# Usage: bash batch_produce.sh [NUM_VIDEOS]
#   bash batch_produce.sh              # デフォルト 3本
#   bash batch_produce.sh 5            # 5本を生成
#
# 前提条件:
#   - EC2 インスタンス上で実行
#   - run_pipeline.sh が同ディレクトリに存在
#   - .env ファイルがセットアップ済み

set -e

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ============================================================
# 変数定義
# ============================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
LOG_FILE="$LOG_DIR/batch_$(date +%Y-%m-%d).log"
PIPELINE_SCRIPT="$SCRIPT_DIR/run_pipeline.sh"

NUM_VIDEOS=${1:-3}
WAIT_SEC=300

SUCCESS_COUNT=0
FAIL_COUNT=0
TOTAL_COUNT=0

START_TIME=$(date '+%Y-%m-%d %H:%M:%S')
START_TIMESTAMP=$(date +%s)

# ============================================================
# ログ関数
# ============================================================
log_info() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] ✅${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ❌${NC} $1" | tee -a "$LOG_FILE"
}

log_warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️${NC} $1" | tee -a "$LOG_FILE"
}

# ============================================================
# STEP 1: 前提チェック
# ============================================================
mkdir -p "$LOG_DIR"

log_info "========== Batch Produce Start =========="
log_info "開始時刻: $START_TIME"
log_info "処理対象: $NUM_VIDEOS 本の動画"

if [ ! -f "$PIPELINE_SCRIPT" ]; then
    log_error "パイプラインスクリプトが見つかりません: $PIPELINE_SCRIPT"
    exit 1
fi

log_info "Pipeline: $PIPELINE_SCRIPT"
log_info ""

# ============================================================
# STEP 2: tmpクリーンアップ
# ============================================================
log_info "前回の一時ファイルをクリーンアップ中..."
if [ -d "$SCRIPT_DIR/tmp" ]; then
    rm -rf "$SCRIPT_DIR/tmp"/*
fi
mkdir -p "$SCRIPT_DIR/tmp"
log_info ""

# ============================================================
# STEP 3: バッチループ
# ============================================================
log_info "========== バッチ処理開始 =========="
log_info ""

for i in $(seq 1 "$NUM_VIDEOS"); do
    log_info "=== Video $i/$NUM_VIDEOS ==="

    # 個別パイプライン実行（set +e で終了コード取得）
    set +e
    bash "$PIPELINE_SCRIPT" >> "$LOG_FILE" 2>&1
    RESULT=$?
    set -e

    if [ $RESULT -eq 0 ]; then
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        log_success "Video $i 完了"
    else
        FAIL_COUNT=$((FAIL_COUNT + 1))
        log_error "Video $i 失敗 (終了コード: $RESULT)"
    fi

    TOTAL_COUNT=$((TOTAL_COUNT + 1))

    # 待機（最後の動画は除く）
    if [ $i -lt "$NUM_VIDEOS" ]; then
        log_info "[WAIT] 次の動画まで ${WAIT_SEC}秒待機中..."
        sleep "$WAIT_SEC"
    fi

    log_info ""
done

# ============================================================
# STEP 4: 完了サマリー
# ============================================================
END_TIME=$(date '+%Y-%m-%d %H:%M:%S')
END_TIMESTAMP=$(date +%s)
ELAPSED_SEC=$((END_TIMESTAMP - START_TIMESTAMP))

log_info "========== バッチ完了 =========="
log_info "[SUMMARY]"
log_info "  開始時刻:   $START_TIME"
log_info "  終了時刻:   $END_TIME"
log_info "  合計時間:   ${ELAPSED_SEC}秒"
log_info "  成功数:     $SUCCESS_COUNT 本"
log_info "  失敗数:     $FAIL_COUNT 本"
log_info "  合計:       $TOTAL_COUNT 本"
log_info ""

if [ $FAIL_COUNT -eq 0 ]; then
    log_success "すべての動画処理が完了しました！"
    exit 0
else
    log_warn "$FAIL_COUNT 本の動画で失敗が発生しました"
    exit 1
fi
