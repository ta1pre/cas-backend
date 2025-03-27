# CAS API

## プロジェクト概要

FastAPIを使用したバックエンドAPIサービスです。

## 技術スタック

- **バックエンド**: FastAPI, SQLAlchemy
- **データベース**: PostgreSQL
- **コンテナ化**: Docker
- **CI/CD**: GitHub Actions
- **デプロイ先**: AWS ECS

## 開発環境のセットアップ

### 前提条件

- Python 3.11以上
- Docker
- PostgreSQL

### ローカル開発環境の構築

```bash
# リポジトリのクローン
git clone git@github.com:ta1pre/sandbox.git
cd sandbox

# 仮想環境の作成と有効化
python -m venv venv
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate

# 依存関係のインストール
pip install -r requirements.txt

# 開発用環境変数の設定
cp .env.development .env

# アプリケーションの起動
uvicorn app.main:app --reload
```

## CI/CD設定

### ブランチ戦略

- **main**: 本番環境用ブランチ
- **develop**: 開発環境用ブランチ
- **feature/XXX**: 機能開発用ブランチ

### GitHub Actions

#### 開発環境へのデプロイ

`develop`ブランチにプッシュすると、自動的に以下の処理が実行されます：

1. テストの実行
2. Dockerイメージのビルド
3. ECRへのプッシュ
4. ECS開発環境へのデプロイ

#### 本番環境へのデプロイ

`main`ブランチにプッシュすると、自動的に以下の処理が実行されます：

1. Dockerイメージのビルド
2. ECRへのプッシュ
3. ECS本番環境へのデプロイ

### 必要なGitHub Secrets

GitHubリポジトリの「Settings > Secrets and variables > Actions」に以下の値を設定してください：

- `AWS_ACCESS_KEY_ID`: AWSアクセスキーID
- `AWS_SECRET_ACCESS_KEY`: AWSシークレットアクセスキー
- `DATABASE_URL`: 本番環境のデータベースURL
- `SECRET_KEY`: 本番環境用のシークレットキー

## AWS環境設定

### ECS設定

- **クラスター名**: cas-api-cluster
- **サービス名**: cas-api-service
- **タスク定義**: cas-api-task
- **コンテナポート**: 8000
- **ターゲットグループ**: cas-api-tg-port8000

### ALB設定

- **ALB名**: cas-api-alb
- **DNS名**: cas-api-alb-1560746111.ap-northeast-1.elb.amazonaws.com
- **セキュリティグループ**: sg-02d3cdf4384f2ff3a
- **重要なポート**: 80(HTTP), 443(HTTPS), 8000(アプリケーション)

### DNS設定

- **ドメイン**: api.cas.tokyo
- **ホストゾーンID**: Z099972515KSVTRPHOMMJ

## トラブルシューティング

### よくある問題と解決策

1. **ECSデプロイの失敗**: タスク定義のポートマッピングが正しいか確認
2. **ALBアクセス不可**: セキュリティグループでポート443が開放されているか確認
3. **DNS設定の問題**: Route 53でALBへの正しいエイリアスレコードが設定されているか確認

### 確認コマンド

```bash
# DNS設定確認
nslookup api.cas.tokyo

# ALB設定確認
aws elbv2 describe-load-balancers --names cas-api-alb

# セキュリティグループ確認
aws ec2 describe-security-groups --group-ids sg-02d3cdf4384f2ff3a

# 接続テスト
curl -v -k https://cas-api-alb-1560746111.ap-northeast-1.elb.amazonaws.com/
```
