# Specialist handoff

- Delegation ID: `learning-resource-phase4-5-fragment-retrieval-033`
- Agent: `learning-resource-curator` trong parent thread, chế độ single-agent
- Status: `completed`

## Cập nhật trạng thái ngày 18/07/2026

Handoff này là mốc lịch sử của lượt chạy ban đầu. Trạng thái hiện tại của Pha 4–5 đã được rebuild cho SGK/SGV Tin học 6–9: 154 đơn vị OCR Markdown, 2.750 fragment và SQLite FTS index. Xem handoff cập nhật `learning-resource-phase4-5-current-sync-042.md`.

- Native thread ID/label: không có; không spawn specialist ẩn

## Delegation prompt

Triển khai plan `03-phase4-5-fragment-and-retrieval-from-nguyen-ocr.md`: dùng Markdown OCR của Nguyên làm nguồn chính cho Pha 4, tách fragment, build index truy xuất Pha 5, không đụng artifact OCR/MinerU cũ.

## Follow-up or steer messages

Không có.

## Inputs read

- `README.md`
- `ARCHITECTURE.md`
- `src/edu_benchmark/README.md`
- `agents/learning-resource-curator/SKILL.md`
- `agents/learning-resource-curator/references/learning-resource-schema.md`
- `agents/learning-resource-curator/references/learning-resource-mapping-v0.md`
- `agents/learning-resource-curator/references/resource-fragmentation-guidelines.md`
- `experiments/20260709_155523/plans/03-phase4-5-fragment-and-retrieval-from-nguyen-ocr.md`
- `experiments/20260709_155523/reports/nguyen-ocr-text-readiness-for-phase5.md`
- `experiments/20260709_155523/reports/plan03-codex-artifact-cleanup-map.md`
- `experiments/20260709_155523/outputs/PLAN03_CODEX_ARTIFACTS_CLEANUP_README.md`
- `experiments/20260709_155523/handoffs/learning-resource-codex-artifact-cleanup-marking-032.md`
- `shared/learning_resources/ocr_text/`
- `shared/learning_resources/registries/sgk_sgv_source_registry.csv`

## Outputs created

- `shared/learning_resources/registries/ocr_text_manifest.csv`
- `shared/learning_resources/fragments/learning_resource_fragments.csv`
- `shared/learning_resources/fragments/README.md`
- `shared/learning_resources/indexes/learning_resources_v0.sqlite`
- `shared/learning_resources/indexes/README.md`
- `src/edu_benchmark/learning_resources/ocr_text_manifest.py`
- `src/edu_benchmark/learning_resources/fragment_markdown.py`
- `src/edu_benchmark/learning_resources/retrieval_index.py`
- `src/edu_benchmark/learning_resources/retrieval_api.py`
- `scripts/learning_resources/build_ocr_text_manifest.py`
- `scripts/learning_resources/build_learning_resource_fragments.py`
- `scripts/learning_resources/build_learning_resource_index.py`
- `scripts/learning_resources/query_learning_resource_index.py`
- `tests/learning_resources/test_ocr_text_manifest.py`
- `tests/learning_resources/test_learning_resource_fragments.py`
- `tests/learning_resources/test_learning_resource_retrieval.py`
- `experiments/20260709_155523/reports/phase4-fragmentation-result.md`
- `experiments/20260709_155523/reports/phase5-retrieval-index-result.md`

## Result summary

Đã tạo manifest 35 dòng cho SGK/SGV Tin học 6, tách 606 fragment và build SQLite FTS index v0. Query thử trả đúng các bài trọng yếu: Bài 17 cho Scratch/chương trình máy tính, Bài 1 cho thông tin và dữ liệu, Bài 9 cho an toàn thông tin, và SGV Bài 17 cho hướng dẫn dạy học.

## Orchestrator decision

Dữ liệu Markdown OCR của Nguyên được dùng làm nguồn chính cho Pha 4. Các artifact OCR/MinerU cũ của Codex không bị xóa và không được dùng làm nguồn chính.

## Uncertainty

- `topic_title` còn thiếu ở một số manifest row; cần nối từ mục lục/registry ở vòng sau.
- Ranh giới fragment mới là draft kỹ thuật, chưa có HNMU xác nhận.
- Chưa quyết định chính sách Git cho ảnh `.jpg` trong `shared/learning_resources/ocr_text`.
- Mới xử lý lớp 6; chưa xử lý lớp 7 nếu Nguyên gửi dữ liệu cùng chuẩn.

## Open questions and next human decisions

- Có cần chạy review nhanh 20–30 fragment đại diện trước khi dùng cho Plan 04 không?
- Có muốn ignore ảnh `.jpg` trong `shared/learning_resources/ocr_text` để tránh push nhầm file nặng không?
- Có cần mở rộng pipeline này sang lớp 7 ngay khi có Markdown OCR của Nguyên không?

## Validation

- Python executable: `/home/quannda/miniconda3/envs/benchmark_env/bin/python`
- Test: `/home/quannda/miniconda3/envs/benchmark_env/bin/python -m pytest tests/learning_resources -q`
- Result: `14 passed`
