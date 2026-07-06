# Ghi chú có cấu trúc — họp ngày 05/07/2026

Ngày họp: 05/07/2026  
Experiment: `20260705_215045`  
Nguồn: `user_diary.md`, mục `Update plan (05-07-2026)`  
Ưu tiên đọc: phần trao đổi riêng giữa Quân và giáo sư.

## 1. Tóm tắt rất ngắn

Buổi họp ngày 05/07/2026 tạo ra một điểm xoay quan trọng: thay vì tiếp tục coi bản task/rubric v0 ngày 04/07 là hướng chính, giai đoạn mới cần ưu tiên thiết kế benchmark theo **độ khó nhận thức**, dựa trên thang Bloom/bốn mức của chương trình phổ thông: `Nhận biết`, `Thông hiểu`, `Vận dụng`, `Vận dụng cao`.

Các trường trong sheet `phiếu tác giả` tạm coi như đã chốt để HNMU có thể bắt đầu tạo khoảng 20 mẫu đầu tiên. Việc của UET là tạo ví dụ minh họa đủ rõ, rồi dựa trên mẫu thật để thử chia task, rubric và case bao phủ.

## 2. Nội dung họp chung với giáo sư và HNMU

### 2.1. Việc đọc bài báo cho tuần sau

Cần đọc kỹ hai bài:

- `document/paper/source_paper/2502.18940v2.pdf` — MathTutorBench.
- `document/paper/source_paper/2512.14554v5.pdf` — VietLegal.

Mục tiêu đọc không phải chỉ tóm tắt paper, mà là soi cách họ chia benchmark:

| Paper | Hướng cần soi | Ý nghĩa với dự án |
|---|---|---|
| MathTutorBench | Chia task theo khía cạnh/phẩm chất của gia sư | Hữu ích để thiết kế rubric và các hành vi gia sư cần chấm. |
| VietLegal | Chia theo độ khó dựa trên Bloom | Hữu ích cho hướng mới: task/dữ liệu phân tầng theo mức nhận thức. |

### 2.2. HNMU review phiếu tác giả

HNMU được đề nghị xem kỹ sheet `Luận giải chi tiết trường dữ liệu` trong `review_form.xlsx`, vì sheet này giải thích các trường của sheet `phiếu tác giả` đã thống nhất trong buổi họp ngày 01/07/2026.

Điểm cần chờ từ HNMU:

- trường nào khó hiểu;
- trường nào chưa phù hợp với quy trình giáo viên tạo dữ liệu;
- trường nào cần ví dụ hoặc ràng buộc rõ hơn;
- trường nào có nguy cơ làm giáo viên hiểu khác nhau.

### 2.3. HNMU tạo khoảng 20 mẫu đầu tiên

Với các trường đã chốt trong phiếu tác giả, HNMU sẽ thử xây khoảng 20 mẫu. Sau đó UET tổng hợp và thử chia task.

Cách làm này thiên về bottom-up: có mẫu thật trước, rồi dùng mẫu thật để kiểm tra lại task/rubric. Điều này hợp với tinh thần “cứ làm đi, cần thêm gì thì bổ sung sau”, nhưng cần ghi rõ các mẫu đầu tiên là mẫu pilot, chưa phải dữ liệu benchmark chính thức.

## 3. Nội dung trao đổi riêng với giáo sư — phần ưu tiên

### 3.1. Phiếu tác giả được coi như đã chốt để chạy

Giáo sư định hướng: coi các trường trong sheet `phiếu tác giả` của `review_form.xlsx` là đã chốt ở giai đoạn này. Không nên tiếp tục dừng lại để sửa metadata mãi.

Hàm ý triển khai:

- UET cần tạo ví dụ cụ thể theo đúng phiếu này để giáo viên hiểu cách điền.
- Các điểm chưa hoàn hảo có thể ghi vào `Ghi chú` hoặc câu hỏi mở, thay vì chặn tiến độ.
- Nếu sau 20 mẫu pilot thấy trường nào thật sự gây lỗi hệ thống, lúc đó mới sửa có căn cứ.

### 3.2. Task ưu tiên chia theo độ khó/Bloom

Giáo sư muốn ưu tiên phân chia task theo độ khó, dựa trên thang Bloom hoặc cách diễn giải bốn mức trong chương trình phổ thông:

1. Nhận biết.
2. Thông hiểu.
3. Vận dụng.
4. Vận dụng cao.

Đây là thay đổi đáng kể so với artifact ngày 04/07, vốn chia task theo các hành vi/phẩm chất của gia sư như giải thích, phản hồi lập luận, gợi ý thuật toán, chẩn đoán lỗi.

Cách hiểu tạm thời:

- `Bloom/difficulty` nên là trục chính để chia task hoặc ít nhất là trường bắt buộc trong task.
- Các task kiểu T01–T07 từ experiment `20260701_100006` không nên vứt bỏ; chúng có thể được hạ xuống thành nhãn hành vi gia sư hoặc case tương tác trong mỗi mức Bloom.
- Cần tránh hiểu “độ khó” chỉ là bài khó/dễ. Ở đây độ khó là mức yêu cầu nhận thức: nhớ/nhận ra, giải thích, áp dụng, giải quyết tình huống mới/phức hợp.

### 3.3. Rubric nên giảm còn khoảng 3–4 tiêu chí

Bản ngày 04/07 có 9 tiêu chí D1–D9. Giáo sư muốn ưu tiên khoảng 3–4 rubric, miễn là có căn cứ khoa học rõ ràng.

Định hướng tạm thời:

1. Đúng chuyên môn và bám học liệu/chương trình.
2. Phù hợp mức nhận thức, chủ đề và tiền kiến thức của học sinh.
3. Chất lượng sư phạm của phản hồi gia sư: gợi mở, giàn giáo, không làm thay quá sớm, có bước tiếp theo rõ.
4. An toàn, công bằng, không bịa nguồn/quy định, không định kiến.

Rubric thứ 4 có thể là rubric riêng hoặc policy lỗi nghiêm trọng, cần cân nhắc sau khi đọc paper và xem 20 mẫu pilot.

### 3.4. Task/rubric phải có bằng chứng khoa học

Giáo sư nhấn mạnh: có thể khảo sát ít paper, nhưng paper tham khảo phải chất lượng và liên quan cao đến benchmark gia sư.

Nguồn ưu tiên hiện có trong repo:

- `document/paper/source_paper/2502.18940v2.pdf` — MathTutorBench.
- `document/paper/source_paper/2512.14554v5.pdf` — VietLegal.
- Có thể dùng thêm `document/paper/source_paper/2510.02663v1.pdf` — TutorBench, nếu cần căn cứ về subject-expert authoring, task/rubric theo phản hồi gia sư.

Cần tách rõ:

- căn cứ nghiên cứu trực tiếp;
- suy luận từ paper sang Tin học 9;
- quyết định cần HNMU/giáo sư xác nhận.

### 3.5. Tiêu chí của một benchmark tốt trong giai đoạn này

Giáo sư nêu ba tiêu chí chính:

| Tiêu chí | Cách hiểu | Rủi ro nếu không định nghĩa kỹ |
|---|---|---|
| Độ phủ kiến thức | Tỷ lệ chủ đề trong SGK/SGV Tin học THCS được bao phủ; ưu tiên lớp 9 và tiền kiến thức lớp 6–8 liên quan. Học liệu chủ đạo là SGK và SGV trên trang tập huấn: https://taphuan.nxbgd.vn/tap-huan?subjects=11. | Rủi ro lớn là tên chủ đề xuyên suốt SGK lớp 6–9 chưa đồng nhất; nếu chưa chuẩn hóa taxonomy chủ đề thì coverage dễ bị đếm sai hoặc bỏ sót. |
| Độ phân hóa | Phân bổ câu hỏi theo `Nhận biết`, `Thông hiểu`, `Vận dụng`, `Vận dụng cao`. | Dễ nhầm Bloom với độ dài/cảm giác khó của câu hỏi. |
| Độ đa dạng định dạng | Cân bằng giữa trắc nghiệm, tự luận lý thuyết, sửa lỗi code Scratch/Python, viết chương trình. | Dễ lệch về một format dễ tạo, làm benchmark kém đại diện. |

Từ ba tiêu chí này, cần xây dựng **bảng bao phủ tình huống** cho mỗi task/mức Bloom: chủ đề nào, mức nhận thức nào, định dạng nào, kiểu tương tác gia sư nào, và cần ví dụ minh họa ra sao.

## 4. Quan hệ với experiment `20260701_100006`

Experiment `20260701_100006` vẫn hữu ích nhưng nên coi là input lịch sử/khởi động, không phải thiết kế cuối.

Các artifact nên tái sử dụng:

- `author_form/author_form_field_review.md`: giúp hiểu các trường phiếu tác giả.
- `benchmark_spec/task_code_registry.csv`: danh sách task T01–T07 theo hành vi gia sư; nên dùng như nhãn phụ hoặc case tương tác.
- `benchmark_spec/rubric_dimensions.csv`: D1–D9 là nguồn để rút gọn về 3–4 rubric.
- `benchmark_spec/rubric_error_mapping.csv`: hữu ích để giữ policy lỗi nghiêm trọng không bị hiểu thành “0 toàn bộ task”.
- `learning_resources/topic_map_grade6_9.md`: nhắc rằng lớp 6–8 hiện vẫn là placeholder, chưa đủ chắc.
- `drive_snapshot/files/teacher_packet/review_form.xlsx`: bản input của phiếu tác giả.

Các điểm cần điều chỉnh:

1. Task T01–T07 hiện chia theo phẩm chất/hành vi gia sư; hướng mới cần thêm hoặc chuyển sang trục Bloom.
2. Rubric D1–D9 quá nhiều so với định hướng mới; cần gom về 3–4 tiêu chí.
3. Topic map lớp 6–8 chưa đủ để tuyên bố coverage toàn THCS; trước mắt nên ưu tiên lớp 9.
4. Cần tạo ví dụ minh họa theo phiếu tác giả thay vì chỉ có đặc tả CSV/Markdown.

## 5. Các mâu thuẫn/rủi ro cần quản trị

### 5.1. Bottom-up nhanh nhưng vẫn cần khung tối thiểu

HNMU tạo 20 mẫu trước là hợp lý để chạy nhanh. Nhưng nếu chưa có khung tối thiểu về Bloom/topic/format, 20 mẫu có thể lệch nhiều và khó tổng hợp.

Đề xuất: trước khi HNMU làm nhiều, UET nên đưa một bảng chọn đơn giản gồm:

- chủ đề;
- mức Bloom;
- định dạng câu hỏi;
- kiểu hỗ trợ gia sư;
- mã học liệu;
- ghi chú case đặc biệt.

### 5.2. “Phiếu tác giả đã chốt” không có nghĩa schema đã hoàn hảo

Nên hiểu là chốt để chạy pilot, không phải đóng băng vĩnh viễn. Nếu 20 mẫu cho thấy lỗi lặp lại, có thể mở version mới của phiếu.

### 5.3. Coverage toàn THCS phụ thuộc vào chuẩn hóa chủ đề SGK/SGV

Tiêu chí coverage nói tới SGK/SGV Tin học THCS 6–9, nhưng tên và cách chia chủ đề giữa các lớp có thể không đồng nhất. Vì vậy rủi ro coverage nên được kiểm soát bằng một taxonomy chủ đề xuyên suốt trước: mỗi bài/mục trong SGK/SGV được map về một chủ đề chuẩn, còn tên gốc trong sách vẫn được giữ để truy vết.

Trong sprint gấp, ưu tiên vẫn là lớp 9 và tiền kiến thức lớp 6–8 liên quan. Không nên tuyên bố phủ đều toàn bộ lớp 6–8 trước khi SGK/SGV đã được snapshot, bóc tách mục lục và map chủ đề đủ chắc.

### 5.4. Format Diversity cần định nghĩa format trước khi đếm

Các format được nhắc gồm:

- trắc nghiệm;
- tự luận lý thuyết;
- sửa lỗi code Scratch/Python;
- viết chương trình.

Cần xác định rõ mỗi format được ghi trong phiếu tác giả ở trường nào, và format nào phù hợp với từng mức Bloom.

### 5.5. Rubric ít hơn không có nghĩa đơn giản hóa quá mức

Giảm còn 3–4 rubric giúp giáo viên chấm dễ hơn. Nhưng cần giữ khả năng phát hiện lỗi nghiêm trọng bằng catalog/policy riêng, nếu không rubric ít quá sẽ bỏ sót an toàn, bịa nguồn, định kiến, vượt phạm vi.

## 6. Hướng làm ngay được đề xuất

1. Đọc sâu `2502.18940v2.pdf` và `2512.14554v5.pdf`, tập trung vào cách chia task, thang Bloom, rubric và cách chứng minh độ bao phủ.
2. Lập bản thiết kế task mới theo Bloom, có thể dùng mã tạm `B1`–`B4` hoặc `BLM-01`–`BLM-04`.
3. Rút gọn D1–D9 thành 3–4 rubric dựa trên bằng chứng paper.
4. Tạo bảng bao phủ tình huống: `topic × Bloom level × format × tutor-support case`.
5. Viết 3–5 ví dụ mẫu theo phiếu tác giả để HNMU nhìn được cách điền, trước khi yêu cầu tạo 20 mẫu.
6. Sau khi nhận 20 mẫu, dùng mẫu thật để kiểm tra lại taxonomy và rubric.

## 7. Kết luận vận hành

Tinh thần giai đoạn mới là: chạy nhanh nhưng có log, có version, có bằng chứng. Không chờ một thiết kế hoàn hảo mới bắt đầu; nhưng cũng không để các mẫu pilot trôi tự do mà thiếu các trục tối thiểu: chủ đề, Bloom, format, học liệu và vai trò gia sư.
