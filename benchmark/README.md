# Benchmark

This is the first clean benchmark framework for this repo.

It is built around one normalized manifest format so we can compare:

- local `PDF / DOC / DOCX / PPT / PPTX` robustness
- `FinanceBench`
- `SlideVQA`
- future `MP-DocVQA / QASPER / DUDE` conversions without rewriting the runner

## What It Measures

- answer `EM`
- answer `F1`
- answer `ANLS`
- page hit rate when gold pages exist
- citation recall when gold evidence strings exist
- parse and indexing time per document
- retrieval and generation latency per example

## Manifest Format

Each example points to one local document:

```json
{
  "dataset_name": "format_robustness",
  "examples": [
    {
      "example_id": "pdf_1_0",
      "document_id": "pdf_1",
      "document_path": "data/test_documents/pdf/1_example.pdf",
      "format_type": "pdf",
      "question": "What is ...?",
      "answers": ["..."],
      "evidence_pages": [1],
      "evidence_sources": ["file.pdf#page:1"],
      "metadata": {}
    }
  ]
}
```

## Quick Start

Build a manifest from the local format-robustness folder:

```powershell
python -m benchmark normalize-format-robustness `
  --source-dir data/test_documents `
  --output benchmark/manifests/format_robustness.json
```

Run the benchmark:

```powershell
python -m benchmark run `
  --manifest benchmark/manifests/format_robustness.json `
  --suite-name format-robustness-v1 `
  --reader-mode default `
  --retrieval-mode hybrid `
  --top-k 5
```

Outputs are written under `benchmark/artifacts/`.

## FinanceBench

Normalize the official open-source release:

```powershell
python -m benchmark normalize-financebench `
  --source-dir D:\datasets\financebench `
  --output benchmark/manifests/financebench.json
```

## SlideVQA

This converter expects:

- a JSON annotation file
- a local document root that contains matching deck files by stem

```powershell
python -m benchmark normalize-slidevqa `
  --annotations D:\datasets\slidevqa\test.json `
  --documents-root D:\datasets\slidevqa\documents `
  --output benchmark/manifests/slidevqa.json
```

## Notes

- This first version is intentionally text-first. It reuses the repo's parsing, chunking, embedding, and prompt flow, but does not yet implement a true page-image retriever.
- `MP-DocVQA / DUDE / QASPER` can plug in by converting their raw data into the same manifest shape.
- The runner caches document parsing and indexing per document inside one run, so repeated questions on the same file are benchmarked as query-time work instead of repeated ingestion.
