# Plan 04 — Bộ tiêu chí chung và riêng theo nguyên tắc

Experiment: `20260727_170150`
Trạng thái: `IMPLEMENTED — AWAITING UET/HNMU REVIEW`
Phụ thuộc: Plan 03 đã hoàn tất phân tích; UET ưu tiên pool 1.400
`eligible_without_plan03_review` và hoãn review 628 mẫu bị cờ

## 1. Mục tiêu

Xây một bộ tiêu chí hai tầng để chấm **phản hồi tiếp theo của gia sư AI**:

1. tiêu chí chung, áp dụng cho mọi mẫu;
2. tiêu chí riêng của các nguyên tắc có `requirement_score >= 4`.

Sáu năng lực gia sư là bản đồ nội dung cần đo. Sáu nguyên tắc KMP xác
định tiêu chí riêng nào được kích hoạt. Không tạo tầng tiêu chí riêng cho
từng candidate.

Plan dùng 1.400 candidate không cần review riêng tại Plan 03 làm pool ưu
tiên để chọn ví dụ, kiểm ranh giới và chuẩn bị thí điểm. 628 candidate
trong backlog UET không được dùng làm ví dụ chuẩn ở giai đoạn này. Bộ
tiêu chí vẫn phải bao phủ đủ sáu nguyên tắc và sáu năng lực; không được
loại `Challenge` hoặc `Practice` chỉ vì chúng hiếm trong pool ưu tiên.

## 2. Quyết định thiết kế cần giữ

- Khởi đầu từ cấu trúc KMP-Bench: một lõi chung nhỏ và ba tiêu chí cho mỗi
  nguyên tắc; cấu trúc `4 + 3 × n` chỉ được giữ nếu thí điểm cho thấy đủ
  bao phủ và không chồng chéo.
- Không ép sáu năng lực thành sáu tiêu chí chung một-một. Mỗi năng lực phải
  được truy vết tới ít nhất một tiêu chí ở một trong hai tầng.
- Mỗi tiêu chí phải nguyên tử, quan sát được trong đúng một phản hồi và có
  ranh giới đạt/không đạt rõ.
- `gold_response` là phản hồi tham chiếu để so sánh, không phải cách trả
  lời duy nhất và không được dùng để chọn tiêu chí.
- Lỗi nghiêm trọng được xử lý bằng cổng riêng; không để điểm trung bình che
  lấp lỗi sai chuyên môn, làm thay học sinh hoặc nội dung có hại.
- Rubric chỉ đạt trạng thái tạm dùng sau UET review; HNMU quyết định cuối
  về tính phù hợp sư phạm và ví dụ môn Tin học THCS.
- Trạng thái `eligible_without_plan03_review` chỉ là điều kiện chọn pool
  ưu tiên, không phải nhãn chuyên gia hay bảo đảm chất lượng
  `gold_response`.
- Tiêu chí chung đo điều kiện nền của toàn bộ response; tiêu chí riêng chỉ
  đo giá trị tăng thêm của nguyên tắc đang được kích hoạt.
- Lỗi nghiêm trọng là một cổng quyết định, không phải rubric và không được
  cộng như một tiêu chí độc lập. `suggested_action` của từng error là
  nguồn duy nhất quyết định rubric nào bị ép phán quyết hoặc giới hạn nào
  được áp dụng ở tầng tổng thể.
- `affected_rubric_ids` phục vụ truy vết và giải thích phạm vi ảnh hưởng;
  bản thân danh sách này không tự tạo thêm các lần phạt.

## 3. Các bước thực hiện

### Bước 1 — Khóa căn cứ

Đọc mô hình sáu năng lực, sáu nguyên tắc, kết quả Plan 03, danh sách
1.400 candidate ưu tiên, phương pháp HNMU và các claim có truy vết của
KMP-Bench. Phân biệt rõ `evidence`, `inference` và
`teacher_decision_needed`.

### Bước 2 — Lập ma trận năng lực–nguyên tắc–tiêu chí

Với từng năng lực, xác định:

- phần nào phải được kiểm ở mọi mẫu;
- phần nào chỉ quan sát được khi một nguyên tắc cụ thể được kích hoạt;
- phần nào không thể suy ra từ một lượt phản hồi.

Ma trận này là phép kiểm độ phủ, không phải phép đồng nhất năng lực với
nguyên tắc.

### Bước 3 — Soạn lõi tiêu chí chung

Soạn tối đa bốn tiêu chí chung. Mỗi tiêu chí có: định nghĩa, bằng chứng
quan sát, ranh giới, ví dụ đạt và ví dụ gần đạt nhưng chưa đủ.

### Bước 4 — Soạn tiêu chí riêng

Soạn ba tiêu chí cho mỗi nguyên tắc `Challenge`, `Explanation`,
`Modelling`, `Practice`, `Feedback`, `Questioning`. Loại hoặc hợp nhất
tiêu chí nếu nó chỉ lặp lại lõi chung.

### Bước 5 — Soạn cổng lỗi nghiêm trọng

Chỉ giữ các lỗi có thể làm phản hồi không còn chấp nhận được hoặc cần giới
hạn điểm. Mỗi lỗi nêu tiêu chí bị ảnh hưởng và hành động đề xuất; hành
động cuối cần HNMU xác nhận.

### Bước 6 — Chuẩn bị, không chạy thí điểm khả năng phân biệt

Chọn một tập nhỏ phản hồi tốt, trung bình và kém đã có hoặc biến đổi lỗi
có kiểm soát. Chuẩn bị phép kiểm xem từng tiêu chí:

- có phân biệt được ba mức chất lượng hay không;
- có bị hai người đọc hiểu khác nhau hay không;
- có chấm trùng với tiêu chí khác hay không.

Plan 04 chỉ kiểm bàn giấy bằng anchor và bàn giao thiết kế thí điểm. Việc
gọi nhiều LLM, chạy judge, tính mức trùng phán quyết và quyết định
gộp/tách rubric được hoãn sang Plan 07 để ưu tiên tiến độ paper.

### Bước 7 — UET rồi HNMU review

UET review cấu trúc, truy vết và ranh giới. Sau đó HNMU nhận một gói tích
hợp gồm rubric, ví dụ và các câu hỏi cần quyết định; không review từng
thành phần rời rạc.

## 4. Output tối thiểu

Tất cả đặt tại
`experiments/20260727_170150/outputs/benchmark_rubric/`:


| File                      | Nội dung                                                                    |
| ------------------------- | ---------------------------------------------------------------------------- |
| `benchmark_tasks.csv`     | Một nhiệm vụ chung: sinh phản hồi tiếp theo của gia sư               |
| `rubrics.csv`             | Toàn bộ tiêu chí chung và riêng, trạng thái và dấu hiệu quan sát |
| `serious_errors.csv`      | Danh mục lỗi nghiêm trọng và hành động đề xuất                    |
| `provenance_matrix.csv`   | Năng lực, nguyên tắc, nguồn nghiên cứu/học liệu hỗ trợ từng mục |
| `rubric_review_packet.md` | Luận giải ngắn, ví dụ biên và câu hỏi cho UET/HNMU                  |

## 5. Cổng hoàn thành

- Mọi tiêu chí có căn cứ hoặc được đánh dấu rõ là suy luận cần review.
- Sáu năng lực đều được bao phủ, nhưng không có tiêu chí trùng chức năng.
- Mỗi nguyên tắc có tiêu chí đủ riêng để tạo khác biệt khi chấm.
- Kiểm tra ban đầu trên response sẵn có không phát hiện tiêu chí hoàn toàn
  không phân biệt; bằng chứng thực nghiệm đầy đủ được bổ sung ở Plan 07.
- UET phê duyệt tạm thời và HNMU xác nhận nội dung sư phạm trước khi freeze.

Plan này không gọi API, không chấm 2.028 candidate và không sửa score của
Plan 02–03.

## 6. Kết quả triển khai

Đã tạo và validate:

- 1 nhiệm vụ chung;
- 4 tiêu chí chung;
- 18 tiêu chí riêng, đúng 3 tiêu chí cho mỗi nguyên tắc;
- 6 mã lỗi nghiêm trọng;
- 29 dòng provenance bao phủ toàn bộ task, rubric và serious error;
- đủ 6/6 năng lực và 6/6 nguyên tắc;
- 6 ca biên lấy context thật từ pool 1.400 để UET/HNMU review.

Desk check cho thấy các tiêu chí có thể tách phản hồi đạt, gần đạt và kém
ở sáu nguyên tắc, nhưng đây chưa phải kiểm định thực nghiệm. Một số
`gold_response` chỉ khen hoặc hỏi ngắn, vì vậy Plan 05 phải cho phép
response mô hình thắng reference theo từng tiêu chí.

UET đã khóa thêm quy tắc chống tính trùng:

- rubric chung chỉ đo điều kiện nền;
- rubric riêng chỉ đo giá trị tăng thêm của nguyên tắc;
- serious error dùng đúng một `suggested_action` ở tầng tổng thể, không
  được cộng như rubric hoặc tự nhân số lần phạt theo
  `affected_rubric_ids`;
- pilot chồng lấn và khả năng phân biệt được hoãn sang Plan 07.

Validator chính thức và kiểm tra bổ sung đều đạt. Plan ở trạng thái chờ
UET review cấu trúc/ranh giới và HNMU xác nhận nội dung sư phạm; chưa
được freeze.
