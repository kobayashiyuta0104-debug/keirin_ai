import json
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = Path(r"C:\競輪AI")
OUT = BASE / "210_jsj057_082_response_capture.json"
KDAY = "20260706"

print("=== 210 JSJ057 / JSJ082 RESPONSE BODY 直接取得テスト ===")

results = []

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        channel="msedge"
    )
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://www.keirin.jp/pc/top", wait_until="domcontentloaded")
    page.wait_for_timeout(3000)

    for api_type in ["JSJ057", "JSJ082"]:
        url = f"https://www.keirin.jp/pc/json?kday={KDAY}&type={api_type}"
        print()
        print("=" * 80)
        print("TYPE:", api_type)
        print("URL:", url)

        response = context.request.get(url)
        text = response.text()

        print("HTTP:", response.status)
        print("文字数:", len(text))
        print("先頭300文字:")
        print(text[:300])

        data = None
        error = None
        try:
            data = json.loads(text)
        except Exception as e:
            error = repr(e)

        if isinstance(data, dict):
            print("TOP KEYS:", list(data.keys()))
        elif isinstance(data, list):
            print("LIST COUNT:", len(data))
            if data and isinstance(data[0], dict):
                print("FIRST KEYS:", list(data[0].keys()))
        else:
            print("JSON DATA TYPE:", type(data).__name__)

        results.append({
            "type": api_type,
            "kday": KDAY,
            "url": url,
            "http_status": response.status,
            "text_length": len(text),
            "json_error": error,
            "data": data,
            "raw_text": text if data is None else None,
        })

    browser.close()

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print()
print("保存完了:", OUT)
print("=== 210 完了 ===")
