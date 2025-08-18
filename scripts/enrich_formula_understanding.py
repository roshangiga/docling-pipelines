from pathlib import Path
from datetime import datetime

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat


def run_formula_enrichment(pdf_path: Path, out_dir: Path) -> None:
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_formula_enrichment = True

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    doc = converter.convert(str(pdf_path)).document

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = f"{pdf_path.stem}__formula__{ts}"

    # Markdown export (formulas appear as LaTeX)
    md_path = out_dir / f"{base}.md"
    md_path.write_text(doc.export_to_markdown(), encoding="utf-8")

    # HTML export leverages MathML rendering for formulas
    html_path = out_dir / f"{base}.html"
    html_path.write_text(doc.export_to_html(), encoding="utf-8")

    print(f"Wrote: {md_path}")
    print(f"Wrote: {html_path}")


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    src_dir = project_root / "source"
    out_dir = project_root / "output"
    out_dir.mkdir(parents=True, exist_ok=True)

    pdfs = [p for p in src_dir.iterdir() if p.is_file() and p.suffix.lower() == ".pdf"]
    if not pdfs:
        print(f"No PDFs found in {src_dir}. Add a PDF with formulas and rerun.")
        return 1

    for pdf in pdfs:
        try:
            run_formula_enrichment(pdf, out_dir)
        except Exception as e:
            print(f"Failed formula enrichment for {pdf}: {e}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
