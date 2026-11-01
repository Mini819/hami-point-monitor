
import os
import re
import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

URL = "https://hamipoint.cht.com.tw/store/brand/357"
STATE_FILE = Path(".monitor_state")
TOPIC = os.environ.get("NTFY_TOPIC", "")

def send_notification(count):
    if not TOPIC:
        raise RuntimeError("找不到 NTFY_TOPIC")

    data = f"Hami Point 目前有 {count} 件商品！\n{URL}".encode("utf-8")
    req = urllib.request.Request(
        f"https://ntfy.sh/{TOPIC}",
        data=data,
        headers={"Title": "Hami Point 商品提醒", "Priority": "high"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=20) as response:
        print("通知結果：", response.status)

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
