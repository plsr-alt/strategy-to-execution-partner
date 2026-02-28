# 実装過程の自動ドキュメント化設計

**作成日**: 2026-02-20
**設計方針**: 人が意識的に記録しなくても記録が溜まる仕組み

---

## 1. 設計思想

```
「記録する」という行動を設計から除去する

やること → 自動でログが生まれる
実験を走らせる → メタデータが自動保存される
PRを作る → ADRテンプレが自動生成される
評価を実行する → 結果サマリが自動集計される
```

---

## 2. ドキュメントカテゴリと保存先

```
03_PROJECTS/runbook_automation/
├── logs/           ← 調査・作業ログ（自動生成）
├── decisions/      ← ADR（PR連動で自動テンプレ生成）
├── experiments/    ← 実験ログ（実験スクリプト実行時に自動保存）
├── validations/    ← 検証結果（評価スクリプト実行時に自動出力）
├── datasets/       ← 評価データセット（PII管理注意）
└── outputs/        ← 集計レポート・デモ出力
```

---

## 3. 調査ログ（logs/）

### ファイル命名規則
```
logs/YYYY-MM-DD_HH-MM_<topic>.md
例: logs/2026-02-20_14-30_textract-accuracy-research.md
```

### テンプレート（logs/_template.md）
```markdown
# 調査ログ: {トピック}

**日時**: {YYYY-MM-DD HH:MM}
**担当**: {名前 or Claude}
**ステータス**: 調査中 / 完了 / 保留

## 収集元
- URL / ドキュメント名 / 実験番号

## 要点（箇条書き）
-

## 判断材料
- この情報が影響する決定:
- 信頼度（高/中/低）:

## 次アクション
-
```

### 自動化フロー
```python
# logs/auto_logger.py（ラッパースクリプト）
# 使い方: python auto_logger.py --topic "textract-accuracy" --run "script.py"
# → 実行前後のログを自動キャプチャしてlogs/に保存

import subprocess, json, datetime, pathlib

def auto_log(topic: str, command: list):
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    log_path = pathlib.Path(f"logs/{ts}_{topic}.md")
    result = subprocess.run(command, capture_output=True, text=True)
    log_path.write_text(f"""# 実行ログ: {topic}
**日時**: {ts}
**コマンド**: {' '.join(command)}
**終了コード**: {result.returncode}

## stdout
```
{result.stdout}
```

## stderr
```
{result.stderr}
```
""")
    return result
```

---

## 4. 意思決定ログ — ADR（decisions/）

### ファイル命名規則
```
decisions/ADR-NNNN_<title>.md
例: decisions/ADR-0001_select-ocr-engine.md
```

### ADRテンプレート（decisions/_template.md）
```markdown
# ADR-NNNN: {タイトル}

**日付**: {YYYY-MM-DD}
**ステータス**: 提案 / 承認 / 廃止 / 置換（→ ADR-XXXX）
**決定者**:

## Context（背景・課題）
どんな状況で、何を決める必要があったか

## Decision（決定内容）
何を選んだか、どうするか

## Options（検討した選択肢）
| 選択肢 | 理由（採用/却下） |
|--------|-----------------|
| A | |
| B | |
| C | |

## Consequences（影響・トレードオフ）
### ポジティブ
-

### ネガティブ（受け入れるリスク）
-

## 関連ファイル
- 実験ログ: experiments/
- 比較資料:
```

### PR連動でADRテンプレを自動生成（GitHub Actions）
```yaml
# .github/workflows/adr-template.yml
name: ADR Template on PR
on:
  pull_request:
    types: [opened]
    paths:
      - 'src/**'
      - 'config/**'

jobs:
  create-adr-template:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Generate ADR template
        run: |
          ADR_NUM=$(ls decisions/ADR-*.md 2>/dev/null | wc -l)
          ADR_NUM=$(printf "%04d" $((ADR_NUM + 1)))
          DATE=$(date +%Y-%m-%d)
          PR_TITLE="${{ github.event.pull_request.title }}"
          FILENAME="decisions/ADR-${ADR_NUM}_$(echo $PR_TITLE | tr ' ' '-' | tr '[:upper:]' '[:lower:]').md"
          cp decisions/_template.md "$FILENAME"
          sed -i "s/NNNN/${ADR_NUM}/g" "$FILENAME"
          sed -i "s/{YYYY-MM-DD}/${DATE}/g" "$FILENAME"
          sed -i "s/{タイトル}/${PR_TITLE}/g" "$FILENAME"
          git add "$FILENAME"
          git commit -m "auto: ADR-${ADR_NUM} template for PR #${{ github.event.pull_request.number }}"
          git push
      - name: Comment on PR
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '📝 ADRテンプレートを自動生成しました。`decisions/ADR-XXXX_*.md` を確認・記入してください。'
            })
```

---

## 5. 実験ログ（experiments/）

### ファイル命名規則
```
experiments/EXP-NNNN_YYYY-MM-DD_<description>.md
例: experiments/EXP-0001_2026-02-21_textract-vs-paddle-accuracy.md
```

### 実験メタデータ自動保存スクリプト
```python
# experiments/run_experiment.py
# 使い方: python run_experiment.py --id EXP-0001 --desc "textract vs paddle" -- python eval.py

import argparse, subprocess, json, datetime, pathlib, platform, sys

def run_experiment():
    parser = argparse.ArgumentParser()
    parser.add_argument('--id', required=True)
    parser.add_argument('--desc', required=True)
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()

    ts = datetime.datetime.now()
    meta = {
        "experiment_id": args.id,
        "description": args.desc,
        "timestamp": ts.isoformat(),
        "python_version": sys.version,
        "platform": platform.platform(),
        "command": args.command[1:],  # -- の後
    }

    start = datetime.datetime.now()
    result = subprocess.run(args.command[1:], capture_output=True, text=True)
    elapsed = (datetime.datetime.now() - start).total_seconds()

    meta["elapsed_sec"] = elapsed
    meta["exit_code"] = result.returncode

    date_str = ts.strftime("%Y-%m-%d")
    fname = f"experiments/{args.id}_{date_str}_{args.desc.replace(' ', '-')}.md"
    pathlib.Path(fname).write_text(f"""# 実験ログ: {args.id}

**説明**: {args.desc}
**実行日時**: {ts.strftime('%Y-%m-%d %H:%M:%S')}
**所要時間**: {elapsed:.1f}秒
**終了コード**: {result.returncode}

## 実験条件
```json
{json.dumps(meta, indent=2, ensure_ascii=False)}
```

## 実行コマンド
```
{' '.join(args.command[1:])}
```

## 結果（stdout）
```
{result.stdout[:5000]}
```

## エラー（stderr）
```
{result.stderr[:2000]}
```

## 考察・次のアクション
（手動記入）

## 再現手順
```bash
{' '.join(args.command[1:])}
```
""")
    print(f"実験ログ保存: {fname}")
    return result.returncode

if __name__ == '__main__':
    sys.exit(run_experiment())
```

---

## 6. 検証テンプレート（validations/）

### テンプレート（validations/_template.md）
```markdown
# 検証記録: {検証ID}

**日付**: {YYYY-MM-DD}
**検証者**:
**対象**: （パイプライン / 特定モジュール）

## 入力
- ファイル:
- 件数:
- 条件:

## 期待値（Expected）
| 項目名 | 期待値 |
|--------|--------|
| | |

## 実際の結果（Actual）
| 項目名 | 実際値 | 一致/不一致 |
|--------|--------|-----------|
| | | |

## 差分・原因
- 差分:
- 原因仮説:

## 対策
- 対策内容:
- 対策後の再検証: 予定日

## ステータス
- [ ] 合格
- [ ] 不合格 → 対策中
- [ ] 条件付き合格
```

### 評価結果の自動集計スクリプト
```python
# validations/aggregate.py
# 使い方: python aggregate.py → validations/summary_YYYY-MM-DD.md を自動生成

import pathlib, datetime, re

def aggregate():
    val_dir = pathlib.Path("validations")
    results = []
    for f in val_dir.glob("*.md"):
        if f.name.startswith("_") or f.name.startswith("summary"):
            continue
        content = f.read_text()
        status = "不明"
        if "- [x] 合格" in content:
            status = "合格"
        elif "- [x] 不合格" in content:
            status = "不合格"
        elif "- [x] 条件付き" in content:
            status = "条件付き"
        results.append({"file": f.name, "status": status})

    total = len(results)
    passed = sum(1 for r in results if r["status"] == "合格")
    date = datetime.date.today().isoformat()

    summary = f"""# 検証結果サマリ
**集計日**: {date}
**合格率**: {passed}/{total} ({100*passed//total if total else 0}%)

| ファイル | ステータス |
|---------|----------|
"""
    for r in results:
        summary += f"| {r['file']} | {r['status']} |\n"

    out = val_dir / f"summary_{date}.md"
    out.write_text(summary)
    print(f"サマリ出力: {out}")

if __name__ == '__main__':
    aggregate()
```

---

## 7. Git運用・変更履歴

### ブランチ戦略
```
main          ← 本番相当（直接pushなし）
develop       ← 統合ブランチ
feature/XXX   ← 機能開発
experiment/XXX ← 実験（失敗してもmainに影響なし）
```

### タグ・リリースノート自動化
```bash
# scripts/release.sh
# 使い方: bash scripts/release.sh v0.1.0 "Textract統合完了"
VERSION=$1
DESCRIPTION=$2
git tag -a "$VERSION" -m "$DESCRIPTION"
echo "## $VERSION - $(date +%Y-%m-%d)" >> CHANGELOG.md
echo "$DESCRIPTION" >> CHANGELOG.md
echo "" >> CHANGELOG.md
git add CHANGELOG.md && git commit -m "chore: release $VERSION"
git push origin "$VERSION"
```

### コミットメッセージ規約
```
feat:    新機能
fix:     バグ修正
exp:     実験
docs:    ドキュメント（自動生成除く）
refactor: リファクタリング
test:    テスト追加
chore:   雑務（依存更新・設定変更）
```

---

## 8. datasets/ の取り扱い注意事項

```
⚠️ datasets/ にはPIIを含む可能性があります。以下を厳守してください。

□ PIIは必ずマスキングしてから保存（氏名→★★★、口座番号→****）
□ .gitignore に datasets/ を追加（Gitへのコミット禁止）
□ S3保存時はSSE-KMS必須
□ アクセスは特定IAMロールのみ
□ 保管期間ポリシーを明示（例: PoC終了後30日で削除）
```

```
# .gitignore に追加必須
datasets/
*.csv
*.json  # 出力JSONも除外
```

---

## 9. 最小自動化フローまとめ

| イベント | 自動で起きること | スクリプト/ツール |
|---------|----------------|----------------|
| PRオープン | ADRテンプレ生成 + PRコメント | GitHub Actions |
| 実験スクリプト実行 | 実験ログ自動保存 | run_experiment.py |
| 検証結果チェック | サマリMarkdown自動生成 | aggregate.py |
| 評価コード実行 | 精度ログをexperiments/に保存 | auto_logger.py |
| リリースタグ付与 | CHANGELOGに自動追記 | release.sh |
| PoC週次完了 | 週次レポートテンプレ生成 | （Lambda/cron） |
