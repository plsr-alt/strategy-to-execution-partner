#!/bin/bash
# ============================================================================
# setup_cron.sh — EC2 Cron Setup Script (Idempotent)
# ============================================================================
# Usage: bash setup_cron.sh
# Description: Register batch_produce.sh to crontab (JST 9:00), setup VOICEVOX
#              autostart on reboot, and configure system timezone.
# Environment: Run on EC2 (ec2-user or root)
# ============================================================================

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

# =========== STEP 3: Remove Existing Cron Entries (Idempotent) ===========
echo "[INFO] Removing old cron entries..."
EXISTING=$(crontab -l 2>/dev/null || echo "")
echo "$EXISTING" | grep -v "batch_produce.sh" | grep -v "docker start voicevox" | crontab - 2>/dev/null || true

# =========== STEP 4: Register New Cron Entries ===========
echo "[INFO] Registering new cron entries..."

# Get current crontab (might be empty)
EXISTING=$(crontab -l 2>/dev/null || echo "")

# Add batch_produce.sh entry (UTC 0:00 = JST 9:00)
BATCH_ENTRY="0 0 * * * /bin/bash ${BATCH_SCRIPT} >> ${LOG_DIR}/batch_\$(date +\%Y-\%m-\%d).log 2>&1"

# Add VOICEVOX reboot entry
VOICEVOX_ENTRY="@reboot sudo docker start voicevox >> ${LOG_DIR}/voicevox_boot.log 2>&1"

# Combine and set crontab
{
    echo "$EXISTING"
    echo "$BATCH_ENTRY"
    echo "$VOICEVOX_ENTRY"
} | crontab -

echo "[SUCCESS] Cron entries registered:"
echo "  - Batch: 0 0 * * * (UTC 0:00 = JST 9:00)"
echo "  - VOICEVOX: @reboot"

# =========== STEP 5: Display Current Crontab ===========
echo ""
echo "[INFO] Current crontab:"
crontab -l

# =========== STEP 6: Final Status Message ===========
echo ""
echo "[SUMMARY]"
echo "  - Log directory: $LOG_DIR"
echo "  - Batch script: $BATCH_SCRIPT"
echo "  - Next execution: Tomorrow UTC 0:00 (JST 9:00)"
echo "  - Status: Ready for automatic execution"
echo ""
echo "[SUCCESS] Cron setup completed at $(date)"
