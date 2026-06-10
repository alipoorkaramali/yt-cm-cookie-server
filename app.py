import os
import asyncio
import logging
from flask import Flask, jsonify, request
from rebrowser_playwright.async_api import async_playwright
import nest_asyncio

nest_asyncio.apply()
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

COOKIE_FILE = os.environ.get("COOKIE_FILE_NAME", "cookies.txt")
EMAIL = os.environ.get("EMAIL")
PASSWORD = os.environ.get("PASSWORD")

async def get_youtube_cookie():
    if not EMAIL or not PASSWORD:
        raise ValueError("EMAIL and PASSWORD environment variables are required")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        context = await browser.new_context()
        page = await context.new_page()

        # گام 1: صفحه لاگین گوگل
        await page.goto('https://accounts.google.com/signin')
        await page.fill('input[type="email"]', EMAIL)
        await page.click('#identifierNext')
        await page.wait_for_timeout(2000)

        await page.fill('input[type="password"]', PASSWORD)
        await page.click('#passwordNext')
        await page.wait_for_timeout(5000)

        # بررسی موفقیت لاگین
        if 'myaccount' in page.url or 'youtube.com' in page.url:
            await page.goto('https://www.youtube.com')
            cookies = await context.cookies()

            # ذخیره در فرمت Netscape
            with open(COOKIE_FILE, 'w') as f:
                f.write("# Netscape HTTP Cookie File\n")
                for cookie in cookies:
                    f.write(
                        f"{cookie['domain']}\t"
                        f"{'TRUE' if cookie.get('hostOnly') else 'FALSE'}\t"
                        f"{cookie['path']}\t"
                        f"{'TRUE' if cookie.get('secure') else 'FALSE'}\t"
                        f"{int(cookie.get('expires', 0))}\t"
                        f"{cookie['name']}\t"
                        f"{cookie['value']}\n"
                    )
            await browser.close()
            return True
        else:
            await browser.close()
            raise Exception("Login failed – captcha or wrong credentials")

@app.route('/run_container', methods=['POST'])
def run_container():
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success = loop.run_until_complete(get_youtube_cookie())
        if success:
            with open(COOKIE_FILE, 'r') as f:
                cookie_content = f.read()
            return jsonify({"cookie": cookie_content}), 200
        else:
            return jsonify({"error": "Could not obtain cookie"}), 500
    except Exception as e:
        logging.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
