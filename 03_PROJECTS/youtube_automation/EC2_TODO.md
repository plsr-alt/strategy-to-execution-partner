# EC2インスタンス自動停止/起動 — 実装TODO

## 🎯 全体ゴール
YouTube 自動化パイプライン用 EC2 インスタンスの自動停止/起動を CloudFormation で実装

---

## Phase 3-1: CloudFormation テンプレート作成

- [ ] **3-1-1** CloudFormation テンプレート生成（YAML）
  - Lambda IAM Role（EC2 start/stop 権限）
  - Lambda Function（Python コード）
  - EventBridge Rules 2個（起動 6:00 / 停止 23:00）
  - Lambda Permission（EventBridge → Lambda 実行権限）
  - 出力: `ec2_automation_stack.yaml`

- [ ] **3-1-2** Lambda コード（Python）を テンプレートに埋め込み
  - Action: start / stop の分岐
  - Error handling
  - CloudWatch Logs 出力

---

## Phase 3-2: youtube_pipeline.py パイプライン内自動停止

- [ ] **3-2-1** `cleanup_on_pipeline_complete()` 関数を追加
  - パイプライン完了後自動実行
  - boto3 で EC2 stop-instances 実行
  - 環境変数 `RUN_ON_EC2` で制御（ローカル開発時は実行しない）

- [ ] **3-2-2** パイプライン main() 内で finally ブロック追加
  - `cleanup_on_pipeline_complete()` 呼び出し

---

## Phase 3-3: デプロイスクリプト作成

- [ ] **3-3-1** `deploy.sh` 作成
  - CloudFormation スタック作成
  - Stack status 確認
  - Lambda 関数を初期テスト

- [ ] **3-3-2** AWS CLI プロファイル確認
  - `aws sts get-caller-identity` で認証確認

---

## Phase 3-4: ローカルテスト

- [ ] **3-4-1** CloudFormation テンプレート構文チェック
  ```bash
  aws cloudformation validate-template --template-body file://ec2_automation_stack.yaml
  ```

- [ ] **3-4-2** Lambda コード単体テスト
  - `pytest` で start/stop ロジック確認
  - boto3 mock テスト

---

## Phase 3-5: AWS デプロイ（実行）

- [ ] **3-5-1** CloudFormation スタック作成
  ```bash
  aws cloudformation create-stack \
    --stack-name youtube-automation-ec2-schedule \
    --template-body file://ec2_automation_stack.yaml \
    --capabilities CAPABILITY_NAMED_IAM \
    --region ap-northeast-1
  ```

- [ ] **3-5-2** スタック作成完了待機
  ```bash
  aws cloudformation wait stack-create-complete \
    --stack-name youtube-automation-ec2-schedule \
    --region ap-northeast-1
  ```

- [ ] **3-5-3** Lambda 関数の手動テスト（START）
  ```bash
  aws lambda invoke \
    --function-name youtube-automation-ec2-control \
    --payload '{"action":"start"}' \
    --region ap-northeast-1 \
    response.json
  ```

- [ ] **3-5-4** EC2 インスタンス状態確認
  ```bash
  aws ec2 describe-instances \
    --instance-ids i-02ae03f0b54d46ac1 \
    --region ap-northeast-1 \
    | jq '.Reservations[].Instances[].State'
  ```

- [ ] **3-5-5** Lambda 関数の手動テスト（STOP）
  ```bash
  aws lambda invoke \
    --function-name youtube-automation-ec2-control \
    --payload '{"action":"stop"}' \
    --region ap-northeast-1 \
    response.json
  ```

---

## Phase 3-6: EventBridge スケジュール検証

- [ ] **3-6-1** EventBridge ルール一覧確認
  ```bash
  aws events list-rules \
    --name-prefix youtube-automation \
    --region ap-northeast-1
  ```

- [ ] **3-6-2** CloudWatch Logs で Lambda 実行ログ確認
  - ログイングループ: `/aws/lambda/youtube-automation-ec2-control`

---

## Phase 3-7: youtube_pipeline.py との統合テスト

- [ ] **3-7-1** EC2 上で環境変数 `RUN_ON_EC2=true` を設定
  ```bash
  export RUN_ON_EC2=true
  export AWS_REGION=ap-northeast-1
  ```

- [ ] **3-7-2** パイプライン実行＆パイプライン完了時に自動停止を確認
  ```bash
  python3 youtube_pipeline.py
  ```

- [ ] **3-7-3** CloudWatch Logs でパイプライン停止ログを確認

---

## Phase 3-8: 本番デプロイ準備

- [ ] **3-8-1** CloudFormation テンプレート + デプロイスクリプトを Git に commit
  ```bash
  git add ec2_automation_stack.yaml deploy.sh EC2_*.md
  git commit -m "feat: EC2自動停止/起動スケジュール（CloudFormation+Lambda）"
  ```

- [ ] **3-8-2** README 更新
  - EC2 自動スケジューリングの説明追加
  - デプロイ手順を記載

- [ ] **3-8-3** 本番環境で定刻テスト（夜23:00停止の動作確認）

---

## トラブルシューティング

### Lambda が EventBridge から実行されない
- [ ] Lambda Permission が正しく設定されているか確認
  ```bash
  aws lambda get-policy \
    --function-name youtube-automation-ec2-control \
    --region ap-northeast-1
  ```

### EC2 start/stop が失敗する
- [ ] Lambda IAM Role の EC2 권限を確認
- [ ] インスタンス ID が正しいか確認
- [ ] スポットインスタンス没収状況を確認

### CloudWatch Logs に出力されない
- [ ] Lambda の実行ロールに `CloudWatchLogsFullAccess` があるか確認
- [ ] ログイングループが自動生成されているか確認

---

## 完成チェックリスト

- [ ] CloudFormation テンプレート作成
- [ ] Lambda 関数実装
- [ ] EventBridge ルール設定
- [ ] youtube_pipeline.py に自動停止機能追加
- [ ] AWS デプロイ完了
- [ ] 手動テスト成功
- [ ] 本番環境テスト成功
- [ ] Git にコミット

---

## 参考資料

- AWS CloudFormation: https://docs.aws.amazon.com/ja_jp/cloudformation/
- AWS Lambda: https://docs.aws.amazon.com/ja_jp/lambda/
- AWS EventBridge: https://docs.aws.amazon.com/ja_jp/events/
- boto3 EC2: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html
