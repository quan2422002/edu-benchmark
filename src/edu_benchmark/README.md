# Bản đồ mã nguồn `edu_benchmark`

Thư mục này chứa logic Python dùng lại của dự án benchmark gia sư AI môn Tin
học THCS. Các lệnh trong `scripts/` chỉ nên đọc tham số và gọi các hàm ở đây;
không nên chứa lại logic nghiệp vụ.

Tài liệu này trả lời hai câu hỏi:

1. mỗi package/file thuộc phase nào của quy trình xây benchmark;
2. các hàm và lớp trong file đó chịu trách nhiệm gì.

## 1. Ba phase của quy trình khoa học

Tên phase trong tài liệu này theo quy trình xây dựng benchmark đang mô tả trong
bản thảo KSE, không theo số Plan của một experiment:

```text
Hội thoại HNMU + SGK/SGV
        │
        ▼
Phase 1 — Kiểm toán hội thoại thô
1.050 hội thoại ──► 665 hội thoại đạt
        │
        ├───────────────┐
        ▼               ▼
Phase 2             Phase 3
Nền đo lường        Chuyển đổi và lọc dữ liệu
6 nguyên tắc        665 dialogue family
6 năng lực          ──► 2.028 candidate
rubric               ──► 1.400 mẫu tạm chọn
        └───────────────┘
                │
                ▼
Đánh giá benchmark — sinh response, judge và phân tích kết quả
```

| Nhãn trong tài liệu | Phạm vi |
|---|---|
| **Phase 1** | Đọc dữ liệu HNMU, chuẩn hóa, kiểm checklist, kiểm độ phủ/trùng lặp/nhất quán và truy xuất SGK/SGV để hỗ trợ audit. |
| **Phase 2** | Xây và kiểm chứng nền đo lường sư phạm: 6 nguyên tắc, 6 năng lực tutor, rubric, serious errors và provenance. |
| **Phase 3** | Tách từng tutor turn thành candidate, chấm mức độ cần thiết của 6 nguyên tắc, phân tích điều kiện hợp lệ và xuất pool 1.400 mẫu tạm chọn. |
| **Đánh giá benchmark** | Dùng benchmark đã xây để sinh response của model, chấm pairwise, chạy batch/recovery và phân tích Section V. Đây là bước sau Phase 3, không phải Phase 3. |
| **Dùng chung** | Model provider, runtime, registry, quản trị experiment và vệ sinh repository. Các phần này phục vụ nhiều phase nhưng không quyết định nội dung khoa học. |

Một số file cũ dùng cụm như “Plan 03”, “Pha OCR 3–5” hoặc “Phase A MinerU”.
Đó là tên bước triển khai lịch sử bên trong một plan OCR/specification; chúng
không phải ba phase khoa học ở bảng trên.

## 2. Quy tắc đọc bản đồ hàm

- Tất cả hàm/lớp trong một dòng file kế thừa nhãn phase hoặc phần chức năng của
  dòng đó, trừ khi cột vai trò nói rõ ngoại lệ.
- Tên không bắt đầu bằng `_` là API nghiệp vụ hoặc helper có thể được script/test
  gọi trực tiếp. Tên bắt đầu bằng `_` là chi tiết cài đặt nội bộ, không phải API
  ổn định, nhưng vẫn được liệt kê để có thể định vị code.
- Các lớp lỗi như `...Error` chỉ định ranh giới fail-closed của cùng chức năng;
  chúng không tạo thành một phase riêng.
- `__init__.py` chỉ công bố API package. `__main__.py` chỉ là entry point; logic
  thật nằm trong module được nó gọi.

## 3. Bản đồ nhanh theo package

| Package | Phase/phần | Đầu vào chính | Đầu ra hoặc người dùng chính |
|---|---|---|---|
| `data_io` | Phase 1 | XLSX HNMU | Dòng dữ liệu chuẩn hóa ban đầu |
| `learning_resources` | Phase 1, hỗ trợ grounding cho Phase 2–3 | SGK/SGV, OCR Markdown | Manifest, fragment và chỉ mục truy xuất |
| `dialogue_audit` | Phase 1 | Hội thoại thô, checklist, evidence | Quyết định audit và review queue |
| `benchmark_specification` | Phase 2 | Nghiên cứu, học liệu, candidate census | Năng lực, nguyên tắc, rubric và provenance tạm thời |
| `benchmark_conversion` | Phase 3 — chuyển đổi | 665 hội thoại đạt | 2.028 candidate và trace |
| `requirement_scoring` | Phase 3 — chấm/lọc | 2.028 candidate, đặc tả 6 nguyên tắc | Requirement scores, phân tích và pool 1.400 |
| `benchmark_quality` | Phase 3 — placeholder | Chưa có implementation | Dành cho quality checks sau conversion |
| `benchmark_evaluation` | Sau Phase 3 | Pool hợp lệ, prompt/rubric, model response | Cấu hình, response, judgment và phân tích |
| `model_providers` | Dùng chung | Request trung gian độc lập provider | Response/lỗi chuẩn hóa từ Vertex AI/OpenAI |
| `benchmark_registry` | Dùng chung — công bố artifact | Artifact đã kiểm chứng từ các phase | `shared/benchmark/` và manifest chuẩn |
| `experiment_runtime` | Dùng chung — vận hành | YAML config khả chuyển | Preflight, run và manifest |
| `governance` | Dùng chung — quản trị | Plan/status/amendment/coordination | Kết quả kiểm tra hợp đồng experiment |
| `repository_hygiene` | Dùng chung — bảo trì | Cấu hình kiểm kê và cây Git | Inventory/duplicate/retention report, không xóa file |

## 4. Phase 1 — học liệu và kiểm toán hội thoại

### `data_io`

| File | Vai trò và các hàm/lớp |
|---|---|
| `data_io/__init__.py` | Package marker; không có logic nghiệp vụ. |
| `data_io/xlsx.py` | Đọc XLSX bằng thư viện chuẩn. `column_index` đổi ký hiệu cột sang chỉ số; `first_sheet_path` tìm sheet đầu; `read_xlsx_rows` đọc bảng; `slug_header` chuẩn hóa tên cột. `_read_shared_strings` và `_cell_text` giải mã cấu trúc XML nội bộ của XLSX. |

### `learning_resources`

Các file này thuộc Phase 1 vì học liệu được dùng để grounding việc kiểm toán
hội thoại. Fragment và retrieval API tiếp tục được Phase 2–3 tái sử dụng; việc
tái sử dụng đó không biến OCR thành một bước chấm candidate.

| File | Vai trò và các hàm/lớp |
|---|---|
| `learning_resources/__init__.py` | Công bố các module OCR, Markdown, fragment và retrieval; không có logic riêng. |
| `learning_resources/utils.py` | Helper I/O dùng chung: `ensure_directory`, `now_iso`, `read_json`, `write_json`, `iter_image_paths`, `read_path_list`, `safe_stem_from_path`, `relative_to_cwd`, `coerce_float`, `coerce_int`. |
| `learning_resources/ocr_detection.py` | Dò vùng chữ bằng PaddleOCR. `polygon_to_bbox`, `extract_paddle_result`, `build_paddle_ocr`, `detect_page`, `run_detection`; helper nội bộ `_to_plain_result`, `_line_sort_key`. |
| `learning_resources/vietocr_recognition.py` | Nhận dạng crop bằng VietOCR và ghi kết quả tăng dần. API: `has_vietnamese_diacritic`, `build_vietocr_predictor`, `log_progress`, `recognize_detection_page`, `run_recognition`; helper batch: `_collect_detection_files`, `_output_paths_for_detection`, `_summary_row`, `_finalize_page`, `_run_batch_recognition`. |
| `learning_resources/layout_reconstruction.py` | Tái dựng bố cục OCR thành Markdown có kiểm soát. `LayoutRow.text/y_min/y_max` mô tả dòng; `LayoutResult` chứa kết quả; `group_lines_into_rows`, `looks_like_page_number`, `row_to_markdown`, `analyze_lines_to_markdown`, `lines_to_markdown_body` là luồng chính. Các helper `_line_bbox`, `_line_center_y`, `_line_height`, `_line_x`, `_line_center_x`, `_line_width`, `_clean_text`, `_escape_table_cell`, `_row_has_right_page_number`, `_row_left_text`, `_looks_like_middle_watermark`, `_looks_like_standalone_watermark`, `_detect_toc_rows`, `_distinct_column_count`, `_find_table_region`, `_column_boundaries`, `_render_multicolumn_table`, `_render_rows_as_text` xử lý hình học và render. |
| `learning_resources/markdown_export.py` | Xuất từng trang OCR sang Markdown. `infer_book_metadata`, `make_page_id`, `front_matter`, `recognition_to_markdown`, `output_path_for_page`, `export_markdown_pages`; `_yaml_scalar` escape metadata. |
| `learning_resources/mineru_book_phase_a.py` | Chuẩn bị PDF/manifest book-level cho MinerU, không tự gọi MinerU. `BookSpec.material_folder/book_id/image_subdir` định danh sách; `PhaseAPaths` giữ đường dẫn. API: `parse_page_number`, `parse_page_range_spec`, `parse_front_matter_overrides`, `parse_back_matter_overrides`, `collect_book_images`, `make_phase_a_paths`, `build_book_manifest_rows`, `write_book_manifest`, `included_images_from_manifest`, `build_pdf_from_images`, `mineru_command_for_book`, `monitored_mineru_command_for_book`, `write_mineru_commands`, `prepare_books`, `find_mineru_markdown`, `collect_book_markdown`. |
| `learning_resources/mineru_postprocess.py` | Hậu xử lý output MinerU và so với OCR tham chiếu. `PostprocessConfig` giữ cấu hình; `read_csv_rows`, `write_csv_rows`, `clean_mineru_markdown`, `strip_markdown`, `remove_vietnamese_diacritics`, `normalize_for_match`, `ngrams`, `ratio_of_ngrams_found`, `extract_numbers`, `extract_ocr_text`, `build_recognition_index`, `content_text`, `mineru_item_to_markdown`, `mineru_page_items_to_markdown`, `load_content_list_pages`, `find_mineru_content_list`, `page_id_from_manifest_row`, `page_output_path`, `yaml_scalar`, `build_front_matter`, `evaluate_markdown_against_ocr`, `process_book`, `discover_book_ids`, `postprocess_phase_a_outputs`. |
| `learning_resources/ocr_text_manifest.py` | Đăng ký OCR Markdown đã có. `SourceRegistryEntry`, `TopicLessonEntry` là record metadata; `read_csv_rows`, `write_csv_rows`, `load_source_registry`, `topic_item_to_lesson_key`, `build_topic_path`, `load_topic_lesson_map`, `infer_material_type_and_grade`, `lesson_sort_key`, `strip_inline_markup`, `iter_headings`, `extract_first_heading`, `infer_topic_title`, `infer_lesson_key_and_number`, `infer_lesson_title`, `count_markdown_tables`, `read_metadata`, `make_ocr_text_id`, `build_manifest_rows`, `write_manifest`. |
| `learning_resources/fragment_markdown.py` | Tách OCR Markdown thành fragment truy xuất được. `PageChunk` giữ từng trang; `strip_inline_markup`, `split_pages`, `infer_printed_page`, `is_heading`, `is_table_start`, `collect_table`, `cleanup_fragment_text`, `classify_fragment`, `preview_text`, `normalize_section_path`, `should_keep_fragment`, `fragment_manifest_row`, `build_fragments`, `write_fragments`, `write_fragments_readme`. |
| `learning_resources/retrieval_index.py` | Dựng SQLite FTS từ fragment. `build_index` là API chính; `write_index_readme` ghi hướng dẫn; `_connect`, `_create_schema` là helper SQLite. |
| `learning_resources/retrieval_api.py` | Truy xuất evidence học liệu. `connect`, `get_learning_fragment`, `resolve_learning_resource`, `search_learning_fragments`; `_fts_query`, `_as_list`, `_row_to_dict`, `_fallback_like_search` chuẩn hóa query và fallback. |
| `learning_resources/quality_checks.py` | `summarize_recognition_outputs` tổng hợp chất lượng output OCR để review. |

### `dialogue_audit`

| File | Vai trò và các hàm/lớp |
|---|---|
| `dialogue_audit/__init__.py` | Công bố `aggregate_sample`, `build_sample_aggregates`, `audit_batch`, `load_dialogue_rows`, `write_audit_report`. |
| `dialogue_audit/hnmu_audit.py` | Luồng audit xác định Phase 1. `RawDialogueRow.to_dict` biểu diễn một dòng HNMU. Nhóm đọc/chuẩn hóa: `normalize_text`, `extract_grade_label`, `find_header_row`, `row_value`, `load_dialogue_rows`. Nhóm phân tầng nội dung: `bloom_band`, `lesson_code`, `lesson_number`, `lesson_key`, `load_topic_lesson_map`, `row_topic_lesson_metadata`, `_direct_lesson_lookup`, `speaker_labels`. Nhóm kiểm tra: `field_issues`, `_coverage_item`, `coverage_rows`, `duplicate_rows`, `best_learning_evidence`, `consistency_flags`, `quality_rows`. Nhóm xuất: `write_csv`, `audit_batch`, `write_audit_report`. |
| `dialogue_audit/checklist_aggregation.py` | Tổng hợp 18 kết quả cấp tiêu chí thành quyết định cấp sample theo rule nghiêm ngặt. `SampleAggregate` là record tổng hợp. I/O và group: `read_csv_rows`, `write_csv_rows`, `group_checklist_rows`. Quyết định: `parse_confidence`, `aggregate_sample`, `build_sample_aggregates`, `sync_quality_rows`, `build_canonical_quality_rows`, `build_review_queue_rows`. Helper định dạng/chính sách: `unique_nonempty`, `unique_fragment_ids`, `format_confidence`, `bool_text`, `preserve_bool`, `reviewer_action_for_decision`, `review_reason_for_aggregate`, `suggested_question_for_aggregate`. |

## 5. Phase 2 — nền đo lường sư phạm

### `benchmark_specification`

Package này tạo và kiểm chứng specification tạm thời; nó không thay thế phán
quyết của UET/HNMU. Một số module annotation là phương pháp legacy/chẩn đoán,
không phải nhãn nguyên tắc đã được xác nhận.

| File | Vai trò và các hàm/lớp |
|---|---|
| `benchmark_specification/__init__.py` | Công bố API census, task discovery và principle grounding; không có logic riêng. |
| `benchmark_specification/manifest.py` | Khóa đầu vào bằng hash: `sha256_file`, `build_input_manifest`, `write_manifest`. |
| `benchmark_specification/task_discovery.py` | Dựng census và mẫu phân tầng để khám phá năng lực/task. Phân loại: `_ascii_fold`, `cognitive_band`, `history_depth_bin`, `target_position_bin`, `content_form_signal`, `student_state_signal`. Luồng chính: `build_candidate_feature_census`, `_stable_tiebreak`, `select_task_discovery_sample`, `enrich_discovery_sample`, `summarize_discovery_strata`. |
| `benchmark_specification/pipeline.py` | `run_task_discovery_preparation` điều phối việc dựng census, sample và strata cho workstream khám phá task. |
| `benchmark_specification/principle_grounding.py` | Dựng input có nguồn cho principle annotation. `materialize_principle_grounding_pool` là API chính; `_read_csv`, `_write_csv`, `_repo_relative`, `_require_columns` là helper I/O/contract. |
| `benchmark_specification/principle_annotation.py` | Công cụ annotation hai lượt legacy. Chuẩn bị: `_read_csv`, `_write_csv`, `_write_json`, `_relative`, `_require_columns`, `_ordered_ids`, `_ordered_id_sha256`, `_document_records`, `_select_rows`, `build_annotation_inputs`, `validate_input_pair`. Đối chiếu: `_read_phase`, `_validate_phase`, `derive_grounding_effect`, `_set_text`, `reconcile_annotation_draft`, `validate_annotation_bundle`, `validate_thresholds`, `_principle_metrics`, `compare_annotation_bundles`. |
| `benchmark_specification/schema.py` | Schema/validator specification. I/O: `read_csv_rows`, `write_csv_rows`, `split_ids`, `validate_exact_header`, `_validate_unique_status_rows`. Validator nghiệp vụ: `validate_capabilities`, `validate_tasks`, `validate_principles`, `validate_current_task_principle_design`, `validate_rubrics`, `validate_serious_errors`, `validate_principle_annotations`, `validate_evaluation_context`. |
| `benchmark_specification/provenance.py` | `validate_provenance_ids` kiểm ID nghiên cứu/học liệu, không tự bù evidence. |
| `benchmark_specification/rubrics.py` | `flatten_two_tier_rubrics` xuất phẳng rubric hai tầng mà vẫn giữ provenance tầng nguồn. |
| `benchmark_specification/teacher_packet.py` | `validate_workstream_b_teacher_packet` kiểm bộ tài liệu review năng lực; `validate_legacy_eight_task_codebook_gate` kiểm gate codebook 8 task lịch sử. |
| `benchmark_specification/publication.py` | Kiểm và công bố draft tạm thời. Helper `_ids`, `_known_research_ids`, `_known_learning_material_ids`; validator `validate_specialist_draft`, `validate_capability_draft`; publisher nguyên tử `publish_capability_draft`, `publish_specialist_draft`. |

## 6. Phase 3 — chuyển đổi, requirement scoring và chọn pool

### `benchmark_conversion`

| File | Vai trò và các hàm/lớp |
|---|---|
| `benchmark_conversion/__init__.py` | Công bố bốn entry point conversion: `run_conversion_input_build`, `run_conversion_pilot`, `run_multi_candidate_migration_pilot`, `run_full_multi_candidate_conversion`. |
| `benchmark_conversion/dialogue_split.py` | Parser/splitter fail-closed. `DialogueSplitError` mang mã lỗi; `DialogueTurn` biểu diễn turn; `parse_dialogue_turns` parse nhãn `HS`/`AI`; `split_final_tutor_response_candidate` tạo candidate cuối; `split_each_tutor_turn_candidates` tạo một candidate cho mỗi tutor turn. |
| `benchmark_conversion/corrections.py` | Áp correction đã được người duyệt cho phép và khóa hash. `load_dialogue_corrections`, `apply_dialogue_corrections`; `_parse_turns_without_sequence_validation`, `_render_turns` hỗ trợ sửa turn có truy vết. |
| `benchmark_conversion/input_selection.py` | Chọn đúng 665 input Phase 1 đạt và pilot deterministic. `SnapshotContractError`, `AuditSnapshot` mô tả contract. API: `load_audit_snapshot`, `aggregate_all_raw_audit_evidence`, `normalize_blocking_evidence`, `build_pass_conversion_input`, `cognitive_band`, `turn_count_bin`, `select_conversion_pilot`. Helper `_read_csv`, `_unique_index`. |
| `benchmark_conversion/last_turn_analysis.py` | Phân tích hội thoại kết thúc ở student turn. `classify_final_student_turn`, `analyze_last_student_turns`; helper `_parse_labelled_turns`, `_normalize_for_exact_match`, `_word_count_bin`. |
| `benchmark_conversion/schema.py` | Contract từng dòng: `parse_json_string_list`, `dump_json_string_list`, `validate_conversion_input_row`, `validate_candidate_split_row`, `validate_conversion_trace_row`, `validate_conversion_disposition_row`. |
| `benchmark_conversion/pipeline.py` | Điều phối conversion theo file. I/O/chụp nguồn: `read_csv_rows`, `write_csv_rows`, `default_snapshot_specs`. Luồng v1/pilot: `run_conversion_input_build`, `run_conversion_pilot`. Luồng multi-candidate: `_split_error`, `_validate_multi_candidate_inputs`, `select_multi_candidate_migration_pilot`, `_build_multi_candidate_outputs`, `_multi_candidate_statistics`, `_validate_plan02_baseline`, `_validate_serialized_candidate_mapping`, `run_multi_candidate_migration_pilot`, `run_full_multi_candidate_conversion`. Công bố nguyên tử/provenance: `_sha256_file`, `_create_staging_directory`, `_atomic_publish_directory`, `_publish_failure_bundle`, `_write_multi_candidate_outputs`. |

### `requirement_scoring`

Đây là phần Phase 3 gắn nền đo lường Phase 2 vào 2.028 candidate. Model chỉ đề
xuất score theo contract; code kiểm schema, lọc và đưa trường hợp không chắc
chắn vào review queue.

| File | Vai trò và các hàm/lớp |
|---|---|
| `requirement_scoring/__init__.py` | Công bố API domain requirement scoring; không chứa workflow riêng. |
| `requirement_scoring/config.py` | Đọc YAML config khả chuyển. `RequirementScoringConfigError` là lỗi contract; `RequirementScoringConfig.experiment_id/run_defaults/analysis_defaults/export_defaults` cung cấp view theo command; `load_requirement_scoring_config` là API. Helper `_mapping`, `_exact_keys`, `_string`, `_positive_int`, `_non_negative_int`, `_number`, `_boolean`, `_scan_for_secrets`, `_repository_root`, `_resolve_path` kiểm kiểu, secret và path. |
| `requirement_scoring/core.py` | Logic domain chính. Policy/contract: `RequirementScoringError`, `ModelGenerationPolicy.as_dict`, `RunExecutionPolicy.as_dict`, `GenerationConfig.__post_init__/as_dict/model_policy/execution_policy/request_dict`. Hash/thời gian/I/O: `utc_now`, `sha256_bytes`, `sha256_file`, `canonical_json_bytes`, `canonical_json_hash`, `atomic_write_text`, `atomic_write_json`. Đọc/chọn input: `_stable_key`, `_parse_history`, `normalize_grounding_row`, `load_grounding_pool`, `_select_diverse`, `select_pilot`, `_serialize_pilot_row`, `write_pilot_input`, `load_pilot_input`, `load_calibration_cases`. Request/response: `build_grounding_payload`, `serialize_user_prompt`, `build_request_hash`, `parse_and_validate_response`, `_normalize_response`, `validate_normalized_response`, `score_map`, `derive_principle_sets`, `lint_principle_scores`. Run/calibration: `load_run_records`, `validate_run_records`, `_weighted_kappa`, `_binary_f1`, `compare_runs`, `write_review_queue`, `build_pilot_summary`, `build_calibration_summary`, `validate_specification_manifest`, `validate_snapshot_manifest`. |
| `requirement_scoring/provider.py` | Adapter domain trên `model_providers`. `RequirementResponseClient.generate/close` là protocol; `RequirementScoringModelClient.__init__/generate/close` đổi prompt domain thành `ModelRequest`; `build_vertex_requirement_client` tạo client tương thích cũ. |
| `requirement_scoring/workflow.py` | Chu trình prepare/run/finalize, resume, retry và ghi JSONL tăng dần. `_ProgressBar.__init__/_line/update/finish` hiển thị tiến độ. Chuẩn bị: `_load_schema`, `_config_from_args`, `_is_calibration`, `_is_full`, `_pilot_directory`, `_load_scoring_rows`, `_repository_root`, `_manifest_path`, `_planned_manifest`, `prepare`. Thực thi: `_append_jsonl`, `_completed_records`, `_generate_record`, `_safe_failure`, `_is_retryable_failure`, `execute_run`. Hoàn tất: `finalize`, `finalize_full`, `run_full_pilot`, `run_full_dataset`, `retry_failed_full`. |
| `requirement_scoring/analysis.py` | Phân tích full run và quyết định eligibility bằng code. I/O/helper: `_rate`, `_mean`, `_stable_key`, `_set_key`, `_json_cell`, `_display_path`, `_atomic_write_csv`, `load_conversion_trace`, `_score_map`, `_normalize_reference_text`. Evidence/thống kê: `evidence_reference_is_traceable`, `_family_positions`, `_score_distribution`, `_principle_statistics`, `_exact_set_distribution`, `_cooccurrence`, `_strata`. Eligibility/report: `_reason_priority`, `_flagged_details`, `_eligible_distribution`, `_family_eligibility`, `_markdown_table`, `build_analysis_markdown`, `_write_paper_registry`, `analyze_full_run`. |
| `requirement_scoring/export.py` | Join kết quả với candidate/trace và xuất pool đủ điều kiện. `export_eligible_candidate_pool` là API; `_json_cell`, `_load_csv_index`, `_atomic_write_csv`, `_family_positions`, `_validate_candidate_match` là helper kiểm join và ghi nguyên tử. |

### `benchmark_quality`

| File | Vai trò và các hàm/lớp |
|---|---|
| `benchmark_quality/__init__.py` | Placeholder cho quality checks cấp benchmark sau conversion. Hiện không có hàm/lớp; không được coi là một bước pipeline đã cài đặt. |

## 7. Sau Phase 3 — đánh giá benchmark

### `benchmark_evaluation`

Package này không xây candidate mới. Nó tiêu thụ pool đã chọn để sinh response,
chấm pairwise và phân tích kết quả model.

| File | Vai trò và các hàm/lớp |
|---|---|
| `benchmark_evaluation/__init__.py` | Công bố transport hội thoại, instruction bundle và prompt builder. |
| `benchmark_evaluation/dialogue_transport.py` | Bảo toàn ranh giới multi-turn. `DialogueTransportError`, `ChatMessage.as_dict`, `NormalizedConversation.as_list`; `_canonical_hash`, `_parse_history`, `build_native_conversation`. |
| `benchmark_evaluation/instruction_bundle.py` | Đọc bundle instruction có version. `InstructionBundleError`, `PrincipleInstruction`, `InstructionBundle.principles_by_id/render_principle`; `_mapping`, `_nonempty_text`, `_template_fields`, `load_instruction_bundle`. |
| `benchmark_evaluation/prompt_builder.py` | `PromptBuildError`; `build_candidate_system_instruction` ghép instruction theo tập nguyên tắc và chặn field cấm. |
| `benchmark_evaluation/provider_adapters.py` | Chuyển conversation chuẩn hóa sang request native. `ProviderAdapterError`, `_validate`, `to_gemini_request`, `to_anthropic_request`, `to_openai_compatible_request`. Đây là adapter format cũ; transport provider chung nằm ở `model_providers`. |
| `benchmark_evaluation/config_builder.py` | Dựng bundle cấu hình đánh giá. `EvaluationConfigError`; `read_csv`, `_csv_text`, `_atomic_write`, `model_rows`, `instruction_rows`, `select_applicable_rubric_ids`, `evaluation_schema`, `protocol_text`, `build_evaluation_config`. |
| `benchmark_evaluation/validation.py` | `EvaluationValidationError`; `_read_csv`, `validate_evaluation_config` kiểm fail-closed bundle cấu hình. |
| `benchmark_evaluation/costing.py` | Chặn vượt ngân sách. `BudgetExceededError`; `TokenPricing.estimate`; `BudgetPolicy.assert_next_batch_allowed`; `estimate_self_deployed_cost`. |
| `benchmark_evaluation/smoke.py` | Chuẩn bị smoke request. `SmokePreparationError`, `PreparedTutorRequest.trace_fields`; `_read_csv`, `_hash_request`, `load_required_principle_sets`, `prepare_tutor_requests`, `prepare_smoke_requests`. |
| `benchmark_evaluation/pilot.py` | Chọn pilot 80 mẫu có coverage. `PilotSelectionError`; `_read_csv`, `_sha256`, `_portable`, `bloom_group`, `_coverage`, `_deficit`, `_plain_coverage`, `build_pilot_manifest`. |
| `benchmark_evaluation/cost_pilot.py` | Chọn cost-pilot judge 30 mẫu. `CostPilotSelectionError`; `_read_csv`, `_sha256`, `_portable`, `_coverage`, `_deficit`, `_plain`, `build_judge_cost_pilot_manifest`. |
| `benchmark_evaluation/full.py` | Khóa đúng pool 1.400 mẫu cho evaluation. `FullManifestError`; `_read_csv`, `_sha256`, `_portable`, `_normalized_history`, `build_full_manifest`. Việc khóa evaluation input không thay đổi disposition Phase 3. |
| `benchmark_evaluation/vertex_endpoint.py` | Gọi custom Vertex endpoint/vLLM. `VertexEndpointError.__init__`, `VertexRawPredictCaller.__init__/_token/call/close`; `endpoint_id_from_resource`, `load_lifecycle_manifest`, `parse_openai_chat_response`. |
| `benchmark_evaluation/judge.py` | Chuẩn bị và hậu xử lý blind pairwise judgment. Contract: `JudgePreparationError`, `JudgeOutputError`, `PreparedJudgeRequest.trace_fields`. Join/prompt: `_read_csv`, `_read_jsonl`, `_index`, `_json_array`, `_version`, `_target_first`, `_evidence`, `_replace_internal_ids`, `_rubric`, `_affected_rubric_ids`, `_error`, `_markdown_value`, `_conversation_history`, `_learning_evidence_markdown`, `_rubrics_markdown`, `_errors_markdown`, `build_judge_user_prompt`, `prepare_judge_requests`. Output: `_json_object`, `_confidence`, `_text`, `validate_judge_output`, `_target_judgment`, `postprocess_judge_output`. |
| `benchmark_evaluation/gemini_judge.py` | Judge Gemini trên provider chung. `GeminiJudgeCallError.__init__`, `GeminiVertexJudgeCaller.__init__/call/close`, `_build_gemini_response_schema`. |
| `benchmark_evaluation/openai_judge.py` | Judge OpenAI trên provider chung. `OpenAIJudgeCallError.__init__`, `OpenAIJudgeCaller.__init__/call/close`, `_object`, `build_judge_response_schema`. |
| `benchmark_evaluation/claude_judge.py` | Judge Claude qua Vertex AI legacy. `ClaudeJudgeCallError.__init__`, `ClaudeVertexJudgeCaller.__init__/_token/_url/call/close`. |
| `benchmark_evaluation/batch_judge.py` | Helper batch judge không phụ thuộc orchestration API. `BatchJudgeError`, `ParsedProviderResult`; I/O/hash: `utc_now`, `file_hash`, `atomic_json`, `atomic_jsonl`, `append_jsonl`, `read_jsonl`, `schema_name`. Request/parse: `build_openai_batch_line`, `build_gemini_batch_line`, `_openai_output_text`, `parse_openai_batch_output`, `parse_gemini_batch_output`, `build_judgment_record`, `validate_judgment_records`. Chi phí: `request_cost_usd`, `empirical_cost_projection`, `actual_cost_usd`. |
| `benchmark_evaluation/recovery.py` | Recovery fail-closed cho response thiếu/cụt. `TargetRecoveryError`; `sha256`, `read_jsonl`, `index_rows`, `candidate_ids_sha256`, `is_completed_response`, `build_recovery_manifest`, `build_followup_recovery_manifest`, `finalize_followup_recovery_bundle`, `_same_request`, `merge_recovery_bundle`. |
| `benchmark_evaluation/section_v_ablation.py` | Phân tích Section V, không gọi model. `SectionVAblationError`, `LoadedJudge`; I/O/load: `sha256_file`, `_read_jsonl`, `load_candidate_families`, `_validate_label`, `load_judge`. Thống kê: `_ratio`, `_judgment_counts`, `score_records`, `_component_value`, `_component_n`, `_family_sufficient_statistics`, `_bootstrap_component_matrix`, `instruction_ablation`, `_component_or_rubric_value`, `_component_or_rubric_n`, `agreement_statistics`, `_criterion_map`, `judge_robustness`, `position_sensitivity`. Công bố: `_assert_close`, `validate_results`, `build_results`, `write_results_atomic`. |

## 8. Hạ tầng dùng chung, không thuộc riêng phase nào

### `model_providers`

| File | Vai trò và các hàm/lớp |
|---|---|
| `model_providers/__init__.py` | Công bố contract và factory provider chung. |
| `model_providers/contracts.py` | Kiểu trung gian độc lập nền tảng: `ModelMessage.__post_init__/as_dict`, `GenerationSettings.__post_init__`, `StructuredOutput.__post_init__`, `ModelRequest.__post_init__`, `TokenUsage`, `ModelResponse.__post_init__`, `ProviderCallError.__init__`, protocol `ModelProvider.generate/close`. |
| `model_providers/registry.py` | Registry lazy. `ProviderRegistry.__init__/normalize_backend/register/create`; `_builtin_factory`, `create_provider`. |
| `model_providers/openai/__init__.py` | Công bố `OpenAIConfigurationError`, `OpenAIProvider`. |
| `model_providers/openai/provider.py` | OpenAI Responses API. `OpenAIConfigurationError`; `OpenAIProvider.__init__/_input/generate/close`; `_is_retryable_status`, `_response_body`. |
| `model_providers/vertex_ai/__init__.py` | Công bố `VertexAIConfigurationError`, `VertexAIProvider`, `normalize_finish_reason`. |
| `model_providers/vertex_ai/provider.py` | Google Gen AI SDK trên Vertex AI. `VertexAIConfigurationError`; `normalize_finish_reason`, `_is_retryable`; `VertexAIProvider.__init__/_new_client/_client/_contents/_config/generate/close`. |

### `benchmark_registry`

Registry công bố artifact từ cả ba phase nhưng không tự thay đổi nhãn hoặc nội
dung benchmark.

| File | Vai trò và các hàm/lớp |
|---|---|
| `benchmark_registry/__init__.py` | Công bố `promote_shared_benchmark`, `validate_shared_benchmark`. |
| `benchmark_registry/promotion.py` | Promotion deterministic sang `shared/benchmark`. `PromotionError`, `sha256_file`, `validate_shared_benchmark`, `promote_shared_benchmark` là API chính. Helper đường dẫn/I/O: `_repo_path`, `_read_csv`, `_write_csv`, `_write_json`, `_copy`, `_unique`. Provenance/manifest: `_source_record`, `_output_record`, `_manifest`, `_validate_sources`, `_write_bundle_manifest`, `_validate_manifest`. Dựng bundle: `_build_selection_rows`, `_build_requirement_score_rows`, `_readme`, `_build_shared_tree`. |

### `experiment_runtime`

| File | Vai trò và các hàm/lớp |
|---|---|
| `experiment_runtime/__init__.py` | Công bố config/preflight API. |
| `experiment_runtime/__main__.py` | Cho phép chạy `python -m edu_benchmark.experiment_runtime`; chỉ gọi `cli.main`. |
| `experiment_runtime/config.py` | Config khả chuyển và fail-closed. `RuntimeConfigError`, `ResolvedInput.manifest_record`, `RuntimeConfig.pipeline_id/config_id/config_version/input/output_path`. Hash/path/contract: `sha256_file`, `canonical_json_hash`, `_utc_now`, `discover_repository_root`, `_mapping`, `_string`, `_scan_for_serialized_secrets`, `_resolve_repo_path`, `_record_count`, `validate_runtime_contract`, `_resolve_config_path`, `load_runtime_config`. Manifest/result: `build_preflight_manifest`, `_portable_repository_path`, `normalize_result_provenance_paths`, `semantic_result_hash`, `write_json_atomic`. |
| `experiment_runtime/cli.py` | CLI runtime. `_load_json`, `_completed_manifest`, `run_configured_section_v`, `preflight`, `_validate_manifest_contract`, `validate`, `build_parser`, `main`. `preflight` chỉ trả đạt sau khi các validator hoàn tất; lỗi phát sinh được đưa thành trạng thái lỗi bởi CLI. |

### `governance`

| File | Vai trò và các hàm/lớp |
|---|---|
| `governance/__init__.py` | Công bố `ValidationIssue`, `validate_experiment`, `validate_templates`. |
| `governance/experiment.py` | Kiểm hợp đồng quản trị experiment. `ValidationIssue.format`; helper `_issue`, `_load_yaml`, `_parse_timestamp`, `_resolve_inside`, `_validate_markdown_links`, `_validate_metadata`, `_approved_marker`, `_registered_conventional_artifacts`, `_validate_plan_status`, `_validate_coordination`; API `validate_templates`, `validate_experiment`. |

### `repository_hygiene`

| File | Vai trò và các hàm/lớp |
|---|---|
| `repository_hygiene/__init__.py` | Công bố config, kết quả inventory và scanner. |
| `repository_hygiene/inventory.py` | Kiểm kê không phá hủy. Contract: `HygieneConfigError`, `HygieneTarget.matches`, `HygieneConfig`, `InventoryResult.as_dict`. Config/path: `_mapping`, `_exact_keys`, `_string`, `_string_list`, `_boolean`, `_relative_path`, `load_hygiene_config`. Git/file scan: `_run_git`, `_nul_paths`, `_excluded`, `_iter_files`, `_sha256`, `_write_csv`, `_target_for`, `_reference_files`, `_file_size`, `_head_blob_summary`, `scan_repository`. Không hàm nào trong module này xóa file. |

### Package gốc

| File | Vai trò và các hàm/lớp |
|---|---|
| `edu_benchmark/__init__.py` | Định danh package; không có logic nghiệp vụ. |

## 9. Cách lần theo một mẫu qua code

| Câu hỏi | Điểm bắt đầu nên đọc |
|---|---|
| Vì sao một hội thoại thô đạt/không đạt Phase 1? | `dialogue_audit/hnmu_audit.py` → `dialogue_audit/checklist_aggregation.py` |
| Evidence SGK/SGV được tạo và truy xuất thế nào? | `learning_resources/ocr_text_manifest.py` → `fragment_markdown.py` → `retrieval_index.py` → `retrieval_api.py` |
| Từ một hội thoại tạo ra các candidate nào? | `benchmark_conversion/dialogue_split.py` → `benchmark_conversion/pipeline.py` |
| 6 nguyên tắc, 6 năng lực và rubric được kiểm ở đâu? | `benchmark_specification/schema.py`, `publication.py`, `rubrics.py` |
| Candidate nào vào pool 1.400 và vì sao? | `requirement_scoring/core.py` → `workflow.py` → `analysis.py` → `export.py` |
| Model target nhận chính xác conversation/prompt nào? | `benchmark_evaluation/dialogue_transport.py` → `instruction_bundle.py` → `prompt_builder.py` |
| Provider thực sự gọi Vertex AI/OpenAI ở đâu? | `model_providers/vertex_ai/provider.py`, `model_providers/openai/provider.py` |
| Pairwise judge và batch/recovery hoạt động ở đâu? | `benchmark_evaluation/judge.py` → các `*_judge.py` → `batch_judge.py`/`recovery.py` |
| Section V được tái lập mà không gọi model ở đâu? | `benchmark_evaluation/section_v_ablation.py`, qua `experiment_runtime/cli.py` |

## 10. Môi trường chạy

Mọi lệnh package, validator và test thông thường dùng:

```text
/home/quannda/miniconda3/envs/benchmark_env/bin/python
```

Repository phải được cài editable bằng `python -m pip install --no-deps -e .`;
không thêm repository hoặc `src/` vào `PYTHONPATH`/`sys.path`.

Chỉ bước VietOCR GPU được phép dùng
`/home/quannda/miniconda3/envs/ocr_vietocr_gpu/bin/python`. Lệnh MinerU thật
dùng môi trường `ocr_mineru`; các bước chuẩn bị/hậu xử lý MinerU vẫn dùng
`benchmark_env`.
