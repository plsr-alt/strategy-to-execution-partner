#!/bin/bash
# =============================================================================
# AI Image Generation GPU Environment Setup
# Run on: Amazon Linux 2023, g6.xlarge (NVIDIA L4, 24GB VRAM)
# Usage:  sudo bash setup_gpu_env.sh
#
# Idempotent: safe to run multiple times.
# Each section checks before installing to avoid redundant work.
# =============================================================================

set -euo pipefail

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------
VENV_DIR="/home/ec2-user/ai-image-env"
MODEL_DIR_FLUX="/home/ec2-user/models/flux2-klein"
MODEL_DIR_WAN="/home/ec2-user/models/wan22-t2v-1.3b"
SCRIPTS_DIR="/home/ec2-user"
LOG_FILE="/var/log/setup_gpu_env.log"
PYTHON_VERSION="3.11"
CUDA_VERSION="12.4"  # matches torch cu124 wheel (L4 supports newer CUDA)

# Track what we actually installed for the summary
INSTALLED_ITEMS=()

# -----------------------------------------------------------------------------
# Logging helper
# -----------------------------------------------------------------------------
log() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $*"
    echo "$msg" | tee -a "$LOG_FILE"
}

log_section() {
    echo "" | tee -a "$LOG_FILE"
    echo "============================================================" | tee -a "$LOG_FILE"
    log "SECTION: $*"
    echo "============================================================" | tee -a "$LOG_FILE"
}

mark_installed() {
    INSTALLED_ITEMS+=("$1")
}

# -----------------------------------------------------------------------------
# Error handler
# -----------------------------------------------------------------------------
on_error() {
    local exit_code=$?
    local line_no=$1
    log "ERROR: command failed at line ${line_no} (exit code ${exit_code})"
    log "Check $LOG_FILE for details."
    exit "$exit_code"
}
trap 'on_error $LINENO' ERR

# -----------------------------------------------------------------------------
# Ensure running as root
# -----------------------------------------------------------------------------
if [[ $EUID -ne 0 ]]; then
    echo "ERROR: This script must be run as root. Use: sudo bash $0"
    exit 1
fi

log "Setup started. All output is also logged to $LOG_FILE"


# =============================================================================
# 1. System Updates
# =============================================================================
log_section "1. System Updates"

log "Updating system packages..."
dnf update -y 2>&1 | tee -a "$LOG_FILE"
dnf install -y \
    git \
    wget \
    curl \
    tar \
    unzip \
    gcc \
    gcc-c++ \
    make \
    kernel-headers \
    kernel-devel \
    dkms \
    pciutils \
    2>&1 | tee -a "$LOG_FILE"

log "System update complete."
mark_installed "System packages (git, gcc, wget, curl, kernel-devel, dkms)"


# =============================================================================
# 2. NVIDIA Driver + CUDA
# =============================================================================
log_section "2. NVIDIA Driver + CUDA"

# Check if NVIDIA driver is already installed
if nvidia-smi &>/dev/null; then
    log "NVIDIA driver already installed. Skipping."
    nvidia-smi | tee -a "$LOG_FILE"
else
    log "Installing NVIDIA driver via amazon-linux-extras / dnf..."

    # Amazon Linux 2023 provides NVIDIA drivers through the OS repo
    # Enable the GPU driver repository
    dnf config-manager --add-repo \
        https://developer.download.nvidia.com/compute/cuda/repos/rhel9/x86_64/cuda-rhel9.repo \
        2>&1 | tee -a "$LOG_FILE"

    dnf clean expire-cache 2>&1 | tee -a "$LOG_FILE"

    # Install CUDA toolkit 12.x (pulls in matching NVIDIA driver)
    log "Installing CUDA ${CUDA_VERSION} toolkit (this may take several minutes)..."
    dnf install -y \
        cuda-toolkit-12-4 \
        nvidia-driver \
        nvidia-driver-cuda \
        2>&1 | tee -a "$LOG_FILE"

    # Load kernel module without reboot (best-effort; reboot may still be needed)
    modprobe nvidia 2>/dev/null || log "Note: nvidia module load failed — a reboot may be required before nvidia-smi works."

    mark_installed "NVIDIA driver + CUDA ${CUDA_VERSION}"
fi

# Set CUDA on PATH for subsequent commands in this script
if [[ -d "/usr/local/cuda/bin" ]]; then
    export PATH="/usr/local/cuda/bin:$PATH"
    export LD_LIBRARY_PATH="/usr/local/cuda/lib64:${LD_LIBRARY_PATH:-}"
fi

# Verify nvidia-smi (non-fatal — driver may need reboot)
log "Verifying nvidia-smi..."
if nvidia-smi 2>&1 | tee -a "$LOG_FILE"; then
    log "GPU verified OK."
else
    log "WARNING: nvidia-smi not yet available. If this is a fresh driver install, reboot and re-run from step 3."
fi


# =============================================================================
# 3. Python 3.11 Environment
# =============================================================================
log_section "3. Python ${PYTHON_VERSION} Environment"

# Install Python 3.11 if not present
if python3.11 --version &>/dev/null; then
    log "Python 3.11 already installed: $(python3.11 --version)"
else
    log "Installing Python ${PYTHON_VERSION}..."
    dnf install -y python3.11 python3.11-pip python3.11-devel 2>&1 | tee -a "$LOG_FILE"
    mark_installed "Python ${PYTHON_VERSION}"
fi

# Create virtualenv
if [[ -d "$VENV_DIR" ]]; then
    log "Virtualenv already exists at $VENV_DIR. Skipping creation."
else
    log "Creating virtualenv at $VENV_DIR ..."
    python3.11 -m venv "$VENV_DIR" 2>&1 | tee -a "$LOG_FILE"
    chown -R ec2-user:ec2-user "$VENV_DIR"
    mark_installed "Python virtualenv at $VENV_DIR"
fi

# Activate for the rest of this script
# shellcheck disable=SC1090
source "${VENV_DIR}/bin/activate"

# Upgrade pip inside venv
log "Upgrading pip..."
pip install --upgrade pip setuptools wheel 2>&1 | tee -a "$LOG_FILE"

log "Python environment ready: $(python --version)"


# =============================================================================
# 4. Python Packages
# =============================================================================
log_section "4. Python Packages"

# PyTorch with CUDA 12.4
if python -c "import torch; assert torch.cuda.is_available()" &>/dev/null; then
    log "PyTorch with CUDA already installed and verified."
else
    log "Installing PyTorch with CUDA ${CUDA_VERSION} support..."
    pip install \
        torch torchvision torchaudio \
        --index-url https://download.pytorch.org/whl/cu124 \
        2>&1 | tee -a "$LOG_FILE"
    mark_installed "PyTorch (cu124)"
fi

# HuggingFace / Diffusers stack
log "Installing HuggingFace / Diffusers stack..."
pip install \
    "diffusers>=0.32.0" \
    transformers \
    accelerate \
    safetensors \
    huggingface_hub \
    sentencepiece \
    2>&1 | tee -a "$LOG_FILE"
mark_installed "diffusers>=0.32.0, transformers, accelerate, safetensors, huggingface_hub"

# Wan 2.2 dependencies (image-to-video)
log "Installing Wan 2.2 dependencies..."
pip install \
    imageio \
    imageio-ffmpeg \
    einops \
    2>&1 | tee -a "$LOG_FILE"
mark_installed "wan2.2 deps (imageio, imageio-ffmpeg, einops)"

# AWS / Image / Video
log "Installing AWS + image/video packages..."
pip install \
    boto3 \
    awscli \
    Pillow \
    opencv-python-headless \
    moviepy \
    2>&1 | tee -a "$LOG_FILE"
mark_installed "boto3, awscli, Pillow, opencv-python-headless, moviepy"

# Verify PyTorch + CUDA
log "Verifying PyTorch CUDA availability..."
python - <<'PYCHECK'
import torch
print(f"PyTorch version : {torch.__version__}")
print(f"CUDA available  : {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA version    : {torch.version.cuda}")
    print(f"GPU device      : {torch.cuda.get_device_name(0)}")
    print(f"VRAM            : {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
else:
    print("WARNING: CUDA not available — check NVIDIA driver install.")
PYCHECK
log "PyTorch verification done."


# =============================================================================
# 5. Download Models (FLUX.2 klein + Wan 2.2)
# =============================================================================
log_section "5. Download Models"

# Retrieve HuggingFace token from SSM Parameter Store (non-fatal if not set)
HF_TOKEN=""
if command -v aws &>/dev/null; then
    log "Attempting to fetch HuggingFace token from SSM Parameter Store..."
    HF_TOKEN=$(aws ssm get-parameter \
        --name "/ai-image-gen/huggingface-token" \
        --with-decryption \
        --query "Parameter.Value" \
        --output text 2>/dev/null || echo "")
fi

if [[ -z "$HF_TOKEN" ]]; then
    log "WARNING: HuggingFace token not found in SSM (/ai-image-gen/huggingface-token)."
    log "         Both FLUX.2-klein and Wan2.2 are Apache 2.0 and do NOT require a token."
    log "         Token is only needed if you later use gated models (FLUX.1-dev etc.)."
fi

if [[ -n "$HF_TOKEN" ]]; then
    HF_TOKEN_ARG="--token ${HF_TOKEN}"
else
    HF_TOKEN_ARG=""
fi

# --- 5a. FLUX.2 [klein] 4B (primary image generation, ~8 GB) ---
if [[ -d "${MODEL_DIR_FLUX}" && -n "$(ls -A "${MODEL_DIR_FLUX}" 2>/dev/null)" ]]; then
    log "FLUX.2-klein directory already populated: ${MODEL_DIR_FLUX}. Skipping download."
else
    log "Creating model directory: ${MODEL_DIR_FLUX}"
    mkdir -p "${MODEL_DIR_FLUX}"
    chown -R ec2-user:ec2-user "$(dirname "${MODEL_DIR_FLUX}")"

    log "Downloading black-forest-labs/FLUX.2-klein (~8 GB). This will take 5-15 minutes..."

    # FLUX.2-klein is Apache 2.0, no token required
    # shellcheck disable=SC2086
    sudo -u ec2-user \
        "${VENV_DIR}/bin/huggingface-cli" download \
        black-forest-labs/FLUX.2-klein \
        --local-dir "${MODEL_DIR_FLUX}" \
        --local-dir-use-symlinks False \
        ${HF_TOKEN_ARG} \
        2>&1 | tee -a "$LOG_FILE"

    log "FLUX.2-klein download complete. Checking size..."
    du -sh "${MODEL_DIR_FLUX}" | tee -a "$LOG_FILE"
    mark_installed "FLUX.2-klein model at ${MODEL_DIR_FLUX}"
fi

# --- 5b. Wan 2.2 T2V 1.3B (image-to-video, ~5 GB) ---
if [[ -d "${MODEL_DIR_WAN}" && -n "$(ls -A "${MODEL_DIR_WAN}" 2>/dev/null)" ]]; then
    log "Wan2.2-T2V-1.3B directory already populated: ${MODEL_DIR_WAN}. Skipping download."
else
    log "Creating model directory: ${MODEL_DIR_WAN}"
    mkdir -p "${MODEL_DIR_WAN}"
    chown -R ec2-user:ec2-user "$(dirname "${MODEL_DIR_WAN}")"

    log "Downloading Wan-AI/Wan2.2-T2V-1.3B (~5 GB). This will take 5-10 minutes..."

    # Wan 2.2 is Apache 2.0, no token required
    # shellcheck disable=SC2086
    sudo -u ec2-user \
        "${VENV_DIR}/bin/huggingface-cli" download \
        Wan-AI/Wan2.2-T2V-1.3B \
        --local-dir "${MODEL_DIR_WAN}" \
        --local-dir-use-symlinks False \
        ${HF_TOKEN_ARG} \
        2>&1 | tee -a "$LOG_FILE"

    log "Wan2.2-T2V-1.3B download complete. Checking size..."
    du -sh "${MODEL_DIR_WAN}" | tee -a "$LOG_FILE"
    mark_installed "Wan2.2-T2V-1.3B model at ${MODEL_DIR_WAN}"
fi

# --- 5c. Z-Image-Turbo (optional — uncomment to enable) ---
# MODEL_DIR_ZTURBO="/home/ec2-user/models/z-image-turbo"
# if [[ -d "${MODEL_DIR_ZTURBO}" && -n "$(ls -A "${MODEL_DIR_ZTURBO}" 2>/dev/null)" ]]; then
#     log "Z-Image-Turbo directory already populated. Skipping."
# else
#     log "Downloading Z-Image-Turbo..."
#     mkdir -p "${MODEL_DIR_ZTURBO}"
#     chown -R ec2-user:ec2-user "$(dirname "${MODEL_DIR_ZTURBO}")"
#     # shellcheck disable=SC2086
#     sudo -u ec2-user \
#         "${VENV_DIR}/bin/huggingface-cli" download \
#         Z-Image-Turbo \
#         --local-dir "${MODEL_DIR_ZTURBO}" \
#         --local-dir-use-symlinks False \
#         ${HF_TOKEN_ARG} \
#         2>&1 | tee -a "$LOG_FILE"
#     mark_installed "Z-Image-Turbo model at ${MODEL_DIR_ZTURBO}"
# fi


# =============================================================================
# 6. Create startup.sh
# =============================================================================
log_section "6. Create startup.sh"

STARTUP_SCRIPT="${SCRIPTS_DIR}/startup.sh"

if [[ -f "$STARTUP_SCRIPT" ]]; then
    log "startup.sh already exists. Overwriting with latest version..."
fi

cat > "$STARTUP_SCRIPT" << 'STARTUP_HEREDOC'
#!/bin/bash
# =============================================================================
# startup.sh — Runs on every boot of the g6.xlarge instance
#
# Flow:
#   1. Activate virtualenv
#   2. Schedule auto-shutdown (safety: 90 minutes)
#   3. Check S3 for pending prompts
#   4. Run image generation if prompts exist
# =============================================================================

set -euo pipefail

VENV_DIR="/home/ec2-user/ai-image-env"
GENERATE_SCRIPT="/home/ec2-user/generate_images.py"
STARTUP_LOG="/var/log/startup_run.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$STARTUP_LOG"
}

log "===== startup.sh begin ====="

# ------------------------------------------------------------------
# 1. Activate virtualenv
# ------------------------------------------------------------------
log "Activating virtualenv: $VENV_DIR"
# shellcheck disable=SC1090
source "${VENV_DIR}/bin/activate"
log "Python: $(python --version)"

# ------------------------------------------------------------------
# 2. Schedule auto-shutdown — 90 minutes from now (safety mechanism)
#    This runs regardless of generation success/failure.
# ------------------------------------------------------------------
log "Scheduling auto-shutdown in 90 minutes (safety)..."
sudo shutdown -h +90 &
SHUTDOWN_PID=$!
log "Shutdown PID: $SHUTDOWN_PID (cancel with: sudo shutdown -c)"

# ------------------------------------------------------------------
# 3. Check S3 for pending prompts
# ------------------------------------------------------------------
log "Checking S3 for pending prompts..."

# Retrieve bucket name from SSM (fallback: environment variable)
if [[ -z "${S3_BUCKET:-}" ]]; then
    S3_BUCKET=$(aws ssm get-parameter \
        --name "/ai-image-gen/s3-bucket" \
        --query "Parameter.Value" \
        --output text 2>/dev/null || echo "")
fi

if [[ -z "${S3_BUCKET:-}" ]]; then
    log "WARNING: S3_BUCKET not set and not found in SSM (/ai-image-gen/s3-bucket)."
    log "         Set environment variable S3_BUCKET or store in SSM and retry."
    log "===== startup.sh end (no S3 bucket) ====="
    exit 0
fi

PENDING_CHECK=$(aws s3 ls "s3://${S3_BUCKET}/prompts/pending.json" 2>/dev/null || echo "")

if [[ -z "$PENDING_CHECK" ]]; then
    log "No pending prompts found at s3://${S3_BUCKET}/prompts/pending.json"
    log "Nothing to generate. Instance will shut down in ~90 minutes."
    log "===== startup.sh end (no prompts) ====="
    exit 0
fi

log "Pending prompts found. Starting generation..."

# ------------------------------------------------------------------
# 4. Run image generation
# ------------------------------------------------------------------
if [[ ! -f "$GENERATE_SCRIPT" ]]; then
    log "ERROR: $GENERATE_SCRIPT not found. Cannot run generation."
    log "===== startup.sh end (script missing) ====="
    exit 1
fi

log "Running: python $GENERATE_SCRIPT --from-s3"
python "$GENERATE_SCRIPT" --from-s3 2>&1 | tee -a "$STARTUP_LOG"

GENERATE_EXIT=${PIPESTATUS[0]}
if [[ $GENERATE_EXIT -eq 0 ]]; then
    log "Generation completed successfully."
else
    log "WARNING: Generation exited with code $GENERATE_EXIT. Check log for details."
fi

log "===== startup.sh end ====="
STARTUP_HEREDOC

chmod +x "$STARTUP_SCRIPT"
chown ec2-user:ec2-user "$STARTUP_SCRIPT"
log "startup.sh written to $STARTUP_SCRIPT"
mark_installed "startup.sh at $STARTUP_SCRIPT"


# =============================================================================
# 7. Systemd Service (auto-run on boot)
# =============================================================================
log_section "7. Systemd Service"

SERVICE_FILE="/etc/systemd/system/ai-image-startup.service"

if [[ -f "$SERVICE_FILE" ]]; then
    log "Systemd service already exists. Overwriting..."
fi

cat > "$SERVICE_FILE" << 'SERVICE_HEREDOC'
[Unit]
Description=AI Image Generation Startup Service
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User=root
ExecStart=/bin/bash /home/ec2-user/startup.sh
StandardOutput=append:/var/log/startup_run.log
StandardError=append:/var/log/startup_run.log
RemainAfterExit=yes
# Give the script up to 2 hours to complete before systemd times out
TimeoutStartSec=7200

[Install]
WantedBy=multi-user.target
SERVICE_HEREDOC

systemctl daemon-reload
systemctl enable ai-image-startup.service 2>&1 | tee -a "$LOG_FILE"
log "Systemd service registered and enabled: ai-image-startup.service"
mark_installed "systemd service: ai-image-startup.service (enabled on boot)"


# =============================================================================
# 8. Verification — Test Generation (1 image)
# =============================================================================
log_section "8. Verification — Test Image Generation"

TEST_OUTPUT="/tmp/test_flux2_output.png"
TEST_SCRIPT="/tmp/test_flux2.py"

cat > "$TEST_SCRIPT" << 'PYTEST_HEREDOC'
"""
Quick smoke test: generate 1 image with FLUX.2 [klein] 4B.
Uses the local model if available; falls back to HuggingFace Hub (requires internet).
"""
import sys
import os
import time

MODEL_DIR = "/home/ec2-user/models/flux2-klein"
OUTPUT_PATH = "/tmp/test_flux2_output.png"

print(f"[test] Python: {sys.version}")

import torch
print(f"[test] PyTorch: {torch.__version__}")
print(f"[test] CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"[test] GPU: {torch.cuda.get_device_name(0)}")
    vram_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
    print(f"[test] VRAM: {vram_gb:.1f} GB")

from diffusers import FluxPipeline

# Determine model source
if os.path.isdir(MODEL_DIR) and os.listdir(MODEL_DIR):
    model_source = MODEL_DIR
    print(f"[test] Loading model from local path: {model_source}")
else:
    model_source = "black-forest-labs/FLUX.2-klein"
    print(f"[test] Local model not found. Loading from HuggingFace Hub: {model_source}")

t0 = time.time()
pipe = FluxPipeline.from_pretrained(
    model_source,
    torch_dtype=torch.float16,
)

if torch.cuda.is_available():
    pipe = pipe.to("cuda")
    # Enable attention slicing for safety (24GB L4 has more headroom, but this
    # keeps peak VRAM in check when running multiple models sequentially)
    pipe.enable_attention_slicing()
    print("[test] Pipeline loaded on CUDA (L4 24GB)")
else:
    print("[test] WARNING: Running on CPU (slow). GPU not detected.")

t1 = time.time()
print(f"[test] Model load time: {t1 - t0:.1f}s")

print("[test] Generating test image (1280x720, 4 steps)...")
result = pipe(
    prompt="A futuristic Tokyo skyline at golden hour, cinematic, 16:9 aspect ratio, high quality",
    width=1280,
    height=720,
    num_inference_steps=4,
    guidance_scale=0.0,
    max_sequence_length=256,
)
t2 = time.time()
print(f"[test] Inference time: {t2 - t1:.1f}s")

image = result.images[0]
image.save(OUTPUT_PATH)
print(f"[test] Test image saved: {OUTPUT_PATH}")
print(f"[test] Image size: {image.size}")
print("[test] PASSED — FLUX.2 klein smoke test complete.")
PYTEST_HEREDOC

log "Running smoke test (generates 1 image)..."
log "Note: First run requires model files. If model was not downloaded, this will pull from HuggingFace Hub."

if sudo -u ec2-user \
    "${VENV_DIR}/bin/python" "$TEST_SCRIPT" 2>&1 | tee -a "$LOG_FILE"; then
    log "Smoke test PASSED. Test image: $TEST_OUTPUT"
    mark_installed "Smoke test: PASSED"
else
    log "WARNING: Smoke test FAILED. Check log for details."
    log "         Common causes: NVIDIA driver needs reboot, model not yet downloaded."
    mark_installed "Smoke test: FAILED (see log)"
fi

# Clean up temp test script
rm -f "$TEST_SCRIPT"


# =============================================================================
# 9. Summary
# =============================================================================
echo ""
echo "============================================================"
echo " SETUP COMPLETE — Summary"
echo "============================================================"
echo " Log file   : $LOG_FILE"
echo " Virtualenv : $VENV_DIR"
echo " Models     : $MODEL_DIR_FLUX"
echo "              $MODEL_DIR_WAN"
echo " startup.sh : ${SCRIPTS_DIR}/startup.sh"
echo ""
echo " Installed / Configured:"
for item in "${INSTALLED_ITEMS[@]}"; do
    echo "   [+] $item"
done
echo ""
echo " Next steps:"
echo "   1. If NVIDIA driver was just installed, REBOOT the instance."
echo "   2. Store SSM parameters:"
echo "      aws ssm put-parameter --name '/ai-image-gen/s3-bucket' \\"
echo "          --value 'your-bucket-name' --type String"
echo "      aws ssm put-parameter --name '/ai-image-gen/huggingface-token' \\"
echo "          --value 'hf_xxx' --type SecureString   # optional for FLUX.2/Wan2.2 (both Apache 2.0)"
echo "   3. Upload generate_images.py to ${SCRIPTS_DIR}/"
echo "   4. Upload pending.json to s3://BUCKET/prompts/pending.json"
echo "   5. To test manually:"
echo "      source ${VENV_DIR}/bin/activate"
echo "      python ${SCRIPTS_DIR}/generate_images.py --from-s3"
echo "   6. Create AMI after verifying everything works:"
echo "      aws ec2 create-image --instance-id \$(ec2-metadata -i | cut -d' ' -f2) \\"
echo "          --name 'ai-image-gen-v1'"
echo "============================================================"
