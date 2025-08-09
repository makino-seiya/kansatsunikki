# Serena 向けセットアップ手順

このプロジェクトでのローカル環境を最短で整えるための手順です。

## 前提
- Docker / Docker Compose が利用可能
- Node.js 18+（ローカルでフロントを動かす場合）
- Python 3.11（ローカルでバックエンドを動かす場合）

## 推奨ワークスペース
- ルートに `kansatsunikki-serena.code-workspace` を用意しています。
  - エディタ推奨設定と拡張が含まれます。

## Serena 個人設定（プロジェクトローカル推奨）
1. プロジェクト直下に `.serena/config.yml` を用意します（初回のみ）。
   - `make serena-init` で空ファイルを用意できます（存在する場合はそのまま）。
   - サンプル:
     ```yaml
     ## Serena local config for kansatsunikki
     # Frontend
     NUXT_PUBLIC_API_BASE: http://localhost:8000
     NUXT_PUBLIC_BASIC_AUTH_USERNAME: plant_user
     NUXT_PUBLIC_BASIC_AUTH_PASSWORD: plant_pass123

     # Backend
     DATABASE_URL: mysql+pymysql://app_user:app_password@database:3306/plant_tracker
     MINIO_ENDPOINT: minio:9000
     MINIO_ACCESS_KEY: minioadmin
     MINIO_SECRET_KEY: minioadmin123
     MINIO_BUCKET_NAME: plant-images
     BASIC_AUTH_USERNAME: plant_user
     BASIC_AUTH_PASSWORD: plant_pass123
     JWT_SECRET_KEY: your-super-secret-jwt-key-change-in-production
     ```
2. YAML を `.env` に変換して docker-compose で読み込みます：
   ```bash
   make serena-up      # 初回は env 生成 + 起動
   # 以降
   make serena-build   # ビルドして起動
   make serena-down    # 停止
   ```
   - 変換スクリプト: `scripts/serena_config_to_env.py`
   - 優先順: `.serena/config.yml` -> `SERENA_CONFIG` で指定 -> `~/.config/serena/config.yml`
   - 生成物: リポジトリ直下に `.serena.env`（`.gitignore` 済み）

## 起動（Docker）
```bash
make build   # 初回は build 推奨（または make up）
make up
```

- Frontend: `http://localhost:3001`
- Backend API: `http://localhost:8000`
- MinIO Console: `http://localhost:9003`
- MySQL: `localhost:3307`

## データ永続化（ホスト側）
- 以下のディレクトリにコンテナのデータが保存されます（再起動・再作成でも残ります）:
  - `./data/mysql` → MySQL のデータ
  - `./data/minio` → MinIO のオブジェクト（画像など）
  - `./data/frontend_cache` → Nuxt のキャッシュ
- `./data/` は `.gitignore` 済みです。

## 環境変数（デフォルト）
`docker-compose.yml` の環境変数が既定値です。必要あれば上書きできます。

- フロント
  - `NUXT_PUBLIC_API_BASE`（既定: `http://localhost:8000`）
  - `NUXT_PUBLIC_BASIC_AUTH_USERNAME`（既定: `plant_user`）
  - `NUXT_PUBLIC_BASIC_AUTH_PASSWORD`（既定: `plant_pass123`）
- バックエンド
  - `DATABASE_URL`
  - `MINIO_ENDPOINT`, `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`, `MINIO_BUCKET_NAME`
  - `BASIC_AUTH_USERNAME`, `BASIC_AUTH_PASSWORD`
  - `JWT_SECRET_KEY`

## ログとデバッグ
```bash
make logs           # 全体ログ
make logs-backend   # バックエンドのみ
make logs-frontend  # フロントのみ
```

## よく使うコマンド
```bash
make restart
make clean
make backend-shell
make frontend-shell
```

## ローカルで直接動かす（任意）
- Backend
  ```bash
  cd backend
  pip install -r requirements.txt
  uvicorn main:app --reload --host 0.0.0.0 --port 8000
  ```
- Frontend
  ```bash
  cd frontend
  npm install
  npm run dev
  ```

## トラブルシュート
- ポート競合: 3001/8000/9002/9003/3307 が他プロセスで使用されていないか確認
- MySQL 初期化遅延: 最初の数十秒はバックエンドの接続に失敗する場合があります。DB ヘルスチェック完了後に安定します。
- フロントが 3001 で開かない: `make logs-frontend` で `http://localhost:3000` ヘルスチェックが通っているか確認