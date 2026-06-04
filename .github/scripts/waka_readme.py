#!/usr/bin/env python3
"""Render WakaTime public-share stats into the README, no API key required.

Pulls two public share endpoints:
  - Languages  -> name + percent (no per-language time in the public payload)
  - Coding Activity -> daily grand totals -> overall total time

Per-language hours are derived as total_time * percent, then written between
the <!--START_SECTION:waka--> / <!--END_SECTION:waka--> markers in README.md.
"""
import json
import os
import re
import urllib.request

LANG_URL = "https://wakatime.com/share/@amalchandran_me/260eb1c6-c9a6-47e3-8886-5639353daae5.json"
ACT_URL = "https://wakatime.com/share/@amalchandran_me/b36c600d-6d8c-41d3-8238-d8b0b62fb182.json"

README = os.path.join(os.path.dirname(__file__), "..", "..", "README.md")
START = "<!--START_SECTION:waka-->"
END = "<!--END_SECTION:waka-->"
TOP_N = 8
BAR_W = 22


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "waka-readme-script"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["data"]


def fmt(secs):
    secs = int(round(secs))
    h, m = secs // 3600, (secs % 3600) // 60
    if h and m:
        return f"{h} hr{'s' if h != 1 else ''} {m} min{'s' if m != 1 else ''}"
    if h:
        return f"{h} hr{'s' if h != 1 else ''}"
    return f"{m} min{'s' if m != 1 else ''}"


def main():
    langs = get(LANG_URL)
    activity = get(ACT_URL)
    total = sum(d["grand_total"]["total_seconds"] for d in activity)

    rows = []
    for lang in langs[:TOP_N]:
        pct = lang.get("percent", 0) or 0
        rows.append((lang["name"], fmt(total * pct / 100), pct))

    name_w = max((len(r[0]) for r in rows), default=4)
    time_w = max((len(r[1]) for r in rows), default=4)

    lines = []
    for name, t, pct in rows:
        filled = round(pct / 100 * BAR_W)
        bar = "█" * filled + "░" * (BAR_W - filled)
        lines.append(f"{name.ljust(name_w)}   {t.ljust(time_w)}   {bar}   {pct:5.2f} %")

    block = (
        "```text\n"
        + "\n".join(lines)
        + f"\n\nTotal: {fmt(total)} over the last 7 days\n```"
    )

    with open(README, encoding="utf-8") as f:
        content = f.read()

    new = re.sub(
        re.escape(START) + r".*?" + re.escape(END),
        START + "\n" + block + "\n" + END,
        content,
        flags=re.S,
    )

    if new != content:
        with open(README, "w", encoding="utf-8") as f:
            f.write(new)
        print("README updated")
    else:
        print("No change")


if __name__ == "__main__":
    main()
