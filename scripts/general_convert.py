import json
import sys
from pathlib import Path
from datetime import datetime

from docling.document_converter import DocumentConverter


def convert_file(converter: DocumentConverter, src_path: Path, out_dir: Path) -> None:
    conv_res = converter.convert(str(src_path))
    doc = conv_res.document

    stem = src_path.stem
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    md_path = out_dir / f"{stem}__{ts}.md"
    json_path = out_dir / f"{stem}__{ts}.json"

    md_path.write_text(doc.export_to_markdown(), encoding="utf-8")

    try:
        payload = doc.export_to_dict()
    except Exception:
        # Fallback if API changes; dump minimal structure
        payload = {"meta": {"source": str(src_path)}, "markdown": doc.export_to_markdown()}
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Wrote: {md_path}")
    print(f"Wrote: {json_path}")


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    src_dir = project_root / "source"
    out_dir = project_root / "output"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Gather common doc types; extend as needed
    exts = {".pdf", ".docx", ".pptx", ".xlsx", ".md", ".html"}
    sources = [p for p in src_dir.iterdir() if p.is_file() and p.suffix.lower() in exts]

    if not sources:
        print(f"No input files found in {src_dir}. Add files (e.g., PDF) and rerun.")
        return 1

    converter = DocumentConverter()

    for path in sources:
        try:
            convert_file(converter, path, out_dir)
        except Exception as e:
            print(f"Failed to convert {path}: {e}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
