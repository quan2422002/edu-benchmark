# Báo cáo kế thừa cho experiment `20260722_000940`

Ngày lập: 22/07/2026  
Mục đích: xác định những thông tin có thể kế thừa từ hai experiment gần nhất để bắt đầu giai đoạn 2: xây dựng mẫu benchmark từ dữ liệu thô đã pass.

## 1. Kết luận nhanh

Có đủ nền tảng để mở experiment mới cho giai đoạn 2.

Hai experiment trước đang bổ trợ cho nhau khá rõ:

- `20260705_215045` trả lời câu hỏi “benchmark nên có task/rubric/độ phủ như thế nào?”.
- `20260709_155523` trả lời câu hỏi “dữ liệu thô HNMU mẫu nào đủ sạch để chuyển đổi tiếp?”.

Vì vậy, giai đoạn 2 không nên bắt đầu từ đầu. Nên bắt đầu bằng cách lấy 665 mẫu đã `pass` ở giai đoạn 1, ghép với task/rubric v0 và registry học liệu Tin học THCS lớp 6–9, rồi chuyển thành ứng viên benchmark có cấu trúc.

Phạm vi đã được cập nhật ngày 23/07/2026: benchmark chuyển hẳn sang miền Tin học THCS lớp 6–9. Ma trận coverage 96 ô kế thừa từ experiment `20260705_215045` thiên về lớp 9 nên chỉ còn là khung tham khảo cho các trục thiết kế, không phải coverage chuẩn đầy đủ của giai đoạn 2.

## 2. Những thứ kế thừa từ experiment `20260705_215045`

### 2.1. Task hành vi gia sư v0

File nguồn: `experiments/20260705_215045/benchmark_design/benchmark_tasks.csv`

Hiện có 4 task:

| Task | Tên task | Vai trò trong giai đoạn 2 |
|---|---|---|
| T1 | Giải thích thích ứng | Dùng cho mẫu cần gia sư giải thích khái niệm/thao tác theo mức hiểu của học sinh. |
| T2 | Phản hồi bài làm hoặc lập luận của học sinh | Dùng cho mẫu có bài làm, đáp án, lập luận, thao tác hoặc sản phẩm của học sinh cần phản hồi. |
| T3 | Gợi ý từng bước để học sinh tự đi tiếp | Dùng cho mẫu cần gia sư dẫn dắt bằng gợi ý, không làm thay quá sớm. |
| T4 | Chẩn đoán lỗi, hiểu lầm hoặc thiếu nền tảng | Dùng cho mẫu cần phát hiện lỗi sai, hiểu lầm, thiếu kiến thức nền hoặc nguyên nhân học sinh bị kẹt. |

Nhận xét kế thừa: 4 task này phù hợp để giai đoạn 2 gán task sơ bộ cho ứng viên benchmark. Tuy nhiên, trạng thái trong file gốc vẫn là v0, nên các mẫu không chắc task cần đưa vào review queue.

### 2.2. Rubric v0

File nguồn: `experiments/20260705_215045/benchmark_design/rubrics.csv`

Hiện có 20 rubric: 5 tiêu chí cho mỗi task, chấm theo thang Likert 1–5.

Năm nhóm tiêu chí cốt lõi là:

1. Độ chính xác kiến thức và bám học liệu.
2. Hiểu đúng yêu cầu, trạng thái và lỗi của học sinh.
3. Chất lượng hỗ trợ sư phạm/giàn giáo.
4. Tuân thủ mục tiêu task, yêu cầu của học sinh và phạm vi học liệu.
5. Tuân thủ ranh giới an toàn, đạo đức và pháp lý.

Nhận xét kế thừa: rubric v0 đủ dùng để gắn vào ứng viên benchmark, nhưng chưa nên coi là bản cuối cùng. Ở giai đoạn 2, mỗi mẫu nên lưu rõ rubric nào được áp dụng và lý do.

### 2.3. Ma trận bao phủ v0

File nguồn:

- `experiments/20260705_215045/coverage_design/general_coverage_matrix_v0.csv`
- `experiments/20260705_215045/coverage_design/coverage_axis_values_v0.csv`

Hiện có 96 ô bao phủ, gồm các trục chính:

- chủ đề/bài học;
- task/hành vi gia sư;
- mức nhận thức;
- dạng câu hỏi;
- dạng bài làm của học sinh;
- mức ưu tiên tạo ví dụ.

Nhận xét kế thừa: ma trận này có thể dùng để tham khảo cách tổ chức task, mức nhận thức và dạng bài. Không dùng tám cụm chủ đề Tin học 9 trong ma trận làm toàn bộ không gian coverage mới. Coverage sau chuyển đổi phải dựa trên registry chủ đề/bài học lớp 6–9 và dữ liệu ứng viên thực tế.

### 2.4. Ví dụ phiếu tác giả và ví dụ hội thoại

Thư mục nguồn: `experiments/20260705_215045/teacher_examples/`

Có 17 ví dụ phiếu tác giả, một số ví dụ hội thoại nhiều lượt và ghi chú chuyển đổi mẫu HNMU.

Nhận xét kế thừa: đây là tài liệu tham khảo tốt để thiết kế output dễ đọc cho HNMU/UET, nhưng không nên tự động coi các ví dụ này là dữ liệu thật.

## 3. Những thứ kế thừa từ experiment `20260709_155523`

### 3.1. Dữ liệu thô đã chuẩn hóa

File nguồn:

- `experiments/20260709_155523/outputs/hnmu_dialogue_audit/normalized_dialogue_rows.csv`
- `experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/normalized_dialogue_rows.csv`

Hai file này là đầu vào thuận tiện nhất cho chuyển đổi vì đã chuẩn hóa về các trường như:

- `sample_id`;
- `source_file`;
- `source_row_number`;
- `grade`;
- `lesson`;
- `position`;
- `question`;
- `bloom_level`;
- `answer_sgv`;
- `dialogue`.

### 3.2. Kết quả đánh giá dữ liệu thô

File nguồn chính:

- `experiments/20260709_155523/outputs/hnmu_dialogue_audit/agent_shard_audit/merged/quality_check_suggestions.csv`
- `experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/quality_check_suggestions.csv`

Kết quả tổng hợp:

| Nhóm dữ liệu | Tổng mẫu | Pass | Cần người xem lại | Failed |
|---|---:|---:|---:|---:|
| Lớp 6–7 | 462 | 238 | 222 | 2 |
| Lớp 8–9 | 588 | 427 | 160 | 1 |
| Tổng | 1.050 | 665 | 382 | 3 |

Nhận xét kế thừa: nhóm `pass` là đầu vào mặc định cho chuyển đổi. Nhóm `need_human_review` có thể để riêng để xử lý sau, không nên trộn vào batch sạch đầu tiên.

### 3.2.1. Ý nghĩa của evidence ở hai cấp output

Định nghĩa dưới đây được đối chiếu với Plan 04, Plan 07, `raw-dialogue-quality-checklist-v0.md`, báo cáo đồng bộ output ngày 19–20/07/2026 và hai báo cáo batch của experiment `20260709_155523`.

`evidence_fragment_ids` trong `quality_check_suggestions.csv` không phải danh sách đầy đủ các fragment đã dùng để audit. Rule tổng hợp phase 1 chỉ đưa lên file cấp mẫu những fragment thuộc tiêu chí trực tiếp kích hoạt `fail` hoặc `uncertain`.

Kết quả rà lại snapshot hiện tại:

| Nhóm | Mẫu pass | Pass có fragment ở file cấp mẫu | Pass có fragment ở checklist chi tiết |
|---|---:|---:|---:|
| Lớp 6–7 | 238 | 0 | 238 |
| Lớp 8–9 | 427 | 0 | 427 |
| Tổng | 665 | 0 | 665 |

Do đó, phase 2 giữ hai trường raw-audit riêng:

- `raw_audit_blocking_evidence_fragment_ids`: bản chuẩn hóa của cột cấp mẫu `evidence_fragment_ids`; với nhóm `pass` trường này rỗng vì không có tiêu chí chặn.
- `raw_audit_all_evidence_fragment_ids`: union toàn bộ `evidence_fragment_id` không rỗng từ checklist chi tiết; với 665 mẫu `pass` hiện tại trường này khác rỗng.

Plan 01 không tái sử dụng tên `evidence_fragment_ids` cho evidence cấp benchmark candidate. Candidate-level evidence sẽ được định nghĩa và kiểm riêng trong Plan 04.

### 3.3. Checklist chất lượng ứng viên benchmark

File nguồn: `experiments/20260709_155523/reports/benchmark-candidate-quality-checklist-v0.md`

Checklist này tách biệt với checklist dữ liệu thô. Nó dùng để kiểm các mẫu sau khi đã được chuyển đổi thành ứng viên benchmark.

Các nhóm kiểm quan trọng:

- cấu trúc mẫu benchmark;
- task/hành vi gia sư;
- rubric và khả năng chấm;
- học liệu và truy vết;
- chất lượng `gold_response`;
- trùng/gần trùng và rò đáp án;
- điều kiện đưa vào pilot.

Nhận xét kế thừa: đây là cơ sở chính để thiết kế bước đánh giá chất lượng ứng viên benchmark ở experiment mới.

### 3.4. Học liệu SGK/SGV và truy xuất

Nguồn dùng lại:

- `shared/learning_resources/registries/ocr_text_manifest.csv`
- `shared/learning_resources/fragments/learning_resource_fragments.csv`
- `shared/learning_resources/indexes/learning_resources_v0.sqlite`
- `shared/learning_resources/agent_context/README.md`
- `shared/learning_resources/agent_context/hnmu_scaffolding_method_canonical.md`
- `shared/learning_resources/agent_context/hnmu_cognitive_level_method_canonical.md`

Hiện có:

- 154 đơn vị OCR SGK/SGV Tin học 6–9;
- 2.750 fragment học liệu;
- SQLite full-text search có thể rebuild;
- tài liệu ngữ cảnh để agent truy xuất học liệu, phương pháp giàn giáo và mức nhận thức.

Nhận xét kế thừa: đủ dùng cho bước kiểm truy vết/học liệu của ứng viên benchmark. Cần nhớ rằng một số fragment vẫn có trạng thái `draft`, nên kết quả truy xuất là căn cứ hỗ trợ, không thay thế xác nhận chuyên môn HNMU.

## 4. Những thông tin nên dùng làm nguồn sự thật trong experiment mới

| Loại thông tin | Nguồn nên dùng | Ghi chú |
|---|---|---|
| Dữ liệu thô để chuyển đổi | `normalized_dialogue_rows.csv` của lớp 6–7 và 8–9 | Không đọc trực tiếp Excel gốc nếu không cần. |
| Quyết định mẫu sạch | `quality_check_suggestions.csv` trong `agent_shard_audit/merged/` | Chỉ lấy `quality_decision = pass` cho batch đầu. |
| Evidence chặn quyết định raw audit | `quality_check_suggestions.evidence_fragment_ids` | Giữ đúng semantics phase 1; mẫu pass rỗng, mẫu review/failed chỉ khác rỗng khi dòng chặn viện dẫn fragment. |
| Toàn bộ evidence raw audit | Checklist chi tiết `raw_dialogue_checklist_results.repaired.csv` và `raw_dialogue_checklist_results.regex_repaired.csv` | Tổng hợp mọi `evidence_fragment_id` không rỗng thành trường dẫn xuất có tên riêng. |
| Tiêu chí kiểm ứng viên benchmark | `benchmark-candidate-quality-checklist-v0.md` | Không dùng checklist dữ liệu thô cho mẫu đã chuyển đổi. |
| Task/rubric | `benchmark_tasks.csv`, `rubrics.csv` từ experiment 20260705 | Trạng thái v0, cần lưu confidence khi agent gán. |
| Học liệu | fragments + SQLite trong `shared/learning_resources/` | Dùng để truy vết SGK/SGV. |
| Mức nhận thức | `hnmu_cognitive_level_method_canonical.md` | Ba mức: Biết, Hiểu, Vận dụng. |
| Phương pháp giàn giáo | `hnmu_scaffolding_method_canonical.md` | Dùng khi kiểm chất lượng hỗ trợ sư phạm. |

## 5. Các rủi ro khi chuyển sang giai đoạn 2

1. Tách hội thoại sai: `student_prompt`, `conversation_history`, `gold_response` có thể bị cắt nhầm nếu hội thoại không theo nhãn lượt nói ổn định.
2. Lẫn `gold_answer` với `gold_response`: nếu không tách rõ, mẫu có thể làm rò đáp án hoặc làm sai mục tiêu chấm tutor.
3. Gán task bằng suy diễn quá mạnh: task phải dựa trên hành vi gia sư cần đánh giá, không chỉ dựa trên mức nhận thức.
4. Một hội thoại tạo nhiều mẫu: có ích, nhưng dễ tạo mẫu gần trùng nếu không quản lý truy vết và mục tiêu từng mẫu.
5. Dữ liệu `pass` ở giai đoạn 1 không có nghĩa là ứng viên benchmark chắc chắn đạt: chuyển đổi có thể tạo lỗi mới.
6. Học liệu fragment vẫn có trạng thái draft: cần lưu cờ và confidence, không biến kết quả retrieval thành “chân lý tuyệt đối”.

## 6. Đề xuất bước tiếp theo

Nên bắt đầu bằng một plan hẹp:

1. Lọc toàn bộ mẫu `pass`.
2. Ghép với dòng chuẩn hóa và tổng hợp raw-audit evidence từ checklist chi tiết.
3. Tách hội thoại bằng quy tắc deterministic trước.
4. Tạo ứng viên benchmark bản nháp.
5. Chạy checklist ứng viên benchmark trên batch nhỏ.
6. Sau khi batch kiểm tra vượt qua validation, tiếp tục xử lý toàn bộ 665 mẫu pass.

Điểm mấu chốt: toàn bộ 665 mẫu pass nằm trong phạm vi ưu tiên, nhưng cần một cổng kiểm tra nhỏ trước khi chạy full batch để tránh nhân rộng lỗi conversion.
