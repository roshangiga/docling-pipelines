# Docling Project Skeleton

This project sets up a simple workflow using Docling 2.45.0.

- Input documents go in `source/`.
- Results are written to `output/`.
- Four example scripts are provided under `scripts/`:
  - `general_convert.py` — basic PDF/URL conversion to Markdown and JSON.
  - `vlm_image_understanding.py` — use the VLM pipeline (SmolDocling) for image-heavy PDFs.
  - `maths_processing.py` — convert and extract math snippets from Markdown.
  - `contextual_hybrid_chunking.py` — chunk a document and produce context-enriched text using HybridChunker.
  - `enrich_formula_understanding.py` — enable Formula Understanding enrichment to extract LaTeX and render MathML in HTML.
  - `enrich_picture_description.py` — enable Picture Description enrichment (image captioning) using local or remote VLMs.

## Setup

1) Create/activate your virtual environment (optional if you already use `.venv/`).

2) Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

- Put your input files into `source/` (e.g., PDFs).
- Run a script, e.g.:

```bash
python scripts/general_convert.py
python scripts/vlm_image_understanding.py
python scripts/maths_processing.py
python scripts/contextual_hybrid_chunking.py
python scripts/enrich_formula_understanding.py
python scripts/enrich_picture_description.py
```

Outputs will be written to `output/`.

## Jupyter: Run pipelines in a notebook

Use the single comprehensive notebook `Docling_Pipelines.ipynb` to run everything interactively (all scripts + combined flow):

1) Open `Docling_Pipelines.ipynb` in Jupyter (VS Code, JupyterLab, or Notebook).
2) Ensure dependencies are installed (first cell runs `pip install -r requirements.txt`).
3) Put inputs in `source/` (PDF, MD, DOCX, HTML).
4) Execute cells in order:
   - Run existing scripts directly using `%run` cells:
     - `general_convert.py` — basic conversion to Markdown/JSON.
     - `vlm_image_understanding.py` — VLM-assisted image understanding for PDFs.
     - `maths_processing.py` — convert and extract math snippets.
     - `contextual_hybrid_chunking.py` — create raw + context-enriched chunks.
     - `enrich_formula_understanding.py` — enable Formula Understanding (LaTeX/MathML outputs).
     - `enrich_picture_description.py` — enable Picture Description (figure captions via VLM).
   - Use the "One-pass combination" cell to enable both Picture Description and Formula Understanding, then run contextual hybrid chunking in a single flow.
   - List output artifacts written to `output/`.

This notebook consolidates all use cases and shows modality-specific enrichments plus the contextual hybrid chunking flow without modifying the scripts.

## Notes

- VLM pipeline example follows Docling docs: `VlmPipeline` with default SmolDocling backend.
- Hybrid chunking follows Docling docs: `HybridChunker` and `contextualize()` for enriched text.
- The math script does not use special Docling options; it converts to Markdown and extracts equations heuristically.
 - Formula Understanding enrichment (`enrich_formula_understanding.py`) follows Docling docs by setting `PdfPipelineOptions.do_formula_enrichment = True`. The HTML export (`export_to_html`) will leverage MathML rendering.
 - Picture Description enrichment (`enrich_picture_description.py`) follows Docling docs by setting `PdfPipelineOptions.do_picture_description = True`. You can optionally select presets like `smolvlm_picture_description` or `granite_picture_description` in the script.
