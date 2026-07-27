"""Tests for Plan-03 unordered-set principle annotation."""

from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from edu_benchmark.benchmark_specification.manifest import sha256_file
from edu_benchmark.benchmark_specification.principle_annotation import (
    CANONICAL_DOCUMENTS,
    CANDIDATE_ANNOTATION_COLUMNS,
    CONTEXT_INPUT_COLUMNS,
    GROUNDING_INPUT_COLUMNS,
    PRINCIPLE_LABEL_COLUMNS,
    REVIEW_QUEUE_COLUMNS,
    RUNTIME_DOCUMENTS,
    THRESHOLD_KEYS,
    build_annotation_inputs,
    compare_annotation_bundles,
    derive_grounding_effect,
    reconcile_annotation_draft,
    validate_annotation_bundle,
    validate_input_pair,
)


def write_csv(
    path: Path, columns: tuple[str, ...], rows: list[dict[str, str]]
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


class PrincipleAnnotationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for relative in dict.fromkeys(CANONICAL_DOCUMENTS + RUNTIME_DOCUMENTS):
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(relative, encoding="utf-8")
        self.output = self.root / "pilot"
        self.input_path = self.root / "grounding.csv"
        rows = []
        for index in range(2):
            row = {
                column: f"{column}-{index}" for column in GROUNDING_INPUT_COLUMNS
            }
            row["benchmark_candidate_id"] = f"C{index}"
            row["sample_id"] = f"S{index}"
            row["grade"] = str(6 + index)
            rows.append(row)
        write_csv(self.input_path, GROUNDING_INPUT_COLUMNS, rows)
        build_annotation_inputs(
            repo_root=self.root,
            grounding_input_path=self.input_path,
            output_dir=self.output,
            created_at="2026-07-27T00:00:00+07:00",
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_inputs_are_isolated_and_hash_locked(self) -> None:
        context_path = self.output / "principle_annotation_pass1_input.csv"
        grounding_path = self.output / "principle_annotation_grounding_input.csv"
        with context_path.open(encoding="utf-8") as handle:
            context_header = next(csv.reader(handle))
        with grounding_path.open(encoding="utf-8") as handle:
            grounding_header = next(csv.reader(handle))
        self.assertEqual(tuple(context_header), CONTEXT_INPUT_COLUMNS)
        self.assertEqual(tuple(grounding_header), GROUNDING_INPUT_COLUMNS)
        self.assertNotIn("gold_response", context_header)
        self.assertNotIn("gold_response", grounding_header)
        result = validate_input_pair(
            repo_root=self.root,
            context_path=context_path,
            grounding_path=grounding_path,
            manifest_path=self.output
            / "principle_annotation_grounding_manifest.json",
        )
        self.assertEqual(result["candidate_count"], 2)
        manifest_path = self.output / "principle_annotation_grounding_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(
            manifest["manifest_version"], "plan03-principle-grounding-v3"
        )
        self.assertTrue(manifest["views"]["grounding"]["gold_response_excluded"])
        before = manifest_path.read_bytes()
        build_annotation_inputs(
            repo_root=self.root,
            grounding_input_path=self.input_path,
            output_dir=self.output,
        )
        self.assertEqual(before, manifest_path.read_bytes())

    def test_grounding_source_with_gold_response_fails_closed(self) -> None:
        rows = list(csv.DictReader(self.input_path.open(encoding="utf-8")))
        path = self.root / "leaking.csv"
        columns = GROUNDING_INPUT_COLUMNS + ("gold_response",)
        for row in rows:
            row["gold_response"] = "leak"
        write_csv(path, columns, rows)
        with self.assertRaisesRegex(ValueError, "must not contain gold_response"):
            build_annotation_inputs(
                repo_root=self.root,
                grounding_input_path=path,
                output_dir=self.root / "bad",
            )

    def test_hash_drift_fails_closed(self) -> None:
        (self.root / CANONICAL_DOCUMENTS[0]).write_text(
            "changed", encoding="utf-8"
        )
        with self.assertRaisesRegex(ValueError, "Locked document hash mismatch"):
            validate_input_pair(
                repo_root=self.root,
                context_path=self.output
                / "principle_annotation_pass1_input.csv",
                grounding_path=self.output
                / "principle_annotation_grounding_input.csv",
                manifest_path=self.output
                / "principle_annotation_grounding_manifest.json",
            )

    def _bundle(
        self,
        name: str,
        coder: str,
        context_sets: tuple[set[str], set[str]],
        *,
        final_sets: tuple[set[str], set[str]] | None = None,
        reconcile: bool = False,
    ) -> Path:
        bundle = self.output / "dual_run" / name
        bundle.mkdir(parents=True)
        final_sets = final_sets or context_sets
        context_metadata = []
        final_metadata = []
        context_labels = []
        final_labels = []
        for index, label_set in enumerate(context_sets):
            base = {column: "" for column in CANDIDATE_ANNOTATION_COLUMNS}
            base.update(
                {
                    "benchmark_candidate_id": f"C{index}",
                    "sample_id": f"S{index}",
                    "student_state_summary": "Trạng thái quan sát được.",
                    "grounding_effect": "not_seen",
                    "coder_id": coder,
                    "review_status": "needs_uet_review",
                }
            )
            context_metadata.append(base)
            after = dict(base)
            after["grounding_effect"] = "unchanged"
            final_metadata.append(after)
            for principle_id in sorted(label_set):
                context_labels.append(
                    {
                        "benchmark_candidate_id": f"C{index}",
                        "principle_id": principle_id,
                        "selection_rationale": "Chức năng độc lập, không thể bỏ.",
                        "context_evidence": "Bằng chứng từ prompt.",
                        "grounding_evidence": "",
                        "coder_id": coder,
                        "review_status": "needs_uet_review",
                    }
                )
            for principle_id in sorted(final_sets[index]):
                final_labels.append(
                    {
                        "benchmark_candidate_id": f"C{index}",
                        "principle_id": principle_id,
                        "selection_rationale": "Chức năng độc lập, không thể bỏ.",
                        "context_evidence": "Bằng chứng từ prompt.",
                        "grounding_evidence": "Căn cứ từ câu hỏi nguồn.",
                        "coder_id": coder,
                        "review_status": "needs_uet_review",
                    }
                )
        write_csv(
            bundle / "principle_annotation_pass1.csv",
            CANDIDATE_ANNOTATION_COLUMNS,
            context_metadata,
        )
        write_csv(
            bundle / "principle_annotation_pass1_labels.csv",
            PRINCIPLE_LABEL_COLUMNS,
            context_labels,
        )
        write_csv(
            bundle / "principle_annotation_final.csv",
            CANDIDATE_ANNOTATION_COLUMNS,
            final_metadata,
        )
        write_csv(
            bundle / "principle_annotation_final_labels.csv",
            PRINCIPLE_LABEL_COLUMNS,
            final_labels,
        )
        write_csv(
            bundle / "principle_annotation_review_queue.csv",
            REVIEW_QUEUE_COLUMNS,
            [],
        )
        if reconcile:
            reconcile_annotation_draft(bundle_dir=bundle, coder_id=coder)
        (bundle / "principle_annotation_run_manifest.json").write_text(
            json.dumps(
                {
                    "manifest_version": "plan03-principle-annotation-run-v3",
                    "coder_id": coder,
                    "candidate_count": 2,
                    "closed": True,
                    "model": "gpt-5.4-mini",
                    "reasoning_effort": "medium",
                    "input_manifest_sha256": sha256_file(
                        self.output
                        / "principle_annotation_grounding_manifest.json"
                    ),
                }
            ),
            encoding="utf-8",
        )
        (bundle / "handoff.md").write_text(
            "Bàn giao tạm thời.", encoding="utf-8"
        )
        return bundle

    def test_bundle_rejects_unknown_principle_and_confirmed_status(self) -> None:
        bundle = self._bundle(
            "annotator_a",
            "A",
            ({"PRINCIPLE-EXPLANATION"}, {"PRINCIPLE-PRACTICE"}),
        )
        path = bundle / "principle_annotation_final_labels.csv"
        rows = list(csv.DictReader(path.open(encoding="utf-8")))
        rows[0]["principle_id"] = "PRINCIPLE-UNKNOWN"
        write_csv(path, PRINCIPLE_LABEL_COLUMNS, rows)
        with self.assertRaisesRegex(ValueError, "unknown principle"):
            validate_annotation_bundle(
                input_dir=self.output, bundle_dir=bundle, coder_id="A"
            )
        rows[0]["principle_id"] = "PRINCIPLE-EXPLANATION"
        rows[0]["review_status"] = "confirmed"
        write_csv(path, PRINCIPLE_LABEL_COLUMNS, rows)
        with self.assertRaisesRegex(ValueError, "invalid label authority"):
            validate_annotation_bundle(
                input_dir=self.output, bundle_dir=bundle, coder_id="A"
            )

    def test_reconciler_derives_set_change_and_queue(self) -> None:
        bundle = self._bundle(
            "annotator_a",
            "A",
            ({"PRINCIPLE-EXPLANATION"}, {"PRINCIPLE-PRACTICE"}),
            final_sets=(
                {"PRINCIPLE-EXPLANATION", "PRINCIPLE-QUESTIONING"},
                {"PRINCIPLE-PRACTICE"},
            ),
        )
        self.assertEqual(
            derive_grounding_effect(
                {"PRINCIPLE-EXPLANATION"},
                {"PRINCIPLE-EXPLANATION", "PRINCIPLE-QUESTIONING"},
                context_gap=False,
                final_gap=False,
            ),
            "changed",
        )
        result = reconcile_annotation_draft(bundle_dir=bundle, coder_id="A")
        self.assertEqual(result["changed_count"], 1)
        final = list(
            csv.DictReader(
                (bundle / "principle_annotation_final.csv").open(
                    encoding="utf-8"
                )
            )
        )
        self.assertEqual(final[0]["grounding_effect"], "changed")
        queue = list(
            csv.DictReader(
                (bundle / "principle_annotation_review_queue.csv").open(
                    encoding="utf-8"
                )
            )
        )
        self.assertEqual(queue[0]["review_reason_codes"], "label_set_changed")

    def test_high_label_count_requires_queue(self) -> None:
        four = {
            "PRINCIPLE-CHALLENGE",
            "PRINCIPLE-EXPLANATION",
            "PRINCIPLE-MODELLING",
            "PRINCIPLE-PRACTICE",
        }
        bundle = self._bundle(
            "annotator_a",
            "A",
            (four, {"PRINCIPLE-PRACTICE"}),
        )
        with self.assertRaisesRegex(ValueError, "Required review queue"):
            validate_annotation_bundle(
                input_dir=self.output, bundle_dir=bundle, coder_id="A"
            )
        reconcile_annotation_draft(bundle_dir=bundle, coder_id="A")
        result = validate_annotation_bundle(
            input_dir=self.output, bundle_dir=bundle, coder_id="A"
        )
        self.assertEqual(result["high_label_count"], 1)

    def test_bundles_compare_with_set_metrics(self) -> None:
        a = self._bundle(
            "annotator_a",
            "A",
            ({"PRINCIPLE-EXPLANATION"}, {"PRINCIPLE-PRACTICE"}),
        )
        b = self._bundle(
            "annotator_b",
            "B",
            (
                {"PRINCIPLE-EXPLANATION"},
                {"PRINCIPLE-PRACTICE", "PRINCIPLE-QUESTIONING"},
            ),
            reconcile=True,
        )
        validate_annotation_bundle(
            input_dir=self.output, bundle_dir=a, coder_id="A"
        )
        validate_annotation_bundle(
            input_dir=self.output, bundle_dir=b, coder_id="B"
        )
        thresholds = {
            "status": "uet_approved",
            "schema_version": "unordered-set-v3",
            "approved_by": "UET-REVIEWER-01",
            "approved_at": "2026-07-27T00:00:00+07:00",
        }
        thresholds.update({key: 0.0 for key in THRESHOLD_KEYS})
        threshold_path = self.output / "dual_run_thresholds_v3.json"
        threshold_path.write_text(json.dumps(thresholds), encoding="utf-8")
        summary = compare_annotation_bundles(
            bundle_a=a,
            bundle_b=b,
            thresholds_path=threshold_path,
            output_dir=self.output,
        )
        self.assertEqual(summary["metrics"]["exact_set_agreement"], 0.5)
        self.assertEqual(summary["metrics"]["mean_jaccard"], 0.75)
        self.assertEqual(summary["gate_status"], "passed")
        first = (self.output / "dual_run_comparison.csv").read_bytes()
        compare_annotation_bundles(
            bundle_a=a,
            bundle_b=b,
            thresholds_path=threshold_path,
            output_dir=self.output,
        )
        self.assertEqual(
            first, (self.output / "dual_run_comparison.csv").read_bytes()
        )

    def test_comparison_requires_preregistered_v3_thresholds(self) -> None:
        a = self._bundle(
            "annotator_a",
            "A",
            ({"PRINCIPLE-EXPLANATION"}, {"PRINCIPLE-PRACTICE"}),
        )
        b = self._bundle(
            "annotator_b",
            "B",
            ({"PRINCIPLE-EXPLANATION"}, {"PRINCIPLE-PRACTICE"}),
        )
        threshold_path = self.output / "thresholds.json"
        threshold_path.write_text(
            json.dumps({"status": "needs_uet_approval"}), encoding="utf-8"
        )
        with self.assertRaisesRegex(ValueError, "have not been approved"):
            compare_annotation_bundles(
                bundle_a=a,
                bundle_b=b,
                thresholds_path=threshold_path,
                output_dir=self.output,
            )


if __name__ == "__main__":
    unittest.main()
