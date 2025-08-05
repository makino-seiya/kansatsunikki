# 植物成長記録アプリ - システム構成ドキュメント

## 概要
植物成長記録アプリケーションのシステム全体の構成とメソッドを整理したドキュメントです。

---

## バックエンド構成 (FastAPI)

### ファイル: `backend/main.py`

### 1. システム管理API

#### ヘルスチェック
- `GET /` - ルートエンドポイント
- `GET /health` - ヘルスチェック
- `startup_event()` - データベース初期化処理

### 2. 植物管理API

#### 植物一覧取得
- `GET /api/plants`
- 機能: アクティブな植物の一覧を取得
- 戻り値: `[{id, name, display_order}]`

### 3. 記録管理API

#### 記録一覧取得
- `GET /api/records`
- 機能: 全ての記録を植物データと共に取得
- 戻り値: 記録配列（日付降順）

#### 今日の記録確認
- `GET /api/records/today`
- 機能: 今日の記録が存在するかチェック
- 戻り値: `{exists: boolean, record?: object}`

#### 記録作成
- `POST /api/records`
- 機能: 新しい記録を作成
- 入力: `{weather, temperature, plantRecords}`
- バリデーション: 今日の記録重複チェック

#### 記録更新
- `PUT /api/records/{record_id}`
- 機能: 既存の記録を更新
- 入力: `{weather?, temperature?, date?, plants?}`

#### 記録削除
- `DELETE /api/records/{record_id}`
- 機能: 記録を削除（植物記録も連動削除）

### 4. 画像管理API

#### 画像アップロード
- `POST /api/upload/image`
- 機能: 画像をMinIOにアップロード
- バリデーション: ファイル形式・サイズチェック（3MB以下）
- 戻り値: `{filename, url}`

#### 画像URL取得
- `GET /api/images/{filename}`
- 機能: 画像のURLを取得
- 戻り値: `{url}`

---

## フロントエンド構成 (Nuxt.js/Vue.js)

### 1. メインページ (`frontend/pages/index.vue`)

#### データ管理メソッド
- `checkTodayRecord()` - 今日の記録存在確認
- `saveRecord()` - 記録保存処理
- `handleImageUpload()` - 画像アップロード処理

#### ユーティリティメソッド
- `getWeatherIcon()` - 天気アイコン取得
- `getWeatherLabel()` - 天気ラベル取得
- `getPlantNameWithFurigana()` - 植物名（ふりがな付き）取得
- `formatDateTime()` - 日時フォーマット
- `goToEditRecord()` - 編集画面への遷移

#### 算出プロパティ
- `currentDate` - 現在日付（日本語形式）
- `canSave` - 保存可能状態判定

### 2. 記録一覧ページ (`frontend/pages/records.vue`)

#### データ管理メソッド
- `fetchRecords()` - 記録一覧取得
- `editRecord()` - 記録編集開始
- `saveEdit()` - 編集内容保存
- `cancelEdit()` - 編集キャンセル

#### 画像管理メソッド
- `handleImageUpload()` - 新規画像アップロード
- `changeImage()` - 画像変更
- `handleImageChange()` - 画像変更処理
- `removeImage()` - 画像削除
- `handleImageError()` - 画像エラー処理

#### ユーティリティメソッド
- `getWeatherIcon()` - 天気アイコン取得（英語・日本語対応）
- `getWeatherName()` - 天気名取得（英語・日本語対応）
- `getPlantName()` - 植物名取得（英語・日本語対応）
- `getPlantIcon()` - 植物アイコン取得
- `formatDate()` - 日付フォーマット
- `formatDateTime()` - 日時フォーマット

### 3. グラフページ (`frontend/pages/graphs.vue`)

#### データ管理メソッド
- `fetchRecords()` - 記録データ取得
- `processChartData()` - グラフ用データ処理
- `updateCharts()` - 全グラフ更新

#### グラフ作成メソッド
- `createHeightChart()` - 高さ推移グラフ作成
- `createTemperatureChart()` - 気温推移グラフ作成
- `createCombinedChart()` - 複合グラフ作成

#### ユーティリティメソッド
- `getPlantName()` - 植物名取得

---

## データフロー

### 1. 記録作成フロー
```
1. ユーザー入力 (index.vue)
2. 画像アップロード (POST /api/upload/image)
3. 記録保存 (POST /api/records)
4. データベース保存 (Record + PlantRecord)
```

### 2. 記録表示フロー
```
1. 記録取得 (GET /api/records)
2. データ変換・表示 (records.vue)
3. 画像URL生成 (GET /api/images/{filename})
```

### 3. グラフ表示フロー
```
1. 記録取得 (GET /api/records)
2. データ処理・フィルタリング (graphs.vue)
3. Chart.js によるグラフ描画
```

---

## データベース構造

### テーブル構成
- **Record**: メイン記録テーブル
  - id, record_date, weather, temperature, created_at
- **PlantRecord**: 植物別記録テーブル
  - id, record_id, plant_id, height, comment, image_filename
- **Plant**: 植物マスターテーブル
  - id, name, display_order, is_active

### リレーション
- Record 1:N PlantRecord
- Plant 1:N PlantRecord

---

## 外部サービス連携

### MinIO (画像ストレージ)
- アップロード: `minio_client.upload_image()`
- URL取得: `minio_client.get_image_url()`

---

## エラーハンドリング

### バックエンド
- HTTPException による統一エラーレスポンス
- ログ出力による詳細エラー記録
- データベーストランザクション管理

### フロントエンド
- try-catch による例外処理
- ユーザーフレンドリーなエラーメッセージ
- ローディング状態管理

---

## セキュリティ考慮事項

### 入力検証
- ファイルタイプ・サイズ制限
- 数値型バリデーション
- SQLインジェクション対策（ORM使用）

### CORS設定
- 許可オリジン: `http://localhost:3001`
- 認証情報許可: `allow_credentials=True`

---

## パフォーマンス最適化

### データベース
- インデックス設定（日付、植物ID）
- 必要なデータのみ取得

### フロントエンド
- 画像遅延読み込み
- Chart.js インスタンス管理
- 不要な再描画防止

---

## 今後の拡張ポイント

### 機能拡張
- ユーザー認証・管理
- データエクスポート機能
- 通知機能
- 植物種類の動的管理

### 技術的改善
- キャッシュ機能
- リアルタイム更新
- PWA対応
- テスト自動化