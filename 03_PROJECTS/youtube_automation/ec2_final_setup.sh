#!/bin/bash
# EC2 最終セットアップ — 残りパッケージ + ファイル再転送 + テスト動画
EC2_PASS="Welcome1234!"
EC2_IP="18.183.153.86"
SSH_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"
LOCAL_DIR="/mnt/c/Users/tshibasaki/Desktop/etc/work/task/03_PROJECTS/youtube_automation"

echo "=== Step 1: 更新ファイル再転送 ==="
for f in youtube_pipeline.py requirements.txt; do
    sshpass -p "$EC2_PASS" scp $SSH_OPTS "$LOCAL_DIR/$f" ec2-user@$EC2_IP:~/youtube_automation/ && \
    echo "  ✅ $f" || echo "  ⚠️ $f failed"
done

echo ""
echo "=== Step 2: requirements.txt フルインストール ==="
sshpass -p "$EC2_PASS" ssh $SSH_OPTS ec2-user@$EC2_IP "
source ~/venv/bin/activate
pip install python-dotenv==1.0.0 groq pydantic==2.5.0 pyyaml==6.0 pillow==10.1.0 moviepy==1.0.3 matplotlib gTTS==2.5.0 pydub==0.25.1 google-auth-oauthlib==1.2.0 google-api-python-client==2.107.0 google-auth-httplib2==0.2.0 2>&1 | tail -20
echo ''
pip install -r ~/youtube_automation/requirements.txt 2>&1 | tail -10
"

echo ""
echo "=== Step 3: .env 確認・更新 ==="
sshpass -p "$EC2_PASS" ssh $SSH_OPTS ec2-user@$EC2_IP "
cd ~/youtube_automation
# VIDEO_DURATION の更新
sed -i 's/VIDEO_DURATION_MIN=.*/VIDEO_DURATION_MIN=20/' .env 2>/dev/null
sed -i 's/VIDEO_DURATION_MAX=.*/VIDEO_DURATION_MAX=25/' .env 2>/dev/null
grep -q CHANNEL_NAME .env 2>/dev/null || echo 'CHANNEL_NAME=マネー研究所' >> .env
cat .env | grep -E '(DURATION|CHANNEL)'
"

echo ""
echo "=== Step 4: パイプライン動作確認 ==="
sshpass -p "$EC2_PASS" ssh $SSH_OPTS ec2-user@$EC2_IP "
source ~/venv/bin/activate
python ~/youtube_automation/youtube_pipeline.py --help
"

echo ""
echo "=== Step 5: テスト動画1本生成 ==="
sshpass -p "$EC2_PASS" ssh $SSH_OPTS ec2-user@$EC2_IP "
source ~/venv/bin/activate
cd ~/youtube_automation
nohup python youtube_pipeline.py --theme finance --count 1 --log-file logs/test_v3.log > logs/test_v3_stdout.log 2>&1 &
echo \$!
echo 'テスト動画生成バックグラウンドで開始 (PID: '\$!')'
" 2>&1

echo ""
echo "=== 完了！ テスト動画はバックグラウンドで生成中 ==="
echo "確認: ssh ec2-user@$EC2_IP 'tail -f ~/youtube_automation/logs/test_v3.log'"
