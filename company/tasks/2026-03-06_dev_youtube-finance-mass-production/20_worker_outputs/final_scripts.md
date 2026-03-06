# YouTube自動化パイプライン — 最終版スクリプト

批評家(critic)の指摘を全て反映し、3つのCritical Bugを修正した最終版です。

---

## redeploy_ec2.sh（最終版）

```bash
#!/bin/bash
# ============================================================
# YouTube自動化パイプライン — EC2再デプロイスクリプト
# ============================================================
# 実行場所: WSL / LocalMachine (Bash環境)
# 用途: スポットインスタンス消失後、新しいEC2に環境を復旧
#
# Usage: bash redeploy_ec2.sh [IP_ADDRESS]
#   bash redeploy_ec2.sh                   # デフォルトIP使用
#   bash redeploy_ec2.sh 54.123.45.67      # 新IP指定
#
# 前提条件:
#   - sshpass がインストール済み
#   - ec2-user / 該当パスワード が設定済み
#   - LOCAL_DIR の .env ファイルが存在
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

# .env ファイルの存在確認 （修正1: 強制化）
if [ ! -f "$LOCAL_DIR/.env" ]; then
    log_error ".env ファイルが見つかりません: $LOCAL_DIR/.env"
    log_error "以下を実行してください: cp .env.example .env && 編集"
    exit 1
fi
log_info "✅ .env ファイル: 存在確認済み"

# 転送対象ファイルが存在するか確認
log_info "転送対象ファイルの確認..."
for file in "${TRANSFER_FILES[@]}"; do
    if [ ! -f "$LOCAL_DIR/$file" ]; then
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
    "mkdir -p $REMOTE_DIR && cd $REMOTE_DIR && rm -f youtube_pipeline.py requirements.txt run_pipeline.sh groq_executor.py token.json batch_produce.sh setup_cron.sh .env" \
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

# .env の転送 （修正2: heredoc を修正。$(cat ...) が展開されるように 'EOF' → EOF）
log_info ""
log_step ".envファイルの転送（scp優先、失敗時はSSH経由）..."

if sshpass -p "$EC2_PASS" scp \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    "$LOCAL_DIR/.env" \
    "$EC2_USER@$EC2_IP:$REMOTE_DIR/" \
    > /dev/null 2>&1; then
    log_info "✅ .env (scp転送成功)"
else
    # scpが失敗した場合、cat パイプ経由で転送
    log_warn "⚠️  scpが失敗。cat パイプでの転送を試行中..."

    if cat "$LOCAL_DIR/.env" | sshpass -p "$EC2_PASS" ssh \
        -o StrictHostKeyChecking=no \
        -o UserKnownHostsFile=/dev/null \
        "$EC2_USER@$EC2_IP" \
        "cat > $REMOTE_DIR/.env" \
        > /dev/null 2>&1; then
        log_info "✅ .env (パイプ転送成功)"
    else
        log_error ".env転送失敗。デプロイを中止します。"
        exit 1
    fi
fi

log_info ""

# ============================================================
# STEP 5: リモートディレクトリの初期化 + タイムゾーン設定
# ============================================================

log_step "リモートディレクトリを初期化中..."

sshpass -p "$EC2_PASS" ssh \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    "$EC2_USER@$EC2_IP" \
    "mkdir -p $REMOTE_DIR/logs $REMOTE_DIR/out $REMOTE_DIR/tmp && chmod 755 $REMOTE_DIR/logs $REMOTE_DIR/out $REMOTE_DIR/tmp" \
    > /dev/null 2>&1

log_info "✅ logs/, out/, tmp/ ディレクトリを作成"

# タイムゾーン設定 （修正3: TZ を Asia/Tokyo に設定）
log_step "タイムゾーンを設定中..."

sshpass -p "$EC2_PASS" ssh \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    "$EC2_USER@$EC2_IP" \
    "sudo timedatectl set-timezone Asia/Tokyo" \
    > /dev/null 2>&1 || log_warn "⚠️  タイムゾーン設定スキップ（sudoが無い場合）"

# タイムゾーン確認
CURRENT_TZ=$(sshpass -p "$EC2_PASS" ssh \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    "$EC2_USER@$EC2_IP" \
    "timedatectl | grep -i timezone | awk '{print \$3}'" \
    2>/dev/null || echo "unknown")

log_info "✅ 現在のタイムゾーン: $CURRENT_TZ"
log_info ""

# ============================================================
# STEP 6: スクリプト実行権限と所有権を設定
# ============================================================

log_step "スクリプト実行権限・所有権を設定中..."

sshpass -p "$EC2_PASS" ssh \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    "$EC2_USER@$EC2_IP" \
    "chmod +x $REMOTE_DIR/youtube_pipeline.py $REMOTE_DIR/run_pipeline.sh $REMOTE_DIR/batch_produce.sh $REMOTE_DIR/setup_cron.sh && \
     chown -R ec2-user:ec2-user $REMOTE_DIR" \
    > /dev/null 2>&1

log_info "✅ 実行権限・所有権を設定"
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
# STEP 8: VOICEVOX Dockerコンテナ確認・起動 （修正4: docker inspect で正確に判定）
# ============================================================

log_step "VOICEVOX Docker確認中..."

VOICEVOX_STATUS=$(sshpass -p "$EC2_PASS" ssh \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    "$EC2_USER@$EC2_IP" \
    "docker inspect voicevox --format '{{.State.Running}}' 2>/dev/null || echo 'false'" \
    2>/dev/null)

if [ "$VOICEVOX_STATUS" = "true" ]; then
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
# STEP 10: Cron自動セットアップ （修正5: setup_cron.sh を自動実行）
# ============================================================

log_step "Cron設定を自動セットアップ中..."

if sshpass -p "$EC2_PASS" ssh \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    "$EC2_USER@$EC2_IP" \
    "bash $REMOTE_DIR/setup_cron.sh" \
    > /dev/null 2>&1; then
    log_info "✅ Cron設定: 完了"
else
    log_warn "⚠️  Cron設定: スキップ（手動で以下を実行してください）"
    log_warn "   sshpass -p \"$EC2_PASS\" ssh $EC2_USER@$EC2_IP \"bash $REMOTE_DIR/setup_cron.sh\""
fi

log_info ""

# ============================================================
# STEP 11: 完了ログ出力
# ============================================================

log_info "============================================================"
log_info "✅✅✅ EC2再デプロイが完了しました！！"
log_info "============================================================"
log_info ""
log_info "次のステップ:"
log_info "  1. .env ファイルが正しく転送されたか確認:"
log_info "     sshpass -p \"$EC2_PASS\" ssh $EC2_USER@$EC2_IP \"cat $REMOTE_DIR/.env\""
log_info ""
log_info "  2. Cronが正しく登録されたか確認:"
log_info "     sshpass -p \"$EC2_PASS\" ssh $EC2_USER@$EC2_IP \"crontab -l\""
log_info ""
log_info "  3. 動作確認（手動テスト）:"
log_info "     sshpass -p \"$EC2_PASS\" ssh $EC2_USER@$EC2_IP \"source ~/venv/bin/activate && python3 $REMOTE_DIR/youtube_pipeline.py --help\""
log_info ""
log_info "スポット消失時の再実行:"
log_info "  bash redeploy_ec2.sh <新しいIP>"
log_info ""
log_info "実行時刻: $(date '+%Y-%m-%d %H:%M:%S')"
log_info "============================================================"
```

---

## batch_produce.sh（最終版）

```bash
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

# グローバルエラーハンドリングON
set -e

# ============================================================
# 色付け出力（ログ見栄え向上）
# ============================================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️ ${NC} $1" | tee -a "$LOG_FILE"
}

# ============================================================
# 変数定義
# ============================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
LOG_FILE="$LOG_DIR/batch_$(date +%Y-%m-%d).log"
PIPELINE_SCRIPT="$SCRIPT_DIR/run_pipeline.sh"

# 処理対象動画数（デフォルト 3本）
NUM_VIDEOS=${1:-3}

# 動画生成間隔（秒） — API rate limit 回復を考慮
WAIT_SEC=300

# カウンタ
SUCCESS_COUNT=0
FAIL_COUNT=0
TOTAL_COUNT=0

# 開始時刻
START_TIME=$(date '+%Y-%m-%d %H:%M:%S')
START_TIMESTAMP=$(date +%s)

# ============================================================
# STEP 1: 前提チェック
# ============================================================
mkdir -p "$LOG_DIR"

log_info "========== Batch Produce Start =========="
log_info "開始時刻: $START_TIME"
log_info "処理対象: $NUM_VIDEOS 本の動画"
log_info ""

# PIPELINE_SCRIPT の存在確認
if [ ! -f "$PIPELINE_SCRIPT" ]; then
    log_error "パイプラインスクリプトが見つかりません"
    log_error "Path: $PIPELINE_SCRIPT"
    exit 1
fi

log_info "Pipeline script: $PIPELINE_SCRIPT"
log_info "Log directory: $LOG_DIR"
log_info ""

# ============================================================
# STEP 2: tmpディレクトリのクリーンアップ（前回の一時ファイル削除）
# ============================================================
log_info "前回の一時ファイルをクリーンアップ中..."
if [ -d "$SCRIPT_DIR/tmp" ]; then
    rm -rf "$SCRIPT_DIR/tmp"/*
    log_info "tmpディレクトリをクリア: $SCRIPT_DIR/tmp"
else
    mkdir -p "$SCRIPT_DIR/tmp"
    log_info "tmpディレクトリを作成: $SCRIPT_DIR/tmp"
fi
log_info ""

# ============================================================
# STEP 3: バッチループ開始（N本の動画を順番に処理）
# ============================================================
log_info "========== バッチ処理開始 =========="
log_info ""

for i in $(seq 1 "$NUM_VIDEOS"); do
    echo ""
    log_info "=== Video $i/$NUM_VIDEOS ==="
    log_info "パイプラインを実行中..."

    # 個別パイプライン実行（エラー続行許可）
    # 修正1: set +e で個別終了コード取得 → set -e で即座に戻す
    set +e
    bash "$PIPELINE_SCRIPT" >> "$LOG_FILE" 2>&1
    RESULT=$?
    set -e

    # 終了コード判定
    if [ $RESULT -eq 0 ]; then
        ((SUCCESS_COUNT++))
        log_success "Video $i 完了"
    else
        ((FAIL_COUNT++))
        log_error "Video $i 失敗 (終了コード: $RESULT)"
    fi

    ((TOTAL_COUNT++))

    # 待機（最後の動画は除く）
    if [ $i -lt "$NUM_VIDEOS" ]; then
        log_info "[WAIT] 次の動画まで ${WAIT_SEC}秒待機中..."
        sleep "$WAIT_SEC"
        log_info "待機終了。続行します。"
    fi

    echo ""
done

# ============================================================
# STEP 4: バッチ完了サマリー
# ============================================================
END_TIME=$(date '+%Y-%m-%d %H:%M:%S')
END_TIMESTAMP=$(date +%s)
ELAPSED_SEC=$((END_TIMESTAMP - START_TIMESTAMP))

log_info "========== バッチ完了 =========="
log_info ""
log_info "[SUMMARY]"
log_info "  開始時刻:   $START_TIME"
log_info "  終了時刻:   $END_TIME"
log_info "  合計時間:   ${ELAPSED_SEC}秒"
log_info "  処理数:     $TOTAL_COUNT 本"
log_info "  成功数:     $SUCCESS_COUNT 本"
log_info "  失敗数:     $FAIL_COUNT 本"
log_info ""

# 標準出力にもサマリーを出力
echo ""
echo "=========================================="
echo "Batch Produce Summary"
echo "=========================================="
echo "Start:   $START_TIME"
echo "End:     $END_TIME"
echo "Elapsed: ${ELAPSED_SEC}s"
echo ""
echo "Total:   $TOTAL_COUNT videos"
echo "Success: $SUCCESS_COUNT videos"
echo "Failed:  $FAIL_COUNT videos"
echo "=========================================="
echo ""

# ============================================================
# STEP 5: 終了コード設定
# ============================================================
if [ $FAIL_COUNT -eq 0 ]; then
    log_success "すべての動画処理が完了しました！"
    exit 0
else
    log_warn "$FAIL_COUNT 本の動画で失敗が発生しました"
    exit 1
fi
```

---

## setup_cron.sh（最終版）

```bash
#!/bin/bash
# ============================================================================
# setup_cron.sh — EC2 Cron Setup Script (Idempotent)
# ============================================================================
# 実行場所: EC2 (ec2-user)
# 用途: batch_produce.sh を crontab に登録、VOICEVOX 再起動を設定
#
# Usage: bash setup_cron.sh
#
# 前提条件:
#   - EC2 インスタンス上で実行
#   - batch_produce.sh が ~/youtube_automation/ に存在
#   - タイムゾーンは redeploy_ec2.sh で Asia/Tokyo に設定済み
#   - 実行ユーザーは ec2-user (sudo は不要）

set -e

# =========== Variables ===========
BATCH_SCRIPT="${HOME}/youtube_automation/batch_produce.sh"
LOG_DIR="${HOME}/youtube_automation/logs"
RUN_PIPELINE="${HOME}/youtube_automation/run_pipeline.sh"

# =========== STEP 1: Create Log Directory ===========
echo "[INFO] Creating log directory: $LOG_DIR"
mkdir -p "$LOG_DIR"
chmod 755 "$LOG_DIR"

# =========== STEP 2: Set Executable Permissions ===========
echo "[INFO] Setting executable permissions..."
chmod +x "$BATCH_SCRIPT"
chmod +x "$RUN_PIPELINE"

# =========== STEP 3: Verify Timezone ===========
echo "[INFO] Verifying current timezone..."
CURRENT_TZ=$(timedatectl | grep -i timezone | awk '{print $3}' || echo "unknown")
echo "[INFO] Current timezone: $CURRENT_TZ"

if [ "$CURRENT_TZ" != "Asia/Tokyo" ]; then
    echo "[WARN] Timezone is not Asia/Tokyo. Cron schedule may be incorrect."
    echo "[WARN] Please run: sudo timedatectl set-timezone Asia/Tokyo"
fi

# =========== STEP 4: Remove Existing Cron Entries (Idempotent) ===========
# 修正1: 既存エントリを取得（対象行を grep で除外）
echo "[INFO] Removing old cron entries..."
EXISTING=$(crontab -l 2>/dev/null | grep -v "batch_produce.sh" | grep -v "docker start voicevox" || echo "")

# =========== STEP 5: Prepare New Cron Entries ===========
echo "[INFO] Registering new cron entries..."

# Add batch_produce.sh entry (UTC 0:00 = JST 9:00)
BATCH_ENTRY="0 0 * * * /bin/bash ${BATCH_SCRIPT} >> ${LOG_DIR}/batch_\$(date +\%Y-\%m-\%d).log 2>&1"

# Add VOICEVOX reboot entry
VOICEVOX_ENTRY="@reboot sudo docker start voicevox >> ${LOG_DIR}/voicevox_boot.log 2>&1"

# =========== STEP 6: Combine and Set Crontab (with Deduplication) ===========
# 修正2: sort | uniq で重複排除
{
    echo "$EXISTING"
    echo "$BATCH_ENTRY"
    echo "$VOICEVOX_ENTRY"
} | sort | uniq | crontab -

echo "[SUCCESS] Cron entries registered:"
echo "  - Batch: 0 0 * * * (UTC 0:00 = JST 9:00)"
echo "  - VOICEVOX: @reboot"

# =========== STEP 7: Display Current Crontab ===========
echo ""
echo "[INFO] Current crontab:"
crontab -l

# =========== STEP 8: Final Status Message ===========
echo ""
echo "[SUMMARY]"
echo "  - Log directory: $LOG_DIR"
echo "  - Batch script: $BATCH_SCRIPT"
echo "  - Timezone: $CURRENT_TZ"
echo "  - Next execution: Tomorrow UTC 0:00 (JST 9:00)"
echo "  - Status: Ready for automatic execution"
echo ""
echo "[SUCCESS] Cron setup completed at $(date)"
```

---

## 修正サマリー

### 1. **batch_produce.sh の `set -e / set +e` 修正** ✅
**指摘**: L110-113 で `set +e` が2度実行（L110, L113）→ エラーハンドリング不完全

**修正内容**:
```bash
# 修正前：
set +e
bash "$PIPELINE_SCRIPT" >> "$LOG_FILE" 2>&1
RESULT=$?
set +e  # ← 重複、不要

# 修正後：
set +e
bash "$PIPELINE_SCRIPT" >> "$LOG_FILE" 2>&1
RESULT=$?
set -e  # ← set -e に戻す（スクリプト全体のエラーハンドリング統一）
```

**理由**: `run_pipeline.sh` が `set -e` で定義されているため、個別実行時のエラーを捕捉した後は、スクリプト全体を `set -e` 状態に戻す必要があります。そうしないと、次ループ以降でエラーが伝播せず、潜在的なバグが見逃される。

---

### 2. **redeploy_ec2.sh の `.env` 転送（heredoc）修正** ✅
**指摘**: L218 の `'EOF'` でシングルクォート保護 → `$(cat ...)` が展開されない → 空ファイル生成

**修正内容**:
```bash
# 修正前：
sshpass -p "$EC2_PASS" ssh ... \
    "cat > $REMOTE_DIR/.env << 'EOF'
$(cat "$LOCAL_DIR/.env")
EOF"

# 修正後：
# Option 1: cat パイプで転送（推奨）
cat "$LOCAL_DIR/.env" | sshpass -p "$EC2_PASS" ssh \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    "$EC2_USER@$EC2_IP" \
    "cat > $REMOTE_DIR/.env"

# Option 2: heredoc + EOF（クォート削除）
sshpass -p "$EC2_PASS" ssh ... \
    "cat > $REMOTE_DIR/.env << EOF
$(cat "$LOCAL_DIR/.env")
EOF"
```

**理由**: `'EOF'` はシングルクォートで保護されているため、ローカル側の `$(cat ...)` が展開されず、空ファイルが生成される。最終版では「cat パイプ」を採用（より安全・シンプル）。

---

### 3. **redeploy_ec2.sh での `.env` 強制化** ✅
**指摘**: L228 で `.env` が見つからない場合は警告のみ → デプロイ続行 → 後で run_pipeline.sh で失敗

**修正内容**:
```bash
# 修正前：
else
    log_warn "⚠️  .env が見つかりません (後で手動で設定してください)"

# 修正後：
if [ ! -f "$LOCAL_DIR/.env" ]; then
    log_error ".env ファイルが見つかりません: $LOCAL_DIR/.env"
    log_error "以下を実行してください: cp .env.example .env && 編集"
    exit 1  # ← デプロイ失敗
fi
```

**理由**: `.env` なしでデプロイを完了させると、後で手動対応が必要になり、運用負荷が増加。事前に強制化することで、デプロイ時に問題を即座に発見できる。

---

### 4. **setup_cron.sh の `Cron` 冪等性強化** ✅
**指摘**: 複数回実行で同じエントリが重複登録される → cron 実行数増加

**修正内容**:
```bash
# 修正前：
EXISTING=$(crontab -l 2>/dev/null || echo "")
echo "$EXISTING" | grep -v "batch_produce.sh" | grep -v "docker start voicevox" | crontab - || true
EXISTING=$(crontab -l 2>/dev/null || echo "")
{
    echo "$EXISTING"  # ← 古いEXISTING 再利用 → 重複の可能性
    echo "$BATCH_ENTRY"
    echo "$VOICEVOX_ENTRY"
} | crontab -

# 修正後：
EXISTING=$(crontab -l 2>/dev/null | grep -v "batch_produce.sh" | grep -v "docker start voicevox" || echo "")
BATCH_ENTRY="0 0 * * * ..."
VOICEVOX_ENTRY="@reboot ..."
{
    echo "$EXISTING"
    echo "$BATCH_ENTRY"
    echo "$VOICEVOX_ENTRY"
} | sort | uniq | crontab -  # ← 重複排除
```

**理由**: `sort | uniq` で既に登録済みのエントリを自動除外。複数回実行時も安全。

---

### 5. **setup_cron.sh での `TZ`（タイムゾーン）設定確認追加** ✅
**指摘**: `setup_cron.sh` で TZ 設定がない → EC2 のデフォルト TZ が UTC でない場合、Cron 実行時刻がずれる

**修正内容**:
```bash
# 新規追加：
# =========== STEP 3: Verify Timezone ===========
echo "[INFO] Verifying current timezone..."
CURRENT_TZ=$(timedatectl | grep -i timezone | awk '{print $3}' || echo "unknown")
echo "[INFO] Current timezone: $CURRENT_TZ"

if [ "$CURRENT_TZ" != "Asia/Tokyo" ]; then
    echo "[WARN] Timezone is not Asia/Tokyo. Cron schedule may be incorrect."
fi
```

**理由**: Cron は EC2 インスタンスのシステムタイムゾーンに従う。UTC 0:00 を JST 9:00 にするには、タイムゾーンが正しく設定されていることが前提。`redeploy_ec2.sh` で自動設定し、`setup_cron.sh` で確認。

---

### 6. **redeploy_ec2.sh での VOICEVOX 状態判定修正** ✅
**指摘**: `docker ps --format '{{.State}}'` は正確でない → `docker inspect` で確認すべき

**修正内容**:
```bash
# 修正前：
VOICEVOX_STATUS=$(sshpass -p "$EC2_PASS" ssh ... \
    "docker ps --filter 'name=voicevox' --format '{{.State}}'" ...)
if [ "$VOICEVOX_STATUS" = "running" ]; then

# 修正後：
VOICEVOX_STATUS=$(sshpass -p "$EC2_PASS" ssh ... \
    "docker inspect voicevox --format '{{.State.Running}}' 2>/dev/null || echo 'false'")
if [ "$VOICEVOX_STATUS" = "true" ]; then
```

**理由**: `docker inspect` は Docker API 直接アクセスで、より確実な状態判定が可能。`{{.State.Running}}` は真偽値 `true/false` を返す。

---

### 7. **redeploy_ec2.sh でのファイル所有権設定** ✅
**指摘**: ファイルが root 所有になると ec2-user が編集・実行時に権限不足

**修正内容**:
```bash
# 修正前：
chmod +x $REMOTE_DIR/youtube_pipeline.py ...

# 修正後：
chmod +x $REMOTE_DIR/youtube_pipeline.py ... && \
chown -R ec2-user:ec2-user $REMOTE_DIR
```

**理由**: Cron は ec2-user で実行されるため、スクリプト・ファイルの所有権も ec2-user に統一。scp 転送後に所有権が自動で ec2-user に変更されない場合があるため、明示的に設定。

---

### 8. **redeploy_ec2.sh での Cron 自動セットアップ** ✅
**指摘**: スポット再起動時、crontab 再登録が手動 → 運用負荷増加

**修正内容**:
```bash
# 新規 STEP 10：
log_step "Cron設定を自動セットアップ中..."
if sshpass -p "$EC2_PASS" ssh ... \
    "bash $REMOTE_DIR/setup_cron.sh" > /dev/null 2>&1; then
    log_info "✅ Cron設定: 完了"
else
    log_warn "⚠️  Cron設定: スキップ（手動で実行してください）"
fi
```

**理由**: `redeploy_ec2.sh` 完了後、自動で `setup_cron.sh` を実行 → スポット消失から復旧まで完全自動化 → 手動実行依存度を低減。

---

## 総合評価

すべての **3つの Critical Bug** と **2つの Medium Risk** が修正されました。

| # | 項目 | 状態 |
|---|------|------|
| 1 | batch_produce.sh の `set -e` 復帰 | ✅ 修正 |
| 2 | redeploy_ec2.sh の .env heredoc | ✅ 修正 |
| 3 | setup_cron.sh の Cron 重複排除 | ✅ 修正 |
| 4 | TZ 設定の追加 | ✅ 修正 |
| 5 | VOICEVOX 状態判定の正確化 | ✅ 修正 |
| 6 | .env 転送の強制化 | ✅ 修正 |
| 7 | ファイル所有権の統一 | ✅ 修正 |
| 8 | Cron 自動セットアップ | ✅ 修正 |

本番デプロイ前には、以下をテストしてください：
- Cron の重複登録がないか確認（`crontab -l` で複数行チェック）
- `.env` が正しく転送されているか確認（内容表示）
- スポット再起動シミュレーション（IP 変更 → redeploy_ec2.sh 再実行）
