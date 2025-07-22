# LINE Rich Menu 実装計画書

## プロジェクト概要
ユーザータイプ（cast/customer/未登録）および状態に応じて動的にLINE Rich Menuを切り替える機能を実装

## 実装方針
- **Phase 1**: 静的画像ベース（immediate）
- **Phase 2**: 動的生成対応（future）
- **Phase 3**: 完全パーソナライズ（long-term）

---

## Phase 1: 基本実装（静的画像方式）

### 🎯 目標
基本的な3パターンのメニュー切り替えを実装

### 📋 必要なメニューパターン
1. **未登録ユーザー** (`unregistered`)
   - 会員登録
   - サービス紹介  
   - よくある質問
   - お問い合わせ

2. **Customer基本** (`customer_basic`)
   - キャスト検索
   - 予約履歴
   - お気に入り
   - アカウント設定

3. **Cast基本** (`cast_basic`)
   - マイページ
   - 予約管理
   - 売上確認
   - プロフィール編集

4. **Cast身分証要求** (`cast_identity_required`)
   - 身分証アップロード（大きなボタン）
   - サポート
   - よくある質問
   - アカウント設定

5. **Cast口座登録要求** (`cast_bank_required`)
   - 振込口座登録（大きなボタン）
   - サポート
   - よくある質問
   - アカウント設定

### 🏗️ 実装ステップ

#### Step 1: ディレクトリ構造作成
```bash
/app/features/linebot/rich_menu/
├── __init__.py
├── services/
│   ├── __init__.py
│   ├── menu_manager.py
│   ├── condition_engine.py
│   ├── rich_menu_client.py
│   └── image_service.py
├── models/
│   ├── __init__.py
│   ├── menu_condition.py
│   └── menu_definition.py
├── config/
│   ├── __init__.py
│   ├── menu_rules.py
│   └── menu_templates.py
├── assets/
│   └── static_images/
│       ├── unregistered.png
│       ├── customer_basic.png
│       ├── cast_basic.png
│       ├── cast_identity_required.png
│       └── cast_bank_required.png
└── templates/
    ├── unregistered.json
    ├── customer_basic.json
    ├── cast_basic.json
    ├── cast_identity_required.json
    └── cast_bank_required.json
```

#### Step 2: 条件判定エンジン実装
- ユーザータイプ判定
- 身分証提出状態判定
- 口座登録状態判定
- 条件に基づくメニューテンプレート選択

#### Step 3: Rich Menu API クライアント実装
- Rich Menu作成API
- Rich Menu削除API
- ユーザーへのメニュー適用API
- 画像アップロードAPI

#### Step 4: Webhook修正
- `follow`イベント処理追加
- ユーザー状態変更時のメニュー更新トリガー

#### Step 5: 管理API実装
- 手動メニュー更新API
- メニュー状態確認API

### 🖼️ 必要な画像仕様

**LINE Rich Menu 画像仕様**:
- **サイズ**: 2500px × 1686px
- **フォーマット**: PNG
- **容量**: 1MB以下
- **色数**: フルカラー

**各メニューの推奨レイアウト**:
- **4分割**（2×2）または**6分割**（2×3）
- タップ領域の明確な区切り
- アイコン + テキストの組み合わせ
- LINE公式の緑色（#00C300）を基調とした配色

---

## Phase 2: 拡張実装

### 🎯 追加予定パターン
- Customer VIP (`customer_vip`)
- Customer 初回 (`customer_first_time`)
- Cast 休止中 (`cast_inactive`)
- キャンペーン期間限定メニュー

### 🔧 動的生成機能
- ユーザー名埋め込み
- リアルタイム売上表示
- 期間限定キャンペーン情報

---

## Phase 3: 高度な機能

### 🚀 将来予定
- AI画像生成
- A/Bテストメニュー
- 地域別カスタマイズ
- 多言語対応

---

## 🎨 画像制作について

### 提案: 画像制作の分担

**あなた（クライアント）に依頼したい画像**:
1. **unregistered.png** - 未登録ユーザー向け
2. **customer_basic.png** - 顧客基本メニュー
3. **cast_basic.png** - キャスト基本メニュー
4. **cast_identity_required.png** - 身分証要求メニュー
5. **cast_bank_required.png** - 口座登録要求メニュー

### 画像制作のガイドライン

**デザイン要件**:
- PreCasブランドカラーに準拠
- 既存サイトデザインとの一貫性
- ユーザビリティを重視したボタン配置
- タップしやすいボタンサイズ（最小120px×120px）

**提供していただきたい情報**:
- 各メニューボタンのテキスト（日本語）
- 遷移先URL一覧
- PreCasロゴ・アイコン素材
- ブランドガイドライン（色、フォント等）

**制作フロー**:
1. 私がテンプレート設計とボタン配置案を作成
2. あなたが最終的な画像デザインを制作
3. 実装テスト後、必要に応じて調整

---

## 🔄 実装スケジュール

### Week 1: 基盤実装
- [ ] ディレクトリ構造作成
- [ ] 条件判定エンジン実装
- [ ] Rich Menu API クライアント実装

### Week 2: 統合・テスト
- [ ] Webhook修正
- [ ] 画像とテンプレート統合
- [ ] ローカル環境テスト

### Week 3: 本番デプロイ・調整
- [ ] 本番環境デプロイ
- [ ] 実機テスト
- [ ] 必要に応じて画像・動作調整

---

## 📝 メモ・課題

### 技術的検討事項
- [ ] LINE API制限（月1000回メニュー変更）の考慮
- [ ] メニューキャッシュ戦略
- [ ] エラーハンドリング（API失敗時の挙動）
- [ ] ログ設計（メニュー変更追跡）

### 運用面検討事項
- [ ] メニュー更新タイミングの最適化
- [ ] A/Bテスト用の仕組み
- [ ] 管理画面での手動メニュー変更機能

---

## 📚 参考資料
- [LINE Rich Menu API Documentation](https://developers.line.biz/ja/reference/messaging-api/#rich-menu)
- [LINE Design Guidelines](https://developers.line.biz/ja/docs/messaging-api/using-rich-menus/#design-guidelines)

---

**更新日**: 2025-07-22
**担当**: Claude + taichiumeki
**ステータス**: Phase 1 準備中