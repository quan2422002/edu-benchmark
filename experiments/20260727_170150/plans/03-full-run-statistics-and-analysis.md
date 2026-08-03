# Plan 03 — Thống kê và phân tích full run requirement-scoring

Experiment: `20260727_170150`
Trạng thái: `COMPLETED — UET REVIEW DEFERRED`
Phụ thuộc: Plan 02 hoàn tất bundle `full_gemini35_medium_v1`

## 1. Mục tiêu

Phân tích bằng code kết quả một run Gemini 3.5 Flash trên toàn bộ 2.028
candidate, nhằm trả lời:

1. sáu `requirement_score` phân bố như thế nào;
2. số candidate phân bố như thế nào theo **toàn bộ tập nguyên tắc bắt
   buộc** (`score >= 4`) và tập thay thế (`score = 3`);
3. phân bố có khác biệt đáng kể theo lớp, bài học, Bloom, lịch sử hội thoại,
   vị trí lượt gia sư và family hay không;
4. những candidate nào có dấu hiệu gán thiếu, gán tràn hoặc lập luận không
   khớp định nghĩa để UET review;
5. bao nhiêu candidate đủ điều kiện đi tiếp mà không cần UET review riêng
   ở Plan 03, và chúng phân bố ra sao;
6. kết quả có đủ hợp lý để chuyển sang xây instruction và rubric hay cần
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
trạng thái `completed_awaiting_analysis`, `runs.full.failed_candidate_ids`
còn giá trị, thiếu record hoặc hash không khớp thì dừng đóng. Trường
`errors` có thể giữ lỗi lịch sử để bảo toàn provenance; nó không phải
failure hiện hành khi trạng thái cuối đã hoàn thành, danh sách ID lỗi hiện
hành rỗng và integrity đã qua validator.

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
- phân bố đầy đủ số candidate theo từng tập nguyên tắc bắt buộc chính xác,
  kể cả tập rỗng;
- ma trận đồng xuất hiện giữa sáu nguyên tắc.

Không coi thang Likert là đo khoảng khi đưa ra kết luận; trung bình chỉ là
thống kê bổ trợ, phân bố mức và tỷ lệ vượt ngưỡng là kết quả chính.

### Bước 2.1 — Phân bố theo tập nguyên tắc bắt buộc

Trong Plan này, “tập nguyên tắc chính” được hiểu là **tập không thứ tự gồm
mọi nguyên tắc có `requirement_score >= 4`**, không phải một nguyên tắc
đứng đầu duy nhất.

Code chuẩn hóa mỗi tập theo thứ tự sáu `principle_id`, rồi báo cho từng tập
quan sát được:

- số candidate và tỷ lệ trên 2.028 candidate;
- số family có ít nhất một candidate thuộc tập đó;
- tỷ lệ family-macro: tính tỷ lệ candidate thuộc tập trong từng
  `sample_id`, rồi trung bình trên 665 family;
- phân bố theo lớp 6–9;
- số lượng theo kích thước tập: 0, 1, 2, 3 và trên 3 nguyên tắc.

Tổng số candidate của mọi tập phải bằng 2.028; tổng tỷ lệ
candidate-macro và family-macro của mọi tập đều phải bằng 1 trong sai số
làm tròn. Báo cáo Markdown trình bày toàn bộ tập quan sát được theo số mẫu
giảm dần; JSON giữ cả bảng đầy đủ và các phân tầng chi tiết. Tập cực hiếm
được gắn cờ review nhưng không bị gộp thành “khác”.

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

### Bước 5.1 — Phân bố trạng thái đủ điều kiện đi tiếp

Code chia toàn bộ 2.028 candidate thành ba trạng thái loại trừ nhau:

- `eligible_without_plan03_review`: có từ 1–3 nguyên tắc bắt buộc, qua mọi
  kiểm tra cấu trúc/evidence và không có cờ rủi ro ngữ nghĩa hoặc tổ hợp
  hiếm;
- `needs_uet_review`: có ít nhất một cờ review nhưng không có lỗi cấu trúc
  chặn xử lý;
- `blocked`: thiếu/sai input, evidence không truy được hoặc lỗi cấu trúc
  khiến candidate chưa thể đi tiếp.

Chỉ tạo ba trạng thái sau khi cổng toàn vẹn cấp bundle đã đạt. Nếu cổng
này thất bại thì dừng toàn bộ và không công bố số eligible; `blocked` chỉ
dành cho lỗi cục bộ được phát hiện sau khi join.

UET khóa trước khi triển khai:

- một tập nguyên tắc bắt buộc chính xác được coi là `rare_required_set`
  nếu xuất hiện ở dưới 5 candidate **hoặc** dưới 3 family;
- phân tầng có dưới 10 candidate chỉ được gắn cảnh báo quy mô nhỏ trong
  báo cáo, không tự động làm candidate vào review;
- khác biệt tỷ lệ giữa các phân tầng chỉ là thống kê mô tả trong Plan 03,
  không được dùng một ngưỡng outlier tùy ý để kết luận candidate có lỗi;
- candidate chỉ vào review do tổ hợp phân bố khi chính tập nguyên tắc của
  nó đạt điều kiện `rare_required_set` ở trên.

Các ngưỡng này nhằm phát hiện tổ hợp gần như cá biệt mà không biến mọi
khác biệt coverage giữa lớp/bài học thành lỗi cấp mẫu.

Báo cáo phải nêu số lượng và tỷ lệ của ba trạng thái, rồi phân bố
`eligible_without_plan03_review` theo:

- tập nguyên tắc bắt buộc chính xác và kích thước tập;
- lớp 6–9, bài học/chủ đề và Bloom;
- có/không có lịch sử hội thoại và vị trí target;
- family: toàn bộ candidate đủ điều kiện, family trộn hai trạng thái, hoặc
  không có candidate nào đủ điều kiện.

JSON lưu danh sách `benchmark_candidate_id` của từng trạng thái và số
lượng theo từng lý do review/block; không tạo thêm file output. Ba nhóm
phải không giao nhau và có tổng đúng 2.028.

`eligible_without_plan03_review` chỉ có nghĩa candidate không cần **review
riêng tại Plan 03** trước khi chuyển sang bước xây rubric/audit candidate.
Nó không phải nhãn HNMU xác nhận, không bỏ qua audit `gold_response`,
grounding và chất lượng candidate ở Plan 06, và chưa đồng nghĩa được công
bố trong benchmark cuối. Một mẫu nhỏ trong nhóm này vẫn được chọn ngẫu
nhiên để kiểm đối chứng; nếu phát hiện lỗi có hệ thống thì phải mở rộng cờ
và tính lại toàn bộ trạng thái bằng code.

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

`full_run_analysis.json` chứa toàn bộ bảng thống kê lồng nhau, ba danh sách
trạng thái eligibility và lý do phân loại để tránh tạo nhiều CSV nhỏ.
Markdown trình bày số liệu chính và quyết định cần review. CSV chỉ chứa
candidate thực sự cần UET xem cùng mẫu kiểm đối chứng.

## 6. Cổng hoàn thành

Plan chỉ hoàn thành khi:

1. input và mọi join đạt kiểm toàn vẹn;
2. tổng mọi bảng phân bố khớp 2.028 candidate và 12.168 score;
3. phân bố theo tập nguyên tắc bắt buộc có đầy đủ số candidate,
   candidate-macro, family-macro và tổng kiểm tra khớp 2.028;
4. ba trạng thái eligibility loại trừ nhau, tổng đúng 2.028 và nhóm đủ
   điều kiện có thống kê theo nguyên tắc, lớp, metadata và family;
5. không dùng model/agent cho phép tính xác định;
6. lint mới có test positive và near-miss, không lặp lỗi dương tính giả đã
   thấy ở calibration;
7. ba artifact tinh gọn tái tạo được từ input khóa;
8. mọi giới hạn của single-run được nêu rõ;
9. UET đã quyết định disposition ngay hoặc ghi rõ việc hoãn review cùng
   phạm vi dữ liệu được phép chuyển tiếp;
10. roadmap, handoff và evidence registry của paper được cập nhật.

## 7. Kết quả triển khai

Code và ba artifact đã được tạo, mọi kiểm tra toàn vẹn đều đạt:

- 2.028 candidate, 665 family và 12.168 score;
- 1.400 `eligible_without_plan03_review`;
- 628 `needs_uet_review`;
- 0 `blocked`;
- review queue có 628 candidate bị cờ và 8 mẫu đối chứng phân tầng;
- cờ lớn nhất là `feedback_confirmation_only` ở 592 candidate.

UET quyết định ngày 2026-07-28:

- đóng Plan 03 ở trạng thái hoàn thành về phân tích;
- ưu tiên 1.400 `eligible_without_plan03_review` cho các plan tiếp theo;
- hoãn disposition của 628 `needs_uet_review` thành backlog, không coi các
  mẫu này là đã được duyệt, bị loại hoặc được sửa nhãn;
- không có score nào bị code tự sửa.

Quyết định này chỉ đóng cổng vận hành của Plan 03. Nó không biến 1.400
mẫu thành ground truth hoặc benchmark đã được HNMU xác nhận; các audit
`gold_response`, grounding và chất lượng candidate ở plan sau vẫn giữ
nguyên.
