"""
youtube_pipeline.py 内に追加する自動停止スニペット

このコードを youtube_pipeline.py の最後に追加してください。
"""

import boto3
import os
from datetime import datetime

def cleanup_on_pipeline_complete():
    """
    パイプライン完了時、EC2インスタンスを自動停止

    環境変数:
      RUN_ON_EC2: "true" の場合のみ実行（ローカル開発時は実行しない）
      AWS_REGION: デフォルト "ap-northeast-1"
      INSTANCE_ID: デフォルト "i-02ae03f0b54d46ac1"
    """

    # 環境変数で制御（ローカル開発時は実行しない）
    if os.getenv('RUN_ON_EC2', 'false').lower() != 'true':
        print(f"[{datetime.now()}] ℹ️  Skipping EC2 stop (RUN_ON_EC2 is not set)")
        return

    instance_id = os.getenv('INSTANCE_ID', 'i-02ae03f0b54d46ac1')
    region = os.getenv('AWS_REGION', 'ap-northeast-1')

    try:
        print(f"[{datetime.now()}] 🛑 Initiating EC2 instance shutdown...")
        print(f"    Instance ID: {instance_id}")
        print(f"    Region: {region}")

        ec2 = boto3.client('ec2', region_name=region)

        # EC2 インスタンスを停止
        response = ec2.stop_instances(InstanceIds=[instance_id])

        print(f"[{datetime.now()}] ✅ Stop command sent to EC2")
        print(f"    Response: {response}")

    except Exception as e:
        # パイプライン自体は失敗と見なさない
        print(f"[{datetime.now()}] ⚠️  EC2 stop failed (but pipeline continues)")
        print(f"    Error: {str(e)}")
        print(f"    → You may need to manually stop the instance")


# ============================================
# 使用方法：youtube_pipeline.py の main() 関数で
# ============================================
#
# if __name__ == "__main__":
#     try:
#         edit_log = run_pipeline(config)
#         print(json.dumps(edit_log, ensure_ascii=False))
#
#     finally:
#         cleanup_on_pipeline_complete()  # ← ここに追加
#
# ============================================

# EC2 上での実行例:
#
# export RUN_ON_EC2=true
# export AWS_REGION=ap-northeast-1
# python3 youtube_pipeline.py
#
# → パイプライン完了後、自動的にインスタンスが停止します
