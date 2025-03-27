# app/features/notifications/dispatcher.py

import importlib
import pkgutil
from app.features.notifications import handlers

# ✅ handlers/ フォルダ内の全ファイルを自動でインポート
NOTIFICATION_HANDLERS = {}

for _, module_name, _ in pkgutil.iter_modules(handlers.__path__):
    module = importlib.import_module(f"app.features.notifications.handlers.{module_name}")
    handler_func = getattr(module, f"send_{module_name}", None)
    if handler_func:
        NOTIFICATION_HANDLERS[module_name] = handler_func

def send(notification_type, **kwargs):
    """
    通知を適切な処理に振り分ける（インポートも自動化）
    """
    handler = NOTIFICATION_HANDLERS.get(notification_type)
    if handler:
        handler(**kwargs)
    else:
        print(f"❌ 未知の通知タイプ: {notification_type}")
