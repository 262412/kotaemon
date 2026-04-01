import json

from benchmark.manifest import load_manifest
from benchmark.normalizers import (
    normalize_financebench_manifest,
    normalize_format_robustness_manifest,
)


def test_normalize_format_robustness_manifest(tmp_path):
    pdf_dir = tmp_path / "pdf"
    pdf_dir.mkdir(parents=True)
    (pdf_dir / "1_sample.pdf").write_text("dummy", encoding="utf-8")
    (pdf_dir / "1_metadata.json").write_text(
        json.dumps(
            {
                "questions": [
                    {"question": "What is this?", "answer": "sample"},
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    manifest_path = tmp_path / "format.json"
    normalize_format_robustness_manifest(tmp_path, manifest_path)
    bundle = load_manifest(manifest_path)

    assert bundle.dataset_name == "format_robustness"
    assert len(bundle.documents) == 1
    assert len(bundle.examples) == 1
    assert bundle.examples[0].answers == ["sample"]


def test_normalize_financebench_manifest(tmp_path):
    data_dir = tmp_path / "data"
    pdf_dir = tmp_path / "pdfs"
    data_dir.mkdir()
    pdf_dir.mkdir()
    (pdf_dir / "company_a.pdf").write_text("pdf", encoding="utf-8")
    (data_dir / "financebench_open_source.jsonl").write_text(
        json.dumps(
            {
                "id": "1",
                "doc_name": "company_a.pdf",
                "question": "What is revenue?",
                "answer": "10",
                "evidence_strings": ["Revenue was 10."],
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    manifest_path = tmp_path / "financebench.json"
    normalize_financebench_manifest(tmp_path, manifest_path)
    bundle = load_manifest(manifest_path)

    assert bundle.dataset_name == "financebench"
    assert len(bundle.examples) == 1
    assert bundle.examples[0].evidence_sources == ["Revenue was 10."]
