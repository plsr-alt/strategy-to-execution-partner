# Plugin Hub — SPEC.md

## 技術スタック
| レイヤー | 技術 |
|---------|------|
| フレームワーク | Next.js 14 (App Router) |
| 言語 | TypeScript |
| スタイル | Tailwind CSS |
| ORM | Prisma |
| DB | SQLite（ローカル開発に最適） |
| 認証 | NextAuth.js (Credentials Provider) |
| UI | shadcn/ui 系の自前コンポーネント |

## 画面一覧

### ユーザー向け
| 画面 | パス | 機能 |
|------|------|------|
| トップ | `/` | ヒーロー + 人気プラグイン + カテゴリ一覧 |
| プラグイン一覧 | `/plugins` | 検索・カテゴリフィルタ・一覧表示 |
| プラグイン詳細 | `/plugins/[id]` | 詳細情報・スクショ・お気に入りボタン |
| ログイン | `/login` | メール+パスワード認証 |
| お気に入り | `/favorites` | ログインユーザーのお気に入り一覧 |

### 管理画面
| 画面 | パス | 機能 |
|------|------|------|
| ダッシュボード | `/admin` | 統計サマリー |
| プラグイン管理 | `/admin/plugins` | 一覧・追加・編集・削除 |
| プラグイン編集 | `/admin/plugins/[id]` | フォームで編集 |
| カテゴリ管理 | `/admin/categories` | カテゴリCRUD |

## データモデル

### User
| カラム | 型 | 説明 |
|--------|-----|------|
| id | String (cuid) | PK |
| email | String | ユニーク |
| password | String | ハッシュ化 |
| name | String | 表示名 |
| role | Enum (USER/ADMIN) | 権限 |
| createdAt | DateTime | 作成日時 |

### Plugin
| カラム | 型 | 説明 |
|--------|-----|------|
| id | String (cuid) | PK |
| name | String | プラグイン名 |
| description | String | 説明文 |
| author | String | 作者名 |
| imageUrl | String? | サムネイル画像URL |
| figmaUrl | String? | Figma Community リンク |
| categoryId | String | FK → Category |
| tags | String | カンマ区切りタグ |
| featured | Boolean | おすすめフラグ |
| createdAt | DateTime | 作成日時 |
| updatedAt | DateTime | 更新日時 |

### Category
| カラム | 型 | 説明 |
|--------|-----|------|
| id | String (cuid) | PK |
| name | String | カテゴリ名 |
| slug | String | URLスラッグ |
| description | String? | 説明 |
| icon | String? | アイコン絵文字 |

### Favorite
| カラム | 型 | 説明 |
|--------|-----|------|
| id | String (cuid) | PK |
| userId | String | FK → User |
| pluginId | String | FK → Plugin |
| createdAt | DateTime | 作成日時 |

## API Routes

| メソッド | パス | 用途 |
|---------|------|------|
| GET | `/api/plugins` | プラグイン一覧（検索・フィルタ対応） |
| GET | `/api/plugins/[id]` | プラグイン詳細 |
| POST | `/api/plugins` | プラグイン作成（admin） |
| PUT | `/api/plugins/[id]` | プラグイン更新（admin） |
| DELETE | `/api/plugins/[id]` | プラグイン削除（admin） |
| GET | `/api/categories` | カテゴリ一覧 |
| POST | `/api/categories` | カテゴリ作成（admin） |
| POST | `/api/favorites` | お気に入り追加/解除 |
| GET | `/api/favorites` | お気に入り一覧 |

## 認証設計
- NextAuth Credentials Provider
- bcrypt でパスワードハッシュ化
- セッションにrole含める（admin判定用）
- 管理画面はmiddlewareでADMINロール必須

## デザイン方針
- ダークテーマベース（Figmaっぽい）
- カード型レイアウト
- レスポンシブ対応
- アニメーション控えめ・操作感重視
