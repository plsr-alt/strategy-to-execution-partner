#!/bin/bash
# EC2 v3.1 デプロイ — 修正コード転送 + ffmpeg + Kokoro モデルDL
EC2_PASS="Welcome1234!"
EC2_IP="18.183.153.86"
SSH_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"
LOCAL_DIR="/mnt/c/Users/tshibasaki/Desktop/etc/work/task/03_PROJECTS/youtube_automation"

echo "=== Step 1: 修正ファイル転送 ==="
for f in youtube_pipeline.py requirements.txt; do
    sshpass -p "$EC2_PASS" scp $SSH_OPTS "$LOCAL_DIR/$f" ec2-user@$EC2_IP:~/youtube_automation/ && \
    echo "  OK: $f" || echo "  FAIL: $f"
done

echo ""
echo "=== Step 2: ffmpeg インストール ==="
sshpass -p "$EC2_PASS" ssh $SSH_OPTS ec2-user@$EC2_IP "
sudo dnf install -y ffmpeg ffmpeg-libs 2>&1 | tail -5
echo ''
ffmpeg -version 2>&1 | head -1
"

echo ""
echo "=== Step 3: pip 更新 ==="
sshpass -p "$EC2_PASS" ssh $SSH_OPTS ec2-user@$EC2_IP "
source ~/venv/bin/activate
pip install -r ~/youtube_automation/requirements.txt 2>&1 | tail -10
"

echo ""
echo "=== Step 4: Kokoro ONNX モデルダウンロード ==="
sshpass -p "$EC2_PASS" ssh $SSH_OPTS ec2-user@$EC2_IP "
source ~/venv/bin/activate
python3 -c '
from pathlib import Path
import requests

model_dir = Path.home() / \".kokoro_onnx\"
model_dir.mkdir(exist_ok=True)

HF_BASE = \"https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX/resolve/main\"
files = [
    (\"onnx/kokoro-v1.0.int8.onnx\", model_dir / \"kokoro-v1.0.int8.onnx\"),
    (\"voices-v1.0.bin\", model_dir / \"voices-v1.0.bin\"),
]

for remote, local in files:
    if local.exists():
        print(f\"  EXISTS: {local.name} ({local.stat().st_size // 1024 // 1024}MB)\")
    else:
        print(f\"  Downloading {local.name}...\")
        resp = requests.get(f\"{HF_BASE}/{remote}\", timeout=600)
        resp.raise_for_status()
        local.write_bytes(resp.content)
        print(f\"  OK: {local.name} ({len(resp.content) // 1024 // 1024}MB)\")
' 2>&1
"

echo ""
echo "=== Step 5: Kokoro ONNX 動作テスト ==="
sshpass -p "$EC2_PASS" ssh $SSH_OPTS ec2-user@$EC2_IP "
source ~/venv/bin/activate
python3 -c '
from kokoro_onnx import Kokoro
from pathlib import Path

model_dir = Path.home() / \".kokoro_onnx\"
kokoro = Kokoro(str(model_dir / \"kokoro-v1.0.int8.onnx\"), str(model_dir / \"voices-v1.0.bin\"))
samples, sr = kokoro.create(\"テスト音声です\", voice=\"jf_alpha\", speed=1.1, lang=\"ja\")
print(f\"OK: {len(samples)} samples at {sr}Hz ({len(samples)/sr:.1f}s)\")
' 2>&1
"

echo ""
echo "=== Step 6: パイプライン起動確認 ==="
sshpass -p "$EC2_PASS" ssh $SSH_OPTS ec2-user@$EC2_IP "
source ~/venv/bin/activate
python3 ~/youtube_automation/youtube_pipeline.py --help 2>&1 | head -5
"

echo ""
echo "=== 完了! ==="
