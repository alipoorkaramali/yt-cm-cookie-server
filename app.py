import os
import asyncio
from flask import Flask, jsonify
from playwright.async_api import async_playwright
import nest_asyncio

nest_asyncio.apply()
app = Flask(__name__)

EMAIL = os.environ.get("EMAIL")
PASSWORD = os.environ.get("PASSWORD")
COOKIE_FILE = "cookies.txt"

async def fetch_cookie():
    if not EMAIL or not PASSWORD:
        raise ValueError("EMAIL and PASSWORD environment variables are required")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto('https://accounts.google.com/signin')
        await page.fill('input[type="email"]', EMAIL)
        await page.click('#identifierNext')
        await page.wait_for_timeout(2000)
        await page.fill('input[type="password"]', PASSWORD)
        await page.click('#passwordNext')
        await page.wait_for_timeout(5000)
        if 'myaccount' in page.url or 'youtube.com' in page.url:
            await page.goto('https://www.youtube.com')
            cookies = await context.cookies()
            with open(COOKIE_FILE, 'w') as f:
                f.write("# Netscape HTTP Cookie File\n")
                for c in cookies:
                    f.write(f"{c['domain']}\t{'TRUE' if not c.get('hostOnly') else 'FALSE'}\t{c['path']}\t{'TRUE' if c.get('secure') else 'FALSE'}\t{int(c.get('expires', 0))}\t{c['name']}\t{c['value']}\n")
            await browser.close()
            return True
        await browser.close()
        return False

@app.route('/run_container', methods=['POST'])
def run():
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success = loop.run_until_complete(fetch_cookie())
        if not success:
            return jsonify({"error": "Login failed"}), 500
        with open(COOKIE_FILE) as f:
            cookie = f.read()
        return jsonify({"cookie": cookie})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    # پورت ثابت 8080 - بدون نیاز به متغیر PORT
    app.run(host='0.0.0.0', port=8080)
