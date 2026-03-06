# WBS: 金融チャンネルYouTube動画の量産体制構築

## タスク概要
EC2上でYouTube動画を1日3本自動生成・アップロードする量産体制を構築する。
スポットインスタンス消失後の再デプロイを即実行できる状態にし、cronで毎日JST9:00に自動バッチ起動させる。

## complexity
standard（researcher → structurer → drafter → critic → editor）

---

## 前提・制約（開発部文脈）

| 項目 | 詳細 |
|------|------|
| 既存コード | `youtube_pipeline.py`（8ステップ全自動）・`run_pipeline.sh`・`ec2-setup.sh` を変更しない |
| 出力先 | `C:/Users/tshibasaki/Desktop/etc/work/task/03_PROJECTS/youtube_automation/` |
| EC2環境 | Amazon Linux 2 / ec2-user / t4g.medium / 18.183.153.86 |
| venv | `~/venv/` に構築済み（消失時は ec2-setup.sh で再構築） |
| VOICEVOX | Docker コンテナ `voicevox` / ポート 50021 |
| 認証情報 | EC2パスワード: Welcome1234!（変数化してスクリプトに埋め込む） |
| 転送ツール | sshpass + scp / WSLから実行 |
| セキュリティ | .env・token.json はgit管理外。スクリプトにパスワードをハードコードしない（変数化）|
| コード整合性 | run_pipeline.sh の呼び出し方・ログパス(~/youtube_automation/out/)を既存コードと合わせる |

---

## WBS（ワーク分解構造）

### Phase 1: 調査・既存コード把握
**担当**: worker-researcher
- run_pipeline.sh の呼び出し仕様確認（set -e あり → 失敗時に即exit）
- ec2-setup.sh の転送対象ファイル一覧確認
- EC2上の想定ディレクトリ構造確認
- batch_produce.sh でset -eを外す設計根拠の確認
- cron UTC/JST変換確認（JST 9:00 = UTC 0:00）
- sshpass + scpのWSLコマンド書式確認

**出力**: `20_worker_outputs/01_research.md`

---

### Phase 2: 構造設計
**担当**: worker-structurer
- 3スクリプトの設計図・引数・ログ仕様の整理
- redeploy_ec2.sh：転送対象ファイルリスト、SSH変数定義、実行順序
- batch_produce.sh：エラー耐性ロジック（set +e、成功カウンタ）、待機時間設計
- setup_cron.sh：cronの冪等性（既存エントリ削除→再追加）、VOICEVOX起動確認
- ログ設計：batch_produce.sh が ~/youtube_automation/logs/YYYY-MM-DD.log に出力

**出力**: `20_worker_outputs/02_structure.md`

---

### Phase 3: スクリプト実装（3本）
**担当**: worker-drafter × 3（並列）

#### 3a: redeploy_ec2.sh
- WSLから実行するssh/scp転送スクリプト
- IP・ユーザー・パスワードを先頭で変数定義
- 転送対象: youtube_pipeline.py, requirements.txt, run_pipeline.sh, ec2-setup.sh, groq_executor.py, token.json, .env
- 転送後: pip install -r requirements.txt（venv内）
- VOICEVOX Docker起動確認（未起動なら起動）
- 動作確認: python3 youtube_pipeline.py --help 等
- 出力: `20_worker_outputs/redeploy_ec2.sh`

#### 3b: batch_produce.sh（EC2上で実行）
- set +e（1本失敗しても次へ）
- run_pipeline.sh を3回ループ呼び出し
- 各動画間に300秒待機（APIレートリミット考慮）
- 日付付きログ: ~/youtube_automation/logs/$(date +%Y-%m-%d).log
- 成功/失敗カウンタで完了サマリー出力
- 出力: `20_worker_outputs/batch_produce.sh`

#### 3c: setup_cron.sh（EC2上で実行）
- ログディレクトリ作成（~/youtube_automation/logs/）
- 既存cron（batch_produce.sh関連）を削除してから再追加（冪等性）
- UTC 0:00（JST 9:00）に batch_produce.sh を起動
- VOICEVOX Docker起動をcron内にも含める（@reboot）
- 出力: `20_worker_outputs/setup_cron.sh`

---

### Phase 4: レビュー・品質チェック
**担当**: worker-critic

チェック項目:
- [ ] run_pipeline.sh の `set -e` との整合（batch内でのエラー扱い）
- [ ] WSLパス vs Linuxパスの混在なし
- [ ] sshpassコマンドの書式正確性
- [ ] cronのUTC/JSTが正しいか（0 0 * * *）
- [ ] .envとtoken.jsonの転送漏れなし
- [ ] VOICEVOX起動確認コマンドの正確性（docker inspect or curl）
- [ ] ログディレクトリの作成タイミング（先に mkdir -p）
- [ ] セキュリティ：パスワードを引数or変数で受け取る（ハードコード禁止）

**出力**: `20_worker_outputs/04_review.md`

---

### Phase 5: 修正・最終出力
**担当**: worker-editor

- criticの指摘を反映した3スクリプトの最終版を出力
- 出力先: `20_worker_outputs/` に最終版を配置
- 使い方コメント（ヘッダコメント）を各スクリプトに記載
- 実行権限コマンド（chmod +x）の記載

**出力**: `20_worker_outputs/final_redeploy_ec2.sh`, `final_batch_produce.sh`, `final_setup_cron.sh`

---

## 統合計画（merge_plan）

manager（私）が `20_worker_outputs/` を読み、以下を行う:

1. 3スクリプトの最終版を確認
2. 既存コード（run_pipeline.sh, ec2-setup.sh）との整合性を最終チェック
3. `03_PROJECTS/youtube_automation/` に配置すべきファイルを `80_manager_output.md` に整理
4. 「70点の成果物」+「残り30点の改善ポイント」を記載

**最終出力ファイル**: `80_manager_output.md`

---

## ファイル構成（最終的に 03_PROJECTS/youtube_automation/ に追加するファイル）

```
03_PROJECTS/youtube_automation/
├── redeploy_ec2.sh      ← 新規（WSLから実行）
├── batch_produce.sh     ← 新規（EC2上で実行）
└── setup_cron.sh        ← 新規（EC2上で実行）
```

---

## タイムライン

| Phase | 担当 | 主な成果物 |
|-------|------|-----------|
| 1 研究 | worker-researcher | 01_research.md |
| 2 構造化 | worker-structurer | 02_structure.md |
| 3a drafter | worker-drafter | redeploy_ec2.sh |
| 3b drafter | worker-drafter | batch_produce.sh |
| 3c drafter | worker-drafter | setup_cron.sh |
| 4 レビュー | worker-critic | 04_review.md |
| 5 編集 | worker-editor | final_*.sh × 3本 |
| 統合 | manager | 80_manager_output.md |
