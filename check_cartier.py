import os
import re
import requests
from playwright.sync_api import sync_playwright

PRODUCT_URL = "https://www.cartier.com/ko-kr/%EC%A3%BC%EC%96%BC%EB%A6%AC/%EB%84%A4%ED%81%AC%EB%A6%AC%EC%8A%A4/%EB%8B%A4%EC%9D%B4%EC%95%84%EB%AA%AC%EB%93%9C-%EC%BB%AC%EB%A0%89%EC%85%98/%EA%B9%8C%EB%A5%B4%EB%9D%A0%EC%97%90-%EB%8B%A4%EB%AC%B4%EB%A5%B4-%ED%8E%9C%EB%8D%98%ED%8A%B8-%EB%B8%8C%EB%A6%B4%EB%A6%AC%EC%96%B8%ED%8A%B8-%EC%BB%B7-%EB%8B%A4%EC%9D%B4%EC%95%84%EB%AA%AC%EB%93%9C-%EC%8A%A4%EB%AA%B0%28small%29-%EB%AA%A8%EB%8D%B8-CRB7215900.html"

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": message,
            "disable_web_page_preview": False,
        },
        timeout=20,
    )

    print("Telegram status:", response.status_code)


def check_stock():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        page = browser.new_page(
            viewport={"width": 1440, "height": 1200},
            locale="ko-KR",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/130.0.0.0 Safari/537.36"
            ),
        )

        try:
            print("Opening Cartier CRB7215900...")
            
            page.goto(
                PRODUCT_URL,
                wait_until="domcontentloaded",
                timeout=60000,
            )

            page.wait_for_timeout(8000)

            title = page.title()
            body = page.locator("body").inner_text()

            print("PAGE TITLE:")
            print(title)

            print("\nPAGE TEXT:")
            print(body[:5000])

            available_patterns = [
                r"쇼핑백에\s*추가",
                r"장바구니에\s*추가",
                r"구매하기",
                r"온라인으로\s*구매",
                r"Add\s*to\s*Bag",
                r"Add\s*to\s*Cart",
            ]

            unavailable_patterns = [
                r"품절",
                r"온라인\s*구매\s*불가",
                r"현재\s*온라인에서\s*구매할\s*수\s*없",
                r"재입고\s*알림",
                r"입고\s*알림",
                r"Get\s*Notified",
                r"Currently\s*unavailable",
                r"Out\s*of\s*stock",
            ]

            available = any(
                re.search(pattern, body, re.IGNORECASE)
                for pattern in available_patterns
            )

            unavailable = any(
                re.search(pattern, body, re.IGNORECASE)
                for pattern in unavailable_patterns
            )

            print("AVAILABLE:", available)
            print("UNAVAILABLE:", unavailable)

            if available and not unavailable:
                print("STOCK FOUND!")

                send_telegram(
                    "🔥 까르띠에 다무르 재입고 감지!\n\n"
                    "CRB7215900\n"
                    "Small / 화이트 골드 / 다이아몬드\n\n"
                    "공식 사이트에서 구매 가능 상태가 감지되었습니다.\n\n"
                    + PRODUCT_URL
                )
            else:
                print("Still unavailable.")

        except Exception as e:
            print("ERROR:", str(e))

        finally:
            browser.close()


if __name__ == "__main__":
    check_stock()
