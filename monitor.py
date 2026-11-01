
import os
import re
import json
import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

URL = "https://hamipoint.cht.com.tw/store/brand/357"
STATE_FILE = Path(".monitor_state")

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")


def send_notification(count):
    if not BOT_TOKEN or not CHAT_ID:
        raise RuntimeError("找不到 Telegram Token 或 Chat ID")

    message = (
        "🎉【Hami Point 新商品通知】\n\n"
        f"目前商品數量：{count} 件\n\n"
        "快來看看：\n"
        f"{URL}"
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
        result = json.loads(response.read().decode("utf-8"))

    if not result.get("ok"):
        raise RuntimeError(f"Telegram 發送失敗：{result}")

    print("Telegram 通知發送成功")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto(
                URL,
                wait_until="domcontentloaded",
                timeout=60000
            )
            page.wait_for_timeout(10000)
            text = page.locator("body").inner_text()
        finally:
            browser.close()

    match = re.search(r"商品\s*([0-9,]+)", text)

    if not match:
        raise RuntimeError("無法讀取商品數量，停止通知")

    count = int(match.group(1).replace(",", ""))
    print("目前商品數量：", count)

    previous = (
        int(STATE_FILE.read_text().strip())
        if STATE_FILE.exists()
        else 0
    )

    print("上次商品數量：", previous)

    if count > previous and count > 0:
        send_notification(count)
        print("發現新增商品，已通知")
    else:
        print("沒有新增商品，不通知")

    STATE_FILE.write_text(str(count))


if __name__ == "__main__":
    main()
