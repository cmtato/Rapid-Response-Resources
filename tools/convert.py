#!/usr/bin/env python3
"""Regenerates the docs/ site from the original files in resources/.

Usage:
    tools/convert.py                          # rebuild every entry in resources.json
    tools/convert.py "resources/slides/X.pptx"  # rebuild just the matching entry
    tools/convert.py --index                  # only regenerate docs/index.html

Requires `soffice` (LibreOffice) on PATH, and openpyxl for xlsx-interactive
entries (pip install -r tools/requirements.txt).

Everything under a resource's docsDir is generated: index.html, any
interactive pages, content.html / slides.pdf / sheet-data*.json. The
hand-maintained files are docs/assets/* and the README.
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
REPO_ROOT = TOOLS.parent
MANIFEST_PATH = TOOLS / "resources.json"


def load_manifest():
    with open(MANIFEST_PATH) as f:
        return json.load(f)


def raw_url(manifest, source):
    """Direct-download URL for an original file, served from the repo."""
    encoded = "/".join(urllib.parse.quote(part) for part in source.split("/"))
    return f"https://raw.githubusercontent.com/{manifest['repo']}/main/{encoded}"


def esc(text):
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


# ---------------------------------------------------------------- conversions

def soffice_convert(src, out_format, outdir):
    subprocess.run(
        ["soffice", "--headless", "--convert-to", out_format,
         "--outdir", str(outdir), str(src)],
        check=True, capture_output=True, text=True,
    )
    produced = list(Path(outdir).glob(f"*.{out_format}"))
    if not produced:
        raise RuntimeError(f"soffice produced no .{out_format} for {src}")
    return produced[0]


def inject_css(html_path, css):
    text = html_path.read_text(encoding="utf-8")
    marker = '<style type="text/css">'
    idx = text.find(marker)
    if idx == -1:
        raise RuntimeError(f"no <style> block to patch in {html_path}")
    at = idx + len(marker)
    html_path.write_text(text[:at] + "\n\t\t" + css + "\n" + text[at:], encoding="utf-8")


def external_links_new_tab(html_path):
    """Open external links in a new tab, so they don't hijack the iframe.

    Only absolute http(s) links are touched; in-document anchors (e.g. a
    document's own table of contents) must stay in the same frame.
    """
    text = html_path.read_text(encoding="utf-8", errors="replace")
    patched, n = re.subn(r'<a href="(https?://[^"]*)"',
                         r'<a href="\1" target="_blank" rel="noopener"',
                         text)
    html_path.write_text(patched, encoding="utf-8")
    return n


def build_content_html(src, docs_dir, css):
    """docx/xlsx -> content.html (+ any extracted images) in docs_dir."""
    for stale in list(docs_dir.glob("*_html_*")):
        stale.unlink()
    with tempfile.TemporaryDirectory() as tmp:
        html = soffice_convert(src, "html", tmp)
        if css:
            inject_css(html, css)
        n = external_links_new_tab(html)
        if n:
            print(f"      {n} external link(s) set to open in a new tab")
        shutil.copy(html, docs_dir / "content.html")
        for asset in Path(tmp).glob("*_html_*"):
            shutil.copy(asset, docs_dir / asset.name)


def build_slides_pdf(src, docs_dir):
    with tempfile.TemporaryDirectory() as tmp:
        pdf = soffice_convert(src, "pdf", tmp)
        shutil.copy(pdf, docs_dir / "slides.pdf")


def build_sheet_data(src, docs_dir, sheets):
    sys.path.insert(0, str(TOOLS))
    import extract_sheet
    for sheet in sheets:
        data = extract_sheet.extract(str(src), sheet["name"])
        with open(docs_dir / sheet["output"], "w") as f:
            json.dump(data, f, indent=0)
        print(f"      {sheet['output']}: {len(data['cells'])} cells, "
              f"{len(data['merges'])} merges")


# ------------------------------------------------------------- page scaffolds

SHELL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="../../assets/style.css">
</head>
<body>
<header class="site">
  <div class="inner">
    <a class="home" href="../../index.html">Rapid Response Resources</a>
    <span class="crumb">/ {section} / {title}</span>
  </div>
</header>
<main{main_class}>
  <div class="resource-header">
    <div>
      <h1>{title}</h1>
      <div class="meta">{meta}</div>
    </div>
    <a class="btn" href="{download}" download="{filename}">Download original {ext}</a>
  </div>
{tabs}{body}
</main>
{scripts}</body>
</html>
"""

META = {
    "pptx": "Slide deck · converted from PowerPoint (PPTX → PDF)",
    "docx": "Document · converted from Word (DOCX → HTML)",
    "xlsx-static": "Excel workbook · converted from XLSX → HTML (formulas are not interactive)",
}


def tab_bar(entry, active):
    """Static view + one tab per interactive sheet."""
    sheets = entry.get("sheets") or []
    if not sheets:
        return ""
    links = [("index.html", "Static view")] + [(s["page"], s["label"]) for s in sheets]
    out = ['  <div class="tabs">']
    for href, label in links:
        cls = ' class="active"' if href == active else ""
        out.append(f'    <a href="{href}"{cls}>{esc(label)}</a>')
    out.append("  </div>")
    return "\n".join(out) + "\n"


def write_pages(manifest, entry, docs_dir):
    src = entry["source"]
    filename = Path(src).name
    ext = Path(src).suffix
    title = esc(entry["title"])
    download = raw_url(manifest, src)
    etype = entry["type"]

    if etype == "pptx":
        body = '  <iframe class="viewer-frame" src="slides.pdf" title="{t} slides"></iframe>'.format(t=title)
        main_class, scripts = ' class="wide"', ""
    else:
        # Word/Excel conversions keep their source page geometry; landscape
        # documents exceed 1400px, so give these the full viewport width.
        body = '  <iframe class="viewer-frame" src="content.html" title="{t}"></iframe>'.format(t=title)
        main_class, scripts = ' class="full"', ""

    (docs_dir / "index.html").write_text(SHELL.format(
        title=title, section=esc(entry.get("section", "")),
        meta=META.get(etype, META["xlsx-static"]),
        download=download, filename=filename, ext=ext,
        tabs=tab_bar(entry, "index.html"), body=body,
        main_class=main_class, scripts=scripts,
    ), encoding="utf-8")

    for sheet in entry.get("sheets") or []:
        body = '  <div id="sheet-container"></div>'
        scripts = ('<script src="../../assets/vendor/hyperformula.full.min.js"></script>\n'
                   '<script src="../../assets/calc-sheet.js"></script>\n'
                   '<script>\n  renderCalcSheet("sheet-container", "%s");\n</script>\n'
                   % sheet["output"])
        (docs_dir / sheet["page"]).write_text(SHELL.format(
            title=title, section=esc(entry.get("section", "")),
            meta=f'Live calculator ({esc(sheet["name"])}) · edit "X =" to rescale reagent volumes',
            download=download, filename=filename, ext=ext,
            tabs=tab_bar(entry, sheet["page"]), body=body,
            main_class=' class="wide"', scripts=scripts,
        ), encoding="utf-8")


# -------------------------------------------------------------- orchestration

def run_entry(manifest, entry):
    if entry["type"] == "download-only":
        print(f"Skipping (download-only): {entry['source']}")
        return
    src = REPO_ROOT / entry["source"]
    docs_dir = REPO_ROOT / entry["docsDir"]
    if not src.exists():
        raise FileNotFoundError(f"source missing: {src}")
    docs_dir.mkdir(parents=True, exist_ok=True)

    print(f"{entry['source']}  ({entry['type']})")
    etype = entry["type"]
    if etype == "pptx":
        build_slides_pdf(src, docs_dir)
    elif etype in ("docx", "xlsx-static"):
        build_content_html(src, docs_dir, manifest.get("fontCss"))
    elif etype == "xlsx-interactive":
        build_sheet_data(src, docs_dir, entry["sheets"])
        build_content_html(src, docs_dir, manifest.get("fontCss"))
    else:
        raise ValueError(f"unknown type: {etype}")
    write_pages(manifest, entry, docs_dir)
    print(f"      -> {entry['docsDir']}/")


INDEX = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Rapid Response Resources</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<header class="site">
  <div class="inner">
    <a class="home" href="index.html">Rapid Response Resources</a>
    <span class="crumb">Metagenomics sequencing &amp; analysis training materials</span>
  </div>
</header>
<main>
  <p>All hosted resources, grouped by type. See the <a href="https://github.com/{repo}">README</a> for the Illumina/Nanopore workflow view.</p>
{sections}</main>
</body>
</html>
"""


def write_index(manifest):
    order = ["Protocols", "Slide Decks", "Worksheets"]
    kinds = {"pptx": "PPTX → PDF", "docx": "DOCX → HTML",
             "xlsx-static": "XLSX → HTML", "xlsx-interactive": "XLSX → HTML + calculator"}
    blocks = []
    for section in order:
        items = [e for e in manifest["entries"]
                 if e.get("section") == section and e["type"] != "download-only"]
        if not items:
            continue
        rows = "\n".join(
            f'      <li>\n'
            f'        <a class="title" href="{e["docsDir"][len("docs/"):]}/index.html"'
            f' target="_blank" rel="noopener">{esc(e["title"])}</a>\n'
            f'        <span class="kind">{kinds[e["type"]]}</span>\n'
            f'      </li>' for e in items)
        blocks.append(f'  <section class="group">\n    <h2>{section}</h2>\n'
                      f'    <ul class="resource-list">\n{rows}\n    </ul>\n  </section>\n')
    (REPO_ROOT / "docs" / "index.html").write_text(
        INDEX.format(repo=manifest["repo"], sections="\n".join(blocks)), encoding="utf-8")
    print("regenerated docs/index.html")


def main():
    manifest = load_manifest()
    args = sys.argv[1:]

    if args == ["--index"]:
        write_index(manifest)
        return

    entries = manifest["entries"]
    if args:
        target = args[0]
        entries = [e for e in entries if e["source"] in (target, str(REPO_ROOT / target))]
        if not entries:
            print(f"No manifest entry for: {target}", file=sys.stderr)
            sys.exit(1)

    for entry in entries:
        run_entry(manifest, entry)
    if not args:
        write_index(manifest)


if __name__ == "__main__":
    main()
