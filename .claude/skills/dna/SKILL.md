---
name: dna
description: "Modify the company DNA document with dated additions."
user-invocable: true
argument-hint: "<修正指示>"
---
あなたはAI会社のDNA管理者です。以下の手順で company/DNA.md を更新してください。

## 修正指示
$ARGUMENTS

## 手順

### 1. 現在のDNAを読む
`company/DNA.md` をReadツールで読み込む。

### 2. 追記案を生成
修正指示に基づいて、「##追記履歴」セクションに追記する内容を決定する。

追記フォーマット:
```
### YYYY-MM-DD 追記
- 内容: （修正指示の要約）
- 詳細: （必要に応じて）
```

### 3. 反映
Editツールで `company/DNA.md` の「##追記履歴」セクションの末尾（`<!-- /dna コマンドによる追記はここに日付付きで追加される -->`の直前）に追記する。

もし修正指示がValues やMission などの既存セクションの変更を求めている場合は、該当セクションも修正する。

### 4. 報告
- 追記した内容を表示
- 変更箇所を明示

## 注意事項
- 既存の内容を不用意に削除しない
- 追記は必ず日付付き
- DNA の核心的な価値観を変更する場合は、変更理由を追記履歴に明記する
