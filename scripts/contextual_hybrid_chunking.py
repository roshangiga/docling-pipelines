from pathlib import Path
from datetime import datetime
from typing import Iterable

from docling.document_converter import DocumentConverter
from docling.chunking import HybridChunker


def chunk_and_write(doc_source: Path, out_dir: Path) -> None:
    dl_doc = DocumentConverter().convert(str(doc_source)).document

    chunker = HybridChunker()
    chunk_iter = chunker.chunk(dl_doc=dl_doc)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = f"{doc_source.stem}__chunks__{ts}"
    txt_path = out_dir / f"{base}.txt"
    jsonl_path = out_dir / f"{base}.jsonl"

    with txt_path.open("w", encoding="utf-8") as f_txt, jsonl_path.open("w", encoding="utf-8") as f_jsonl:
        for i, chunk in enumerate(chunk_iter):
            # Raw chunk text
            raw_text = chunk.text or ""
            # Context-enriched text recommended for embedding/search
            enriched = chunker.contextualize(chunk=chunk)

            f_txt.write(f"=== {i} ===\n")
            f_txt.write("-- raw --\n")
            f_txt.write(raw_text)
            f_txt.write("\n-- enriched --\n")
            f_txt.write(enriched)
            f_txt.write("\n\n")

            # Minimal JSONL per chunk
            import json  # local import to avoid top-level if unused
            f_jsonl.write(
                json.dumps(
                    {
                        "index": i,
                        "raw": raw_text,
                        "enriched": enriched,
                        # include simple structural hints if present
                        "path": getattr(chunk, "path", None),
                        "id": getattr(chunk, "id", None),
                    },
                    ensure_ascii=False,
                )
            )
            f_jsonl.write("\n")

    print(f"Wrote: {txt_path}")
    print(f"Wrote: {jsonl_path}")


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    src_dir = project_root / "source"
    out_dir = project_root / "output"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Try Markdown first (like docs example), then PDFs and others
    preferred_order = [".md", ".pdf", ".docx", ".html"]
    sources: list[Path] = []
    for ext in preferred_order:
        sources.extend([p for p in src_dir.iterdir() if p.is_file() and p.suffix.lower() == ext])
    if not sources:
        print(f"No suitable files found in {src_dir}. Add a .md or .pdf and rerun.")
        return 1

    for src in sources:
        try:
            chunk_and_write(src, out_dir)
        except Exception as e:
            print(f"Failed hybrid chunking for {src}: {e}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
