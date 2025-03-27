import logging
from .adjusting_schema import AdjustingRequest
def run_action(request: AdjustingRequest):
    """
    adjusting のステータスで必要な「独自処理」を行う。
    今はデモとしてログ出力だけ。
    """
    logging.info(f"[adjusting_repository] ユーザーID={request.user_id} が 予約ID={request.reservation_id} を 'adjusting' に変更 (独自処理).")
    # TODO: 後からDB書き込み処理などを追加する
