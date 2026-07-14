# Giao thức rà soát — đánh giá chất lượng của bộ đánh giá từ 4 bài báo lõi

Thử nghiệm: `20260709_155523`
Kế hoạch: `01-benchmark-quality-literature-review.md`
Ngày thực hiện: 12/07/2026
Chế độ thực hiện: một luồng trong luồng cha; không gọi thêm luồng agent chuyên trách.

## 1. Câu hỏi nghiên cứu

Câu hỏi chính:

> Các bài báo lõi đánh giá chất lượng của chính bộ đánh giá như thế nào, và những tiêu chí nào có thể chuyển hóa sang bộ đánh giá gia sư Tin học THCS Việt Nam?

Câu hỏi phụ:

1. Bộ đánh giá được tạo từ nguồn dữ liệu nào?
2. Bài báo kiểm tra độ phủ của bộ đánh giá bằng cách nào?
3. Bài báo kiểm tra độ chính xác hoặc chất lượng dữ liệu bằng cách nào?
4. Bài báo kiểm tra độ khó, độ đa dạng hoặc phân tầng nhiệm vụ như thế nào?
5. Bài báo có kiểm tra độ tin cậy giữa người chấm không?
6. Bài báo có chứng minh bộ đánh giá phân biệt được mô hình/gia sư mạnh/yếu không?
7. Có sử dụng phản hồi tham chiếu hoặc phản hồi gia sư mẫu không, và dùng để làm gì?
8. Những tiêu chí nào có thể chuyển hóa sang bộ đánh giá gia sư Tin học THCS?
9. Những tiêu chí nào không phù hợp hoặc cần HNMU xác nhận?

## 2. Phạm vi

Trong phạm vi:

- 3 bài báo về gia sư đã đọc sâu ở thử nghiệm `20260705_215045`;
- 1 bài báo VietLegal/V-Legal được Quân nhắc để học cách phân tầng độ khó và kiểm soát chất lượng của bộ đánh giá;
- chỉ tập trung vào cách đánh giá hoặc chứng minh chất lượng của bộ đánh giá.

Ngoài phạm vi:

- không mở rộng thành rà soát hệ thống sang bài báo mới;
- không chốt nhiệm vụ hoặc tiêu chí chấm chính thức;
- không đánh giá dữ liệu HNMU vì chưa có đợt dữ liệu thật trong kho mã cục bộ;
- không triển khai mã nguồn.

## 3. Nguồn và đường dẫn

Nguồn cục bộ:

- `document/paper/source_paper/2502.18940v2.pdf`
- `document/paper/source_paper/18426-AAAI26.ShiW-NLP.pdf`
- `document/paper/source_paper/2510.02663v1.pdf`
- `document/paper/source_paper/2512.14554v5.pdf`
- `experiments/20260705_215045/literature_notes/paper_summaries/`

Nguồn trực tuyến chỉ dùng để xác nhận đường dẫn ổn định cho các bản arXiv:

- `https://arxiv.org/abs/2502.18940`
- `https://arxiv.org/abs/2603.02775`
- `https://arxiv.org/abs/2510.02663`
- `https://arxiv.org/abs/2512.14554`

## 4. Quy tắc đưa vào/loại ra

Đưa vào:

- bài báo trực tiếp xây bộ đánh giá gia sư hoặc bộ đánh giá có quy trình kiểm soát chất lượng dữ liệu rõ;
- bài báo có thông tin về độ phủ, chuyên gia xác thực, độ tin cậy, phản hồi tham chiếu hoặc khả năng phân biệt năng lực mô hình.

Loại ra:

- bài báo chỉ nói về mô hình hoặc huấn luyện mà không có bằng chứng về chất lượng của bộ đánh giá;
- tài liệu học liệu SGK/HNMU vì thuộc kế hoạch khác.

## 5. Quy tắc dừng

Dừng ở 4 bài báo bắt buộc của kế hoạch. Không mở rộng theo trích dẫn trong lượt này để giữ phạm vi gọn và đúng ưu tiên hiện tại.

## 6. Nhãn tổng hợp

- `bằng chứng`: được nguồn trực tiếp hỗ trợ.
- `suy luận`: rút ra từ nguồn nhưng đã chuyển miền sang Tin học THCS/HNMU.
- `câu hỏi mở`: cần Quân, giáo sư hoặc HNMU xác nhận.
