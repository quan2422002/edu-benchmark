# Hướng dẫn làm quen codebase theo phân công Benchmark v2

Trạng thái: `DRAFT — TÀI LIỆU HỖ TRỢ, KHÔNG THAY THẾ PHÊ DUYỆT PLAN`

Ngày rà soát code và đường dẫn: 16/08/2026

Mục đích của tài liệu này là giúp thành viên mới biết **đọc gì, bắt đầu ở hàm
nào, chạy lệnh nào và kiểm đầu ra nào**. Tài liệu ưu tiên phần của Thủy và
Triệu vì hai nhiệm vụ này nối trực tiếp định nghĩa sư phạm với requirement
scoring và LLM judge.

## 1. Thứ tự ưu tiên khi tài liệu chưa đồng bộ

Khi hai tài liệu mô tả khác nhau, dùng thứ tự sau:

1. [Bản phân công rút gọn v2](team-workplan-concise-v2.md) để xác định vai trò,
   quy mô `PL-REQ`, `PL-JDG`, `BG-JDG` và mốc 18/09.
2. File này để tìm code, dữ liệu, lệnh chạy và thứ tự làm quen.
3. [Kiến trúc repository](../../../ARCHITECTURE.md),
   [README gốc](../../../README.md) và
   [README của package](../../../src/edu_benchmark/README.md) để hiểu ranh giới
   component.
4. [Shared benchmark README](../../../shared/benchmark/README.md), registry và
   manifest của từng artifact để xác định dữ liệu nào đang được dùng.
5. Plan và output của experiment cũ chỉ dùng để hiểu quyết định lịch sử và
   provenance.

Các file `planning/member-task-cards.md`, `planning/team-gantt.md`,
`planning/team-gantt.xlsx`, roadmap và Plan 01 hiện vẫn chứa phương án cũ như
đổi vai trò Hiếu–Hoàng hoặc pilot 30 mẫu. Không dùng chúng để thay bản phân công
rút gọn v2.

Plan 01 hiện là `DRAFT`, gate đang đóng. Vì vậy việc đọc, query, validate và chạy
unit test ngoại tuyến được phép; chưa được xem guide này là quyền sửa `src/`,
ghi output thử nghiệm, gọi API trả phí hoặc công bố sang `shared/benchmark`.

## 2. Môi trường và cách chạy chung

Môi trường chính trên server này là:

```text
/workspace/quannd/miniconda3/envs/benchmark_env/bin/python
```

Một số README cũ còn ghi `/home/quannda/miniconda3/...`; đó là đường dẫn của
server trước. Trên server hiện tại phải dùng đường dẫn `/workspace/quannd/...`
ở trên.

### 2.1. Thiết lập một lần

Chạy từ repository root:

```bash
cd /workspace/quannd/kaggle-backup/edu-benchmark

BENCHMARK_PY=/workspace/quannd/miniconda3/envs/benchmark_env/bin/python

"$BENCHMARK_PY" -m pip install -r requirements.txt
"$BENCHMARK_PY" -m pip install --no-deps -e .
"$BENCHMARK_PY" -c "import edu_benchmark; print(edu_benchmark.__file__)"
```

Không thêm repository hoặc `src/` vào `PYTHONPATH`/`sys.path`. Package đã dùng
src-layout và phải được cài editable. Thành viên không cần cài lại nếu lệnh
import cuối đã trỏ tới repository hiện tại.

### 2.2. Bốn lệnh kiểm tra an toàn

```bash
# Xem CLI requirement scoring, không gọi model.
"$BENCHMARK_PY" scripts/requirement_scoring/run_requirement_scoring.py --help

# Kiểm registry, manifest, checksum, count và phép nối; không promote dữ liệu.
"$BENCHMARK_PY" scripts/benchmark_registry/promote_shared_benchmark.py \
  --validate-only

# Query thử index học liệu hiện có; không build lại index.
"$BENCHMARK_PY" scripts/learning_resources/query_learning_resource_index.py \
  --query "Scratch trung bình cộng ba số" --grade 6 --limit 3

# Chạy nhóm test gần nhất với requirement/rubric/judge.
"$BENCHMARK_PY" -m pytest -q \
  tests/requirement_scoring \
  tests/benchmark_specification/test_benchmark_specification_schema.py \
  tests/benchmark_specification/test_rubrics.py \
  tests/benchmark_evaluation/test_config_integration.py \
  tests/benchmark_evaluation/test_prompt_and_costing.py \
  tests/benchmark_evaluation/test_judge_preparation.py
```

## 3. Bản đồ ngắn từ candidate đến phán quyết judge

```text
shared candidate pool
        │
        ▼
requirement_scoring
6 điểm 1–5 ──► required set (điểm >= 4) + alternative set (điểm = 3)
        │
        ├────────► instruction bundle ──► 3 target response/candidate
        │
        ▼
rubric activation
4 rubric chung + 3 rubric × mỗi required principle
        │
        ▼
blind pairwise judge
criterion judgments + overall judgment ──► analysis/agreement
```

Các package nghiệp vụ nằm dưới `src/edu_benchmark/`; các file trong `scripts/`
chỉ là CLI mỏng. Khi cần hiểu một quy tắc, đọc `src/` trước rồi mới đọc script
gọi nó.

## 4. Khái niệm phải thống nhất trước khi đọc code

| Khái niệm | Cách hiểu trong dự án |
|---|---|
| Dialogue family | Một hội thoại nguồn; có thể sinh nhiều candidate ở các tutor turn khác nhau. |
| Candidate | Một điểm cắt cụ thể để model sinh phản hồi gia sư tiếp theo. ID chính là `benchmark_candidate_id`. |
| Requirement score | Điểm 1–5 cho từng trong sáu nguyên tắc, dựa vào candidate trước khi xem target response. |
| Required set | Tập nguyên tắc có điểm `>=4`, được code suy ra; model không tự ghi tập này. |
| Alternative set | Tập nguyên tắc có điểm `=3`; không kích hoạt rubric riêng. |
| General rubric | Bốn tiêu chí nền áp dụng cho mọi instance judge hợp lệ. |
| Principle rubric | Ba tiêu chí riêng cho mỗi nguyên tắc đang nằm trong required set. |
| Judge instance | Một phép so sánh một target response với gold/reference trên một candidate. Không đồng nghĩa với một criterion. |
| Criterion decision | Một phán quyết Win/Tie/Lose cho một rubric trong một judge instance. |
| Calibration | Dữ liệu được phép dùng để sửa định nghĩa, rubric, threshold hoặc prompt; không báo như accuracy cuối. |
| Held-out validation | Tập giữ lại chỉ mở sau khi mọi phiên bản đã đóng băng; trong kế hoạch này là `BG-JDG`. |

Code hiện tại từ chối required set rỗng tại
`select_applicable_rubric_ids()` và `build_candidate_system_instruction()`.
Do đó candidate nhãn rỗng được giữ trong `PL-REQ`, không đi thẳng vào denominator
sạch của `PL-JDG`.

## 5. Nguồn dữ liệu và đặc tả chung

Mọi thành viên nên biết các điểm bắt đầu sau:

| Thành phần | Đường dẫn | Cần đọc gì |
|---|---|---|
| Registry chung | `shared/benchmark/artifact_registry.csv` | Trạng thái, nguồn, count, authority và limitation của bảy bundle. |
| 2.028 candidate | `shared/benchmark/datasets/candidate_pool/v1/` | `manifest.json`, `candidates.csv`, `trace.csv`, `dispositions.csv`. |
| Pool tạm 1.400 | `shared/benchmark/selections/provisional_evaluation_pool/v1/` | `manifest.json`, `selection.csv`, `requirement_scores.csv`. |
| Sáu năng lực | `shared/benchmark/specifications/tutor_capabilities/v0/` | `tutor_capability_model.md`, CSV và manifest. |
| Sáu nguyên tắc | `shared/benchmark/specifications/pedagogical_principles/v0/` | Định nghĩa, `include_when`, `exclude_when`, evidence và câu hỏi cần giáo viên quyết định. |
| Rubric hai tầng | `shared/benchmark/specifications/rubric_library/v0/` | 4 rubric chung, 18 rubric riêng, provenance, serious errors và review packet. |
| Prompt requirement | `shared/prompts/benchmark_candidate_task_assigning/system_prompt_v4.md` | Prompt đang gắn với full requirement run hiện có. |
| Prompt judge hiện hành | `shared/prompts/benchmark_response_judging/system_prompt_gold_answer_only_v4.md` | Contract judge v4: dùng `gold_answer`, không đưa fragment hoặc serious-error gate vào prompt. |
| Instruction sinh response | `shared/prompts/benchmark_tutor_response_generation/` | Bundle v2 cho baseline/Llama và v3-learnlm cho biến thể prompted. |

Tất cả specification dưới `shared/benchmark` vẫn có trạng thái
`needs_hnmu_review` hoặc provisional tương đương. “Shared” nghĩa là điểm khám
phá chuẩn của repository, không phải ground truth đã được HNMU xác nhận.

## 6. Tra nhanh theo người phụ trách

| Người | Mã | Điểm bắt đầu trong `src/` | Script/kiểm tra gần nhất |
|---|---|---|---|
| Quân | `NV-01` | `governance/experiment.py`, `benchmark_registry/promotion.py`, `experiment_runtime/` | `scripts/governance/validate_experiment.py`, registry `--validate-only` |
| Nguyên | `NV-02` | `learning_resources/retrieval_api.py`, `benchmark_conversion/schema.py` | `query_learning_resource_index.py` |
| Hoàng | `NV-03` | `learning_resources/retrieval_api.py`, `retrieval_index.py`, `quality_checks.py` | query/build index và `tests/learning_resources/test_learning_resource_retrieval.py` |
| Hiếu | `NV-04` | `requirement_scoring/`, `benchmark_evaluation/judge.py`, `section_v_ablation.py` | requirement CLIs, evaluation CLIs và test hai package |
| Thủy | `NV-05` | `benchmark_specification/schema.py`, `requirement_scoring/core.py`, `analysis.py` | test requirement/specification; không tự gọi API |
| Triệu | `NV-06` | `benchmark_specification/rubrics.py`, `benchmark_evaluation/config_builder.py`, `judge.py` | test config/prompt/judge; không tự gọi API |

## 7. Hướng dẫn chi tiết cho Thủy — `NV-05`

### 7.1. Kết quả Thủy cần hiểu và sở hữu

Thủy sở hữu ranh giới của sáu năng lực, sáu nguyên tắc, neo điểm requirement
1–5, ý nghĩa ngưỡng `>=4` và bốn rubric chung. Thủy không sở hữu 18 rubric riêng,
không dùng output LLM làm nhãn chuẩn và không xác nhận nội dung Tin học thay
Nguyên/giáo viên chuyên môn.

### 7.2. Thứ tự đọc đề xuất

1. Mục `NV-05`, 2.8–2.10 và phiếu Thủy trong
   `planning/team-workplan-concise-v2.md`.
2. `shared/benchmark/specifications/tutor_capabilities/v0/tutor_capability_model.md`
   rồi `tutor_capabilities.csv`.
3. `shared/benchmark/specifications/pedagogical_principles/v0/pedagogical_principles.csv`.
4. `experiments/20260727_170150/plans/01-principle-requirement-score-specification.md`
   để hiểu vì sao điểm 4–5 là bắt buộc, điểm 3 là chiến lược thay thế.
5. `experiments/20260727_170150/outputs/principle_requirement_scoring/specification_v4.md`,
   `scoring_schema_v2.json` và `shared/prompts/benchmark_candidate_task_assigning/system_prompt_v4.md`.
6. `experiments/20260727_170150/outputs/principle_requirement_scoring/calibration_gemini35_medium_v1/calibration_summary.md`
   và `review_queue.csv` để xem lỗi đã gặp; đây chỉ là calibration cũ.
7. `experiments/20260727_170150/outputs/principle_requirement_scoring/full_gemini35_medium_v1/full_run_analysis.md`
   và `full_run_review_queue.csv` để hiểu 2.028 candidate được phân tích thế nào.
8. Sau cùng mới đọc code và test ở bảng dưới.

### 7.3. File và hàm cần biết

| File | Hàm/contract cần đọc | Vì sao cần đọc |
|---|---|---|
| `src/edu_benchmark/requirement_scoring/core.py` | `PRINCIPLE_IDS`, `build_grounding_payload()`, `serialize_user_prompt()` | Biết chính xác model thấy trường nào; requirement không được nhìn target response/gold response. |
| Cùng file | `parse_and_validate_response()`, `validate_normalized_response()` | Biết schema bắt buộc đủ sáu principle và điểm nguyên 1–5. |
| Cùng file | `derive_principle_sets()` | Đây là nơi code áp ngưỡng: `>=4` vào required set, `=3` vào alternative set. |
| Cùng file | `lint_principle_scores()` | Xem các cảnh báo semantic hiện có, nhất là score cao thiếu lý do bắt buộc và Feedback chỉ xác nhận. |
| Cùng file | `compare_runs()`, `build_calibration_summary()` | Hiểu metric ổn định giữa hai lượt model lịch sử; không nhầm repeatability với expert accuracy. |
| `src/edu_benchmark/requirement_scoring/analysis.py` | `evidence_reference_is_traceable()`, `analyze_full_run()` | Biết code kiểm evidence và tạo review queue/eligibility, nhưng không xác nhận nhãn sư phạm. |
| `src/edu_benchmark/benchmark_specification/schema.py` | `validate_capabilities()`, `validate_principles()`, `validate_rubrics()` | Biết constraint cấu trúc và trạng thái `needs_hnmu_review`. |
| `src/edu_benchmark/benchmark_evaluation/config_builder.py` | `select_applicable_rubric_ids()` | Thấy bốn rubric chung luôn bật và rubric riêng chỉ bật cho required set không rỗng. |

### 7.4. Ba bài làm quen từ dữ liệu thật

1. Lấy một dòng trong `requirement_scores.csv`, mở đúng candidate trong
   `candidates.csv`, rồi tự giải thích vì sao mỗi principle là 1–5 **trước khi**
   xem score của model.
2. Chọn một ca có score 3–4 hoặc nằm trong `full_run_review_queue.csv`; viết lại
   ranh giới “có thể hữu ích” so với “bắt buộc phải có”.
3. Chọn một ca required set rỗng; xác nhận ca vẫn có ích cho `PL-REQ` nhưng không
   được ép vào `PL-JDG` chỉ để đủ số lượng.

### 7.5. Lệnh Thủy có thể tự chạy

```bash
# Các test minh họa ngưỡng, schema, calibration cases và semantic lint.
"$BENCHMARK_PY" -m pytest -q \
  tests/requirement_scoring/test_requirement_scoring.py \
  -k "response_validation or semantic_lint or calibration_cases"

# Các test minh họa contract năng lực, nguyên tắc và rubric hai tầng.
"$BENCHMARK_PY" -m pytest -q \
  tests/benchmark_specification/test_benchmark_specification_schema.py \
  tests/benchmark_specification/test_rubrics.py \
  -k "capabilit or principle or rubric"

# Chỉ xem interface; không gọi Vertex AI.
"$BENCHMARK_PY" scripts/requirement_scoring/run_requirement_scoring.py \
  calibration --help
```

Không chạy `calibration --execute-api` bằng config lịch sử. Config hiện có trỏ
về output của experiment `20260727_170150`; Hiếu phải tạo config/output mới được
plan phê duyệt trước khi có model call mới.

### 7.6. Dấu hiệu Thủy đã nắm được phần việc

- Giải thích được vì sao requirement score chấm candidate, không chấm response.
- Phân biệt được score 3 với score 4 bằng một ví dụ thật.
- Phân biệt được năng lực, nguyên tắc, rubric chung và rubric riêng.
- Chỉ ra được output nào là model-derived, output nào là giáo viên chấm độc lập.
- Nêu được ít nhất ba lỗi định nghĩa/neo điểm cần đưa vào calibration log.

## 8. Hướng dẫn chi tiết cho Triệu — `NV-06`

### 8.1. Kết quả Triệu cần hiểu và sở hữu

Triệu sở hữu 18 rubric riêng: ba rubric cho mỗi trong sáu nguyên tắc. Triệu phải
kiểm chúng không lặp bốn rubric chung, không lặp nhau và thực sự đo giá trị tăng
thêm của nguyên tắc. Triệu không sửa ngược required set trong bước judge và
không tự xác nhận tính đúng kiến thức Tin học.

### 8.2. Thứ tự đọc đề xuất

1. Mục `NV-06`, 2.8–2.10 và phiếu Triệu trong
   `planning/team-workplan-concise-v2.md`.
2. `experiments/20260727_170150/plans/04-two-tier-rubric-library.md`.
3. `shared/benchmark/specifications/rubric_library/v0/rubric_review_packet.md`,
   rồi `rubrics.csv`, `provenance_matrix.csv`, `serious_errors.csv` và manifest.
4. `experiments/20260727_170150/outputs/benchmark_evaluation/evaluation_protocol.md`
   và `evaluation_schema.json`.
5. `shared/prompts/benchmark_response_judging/system_prompt_gold_answer_only_v4.md`.
6. Ba target manifest dưới
   `experiments/20260727_170150/outputs/benchmark_evaluation/full_1400_v1/` để
   biết response nào dùng instruction bundle v2 và response nào dùng
   `v3-learnlm`.
7. `experiments/20260727_170150/reports/plan05-full-judge-results-analysis-20260730.md`
   để xem lỗi và giới hạn đã quan sát trên 4.200 judgment/judge.
8. Sau cùng mới đọc code và test ở bảng dưới.

### 8.3. File và hàm cần biết

| File | Hàm/contract cần đọc | Vì sao cần đọc |
|---|---|---|
| `src/edu_benchmark/benchmark_specification/rubrics.py` | `flatten_two_tier_rubrics()` | Hiểu cách rubric chung và rubric riêng được xuất phẳng nhưng vẫn giữ tier. |
| `src/edu_benchmark/benchmark_specification/schema.py` | `validate_rubrics()`, `validate_serious_errors()` | Biết foreign key, count và contract của rubric/error. |
| `src/edu_benchmark/benchmark_evaluation/config_builder.py` | `select_applicable_rubric_ids()` | Quy tắc vận hành `4 + 3 × n`; score 3 không kích hoạt rubric riêng; tập rỗng bị từ chối. |
| Cùng file | `evaluation_schema()`, `build_evaluation_config()` | Biết cấu trúc một judge call và các file cấu hình được sinh. |
| `src/edu_benchmark/benchmark_evaluation/instruction_bundle.py` | `load_instruction_bundle()` | Kiểm version/hash và sáu instruction nguyên tắc dùng khi sinh target response. |
| `src/edu_benchmark/benchmark_evaluation/prompt_builder.py` | `build_candidate_system_instruction()` | Biết required set được đưa vào target prompt thế nào và field evaluator nào bị cấm. |
| `src/edu_benchmark/benchmark_evaluation/judge.py` | `build_judge_user_prompt()`, `prepare_judge_requests()` | Biết candidate, gold, response và rubric được ghép thành pairwise prompt thế nào. |
| Cùng file | `validate_judge_output()`, `postprocess_judge_output()` | Hiểu coverage từng criterion, blind order và cách đổi `response_1/2` về Win/Tie/Lose của target. |
| `src/edu_benchmark/benchmark_evaluation/section_v_ablation.py` | `agreement_statistics()`, `judge_robustness()`, `position_sensitivity()` | Hiểu các metric Hiếu sẽ dùng; Triệu diễn giải lỗi rubric, không tự sửa nhãn. |

### 8.4. Ba bài làm quen từ dữ liệu thật

1. Chọn một principle trong `rubrics.csv`; lập bảng ba rubric riêng, ranh giới
   giữa chúng và ranh giới với bốn rubric chung.
2. Lấy một dòng `run_judgments.jsonl`; kiểm `required_principle_ids`,
   `applicable_rubric_ids`, số criterion và `overall_judgment`. Với một principle
   bắt buộc, phải có `4 + 3 = 7` criterion.
3. So sánh `serious_errors.csv` với judgment `gold-answer-only-v4`: code còn giữ
   compatibility fields nhưng v4 không đưa serious-error gate hoặc fragment vào
   judge prompt. Không đánh giá một cơ chế là “đang hoạt động” chỉ vì schema còn
   trường tương thích.

### 8.5. Lệnh Triệu có thể tự chạy

```bash
# Kiểm rubric activation, instruction bundle và judge v4.
"$BENCHMARK_PY" -m pytest -q \
  tests/benchmark_evaluation/test_config_integration.py \
  tests/benchmark_evaluation/test_judge_preparation.py \
  tests/benchmark_evaluation/test_prompt_and_costing.py \
  -k "applicable or gold_answer_only or prepare_three_target or unknown_criterion or instruction_bundle"

# Xem interface dựng evaluation config; không ghi file khi chỉ dùng --help.
"$BENCHMARK_PY" scripts/benchmark_evaluation/build_evaluation_config.py --help

# Xem interface phân tích Section V ngoại tuyến.
"$BENCHMARK_PY" scripts/benchmark_evaluation/analyze_section_v_ablation.py --help
```

Không chạy các wrapper `run_*judge*.sh`, `run_batch_judge.py` hoặc lệnh có
provider credential khi chưa có phê duyệt riêng. `PL-JDG` chỉ được chuẩn bị sau
khi danh sách 30 candidate qua cổng requirement đã khóa.

### 8.6. Dấu hiệu Triệu đã nắm được phần việc

- Giải thích được vì sao rubric riêng chỉ áp dụng cho required set.
- Với `n` nguyên tắc bắt buộc, tính được số criterion là `4 + 3 × n`.
- Phân biệt được criterion judgment, overall judgment và judge instance.
- Truy được một judgment về candidate, target response, instruction bundle và
  rubric version.
- Nêu được ít nhất ba cặp rubric có nguy cơ chồng lấn để đưa vào calibration log.

## 9. Hướng dẫn ngắn cho Hiếu — `NV-04`

Hiếu là người nối nhãn giáo viên với output LLM và chịu trách nhiệm kỹ thuật cho
calibration/validation, không quyết định thay giáo viên.

Đọc theo thứ tự:

1. `src/edu_benchmark/requirement_scoring/config.py`, `core.py`, `workflow.py`,
   `analysis.py`, `export.py`.
2. `scripts/requirement_scoring/run_requirement_scoring.py`,
   `analyze_requirement_scoring.py`, `export_eligible_candidate_pool.py`.
3. `src/edu_benchmark/benchmark_evaluation/config_builder.py`, `judge.py`,
   `batch_judge.py`, `recovery.py`, `section_v_ablation.py`.
4. `tests/requirement_scoring/` và `tests/benchmark_evaluation/`.
5. Config lịch sử
   `experiments/20260806_145124/configs/requirement-scoring-20260727-v1.yaml`
   chỉ làm mẫu về contract; không dùng nó để ghi đè output cũ.

Các entry point chính:

- `load_requirement_scoring_config()` — resolve config/path và chặn secret/path
  escape.
- `prepare()`, `execute_run()`, `finalize()` — lifecycle requirement scoring.
- `analyze_full_run()` — thống kê và review queue.
- `prepare_judge_requests()` — join candidate/requirement/response/rubric và làm
  mù A/B.
- `validate_judge_output()`/`postprocess_judge_output()` — validate rồi quy đổi
  phán quyết.
- `agreement_statistics()`/`position_sensitivity()` — metric ngoại tuyến.

Trước model call mới, Hiếu phải có config mới trỏ vào experiment hiện tại, output
root mới, danh sách ID khóa, manifest input và phê duyệt `--execute-api`.

## 10. Hướng dẫn ngắn cho Hoàng — `NV-03`

Điểm bắt đầu:

- `shared/learning_resources/agent_context/README.md` — hub về fragment, index,
  nguồn HNMU và quy tắc evidence.
- `src/edu_benchmark/learning_resources/retrieval_api.py` —
  `resolve_learning_resource()`, `search_learning_fragments()`,
  `get_learning_fragment()`.
- `src/edu_benchmark/learning_resources/retrieval_index.py` — `build_index()`.
- `src/edu_benchmark/learning_resources/quality_checks.py` — kiểm cấu trúc và
  chất lượng artifact học liệu.
- `tests/learning_resources/test_learning_resource_retrieval.py` — ví dụ nhỏ,
  deterministic, không gọi model.

Lệnh làm quen:

```bash
"$BENCHMARK_PY" scripts/learning_resources/query_learning_resource_index.py \
  --query "Scratch trung bình cộng ba số" --grade 6 --limit 5

"$BENCHMARK_PY" -m pytest -q \
  tests/learning_resources/test_learning_resource_retrieval.py
```

Không sửa 2.750 fragment v0. Mọi thử nghiệm mới phải giữ query, filter, top-k,
fragment đã xem, lý do chọn và trạng thái `unresolved`.

## 11. Hướng dẫn ngắn cho Nguyên — `NV-02`

Nguyên tập trung vào nội dung và provenance; không cần viết pipeline.

Đọc:

- `shared/benchmark/datasets/candidate_pool/v1/candidates.csv` và `trace.csv` để
  nối candidate về dialogue nguồn.
- `shared/learning_resources/fragments/learning_resource_fragments.csv` và
  registry OCR.
- `shared/learning_resources/agent_context/hnmu_cognitive_level_method_canonical.md`
  và `hnmu_scaffolding_method_canonical.md`.
- `src/edu_benchmark/benchmark_conversion/schema.py` để biết field nào là contract.
- `src/edu_benchmark/learning_resources/retrieval_api.py` để biết kết quả query
  được tạo thế nào.

Nguyên có thể dùng CLI query ở mục 2.2 để đọc 1–5 fragment, rồi ghi quyết định
`supports`, `contradicts`, `partial` hoặc `unresolved`. Metadata cùng lớp/bài
không đủ để kết luận fragment hỗ trợ nội dung.

## 12. Hướng dẫn ngắn cho Quân — `NV-01`

Điểm bắt đầu:

- `src/edu_benchmark/governance/experiment.py` — `validate_experiment()`.
- `src/edu_benchmark/benchmark_registry/promotion.py` —
  `validate_shared_benchmark()` và `promote_shared_benchmark()`.
- `src/edu_benchmark/experiment_runtime/config.py`/`cli.py` — preflight, path,
  hash và provenance ngoại tuyến.
- `shared/benchmark/artifact_registry.csv` và manifest của từng bundle.
- `experiments/20260814_062402/plans/01-status.yaml` để kiểm gate hiện tại.

Lệnh kiểm an toàn:

```bash
"$BENCHMARK_PY" scripts/governance/validate_experiment.py \
  experiments/20260814_062402

"$BENCHMARK_PY" scripts/benchmark_registry/promote_shared_benchmark.py \
  --validate-only
```

Không chạy `promote_shared_benchmark.py` thiếu `--validate-only` và không gọi một
bundle là Benchmark v2 trước khi các gate, manifest, limitation và thẩm quyền
phê duyệt đều đầy đủ.

## 13. Ma trận lệnh theo mức quyền

| Loại lệnh | Ví dụ | Ghi file | Gọi mạng/model | Trạng thái hiện tại |
|---|---|---:|---:|---|
| Khám phá | `--help`, `rg`, đọc CSV/JSON/Markdown | Không | Không | Được phép |
| Validate read-only | registry `--validate-only`, query index | Không | Không | Được phép |
| Unit test | `python -m pytest ...` | Chỉ cache test cục bộ | Không trong nhóm test nêu trên | Được phép |
| Prepare/build | requirement `prepare`, build evaluation config/index | Có | Không nhất thiết | Chỉ sau khi plan duyệt và output path được khóa |
| Model execution | `--execute-api`, batch judge, các wrapper `run_*` | Có | Có | Cần phê duyệt plan và phê duyệt chi phí/API riêng |
| Publish/promote | registry không có `--validate-only` | Ghi `shared/benchmark` | Không nhất thiết | Không nằm trong guide này |

## 14. Những chỗ dễ hiểu sai

1. `300` và `150` trong human evaluation của KMP-Bench là số evaluation
   instance/phiếu so sánh, không phải số criterion.
2. `PL-REQ` 60 candidate tạo 360 điểm requirement **cho mỗi người chấm**;
   `PL-JDG` 30 × 3 tạo 90 judge instance/người.
3. `BG-JDG` 60 × 1 không chấm lại requirement; kết luận judge có điều kiện trên
   required set đã khóa.
4. `gold_answer` là neo nội dung; `gold_response` là phản hồi tham chiếu; target
   response là output model cần so sánh. Không đồng nhất ba trường này.
5. `serious_errors.csv` vẫn tồn tại trong rubric library, nhưng contract judge
   đang dùng là `gold-answer-only-v4`, đã bỏ serious-error gate và fragment khỏi
   prompt/output hoạt động.
6. Các file `.orig` và output lịch sử chỉ là provenance/backup; không chọn chúng
   làm source chính khi đã có file không mang hậu tố `.orig`.
7. Hai full judge có đủ 4.200 record không đồng nghĩa chúng là ground truth.
8. Không sửa trực tiếp file dưới `shared/benchmark`, raw HNMU hoặc output lịch sử
   để làm kết quả mới “khớp” hơn.

## 15. Checklist hoàn tất onboarding

Mỗi thành viên xác nhận:

- [ ] Dùng đúng interpreter `/workspace/quannd/.../benchmark_env/bin/python`.
- [ ] Import được `edu_benchmark` mà không thêm `PYTHONPATH`.
- [ ] Đã đọc manifest của dữ liệu mình dùng và biết limitation/authority.
- [ ] Nối được một candidate từ shared pool tới artifact thuộc phần việc của mình.
- [ ] Chạy được ít nhất một CLI read-only và nhóm unit test liên quan.
- [ ] Phân biệt được output model, nhãn người chấm độc lập và nhãn sau phân xử.
- [ ] Biết file/hàm mình sở hữu về nội dung và file/hàm chỉ đọc để hiểu contract.
- [ ] Biết ai có quyền phân xử khi gặp lỗi kỹ thuật, nội dung Tin học hoặc sư phạm.
- [ ] Không chạy API, ghi output hoặc sửa shared khi plan/gate còn đóng.

Nếu một thành viên chưa làm được ba việc “nối một candidate”, “giải thích đúng
contract” và “chạy test liên quan”, chưa giao cho người đó xử lý toàn bộ pilot;
hãy dùng 2–3 ca thật làm bài làm quen và review kết quả trước.
