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

# Public WakaTime "All Time" languages share (no API key needed) — has absolute
# lifetime hours per language (total_seconds / text fields).
LANG_URL = "https://wakatime.com/share/@amalchandran_me/1a05ded7-9f58-47f5-8796-de7c952a0254.json"

README = os.path.join(os.path.dirname(__file__), "..", "..", "README.md")
START = "<!--START_SECTION:waka-->"
END = "<!--END_SECTION:waka-->"
TOP_N = 12

# Generic / non-language buckets to drop from the showcase.
SKIP = {"Other", "Text"}

# Chip styling (mirrors the tech-stack tags).
BG = "1F2328"
ACCENT = "FF5C35"

# Language name -> simple-icons logo slug (omitted langs render as a plain chip).
LANG_LOGO = {
    "TypeScript": "typescript", "JavaScript": "javascript", "Python": "python",
    "Markdown": "markdown", "Bash": "gnubash", "sh": "gnubash", "Shell": "gnubash",
    "YAML": "yaml", "JSON": "json", "Dart": "dart", "Java": "openjdk", "JSX": "react",
    "HTML": "html5", "CSS": "css3", "SCSS": "sass", "LESS": "less", "Lua": "lua",
    "Go": "go", "Rust": "rust", "PHP": "php", "Ruby": "ruby", "Kotlin": "kotlin",
    "Swift": "swift", "Vue.js": "vuedotjs", "C++": "cplusplus", "C": "c",
    "TOML": "toml", "GraphQL": "graphql", "Docker": "docker", "Dockerfile": "docker",
}


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "waka-readme-script"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["data"]


def fmt(secs):
    """Compact time for a chip: whole hours (with thousands sep) once >= 1h, else minutes."""
    secs = int(round(secs))
    if secs >= 3600:
        h = round(secs / 3600)
        return f"{h:,} hr{'s' if h != 1 else ''}"
    m = round(secs / 60)
    return f"{m} min{'s' if m != 1 else ''}"


def enc(text):
    """Encode a label/message for a shields.io path segment."""
    return text.replace("-", "--").replace(" ", "_").replace("/", "%2F")


def chip(name, t):
    logo = LANG_LOGO.get(name)
    url = f"https://img.shields.io/badge/{enc(name)}-{enc(t)}-{BG}?style=flat&labelColor={BG}"
    if logo:
        url += f"&logo={logo}&logoColor={ACCENT}"
    return f"![{name}]({url})"


def main():
    langs = [l for l in get(LANG_URL) if l["name"] not in SKIP][:TOP_N]
    chips = [chip(l["name"], fmt(l.get("total_seconds", 0))) for l in langs]

    block = "\n".join(chips) + "\n\n_Lifetime coding hours, via WakaTime._"

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
