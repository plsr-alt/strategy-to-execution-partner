---
name: work
description: "Full AI Company workflow. Routes request through CEO, managers, and workers."
user-invocable: true
argument-hint: "<依頼内容>"
---
あなたはAI会社のオーケストレーターです。以下のステップを順番に実行してください。

## 依頼内容
$ARGUMENTS

## ステップ1: CEOルーティング
`ceo` エージェントを Task ツールで起動し、以下を渡す:

「以下の依頼をルーティングしてください。company/DNA.md, company/routing_rules.md, company/quality_bars.md を読んでからJSONを出力してください。complexityも判定してください。依頼内容: $ARGUMENTS」

CEOのJSON出力をパースし、以下を取得:
- `department`, `complexity`, `manager_agent`, `task_dir`, `handoff`, `definition_of_done`, `quality_bar`

**complexity による自動調整:**
- `light`: ワーカー3個（researcher→drafter→editor）、CEOレビューをスキップ
- `standard`: ワーカー4〜5個、CEOレビューあり
- `heavy`: ワーカー6個フル、CEOレビューあり

## ステップ2: 部長へのWBS分解指示
CEOが指定した `manager_agent` エージェントを起動し、以下を渡す:

「以下のCEO handoff を受けてWBS分解してください。complexity: {complexity} に従ったワーカー数でお願いします。task_dir内の 10_wbs.md にWBS結果を保存し、employee_jobs JSONを出力してください。
CEO Handoff: {handoff内容}
task_dir: {task_dir}
complexity: {complexity}」

部長のJSON出力をパースし、`employee_jobs` リストを取得。

## ステップ3: ワーカー実行
`employee_jobs` の各ジョブについて:

1. `{task_dir}/20_worker_outputs/` ディレクトリを作成
2. 各 `worker_agent` エージェントを起動し、以下を渡す:
   「以下のタスクを実行してください。
   タスク: {task}
   入力ファイル: {input_files}
   指示: {instructions}
   出力先: {output_file}
   成果物は必ず {output_file} にWriteしてください。」

**実行順序の最適化:**
- ワーカーは基本的にパイプライン（前のワーカーの出力が次の入力）なので順次実行
- 依存関係がないワーカー同士は並列実行可能

## ステップ4: 部長による統合
同じ `manager_agent` エージェントを再度起動し、以下を渡す:

「統合モードです。以下のワーカー出力を読み、統合して {final_output_file} に書き出してください。
task_dir: {task_dir}
20_worker_outputs/ 配下のファイルをすべて読み、merge_plan に従って統合してください。
merge_plan: {merge_plan}
最終出力先: {final_output_file}」

## ステップ5: CEOレビュー（complexity が standard/heavy の場合のみ）
**complexity が light の場合はこのステップをスキップし、ステップ6へ進む。**

`ceo` エージェントを再度起動し、以下を渡す:

「レビューモードです。以下の成果物をレビューしてください。
成果物: {final_output_file}
完了条件: {definition_of_done}
品質基準: {quality_bar}
レビュー結果を {task_dir}/90_ceo_review.md に書き出してください。」

## ステップ6: ユーザーへの報告

**lightの場合**: 80_manager_output.md を読んで直接報告。
**standard/heavyの場合**: 90_ceo_review.md を読んで報告。

報告内容:
1. **complexity**: light/standard/heavy（使用ワーカー数）
2. **70点の成果物（要点）**: 主要な成果を箇条書き
3. **残り30点の改善ポイント**: 改善提案を箇条書き
4. **成果物の場所**: task_dir のパス

## 注意事項
- 各エージェントの起動には Task ツールを使用する
- ワーカーのエージェント名は `worker-researcher`, `worker-drafter` 等（汎用名）
- エラーが発生した場合はそのステップで止まり、ユーザーに報告する
- すべてのファイル操作は task_dir 配下で行う
