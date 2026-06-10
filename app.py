import os
import logging
from flask import Flask, jsonify
from yt_cm import YouTubeCookieManager

app = Flask(__name__)

# مسیر فایل کوکی (همان مسیری که yt-cm استفاده می‌کند)
COOKIE_FILE = "/tmp/cookies.txt"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ensure_cookie_file():
    """اطمینان از وجود فایل کوکی (حتی اگر خالی باشد)"""
    if not os.path.exists(COOKIE_FILE):
        open(COOKIE_FILE, 'w').close()
        logger.warning("Cookie file did not exist. Created empty file.")

def get_valid_cookie():
    """دریافت کوکی معتبر، در صورت لزوم تمدید خودکار"""
    ensure_cookie_file()
    
    try:
        cookie_manager = YouTubeCookieManager(COOKIE_FILE)
        validation = cookie_manager.validate()
        
        if validation.get("valid"):
            logger.info("Cookie is valid.")
            return cookie_manager.export_netscape()
        
        logger.info("Cookie invalid or missing. Attempting to renew...")
        renew_result = cookie_manager.renew_session()
        
        if renew_result.get("renewed"):
            logger.info(f"Cookie renewed. Expiry: {renew_result.get('cookie_expiry')}")
            return cookie_manager.export_netscape()
        else:
            logger.error("Renewal failed.")
            return None
            
    except Exception as e:
        logger.error(f"Error in get_valid_cookie: {e}")
        return None

@app.route('/cookies', methods=['GET'])
def get_cookies_endpoint():
    cookie = get_valid_cookie()
    if cookie is None:
        return jsonify({"error": "Could not obtain valid cookie"}), 500
    return jsonify({"cookie": cookie})

@app.route('/health', methods=['GET'])
def health_check():
    """
    بررسی سلامت سرویس:
    - اگر کوکی معتبر وجود داشته باشد → 200
    - اگر خطا بدهد ولی سرویس قابل بازیابی باشد → 200 (فعلاً ساده)
    """
    try:
        ensure_cookie_file()
        # بررسی اولیه: آیا فایل قابل خواندن است؟
        with open(COOKIE_FILE, 'r') as f:
            _ = f.read(10)
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({"status": "error", "detail": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
