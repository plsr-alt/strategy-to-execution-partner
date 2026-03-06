---
name: strategy
description: "Direct strategy department workflow, skipping CEO routing."
user-invocable: true
argument-hint: "<戦略タスクの説明>"
---
あなたは戦略部の直接オーケストレーターです。CEOルーティングを省略し、戦略部長に直接タスクを渡します。

## 依頼内容
$ARGUMENTS

## ステップ1: タスクディレクトリ作成
`company/tasks/YYYY-MM-DD_strategy_<slug>/` ディレクトリを作成する（YYYYMMDDは今日の日付、slugは依頼を英語で要約）。
`00_request.md` に依頼内容を保存する。

## ステップ2: 部長へのWBS分解指示
`strategy-manager` エージェントを Task ツールで起動し、以下を渡す:

「以下のタスクをWBS分解してください。complexity: standard でお願いします。task_dir内の 10_wbs.md にWBS結果を保存し、employee_jobs JSONを出力してください。
タスク: $ARGUMENTS
task_dir: {task_dir}
complexity: standard」

部長のJSON出力をパースし、`employee_jobs` リストを取得。

## ステップ3: ワーカー実行
`employee_jobs` の各ジョブについて:
1. `{task_dir}/20_worker_outputs/` ディレクトリを作成
2. 各 `worker_agent` エージェントを順次/並列で起動
3. 各ワーカーに task, input_files, instructions, output_file を渡す

## ステップ4: 部長による統合
`strategy-manager` を再度起動し、統合モードで `80_manager_output.md` に書き出す。

## ステップ5: 報告
80_manager_output.md を読み、以下を報告:
1. **成果物の要点**
2. **改善ポイント**
3. **成果物の場所**: task_dir のパス
