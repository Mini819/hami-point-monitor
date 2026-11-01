
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
        raise RuntimeError("找不到 Telegram 設定")

    message = (
        f"🎉 Hami Point 有新商品了！\n"
        f"目前商品數量：{count} 件\n"
        f"快來看看：{URL}"
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
        print("Telegram 通知結果：", response.status)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(10000)
        text = page.locator("body").inner_text()
        browser.close()

    match = re.search(r"商品\s*([0-9,]+)", text)

    if not match:
        raise RuntimeError("無法讀取商品數量，停止通知")

    count = int(match.group(1).replace(",", ""))
    print("目前商品數量：", count)

    previous = int(STATE_FILE.read_text()) if STATE_FILE.exists() else 0

    if count > previous and count > 0:
        send_notification(count)
    else:
        print("沒有新增商品，不通知")

    STATE_FILE.write_text(str(count))


if __name__ == "__main__":
    main()
