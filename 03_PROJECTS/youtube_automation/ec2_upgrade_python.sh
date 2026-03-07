#!/bin/bash
# EC2上のPythonを3.11にアップグレード + Kokoro ONNX インストール
EC2_PASS="Welcome1234!"
EC2_IP="18.183.153.86"
SSH_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"

echo "=== Step 1: Python 3.11 インストール ==="
sshpass -p "$EC2_PASS" ssh $SSH_OPTS ec2-user@$EC2_IP "
# Amazon Linux 2 の場合
sudo amazon-linux-extras install python3.11 -y 2>/dev/null || \
# Amazon Linux 2023 の場合
sudo dnf install python3.11 python3.11-devel -y 2>/dev/null || \
# AL2 で extras がない場合
sudo yum install python3.11 python3.11-devel -y 2>/dev/null || \
echo 'Python 3.11 install failed'

# 確認
python3.11 --version 2>/dev/null || python3 --version
"

echo ""
echo "=== Step 2: venv を Python 3.11 で再構築 ==="
sshpass -p "$EC2_PASS" ssh $SSH_OPTS ec2-user@$EC2_IP "
if python3.11 --version 2>/dev/null; then
    echo 'Python 3.11 detected, rebuilding venv...'
    rm -rf ~/venv
    python3.11 -m venv ~/venv
    source ~/venv/bin/activate
    pip install --upgrade pip
    python --version
else
    echo 'Python 3.11 not available, keeping Python 3.9 venv'
    source ~/venv/bin/activate
    python --version
fi
"

echo ""
echo "=== Step 3: 全パッケージインストール ==="
sshpass -p "$EC2_PASS" ssh $SSH_OPTS ec2-user@$EC2_IP "
source ~/venv/bin/activate
PYVER=\$(python --version 2>&1)
echo \"Python version: \$PYVER\"

# まず requirements.txt の基本パッケージ
pip install -r ~/youtube_automation/requirements.txt 2>&1 | tail -15
echo ''

# Python 3.10+ なら kokoro-onnx をインストール
if python -c 'import sys; exit(0 if sys.version_info >= (3,10) else 1)' 2>/dev/null; then
    echo '=== Kokoro ONNX インストール ==='
    pip install kokoro-onnx soundfile numpy 2>&1 | tail -10
    echo ''
    echo '=== Kokoro モデルダウンロード ==='
    python -c '
import os
from pathlib import Path
model_dir = Path.home() / \".kokoro_onnx\"
model_dir.mkdir(exist_ok=True)
# kokoro-onnx は初回実行時に自動ダウンロード
print(\"Model dir:\", model_dir)
' 2>&1
else
    echo 'Python < 3.10 — Kokoro TTS スキップ (gTTS fallback)'
fi
"

echo ""
echo "=== Step 4: 動作確認 ==="
sshpass -p "$EC2_PASS" ssh $SSH_OPTS ec2-user@$EC2_IP "
source ~/venv/bin/activate
python --version
echo ''

# Kokoro ONNX テスト
python -c '
try:
    from kokoro_onnx import Kokoro
    print(\"Kokoro ONNX: OK (import success)\")
except ImportError as e:
    print(f\"Kokoro ONNX: NOT AVAILABLE ({e})\")
    print(\"gTTS fallback will be used\")
' 2>&1

echo ''
# パイプライン起動テスト
python ~/youtube_automation/youtube_pipeline.py --help 2>&1 | head -5
"

echo ""
echo "=== 完了 ==="
