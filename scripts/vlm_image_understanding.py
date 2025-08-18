from pathlib import Path
from datetime import datetime

from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.pipeline.vlm_pipeline import VlmPipeline


def convert_with_vlm(pdf_path: Path, out_dir: Path) -> None:
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_cls=VlmPipeline,
            ),
        }
    )

    doc = converter.convert(source=str(pdf_path)).document

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    md_path = out_dir / f"{pdf_path.stem}__vlm__{ts}.md"
    md_path.write_text(doc.export_to_markdown(), encoding="utf-8")
    print(f"Wrote: {md_path}")


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    src_dir = project_root / "source"
    out_dir = project_root / "output"
    out_dir.mkdir(parents=True, exist_ok=True)

    pdfs = [p for p in src_dir.iterdir() if p.is_file() and p.suffix.lower() == ".pdf"]
    if not pdfs:
        print(f"No PDFs found in {src_dir}. Add PDFs and rerun.")
        return 1

    for pdf in pdfs:
        try:
            convert_with_vlm(pdf, out_dir)
        except Exception as e:
            print(f"Failed VLM conversion for {pdf}: {e}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
