
import os
import json
import urllib.request

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

URL = "https://hamipoint.cht.com.tw/store/brand/357"

def send_notification():
    if not BOT_TOKEN or not CHAT_ID:
        raise RuntimeError("找不到 Telegram 設定")

    message = (
        "🎉【Hami Point 新商品通知】\n\n"
        "發現新商品！\n"
        "目前商品數量：1 件\n\n"
        "請立即前往查看：\n"
        f"{URL}\n\n"
        "（這是一則模擬新增商品的測試通知）"
    )

    data = json.dumps({
        "chat_id": CHAT_ID,
        "text": message
    }).encode("utf-8")

    req = urllib.request.Request(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=20) as response:
        print("Hami Point 模擬商品通知成功：", response.status)

if __name__ == "__main__":
    send_notification()
