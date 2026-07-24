# Giao thức đọc lại 4 paper trước Plan 03

Ngày rà soát: 24/07/2026  
Experiment: `20260722_000940`  
Chế độ: `research-methodologist`, một tác tử  
Loại tổng hợp: đối chiếu cách vận hành

## 1. Câu hỏi rà soát

Câu hỏi chính:

> Bốn bài báo định nghĩa nhiệm vụ, tiêu chí chấm, phản hồi tham chiếu/chuẩn và phép tính điểm ở cấp một mẫu như thế nào; những cấu trúc nào phù hợp với tập 2.028 mẫu ứng viên Tin học THCS lớp 6–9?

Câu hỏi phụ:

1. Bài báo dùng từ “nhiệm vụ” cho mô-đun, tình huống sử dụng, hành vi gia sư hay hợp đồng đầu vào–đầu ra nào?
2. Một mẫu được gắn bao nhiêu nhiệm vụ, nguyên tắc sư phạm và tiêu chí chấm?
3. Tiêu chí chấm là bộ chung, bộ chọn theo nhiệm vụ/nguyên tắc, hay được viết riêng cho từng mẫu?
4. Phản hồi tham chiếu, phản hồi gia sư mẫu hoặc nhãn chuẩn đi vào phép chấm trực tiếp hay chỉ hỗ trợ viết tiêu chí?
5. Bộ chấm tạo phán quyết gì ở cấp tiêu chí và bài báo tổng hợp các phán quyết đó thành điểm như thế nào?
6. Mức Bloom/mức nhận thức là nhiệm vụ, siêu dữ liệu phân tích hay tầng tổ chức taxonomy?
7. Thiết kế nào chuyển được sang dữ liệu HNMU mà không coi `gold_response` là đáp án câu chữ duy nhất?

## 2. Phạm vi

Chỉ gồm bốn bài báo đã được hai experiment trước sử dụng:

1. MathTutorBench.
2. KMP-Bench.
3. TutorBench.
4. VietLegal/VLegal-Bench.

Không mở rộng sang bài báo thứ năm. Việc lần theo trích dẫn chỉ dùng để hiểu thuật ngữ được bốn bài báo nhắc tới, không thêm bản ghi nghiên cứu vào bản tổng hợp.

## 3. Nguồn

Nguồn toàn văn cục bộ:

- `document/paper/source_paper/2502.18940v2.pdf`
- `document/paper/source_paper/18426-AAAI26.ShiW-NLP.pdf`
- `document/paper/source_paper/2510.02663v1.pdf`
- `document/paper/source_paper/2512.14554v5.pdf`

Nguồn chính thức trực tuyến:

- `https://arxiv.org/html/2502.18940v2`
- `https://arxiv.org/html/2603.02775v1`
- `https://doi.org/10.1609/aaai.v40i39.40578`
- `https://arxiv.org/html/2510.02663v1`
- `https://huggingface.co/datasets/tutorbench/tutorbench`
- `https://arxiv.org/html/2512.14554v5`

Nguồn kế thừa dùng để đối chiếu, không được coi là thay thế toàn văn:

- `experiments/20260705_215045/literature_notes/paper_summaries/`
- `experiments/20260709_155523/literature_benchmark_quality/`
- `experiments/20260709_155523/reports/three-paper-benchmark-use-synthesis.md`
- `experiments/20260709_155523/reports/meeting-notes-structured-20260708.md`

## 4. Quy tắc đưa vào và loại ra

Đưa vào một phát biểu khi có vị trí nguồn cụ thể về ít nhất một thành phần:

- nhiệm vụ/mô-đun/tình huống sử dụng;
- cấu trúc mẫu;
- rubric/tiêu chí chấm;
- phản hồi tham chiếu/chuẩn;
- đầu ra của bộ chấm;
- thước đo/cách tổng hợp;
- kiểm định bộ chấm/người chấm.

Loại khỏi kết luận vận hành:

- nhận định chỉ có trong tóm tắt cũ nhưng không tìm lại được trong paper;
- tên tiêu chí không được bài báo công bố đầy đủ;
- suy luận chuyển miền bị trình bày như kết luận của paper;
- kết quả học tập, vì bốn bài báo không cùng đo kết quả học tập của học sinh.

## 5. Quy tắc trích xuất

Mỗi bài báo được trích xuất theo cùng sáu tầng:

1. `benchmark_scope`: phạm vi/mô-đun đang đo gì;
2. `task_contract`: đầu vào, đầu ra và năng lực đích;
3. `instance_structure`: một mẫu chứa những thành phần nào;
4. `rubric_scope`: tiêu chí chung, tiêu chí được chọn theo nhiệm vụ/nguyên tắc hay tiêu chí riêng theo mẫu;
5. `reference_role`: nhãn chuẩn chính xác, đối chứng so sánh theo cặp, căn cứ biên soạn tiêu chí hay mức chuẩn của con người;
6. `judgment_and_aggregation`: phán quyết cấp tiêu chí và điểm cấp mẫu/nhiệm vụ/mô hình.

Mỗi claim dùng một trong ba nhãn:

- `evidence` — bằng chứng: bài báo hỗ trợ trực tiếp;
- `inference` — suy luận: hàm ý thiết kế cho bộ đánh giá Tin học THCS;
- `open_question` — câu hỏi mở: bài báo không đủ thông tin hoặc cần HNMU/UET quyết định.

## 6. Kiểm soát chất lượng

- Đối chiếu nội dung chính với phụ lục và bảng/hình liên quan.
- Đối chiếu PDF local với arXiv HTML chính thức khi bản PDF hội nghị lược appendix.
- Không tự điền tên của toàn bộ 22 criteria KMP-Bench khi paper chỉ công bố ví dụ minh họa.
- Ghi rõ sự khác nhau giữa độ tin cậy của dữ liệu, độ đồng thuận giữa người chấm và độ khớp giữa bộ chấm tự động với con người.
- Giữ quyền quyết định chuyên môn/sư phạm cuối cùng cho HNMU/UET.

## 7. Quy tắc dừng

Dừng khi cả bốn paper đã có:

- sơ đồ vận hành từ mẫu đến điểm;
- vị trí nguồn cho nhiệm vụ/tiêu chí/phản hồi tham chiếu/cách tổng hợp;
- ít nhất một hạn chế chuyển giao;
- đối chiếu trực tiếp với schema và Plan 03 hiện tại.
