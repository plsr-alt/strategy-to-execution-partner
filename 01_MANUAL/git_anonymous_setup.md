# Git 匿名コミット・PR 設定手順

## 現在の設定（このリポジトリ）

```
git config --local user.name "plsr-alt"
git config --local user.email "plsr-alt@users.noreply.github.com"
```

→ `--local` なのでこのリポジトリのみ有効。他のリポジトリには影響しない。

---

## 新しいリポジトリでの設定手順

```bash
# 1. リポジトリのローカル設定を変更
git config --local user.name "plsr-alt"
git config --local user.email "plsr-alt@users.noreply.github.com"

# 2. 確認
git config --local user.name
git config --local user.email
```

---

## 過去のコミットを匿名に書き換える（git-filter-repo）

```bash
# WSL で実行
pip3 install --user --break-system-packages git-filter-repo

# mailmap で一括書き換え
export PATH=/root/.local/bin:$PATH
cd /mnt/c/Users/tshibasaki/Desktop/etc/work/task

git-filter-repo --mailmap <(echo '
plsr-alt <plsr-alt@users.noreply.github.com> 旧名前 <旧メール>
') --force

# remote が消えるので再追加
git remote add origin https://github.com/plsr-alt/strategy-to-execution-partner
git push --force --all origin
```

---

## GitHub側の設定（推奨）

1. GitHub Settings → Emails → 「Keep my email addresses private」をON
2. GitHub Settings → Emails → 「Block command line pushes that expose my email」をON
3. → これで `plsr-alt@users.noreply.github.com` が自動的に使われる

---

## PR作成（gh CLIなし・API直接）

```bash
# WSL から curl で PR 作成
curl -s -X POST \
  -H "Authorization: token <TOKEN>" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/plsr-alt/strategy-to-execution-partner/pulls \
  -d '{
    "title": "PRタイトル",
    "head": "feature/ブランチ名",
    "base": "master",
    "body": "PR本文"
  }'

# マージ
curl -s -X PUT \
  -H "Authorization: token <TOKEN>" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/plsr-alt/strategy-to-execution-partner/pulls/<PR番号>/merge \
  -d '{"merge_method": "squash"}'
```

---

## 注意事項

- `git config --global` は変更しない（本業リポジトリに影響するため）
- `--local` のみ使用する
- force push 前に全ブランチの状態を確認する
- filter-repo は remote を自動削除するので、実行後に `git remote add origin` が必要
