import json
import importlib.util
import os
from pathlib import Path
from datetime import datetime, timedelta, timezone

# ===========================================================
# 基本設定
# ===========================================================

if os.name == "nt":
    BASE = Path(r"C:\競輪AI")
else:
    BASE = Path(__file__).resolve().parent.parent

COLLECTOR_FILE = (
    BASE
    / "official_program"
    / "origin_program"
    / "004_collect_historical_raw.py"
)

JST = timezone(timedelta(hours=9))
YESTERDAY = (
    datetime.now(JST) - timedelta(days=1)
).strftime("%Y%m%d")


# ===========================================================
# 004読込
# ===========================================================

def load_collector_module():

    if not COLLECTOR_FILE.exists():
        raise FileNotFoundError(
            "004_collect_historical_raw.py がありません"
        )

    spec = importlib.util.spec_from_file_location(
        "official_collector_004",
        COLLECTOR_FILE,
    )

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


# ===========================================================
# JSJ001表示
# ===========================================================

def show_jsj001():

    collector = load_collector_module()

    print("=" * 80)
    print("JSJ001デバッグ")
    print("対象日:", YESTERDAY)
    print("=" * 80)

    # JSJ057取得
    jsj057 = collector.fetch_jsj057(YESTERDAY)

    if not jsj057["ok"]:
        print("JSJ057取得失敗")
        print(jsj057["error"])
        return

    venues = jsj057.get("venues", [])

    print("開催場数:", len(venues))
    print()

    if len(venues) == 0:
        print("開催場がありません")
        return

    # 最初の開催場
    venue = venues[0]

    print("開催場:", venue.get("jyoName"))
    print()

    enc_prm = venue.get("encPrm")

    print("encPrm")
    print(enc_prm)
    print()

    # JSJ001取得
    jsj001 = collector.fetch_jsj001(enc_prm)

    if not jsj001["ok"]:
        print("JSJ001取得失敗")
        print(jsj001["error"])
        return

    print("=" * 80)
    print("JSJ001 JSON")
    print("=" * 80)

    print(json.dumps(
        jsj001["data"],
        ensure_ascii=False,
        indent=2
    ))

    print()

    print("=" * 80)
    print("トップキー")
    print("=" * 80)

    for key in sorted(jsj001["data"].keys()):
        print(key)

    print()

    c0201 = jsj001["data"].get("C0201data")

    if isinstance(c0201, dict):

        print("=" * 80)
        print("C0201data キー")
        print("=" * 80)

        for key in sorted(c0201.keys()):
            print(key)

    input("\nEnterで終了...")


# ===========================================================
# main
# ===========================================================

if __name__ == "__main__":
    show_jsj001()