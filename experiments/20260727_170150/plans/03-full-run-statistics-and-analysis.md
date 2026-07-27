# Plan 03 — Thống kê và phân tích full run requirement-scoring

Experiment: `20260727_170150`  
Trạng thái: `DRAFT — AWAITING_UET_REVIEW; DO_NOT_IMPLEMENT`  
Phụ thuộc: Plan 02 hoàn tất bundle `full_gemini35_medium_v1`

## 1. Mục tiêu

Phân tích bằng code kết quả một run Gemini 3.5 Flash trên toàn bộ 2.028
candidate, nhằm trả lời:

1. sáu `requirement_score` phân bố như thế nào;
2. tập nguyên tắc bắt buộc (`score >= 4`) và tập thay thế (`score = 3`)
   bao phủ dữ liệu ra sao;
3. phân bố có khác biệt đáng kể theo lớp, bài học, Bloom, lịch sử hội thoại,
   vị trí lượt gia sư và family hay không;
4. những candidate nào có dấu hiệu gán thiếu, gán tràn hoặc lập luận không
   khớp định nghĩa để UET review;
5. kết quả có đủ hợp lý để chuyển sang xây instruction và rubric hay cần
   hiệu chỉnh phương pháp.

Plan này không gọi thêm model hoặc agent để tính thống kê, không tự sửa
score và không gọi output một run là nhãn đúng hay ground truth.

## 2. Input khóa

- `outputs/principle_requirement_scoring/full_gemini35_medium_v1/run_full.jsonl`;
- `outputs/principle_requirement_scoring/full_gemini35_medium_v1/run_manifest.json`;
- grounding pool 2.028 dòng đã khóa;
- `conversion_trace.csv` để lấy `target_tutor_turn_index`;
- specification V4, schema V2 và system prompt V4.

Mọi input phải được kiểm SHA-256 trước khi phân tích. Nếu manifest chưa có
trạng thái `completed_awaiting_analysis`, còn candidate lỗi, thiếu record
hoặc hash không khớp thì dừng đóng.

## 3. Giới hạn diễn giải

Đây là một run duy nhất nên không được báo:

- độ ổn định A/B;
- exact agreement, Jaccard hay F1 giữa hai run;
- accuracy nếu chưa có nhãn chuyên gia;
- độ tin cậy thống kê của model như một annotator đã được xác nhận;
- kết luận rằng nguyên tắc vắng mặt trong output là không quan trọng về
  mặt sư phạm.

Kết quả calibration chỉ được dùng làm thông tin hạn chế đã biết của
phương pháp, không dùng để sửa score full run hoặc suy ra accuracy của
2.028 candidate.

## 4. Quy trình tuần tự

### Bước 1 — Kiểm toàn vẹn

Code kiểm:

- đúng 2.028 `benchmark_candidate_id` duy nhất;
- join một-một với grounding pool và conversion trace;
- đủ 665 `sample_id`;
- mỗi record có đúng sáu nguyên tắc, score trong 1–5;
- `user_prompt` tái tạo khớp chính xác input;
- request hash, model/config và file hash khớp manifest;
- không còn failure, duplicate hoặc response rỗng.

### Bước 2 — Thống kê phân bố điểm

Với từng nguyên tắc và toàn bộ dữ liệu:

- số lượng/tỷ lệ score 1–5;
- trung vị, tứ phân vị và trung bình chỉ dùng mô tả;
- số lượng/tỷ lệ `score >= 4`;
- số lượng/tỷ lệ `score = 3`;
- phân bố số nguyên tắc bắt buộc trên mỗi candidate;
- các tổ hợp nguyên tắc bắt buộc phổ biến;
- ma trận đồng xuất hiện giữa sáu nguyên tắc.

Không coi thang Likert là đo khoảng khi đưa ra kết luận; trung bình chỉ là
thống kê bổ trợ, phân bố mức và tỷ lệ vượt ngưỡng là kết quả chính.

### Bước 3 — Báo cáo candidate-macro và family-macro

Mọi coverage chính phải có hai cách tính:

- `candidate-macro`: mỗi candidate có trọng số như nhau;
- `family-macro`: tính tỷ lệ trong từng `sample_id`, sau đó trung bình trên
  665 family để hội thoại dài không chi phối kết quả.

Code còn báo số candidate trên mỗi family và kiểm các family có nhiều
target có tạo phân bố nguyên tắc khác thường hay không.

### Bước 4 — Phân tầng

Phân tích theo:

- lớp 6, 7, 8, 9;
- bài học/chủ đề;
- Bloom;
- có/không có `conversation_history`;
- số lượt trong history;
- `target_tutor_turn_index`;
- vị trí đầu, giữa, cuối trong family.

Với strata quá nhỏ, chỉ báo số đếm và gắn cảnh báo; không diễn giải tỷ lệ
như một xu hướng ổn định.

### Bước 5 — Kiểm rủi ro ngữ nghĩa bằng code

Trước khi chạy lint trên full output, sửa và kiểm thử regex để không bắt
nhầm từ “có thể” nằm trong phần phản chứng
`Nếu bỏ nguyên tắc này:`. Lint chỉ tạo cờ review, không thay đổi score.

Review queue gồm:

- không có nguyên tắc nào đạt 4;
- hơn ba nguyên tắc đạt 4;
- Feedback cao nhưng chỉ xác nhận/khen, không dẫn hướng cải thiện;
- Questioning cao nhưng không chứng minh phản hồi phụ thuộc vào câu trả
  lời học sinh;
- score 4–5 thiếu cổng nhu cầu độc lập hoặc phản chứng;
- rationale/evidence nói nguyên tắc chỉ là tùy chọn;
- evidence không truy được về payload;
- các tổ hợp cực hiếm hoặc outlier theo strata;
- một mẫu phân tầng các candidate không bị cờ để kiểm đối chứng.

### Bước 6 — UET review

UET review theo thứ tự:

1. lỗi cấu trúc/evidence;
2. trường hợp gán tràn hoặc không có nguyên tắc bắt buộc;
3. ranh giới Feedback và Questioning;
4. tổ hợp nguyên tắc hiếm;
5. mẫu đối chứng bình thường.

UET chỉ ghi disposition và ghi chú; không sửa trực tiếp `run_full.jsonl`.
Nếu cần correction, plan sau phải dùng bảng overlay riêng có provenance.

### Bước 7 — Kết luận và paper packet

Báo cáo phải tách:

- `evidence`: số liệu trực tiếp từ run;
- `inference`: diễn giải của UET/nhóm nghiên cứu;
- `teacher_decision_needed`: điểm cần HNMU xác nhận.

Chỉ sau disposition mới quyết định chuyển sang plan instruction/rubric.
Các số liệu đủ ổn định được chuyển sang evidence registry của paper KSE;
không đưa claim về accuracy hoặc expert agreement khi chưa có bằng chứng.

## 5. Code và artifact

Khi plan được duyệt, code mới đặt tại:

```text
src/vertex_ai_call/analyze_requirement_scoring.py
```

Không gọi model. Toàn bộ phép join, lọc, đếm, sampling và xuất báo cáo
dùng code xác định, có test dưới `tests/vertex_ai_call/`.

Chỉ tạo ba artifact mới trong bundle full:

```text
full_gemini35_medium_v1/
├── full_run_analysis.json
├── full_run_analysis.md
└── full_run_review_queue.csv
```

`full_run_analysis.json` chứa toàn bộ bảng thống kê lồng nhau để tránh tạo
nhiều CSV nhỏ. Markdown chỉ trình bày số liệu chính và quyết định cần
review. CSV chỉ chứa candidate thực sự cần UET xem.

## 6. Cổng hoàn thành

Plan chỉ hoàn thành khi:

1. input và mọi join đạt kiểm toàn vẹn;
2. tổng mọi bảng phân bố khớp 2.028 candidate và 12.168 score;
3. coverage có cả candidate-macro và family-macro;
4. không dùng model/agent cho phép tính xác định;
5. lint mới có test positive và near-miss, không lặp lỗi dương tính giả đã
   thấy ở calibration;
6. ba artifact tinh gọn tái tạo được từ input khóa;
7. mọi giới hạn của single-run được nêu rõ;
8. UET review có disposition, còn quyết định sư phạm được giữ cho HNMU;
9. roadmap, handoff và evidence registry của paper được cập nhật.
