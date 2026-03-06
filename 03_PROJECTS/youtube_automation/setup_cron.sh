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

set -e

# Variables
BATCH_SCRIPT="${HOME}/youtube_automation/batch_produce.sh"
LOG_DIR="${HOME}/youtube_automation/logs"
RUN_PIPELINE="${HOME}/youtube_automation/run_pipeline.sh"

# STEP 1: Create Log Directory
echo "[INFO] Creating log directory: $LOG_DIR"
mkdir -p "$LOG_DIR"
chmod 755 "$LOG_DIR"

# STEP 2: Set Executable Permissions
echo "[INFO] Setting executable permissions..."
chmod +x "$BATCH_SCRIPT"
chmod +x "$RUN_PIPELINE"

# STEP 3: Verify Timezone
echo "[INFO] Verifying current timezone..."
CURRENT_TZ=$(timedatectl | grep -i timezone | awk '{print $3}' || echo "unknown")
echo "[INFO] Current timezone: $CURRENT_TZ"

if [ "$CURRENT_TZ" != "Asia/Tokyo" ]; then
    echo "[WARN] Timezone is not Asia/Tokyo. Cron schedule may be incorrect."
    echo "[WARN] Please run: sudo timedatectl set-timezone Asia/Tokyo"
fi

# STEP 4: Remove Existing Cron Entries (Idempotent)
echo "[INFO] Removing old cron entries..."
EXISTING=$(crontab -l 2>/dev/null | grep -v "batch_produce.sh" | grep -v "docker start voicevox" || echo "")

# STEP 5: Prepare New Cron Entries
echo "[INFO] Registering new cron entries..."

# JST 9:00 = TZ Asia/Tokyo設定済みなので 9 0 * * * で直接指定
BATCH_ENTRY="0 9 * * * /bin/bash ${BATCH_SCRIPT} >> ${LOG_DIR}/batch_\$(date +\%Y-\%m-\%d).log 2>&1"
VOICEVOX_ENTRY="@reboot sudo docker start voicevox >> ${LOG_DIR}/voicevox_boot.log 2>&1"

# STEP 6: Combine and Set Crontab (with Deduplication)
{
    echo "$EXISTING"
    echo "$BATCH_ENTRY"
    echo "$VOICEVOX_ENTRY"
} | grep -v '^$' | sort | uniq | crontab -

echo "[SUCCESS] Cron entries registered:"
echo "  - Batch: 0 9 * * * (JST 9:00)"
echo "  - VOICEVOX: @reboot"

# STEP 7: Display Current Crontab
echo ""
echo "[INFO] Current crontab:"
crontab -l

# STEP 8: Final Status
echo ""
echo "[SUMMARY]"
echo "  - Log directory: $LOG_DIR"
echo "  - Batch script: $BATCH_SCRIPT"
echo "  - Timezone: $CURRENT_TZ"
echo "  - Next execution: Tomorrow JST 9:00"
echo "  - Status: Ready for automatic execution"
echo ""
echo "[SUCCESS] Cron setup completed at $(date)"
