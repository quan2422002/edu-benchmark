# Giải thích cột trong các file CSV pilot `hnmu-dialogue-auditor`

Ngày tạo: 17/07/2026  
Phạm vi: chỉ áp dụng cho output pilot trong thư mục này.  
Mục đích: giúp Quân xem cột nào thực sự cần giữ lại trước khi chạy audit rộng hoặc merge vào output chính của Plan 04.

Quy ước trong cột “Nên giữ ở v0?”:

- `Nên giữ`: cột quan trọng cho truy vết, review hoặc tổng hợp.
- `Có thể gộp/bỏ sau`: hữu ích ở pilot, nhưng có thể gộp hoặc bỏ khi format ổn định.
- `Chỉ để debug/pilot`: chủ yếu dùng để kiểm thử quy trình, không nhất thiết giữ trong output chính.

## 1. `pilot_sample_selection.csv`

File này chỉ giải thích **vì sao những mẫu này được chọn để chạy pilot**. Nó không phải output kiểm toán chính.

| Cột | Ý nghĩa | Nên giữ ở v0? | Lý do |
|---|---|---|---|
| `sample_id` | Mã định danh mẫu thô trong batch HNMU. | Nên giữ | Khóa chính để nối với mọi file khác. |
| `source_file` | File Excel gốc chứa mẫu. | Nên giữ | Cần để truy vết về dữ liệu thô. |
| `source_row_number` | Số dòng trong file gốc/normalized data. | Nên giữ | Giúp tìm lại đúng dòng trong file HNMU. |
| `grade` | Khối lớp của mẫu. | Nên giữ | Cần cho kiểm độ phủ và lọc dữ liệu. |
| `lesson` | Bài học do dữ liệu thô ghi. | Nên giữ | Cần để xem pilot có rải đều theo bài hay không. |
| `position` | Vị trí học liệu, ví dụ mục/trang SGK. | Có thể gộp/bỏ sau | Hữu ích khi chọn mẫu, nhưng output chính có thể truy qua `sample_id`. |
| `question` | Câu hỏi/nhiệm vụ học sinh trong mẫu thô. | Có thể gộp/bỏ sau | Dễ đọc khi soi pilot, nhưng có thể làm file nặng và lặp dữ liệu gốc. |
| `bloom_level` | Mức nhận thức do HNMU ghi. | Có thể gộp/bỏ sau | Hữu ích để soi phân bố pilot; output chính có thể lấy từ normalized rows. |

Khuyến nghị: giữ file này cho pilot; khi chạy chính thức, có thể thay bằng `audit_shard_manifest.csv` gọn hơn gồm `sample_id`, `source_file`, `source_row_number`, `grade`, `lesson`.

## 2. `raw_dialogue_checklist_results.csv`

Đây là file quan trọng nhất. Mỗi dòng là kết quả kiểm **một tiêu chí** trên **một mẫu**. File này giúp truy vết vì sao một mẫu được kết luận `pass`, `fail` hoặc `needs_human_review`.

| Cột | Ý nghĩa | Nên giữ ở v0? | Lý do |
|---|---|---|---|
| `sample_id` | Mã mẫu được kiểm. | Nên giữ | Khóa nối với dữ liệu thô, output tổng hợp và review queue. |
| `criterion_id` | Mã tiêu chí kiểm, ví dụ `RAW-CON-01`. | Nên giữ | Khóa để biết mẫu trượt/đạt tiêu chí nào. |
| `criterion_group` | Nhóm tiêu chí, ví dụ `structure`, `consistency`, `pedagogy`, `duplicate_risk`. | Nên giữ | Giúp tổng hợp lỗi theo nhóm. |
| `criterion_name` | Tên tiêu chí bằng ngôn ngữ dễ đọc. | Nên giữ | Giúp người đọc không phải tra mã tiêu chí liên tục. |
| `result` | Kết quả tiêu chí: `pass`, `fail`, `uncertain`, `not_applicable`. | Nên giữ | Đây là giá trị cốt lõi của checklist. |
| `confidence_score` | Mức tự tin của agent với riêng tiêu chí đó, từ 0 đến 1. | Nên giữ | Giúp phân biệt lỗi chắc chắn và lỗi cần người xem lại. |
| `evidence_fragment_id` | Mã fragment SGK/SGV dùng làm bằng chứng, nếu có. | Nên giữ | Cần cho truy vết học liệu. |
| `evidence_source` | Đường dẫn/tên nguồn evidence, thường là Markdown học liệu hoặc tên sách. | Nên giữ | Giúp người review mở đúng nguồn mà không phải tra thêm. |
| `evidence_match_reason` | Vì sao evidence được xem là liên quan. | Nên giữ | Rất quan trọng để phát hiện agent chọn nhầm evidence. |
| `reason` | Lý do agent đưa ra kết quả tiêu chí. | Nên giữ | Đây là phần giải thích chính cho người review. |
| `suggested_reviewer_action` | Hành động gợi ý, ví dụ `keep`, `ask_hnmu_review`, `exclude_from_current_batch`. | Nên giữ | Giúp chuyển checklist thành việc cần làm. |
| `checked_by` | Ai/cơ chế nào kiểm, ví dụ `hnmu-dialogue-auditor(single-agent-pilot)`. | Có thể gộp/bỏ sau | Hữu ích khi nhiều agent/người cùng kiểm; nếu chỉ một pipeline cố định thì có thể đưa vào metadata file. |
| `checked_at` | Thời điểm kiểm. | Có thể gộp/bỏ sau | Cần cho audit trail, nhưng có thể chuyển sang metadata batch nếu muốn CSV gọn hơn. |

Khuyến nghị: giữ hầu hết các cột trong file này ở v0. Nếu muốn rút gọn, chỉ nên cân nhắc chuyển `checked_by` và `checked_at` sang metadata cấp batch, không nên bỏ các cột evidence/reason.

## 3. `quality_check_suggestions.csv`

File này tổng hợp từ checklist chi tiết sang **gợi ý quyết định cấp mẫu**. Đây chưa phải quyết định cuối cùng của HNMU/UET.

| Cột | Ý nghĩa | Nên giữ ở v0? | Lý do |
|---|---|---|---|
| `sample_id` | Mã mẫu thô. | Nên giữ | Khóa chính. |
| `source_file` | File Excel gốc. | Nên giữ | Truy vết nhanh về dữ liệu thô. |
| `source_row_number` | Dòng nguồn trong file gốc/normalized data. | Nên giữ | Truy vết nhanh về dữ liệu thô. |
| `grade` | Khối lớp. | Nên giữ | Cần cho lọc và thống kê. |
| `lesson` | Bài học. | Nên giữ | Cần cho lọc và review theo bài. |
| `quality_decision_suggestion` | Gợi ý quyết định cấp mẫu: `pass`, `fail`, `needs_human_review`. | Nên giữ | Đây là kết luận tổng hợp chính. |
| `confidence_score` | Mức tự tin tổng hợp cấp mẫu. | Nên giữ | Giúp ưu tiên review mẫu không chắc. |
| `failure_reasons` | Tóm tắt các tiêu chí `fail`/`uncertain` nổi bật. | Nên giữ | Giúp người đọc hiểu nhanh trước khi mở checklist chi tiết. |
| `suggested_reviewer_action` | Hành động gợi ý ở cấp mẫu. | Nên giữ | Dùng để điều phối review/chuyển đổi. |
| `needs_hnmu_review` | Có cần HNMU xem lại không. | Nên giữ | Cờ điều phối rất hữu ích. |
| `needs_learning_resource_review` | Có cần xem lại evidence học liệu không. | Nên giữ | Tách lỗi dữ liệu thô khỏi lỗi truy xuất/học liệu. |
| `needs_sgv_verification` | Có cần xác minh lại SGV không. | Nên giữ | Rất quan trọng vì nhiều mẫu pass vẫn chưa có evidence SGV đủ chắc. |
| `evidence_fragment_ids` | Danh sách fragment liên quan. | Nên giữ | Giúp mở nhanh evidence chính. |
| `checked_by` | Cơ chế/người tạo gợi ý. | Có thể gộp/bỏ sau | Có thể chuyển sang metadata batch nếu chỉ một pipeline. |
| `checked_at` | Thời điểm tạo gợi ý. | Có thể gộp/bỏ sau | Có thể chuyển sang metadata batch. |

Khuyến nghị: file này nên giữ trong output chính, nhưng tên có thể đổi từ `quality_check_suggestions.csv` thành `quality_check_results.csv` sau khi quy trình được duyệt. Cần giữ rõ chữ `suggestion` nếu chưa có người duyệt.

## 4. `hnmu_review_queue_suggestions.csv`

File này là danh sách mẫu agent đề xuất đưa vào hàng đợi HNMU/UET xem lại.

| Cột | Ý nghĩa | Nên giữ ở v0? | Lý do |
|---|---|---|---|
| `sample_id` | Mã mẫu cần review. | Nên giữ | Khóa chính để tìm mẫu. |
| `grade` | Khối lớp. | Nên giữ | Giúp phân công theo lớp. |
| `lesson` | Bài học. | Nên giữ | Giúp HNMU/UET lọc theo bài. |
| `review_reason` | Lý do mẫu cần review. | Nên giữ | Nội dung cốt lõi để người review hiểu vấn đề. |
| `priority` | Mức ưu tiên, ví dụ `high`, `medium`. | Nên giữ | Giúp xử lý mẫu nghiêm trọng trước. |
| `suggested_question_to_hnmu` | Câu hỏi gợi ý gửi HNMU. | Nên giữ | Giúp biến lỗi kỹ thuật thành câu hỏi dễ trả lời cho thầy cô. |
| `related_criterion_ids` | Các tiêu chí liên quan tới lý do review. | Nên giữ | Truy vết từ review queue về checklist chi tiết. |
| `evidence_fragment_ids` | Fragment học liệu liên quan. | Nên giữ | Giúp reviewer mở evidence nhanh. |
| `checked_by` | Cơ chế/người đưa vào queue. | Có thể gộp/bỏ sau | Có thể chuyển sang metadata batch. |
| `checked_at` | Thời điểm đưa vào queue. | Có thể gộp/bỏ sau | Có thể chuyển sang metadata batch. |

Khuyến nghị: file này nên giữ, nhưng khi gửi cho HNMU có thể tạo bản teacher-facing đơn giản hơn, chỉ gồm `grade`, `lesson`, câu hỏi/hội thoại tóm tắt, `review_reason`, `suggested_question_to_hnmu`.

## 5. Nhận xét về các cột có thể rút gọn

Nếu muốn output gọn hơn ở lần chạy rộng, có thể cân nhắc:

1. Chuyển `checked_by`, `checked_at` khỏi từng CSV sang một file metadata cấp batch, ví dụ `audit_run_metadata.yaml`.
2. Không đưa `question`, `bloom_level`, `position` vào file chọn mẫu nếu đã có `normalized_dialogue_rows.csv` làm nguồn tra cứu.
3. Giữ nguyên các cột `evidence_*`, `reason`, `suggested_reviewer_action` trong checklist chi tiết, vì đây là phần giúp output có thể audit được.
4. Với file gửi HNMU, tạo bản rút gọn riêng thay vì làm nghèo output kỹ thuật.

## 6. Đề xuất cấu trúc lâu dài

- Output kỹ thuật đầy đủ cho UET/agent:
  - `raw_dialogue_checklist_results.csv`
  - `quality_check_results.csv`
  - `hnmu_review_queue.csv`
- Output rút gọn cho HNMU:
  - `hnmu_review_queue_teacher_view.xlsx` hoặc `.csv`
  - chỉ giữ các cột dễ đọc và câu hỏi cần thầy cô trả lời.
