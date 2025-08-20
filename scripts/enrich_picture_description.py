import shutil
from pathlib import Path
from datetime import datetime

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat


def run_picture_description(pdf_path: Path, out_dir: Path, archive_dir: Path) -> None:
    print(f"Processing file: {pdf_path.name}")
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_picture_description = True

    # Optional: choose a specific vision model preset, e.g. SmolVLM or Granite.
    # from docling.datamodel.pipeline_options import smolvlm_picture_description
    # pipeline_options.picture_description_options = smolvlm_picture_description

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    doc = converter.convert(str(pdf_path)).document

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = f"{pdf_path.stem}__picdesc__{ts}"

    md_path = out_dir / f"{base}.md"
    md_path.write_text(doc.export_to_markdown(), encoding="utf-8")

    print(f"Wrote: {md_path}")
    
    # Move processed file to archive
    archive_path = archive_dir / pdf_path.name
    shutil.move(str(pdf_path), str(archive_path))
    print(f"Moved {pdf_path.name} to archive")
    print(f"Finished processing: {pdf_path.name}")


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    src_dir = project_root / "source"
    out_dir = project_root / "output"
    archive_dir = project_root / "archive"
    out_dir.mkdir(parents=True, exist_ok=True)
    archive_dir.mkdir(parents=True, exist_ok=True)

    pdfs = [p for p in src_dir.iterdir() if p.is_file() and p.suffix.lower() == ".pdf"]
    if not pdfs:
        print(f"No PDFs found in {src_dir}. Add an image-heavy PDF and rerun.")
        return 1

    for pdf in pdfs:
        try:
            run_picture_description(pdf, out_dir, archive_dir)
        except Exception as e:
            print(f"Failed picture description for {pdf}: {e}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
