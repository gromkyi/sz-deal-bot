#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Дамп структуры лотов/сделок по одному артефакту (с additional=true),
чтобы понять, как закодировано качество. Запуск: python dump_artifact.py [id]
По умолчанию id = kqgy (Браслет). Читает api_credentials.json.
"""
import json, os, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
API_BASE = "https://eapi.stalcraft.net"; REGION = "RU"
iid = sys.argv[1] if len(sys.argv) > 1 else "kqgy"

c = json.load(open(os.path.join(HERE, "api_credentials.json"), encoding="utf-8"))
H = {"Client-Id": str(c["client_id"]).strip(), "Client-Secret": str(c["client_secret"]).strip(),
     "Accept": "application/json", "User-Agent": "ArtifactDump/1.0"}

def get(path):
    req = urllib.request.Request(f"{API_BASE}/{REGION}/{path}", headers=H)
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read().decode("utf-8"))

print(f"=== ЛОТЫ {iid} (additional=true), первые 6 ===")
lots = get(f"auction/{iid}/lots?limit=6&additional=true")
print("total:", lots.get("total"))
for lot in (lots.get("lots") or [])[:6]:
    print(json.dumps(lot, ensure_ascii=False, indent=2))

print(f"\n=== СДЕЛКИ {iid} (additional=true), первые 4 ===")
hist = get(f"auction/{iid}/history?limit=4&additional=true")
for s in (hist.get("prices") or [])[:4]:
    print(json.dumps(s, ensure_ascii=False, indent=2))
