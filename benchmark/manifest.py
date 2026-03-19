from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from .schemas import BenchmarkDocument, BenchmarkExample, ManifestBundle


def _ensure_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _resolve_path(manifest_path: Path, document_path: str) -> Path:
    path = Path(document_path)
    if path.is_absolute():
        return path
    return (manifest_path.parent / path).resolve()


def _coerce_examples(
    records: Iterable[dict[str, Any]],
    manifest_path: Path,
) -> ManifestBundle:
    records = list(records)
    dataset_name = "custom_manifest"
    documents: dict[str, BenchmarkDocument] = {}
    examples: list[BenchmarkExample] = []

    for index, record in enumerate(records):
        document_id = str(record["document_id"])
        document_path = _resolve_path(manifest_path, str(record["document_path"]))
        format_type = str(
            record.get("format_type") or document_path.suffix.lower().lstrip(".")
        ).lower()
        dataset_name = str(record.get("dataset_name") or dataset_name)

        if document_id not in documents:
            documents[document_id] = BenchmarkDocument(
                document_id=document_id,
                path=document_path,
                format_type=format_type,
                metadata=dict(record.get("document_metadata") or {}),
            )

        answers = [str(item).strip() for item in _ensure_list(record.get("answers"))]
        if not answers:
            answer = str(record.get("answer", "")).strip()
            if answer:
                answers = [answer]

        examples.append(
            BenchmarkExample(
                example_id=str(record.get("example_id") or f"{document_id}_{index}"),
                document_id=document_id,
                question=str(record["question"]).strip(),
                answers=answers,
                evidence_pages=_ensure_list(record.get("evidence_pages")),
                evidence_sources=[
                    str(item).strip()
                    for item in _ensure_list(record.get("evidence_sources"))
                    if str(item).strip()
                ],
                metadata=dict(record.get("metadata") or {}),
            )
        )

    return ManifestBundle(
        dataset_name=dataset_name,
        manifest_path=manifest_path,
        documents=documents,
        examples=examples,
    )


def load_manifest(manifest_path: str | Path) -> ManifestBundle:
    manifest_path = Path(manifest_path).resolve()
    suffix = manifest_path.suffix.lower()
    raw = manifest_path.read_text(encoding="utf-8")

    if suffix == ".jsonl":
        records = [json.loads(line) for line in raw.splitlines() if line.strip()]
        return _coerce_examples(records, manifest_path)

    payload = json.loads(raw)
    if isinstance(payload, list):
        return _coerce_examples(payload, manifest_path)

    if not isinstance(payload, dict):
        raise ValueError(f"Unsupported manifest payload type: {type(payload)!r}")

    dataset_name = str(payload.get("dataset_name") or "custom_manifest")
    examples_payload = payload.get("examples", [])
    bundle = _coerce_examples(examples_payload, manifest_path)
    bundle.dataset_name = dataset_name
    return bundle


def write_manifest(
    output_path: str | Path,
    dataset_name: str,
    records: list[dict[str, Any]],
) -> Path:
    output_path = Path(output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "dataset_name": dataset_name,
        "examples": records,
    }
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return output_path
