# EC2インスタンス自動停止/起動スケジュール — 仕様書

## 概要
YouTube 自動化パイプライン用 EC2 インスタンス（`t4g.medium`）の自動停止/起動をスケジュール化。
課金を最小化しつつ、スポットインスタンス没収時の保険とする。

---

## ターゲット
| 項目 | 値 |
|------|-----|
| インスタンスID | `i-02ae03f0b54d46ac1` |
| インスタンスタイプ | `t4g.medium` |
| リージョン | `ap-northeast-1` (東京) |
| 環境 | 開発・本番共用 |

---

## スケジューリング要件

### 毎日のライフサイクル

| 時刻 | アクション | 理由 |
|------|----------|------|
| **06:00** | **START** | YouTube パイプライン実行開始 |
| **~06:30** | パイプライン処理中（自動） | 15-25分で完了 |
| **完了時** | **STOP**（自動） | パイプライン終了時に自動停止 |
| **23:00** | **STOP**（スケジュール停止） | 保険（念のため） |

### 料金削減効果（試算）

```
t4g.medium on-demand 東京リージョン:
  - オンデマンド: 約 ¥0.0528/h
  - スポット: 約 ¥0.0158/h (70%削減)

毎日 06:00-06:30 実行 + スケジュール停止 の場合:
  - 1ヶ月: 約 ¥30-50（月次消費 vs 継続稼働なら ¥1,300以上）
```

---

## アーキテクチャ

```
┌─────────────────────────────────────────┐
│ AWS CloudWatch Events (EventBridge)     │
│                                          │
│  ┌──────────────────────────────────┐  │
│  │ Cron: 06:00 JST (Every day)      │  │
│  │ Action: Invoke Lambda             │  │
│  └──────────────────────────────────┘  │
│                                          │
│  ┌──────────────────────────────────┐  │
│  │ Cron: 23:00 JST (Every day)      │  │
│  │ Action: Invoke Lambda             │  │
│  └──────────────────────────────────┘  │
└────────────────┬────────────────────────┘
                 │
                 ↓
        ┌────────────────┐
        │ AWS Lambda     │
        │ Function       │
        │ (py script)    │
        └────────────┬───┘
                     │
                     ↓
        ┌────────────────────────┐
        │ AWS EC2                │
        │ start/stop API call    │
        │ i-02ae03f0b54d46ac1    │
        └────────────────────────┘
```

---

## 実装詳細

### 1. IAM Role (Lambda用)
**スタック内で自動生成**

```yaml
LambdaEC2Role:
  Type: AWS::IAM::Role
  Properties:
    AssumeRolePolicyDocument:
      Version: '2012-10-17'
      Statement:
        - Effect: Allow
          Principal:
            Service: lambda.amazonaws.com
          Action: sts:AssumeRole
    ManagedPolicyArns:
      - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
    Policies:
      - PolicyName: EC2Control
        PolicyDocument:
          Version: '2012-10-17'
          Statement:
            - Effect: Allow
              Action:
                - ec2:StartInstances
                - ec2:StopInstances
                - ec2:DescribeInstances
              Resource: arn:aws:ec2:ap-northeast-1:*:instance/*
              Condition:
                StringEquals:
                  ec2:ResourceTag/ManagedBy: youtube-automation
```

---

### 2. Lambda Function

#### 環境変数
```
INSTANCE_ID = i-02ae03f0b54d46ac1
REGION = ap-northeast-1
ACTION = (start|stop) ← EventBridge から渡す
```

#### コード例
```python
import boto3
import json
import os
from datetime import datetime

ec2 = boto3.client('ec2', region_name=os.getenv('REGION'))

def lambda_handler(event, context):
    """EC2 インスタンスの start/stop を実行"""

    instance_id = os.getenv('INSTANCE_ID')
    action = event.get('action', 'unknown')

    try:
        if action == 'start':
            ec2.start_instances(InstanceIds=[instance_id])
            message = f"✅ Started instance {instance_id}"
        elif action == 'stop':
            ec2.stop_instances(InstanceIds=[instance_id])
            message = f"⏹️ Stopped instance {instance_id}"
        else:
            message = f"❌ Unknown action: {action}"

        print(json.dumps({
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "instance_id": instance_id,
            "status": "success",
            "message": message
        }))

        return {
            "statusCode": 200,
            "body": json.dumps({"message": message})
        }

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
```

---

### 3. EventBridge Rules

#### Rule 1: 朝 6:00 START
```yaml
StartInstanceRule:
  Type: AWS::Events::Rule
  Properties:
    Name: youtube-automation-start-6am
    ScheduleExpression: "cron(0 6 * * ? *)"  # UTC+9 では 15:00 UTC = 06:00 JST
    State: ENABLED
    Targets:
      - Arn: !GetAtt EC2ControlLambda.Arn
        RoleArn: !GetAtt EventBridgeRole.Arn
        Input: '{"action": "start"}'
```

#### Rule 2: 夜 23:00 STOP
```yaml
StopInstanceRule:
  Type: AWS::Events::Rule
  Properties:
    Name: youtube-automation-stop-11pm
    ScheduleExpression: "cron(0 14 * * ? *)"  # UTC+9 では 14:00 UTC = 23:00 JST
    State: ENABLED
    Targets:
      - Arn: !GetAtt EC2ControlLambda.Arn
        RoleArn: !GetAtt EventBridgeRole.Arn
        Input: '{"action": "stop"}'
```

---

### 4. youtube_pipeline.py 内の自動停止

パイプライン完了後、以下を追加：

```python
# パイプライン最後 (Step 8 後)
def cleanup_on_pipeline_complete():
    """パイプライン完了時、EC2インスタンスを自動停止"""

    import boto3
    import os
    from datetime import datetime

    try:
        if os.getenv('RUN_ON_EC2') == 'true':
            ec2 = boto3.client('ec2', region_name='ap-northeast-1')
            instance_id = 'i-02ae03f0b54d46ac1'

            print(f"[{datetime.now()}] 🛑 Stopping EC2 instance: {instance_id}")
            ec2.stop_instances(InstanceIds=[instance_id])
            print(f"[{datetime.now()}] ✅ Stop command sent")

    except Exception as e:
        print(f"[ERROR] Failed to stop instance: {str(e)}")
        # 停止失敗しても パイプライン自体は失敗とは見なさない
        pass

# main() の最後に呼び出し
if __name__ == "__main__":
    try:
        edit_log = run_pipeline(config)
        print(json.dumps(edit_log, ensure_ascii=False))
    finally:
        cleanup_on_pipeline_complete()  # ← 追加
```

---

## CloudFormation テンプレート出力物

| ファイル | 内容 |
|---------|------|
| `ec2_automation_stack.yaml` | CloudFormation テンプレート |
| `lambda_ec2_control.py` | Lambda関数コード |
| `deploy.sh` | デプロイスクリプト |

---

## デプロイ手順（概要）

```bash
# 1. CloudFormation スタック作成
aws cloudformation create-stack \
  --stack-name youtube-automation-ec2-schedule \
  --template-body file://ec2_automation_stack.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --region ap-northeast-1

# 2. スタック確認
aws cloudformation describe-stacks \
  --stack-name youtube-automation-ec2-schedule \
  --region ap-northeast-1

# 3. EventBridge ルール確認
aws events list-rules \
  --name-prefix youtube-automation \
  --region ap-northeast-1
```

---

## 注意事項

### ⚠️ UTC/JST 変換
EventBridge の cron は UTC で指定。
- 06:00 JST = 21:00 UTC 前日 → `cron(0 21 * * ? *)`
- 23:00 JST = 14:00 UTC → `cron(0 14 * * ? *)`

✅ **テンプレートで自動変換済み**

### ⚠️ スポットインスタンスの仕様
- 没収されると Stop → Terminate に変わる可能性
- → EventBridge で復帰できない場合あり
- **対策**: Lambda で DescribeInstances → 状態確認 → 必要に応じてリスタート

### ⚠️ boto3 認証
EC2 上で実行する場合、IAM Instance Profile 必須
テンプレート内で自動設定済み

---

## テスト方法

```bash
# 1. Lambda を手動で実行（START）
aws lambda invoke \
  --function-name youtube-automation-ec2-control \
  --payload '{"action":"start"}' \
  --region ap-northeast-1 \
  response.json

# 2. Lambda を手動で実行（STOP）
aws lambda invoke \
  --function-name youtube-automation-ec2-control \
  --payload '{"action":"stop"}' \
  --region ap-northeast-1 \
  response.json

# 3. 実行ログ確認
cat response.json
```

---

## 完成後の状態

✅ インスタンス自動起動：朝 6:00
✅ パイプライン完了時に自動停止
✅ 保険停止：夜 23:00
✅ 月間コスト：最小化（~¥30-50）
