import logging
from sqlalchemy.orm import Session

def run_action(db: Session, reservation_id: int, user_id: int):
    """
    adjusting のステータスで必要な「独自処理」を行う。
    今はデモとしてログ出力だけ。
    """
    logging.info(f"[adjusting_repository] ユーザーID={user_id} が 予約ID={reservation_id} を 'adjusting' に変更 (独自処理).")
    # TODO: 後からDB書き込み処理などを追加する
    
    # 重要: "OK"を返さないとステータス更新が実行されない
    return {"status": "OK", "message": "修正依頼を送信しました"}
