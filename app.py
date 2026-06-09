import os
import logging
from flask import Flask, jsonify
from yt_cm import YouTubeCookieManager

app = Flask(__name__)
COOKIE_FILE_PATH = "/tmp/cookies.txt"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_valid_cookie():
    # اگر فایل کوکی وجود نداشت، یک نمونه جدید ایجاد کن
    if not os.path.exists(COOKIE_FILE_PATH):
        logger.info("Cookie file not found. Creating a new one...")
        # ساخت یک فایل خالی (یا مستقیم به yt_cm بدیم)
        open(COOKIE_FILE_PATH, 'a').close()
    
    cookie_manager = YouTubeCookieManager(COOKIE_FILE_PATH)
    validation_result = cookie_manager.validate()
    
    if not validation_result.get("valid", False):
        logger.info("Cookie invalid or missing. Attempting to renew...")
        renew_result = cookie_manager.renew_session()
        if not renew_result.get("renewed", False):
            logger.error("Failed to renew the cookie.")
            return None
        logger.info(f"Cookie renewed successfully. New expiry: {renew_result.get('cookie_expiry')}")
    
    return cookie_manager.export_netscape()

@app.route('/cookies', methods=['GET'])
def get_cookies():
    cookie_content = get_valid_cookie()
    if cookie_content is None:
        return jsonify({"error": "Failed to get or renew cookie"}), 500
    logger.info("Cookie served successfully.")
    return jsonify({"cookie": cookie_content})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
