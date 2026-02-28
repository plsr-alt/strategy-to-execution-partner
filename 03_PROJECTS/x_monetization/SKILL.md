---
name: x-research-skills
description: X(旧Twitter)の特定トピックを自動調査し、トレンドのクラスター抽出から投稿素材リスト(Markdown)の作成までを一気通貫で行うCLIツール。
args:
  - name: topic
    type: string
    description: "必須。調査したいメイントピック（例: 'AI developer tools', 'LLM Agents'）"
  - name: options
    type: string
    description: "追加のオプション群。例: '--hours 24 --count 10 --lang ja --mode balanced --out path/to/res.md'"
---

# `x-research-skills (xrs)` スキルガイド

Claude Code は、ユーザーから「〜についてXでリサーチして」「〜の最近の話題をまとめてブログネタを出して」といったリクエストを受けた際、このスキルを利用して自律的な調査を実行してください。

## 実行方法

本プロジェクトのルートディレクトリ(`c:\Users\tshibasaki\Desktop\etc\work\task\03_PROJECTS\x_monetization`)にて、CLIツールを実行します。

推奨されるコマンドの組み立て方:
```bash
# TypeScript実行環境(tsx)を利用して直接実行する場合
npx tsx src/cli.ts run --topic "{topic}" {options}
```

### 推奨コマンド例
ユーザーが「最近のClaudeのユースケースについて12個のネタを日本語で作って」と依頼してきた場合：
```bash
npx tsx src/cli.ts run --topic "Claude 3.5 Sonnet Use Cases" --hours 48 --count 12 --lang ja --out outputs/claude_usecases.md
```

## Claudeへの指示（システムプロンプト的解釈）

1. **トピックの抽象化**: ユーザーからの漠然とした指示（例:「仮想通貨の最近の話題」）を、CLIに渡す際により検索しやすい具体的な `--topic`（例: "Crypto trends OR Bitcoin OR Web3"）に翻訳してください。
2. **オプションの自動補完**: 
   - トレンドが早そうな話題は `--hours 24`、ニッチな話題は `--hours 72` を設定してください。
   - ユーザーがファイル保存を明示していない場合でも、ターミナルのログが流れるのを防ぐため、原則 `--out` オプションを使用してマークダウンファイル（例: `research_result.md`）として出力してください。
3. **実行後のフォロー**: CLIの実行が完了し Markdown ファイルが生成されたら、そのファイルを読み込み、ユーザーに対して「このような切り口のトレンドが見つかりました。この中の〇〇番のネタを使って、実際にツイート原稿を書きましょうか？」と提案してください。

## トラブルシュート
- **APIキーエラー**: `XAI_API_KEY environment variable is missing` と出た場合、`.env`ファイルが存在するか確認してください。
- **結果が0件**: 対象言語(`--lang`)や時間が狭すぎる可能性があります。`--hours` を拡張するか、`--lang` を `en` に変えて再試行してください。
