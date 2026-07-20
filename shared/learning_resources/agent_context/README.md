# Hub ngữ cảnh cho agent kiểm tra dữ liệu HNMU

Thư mục này không chứa bản sao của dữ liệu nguồn. Nó là “bàn điều khiển” giúp specialist agent biết cần dùng tài nguyên nào để kiểm tra độ chính xác và tính nhất quán của dữ liệu hội thoại thô HNMU.

## Nguyên tắc

1. Không sửa dữ liệu gốc trong `shared/raw_data/HNMU-teacher_dialog_samples/`.
2. Không coi OCR/fragment ở trạng thái `draft` là xác nhận chuyên môn cuối cùng của HNMU, nhưng nếu fragment khớp metadata + nội dung thì vẫn dùng như evidence sơ bộ và không tự động đưa mẫu vào review.
3. Khi kết luận một mẫu đúng/sai/chưa chắc, phải trỏ được về evidence học liệu bằng `fragment_id` hoặc đường dẫn học liệu tương ứng.
4. Nếu evidence học liệu còn mơ hồ, gắn cờ cần UET/HNMU kiểm lại thay vì tự chốt.
5. Agent không đọc toàn bộ thư mục Markdown. Agent dùng công cụ truy xuất để tìm đúng vùng cần đọc.



Tính đến 20/07/2026, manifest/fragment/index học liệu đã bao phủ OCR Markdown SGK/SGV Tin học 6–9 do Nguyên gửi. Raw dialogue lớp 6–7 và lớp 8–9 đều đã có lượt audit Plan 04 riêng. Các output agent-level mới nhất phải được đọc trong thư mục `agent_shard_audit/merged/` của từng batch, không lấy các file debug/lần chạy trung gian làm kết quả chính.

## Tài nguyên chính


| Nhóm                                                  | Đường dẫn                                                                                         | Vai trò                                                                                                                                                                           |
| ------------------------------------------------------ | ----------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Dữ liệu hội thoại thô                             | `shared/raw_data/HNMU-teacher_dialog_samples/`                                                        | Input gốc do HNMU gửi; chỉ đọc, không sửa trực tiếp.                                                                                                                      |
| Manifest OCR Markdown                                  | `shared/learning_resources/registries/ocr_text_manifest.csv`                                          | Danh sách SGK/SGV đã có OCR Markdown theo lớp, bài, trạng thái.                                                                                                            |
| Fragment học liệu                                    | `shared/learning_resources/fragments/learning_resource_fragments.csv`                                 | Bảng đoạn học liệu để agent đối chiếu câu hỏi, đáp án, bài học, vị trí.                                                                                         |
| SQLite truy xuất                                      | `shared/learning_resources/indexes/learning_resources_v0.sqlite`                                      | Chỉ mục FTS sinh lại được; dùng cho truy vấn nhanh theo từ khóa và bộ lọc.                                                                                            |
| Checklist kiểm dữ liệu thô HNMU                    | `experiments/20260709_155523/reports/raw-dialogue-quality-checklist-v0.md`                            | Checklist vận hành cho Plan 04; chỉ kiểm dữ liệu thô HNMU trước khi chuyển đổi thành mẫu benchmark.                                                                  |
| Registry tiêu chí từng mẫu                         | `experiments/20260709_155523/reports/raw-dialogue-audit-criteria-v0.csv`                              | Danh sách 18 tiêu chí bắt buộc mà agent phải chấm cho từng mẫu; mỗi mẫu đúng một dòng cho mỗi tiêu chí.                                                               |
| Checklist kiểm ứng viên benchmark                   | `experiments/20260709_155523/reports/benchmark-candidate-quality-checklist-v0.md`                     | Chỉ dùng sau Plan 06, khi đã có mẫu ứng viên benchmark với`student_prompt`, `conversation_history`, `gold_response`, task/rubric và truy vết. Không dùng cho Plan 04. |
| Checklist tổng hợp nền                              | `experiments/20260709_155523/reports/benchmark-quality-checklist-v0.md`                               | Bản tổng hợp logic từ 4 bài báo; không dùng trực tiếp làm checklist vận hành cho specialist agent.                                                                    |
| Phương pháp dàn giáo — nguồn gốc               | `document/teacher_training_curriculum/benchmark_building_documents/KhungDanGiao_HoiThoaiMinhHoa.docx` | Tài liệu gốc do HNMU biên soạn. Dùng để đối chiếu khi cần chắc chắn tuyệt đối.                                                                                    |
| Phương pháp dàn giáo — bản Markdown chuẩn hóa | `shared/learning_resources/agent_context/hnmu_scaffolding_method_canonical.md`                        | Nguồn chính dạng Markdown cho agent khi kiểm dấu hiệu dàn giáo trong hội thoại.                                                                                          |
| Đối chiếu nguồn dàn giáo                         | `experiments/20260709_155523/reports/scaffolding-source-comparison-20260717.md`                       | Báo cáo giải thích vì sao bản Markdown cũ không nên làm nguồn chính.                                                                                                   |
| Plan kiểm toán dữ liệu HNMU                        | `experiments/20260709_155523/plans/04-hnmu-dialogue-intake-coverage-consistency-dedup.md`             | Phạm vi và output cần tạo khi triển khai kiểm toán batch HNMU.                                                                                                              |
| Hướng dẫn xử lý OCR Markdown mới                 | `shared/learning_resources/OCR_TEXT_PROCESSING_RUNBOOK.md`                                            | Cách cập nhật manifest, topic-map enrichment, fragment và index khi có thêm hoặc sửa SGK/SGV OCR Markdown.                                                                                                     |

## Công cụ truy xuất học liệu

Các hàm chính nằm trong `src/edu_benchmark/learning_resources/retrieval_api.py`:

- `resolve_learning_resource(metadata)`: tìm fragment ứng viên từ metadata như lớp, loại sách, bài học, chủ đề.
- `search_learning_fragments(query, filters)`: tìm fragment bằng từ khóa và bộ lọc như lớp, SGK/SGV, bài, loại fragment.
- `get_learning_fragment(fragment_id)`: lấy đầy đủ nội dung và truy vết của một fragment cụ thể.

Ví dụ query nhanh:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/learning_resources/query_learning_resource_index.py \
  --query "Scratch trung bình cộng ba số" --grade 6
```

Nếu agent gọi trực tiếp API bằng Python thay vì script dòng lệnh, cần chạy từ repo root với `PYTHONPATH=src`, ví dụ:

```bash
PYTHONPATH=src /home/quannda/miniconda3/envs/benchmark_env/bin/python -c "from edu_benchmark.learning_resources.retrieval_api import search_learning_fragments; print(search_learning_fragments('Scratch trung bình cộng ba số', filters={'grade': '6'}, limit=1))"
```

## Công cụ tổng hợp kết quả audit

Sau khi agent đã ghi đủ checklist chi tiết, không tự tổng hợp mềm bằng cảm tính. Dùng rule strict trong:

```text
src/edu_benchmark/dialogue_audit/checklist_aggregation.py
scripts/dialogue_audit/sync_quality_suggestions_from_checklist.py
```

Quy tắc tổng hợp:

- có tiêu chí `fail` → mẫu tổng thể là `fail`;
- không có `fail` nhưng có tiêu chí `uncertain` → mẫu tổng thể là `needs_human_review`;
- toàn bộ tiêu chí là `pass` hoặc `not_applicable` → mẫu tổng thể là `pass` hoặc nhãn tương đương `keep` ở batch cũ.

`confidence_score` tổng thể được lấy từ các tiêu chí trực tiếp kích hoạt quyết định: thấp nhất trong nhóm `fail`, hoặc thấp nhất trong nhóm `uncertain`, hoặc thấp nhất trong toàn bộ tiêu chí nếu mẫu `pass`/`keep`.

## Cách agent nên làm khi kiểm một mẫu hội thoại

1. Đọc các trường trong dòng HNMU: lớp, bài, vị trí, câu hỏi, mức nhận thức, đáp án SGV, hội thoại.
2. Dùng `resolve_learning_resource(...)` nếu metadata đủ rõ; nếu chưa đủ rõ thì dùng `search_learning_fragments(...)` với từ khóa từ câu hỏi/đáp án/hội thoại.
3. Đọc 1–5 fragment phù hợp nhất bằng `get_learning_fragment(fragment_id)`.
4. Kiểm nhất quán theo checklist dữ liệu thô `raw-dialogue-quality-checklist-v0.md`. Không dùng checklist ứng viên benchmark ở bước này. Khi kiểm dấu hiệu giàn giáo, đọc tài liệu giàn giáo theo thứ tự ưu tiên: bản Markdown chuẩn hóa `hnmu_scaffolding_method_canonical.md` → file `.docx` gốc HNMU khi cần đối chiếu → báo cáo đối chiếu.
   - câu hỏi có khớp bài/vị trí không;
   - đáp án SGV có trả lời đúng câu hỏi không;
   - hội thoại có bám câu hỏi, đáp án và lịch sử tương tác không;
   - mức nhận thức có hợp lý không;
   - mức hỗ trợ/giàn giáo có phù hợp không;
   - có trùng hoặc gần trùng với mẫu khác không.
5. Ghi kết quả từng tiêu chí vào `raw_dialogue_checklist_results.csv` trong thư mục output được giao. Mỗi dòng là một cặp `sample_id` + `criterion_id`, với `result` thuộc `pass`, `fail`, `uncertain`, `not_applicable`, kèm `confidence_score`, evidence và lý do.
6. Sau đó mới tổng hợp sang `quality_check_suggestions.csv` và `hnmu_review_queue_suggestions.csv` bằng rule strict. Không chỉ ghi một kết luận chung mà thiếu bảng checklist chi tiết.

## Không nên làm

- Không mở cả thư mục `ocr_text/` rồi đọc tuần tự như văn bản dài.
- Không sửa file Excel gốc của HNMU.
- Không tự đổi nội dung học liệu, câu hỏi, đáp án hoặc hội thoại để “khớp” với kết quả kiểm.
- Không chốt thay chuyên gia HNMU khi có nghi ngờ về kiến thức hoặc sư phạm.
- Không bỏ qua `raw_dialogue_checklist_results.csv`; nếu chỉ có `quality_check_results.csv` thì chưa đủ truy vết cho phần agent kiểm ngữ nghĩa.

## Gợi ý mở rộng Plan 04

Nếu kiểm toán dữ liệu HNMU trở thành việc lặp lại nhiều batch, nên cân nhắc tạo specialist/skill riêng, ví dụ `hnmu-dialogue-auditor`, với nhiệm vụ hẹp: kiểm độ chính xác và tính nhất quán của dữ liệu thô dựa trên `raw-dialogue-quality-checklist-v0.md`, retrieval học liệu, và phương pháp giàn giáo. Specialist này chỉ tạo kết quả kiểm toán và hàng đợi review; không sửa dữ liệu gốc và không thay HNMU quyết định chuyên môn.
