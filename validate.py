#!/usr/bin/env python3
"""
S1gns Of L1fe app — content checker.

Checks a content.json patch before you publish it, and explains any problems in plain English.

    python3 validate.py                 # checks content.json next to this script
    python3 validate.py path/to/file.json
    python3 validate.py --online        # also checks that every link actually opens (slower)

Only uses Python's standard library — nothing to install.
Exit code 0 = good to publish, 1 = there are errors to fix.
"""

import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import date, datetime

KINDS = {
    "youtube": "a YouTube video (needs youtubeId)",
    "video": "a video file or Vimeo/Wistia/YouTube page (needs mediaURL or youtubeId)",
    "audio": "an audio file (needs mediaURL ending in .mp3/.m4a/.wav/.aac)",
    "article": "long-form text (uses body paragraphs)",
    "download": "a free download page (needs mediaURL or attachments)",
    "pdf": "a PDF guide (needs mediaURL ending in .pdf)",
    "link": "a web page (needs mediaURL)",
    "gallery": "a set of images (needs images)",
}
VAULT_FIELDS = {"id", "title", "subtitle", "kind", "category", "summary", "body", "mediaURL", "youtubeId",
                "thumbnail", "images", "attachments", "tags", "publishedAt", "duration", "featured"}
ATTACHMENT_FIELDS = {"title", "url", "kind", "size"}
ANNOUNCEMENT_FIELDS = {"id", "title", "message", "url", "cta", "expires"}
TOP_LEVEL_KEYS = {"version", "updatedAt", "artist", "stats", "timeline", "stories", "quotes", "interviews",
                  "releases", "projects", "labels", "plugins", "education", "services", "links", "testimonials",
                  "awards", "merch", "videos", "studio", "vault", "announcements"}

ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
YOUTUBE_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")
DATE_RE = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")
DURATION_RE = re.compile(r"^(\d+:)?\d{1,2}:\d{2}$")
AUDIO_EXT = (".mp3", ".m4a", ".wav", ".aac")
VIDEO_EXT = (".mp4", ".m4v", ".mov", ".m3u8")

USE_COLOR = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None


def paint(text, code):
    return f"\033[{code}m{text}\033[0m" if USE_COLOR else text


class Report:
    def __init__(self):
        self.errors, self.warnings = [], []

    def error(self, where, msg):
        self.errors.append((where, msg))

    def warn(self, where, msg):
        self.warnings.append((where, msg))


def is_url(value):
    return isinstance(value, str) and re.match(r"^https://[^\s/$.?#].[^\s]*$", value) is not None


def parse_date(value):
    if not isinstance(value, str):
        return None
    v = value.strip()
    if DATE_RE.match(v):
        parts = [int(p) for p in v.split("-")] + [1, 1]
        try:
            return date(parts[0], parts[1], parts[2])
        except ValueError:
            return None
    try:
        return datetime.fromisoformat(v.replace("Z", "+00:00")).date()
    except ValueError:
        return None


def check_url(r, where, field, value, required_ext=None):
    if not is_url(value):
        r.error(where, f"“{field}” must be a full web address starting with https:// (got {value!r}).")
        return False
    if required_ext and not value.lower().split("?")[0].endswith(required_ext):
        r.warn(where, f"“{field}” doesn't end in {' / '.join(required_ext)} — make sure it links straight to the file, not a web page.")
    if "dropbox.com" in value and "dl=1" not in value and "raw=1" not in value:
        r.warn(where, f"“{field}” is a Dropbox link. Change the ending to ?dl=1 (or &raw=1) so the app gets the file, not the Dropbox page.")
    if "drive.google.com/file" in value:
        r.warn(where, f"“{field}” is a Google Drive page link — these often don't play or download inside apps. See README “Where to host media”.")
    return True


def validate_item(r, item, index, seen_ids):
    where = f"vault item #{index + 1}"
    if not isinstance(item, dict):
        r.error(where, "must be an object in curly braces { … }.")
        return
    if isinstance(item.get("title"), str):
        where = f"vault item #{index + 1} (“{item['title']}”)"

    for key in item:
        if key not in VAULT_FIELDS:
            close = [f for f in VAULT_FIELDS if f.lower() == key.lower()]
            hint = f" Did you mean “{close[0]}”? (capital letters matter)" if close else ""
            r.warn(where, f"unknown field “{key}” will be ignored.{hint}")

    item_id = item.get("id")
    if not item_id:
        r.error(where, "is missing “id” (a short name like “drone-pack-2”).")
    elif not isinstance(item_id, str) or not ID_RE.match(item_id):
        r.error(where, f"“id” {item_id!r} should use only lowercase letters, numbers and dashes, e.g. “drone-pack-2”.")
    elif item_id in seen_ids:
        r.error(where, f"“id” “{item_id}” is used twice — every item needs its own id.")
    else:
        seen_ids.add(item_id)

    if not isinstance(item.get("title"), str) or not item["title"].strip():
        r.error(where, "is missing a “title”.")
    elif len(item["title"]) > 80:
        r.warn(where, "title is quite long — under 60 characters looks best on a phone.")

    kind = item.get("kind")
    if kind is None:
        r.error(where, f"is missing “kind”. Use one of: {', '.join(KINDS)}.")
        kind = None
    elif kind not in KINDS:
        r.error(where, f"“kind” {kind!r} isn't known. Use one of: {', '.join(KINDS)}.")
        kind = None

    for text_field in ("subtitle", "category", "summary", "thumbnail", "duration"):
        if text_field in item and not isinstance(item[text_field], str):
            r.error(where, f"“{text_field}” must be text in quotes.")

    media = item.get("mediaURL")
    if media is not None:
        ext = {"audio": AUDIO_EXT, "pdf": (".pdf",)}.get(kind)
        check_url(r, where, "mediaURL", media, ext)

    yt = item.get("youtubeId")
    if yt is not None:
        if not isinstance(yt, str) or not YOUTUBE_RE.match(yt):
            hint = ""
            if isinstance(yt, str) and ("youtu" in yt or "/" in yt):
                m = re.search(r"(?:v=|youtu\.be/|embed/|shorts/)([A-Za-z0-9_-]{11})", yt)
                hint = f" It looks like a full link — use just the id: “{m.group(1)}”." if m else ""
            r.error(where, f"“youtubeId” must be the 11-character video id (the part after watch?v=).{hint}")

    thumb = item.get("thumbnail")
    if isinstance(thumb, str) and thumb.startswith("http") and not is_url(thumb):
        r.error(where, "“thumbnail” must start with https://")
    if isinstance(thumb, str) and thumb.startswith("http://"):
        r.error(where, "“thumbnail” must use https:// (iPhones block plain http images).")

    images = item.get("images", [])
    if not isinstance(images, list):
        r.error(where, "“images” must be a list: [\"https://…\", \"https://…\"].")
        images = []
    for i, img in enumerate(images):
        check_url(r, where, f"images[{i + 1}]", img)

    body = item.get("body", [])
    if isinstance(body, str):
        r.error(where, "“body” must be a list of paragraphs: [\"First paragraph.\", \"Second paragraph.\"].")
    elif not isinstance(body, list) or not all(isinstance(p, str) for p in body):
        r.error(where, "“body” must be a list of text paragraphs.")

    tags = item.get("tags", [])
    if not isinstance(tags, list) or not all(isinstance(t, str) for t in tags):
        r.error(where, "“tags” must be a list of words: [\"Vital\", \"Presets\"].")

    attachments = item.get("attachments", [])
    if not isinstance(attachments, list):
        r.error(where, "“attachments” must be a list of { \"title\": …, \"url\": … } objects.")
        attachments = []
    for i, att in enumerate(attachments):
        aw = f"{where}, attachment #{i + 1}"
        if not isinstance(att, dict):
            r.error(aw, "must be an object with “title” and “url”.")
            continue
        for key in att:
            if key not in ATTACHMENT_FIELDS:
                r.warn(aw, f"unknown field “{key}” will be ignored (allowed: title, url, kind, size).")
        if not isinstance(att.get("title"), str) or not att["title"].strip():
            r.error(aw, "is missing a “title”.")
        if "url" not in att:
            r.error(aw, "is missing a “url”.")
        else:
            check_url(r, aw, "url", att["url"])

    published = item.get("publishedAt")
    if published is not None:
        d = parse_date(published)
        if d is None:
            r.error(where, f"“publishedAt” {published!r} isn't a date. Use YYYY-MM-DD, e.g. “{date.today().isoformat()}”.")
        elif d > date.today():
            r.warn(where, f"“publishedAt” {published} is in the future — it will sort above everything else.")
    else:
        r.warn(where, "has no “publishedAt” date — it will sort to the bottom and show a NEW badge until opened.")

    duration = item.get("duration")
    if isinstance(duration, str) and not DURATION_RE.match(duration):
        r.warn(where, f"“duration” {duration!r} looks odd — use minutes:seconds like “23:21” or “1:05:00”.")

    featured = item.get("featured")
    if featured is not None and not isinstance(featured, bool):
        r.error(where, "“featured” must be true or false (no quotes).")

    # Kind-specific requirements.
    if kind == "youtube" and not yt:
        r.error(where, "is a youtube item but has no “youtubeId”.")
    if kind == "video" and not media and not yt:
        r.error(where, "is a video item but has neither “mediaURL” nor “youtubeId”.")
    if kind == "video" and isinstance(media, str) and is_url(media):
        path = media.lower().split("?")[0]
        embeddable = any(h in media for h in ("youtu", "vimeo.com", "wistia"))
        if not path.endswith(VIDEO_EXT) and not embeddable:
            r.warn(where, "video “mediaURL” isn't a video file or YouTube/Vimeo/Wistia link — the app will open it as a web page instead of playing it.")
    if kind in ("audio", "pdf", "link") and not media:
        r.error(where, f"is a {kind} item but has no “mediaURL”.")
    if kind == "download" and not media and not attachments:
        r.error(where, "is a download item but has no “mediaURL” or “attachments” — there's nothing to download.")
    if kind == "gallery" and not images:
        r.error(where, "is a gallery item but has no “images”.")
    if kind == "article" and not body and not item.get("summary"):
        r.warn(where, "is an article with no “body” or “summary” text.")
    if kind not in ("youtube", "video") and not thumb and not yt and not images:
        r.warn(where, "has no “thumbnail” — it will show a plain placeholder image.")


def validate_announcements(r, value):
    if not isinstance(value, list):
        r.error("announcements", "must be a list [ … ].")
        return
    seen = set()
    for i, a in enumerate(value):
        where = f"announcement #{i + 1}"
        if not isinstance(a, dict):
            r.error(where, "must be an object { … }.")
            continue
        for key in a:
            if key not in ANNOUNCEMENT_FIELDS:
                r.warn(where, f"unknown field “{key}” will be ignored (allowed: {', '.join(sorted(ANNOUNCEMENT_FIELDS))}).")
        if not a.get("id"):
            r.error(where, "is missing “id”.")
        elif a["id"] in seen:
            r.error(where, f"“id” “{a['id']}” is used twice.")
        else:
            seen.add(a["id"])
        if not a.get("title"):
            r.error(where, "is missing “title”.")
        if "url" in a:
            check_url(r, where, "url", a["url"])
        if "expires" in a:
            d = parse_date(a["expires"])
            if d is None:
                r.error(where, "“expires” must be a date like 2026-12-31.")
            elif d < date.today():
                r.warn(where, f"has already expired ({a['expires']}) and won't be shown.")


def check_links_online(r, data):
    urls = []
    for i, item in enumerate(data.get("vault", []) or []):
        if not isinstance(item, dict):
            continue
        name = item.get("title", f"#{i + 1}")
        for field in ("mediaURL", "thumbnail"):
            if is_url(item.get(field)):
                urls.append((name, field, item[field]))
        for img in item.get("images", []) or []:
            if is_url(img):
                urls.append((name, "images", img))
        for att in item.get("attachments", []) or []:
            if isinstance(att, dict) and is_url(att.get("url")):
                urls.append((name, "attachment", att["url"]))
        if isinstance(item.get("youtubeId"), str):
            urls.append((name, "youtubeId", f"https://www.youtube.com/oembed?format=json&url=https://www.youtube.com/watch?v={item['youtubeId']}"))
    print(f"Checking {len(urls)} links online…")
    for name, field, url in urls:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (S1gnsOfL1fe content checker)"})
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                ok = 200 <= resp.status < 400
        except urllib.error.HTTPError as e:
            ok = False
            status = e.code
        except Exception as e:  # noqa: BLE001 — report anything as unreachable
            ok = False
            status = type(e).__name__
        else:
            status = resp.status
        if not ok:
            r.error(f"“{name}”", f"{field} link didn't open ({status}): {url}")


def main(argv):
    online = "--online" in argv
    args = [a for a in argv if not a.startswith("--")]
    path = args[0] if args else os.path.join(os.path.dirname(os.path.abspath(__file__)), "content.json")
    print(paint("S1gns Of L1fe content checker", "1;35"))
    print(f"File: {path}\n")

    try:
        with open(path, encoding="utf-8") as f:
            raw = f.read()
    except OSError as e:
        print(paint(f"✗ Couldn't open the file: {e}", "31"))
        return 1
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        line = raw.splitlines()[e.lineno - 1] if e.lineno - 1 < len(raw.splitlines()) else ""
        print(paint(f"✗ The file isn't valid JSON (line {e.lineno}, column {e.colno}): {e.msg}", "31"))
        print(f"    {line.strip()}")
        print("  Common causes: a missing comma between items, a comma after the LAST item,")
        print("  curly “smart quotes” instead of straight \"quotes\", or a missing } or ].")
        return 1

    r = Report()
    if not isinstance(data, dict):
        r.error("file", "must be one object { … } with keys like \"vault\" and \"announcements\".")
    else:
        for key in data:
            if key not in TOP_LEVEL_KEYS:
                r.warn("file", f"top-level key “{key}” isn't used by the app and will be ignored.")
        vault = data.get("vault")
        if vault is not None:
            if not isinstance(vault, list):
                r.error("vault", "must be a list [ … ] of items.")
            else:
                seen = set()
                for i, item in enumerate(vault):
                    validate_item(r, item, i, seen)
                featured = sum(1 for it in vault if isinstance(it, dict) and it.get("featured") is True)
                if featured > 5:
                    r.warn("vault", f"{featured} items are featured — 1 to 4 keeps the carousel special.")
        if "announcements" in data:
            validate_announcements(r, data["announcements"])
        if online:
            check_links_online(r, data)

    for where, msg in r.warnings:
        print(paint("⚠ ", "33") + f"{where}: {msg}")
    for where, msg in r.errors:
        print(paint("✗ ", "31") + f"{where}: {msg}")

    vault_count = len(data.get("vault", []) or []) if isinstance(data, dict) and isinstance(data.get("vault"), list) else 0
    print()
    if r.errors:
        print(paint(f"✗ {len(r.errors)} error(s) to fix before publishing.", "1;31"))
        return 1
    print(paint(f"✓ Looks good! {vault_count} vault item(s) ready to publish.", "1;32")
          + (f" ({len(r.warnings)} suggestion(s) above.)" if r.warnings else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
