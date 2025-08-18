import re
from pathlib import Path
from datetime import datetime

from docling.document_converter import DocumentConverter


INLINE_MATH = re.compile(r"(?<!\\)\$(.+?)(?<!\\)\$")
BLOCK_MATH = re.compile(r"(?ms)^\s*\$\$(.+?)\$\$\s*$")


def extract_equations(markdown_text: str) -> dict:
    inline = INLINE_MATH.findall(markdown_text) if markdown_text else []
    block = BLOCK_MATH.findall(markdown_text) if markdown_text else []
    return {"inline": inline, "block": block}


def process_file(src_path: Path, out_dir: Path) -> None:
    conv = DocumentConverter()
    doc = conv.convert(str(src_path)).document

    md = doc.export_to_markdown()
    eq = extract_equations(md)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = f"{src_path.stem}__math__{ts}"
    md_path = out_dir / f"{base}.md"
    eq_path = out_dir / f"{base}.equations.txt"

    md_path.write_text(md, encoding="utf-8")

    lines = ["# Extracted equations\n"]
    if eq["block"]:
        lines.append("## Block equations ($$...$$)\n")
        for i, e in enumerate(eq["block"], 1):
            lines.append(f"[{i}] $$ {e.strip()} $$\n")
    if eq["inline"]:
        lines.append("\n## Inline equations ($...$)\n")
        for i, e in enumerate(eq["inline"], 1):
            lines.append(f"({i}) $ {e.strip()} $\n")
    eq_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote: {md_path}")
    print(f"Wrote: {eq_path}")


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    src_dir = project_root / "source"
    out_dir = project_root / "output"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Accept common doc types
    exts = {".pdf", ".docx", ".pptx", ".md", ".html"}
    sources = [p for p in src_dir.iterdir() if p.is_file() and p.suffix.lower() in exts]

    if not sources:
        print(f"No input files found in {src_dir}. Add files (e.g., PDF with formulas) and rerun.")
        return 1

    for p in sources:
        try:
            process_file(p, out_dir)
        except Exception as e:
            print(f"Failed math processing for {p}: {e}")

    return 0


if __name__ == "__main__":
    import sys
    raise SystemExit(main())
