#!/bin/bash
# EC2上でKokoro TTSの依存をインストールする一時スクリプト
EC2_PASS="Welcome1234!"
EC2_IP="18.183.153.86"
SSH_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"

echo "=== Step 1: .env の更新 ==="
sshpass -p "$EC2_PASS" ssh $SSH_OPTS ec2-user@$EC2_IP "
cd ~/youtube_automation
# VIDEO_DURATION の更新
sed -i 's/VIDEO_DURATION_MIN=.*/VIDEO_DURATION_MIN=20/' .env
sed -i 's/VIDEO_DURATION_MAX=.*/VIDEO_DURATION_MAX=25/' .env
# CHANNEL_NAME 追加（なければ）
grep -q CHANNEL_NAME .env || echo 'CHANNEL_NAME=マネー研究所' >> .env
# VOICEVOX_URL が不要なので削除（あれば）
sed -i '/VOICEVOX_URL/d' .env
echo '=== .env 内容 ==='
cat .env
"

echo ""
echo "=== Step 2: espeak-ng + フォントインストール ==="
sshpass -p "$EC2_PASS" ssh $SSH_OPTS ec2-user@$EC2_IP "
sudo yum install -y espeak-ng 2>/dev/null || echo 'espeak-ng: yum failed, trying alternatives'
sudo amazon-linux-extras install epel -y 2>/dev/null
sudo yum install -y espeak-ng 2>/dev/null || echo 'espeak-ng install skipped'
# フォントは既にあるか確認
fc-list | grep -i noto | head -3 || echo 'Noto CJK fonts not found'
"

echo ""
echo "=== Step 3: pip install Kokoro TTS ==="
sshpass -p "$EC2_PASS" ssh $SSH_OPTS ec2-user@$EC2_IP "
source ~/venv/bin/activate
pip install --upgrade pip
pip install kokoro soundfile numpy 'misaki[ja]' 2>&1 | tail -30
echo ''
echo '=== pip install result: $? ==='
pip list | grep -i kokoro
pip list | grep -i misaki
"

echo ""
echo "=== Step 4: requirements.txt の残りインストール ==="
sshpass -p "$EC2_PASS" ssh $SSH_OPTS ec2-user@$EC2_IP "
source ~/venv/bin/activate
pip install -r ~/youtube_automation/requirements.txt 2>&1 | tail -15
"

echo ""
echo "=== Step 5: 動作確認 ==="
sshpass -p "$EC2_PASS" ssh $SSH_OPTS ec2-user@$EC2_IP "
source ~/venv/bin/activate
python3 -c 'from kokoro import KPipeline; print(\"Kokoro TTS: OK\")' 2>&1 || echo 'Kokoro TTS: FAILED (gTTS fallback will be used)'
python3 ~/youtube_automation/youtube_pipeline.py --help 2>&1 | head -5
"

echo ""
echo "=== 完了 ==="
