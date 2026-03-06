# タスク: 金融チャンネルYouTube動画の量産体制構築

## 現状
- EC2: 18.183.153.86 (ec2-user, パスワード: Welcome1234!, t4g.medium, ap-northeast-1)
- EC2上のyoutube_automationフォルダが空（スポットインスタンス再起動で消失）
- ローカルにパイプライン一式あり: `C:/Users/tshibasaki/Desktop/etc/work/task/03_PROJECTS/youtube_automation/`
- youtube_pipeline.py（8ステップ全自動）は実装済み・動作確認済み
- token.json（OAuth認証済み）もローカルにあり

## 必要な成果物
1. **EC2再デプロイスクリプト** (`redeploy_ec2.sh`)
   - ローカルからEC2へパイプライン一式を再転送するスクリプト
   - sshpass + scp（またはSSH経由echo）でファイル転送
   - .env, token.json, youtube_pipeline.py, requirements等
   - pip install実行
   - 動作確認コマンド

2. **量産バッチスクリプト** (`batch_produce.sh`)
   - 1日に複数本（3本）の動画を順番に生成・アップロード
   - 各動画間に適切な待機時間
   - ログ出力（日付付き）
   - エラー時に次の動画へ継続（1本失敗しても止まらない）

3. **cron設定スクリプト** (`setup_cron.sh`)
   - 毎日JST 9:00にbatch_produce.shを自動起動
   - ログを~/youtube_automation/logs/に保存

## 制約
- 出力先: `C:/Users/tshibasaki/Desktop/etc/work/task/03_PROJECTS/youtube_automation/` に作成
- WSLコマンド形式で実行可能にすること（wsl sshpass...）
- EC2ユーザー: ec2-user（ubuntuではない）
- 金融・投資・節約ジャンルの動画を量産
- youtube_pipeline.py の既存コードは変更しない
