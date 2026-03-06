# Plugin Hub

Figmaプラグインのキュレーション型ギャラリーWebアプリ。

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **ORM**: Prisma
- **Database**: SQLite
- **Auth**: NextAuth.js (Credentials)

## Getting Started

```bash
# 依存関係インストール
npm install

# Prisma Client生成 & DB作成
npx prisma generate
npx prisma db push

# シードデータ投入
npx prisma db seed

# 開発サーバー起動
npm run dev
```

http://localhost:3000 でアクセス。

## テストアカウント

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@pluginhub.dev | admin123 |
| User | user@pluginhub.dev | user1234 |

## 画面一覧

### ユーザー向け
| 画面 | パス | 機能 |
|------|------|------|
| トップ | `/` | ヒーロー + Featured + カテゴリ一覧 |
| プラグイン一覧 | `/plugins` | 検索・カテゴリフィルタ |
| プラグイン詳細 | `/plugins/[id]` | 詳細・お気に入り |
| お気に入り | `/favorites` | ログインユーザーのお気に入り |
| ログイン | `/login` | メール+パスワード認証 |
| ユーザー登録 | `/register` | 新規アカウント作成 |

### 管理画面
| 画面 | パス | 機能 |
|------|------|------|
| ダッシュボード | `/admin` | 統計サマリー |
| プラグイン管理 | `/admin/plugins` | CRUD・Featured切替 |
| カテゴリ管理 | `/admin/categories` | インライン編集 |

## DB操作

```bash
# DBリセット（全データ削除→再シード）
npm run db:reset

# Prisma Studio（DB GUIブラウザ）
npx prisma studio
```

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new).

Check out [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
