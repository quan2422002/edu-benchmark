# Tổng hợp ba nghiên cứu cho cách sử dụng benchmark

Ngày tạo: 09/07/2026  
Phạm vi: ba nghiên cứu đã được đọc kỹ trong P03 của experiment `20260705_215045`.

## 1. Câu hỏi cần trả lời

1. Mô hình được yêu cầu sinh gì?
2. Hội thoại mẫu và phản hồi gia sư do con người viết được dùng như thế nào?
3. Phản hồi mô hình được chấm bằng cách nào?
4. Điều gì có thể chuyển sang benchmark gia sư Tin học THCS?

## 2. So sánh ba nghiên cứu

| Thành phần | MathTutorBench | KMP-Bench | TutorBench |
|---|---|---|---|
| Đơn vị sinh chính có liên quan | Lượt gia sư tiếp theo trong hội thoại. | Lượt gia sư tại vị trí hội thoại bị cắt. | Phản hồi cuối trong hội thoại/bối cảnh đã định sẵn. |
| Đầu vào | Bài toán và lịch sử hội thoại; biến thể khó có lịch sử dài hơn. | Lịch sử tới lượt học sinh ngay trước lượt gia sư bị cắt, kèm chỉ dẫn theo ngữ cảnh. | Câu hỏi, bài làm/bối cảnh và lịch sử được viết sẵn theo từng trường hợp sử dụng. |
| Phản hồi của con người | Phản hồi giáo viên làm đối chứng. | Lượt gia sư gốc bị cắt làm `reference response`. | Chuyên gia viết `golden tutoring response` làm căn cứ xây rubric. |
| Cách chấm | Mô hình chấm chuyên biệt xếp hạng phản hồi mô hình với phản hồi giáo viên; báo cáo tỷ lệ thắng. | Mô hình giám khảo so sánh phản hồi mô hình và tham chiếu theo tiêu chí; Thắng/Hòa/Thua. | Mô hình giám khảo chấm Đạt/Không đạt trên rubric riêng cho từng mẫu, có trọng số. |
| Kiểm tra mô hình chấm | Kiểm tra khả năng ưu tiên phản hồi chuyên gia hơn phản hồi giáo viên mới vào nghề. | So sánh với nhãn chuyên gia trên 300 trường hợp; báo cáo mức phù hợp trung bình 89,8%. | Ba chuyên gia chấm trên 250 mẫu; so sánh mô hình giám khảo với ý kiến đa số. |
| Giới hạn chính | Không đo trực tiếp kết quả học tập và chưa bao phủ đầy đủ an toàn. | Toán K–8, nhiều dữ liệu được sinh rồi kiểm tra. | Chỉ chấm phản hồi cuối, không đo thích ứng động trong hội thoại tự do. |

## 3. Kết luận có bằng chứng trực tiếp

### 3.1. Có thể đánh giá một lượt gia sư trong lịch sử đã định sẵn

Cả ba nghiên cứu đều có thiết kế đánh giá phản hồi tại một thời điểm cụ thể thay vì bắt buộc mô hình tự tạo toàn bộ hội thoại. Điều này hỗ trợ quy ước hiện tại:

```text
student_prompt + conversation_history → phản hồi mô hình
```

### 3.2. Phản hồi tham chiếu có giá trị nhưng không phải “đáp án văn bản”

KMP-Bench và MathTutorBench dùng phản hồi giáo viên làm đối chứng so sánh. TutorBench dùng phản hồi lý tưởng để xây rubric. Không nghiên cứu nào trong ba nghiên cứu này ủng hộ việc chỉ chấm bằng độ giống từ ngữ với phản hồi mẫu.

### 3.3. Rubric phải phụ thuộc vào task và bối cảnh

KMP-Bench có tiêu chí theo nguyên tắc sư phạm mục tiêu của lượt. TutorBench dùng tiêu chí riêng cho từng mẫu. Vì vậy, việc chấm một phản hồi có tiết lộ đáp án hay không phải phụ thuộc task: cùng một nội dung có thể phù hợp trong task giải thích/tổng kết nhưng không phù hợp trong task gợi mở.

### 3.4. Mô hình giám khảo phải được hiệu chỉnh với chuyên gia

KMP-Bench và TutorBench đều kiểm tra mô hình giám khảo với nhãn con người. Dự án không nên coi kết quả chấm tự động là đáng tin trước khi so sánh với đánh giá của HNMU trên một tập mẫu tiếng Việt đủ đại diện.

## 4. Thiết kế đề xuất cho dữ liệu HNMU

### 4.1. Một hội thoại có thể tạo nhiều mẫu

Flow đề xuất không ánh xạ đầy đủ vào phiếu tác giả ngay từ đầu. Trước hết, hệ thống tách cấu trúc tối thiểu:

- thông tin học liệu và thông tin phụ trợ;
- từng lượt hội thoại;
- số thứ tự, người nói và vị trí nguồn;
- đáp án và kỹ thuật giàn giáo do HNMU cung cấp.

Sau đó, với mỗi lượt gia sư có giá trị đánh giá, hệ thống tạo một **ứng viên mẫu**:

1. bối cảnh kết thúc ở lượt học sinh ngay trước lượt gia sư mục tiêu;
2. lượt gia sư mục tiêu được giữ nguyên như phản hồi tham chiếu tiềm năng;
3. agent đề xuất nhiệm vụ chính, luận giải, bằng chứng và độ tin cậy;
4. UET/HNMU duyệt nhiệm vụ và điểm cắt;
5. chỉ sau đó mới ánh xạ đầy đủ `student_prompt`, `conversation_history`, `gold_response` và các trường còn lại vào phiếu tác giả.

Ví dụ một hội thoại có ba lượt gia sư có thể tạo tối đa ba ứng viên mẫu. Không bắt buộc dùng tất cả; chỉ giữ lượt có giá trị đánh giá và đủ bối cảnh.

Điểm cần phân biệt:

```text
tách cấu trúc tối thiểu → giúp agent hiểu nguồn
ánh xạ đầy đủ phiếu tác giả → tạo mẫu benchmark sau khi nhiệm vụ được duyệt
```

### 4.2. Vai trò của `answer`

`answer` lưu kết quả/kiến thức đích của bài. `gold_response` lưu cách gia sư nên phản hồi ở thời điểm cụ thể.

```text
answer        = nội dung chuyên môn cần đạt
gold_response = hành động giao tiếp–sư phạm lý tưởng trong bối cảnh cụ thể
```

Một `gold_response` tốt có thể:

- hỏi gợi mở mà chưa nêu `answer`;
- chỉ ra lỗi nhưng chưa sửa toàn bộ;
- đưa hướng dẫn từng bước;
- nêu đáp án khi task và trạng thái hội thoại yêu cầu tổng kết.

### 4.3. Cách chấm nên kết hợp hai lớp

Lớp bắt buộc:

- chấm phản hồi mô hình theo R1–R5 hoặc phiên bản rubric được chốt;
- dùng `answer`, học liệu và lịch sử làm căn cứ;
- không yêu cầu giống câu chữ với `gold_response`.

Lớp thử nghiệm:

- so sánh cặp phản hồi mô hình với `gold_response` theo từng rubric;
- cho phép kết quả Tốt hơn/Tương đương/Kém hơn;
- kiểm tra kết quả tự động với chuyên gia HNMU.

## 5. Trạng thái bằng chứng

| Kết luận | Nhãn |
|---|---|
| Đánh giá một lượt gia sư trong lịch sử định sẵn | Bằng chứng trực tiếp từ cả ba nghiên cứu. |
| Dùng lượt gia sư HNMU làm phản hồi tham chiếu | Bằng chứng trực tiếp từ KMP-Bench; gần tương ứng với MathTutorBench và TutorBench. |
| Một hội thoại HNMU tạo nhiều mẫu benchmark | Suy luận thiết kế dựa trên cách KMP-Bench cắt hội thoại; cần kiểm tra trên dữ liệu thật. |
| Xác định nhiệm vụ trước khi hoàn thiện phiếu tác giả | Quyết định quy trình của dự án; giúp nhiệm vụ điều khiển chỉ dẫn, trường cần điền và tiêu chí chấm. |
| Thêm trường `answer` tách khỏi `gold_response` | Quyết định thiết kế của dự án, được hỗ trợ gián tiếp bởi phân biệt lời giải và phản hồi sư phạm trong các nghiên cứu. |
| Dùng specialist để đề xuất task | Quyết định kỹ thuật; chưa được ba nghiên cứu trực tiếp kiểm chứng. |

## 6. Nguồn đã đối chiếu

- `experiments/20260705_215045/literature_notes/paper_summaries/P03-P001-mathtutorbench.md`
- `experiments/20260705_215045/literature_notes/paper_summaries/P03-P002-kmp-bench.md`
- `experiments/20260705_215045/literature_notes/paper_summaries/P03-P003-tutorbench.md`
- `document/paper/source_paper/2502.18940v2.pdf`
- `document/paper/source_paper/18426-AAAI26.ShiW-NLP.pdf`
- `document/paper/source_paper/2510.02663v1.pdf`

Vị trí nguồn chính đã kiểm tra:

- MathTutorBench: Bảng 1; mục 4.1; mục 4.3; Bảng 4.
- KMP-Bench: mục *Evaluation Framework*; phần chuẩn bị mẫu bằng cách cắt hội thoại; Bảng 3.
- TutorBench: mục 2.3; mục 3.7; mục 5; Phụ lục A.1.
