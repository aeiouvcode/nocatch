#!/usr/bin/env python3
"""Fail-closed static checks for the one-file directory. No third-party packages."""
import base64
import hashlib
import html.parser
import json
import pathlib
import re
import sys
from urllib.parse import urlsplit

ROOT = pathlib.Path(__file__).resolve().parents[1]
PAGE = ROOT / "index.html"


class Page(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.current = None
        self.attrs = {}
        self.content = {}
        self.ids = set()
        self.duplicate_ids = set()
        self.links = []
        self.anchors = []
        self.meta = {}

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == "link":
            self.links.append(attrs)
        if tag == "a":
            self.anchors.append(attrs)
        if tag == "meta" and attrs.get("name"):
            self.meta[attrs["name"]] = attrs.get("content", "")
        if tag == "title":
            self.current = "title"
        identifier = attrs.get("id")
        if identifier in self.ids:
            self.duplicate_ids.add(identifier)
        if identifier:
            self.ids.add(identifier)
            if identifier in {"mTools", "mCats", "mSources"}:
                self.current = identifier
        if tag in {"script", "style"}:
            if tag in self.content:
                raise ValueError(f"Multiple {tag} elements require explicit CSP review")
            self.current = tag
            self.content[tag] = ""
        if tag == "meta" and attrs.get("http-equiv", "").lower() == "content-security-policy":
            self.attrs["csp"] = attrs.get("content", "")

    def handle_data(self, data):
        if self.current:
            self.content[self.current] = self.content.get(self.current, "") + data

    def handle_endtag(self, tag):
        if tag in {"script", "style", "strong", "title"}:
            self.current = None


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def main():
    page = Page()
    page.feed(PAGE.read_text(encoding="utf-8"))
    require(not page.duplicate_ids, f"Duplicate HTML IDs: {page.duplicate_ids}")
    require(page.content.get("title", "").strip() == "NoCatch - honest AI tools directory", "Missing meaningful page title")
    require("free limits" in page.meta.get("description", "").lower(), "Missing meaningful meta description")
    favicon = next((link.get("href") for link in page.links if "icon" in link.get("rel", "").split()), None)
    require(favicon == "favicon.svg" and (ROOT / favicon).is_file(), "Missing local favicon")
    svg = (ROOT / favicon).read_text(encoding="utf-8")
    require("<svg" in svg and "viewBox" in svg and "</svg>" in svg, "Invalid favicon SVG")
    missing = Page()
    missing.feed((ROOT / "404.html").read_text(encoding="utf-8"))
    require("not found" in missing.content.get("title", "").lower() and "description" in missing.meta,
            "Missing 404 title or description")
    require(any(link.get("href") == "/nocatch/favicon.svg" for link in missing.links), "404 missing favicon")
    not_found = (ROOT / "404.html").read_text(encoding="utf-8")
    require(any(link.get('href') == '/nocatch/' for link in missing.anchors) and "Nothing here." in not_found,
            "404 needs a route back to the directory")
    require("default-src 'none'" in missing.attrs.get("csp", ""), "404 lacks restrictive CSP")
    require("noindex" in missing.meta.get("robots", ""), "404 must not be indexed")
    digest = base64.b64encode(hashlib.sha256(missing.content["style"].encode()).digest()).decode()
    require(f"'sha256-{digest}'" in missing.attrs["csp"], "404 CSP hash differs from content")
    csp = page.attrs.get("csp", "")
    require("default-src 'none'" in csp and "connect-src 'none'" in csp,
            "CSP must deny unknown resources and network connections")
    for tag in ("style", "script"):
        require(tag in page.content, f"Missing inline {tag}")
        digest = base64.b64encode(hashlib.sha256(page.content[tag].encode()).digest()).decode()
        require(f"'sha256-{digest}'" in csp, f"{tag} CSP hash differs from content")

    script = page.content["script"]
    require(script.startswith("const D="), "Dataset is no longer at script start: update validator")
    data, end = json.JSONDecoder().raw_decode(script[len("const D="):])
    require(script[len("const D=") + end] == ";", "Dataset tail changed: review parser")
    require(isinstance(data, list) and data, "Dataset is missing")
    names = set()
    categories = set()
    sources = set()
    for row_number, row in enumerate(data, 1):
        require(isinstance(row, list) and len(row) == 8, f"Row {row_number} has wrong shape")
        category, name, desc, offer, license, limit, risk, source = row
        require(all(isinstance(field, str) and field.strip() for field in row),
                f"Row {row_number} has empty or non-string field")
        require(name not in names, f"Duplicate saved-state key: {name}")
        names.add(name)
        categories.add(category)
        require(re.search(r"^CHECKED \d{1,2} (JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC) \d{4} · ", limit),
                f"Row {row_number} lacks a parseable check date")
        require("Card: " in limit or "Card requirement is not stated" in limit,
                f"Row {row_number} lacks card status")
        parts = urlsplit(source)
        require(parts.scheme == "https" and parts.netloc and not parts.username and not parts.password,
                f"Row {row_number} has invalid HTTPS source")
        sources.add(source)

    for identifier, expected in {"mTools": len(data), "mCats": len(categories), "mSources": len(sources)}.items():
        require(identifier in page.content, f"Missing metric {identifier}")
        require(page.content[identifier].strip() == str(expected),
                f"Static metric {identifier} says {page.content[identifier]!r}, expected {expected}")
    require("<noscript>" in PAGE.read_text(encoding="utf-8"), "Missing no-script state")
    require(".directory{display:none}.ready .directory{display:block}" in page.content["style"] and
            "document.body.classList.add('ready')" in script,
            "Directory must stay hidden until hydrated")
    require(all(text in script for text in ("$('emptyText').textContent", "$('feedback').textContent", "Browser storage is unavailable", "Saved", "Removed")),
            "Missing explicit empty/success/error feedback")
    required = {"emptyText", "feedback", "q", "surprise", "more", "cats", "access", "license", "card", "fresh", "view", "sort", "reset", "grid", "empty"}
    require(required <= page.ids, f"Feature map control missing from HTML: {required - page.ids}")
    fmap = (ROOT / "FEATURE-MAP.md").read_text(encoding="utf-8")
    require(all(label in fmap for label in ("Search", "Surprise me", "Freshness filter", "Saved view", "Shareable filter state", "404.html", "favicon.svg", "storage failure")),
            "Feature map lacks key behavior")
    print(f"PASS: {len(data)} listings, {len(categories)} categories, {len(sources)} source URLs; CSP, metadata, favicon, 404 and states checked")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, IndexError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
