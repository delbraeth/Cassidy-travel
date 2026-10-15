#!/usr/bin/env python3
"""Copy Approved offers from the Notion "Website feed" database into offers.json.

Runs in GitHub Actions (see .github/workflows/sync-offers.yml). Needs a Notion
internal integration token in the NOTION_TOKEN environment variable, and the
integration must be connected to the Website feed database.
"""
import datetime
import json
import os
import sys
import urllib.error
import urllib.request

DATABASE_ID = os.environ.get("NOTION_FEED_DB", "8143a807a8d142c5a76e2f43b1543619")
DATA_SOURCE_ID = os.environ.get("NOTION_FEED_DS", "0708d3d0-86f0-4f0e-a25a-163e5b386fdb")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "offers.json")


def post(url, body, version, token):
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        method="POST",
        headers={
            "Authorization": "Bearer " + token,
            "Notion-Version": version,
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def approved_rows(token):
    body = {"filter": {"property": "Status", "select": {"equals": "Approved"}}, "page_size": 100}
    # Newer API versions query data sources; older ones query the database.
    endpoints = [
        ("https://api.notion.com/v1/data_sources/%s/query" % DATA_SOURCE_ID, "2025-09-03"),
        ("https://api.notion.com/v1/databases/%s/query" % DATABASE_ID, "2022-06-28"),
    ]
    errors = []
    for url, version in endpoints:
        try:
            rows, cursor = [], None
            while True:
                page = dict(body, start_cursor=cursor) if cursor else body
                data = post(url, page, version, token)
                rows.extend(data["results"])
                if not data.get("has_more"):
                    return rows
                cursor = data["next_cursor"]
        except urllib.error.HTTPError as err:
            errors.append("%s -> HTTP %s: %s" % (url, err.code, err.read().decode()[:300]))
    sys.exit("Could not read the Website feed database.\n" + "\n".join(errors))


def text(prop):
    if not prop:
        return ""
    parts = prop.get("title") if prop.get("type") == "title" else prop.get("rich_text")
    return "".join(p.get("plain_text", "") for p in parts or []).strip()


def date(prop):
    value = (prop or {}).get("date")
    return value["start"][:10] if value and value.get("start") else None


def main():
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        print("NOTION_TOKEN is not set yet, so offers.json was left as it is.")
        return
    today = datetime.date.today().isoformat()
    offers = []
    for row in approved_rows(token):
        props = row.get("properties", {})
        offer = {
            "brand": text(props.get("Supplier")),
            "title": text(props.get("Offer")),
            "terms": text(props.get("Terms")),
            "why": text(props.get("Why it matters")),
        }
        if not offer["brand"] or not offer["title"]:
            print("Skipping a row with no Offer or Supplier: " + row.get("url", ""), file=sys.stderr)
            continue
        start, end = date(props.get("Show from")), date(props.get("Hide after"))
        if end and end < today:
            continue
        if start:
            offer["start"] = start
        if end:
            offer["end"] = end
        offers.append(offer)
    offers.sort(key=lambda o: (o.get("end") or "9999", o["brand"], o["title"]))
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"offers": offers}, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("Wrote %d offers to offers.json" % len(offers))


if __name__ == "__main__":
    main()
