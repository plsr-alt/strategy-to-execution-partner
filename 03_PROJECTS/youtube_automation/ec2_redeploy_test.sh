#!/bin/bash
# 修正コード再転送 + v3.2テスト実行
EC2_PASS="Welcome1234!"
EC2_IP="18.183.153.86"
SSH_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"
LOCAL_DIR="/mnt/c/Users/tshibasaki/Desktop/etc/work/task/03_PROJECTS/youtube_automation"

echo "=== Step 1: 修正コード転送 ==="
sshpass -p "$EC2_PASS" scp $SSH_OPTS "$LOCAL_DIR/youtube_pipeline.py" ec2-user@$EC2_IP:~/youtube_automation/ && echo "  OK" || echo "  FAIL"

echo ""
echo "=== Step 2: テスト動画開始 ==="
sshpass -p "$EC2_PASS" ssh $SSH_OPTS ec2-user@$EC2_IP "
source ~/venv/bin/activate
cd ~/youtube_automation
nohup python youtube_pipeline.py --theme finance --count 1 --log-file logs/test_v32.log > logs/test_v32_stdout.log 2>&1 &
echo \"PID: \$!\"
echo \"v3.2 test started\"
" 2>&1

echo ""
echo "=== 完了 ==="
