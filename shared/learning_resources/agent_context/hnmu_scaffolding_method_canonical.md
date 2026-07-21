# Phương pháp dàn giáo cho gia sư ảo — bản Markdown chuẩn hóa từ tài liệu HNMU

Trạng thái: `derived_from_hnmu_source` — bản Markdown này được chuyển từ tài liệu `.docx` gốc do HNMU biên soạn để agent có thể đọc ổn định hơn.

Nguồn gốc:

```text
document/teacher_training_curriculum/benchmark_building_documents/KhungDanGiao_HoiThoaiMinhHoa.docx
```

Ghi chú sử dụng:

- Đây là nguồn chính dạng Markdown cho agent khi kiểm dấu hiệu dàn giáo trong hội thoại HNMU.
- Nếu cần đối chiếu tuyệt đối, quay lại file `.docx` gốc.
- Không hiểu năm “bước” dưới đây như một quy trình tuyến tính bắt buộc; tài liệu gốc nêu rõ đây là các chức năng dàn giáo để gia sư chọn theo diễn biến học sinh.

## I. Khung dàn giáo cho gia sư ảo

### Bước 1: Tiếp nhận và Chẩn đoán

Gia sư ảo bắt đầu bằng việc thu hút sự chú ý của học sinh vào nhiệm vụ (recruitment), đồng thời yêu cầu học sinh nêu ý tưởng ban đầu để đánh giá xem học sinh đang ở đâu trong "Vùng phát triển gần nhất" (Zone of Proximal Development - ZPD). Gia sư không đưa ra giải pháp ngay lập tức mà đặt câu hỏi gợi mở.

### Bước 2: Giảm bậc tự do và Đặt mục tiêu

Khi bài toán quá phức tạp, gia sư giúp học sinh chia nhỏ bài toán thành các mục tiêu phụ (sub-goals) vừa sức. Gia sư hướng sự chú ý của học sinh vào việc giải quyết từng bước một để tránh quá tải nhận thức.

### Bước 3: Đánh dấu đặc điểm quan trọng và Hỗ trợ thích ứng

Gia sư phân tích câu trả lời của học sinh, đánh dấu (làm nổi bật) những lỗi sai hoặc thông tin quan trọng. Sự hỗ trợ (scaffolding) được cung cấp theo nguyên tắc thích ứng (contingency), đi từ mức độ thấp đến cao dựa trên nhu cầu của học sinh: Gợi mở (Prompt) -> Giải thích (Explanation) -> Gợi ý (Hint) -> Hướng dẫn (Instruction) -> Làm mẫu (Modeling).

### Bước 4: Kiểm soát sự thất vọng và Khuyến khích tự sửa lỗi

Nếu học sinh làm sai, gia sư không chỉ trích mà sử dụng phương pháp đặt câu hỏi Socrates để học sinh tự nhận ra lỗi và sửa lại. Điều này giúp giữ vững động lực và tránh sự nản chí.

### Bước 5: Rút dần hỗ trợ và Đánh giá

Khi học sinh đã hiểu vấn đề, gia sư rút dần sự trợ giúp (fading), để học sinh tự hoàn thiện bài toán một cách độc lập. Sau cùng, gia sư khen ngợi, tóm tắt lại kiến thức để xác nhận học sinh đã hoàn toàn làm chủ kĩ năng.

> **Lưu ý từ tài liệu gốc:** đây không là một quy trình các bước theo thứ tự thời gian, mà gọi là các "chức năng dàn giáo" (scaffolding functions). Gia sư sử dụng các chức năng này như một bộ công cụ. Tuỳ thuộc vào diễn biến của việc giải quyết vấn đề, gia sư sẽ chọn công cụ nào phù hợp nhất tại thời điểm đó. Thành công hay thất bại của học sinh tại bất kì thời điểm nào sẽ quyết định mức độ và hình thức hướng dẫn tiếp theo của gia sư.

## II. Hội thoại minh hoạ 1

**Nguồn bài tập:** Câu 2, phần Luyện tập, Bài 3: Thông tin trong máy tính, trang 15, SGK Tin học 6 (Kết nối tri thức với cuộc sống). Đề bài: Giả sử một bức ảnh được chụp bằng một máy ảnh chuyên nghiệp có dung lượng khoảng 12 MB. Vậy một thẻ nhớ 16 GB có thể chứa bao nhiêu bức ảnh như vậy?

- **Học sinh:** Thầy ơi, giúp em bài 2 phần Luyện tập trang 16 sách Tin học với ạ. Đề hỏi là một thẻ nhớ 16 GB có thể chứa được bao nhiêu bức ảnh 12 MB. Em không biết tính thế nào.

- **Gia sư ảo:** (Bước 1 - Tiếp nhận & Chẩn đoán): Chào em! Bài toán tính toán dung lượng lưu trữ này rất thú vị và bám sát thực tế đấy. Để biết thẻ nhớ chứa được bao nhiêu bức ảnh, em nghĩ chúng ta cần làm phép tính gì giữa tổng dung lượng thẻ nhớ và dung lượng của một bức ảnh?

- **Học sinh:** Em nghĩ là phải chia ạ. Mình lấy 16 chia cho 12.

- **Gia sư ảo:** (Bước 3 - Đánh dấu đặc điểm quan trọng & Bước 4 - Kiểm soát sự thất vọng): Em đã xác định đúng hướng là dùng phép chia rồi, rất tốt! Tuy nhiên, em hãy để ý kĩ đơn vị đo của thẻ nhớ là GB, còn của bức ảnh là MB. Hai đơn vị này đã giống nhau để mình chia trực tiếp chưa nhỉ?

- **Học sinh:** À, chưa ạ. Một cái là GB, một cái là MB.

- **Gia sư ảo:** (Bước 2 - Giảm bậc tự do & Đặt mục tiêu phụ): Đúng vậy. Nên bước đầu tiên, mình cần quy đổi chúng về cùng một đơn vị. Em hãy đổi dung lượng của thẻ nhớ từ GB sang MB trước nhé. Em có nhớ 1 GB bằng bao nhiêu MB không? (Sử dụng mức độ hỗ trợ Prompt/Gợi mở).

- **Học sinh:** Em nhớ mang máng là 1000 MB ạ.

- **Gia sư ảo:** (Bước 3 - Hỗ trợ thích ứng-Gợi ý): Em nhớ rất gần đúng rồi! Tuy nhiên, 1000 là con số người ta hay dùng để làm tròn cho dễ nhớ ở ngoài đời. Trong máy tính, các đơn vị như KB, MB, GB liên hệ với nhau qua một con số đặc biệt hơn. Em hãy xem lại Bảng 1.3 "Một số đơn vị cơ bản đo dung lượng thông tin" ở trang 15 để tìm con số chính xác là bao nhiêu nhé.

- **Học sinh:** Em xem lại rồi, 1 GB = 1024 MB. Vậy thẻ nhớ 16 GB sẽ bằng 16 x 1024 = 16384 MB!

- **Gia sư ảo:** (Bước 5 - Rút dần hỗ trợ & Đánh giá): Tuyệt vời! Vậy là em đã có tổng dung lượng thẻ nhớ là 16384 MB và mỗi bức ảnh chiếm 12 MB. Cùng một đơn vị rồi, bây giờ em hãy tự thực hiện phép chia ban đầu em đề xuất để tìm ra kết quả cuối cùng xem thẻ nhớ chứa được bao nhiêu bức ảnh nào?

- **Học sinh:** Em lấy 16384 chia cho 12. Kết quả là khoảng 1365,33. Vậy thẻ nhớ sẽ chứa được tối đa 1365 bức ảnh ạ!

- **Gia sư ảo:** Hoàn toàn chính xác! Em đã làm rất tốt khi biết phân tích bài toán, chủ động tra cứu quy đổi đơn vị và tính toán cẩn thận. Em có muốn thử sức thêm một câu hỏi nào về quy đổi dung lượng nữa không?

## III. Hội thoại minh hoạ 2

**Nguồn bài tập:** trong Bài 3: Thông tin trong máy tính, SGK Tin học 6 (Kết nối tri thức với cuộc sống), câu hỏi 2 phần vận dụng: Thực hiện tương tự như Hoạt động 1, với các số từ 0 đến 15, mã hoá số 8 đến 15 và đưa ra nhận xét.

- **Học sinh:** Chào gia sư, em đang làm một bài tập nâng cao từ Hoạt động 1 trang 13 sách Tin học 6. Đề bài yêu cầu: "Thực hiện tương tự Hoạt động 1 với dãy số từ 0 đến 15, hãy mã hoá các số từ 8 đến 15 và đưa ra nhận xét". Em chưa biết phải bắt đầu thế nào.

- **Gia sư ảo:** (Bước 1 - Tiếp nhận & Chẩn đoán): Chào em! Đây là một bài toán rất hay để em hiểu sâu hơn về cách máy tính mã hoá dữ liệu thành các bit 0 và 1. Để bắt đầu, em hãy nhớ lại Hoạt động 1, dãy số ban đầu chúng ta cần viết ra sẽ bắt đầu và kết thúc bằng số nào nhỉ?

- **Học sinh:** Dãy số sẽ từ 0 đến 15 ạ: 0, 1, 2, ..., 14, 15. Tổng cộng là có 16 số.

- **Gia sư ảo:** (Bước 2 - Giảm bậc tự do & Đặt mục tiêu phụ): Rất chuẩn! Thay vì làm tất cả các số cùng lúc, chúng ta hãy đặt mục tiêu mã hoá thử số 8 trước nhé. Bước đầu tiên của thuật toán là chia dãy làm hai nửa (trái, phải) đều nhau. Với 16 số này, em hãy cho biết nửa trái và nửa phải gồm những số nào? (Sử dụng mức độ hỗ trợ: Gợi mở - Prompt).

- **Học sinh:** 16 số chia đôi thì mỗi bên 8 số. Em nghĩ nửa trái là từ 0 đến 8, nửa phải là từ 9 đến 15 ạ.

- **Gia sư ảo:** (Bước 3 - Đánh dấu đặc điểm quan trọng & Bước 4 - Kiểm soát sự thất vọng/Khuyến khích tự sửa lỗi): Em làm phép chia 16 chia 2 bằng 8 rất đúng. Tuy nhiên, em thử đếm tay lại xem: 0, 1, 2, 3, 4, 5, 6, 7, 8... như vậy là có 9 số mất rồi! Em hãy xem lại xem nửa trái nên kết thúc ở số mấy để có vừa đúng 8 số? (Sử dụng mức độ hỗ trợ: Gợi ý - Hint).

- **Học sinh:** Ôi em đếm nhầm vì quên mất số 0! Nửa trái sẽ là từ 0 đến 7, còn nửa phải là từ 8 đến 15.

- **Gia sư ảo:** (Bước 3 - Hỗ trợ thích ứng - Phản hồi xác nhận): Hoàn toàn chính xác! Bây giờ mình đang tìm số 8. Số 8 nằm ở nửa trái hay nửa phải? Theo quy tắc của sách, em sẽ ghi lại chữ "trái" hay "phải" và giữ lại nửa nào?

- **Học sinh:** Số 8 nằm ở nửa phải. Nên em ghi lại chữ "phải" và giữ lại nửa (8 đến 15) để làm tiếp.

- **Gia sư ảo:** (Bước 5 - Rút dần hỗ trợ): Tuyệt vời! Em đã nắm được quy luật rồi đấy. Bây giờ, em hãy tiếp tục tự chia đôi nửa (8 đến 15) này cho đến khi chỉ còn lại đúng số 8, và đọc cho thầy/cô chuỗi vị trí "trái/phải" mà em ghi lại được nhé. (Fading - Để học sinh tự thực hiện chuỗi thao tác lặp).

- **Học sinh:** Em làm như sau:

Lần 2: Chia (8 đến 15) ra làm hai. Trái là (8 đến 11), phải là (12 đến 15). Số 8 ở bên trái -> Ghi "trái", giữ lại (8 đến 11).

Lần 3: Chia (8 đến 11) ra. Trái (8, 9), phải (10, 11). Số 8 bên trái -> Ghi "trái", giữ lại (8, 9).

Lần 4: Chia (8, 9) ra. Trái (8), phải (9). Số 8 bên trái -> Ghi "trái". Còn lại đúng số 8! Chuỗi em ghi được là: phải - trái - trái - trái.

- **Gia sư ảo:** (Bước 5 - Kiểm chứng & Chuyển bước): Phân tích từng bước cực kì rõ ràng! Bước cuối cùng, áp dụng quy tắc "trái thành 0, phải thành 1", em hãy đọc mã nhị phân của số 8 nào.

- **Học sinh:** Phải là 1, trái là 0. Vậy số 8 được mã hoá thành 1000 ạ.

- **Gia sư ảo:** (Bước 2 & 3 - Đặt mục tiêu cho phần "Nhận xét"): Đúng 100% luôn! Bây giờ quay lại yêu cầu thứ hai của đề bài: "đưa ra nhận xét về các số từ 8 đến 15". Em hãy nhìn lại lần chia đầu tiên của chúng ta (chia dãy 0-15 thành nửa trái 0-7, nửa phải 8-15). Nếu em chọn bất kì một số nào từ 8 đến 15 (chẳng hạn số 9, số 12 hay số 15), chúng sẽ luôn rơi vào nửa nào ở lần chia đầu tiên? Điều đó quyết định bit đầu tiên của mã nhị phân là gì? (Sử dụng mức độ hỗ trợ: Gợi mở - Prompt).

- **Học sinh:** Dạ, vì nó nằm từ 8 đến 15 nên ở lần chia đầu tiên chắc chắn nó phải rơi vào nửa phải. Mà nửa phải thì luôn đổi thành số 1. Vậy bit đầu tiên của tất cả các số này đều là 1!

- **Gia sư ảo:** (Bước 5 - Đánh giá hoàn thiện): Rất sắc sảo! Đó chính là nhận xét cốt lõi. Trong dãy 0-15, các số từ 8 đến 15 khi mã hoá sẽ cần 4 bit (vì trải qua 4 lần chia) và bit ngoài cùng bên trái luôn luôn là 1 (như số 8 là 1000, số 15 là 1111). Ngược lại, nhóm từ 0 đến 7 nằm ở nửa trái nên bit đầu tiên sẽ luôn là 0. Em đã giải quyết trọn vẹn cả hai yêu cầu của bài toán một cách độc lập và xuất sắc rồi đấy! Em có muốn thử tự nhẩm nhanh mã nhị phân của một số khác như số 15 không?

## Tài liệu tham khảo

Anderson, J. R., Corbett, A. T., Koedinger, K. R., & Pelletier, R. (1995). Cognitive tutors: Lessons learned. The Journal of the Learning Sciences, 4(2), 167-207.

Collins, A., Brown, J. S., & Holum, A. (1991). Cognitive apprenticeship: Making thinking visible. American Educator, 15(3), 38-46.

Graesser, A. C., Person, N. K., & Magliano, J. P. (1995). Collaborative dialogue patterns in naturalistic one-to-one tutoring. Applied Cognitive Psychology, 9(6), 1-28.

Macina, J., Daheim, N., Hakimi, I., Kapur, M., Gurevych, I., & Sachan, M. (2025). MathTutorBench: A benchmark for measuring open-ended pedagogical capabilities of LLM tutors.

Olney, A. M. (2014). Scaffolding made visible. In Design Recommendations for Intelligent Tutoring Systems - Volume 2: Adaptive Instructional Management (pp. 327-340).

Schouten, D. G. M., Massink, P., Donker, S. F., Neerincx, M. A., & Cremers, A. H. M. (2021). Using scaffolding to formalize digital coach support for low-literate learners. User Modeling and User-Adapted Interaction, 31(2), 183-223.

Wood, D., Bruner, J. S., & Ross, G. (1976). The role of tutoring in problem solving. Journal of Child Psychology and Psychiatry, 17(2), 89-100.
