#!/bin/bash
EC2_PASS="Welcome1234!"
EC2_IP="18.183.153.86"
SSH_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"
sshpass -p "$EC2_PASS" ssh $SSH_OPTS ec2-user@$EC2_IP "
cat ~/youtube_automation/logs/test_v3.log 2>/dev/null | tail -60
echo '---'
cat ~/youtube_automation/logs/test_v3_stdout.log 2>/dev/null | tail -30
echo '---'
ps aux | grep youtube_pipeline | grep -v grep
"
