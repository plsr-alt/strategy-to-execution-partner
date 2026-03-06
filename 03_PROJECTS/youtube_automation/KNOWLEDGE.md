# YouTube自動化パイプライン — KNOWLEDGE

> 最終更新: 2026-03-06

---

## 🔴 EC2 スポットインスタンス再起動手順（クイックリカバリ）

### 前提
- インスタンスID: `i-02ae03f0b54d46ac1` (ap-northeast-1)
- タイプ: t4g.medium (ARM/Graviton)
- OS: Amazon Linux 2023
- ユーザー: `ec2-user`
- パスワード: SSH key or password (Tera Term で確認済み)

### ケース1: スポットインスタンスが中断 → 再起動した場合

IPアドレスが変わるため、以下の手順で復帰:

```bash
# 1. 新しいIPを取得
aws ec2 describe-instances \
  --instance-ids i-02ae03f0b54d46ac1 \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text --region ap-northeast-1

# 2. AWS CLI未設定の場合 → Tera Term で直接接続して確認
#    IP はAWSコンソール（EC2 > インスタンス）からも確認可能

# 3. SSH接続（WSL + expect 推奨）
wsl expect -c "
spawn ssh -o StrictHostKeyChecking=no ec2-user@<NEW_IP>
expect \"password:\"
send \"<PASSWORD>\r\"
interact
"

# 4. バッチ状態確認
ps aux | grep python3
ls -lhrt ~/youtube_automation/out/
cat ~/youtube_automation/out/batch_*.log | tail -50

# 5. バッチが止まっていた場合 → 再開
cd ~/youtube_automation
nohup bash batch_produce.sh > out/batch_restart_$(date +%Y%m%d_%H%M%S).log 2>&1 &
disown
echo "PID: $!"
```

### ケース2: インスタンス完全消失 → 新インスタンスで再構築

```bash
# 1. redeploy_ec2.sh を使って全自動デプロイ
#    （WSL上で実行）
cd /mnt/c/Users/tshibasaki/Desktop/etc/work/task/03_PROJECTS/youtube_automation
bash redeploy_ec2.sh

# 2. デプロイ完了後、cron が自動設定される（JST 9:00 バッチ）
# 3. 手動で即時バッチ開始する場合:
ssh ec2-user@<IP>
cd ~/youtube_automation
nohup bash batch_produce.sh > out/batch_$(date +%Y%m%d_%H%M%S).log 2>&1 &
disown
```

### ケース3: デプロイ高速化のコツ

1. **SCP一括転送**: `redeploy_ec2.sh` が自動でやる
2. **venv再作成不要**: `pip install` がべき等なので既存venvに上書き
3. **cron再登録不要**: `setup_cron.sh` がべき等（重複排除済み）
4. **所要時間目安**: 約5-10分（ネットワーク状態による）

---

## 🟡 既知の問題と解決策

### 1. Pillow 10+ で `Image.ANTIALIAS` エラー
- **原因**: Pillow 10 で `ANTIALIAS` が削除 → `LANCZOS` に統合
- **対策**: `youtube_pipeline.py` 冒頭にパッチ追加済み
```python
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS
```

### 2. sshpass がWSLで `!` 付きパスワードを渡せない
- **原因**: bash が `!` を履歴展開と解釈
- **対策**: `expect` を使う（sshpass の代替）
```bash
sudo apt install expect
expect -c "
spawn ssh -o StrictHostKeyChecking=no ec2-user@<IP>
expect \"password:\"
send \"<PASSWORD>\r\"
interact
"
```

### 3. SSH セッションタイムアウト（長時間エンコード中）
- **対策**: `nohup` + `disown` で切断しても継続
```bash
nohup bash batch_produce.sh > out/batch.log 2>&1 &
disown
```

### 4. VOICEVOX Docker 未セットアップ
- **現状**: EC2にDockerイメージなし
- **対策**: gTTS（Google TTS）で代替動作中。品質はPhase 2でElevenLabsに移行予定

### 5. EC2の .env 設定（デプロイ時に更新が必要）
```
VIDEO_DURATION_MIN=15   ← 8から変更（長尺化） ✅ 反映済み
VIDEO_DURATION_MAX=20   ← 12から変更（長尺化） ✅ 反映済み
```

### 6. groq SDK バージョン不整合（2026-03-06 発生・解決済み）
- **症状**: `__init__() got an unexpected keyword argument 'proxies'`
- **原因**: `groq==0.4.2` + `httpx==0.28.1` の非互換。httpx 0.28 で `proxies` パラメータ廃止
- **対策**: `groq>=1.0.0` にアップグレード（`pip install --upgrade groq`）
- **requirements.txt** も `groq>=1.0.0` に更新済み

### 7. 旧バッチの `import time` 漏れ（2026-03-06 発生・解決済み）
- **症状**: 20本バッチが1本成功後クールダウンで `NameError: name 'time' is not defined`
- **原因**: 旧版コードに `import time` が欠落
- **対策**: v2版で修正済み（冒頭に `import time` 追加）

---

## 🟢 パイプライン改善履歴

| 日付 | 改善内容 |
|------|---------|
| 2026-03-06 | 初版実装: 8ステップパイプライン |
| 2026-03-06 | ANTIALIAS互換パッチ |
| 2026-03-06 | 量産スクリプト3本（redeploy/batch/cron）|
| 2026-03-06 | レビュー修正8件反映（Critical3+Medium2+追加3）|
| 2026-03-06 | 20本バッチ投入（PID=13097）|
| 2026-03-06 | **品質改善v2**: 長尺化15-20分/サムネ黒+白+黄/SEO最適化/フック強化/チャプター自動生成/AI表記追加 |
| 2026-03-06 | **v2 EC2デプロイ完了**: groq 0.4.2→1.0.0/テスト1本成功(158MB)/10本バッチ投入 |
