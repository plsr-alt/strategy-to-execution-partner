#!/bin/bash
# EC2 v3.1 修正 — ffmpeg静的バイナリ + Kokoroモデル正しいURL + コード再転送
EC2_PASS="Welcome1234!"
EC2_IP="18.183.153.86"
SSH_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"
LOCAL_DIR="/mnt/c/Users/tshibasaki/Desktop/etc/work/task/03_PROJECTS/youtube_automation"

echo "=== Step 1: 修正済みpipeline再転送 ==="
sshpass -p "$EC2_PASS" scp $SSH_OPTS "$LOCAL_DIR/youtube_pipeline.py" ec2-user@$EC2_IP:~/youtube_automation/ && echo "  OK" || echo "  FAIL"

echo ""
echo "=== Step 2: ffmpeg 静的バイナリ (aarch64) ==="
sshpass -p "$EC2_PASS" ssh $SSH_OPTS ec2-user@$EC2_IP '
if command -v ffmpeg &>/dev/null; then
    echo "ffmpeg already installed"
    ffmpeg -version | head -1
else
    echo "Downloading ffmpeg static binary for aarch64..."
    cd /tmp
    curl -L -o ffmpeg-release-arm64-static.tar.xz "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-arm64-static.tar.xz" 2>&1 | tail -3
    tar xf ffmpeg-release-arm64-static.tar.xz
    FFDIR=$(ls -d ffmpeg-*-arm64-static 2>/dev/null | head -1)
    if [ -n "$FFDIR" ]; then
        sudo cp "$FFDIR/ffmpeg" /usr/local/bin/
        sudo cp "$FFDIR/ffprobe" /usr/local/bin/
        sudo chmod +x /usr/local/bin/ffmpeg /usr/local/bin/ffprobe
        echo "ffmpeg installed:"
        ffmpeg -version | head -1
    else
        echo "FAIL: could not find extracted directory"
        ls /tmp/ffmpeg* 2>/dev/null
    fi
    rm -rf /tmp/ffmpeg*
fi
' 2>&1

echo ""
echo "=== Step 3: Kokoro ONNX モデルDL (GitHub Releases) ==="
sshpass -p "$EC2_PASS" ssh $SSH_OPTS ec2-user@$EC2_IP '
mkdir -p ~/.kokoro_onnx
cd ~/.kokoro_onnx
GH="https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0"
for f in kokoro-v1.0.int8.onnx voices-v1.0.bin; do
    if [ -f "$f" ] && [ -s "$f" ]; then
        echo "  EXISTS: $f ($(du -h $f | cut -f1))"
    else
        echo "  Downloading $f..."
        curl -L -o "$f" "$GH/$f" 2>&1 | tail -2
        echo "  OK: $f ($(du -h $f | cut -f1))"
    fi
done
ls -lh ~/.kokoro_onnx/
' 2>&1

echo ""
echo "=== Step 4: Kokoro ONNX テスト ==="
sshpass -p "$EC2_PASS" ssh $SSH_OPTS ec2-user@$EC2_IP '
source ~/venv/bin/activate
python3 -c "
from kokoro_onnx import Kokoro
from pathlib import Path
import soundfile as sf
import numpy as np

model_dir = Path.home() / \".kokoro_onnx\"
print(\"Loading model...\")
kokoro = Kokoro(str(model_dir / \"kokoro-v1.0.int8.onnx\"), str(model_dir / \"voices-v1.0.bin\"))
print(\"Generating test audio...\")
samples, sr = kokoro.create(\"こんにちは、マネー研究所です。今日は投資について解説します。\", voice=\"jf_alpha\", speed=1.1, lang=\"ja\")
sf.write(\"/tmp/kokoro_test.wav\", samples, sr)
duration = len(samples) / sr
print(f\"SUCCESS: {duration:.1f}s audio at {sr}Hz\")
" 2>&1
' 2>&1

echo ""
echo "=== Step 5: ffmpeg WAV→MP3 テスト ==="
sshpass -p "$EC2_PASS" ssh $SSH_OPTS ec2-user@$EC2_IP '
if [ -f /tmp/kokoro_test.wav ]; then
    ffmpeg -y -i /tmp/kokoro_test.wav -codec:a libmp3lame -qscale:a 2 /tmp/kokoro_test.mp3 2>&1 | tail -3
    ls -lh /tmp/kokoro_test.mp3 2>/dev/null && echo "MP3 conversion OK" || echo "MP3 conversion FAIL"
fi
' 2>&1

echo ""
echo "=== 完了! ==="
