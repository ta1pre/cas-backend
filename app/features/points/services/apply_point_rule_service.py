from sqlalchemy.orm import Session
from app.db.models.point import PointTransaction, PointBalance, PointRule
from datetime import datetime, timezone, timedelta
import json
import logging

def apply_point_rule(db: Session, user_id: int, rule_name: str, variables: dict = None, transaction_type: str = None):
    """ ルールを適用してポイントを更新する """
    # <<< ログ追加 >>>
    logging.info(f"🚀 apply_point_rule 開始: user_id={user_id}, rule_name='{rule_name}', variables={variables}, transaction_type={transaction_type}")

    # ルール取得
    rule = db.query(PointRule).filter(PointRule.rule_name == rule_name).first()
    if not rule:
        logging.error(f"🚨 ルール `{rule_name}` が見つかりません")
        return {"success": False, "message": f"🚨 ルール `{rule_name}` が見つかりません"}
    # <<< ログ追加 >>>
    logging.info(f"  ✅ ルール取得成功: rule_id={rule.id}, point_value={rule.point_value}, is_addition={rule.is_addition}")

    # ユーザーのポイント残高取得（なければ新規作成）
    balance = db.query(PointBalance).filter(PointBalance.user_id == user_id).first()
    is_new_balance = False
    if not balance:
        is_new_balance = True
        balance = PointBalance(user_id=user_id, regular_point_balance=0, bonus_point_balance=0, total_point_balance=0)
        db.add(balance)
        # <<< ログ追加 >>>
        logging.info(f"  ⚠️ ユーザー {user_id} のポイント残高レコードを新規作成")
    else:
        # <<< ログ追加 >>>
        logging.info(f"  ✅ ユーザー {user_id} のポイント残高取得: regular={balance.regular_point_balance}, bonus={balance.bonus_point_balance}, total={balance.total_point_balance}")

    # 変数からポイント値を取得（なければルールのポイント値を使用）
    point_value = rule.point_value
    if variables and "amount" in variables:
        point_value = variables["amount"]
        # <<< ログ追加 >>>
        logging.info(f"  ➡️ 変数からポイント値を取得: {point_value}")

    # <<< ログ追加 >>>
    logging.info(f"  ⚙️ ポイント計算開始: 計算に使用する値 = {point_value}")
    
    # ルールがボーナス or レギュラーポイントか確認
    if rule.is_addition:
        # 加算の場合
        # <<< ログ追加 >>>
        logging.info(f"  ➕ ポイント加算処理開始")
        if rule.point_type == "regular":
            balance.regular_point_balance += point_value
        else:
            balance.bonus_point_balance += point_value
        
        # 合計ポイント更新
        balance.total_point_balance += point_value
    else:
        # 減算の場合（ポイント値は絶対値にする）
        # <<< ログ追加 >>>
        logging.info(f"  ➖ ポイント減算処理開始")
        actual_value = abs(point_value)  # 絶対値

        # ===>>> 仕様変更: reservation_payment の場合は通常ポイントのみから減算 <<<===
        if rule_name == "reservation_payment":
            # <<< ログ追加 >>>
            logging.info(f"    ⚠️ reservation_paymentルール: 通常ポイントからのみ {actual_value} ポイント減算")
            if balance.regular_point_balance < actual_value:
                # 通常ポイントが足りない場合のエラーハンドリング（念のため）
                logging.error(f"🚨 予約支払いエラー: 通常ポイント不足 (必要: {actual_value}, 残高: {balance.regular_point_balance})")
                return {"success": False, "message": "通常ポイントが不足しています"}
            balance.regular_point_balance -= actual_value
            balance.total_point_balance -= actual_value # 合計も減らす
        else:
            # ===>>> それ以外の減算ルールは従来のロジック (ボーナス優先) <<<===
            # ボーナスポイントから減算
            bonus_deduction = min(balance.bonus_point_balance, actual_value)
            balance.bonus_point_balance -= bonus_deduction
            remaining = actual_value - bonus_deduction
            # <<< ログ追加 >>>
            logging.info(f"    ➖ ボーナスから減算: {bonus_deduction} ポイント")
            
            # 残りのポイントをレギュラーポイントから減算
            if remaining > 0:
                balance.regular_point_balance -= remaining
                # <<< ログ追加 >>>
                logging.info(f"    ➖ 通常から減算: {remaining} ポイント")
            
            # 合計ポイント更新
            balance.total_point_balance -= actual_value
        # ===>>> 仕様変更ここまで <<<===

        # <<< ログ追加 >>>
        logging.info(f"  📊 ポイント減算処理後: regular={balance.regular_point_balance}, bonus={balance.bonus_point_balance}, total={balance.total_point_balance}")
    
    balance.last_updated = datetime.now(timezone.utc)

    # 取引履歴を追加
    # <<< ログ追加 >>>
    logging.info(f"  📝 取引履歴作成開始")

    # transaction_typeの決定
    current_transaction_type = transaction_type or rule.transaction_type or "purchase"
    # purchaseルールのときは必ずbuyinに
    if rule_name == "purchase":
        current_transaction_type = "buyin"
    if rule_name == "reservation_payment":
        current_transaction_type = "deposit"
        logging.info(f"    ⚠️ transaction_type を 'deposit' に設定")
    
    transaction = PointTransaction(
        user_id=user_id,
        rule_id=rule.id,
        transaction_type=current_transaction_type,
        point_change=point_value,
        point_source=rule.point_type,
        balance_after=balance.total_point_balance
    )
    
    # 予約IDと説明を追加（なければ空）
    if variables:
        if "reservation_id" in variables:
            transaction.related_id = variables["reservation_id"]
            transaction.related_table = "reservation"
            # <<< ログ追加 >>>
            logging.info(f"    📝 取引履歴に予約ID {variables['reservation_id']} を関連付け")
        
        if "description" in variables:
            transaction.description = variables["description"]
            # <<< ログ追加 >>>
            logging.info(f"    📝 取引履歴に説明を追加: {variables['description']}")
    
    db.add(transaction)

    # DB保存
    # <<< ログ追加 >>>
    logging.info(f"  💾 データベースへの保存 (commit) 開始")
    try:
        # <<< ログ追加 (Commit前) >>>
        if is_new_balance:
            logging.info(f"    💾 新規残高情報: {balance.__dict__}")
        else:
            logging.info(f"    💾 更新残高情報: {balance.__dict__}")
        logging.info(f"    💾 新規取引履歴情報: {transaction.__dict__}")
        
        db.commit()
        
        # <<< ログ追加 (Commit後) >>>
        logging.info(f"  ✅ データベースへの保存成功 (commit 完了)")
        logging.info(f"🔚 apply_point_rule 正常終了")
        return {
            "success": True, 
            "message": f"✅ `{rule_name}` が適用されました！", 
            "point_change": point_value,
            "new_balance": balance.total_point_balance,
            "transaction_id": transaction.id
        }
    except Exception as e:
        db.rollback()
        # <<< ログ追加 >>>
        logging.error(f"🚨 データベースへの保存失敗 (rollback 実行): {e}")
        logging.exception("  詳細なエラー情報:") # スタックトレースも出力
        logging.info(f"🔚 apply_point_rule 異常終了")
        return {"success": False, "message": f"🚨 ポイント処理が失敗しました: {e}"}
