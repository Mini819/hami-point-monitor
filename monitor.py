
import os
import json
import urllib.request

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")

CHAT_IDS = [
    os.environ.get("TELEGRAM_CHAT_ID", ""),
    "8309012509",
]

URL = "https://hamipoint.cht.com.tw/store/brand/357"


def test_notification():
    if not BOT_TOKEN:
        raise RuntimeError("找不到 Telegram Bot Token")

    message = (
        "🧪【Hami Point 多人通知測試】\n\n"
        "這是一則測試訊息！\n"
        "如果你收到這則通知，代表 Bot 連接成功。\n\n"
        f"商品頁面：\n{URL}"
    )

    for chat_id in CHAT_IDS:
        if not chat_id:
            continue

        print(f"正在發送通知給：{chat_id}")

        data = json.dumps({
            "chat_id": chat_id,
            "text": message
        }).encode("utf-8")

        req = urllib.request.Request(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=20) as response:
                result = json.loads(
                    response.read().decode("utf-8")
                )

            if not result.get("ok"):
                raise RuntimeError(str(result))

            print(f"通知成功：{chat_id}")

        except Exception as e:
            print(f"通知失敗：{chat_id}")
            print(f"錯誤原因：{e}")

    print("測試結束")


if __name__ == "__main__":
    test_notification()
