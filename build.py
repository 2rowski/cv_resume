"""Buduje CV z cv.yaml.

Wynik:
  docs/index.html                     strona WWW (GitHub Pages) – bez telefonu
  docs/<Imie_Nazwisko>_CV_EN|PL.pdf   PDF-y do pobrania ze strony – bez telefonu
  out/<Imie_Nazwisko>_CV_EN|PL.pdf    PDF-y do wysyłki rekruterom – z telefonem (nie trafiają do repo)

Użycie:
  .venv\\Scripts\\python build.py           # strona + wszystkie PDF-y
  .venv\\Scripts\\python build.py --no-pdf  # tylko strona
"""

from __future__ import annotations

import argparse
import base64
import copy
import datetime as dt
import html
import json
import mimetypes
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
OUT = ROOT / "out"
BUILD = ROOT / "build"
LANGS = ("en", "pl")

BROWSER_CANDIDATES = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def slug(name: str) -> str:
    name = name.replace("ł", "l").replace("Ł", "L")
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return "_".join(ascii_name.split())


def data_uri(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"


def tr(value, lang: str) -> str:
    if isinstance(value, dict):
        return value.get(lang) or value.get("en") or ""
    return "" if value is None else str(value)


def split_template() -> tuple[str, str]:
    text = (ROOT / "template.html").read_text(encoding="utf-8")
    head, body = text.split("<!--BODY-->", 1)
    return head, body


def render(cv: dict, build: dict, *, full_document: bool) -> str:
    head, body = split_template()
    payload = json.dumps({"cv": cv, "build": build}, ensure_ascii=False, default=str)
    payload = payload.replace("</", "<\\/")  # nie zamyka znacznika <script> przedwcześnie
    body = body.replace("__CV_JSON__", payload)
    if not full_document:
        return head + body

    site = cv.get("site") or {}
    lang = build.get("lang") or "en"
    description = html.escape(" ".join(tr(cv["basics"].get("summary"), lang).split()), quote=True)
    meta = [
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">',
        f'<meta name="description" content="{description}">',
        '<meta property="og:type" content="profile">',
        f'<meta property="og:title" content="{html.escape(cv["basics"]["name"])} – CV">',
        f'<meta property="og:description" content="{description}">',
    ]
    if site.get("noindex", True):
        meta.append('<meta name="robots" content="noindex, nofollow">')
    return (
        f'<!doctype html>\n<html lang="{lang}">\n<head>\n'
        + "\n".join(meta)
        + "\n"
        + head.strip()
        + "\n</head>\n<body>\n"
        + body.strip()
        + "\n</body>\n</html>\n"
    )


def find_browser() -> str | None:
    for candidate in BROWSER_CANDIDATES:
        if Path(candidate).exists():
            return candidate
    for name in ("msedge", "chrome", "chromium", "google-chrome"):
        found = shutil.which(name)
        if found:
            return found
    return None


def print_pdf(browser: str, html_path: Path, pdf_path: Path) -> None:
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as profile:
        cmd = [
            browser,
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-extensions",
            f"--user-data-dir={profile}",
            "--no-pdf-header-footer",
            "--print-to-pdf-no-header",
            "--run-all-compositor-stages-before-draw",
            "--virtual-time-budget=10000",
            f"--print-to-pdf={pdf_path}",
            html_path.as_uri(),
        ]
        subprocess.run(cmd, check=True, timeout=180, capture_output=True)
    if not pdf_path.exists() or pdf_path.stat().st_size == 0:
        raise RuntimeError(f"Przeglądarka nie utworzyła pliku {pdf_path}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Buduje stronę i PDF-y CV z cv.yaml")
    parser.add_argument("--no-pdf", action="store_true", help="tylko strona WWW, bez PDF-ów")
    args = parser.parse_args()

    cv = load_yaml(ROOT / "cv.yaml")
    private = load_yaml(ROOT / "private.yaml")

    photo = cv["basics"].get("photo")
    if photo:
        cv["basics"]["photo"] = data_uri(ROOT / photo)

    today = dt.date.today().isoformat()
    base = slug(cv["basics"]["name"])
    pdf_names = {lang: f"{base}_CV_{lang.upper()}.pdf" for lang in LANGS}
    github = cv["basics"].get("github")
    repo = f"{github.rstrip('/')}/cv" if github else None

    # Strona WWW: bez telefonu i bez klauzuli RODO
    web_cv = copy.deepcopy(cv)
    web_cv.pop("gdpr_clause", None)
    web_build = {"mode": "web", "generated": today, "pdf": pdf_names, "repo": repo}

    DOCS.mkdir(exist_ok=True)
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    (DOCS / "index.html").write_text(render(web_cv, web_build, full_document=True), encoding="utf-8")
    print("OK  docs/index.html")

    # Podgląd na claude.ai (fragment HTML, bez przycisku PDF – tam pobieranie plików nie działa)
    BUILD.mkdir(exist_ok=True)
    preview_build = {**web_build, "pdf": None}
    (BUILD / "preview-fragment.html").write_text(render(web_cv, preview_build, full_document=False), encoding="utf-8")

    if args.no_pdf:
        return 0

    browser = find_browser()
    if not browser:
        print("UWAGA: nie znaleziono Edge ani Chrome – PDF-y pominięte.", file=sys.stderr)
        return 1

    variants = [
        (DOCS, None),                   # publiczne – do pobrania ze strony
        (OUT, private.get("phone")),    # prywatne – do wysyłki
    ]
    for target, phone in variants:
        for lang in LANGS:
            build = {"mode": "print", "lang": lang, "generated": today, "phone": phone, "gdpr": True}
            html_path = BUILD / f"print-{target.name}-{lang}.html"
            html_path.write_text(render(cv, build, full_document=True), encoding="utf-8")
            pdf_path = target / pdf_names[lang]
            print_pdf(browser, html_path, pdf_path)
            print(f"OK  {pdf_path.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
