#!/usr/bin/env python3
"""
Unipile canlı yoxlama skripti (Arachi üçün). Serverdə, /root/FreightFlow qovluğunda işlədin:

    venv/bin/python unipile_smoke.py                      # açarı və hesabları yoxlayır
    venv/bin/python unipile_smoke.py send ACCOUNT_ID you@example.com   # həmin hesabdan bir test məktubu göndərir
    venv/bin/python unipile_smoke.py email ACCOUNT_ID EMAIL_ID         # bir məktubun sahələrini göstərir (in_reply_to, message_id)

UNIPILE_DSN və UNIPILE_API_KEY .env faylından oxunur. Açar ekrana yazılmır.
"""
import json
import os
import sys
import urllib.error
import urllib.request


def load_env(path=".env"):
    if not os.path.exists(path):
        return
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def call(method, path, body=None):
    dsn = os.environ.get("UNIPILE_DSN", "").rstrip("/")
    key = os.environ.get("UNIPILE_API_KEY", "")
    if not dsn or not key:
        sys.exit("UNIPILE_DSN və UNIPILE_API_KEY .env faylında olmalıdır.")
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(dsn + path, data=data, method=method,
                                 headers={"X-API-KEY": key, "accept": "application/json", "content-type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read().decode()
            return r.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, {"raw": raw[:300]}


def main():
    load_env()
    args = sys.argv[1:]
    if not args:
        status, data = call("GET", "/api/v1/accounts")
        print("Hesabların siyahısı:", status)
        items = data.get("items") if isinstance(data, dict) else data
        for a in items or []:
            print(" -", a.get("id"), a.get("type"), a.get("name"), a.get("sources") or "")
        if status == 200 and not items:
            print("(hələ qoşulmuş hesab yoxdur: paneldə «Poçt hesabı» ilə qoşun)")
        status, data = call("GET", "/api/v1/webhooks")
        print("Webhook-lar:", status)
        for w in (data.get("items") if isinstance(data, dict) else []) or []:
            print(" -", w.get("id"), w.get("source"), w.get("request_url"))
        return
    if args[0] == "send" and len(args) == 3:
        status, data = call("POST", "/api/v1/emails", {
            "account_id": args[1], "subject": "Arachi test [RFQ-00000000]", "body": "<p>Arachi test məktubu.</p>",
            "to": [{"display_name": "", "identifier": args[2]}]})
        print("Göndərmə:", status)
        print(json.dumps(data, indent=2, ensure_ascii=False)[:1500])
        print("Cavabda message_id / provider_id / tracking_id varmı? Yuxarıya baxın və Arachi-yə yazın.")
        return
    if args[0] == "email" and len(args) == 3:
        status, data = call("GET", f"/api/v1/emails/{args[2]}?account_id={args[1]}")
        print("Məktub:", status)
        safe = {k: data.get(k) for k in ("id", "provider_id", "message_id", "in_reply_to", "subject", "origin", "folders", "role") if isinstance(data, dict)}
        print(json.dumps(safe, indent=2, ensure_ascii=False))
        return
    sys.exit(__doc__)


if __name__ == "__main__":
    main()
