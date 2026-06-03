import re
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / "static"


def minify_js(content: str) -> str:
    # remove single-line comments
    content = re.sub(r"//.*?\n", "\n", content)
    # remove multi-line comments
    content = re.sub(r"/\*[\s\S]*?\*/", "", content)
    # collapse whitespace
    content = re.sub(r"\s+", " ", content)
    return content.strip()


def minify_css(content: str) -> str:
    # remove comments
    content = re.sub(r"/\*[\s\S]*?\*/", "", content)
    # collapse whitespace
    content = re.sub(r"\s+", " ", content)
    # remove spaces around symbols
    content = re.sub(r"\s*([{};:,])\s*", r"\1", content)
    return content.strip()


def run():
    js_dir = BASE / "javascript"
    css_dir = BASE / "css"

    for path in js_dir.glob("*.js"):
        try:
            text = path.read_text(encoding="utf-8")
            minified = minify_js(text)
            out = path.with_suffix(".min.js")
            out.write_text(minified, encoding="utf-8")
            print(f"Minified {path.name} -> {out.name}")
        except Exception as e:
            print(f"Failed to minify {path}: {e}")

    for path in css_dir.glob("*.css"):
        try:
            text = path.read_text(encoding="utf-8")
            minified = minify_css(text)
            out = path.with_suffix(".min.css")
            out.write_text(minified, encoding="utf-8")
            print(f"Minified {path.name} -> {out.name}")
        except Exception as e:
            print(f"Failed to minify {path}: {e}")


if __name__ == "__main__":
    run()
