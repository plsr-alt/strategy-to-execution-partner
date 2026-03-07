#!/bin/bash
EC2_PASS="Welcome1234!"
EC2_IP="18.183.153.86"
SSH_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=10"
sshpass -p "$EC2_PASS" ssh $SSH_OPTS ec2-user@$EC2_IP "tail -25 ~/youtube_automation/logs/prod_v35.log 2>/dev/null; echo ---; ps aux | grep python | grep -v grep" 2>&1
