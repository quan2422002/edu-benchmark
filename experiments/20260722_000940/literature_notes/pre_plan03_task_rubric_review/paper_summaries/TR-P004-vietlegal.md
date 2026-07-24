# TR-P004 — VietLegal/VLegal-Bench

Bài báo: `Benchmarking Vietnamese Legal Knowledge of Large Language Models`  
Tệp cục bộ: `document/paper/source_paper/2512.14554v5.pdf`  
Đường dẫn ổn định: `https://arxiv.org/abs/2512.14554`  
Trạng thái công bố: bản tiền công bố (`preprint`), phiên bản v5  
Miền nghiên cứu: kiến thức và suy luận pháp luật Việt Nam  
Vai trò trong experiment hiện tại: nguồn ngoài miền gia sư, dùng để làm rõ taxonomy nhiệm vụ, thước đo theo nhiệm vụ, mức nhận thức, truy vết nguồn, quy trình kiểm tra chéo và phân xử.

## 1. Mục tiêu đọc bài báo trong experiment này

Bản tóm tắt không dùng VietLegal để suy ra trực tiếp tiêu chí sư phạm. Nó trả lời:

1. Bài báo phân biệt nhiệm vụ và mức nhận thức như thế nào?
2. Một mẫu được gắn nhiệm vụ, đầu ra chuẩn và thước đo ra sao?
3. Có tiêu chí riêng ở cấp mẫu hay không?
4. Quy trình nguồn, người gán nhãn, kiểm tra chéo và phân xử có thể chuyển sang dự án thế nào?
5. Phần nào không nên chuyển vì đây không phải benchmark gia sư?

## 2. Vấn đề bài báo giải quyết

**Bằng chứng.** VietLegal xây dựng bộ đánh giá tiếng Việt về kiến thức, suy luận và trách nhiệm pháp lý, dựa trên nguồn pháp luật chính thức. Bài báo nhấn mạnh:

- độ phủ nhiều loại nhiệm vụ;
- phân tầng nhận thức;
- truy vết nguồn;
- quy trình chuyên gia nhiều tầng;
- thước đo phù hợp với từng dạng đầu ra.

Bộ dữ liệu cuối có 10.450 mẫu thuộc 22 nhiệm vụ.

Vị trí nguồn: `Abstract`; `Section 3`; `Figure 1`; `Table 1`.

## 3. Năm tầng nhận thức và 22 nhiệm vụ

### 3.1. `Recognition and Recall`

Năm nhiệm vụ:

- nhận diện thực thể;
- phân loại chủ đề;
- nhớ khái niệm;
- nhớ điều luật;
- nhớ cấu trúc văn bản.

### 3.2. `Understanding and Structuring`

Năm nhiệm vụ:

- trích xuất quan hệ;
- nhận diện thành phần;
- cấu trúc đồ thị;
- xác minh phán quyết;
- nhận diện ý định người dùng.

### 3.3. `Reasoning and Inference`

Năm nhiệm vụ:

- dự đoán điều/khoản;
- dự đoán quyết định của tòa;
- suy luận nhiều điều luật;
- phát hiện xung đột;
- xác định chế tài/biện pháp khắc phục.

### 3.4. `Interpretation and Generation`

Ba nhiệm vụ:

- tóm tắt văn bản pháp luật;
- tạo lập luận tư pháp;
- đưa ý kiến pháp lý khách quan.

### 3.5. `Ethics, Fairness and Bias`

Bốn nhiệm vụ:

- phát hiện thiên lệch;
- bảo vệ quyền riêng tư/dữ liệu;
- kiểm tra nhất quán đạo đức;
- phát hiện điều khoản hợp đồng không công bằng.

**Kết luận có căn cứ.** Năm tầng nhận thức tổ chức taxonomy và độ phủ. Nhiệm vụ vẫn là đơn vị có đầu vào, đầu ra và thước đo riêng.

Vị trí nguồn: `Section 3.1`; `Table 1`; `Figure 3`.

## 4. Một mẫu benchmark được biểu diễn như thế nào?

Tùy nhiệm vụ, một mẫu có:

- chỉ dẫn theo nhiệm vụ;
- văn bản, tình huống hoặc câu hỏi đầu vào;
- nhãn, cấu trúc hoặc phản hồi tham chiếu;
- liên kết tới nguồn pháp luật;
- thước đo được quy định ở cấp nhiệm vụ.

Một mẫu thuộc một nhiệm vụ. Bài báo không gắn một bộ tiêu chí sư phạm riêng cho từng mẫu.

Vị trí nguồn: `Table 1`; `Section 3.2`; các phụ lục mô tả nhiệm vụ.

## 5. Thước đo được chọn như thế nào?

Các thước đo thay đổi theo dạng đầu ra:

- `Accuracy`;
- `F1`;
- `Macro-F1`;
- `ROUGE-L`;
- `Node-F1`;
- `Edge-F1`;
- các biến thể F1 nhị phân.

Ba nhiệm vụ sinh văn bản dùng `ROUGE-L` làm thước đo tự động chính và có thêm đánh giá con người trên một tập con.

**Kết luận có căn cứ.** Bài báo không cố dùng một thước đo cho toàn bộ 22 nhiệm vụ. Hợp đồng đầu ra quyết định thước đo.

Vị trí nguồn: `Table 1`; `Section 4.1`.

## 6. Đánh giá con người cho nhiệm vụ sinh văn bản

Phản hồi sinh được chấm thêm trên hai chiều, thang 1–5:

- `Legal Accuracy` — tính chính xác pháp lý;
- `Completeness` — mức đầy đủ.

Đây là một lớp kiểm tra bổ sung trên tập mẫu, không phải tiêu chí riêng cho từng mẫu trong toàn bộ bộ dữ liệu.

**Bất nhất trong nguồn.** Phần trình bày bảng mô tả ba chuyên gia cao cấp, trong khi phụ lục mô tả hai chuyên gia trẻ cho quy trình liên quan. Bản tóm tắt không tự chọn một mô tả là đúng; thành phần người chấm được ghi là điểm cần xác minh.

Vị trí nguồn: `Table 4`; `Appendix F.1`.

## 7. Vai trò của đáp án và phản hồi tham chiếu

Nhiệm vụ phân loại/trích xuất có nhãn chuẩn. Nhiệm vụ sinh văn bản có phản hồi do con người viết.

Đáp án hoặc phản hồi tham chiếu phục vụ hợp đồng của nhiệm vụ:

- tính thước đo tự động khi phù hợp;
- làm chuẩn để kiểm tra tính đúng;
- so sánh trong đánh giá con người.

**Giới hạn chuyển giao.** Việc VietLegal dùng `ROUGE-L` không phải bằng chứng rằng phản hồi gia sư mở nên được chấm bằng độ giống văn bản.

Vị trí nguồn: `Table 1`; `Table 4`; `Appendix F`.

## 8. Nguồn dữ liệu và truy vết

**Bằng chứng.**

- Văn bản được thu thập từ nguồn nhà nước chính thức.
- Khoảng 55.000 văn bản được xử lý bằng phân tích HTML và nhận dạng ký tự quang học.
- Dữ liệu được tổ chức trong cơ sở dữ liệu văn bản và đồ thị tri thức.
- Mỗi mẫu cuối được gắn với nguồn pháp luật có thẩm quyền.

Vị trí nguồn: `Section 3.2`; `Figure 1`; `Appendix E`.

## 9. Quy trình chuyên gia

### 9.1. Phân vai

- Chuyên gia cao cấp định nghĩa chủ đề, nguồn và hướng dẫn.
- Hai chuyên gia trẻ tạo tình huống/đáp án theo các đợt dữ liệu độc lập.
- Các đợt được đổi để kiểm tra chéo trong chế độ mù.
- Trường hợp không thống nhất được chuyển lên chuyên gia cao cấp phân xử.

### 9.2. Huấn luyện người gán nhãn

Người gán nhãn:

- trải qua hai ngày huấn luyện;
- làm thử 50 mẫu cho mỗi nhiệm vụ;
- hiệu chỉnh trên các trường hợp biên;
- phải đạt ít nhất 85% khớp với nhãn chuẩn.

### 9.3. Độ đồng thuận

- độ đồng thuận ban đầu: `92,39%`;
- Cohen’s Kappa: `0,89`;
- `7,61%` mẫu bất đồng được giải quyết bằng thảo luận/phân xử;
- đánh giá sinh văn bản báo Cohen’s Kappa trung bình `0,92`.

Vị trí nguồn: `Appendix E`; `Appendix F.1`; `Table 4`.

## 10. Kiểm tra trùng lặp và rò rỉ

**Bằng chứng.** Bài báo kiểm tra 1.000 mẫu phân tầng bằng tìm kiếm web, Common Crawl, n-gram và so khớp gần đúng. Tỷ lệ chồng lặp tiềm năng khoảng `1,8%`, chủ yếu liên quan văn bản pháp luật hoặc mẫu biểu bắt buộc.

**Khả năng chuyển giao.** Dự án có thể dùng tư duy tương tự để kiểm tra:

- trùng lặp giữa các hội thoại;
- lộ nguyên văn học liệu trong đề;
- mẫu do mô hình sinh có giống nguồn công khai hoặc mẫu huấn luyện hay không.

Vị trí nguồn: phần phân tích nhiễm dữ liệu; phụ lục liên quan.

## 11. Kết quả liên quan tới thiết kế benchmark

**Bằng chứng.**

- 23 mô hình có kết quả khác nhau theo nhóm nhiệm vụ.
- Mô hình thích nghi miền không thắng đồng đều ở mọi tầng nhận thức.
- Truy xuất nguồn theo kiểu tác tử giúp một số nhiệm vụ nhưng không phải tất cả.
- Phản hồi do con người viết cao hơn mô hình khoảng 1,2–1,5 điểm ở các chiều đánh giá sinh văn bản.

Vị trí nguồn: `Table 2`; `Table 3`; `Table 4`; `Table 11`.

## 12. Khả năng chuyển sang Tin học THCS

### Bằng chứng có thể sử dụng

- Nhiệm vụ phải có hợp đồng đầu vào–đầu ra và thước đo rõ.
- Mức nhận thức có thể tổ chức taxonomy/độ phủ mà không thay thế nhiệm vụ.
- Mỗi mẫu cần truy vết tới nguồn có thẩm quyền.
- Quy trình dữ liệu quan trọng cần kiểm tra chéo, đo đồng thuận và phân xử.
- Có thể dùng đánh giá con người trên tập con để kiểm phép chấm tự động.

### Suy luận cho dự án

- `Biết`, `Hiểu`, `Vận dụng` nên là trục độ phủ, không phải nhiệm vụ gia sư.
- Mẫu Tin học cần truy vết tới fragment SGK/SGV hoặc học liệu phù hợp.
- Bảng provenance nên lưu nguồn và trạng thái xác minh cho nhiệm vụ, tiêu chí và mẫu.
- Trước khi dùng bộ chấm tự động toàn tập, cần thí điểm với nhiều giáo viên/người rà soát.

## 13. Những phần không nên chuyển trực tiếp

- 22 nhiệm vụ pháp luật không có ý nghĩa sư phạm trực tiếp cho Tin học.
- Năm tầng nhận thức đã được điều chỉnh cho miền luật, không thể thay ba mức HNMU.
- `ROUGE-L` không đủ để đánh giá phản hồi gia sư mở.
- Hai chiều `Legal Accuracy` và `Completeness` không phải rubric gia sư.
- Nguồn luật chính thức có tính cấu trúc khác ảnh SGK/SGV và fragment học liệu hiện tại.

## 14. Giới hạn của bằng chứng

- Đây không phải benchmark gia sư.
- Bản đang dùng là tiền công bố.
- Có bất nhất về thành phần người đánh giá sinh văn bản.
- Quy trình chuyên gia miền luật có thể đắt và khó sao chép nguyên xi.
- Kết quả không chứng minh tác động lên việc học của học sinh.

## 15. Phát biểu đưa vào ma trận bằng chứng

| Phát biểu | Nhãn | Vị trí nguồn |
|---|---|---|
| VietLegal tổ chức 22 nhiệm vụ trong năm tầng nhận thức. | Bằng chứng | `Section 3.1`; `Table 1` |
| Mỗi nhiệm vụ có thước đo phù hợp với đầu ra; không có một thước đo chung. | Bằng chứng | `Table 1`; `Section 4.1` |
| Mức nhận thức tổ chức taxonomy, không thay thế nhiệm vụ. | Bằng chứng | `Section 3.1`; `Table 1` |
| Dữ liệu có truy vết nguồn, kiểm tra chéo và phân xử. | Bằng chứng | `Section 3.2`; `Appendix E` |
| Dự án nên giữ mức nhận thức làm trục độ phủ và nhiệm vụ làm hợp đồng hành vi. | Suy luận | Đối chiếu với miền Tin học THCS |

## 16. Câu hỏi mở cho HNMU/UET

1. Mỗi nhiệm vụ/tiêu chí Tin học phải truy vết tới học liệu ở mức nào?
2. Ai là người viết, rà soát và phân xử tiêu chí chấm?
3. Cần bao nhiêu người chấm độc lập trong thí điểm?
4. Ngưỡng đồng thuận nào đủ để dùng bộ chấm tự động?
5. Cần kiểm tra trùng/rò rỉ ở cấp hội thoại thô, mẫu ứng viên hay cả hai?

## 17. Kết luận có mục tiêu

VietLegal không trả lời trực tiếp cách chấm một gia sư AI. Giá trị của bài báo đối với Plan 03 nằm ở cấu trúc:

```text
tầng nhận thức để tổ chức độ phủ
≠ nhiệm vụ có đầu vào–đầu ra
→ thước đo theo nhiệm vụ
→ nguồn có thẩm quyền
→ kiểm tra chéo
→ đo đồng thuận
→ phân xử
```

Do đó, bài báo hỗ trợ phần taxonomy, provenance và kiểm định của Plan 03, nhưng không nên được dùng để biện minh cho nội dung rubric sư phạm.
