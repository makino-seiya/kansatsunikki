# 設計書

## 概要

植物成長記録アプリは、子供が植物の成長を記録・管理できるWebアプリケーションです。スマホ対応のタブナビゲーション（入力・一覧・グラフ）を持つユーザー画面と、ID/パスワード認証による管理画面で構成されます。

## アーキテクチャ

### システム構成

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (Nuxt/Vue)    │◄──►│   (FastAPI)     │◄──►│   (MySQL 8)     │
│                 │    │                 │    │                 │
│ - User UI       │    │ - REST API      │    │ - Records       │
│ - Admin UI      │    │ - Auth          │    │ - Plants        │
│ - Charts        │    │ - File Upload   │    │ - Users         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Docker環境構成

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Docker Compose                                   │
├─────────────┬─────────────┬─────────────┬─────────────────────────────────┤
│  frontend   │   backend   │  database   │           minio                 │
│ (Nuxt/Vue)  │  (FastAPI)  │ (MySQL 8)   │      (Object Storage)           │
│ Port: 3001  │ Port: 8001  │ Port: 3307  │ API: 9002, Console: 9003        │
└─────────────┴─────────────┴─────────────┴─────────────────────────────────┘
```

## コンポーネントとインターフェース

### フロントエンド構成

#### ユーザー画面（/）- Basic認証保護
- **Basic認証**: 全ユーザー画面へのアクセス制限
- **タブナビゲーション**: 画面下部固定
  - 入力タブ: 記録入力フォーム
  - 一覧タブ: 記録一覧（植物種類絞り込み機能付き）
  - グラフタブ: 成長グラフ（植物種類絞り込み機能付き）

#### 管理画面（/admin/）- SQLAdmin使用
- **認証画面**: ID/パスワードログイン（SQLAdmin内蔵認証）
- **ダッシュボード**: 記録統計・概要（カスタムダッシュボード）
- **記録管理**: 全記録の一覧・編集・削除（自動CRUD画面）
- **植物種類管理**: 植物種類の追加・編集・削除（自動CRUD画面）
- **画像プレビュー**: MinIO画像の表示機能

### バックエンドAPI設計

#### 認証API
```
POST /api/auth/login
POST /api/auth/logout
GET  /api/auth/me
```

#### 管理画面（SQLAdmin）
```
GET  /admin/           # SQLAdmin管理画面
POST /admin/login      # SQLAdmin認証
GET  /admin/records    # 記録管理画面
GET  /admin/plants     # 植物種類管理画面
```

#### 記録管理API
```
GET    /api/records          # 記録一覧取得（フィルタ機能付き）
POST   /api/records          # 新規記録作成
GET    /api/records/{id}     # 特定記録取得
PUT    /api/records/{id}     # 記録更新
DELETE /api/records/{id}     # 記録削除
```

#### 植物種類管理API
```
GET    /api/plants           # 植物種類一覧取得
POST   /api/plants           # 植物種類作成
PUT    /api/plants/{id}      # 植物種類更新
DELETE /api/plants/{id}      # 植物種類削除
```

#### ファイルアップロードAPI
```
POST   /api/upload/image     # 画像アップロード（MinIOに保存）
GET    /api/images/{filename} # 画像取得（MinIOから読み込み）
```

## データモデル

### データベーススキーマ

#### users テーブル
```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### plants テーブル
```sql
CREATE TABLE plants (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    display_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### records テーブル
```sql
CREATE TABLE records (
    id INT PRIMARY KEY AUTO_INCREMENT,
    record_date DATE NOT NULL UNIQUE,  -- 日付の重複を防ぐ
    weather ENUM('sunny', 'cloudy', 'rainy', 'thunder') NOT NULL,
    temperature DECIMAL(4,1) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_record_date (record_date)
);
```

#### plant_records テーブル
```sql
CREATE TABLE plant_records (
    id INT PRIMARY KEY AUTO_INCREMENT,
    record_id INT NOT NULL,
    plant_id INT NOT NULL,
    height DECIMAL(5,1),
    image_filename VARCHAR(255),  -- MinIOでのファイル名
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (record_id) REFERENCES records(id) ON DELETE CASCADE,
    FOREIGN KEY (plant_id) REFERENCES plants(id) ON DELETE CASCADE,
    INDEX idx_record_plant (record_id, plant_id)
);
```

### データ関係図

```
records (1) ──── (N) plant_records (N) ──── (1) plants
   │                                              │
   │ record_date                                  │ name
   │ weather                                      │ display_order
   │ temperature                                  │ is_active
   │                                              │
   └─ plant_records                               │
      │ height                                    │
      │ image_filename ──────► MinIO             │
      │ comment                (plant-images)     │
```

## エラーハンドリング

### フロントエンド
- **ネットワークエラー**: 再試行機能付きエラー表示
- **バリデーションエラー**: フィールド単位でのエラー表示
- **重複記録エラー**: 既存記録がある日付での保存時のエラー表示
- **認証エラー**: ログイン画面へのリダイレクト
- **ファイルアップロードエラー**: プログレス表示とエラー通知

### バックエンド
- **HTTPステータスコード**: 適切なステータスコードの返却
- **エラーレスポンス形式**:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "入力データに問題があります",
    "details": {
      "field": "temperature",
      "message": "気温は-50〜50の範囲で入力してください"
    }
  }
}
```

### データベース
- **制約違反**: 適切なエラーメッセージでの応答
- **接続エラー**: 自動再接続とログ出力
- **トランザクション**: データ整合性の保証

## テスト戦略

### フロントエンドテスト
- **単体テスト**: Vue Test Utils + Jest
  - コンポーネントの動作確認
  - バリデーション機能のテスト
- **E2Eテスト**: Playwright
  - ユーザーフローの確認
  - タブナビゲーションの動作確認

### バックエンドテスト
- **単体テスト**: pytest
  - API エンドポイントのテスト
  - データベース操作のテスト
- **統合テスト**: TestClient
  - 認証フローのテスト
  - ファイルアップロードのテスト

### データベーステスト
- **マイグレーションテスト**: スキーマ変更の確認
- **パフォーマンステスト**: インデックス効果の確認

## セキュリティ考慮事項

### 認証・認可
- **Basic認証**: ユーザー画面（/以下）への簡易アクセス制限
- **管理者認証**: ID/パスワードによる管理画面認証
- **パスワードハッシュ化**: bcrypt使用
- **セッション管理**: JWT トークン使用（管理画面）
- **CSRF対策**: CSRFトークンの実装

### ファイルアップロード（MinIO）
- **ファイル形式制限**: 画像ファイルのみ許可（JPEG, PNG, WebP）
- **ファイルサイズ制限**: 最大3MB（アップロード前検証）
- **画像圧縮**: ブラウザ側でCanvas APIを使用した圧縮処理
- **植物別制限**: 各植物につき1枚の写真のみ
- **差し替え機能**: 既存写真の削除と新規アップロード
- **ファイル名サニタイズ**: UUID + 拡張子での保存
- **バケット構成**: `plant-images` バケットに保存
- **アクセス制御**: パブリック読み取り、認証済み書き込み

### データ保護
- **SQLインジェクション対策**: ORM使用
- **XSS対策**: 入力値のエスケープ処理
- **入力値検証**: フロントエンド・バックエンド両方で実装

## パフォーマンス最適化

### フロントエンド
- **画像最適化**: WebP形式での保存・表示
- **レイジーローディング**: 画像の遅延読み込み
- **キャッシュ戦略**: ブラウザキャッシュの活用

### バックエンド
- **データベースインデックス**: 検索性能の最適化
- **ページネーション**: 大量データの分割取得
- **画像リサイズ**: アップロード時の自動リサイズ

### データベース
- **クエリ最適化**: N+1問題の回避
- **接続プール**: 効率的な接続管理

### MinIO設定
- **バケット**: `plant-images` バケットの自動作成
- **アクセスキー**: 開発環境用の固定キー設定
- **画像配信**: 直接URL配信またはプロキシ経由配信
- **データ永続化**: Docker Volumeによる永続化
- **バックアップ**: 開発環境では不要、本番環境では別途検討

### SQLAdmin設定
- **自動CRUD**: SQLAlchemyモデルから管理画面を自動生成
- **認証統合**: 既存のユーザーテーブルとの統合
- **カスタムビュー**: ダッシュボードとグラフ表示のカスタム画面
- **画像表示**: MinIO画像のプレビュー機能
- **日本語化**: 管理画面の日本語対応