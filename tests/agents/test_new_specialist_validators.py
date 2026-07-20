"""Validator tests for newly added specialist agents."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


learning_validator = load_module(
    ROOT / "agents/learning-resource-curator/scripts/validate_learning_resource_registry.py",
    "validate_learning_resource_registry",
)
benchmark_validator = load_module(
    ROOT / "agents/benchmark-specification-designer/scripts/validate_benchmark_specification.py",
    "validate_benchmark_specification",
)

hnmu_audit_validator = load_module(
    ROOT / "agents/hnmu-dialogue-auditor/scripts/validate_raw_dialogue_audit_output.py",
    "validate_raw_dialogue_audit_output",
)


class LearningResourceValidatorTests(unittest.TestCase):
    """Check v0 learning-resource mapping validation."""

    def test_valid_source_and_fragment_maps_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            source = directory / "learning_resource_source_map.csv"
            fragments = directory / "learning_resource_fragments.csv"
            source.write_text(
                "learning_material_id,source_title,material_type,grade,source_url,source_key,local_file_path,version_label,status,notes\n"
                "LM-SGK-TIN9-4700233123,SGK Tin học 9,SGK,9,https://example.edu/sgk-tin9,4700233123,,20260701,needs_hnmu_review,Cần HNMU xác nhận\n",
                encoding="utf-8",
            )
            fragments.write_text(
                "fragment_id,learning_material_id,page_start,page_end,section_label,order_index,location_note,status\n"
                "LM-SGK-TIN9-4700233123#F0001,LM-SGK-TIN9-4700233123,17,18,Bài 3 mục 2,1,Đoạn ví dụ,needs_hnmu_review\n",
                encoding="utf-8",
            )
            errors = learning_validator.validate_learning_resource_registry(source, fragments)
            self.assertEqual(errors, [])

    def test_duplicate_source_id_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "learning_resource_source_map.csv"
            source.write_text(
                "learning_material_id,source_title,material_type,grade,source_url,source_key,local_file_path,version_label,status,notes\n"
                "LM-SGK-TIN9-0001,SGK Tin học 9,SGK,9,https://example.edu/a,,,,draft,\n"
                "LM-SGK-TIN9-0001,SGK Tin học 9 bản khác,SGK,9,https://example.edu/b,,,,draft,\n",
                encoding="utf-8",
            )
            errors = learning_validator.validate_learning_resource_registry(source)
            self.assertTrue(any("duplicate learning_material_id" in error for error in errors))

    def test_fragment_unknown_parent_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            source = directory / "learning_resource_source_map.csv"
            fragments = directory / "learning_resource_fragments.csv"
            source.write_text(
                "learning_material_id,source_title,material_type,grade,source_url,source_key,local_file_path,version_label,status,notes\n"
                "LM-SGK-TIN9-0001,SGK Tin học 9,SGK,9,https://example.edu/a,,,,draft,\n",
                encoding="utf-8",
            )
            fragments.write_text(
                "fragment_id,learning_material_id,page_start,page_end,section_label,order_index,location_note,status\n"
                "LM-SGK-TIN9-0002#F0001,LM-SGK-TIN9-0002,1,1,Bài 1,1,,draft\n",
                encoding="utf-8",
            )
            errors = learning_validator.validate_learning_resource_registry(source, fragments)
            self.assertTrue(any("unknown learning_material_id" in error for error in errors))


class BenchmarkSpecificationValidatorTests(unittest.TestCase):
    """Check benchmark specification validation."""

    def write_valid_spec(self, directory: Path) -> None:
        (directory / "benchmark_tasks.csv").write_text(
            "task_id,task_name,definition,scope,input_requirements,output_requirements,status,research_ids,learning_material_ids,teacher_decision_needed\n"
            "T01,Chẩn đoán lỗ hổng,Đánh giá khả năng tìm lỗ hổng,Tin học 9,Câu hỏi và lịch sử,Phản hồi gia sư,needs_hnmu_review,RS-ARXIV-2510-02663-V1,LM-SGK-TIN9-0001,Cần HNMU xác nhận phạm vi\n",
            encoding="utf-8",
        )
        (directory / "rubrics.csv").write_text(
            "rubric_id,task_id,criterion,observable_evidence,score_levels,status\n"
            "R01,T01,Kiểm tra tiền kiến thức,Câu hỏi dẫn dắt rõ,0/1/2,needs_hnmu_review\n",
            encoding="utf-8",
        )
        (directory / "serious_errors.csv").write_text(
            "error_id,description,suggested_action,affected_rubric_ids,status\n"
            "E01,Bịa kiến thức chương trình,Cần HNMU xem xét loại hoặc sửa,R01,needs_hnmu_review\n",
            encoding="utf-8",
        )
        (directory / "provenance_matrix.csv").write_text(
            "item_id,item_type,research_ids,learning_material_ids,rationale,status\n"
            "T01,task,RS-ARXIV-2510-02663-V1,LM-SGK-TIN9-0001,Có căn cứ nghiên cứu và học liệu,needs_hnmu_review\n"
            "R01,rubric,RS-ARXIV-2510-02663-V1,,Rubric xuất phát từ năng lực giàn giáo,needs_hnmu_review\n"
            "E01,serious_error,,LM-SGK-TIN9-0001,Lỗi liên quan căn cứ chương trình,needs_hnmu_review\n",
            encoding="utf-8",
        )

    def test_valid_spec_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            self.write_valid_spec(directory)
            errors = benchmark_validator.validate_benchmark_specification(directory)
            self.assertEqual(errors, [])

    def test_unknown_rubric_task_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            self.write_valid_spec(directory)
            (directory / "rubrics.csv").write_text(
                "rubric_id,task_id,criterion,observable_evidence,score_levels,status\n"
                "R01,T99,Kiểm tra tiền kiến thức,Câu hỏi dẫn dắt rõ,0/1/2,needs_hnmu_review\n",
                encoding="utf-8",
            )
            errors = benchmark_validator.validate_benchmark_specification(directory)
            self.assertTrue(any("unknown task_id" in error for error in errors))

    def test_confirmed_task_without_grounding_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            self.write_valid_spec(directory)
            (directory / "benchmark_tasks.csv").write_text(
                "task_id,task_name,definition,scope,input_requirements,output_requirements,status,research_ids,learning_material_ids,teacher_decision_needed\n"
                "T01,Chẩn đoán lỗ hổng,Đánh giá khả năng tìm lỗ hổng,Tin học 9,Câu hỏi và lịch sử,Phản hồi gia sư,confirmed,,,\n",
                encoding="utf-8",
            )
            errors = benchmark_validator.validate_benchmark_specification(directory)
            self.assertTrue(any("needs research_ids" in error for error in errors))
            self.assertTrue(any("needs learning_material_ids" in error for error in errors))


class HNMUDialogueAuditorValidatorTests(unittest.TestCase):
    """Check raw HNMU dialogue audit output validation."""

    def write_valid_raw_dialogue_checklist_results(self, path: Path, *, omit_last: bool = False) -> list[str]:
        criteria_path = ROOT / "experiments/20260709_155523/reports/raw-dialogue-audit-criteria-v0.csv"
        with criteria_path.open(encoding="utf-8-sig") as handle:
            lines = handle.read().splitlines()
        header, *criterion_lines = lines
        criterion_ids = [line.split(",", 1)[0] for line in criterion_lines if line.strip()]
        if omit_last:
            criterion_ids = criterion_ids[:-1]
        rows = [
            "sample_id,criterion_id,criterion_group,criterion_name,result,confidence_score,evidence_fragment_id,evidence_source,evidence_match_reason,reason,suggested_reviewer_action,checked_by,checked_at"
        ]
        for criterion_id in criterion_ids:
            group = criterion_id.split("-")[1].lower()
            rows.append(
                f"HN-L6-0001,{criterion_id},{group},Tiêu chí kiểm thử,pass,0.86,SGK_TIN6_B17_P71_F001,SGK Tin học 6,Khớp bài và trang,Câu hỏi phù hợp,Không cần hành động,hnmu-dialogue-auditor,2026-07-17T12:00:00+07:00"
            )
        path.write_text("\n".join(rows) + "\n", encoding="utf-8")
        return criterion_ids

    def test_valid_raw_dialogue_checklist_results_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "raw_dialogue_checklist_results.csv"
            self.write_valid_raw_dialogue_checklist_results(path)
            errors = hnmu_audit_validator.validate_raw_dialogue_audit_output(path)
            self.assertEqual(errors, [])

    def test_missing_required_registry_criterion_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "raw_dialogue_checklist_results.csv"
            self.write_valid_raw_dialogue_checklist_results(path, omit_last=True)
            errors = hnmu_audit_validator.validate_raw_dialogue_audit_output(path)
            self.assertTrue(any("missing required criterion_id" in error for error in errors))

    def test_invalid_result_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "raw_dialogue_checklist_results.csv"
            path.write_text(
                "sample_id,criterion_id,criterion_group,criterion_name,result,confidence_score,evidence_fragment_id,evidence_source,evidence_match_reason,reason,suggested_reviewer_action,checked_by,checked_at\n"
                "HN-L6-0001,RAW-CONSISTENCY-01,Nhất quán metadata,Câu hỏi khớp bài học,maybe,0.86,,,,,,hnmu-dialogue-auditor,2026-07-17T12:00:00+07:00\n",
                encoding="utf-8",
            )
            errors = hnmu_audit_validator.validate_raw_dialogue_audit_output(path, criteria_registry_path=None)
            self.assertTrue(any("invalid result" in error for error in errors))

    def test_uncertain_requires_reason_and_reviewer_action(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "raw_dialogue_checklist_results.csv"
            path.write_text(
                "sample_id,criterion_id,criterion_group,criterion_name,result,confidence_score,evidence_fragment_id,evidence_source,evidence_match_reason,reason,suggested_reviewer_action,checked_by,checked_at\n"
                "HN-L6-0001,RAW-SGV-01,Đối chiếu SGV,Đáp án SGV khớp câu hỏi,uncertain,0.55,,,,,,hnmu-dialogue-auditor,2026-07-17T12:00:00+07:00\n",
                encoding="utf-8",
            )
            errors = hnmu_audit_validator.validate_raw_dialogue_audit_output(path, criteria_registry_path=None)
            self.assertTrue(any("reason is required" in error for error in errors))
            self.assertTrue(any("suggested_reviewer_action is required" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
