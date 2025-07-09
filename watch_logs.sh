#!/bin/bash

# 古いログファイルを削除
rm -f fastapi.log

echo "📝 ログの監視を開始します..."
echo "💡 ヒント: Claude Codeで 'claude \"fastapi.logのエラーを修正して\"' と入力すると自動修正できます"
echo "🔕 ヘルスチェック(/api/v1/health)のログは除外しています"
echo ""

# ログを表示しながらファイルに保存（ヘルスチェックは除外）
docker logs -f fastapi-app 2>&1 | while IFS= read -r line; do
    # ヘルスチェックのログは無視
    if [[ ! "$line" =~ "GET /api/v1/health" ]]; then
        # 画面に表示
        echo "$line"
        
        # ファイルに追加
        echo "$line" >> fastapi.log
        
        # 1000行を超えたら古い行を削除
        if [ $(wc -l < fastapi.log 2>/dev/null || echo 0) -gt 1000 ]; then
            tail -n 1000 fastapi.log > fastapi.log.tmp
            mv fastapi.log.tmp fastapi.log
        fi
    fi
done