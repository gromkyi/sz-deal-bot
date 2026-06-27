#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Из market_overview.csv собирает список ликвидных предметов (с названиями) -> watchlist.csv.
Названия берёт из официальной базы предметов (GitHub, без авторизации).
Запускать локально один раз (и потом изредка, когда обновишь market_overview).

Настройки ниже: порог ликвидности и диапазон медианной цены.
"""
import csv, os, json, time, urllib.request, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
DB_REPO = "EXBO-Studio/stalzone-database"
REGION = "ru"

# --- настройки фильтра ---
MIN_LIQ = 5            # минимум сделок в день
MIN_MEDIAN = 10_000    # не брать мелочь дешевле (0 = брать всё)
MAX_MEDIAN = float("inf")  # верхний потолок медианы (напр. 5_000_000)
EXCLUDE_CATEGORIES = ["weapon_modules"]  # не включать: слишком разные характеристики (медиана обманчива)

def find_overview():
    for p in [os.path.join(HERE, "market_overview.csv"),
              os.path.join(HERE, "..", "price_tracker", "market_overview.csv")]:
        if os.path.exists(p): return p
    raise SystemExit("Не найден market_overview.csv — положи его рядом с этим скриптом.")

def fnum(x):
    try: return float(x)
    except (TypeError, ValueError): return None

def rate(r):
    v = r.get("sales_per_day")
    return 1e9 if v == ">100" else (fnum(v) or 0)

def fetch_name(category, iid):
    url = f"https://raw.githubusercontent.com/{DB_REPO}/main/{REGION}/items/{category}/{iid}.json"
    try:
        req = urllib.request.Request(url, headers={"User-Agent":"StalzoneWatchlist/1.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            d = json.loads(r.read().decode("utf-8"))
        n = d.get("name", {})
        if isinstance(n, dict):
            if "lines" in n and isinstance(n["lines"], dict):
                return n["lines"].get("ru") or n["lines"].get("en") or iid
            if n.get("type") == "text":
                return n.get("text", iid)
        return iid
    except Exception:
        return iid

def main():
    src = find_overview()
    rows = list(csv.DictReader(open(src, encoding="utf-8-sig")))
    sel = [r for r in rows
           if rate(r) >= MIN_LIQ
           and (fnum(r.get("median_price")) or 0) >= MIN_MEDIAN
           and (fnum(r.get("median_price")) or 0) <= MAX_MEDIAN
           and not any((r.get("category") or "").startswith(x) for x in EXCLUDE_CATEGORIES)]
    sel.sort(key=rate, reverse=True)
    print(f"Отобрано ликвидных: {len(sel)} (порог {MIN_LIQ} сд/день, медиана {MIN_MEDIAN}..{MAX_MEDIAN})")
    out = os.path.join(HERE, "watchlist.csv")
    with open(out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["id","name","category","median_price","sales_per_day","tier"])
        for i, r in enumerate(sel):
            name = fetch_name(r["category"], r["id"])
            w.writerow([r["id"], name, r["category"], r.get("median_price",""),
                        r.get("sales_per_day",""), r.get("tier","")])
            if (i+1) % 50 == 0: print(f"  ...{i+1}/{len(sel)}")
            time.sleep(0.08)
    print("Готово ->", out)

if __name__ == "__main__":
    main()
