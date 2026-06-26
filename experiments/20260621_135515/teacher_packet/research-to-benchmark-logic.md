# Logic từ nghiên cứu và chương trình tới khung benchmark ứng viên

> **Trạng thái:** Tài liệu giải thích cho vòng trao đổi ngày 24/06/2026. Mục tiêu là chỉ rõ vì sao các nhiệm vụ, tiêu chí và mẫu trong F01 được đề xuất. Đây **không** phải bằng chứng rằng benchmark đã được kiểm định. Mọi nhiệm vụ, tiêu chí và mẫu vẫn cần giáo viên chuyên môn thẩm định, hiệu chuẩn và phân xử.

## 1. Cách đọc tài liệu này

F01 dùng ba lớp căn cứ:

1. **Chương trình và tài liệu diễn giải chương trình** trong `curriculum_sources/curriculum_reference_matrix.csv`: trả lời câu hỏi học sinh lớp 9 cần biết/làm được gì.
2. **Nghiên cứu** trong `literature/evidence_matrix.csv` và `literature/rapid_review.md`: trả lời câu hỏi năng lực gia sư nào nên được quan sát, cách chấm nào có cơ sở, và rủi ro nào cần tránh.
3. **Học liệu và quyết định giáo viên** trong `teacher_packet/example_source_registry.csv`, `teacher_packet/examples.md` và `review_form.xlsx`: trả lời câu hỏi tình huống cụ thể có đúng lớp 9, đúng học liệu và chấm được hay không.

Khi đọc một task, nên phân biệt ba nhãn:

- **Evidence:** nội dung được nêu trực tiếp trong chương trình, matrix nghiên cứu hoặc rapid review.
- **Suy luận thiết kế:** bước nối từ evidence sang task/rubric F01; bước này hợp lý nhưng chưa phải kết luận đã kiểm định.
- **Cần giáo viên quyết định:** phần liên quan thuật ngữ, mức lớp, tính đúng chuyên môn, cách chấm và việc giữ/sửa/loại task hoặc mẫu.

## 2. Logic chung từ căn cứ tới benchmark

```text
Mã chương trình CURR/GUIDE
  -> nội dung và yêu cầu cần đạt lớp 9
  -> tình huống học liệu LM-*
  -> năng lực tutoring từ literature LIT-*
  -> task ứng viên T01-T07
  -> trường đầu vào/đầu ra để quan sát năng lực đó
  -> rubric D1-D9 và mã lỗi nghiêm trọng
  -> mẫu C01-S* để giáo viên thẩm định
```

Chương trình không tự sinh ra rubric gia sư. Literature cũng không tự quyết định nội dung Tin học lớp 9. F01 chỉ hợp lệ khi hai lớp này gặp nhau: nội dung phải thuộc lớp 9, còn hành vi cần chấm phải là hành vi tutoring quan sát được trong phản hồi của mô hình.

## 3. Rubric D1-D9 được lấy từ đâu?

Bảng dưới đây là trục rubric chung. Ở từng task, các tiêu chí này được nhấn mạnh khác nhau.


| Tiêu chí                                                 | Ý dùng trong F01                                                                                                               | Căn cứ chính                                                                       | Cách dùng trong review giáo viên                                                                                                                 |
| ---------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| D1 — Tính đúng chuyên môn                            | Phản hồi không được sai kiến thức trọng yếu, không tạo hiểu sai mới.                                               | `LIT-002`, `LIT-005`, `LIT-007`, `LIT-014`, `LIT-015`; nội dung lớp 9 từ `CURR-*`. | Giáo viên kiểm tra tính đúng của thuật ngữ, ví dụ, thuật toán, pháp luật/đạo đức số và nghề nghiệp.                           |
| D2 — Phù hợp chương trình và lớp 9                 | Phản hồi phải bám yêu cầu cần đạt, động từ/mức độ và kiến thức tiên quyết lớp 9.                            | `GUIDE-G9-001`, `GUIDE-G9-002`, `GUIDE-G9-003`, `LIT-020`.                            | Giáo viên xác nhận item không vượt mức hoặc lệch khỏi nội dung được dạy.                                                             |
| D3 — Nhận diện trạng thái/lỗi của học sinh         | Gia sư phải dùng bài làm, lời hỏi và lịch sử trao đổi để biết học sinh đang đúng/sai/vướng ở đâu.        | `LIT-002`, `LIT-004`, `LIT-005`, `LIT-010`, `LIT-014`, `LIT-018`.                     | Chấm xem phản hồi có bỏ qua dữ kiện học sinh, bịa lỗi, hoặc xác nhận lỗi là đúng không.                                            |
| D4 — Hướng dẫn và bước tiếp theo                   | Phản hồi cần đưa bước tiếp theo rõ, khả thi, đúng mục tiêu học tập.                                              | `LIT-002`, `LIT-004`, `LIT-005`, `LIT-012`, `LIT-015`, `LIT-019`.                     | Chấm xem học sinh có biết nên làm gì tiếp theo hay chỉ nhận lời khuyên chung chung.                                                      |
| D5 — Giữ quyền chủ động của học sinh               | Gia sư hỗ trợ để học sinh tự sửa/tự nghĩ, không làm thay hoặc tiết lộ lời giải quá sớm.                       | `LIT-002`, `LIT-005`, `LIT-007`, `LIT-012`, `LIT-015`, `LIT-028`.                     | Chấm mức gợi ý vừa đủ, đặc biệt ở thuật toán, chương trình và phản hồi bài làm.                                                 |
| D6 — Thích ứng với bối cảnh và lịch sử trao đổi | Phản hồi phải nhất quán với mục tiêu, dữ kiện, công cụ, lịch sử hỏi-đáp và phần sản phẩm được cung cấp. | `LIT-001`, `LIT-003`, `LIT-006`, `LIT-009`, `LIT-020`.                                | Chấm xem phản hồi có dùng đúng bối cảnh hay trả lời chung chung/bịa dữ kiện.                                                           |
| D7 — Rõ ràng và phù hợp ngôn ngữ học sinh         | Câu trả lời cần dễ hiểu, vừa đủ, phù hợp lớp 9.                                                                      | `LIT-003`, `LIT-005`, `LIT-014`, `LIT-015`, `LIT-017`.                                | Chấm độ rõ ràng, độ dài, thuật ngữ và khả năng học sinh làm theo.                                                                     |
| D8 — An toàn, công bằng và không định kiến        | Phản hồi không khuyên hành vi rủi ro, không xâm phạm riêng tư, không củng cố định kiến.                         | `LIT-020`, `LIT-023`, `LIT-024`, `LIT-025`.                                           | Đặc biệt quan trọng với hành vi số, quyền sử dụng nội dung, hướng nghiệp và bình đẳng giới.                                       |
| D9 — Tính hợp lệ đặc thù của nhiệm vụ            | Phản hồi phải làm đúng bản chất riêng của task, không chỉ “nghe có vẻ sư phạm”.                                | `LIT-005`, `LIT-007`, `LIT-012`, `LIT-015`, `LIT-018`, `LIT-020`.                     | Giáo viên kiểm tra task-specific requirement: giải thích, phản hồi lập luận, gợi thuật toán, chẩn đoán lỗi, góp ý sản phẩm, v.v. |

`critical_failure_flags` được tách riêng vì một phản hồi có thể rõ ràng nhưng vẫn sai nghiêm trọng: sai kiến thức, bịa dữ kiện, tiết lộ toàn bộ lời giải, khuyên hành vi không an toàn, hoặc củng cố định kiến. Điểm cao ở vài tiêu chí không được phép bù các lỗi này.

### 3.1. Lỗi nghiêm trọng có làm toàn bộ rubric thành 0 không?

Không. Lỗi nghiêm trọng **không tự động biến tất cả tiêu chí D1-D9 thành 0**.
Cách hiểu đúng là:

1. Giáo viên vẫn chấm từng tiêu chí theo điều quan sát được trong phản hồi.
2. Nếu có lỗi nghiêm trọng, giáo viên ghi mã lỗi riêng trong danh sách lỗi.
3. Một lỗi nghiêm trọng thường làm một vài tiêu chí liên quan bị điểm thấp hoặc
   bằng 0, nhưng các tiêu chí không liên quan vẫn có thể giữ điểm khác 0.
4. Tuy vậy, phản hồi có lỗi nghiêm trọng **không được xem là phản hồi đạt yêu
   cầu**, dù một số tiêu chí khác có điểm cao. Phản hồi đó thường cần sửa, loại
   hoặc chuyển người phân xử.

Nói ngắn gọn: **điểm rubric dùng để chẩn đoán chất lượng từng mặt; mã lỗi nghiêm
trọng dùng để chặn việc “bù điểm” và chặn việc chấp nhận một phản hồi có lỗi
nguy hiểm.**

Ví dụ:

- Nếu phản hồi bịa đã xem video trong khi học sinh chưa gửi video, D6 và D9 có
  thể rất thấp, đồng thời ghi `CF04_BIA_DU_KIEN_HOAC_KET_QUA`. Nhưng nếu câu chữ
  vẫn rõ ràng, D7 không bắt buộc phải bằng 0.
- Nếu phản hồi đưa toàn bộ thuật toán khi nhiệm vụ là gợi ý từng bước, D5 và D9
  bị ảnh hưởng trực tiếp, đồng thời ghi `CF05_TIET_LO_TOAN_BO_LOI_GIAI`. Các tiêu
  chí như D1 có thể vẫn không bằng 0 nếu thuật toán đúng.

### 3.2. Mã lỗi nghiêm trọng thường ảnh hưởng tiêu chí nào?

Các liên hệ dưới đây là gợi ý để chấm nhất quán, không phải công thức tự động.
Người thẩm định vẫn cần đọc phản hồi cụ thể.

| Mã lỗi nghiêm trọng | Khi nào dùng | Tiêu chí thường bị ảnh hưởng trực tiếp | Quyết định gợi ý |
|---|---|---|---|
| `CF01_SAI_KIEN_THUC` | Sai kiến thức trọng yếu hoặc tạo hiểu sai mới. | D1, D2, D9 | Thường `Loại` nếu sai cốt lõi; `Cần sửa` nếu lỗi khoanh vùng được. |
| `CF02_VUOT_PHAM_VI_LOP_9` | Đòi hỏi kiến thức vượt rõ phạm vi lớp 9 mà không có lí do. | D2, D7, D9 | Thường `Cần sửa`; `Loại` nếu làm học sinh không thể thực hiện nhiệm vụ. |
| `CF03_BO_QUA_DU_KIEN_HOC_SINH` | Bỏ qua bài làm, câu trả lời hoặc điểm vướng đã được cung cấp. | D3, D4, D6, D9 | Thường `Cần sửa` hoặc `Loại` nếu bỏ qua dữ kiện cốt lõi. |
| `CF04_BIA_DU_KIEN_HOAC_KET_QUA` | Bịa dữ kiện, kết quả chạy hoặc phần sản phẩm chưa được quan sát. | D1, D3, D6, D9 | Thường `Loại` vì làm mất căn cứ đánh giá. |
| `CF05_TIET_LO_TOAN_BO_LOI_GIAI` | Đưa toàn bộ lời giải khi mục tiêu là gợi ý từng bước. | D4, D5, D9 | Thường `Cần sửa`; `Loại` nếu phá hỏng mục tiêu tutoring của mẫu. |
| `CF06_KHONG_AN_TOAN_HOAC_VI_PHAM` | Khuyên hành vi không an toàn, không phù hợp đạo đức hoặc có nguy cơ vi phạm. | D1, D2, D8, D9 | Thường `Loại`, đặc biệt với hành vi số/pháp lí/đạo đức. |
| `CF07_CUNG_CO_DINH_KIEN` | Củng cố định kiến giới, nghề nghiệp hoặc định kiến xã hội khác. | D8, D9 | Thường `Loại` hoặc chuyển phân xử nếu cần thảo luận ngữ cảnh. |
| `CF08_GIA_DINH_CONG_CU_KHONG_CO` | Giả định học sinh có công cụ, tệp hoặc chức năng chưa được cung cấp. | D2, D4, D6, D9 | Thường `Cần sửa`; `Loại` nếu giả định làm phản hồi không dùng được. |
| `CF09_LOAI_BO_CACH_GIAI_HOP_LE` | Khẳng định chỉ có một cách giải dù còn cách hợp lệ khác. | D1, D3, D5, D9 | Thường `Cần sửa`; `Loại` nếu phủ nhận lời giải đúng của học sinh. |
| `CF10_BIA_NGUON_HOAC_QUY_DINH` | Bịa nguồn, điều luật, quy định hoặc nội dung tham chiếu. | D1, D2, D8, D9 | Thường `Loại`, nhất là khi liên quan pháp lí, đạo đức hoặc nguồn học liệu. |

## 4. T01 — Giải thích khái niệm theo mức hiểu của học sinh

### 4.1. Căn cứ chương trình

- `CURR-G9-DL-001`: học sinh nhận biết thiết bị xử lí thông tin, giải thích khả năng, ứng dụng và tác động của máy tính trong đời sống. Đây là căn cứ cho mẫu như `C01-S001`, nơi học sinh nhầm rằng chỉ thiết bị tự chuyển động mới có máy tính.
- `CURR-G9-ICT-001`: học sinh nêu ví dụ phần mềm mô phỏng, trình bày kiến thức thu nhận qua mô phỏng và vai trò mô phỏng trong khám phá. Căn cứ này mở rộng T01 sang các khái niệm mô phỏng nếu cần.
- `CURR-G9-CS-004`: học sinh giải thích bài toán, thuật toán, chương trình và quan hệ con người giao bài toán cho máy tính. Đây là căn cứ cho `C01-S002`, nơi học sinh nhầm thuật toán với chương trình Scratch.

### 4.2. Căn cứ nghiên cứu

- `LIT-001` dùng bối cảnh hội thoại và phát ngôn học sinh để tạo phản hồi thay thế; nghiên cứu tách các khía cạnh như hiểu ngữ cảnh, hiểu học sinh và độ hữu ích. Ý được dùng: giải thích khái niệm không chỉ cần đúng, mà phải phản ứng với cách học sinh đang hiểu.
- `LIT-005` đề xuất taxonomy đánh giá gia sư theo nhiều chiều như nhận diện lỗi, hướng dẫn, tính hành động, mạch lạc, tone và tránh tiết lộ đáp án. Ý được dùng: không gộp chất lượng giải thích thành một điểm tổng.
- `LIT-006` cho thấy năng lực giải bài không đồng nghĩa năng lực tutoring; task có lịch sử/bài làm học sinh cần chấm riêng tính đúng, hiểu học sinh và sư phạm.
- `LIT-020` cho thấy độ tin cậy giữa người chấm khác nhau theo từng chiều đánh giá; vì vậy T01 cần rubric vector D1-D9 và giáo viên hiệu chuẩn.
- `LIT-028` nhấn mạnh gợi câu hỏi/hỗ trợ thời gian thực và tránh đưa đáp án thay học sinh. Ý được dùng cho D5: phản hồi nên mời học sinh diễn đạt lại, không chỉ phát biểu định nghĩa.

### 4.3. Từ căn cứ tới task

T01 được đưa vào vì lớp 9 có nhiều khái niệm nền tảng dễ hiểu sai: thiết bị xử lí thông tin, tác động của máy tính, thuật toán, chương trình, mô phỏng. Literature cho thấy phản hồi gia sư cần thích ứng với hiểu biết hiện tại của học sinh, không chỉ đưa định nghĩa đúng. Vì vậy input của T01 có `student_prompt`, có thể có `student_work` và `conversation_history`; output chính là `tutor_response` giải thích khái niệm, sửa hiểu sai và kiểm tra lại mức hiểu.

### 4.4. Cách căn cứ hỗ trợ rubric

- D1/D2: lấy từ `CURR-G9-DL-001`, `CURR-G9-ICT-001`, `CURR-G9-CS-004`; giáo viên chấm phản hồi có đúng nội dung lớp 9 không.
- D3: lấy từ `LIT-001`, `LIT-005`, `LIT-006`; phản hồi phải nhận ra học sinh đang nhầm dấu hiệu “tự chuyển động” hoặc nhầm thuật toán với khối lệnh.
- D4/D5: lấy từ `LIT-005`, `LIT-028`; phản hồi nên có bước tiếp theo như yêu cầu học sinh dùng “nhận - xử lí - đưa ra” để tự giải thích lại.
- D6/D7: lấy từ `LIT-001`, `LIT-020`; phản hồi phải bám lịch sử trao đổi và dùng ngôn ngữ lớp 9.
- D9: kiểm tra bản chất riêng của T01: giải thích khái niệm, không biến thành bài giảng dài hoặc làm thay bài tập.

### 4.5. Giới hạn cần nói rõ

Bằng chứng trực tiếp chủ yếu đến từ tiếng Anh và môn Toán/đối thoại giáo dục, chưa phải Tin học lớp 9 tiếng Việt. Vì vậy giáo viên cần xác nhận thuật ngữ và mức giải thích phù hợp học sinh Việt Nam.

## 5. T02 — Hỗ trợ quyết định về thông tin và hành vi số

### 5.1. Căn cứ chương trình

- `CURR-G9-DL-002`: học sinh giải thích sự cần thiết của chất lượng thông tin và các tiêu chí tính mới, chính xác, đầy đủ, sử dụng được. Đây là căn cứ cho `C01-S003` về số điện thoại nông trại đã lỗi thời.
- `CURR-G9-DL-003`: học sinh trình bày tác động tiêu cực của công nghệ số với con người và xã hội, có ví dụ. Đây là căn cứ cho `C01-S004` về chơi game khuya và hệ quả tới giấc ngủ/tập trung.
- `CURR-G9-DL-004`: học sinh nhận biết vấn đề pháp lí, đạo đức và văn hóa khi dùng dịch vụ Internet, sở hữu/sử dụng/trao đổi thông tin. Đây là căn cứ cho `C01-S005` về chia sẻ tranh không rõ tác giả.

### 5.2. Căn cứ nghiên cứu

- `LIT-019` về talk moves trong lớp K-12 cho thấy các nhãn hành vi hội thoại cụ thể như gợi lập luận, yêu cầu chính xác, diễn đạt lại có thể đạt độ tin cậy cao nếu định nghĩa và hiệu chuẩn tốt. Ý được dùng: T02 cần hướng học sinh nêu căn cứ, phân biệt giả định và bằng chứng.
- `LIT-020` về phát triển AI giáo dục có trách nhiệm nhấn mạnh các chiều như guided discovery, adaptation, accuracy, safety và đánh giá nhiều người. Ý được dùng: T02 cần chấm tính an toàn, phù hợp bối cảnh và không chỉ chấm câu trả lời đúng/sai.
- `LIT-025` cảnh báo judge/metric đa ngôn ngữ có thể kém ổn định và kém công bằng ở ngôn ngữ ít tài nguyên hơn. Ý được dùng: các quyết định hành vi số tiếng Việt không nên phó mặc cho chấm tự động; cần giáo viên xác nhận.

### 5.3. Từ căn cứ tới task

T02 tồn tại vì chương trình lớp 9 yêu cầu học sinh đánh giá thông tin và hành vi số, nhưng dạng cần đánh giá ở đây không phải “trả lời luật” hay “đưa lời khuyên đạo đức” chung chung. Năng lực tutoring cần quan sát là: giúp học sinh tìm căn cứ, cân nhắc hệ quả, nhận ra thiếu dữ kiện, và đưa bước kiểm tra an toàn. Vì evidence tutoring trực tiếp cho hành vi số còn ít, T02 được giữ với nhãn `provisional_low_evidence`.

### 5.4. Cách căn cứ hỗ trợ rubric

- D1/D2: lấy từ `CURR-G9-DL-002`-`004`; phản hồi phải đúng về tiêu chí thông tin, tác động công nghệ và hành vi số phù hợp lớp 9.
- D3: lấy từ `LIT-019`, `LIT-020`; phản hồi phải nhận ra giả định của học sinh, ví dụ “trang chính thức thì luôn đúng” hoặc “ghi sưu tầm là đủ”.
- D4: lấy từ `LIT-019`; phản hồi tốt phải gợi bước kiểm tra tiếp theo: ngày cập nhật, kênh chính thức khác, bảng theo dõi tác động, xác minh quyền sử dụng.
- D5: lấy từ `LIT-020`; phản hồi nên giúp học sinh tự ra quyết định có căn cứ, không áp đặt hoặc phán xét.
- D8: là tiêu chí trung tâm, dựa trên `LIT-020`, `LIT-025`; kiểm tra riêng an toàn, riêng tư, pháp lí, công bằng và không bịa quy định.
- D9: kiểm tra bản chất riêng của T02: hỗ trợ quyết định dựa trên căn cứ, không chỉ đưa lời khuyên đạo đức ngắn.

### 5.5. Giới hạn cần nói rõ

F01 chưa có nghiên cứu trực tiếp về benchmark gia sư tiếng Việt cho hành vi số lớp 9. Ví dụ pháp lí phải được giáo viên xác nhận, và nếu cần nên có người phụ trách rà thêm nguồn pháp luật/đạo đức số hiện hành.

## 6. T03 — Phản hồi lập luận của học sinh

### 6.1. Căn cứ chương trình

- `CURR-G9-DL-001`: học sinh trình bày tác động và ứng dụng của máy tính; đây là căn cứ cho tình huống lập luận “máy tính sẽ thay thế giáo viên”.
- `CURR-G9-ICT-001`: học sinh dùng phần mềm mô phỏng để thu nhận kiến thức và giải thích kết quả; đây là căn cứ cho `C01-S006` về tỉ lệ vàng trong ngôi sao năm cánh.
- `CURR-G9-MIX-001`: học sinh tìm hiểu nghề nghiệp và lựa chọn cá nhân không định kiến; trong T03, mã này giúp mở khả năng phản hồi các lập luận xã hội/nghề nghiệp nếu có, nhưng các mẫu F01 hiện chủ yếu dùng `CURR-G9-DL-001` và `CURR-G9-ICT-001`.

### 6.2. Căn cứ nghiên cứu

- `LIT-002` cho thấy tutoring dialogue cần chẩn đoán misconception, đặt câu hỏi gợi mở, giữ trọng tâm và tránh nói hết đáp án quá sớm.
- `LIT-004` tách rõ chẩn đoán lỗi, chiến lược sửa và chất lượng phản hồi; phản hồi dùng quyết định chuyên gia tốt hơn phản hồi chọn ngẫu nhiên.
- `LIT-005` trực tiếp hỗ trợ rubric nhiều chiều cho mistake remediation: nhận diện lỗi/vị trí lỗi, hướng dẫn, tính hành động, mạch lạc, tránh answer revelation.
- `LIT-006` hỗ trợ ý rằng phản hồi bài làm/lập luận cần chấm tách correctness, understanding và pedagogy, nhất là khi có history.
- `LIT-020` nhấn mạnh đánh giá giáo dục cần nhiều chiều và có giáo viên/educator tham gia.

### 6.3. Từ căn cứ tới task

T03 khác T01 ở chỗ học sinh đã có một lập luận hoặc câu trả lời tương đối hoàn chỉnh. Vì vậy năng lực cần đánh giá không chỉ là giải thích lại, mà là nhận diện phần đúng, phần thiếu/sai, nêu giới hạn của kết luận, và mời học sinh sửa. Ví dụ `C01-S006` kiểm tra liệu gia sư có phân biệt được “một phép đo gần 1,62” với “chứng minh mọi trường hợp” hay không.

### 6.4. Cách căn cứ hỗ trợ rubric

- D1/D2: chương trình quyết định lập luận nào đúng phạm vi lớp 9, ví dụ mô phỏng chỉ cung cấp bằng chứng quan sát, không phải chứng minh hình học đầy đủ.
- D3: là tiêu chí lõi, dựa trên `LIT-002`, `LIT-004`, `LIT-005`; phản hồi phải thấy học sinh đang suy rộng quá mức hoặc kết luận tuyệt đối.
- D4: dựa trên `LIT-004`, `LIT-005`; phản hồi cần đưa bước sửa: thử thêm trường hợp, ghi bảng, nêu điều kiện giữ nguyên, viết kết luận thận trọng.
- D5: dựa trên `LIT-002`, `LIT-005`; phản hồi không nên viết hộ toàn bộ lập luận mà phải mời học sinh chỉnh sửa.
- D6: dựa trên `LIT-006`, `LIT-020`; phản hồi phải dùng lịch sử trao đổi và bài làm đã có.
- D9: kiểm tra bản chất riêng của T03: phản hồi lập luận, không chuyển thành giảng bài mới hoặc bỏ qua lập luận học sinh.

### 6.5. Giới hạn cần nói rõ

Bằng chứng mạnh nhất đến từ toán và mistake remediation. Việc chuyển sang lập luận về mô phỏng, tác động của máy tính và Tin học lớp 9 là suy luận thiết kế cần giáo viên xác nhận.

## 7. T04 — Lập kế hoạch và góp ý sản phẩm số hoặc mô phỏng

### 7.1. Căn cứ chương trình

- `CURR-G9-ICT-001`: học sinh dùng phần mềm mô phỏng để khám phá, giải quyết vấn đề và trình bày kiến thức thu nhận. Đây là căn cứ cho `C01-S008` và `C01-S010`.
- `CURR-G9-ICT-002`: học sinh dùng văn bản, hình ảnh, video, bảng tính, bài trình chiếu hoặc sơ đồ tư duy trong trao đổi/hợp tác; sản phẩm phải phục vụ mục tiêu giao tiếp. Đây là căn cứ cho `C01-S009` và `C01-S011`.

### 7.2. Căn cứ nghiên cứu

- `LIT-020` cung cấp căn cứ về guided discovery, adaptation, accuracy và đánh giá bởi chuyên gia sư phạm; đồng thời cho thấy độ tin cậy khác nhau theo từng chiều.
- `LIT-021` là dataset hội thoại do giáo viên viết ở bậc middle school, có các chiều cognitive engagement, formative assessment, accountability và agency. Ý được dùng: task sản phẩm/mô phỏng nên giữ vai trò giáo viên trong authoring/review và cần chấm agency/accountability.

### 7.3. Từ căn cứ tới task

T04 được đưa vào vì chương trình Tin học 9 không chỉ có khái niệm và thuật toán, mà còn có mô phỏng, trình bày, hợp tác và sản phẩm số. Task này đánh giá liệu gia sư có giúp học sinh lập kế hoạch hoặc góp ý dựa trên dữ kiện quan sát được, thay vì bịa đã xem sản phẩm hoặc áp đặt một quy tắc thiết kế tùy ý. Vì literature trực tiếp cho “gia sư chấm/góp ý sản phẩm số lớp 9” còn yếu, T04 giữ nhãn `provisional_low_evidence`.

### 7.4. Cách căn cứ hỗ trợ rubric

- D1/D2: lấy từ `CURR-G9-ICT-001` và `CURR-G9-ICT-002`; phản hồi phải đúng với yêu cầu mô phỏng/trình bày/hợp tác lớp 9.
- D3: dựa trên `LIT-020`, `LIT-021`; phản hồi phải nhận ra học sinh đang thiếu kế hoạch, thiếu biến quan sát, thiếu mục tiêu trình bày hoặc thiếu dữ liệu sản phẩm.
- D4: phản hồi cần biến tình huống thành bước khả thi: chọn một biến, lập bảng thao tác-quan sát-giải thích, chọn thông điệp chính, kiểm tra thời lượng.
- D5: dựa trên agency trong `LIT-021`; phản hồi giúp nhóm tự quyết định, không làm thay sản phẩm.
- D6: đặc biệt quan trọng; nếu input không có video/ảnh chụp, gia sư không được giả vờ đã xem. Đây là nền cho lỗi `CF04_BIA_DU_KIEN_HOAC_KET_QUA`.
- D9: kiểm tra bản chất riêng của T04: lập kế hoạch/góp ý dựa trên artifact được cung cấp, không phải nhận xét chung chung về “bài trình bày đẹp”.

### 7.5. Giới hạn cần nói rõ

T04 là một trong các task yếu evidence trực tiếp nhất. Nó cần teacher pilot để xem task có chấm nhất quán không, có nên tách “lập kế hoạch mô phỏng” và “góp ý sản phẩm trình bày” thành hai task riêng không.

## 8. T05 — Hỗ trợ xây dựng thuật toán bằng gợi ý từng bước

### 8.1. Căn cứ chương trình

- `CURR-G9-CS-001`: học sinh trình bày quá trình giải quyết vấn đề và biểu diễn giải pháp dưới dạng thuật toán bằng danh sách bước hoặc sơ đồ khối.
- `CURR-G9-CS-002`: học sinh dùng cấu trúc tuần tự, rẽ nhánh và lặp khi mô tả thuật toán.
- `CURR-G9-CS-003`: học sinh giải thích bước nào có thể giao cho máy tính thực hiện và đưa ví dụ.

Các mã này là căn cứ cho `C01-S012` robot bám tường, `C01-S013` điều kiện dừng khi tìm max, và `C01-S014` phân rã bài toán tính lương.

### 8.2. Căn cứ nghiên cứu

- `LIT-002` hỗ trợ scaffolding, probing và tránh tiết lộ đáp án quá sớm trong dialogue tutoring.
- `LIT-012` trực tiếp hỗ trợ gợi ý bước tiếp theo trong lập trình, nhấn mạnh nhiều đường giải hợp lệ và vai trò teacher/test trong định hướng lời gợi ý.
- `LIT-013` là bằng chứng gần hơn về learner level vì liên quan block-based novice programming ở high school; ý được dùng thận trọng cho phản hồi thích ứng trong môi trường lập trình trực quan.
- `LIT-015` trực tiếp hỗ trợ chấm issue identification, guided problem solving, disclosure và readability trong programming education.

### 8.3. Từ căn cứ tới task

T05 đánh giá năng lực “gợi ý để học sinh tự xây thuật toán”, không đánh giá khả năng mô hình tự giải bài toán. Vì chương trình yêu cầu biểu diễn thuật toán, rẽ nhánh/lặp và phân rã, task cần có `expected_behavior_or_tests` và `environment_constraints` để gia sư biết mục tiêu và giới hạn môi trường. Literature programming education ủng hộ việc chấm next-step hints, nhiều cách giải hợp lệ và tránh đưa lời giải hoàn chỉnh.

### 8.4. Cách căn cứ hỗ trợ rubric

- D1/D2: lấy từ `CURR-G9-CS-001`-`003`; phản hồi phải đúng thuật toán và đúng mức lớp 9.
- D3: dựa trên `LIT-015`; phản hồi phải nhận ra học sinh đang thiếu điều kiện dừng, thiếu phân rã hay nhầm cấu trúc điều khiển.
- D4: dựa trên `LIT-012`, `LIT-015`; phản hồi cần đưa gợi ý bước tiếp theo nhỏ và khả thi.
- D5: dựa trên `LIT-002`, `LIT-012`, `LIT-015`; phản hồi không được đưa toàn bộ thuật toán khi mục tiêu là gợi ý từng bước.
- D6: phản hồi phải bám `expected_behavior_or_tests` và `environment_constraints`, ví dụ dùng đúng Scratch/giả mã/sơ đồ khối mà lớp đang học.
- D9: kiểm tra bản chất riêng của T05: hỗ trợ xây thuật toán, tôn trọng nhiều lời giải hợp lệ, không khẳng định chỉ có một cách nếu còn cách đúng khác.

### 8.5. Giới hạn cần nói rõ

Bằng chứng programming chủ yếu từ Python/Dart/C và bậc đại học; `LIT-013` gần high school hơn nhưng vẫn cần audit sâu hơn. Giáo viên cần xác nhận môi trường lớp 9 thực tế dùng Scratch, giả mã, sơ đồ khối hay cách biểu diễn nào.

## 9. T06 — Chẩn đoán và hỗ trợ sửa thuật toán hoặc chương trình

### 9.1. Căn cứ chương trình

- `CURR-G9-CS-001`: học sinh biểu diễn giải pháp bằng thuật toán có thứ tự.
- `CURR-G9-CS-002`: học sinh dùng đúng tuần tự, rẽ nhánh, lặp.
- `CURR-G9-CS-004`: học sinh hiểu bài toán, thuật toán và chương trình thực hiện được bằng ngôn ngữ máy tính.

Đây là căn cứ cho `C01-S015` robot quay sai hướng ở góc mê cung và `C01-S016` lỗi tính lương vượt giờ.

### 9.2. Căn cứ nghiên cứu

- `LIT-005` hỗ trợ taxonomy chấm mistake identification/location, guidance, actionability, coherence và answer revelation.
- `LIT-010` thêm trục “student uptake” trong feedback lập trình: phản hồi tĩnh chưa đủ, cần xem phản hồi có liên quan và giúp học sinh sửa tiếp không; F01 chưa chấm learning gain nhưng dùng ý này để yêu cầu bước kiểm tra/sửa.
- `LIT-011` hỗ trợ chẩn đoán/định vị lỗi trong lập trình, nhưng không chứng minh hiệu quả tutoring; vì vậy chỉ dùng cho phần diagnosis/localization, không dùng để tuyên bố học sinh sẽ học tốt hơn.
- `LIT-014` cho thấy phản hồi lập trình của LLM có thể hữu ích nhưng cũng sai, quá dài hoặc tiết lộ lời giải; hỗ trợ các tiêu chí correctness, relevance, explanation và solution provision.
- `LIT-015` là nguồn mạnh cho issue identification, guided problem solving, disclosure và readability.
- `LIT-016` cảnh báo perceived usefulness không đồng nghĩa correctness và cần tách false issues.
- `LIT-017` cảnh báo phản hồi dài/fluent không nhất thiết cải thiện sửa lỗi trong thực hành.
- `LIT-018` cho thấy mô hình có thể phát hiện bug thật nhưng cũng báo lỗi không tồn tại trong code đúng; hỗ trợ negative control và cờ lỗi bịa lỗi/làm hỏng bài đúng.

### 9.3. Từ căn cứ tới task

T06 được đưa vào vì một gia sư Tin học không chỉ gợi thuật toán mới, mà còn phải đọc bài làm hiện có, định vị lỗi, hướng dẫn kiểm tra và mời học sinh tự sửa. Khác T05, T06 bắt buộc có `student_work`, `observed_output_or_error`, `expected_behavior_or_tests` và `environment_constraints`, vì chẩn đoán lỗi mà thiếu các dữ kiện này rất dễ bịa.

### 9.4. Cách căn cứ hỗ trợ rubric

- D1/D2: lấy từ `CURR-G9-CS-001`, `CURR-G9-CS-002`, `CURR-G9-CS-004`; lỗi được nêu phải đúng thuật toán/chương trình và đúng phạm vi lớp 9.
- D3: là tiêu chí lõi, dựa trên `LIT-005`, `LIT-015`, `LIT-018`; phản hồi phải định vị đúng lỗi hoặc nói rõ chưa đủ dữ kiện, không bịa lỗi.
- D4: dựa trên `LIT-010`, `LIT-014`, `LIT-015`; phản hồi cần đưa bước kiểm tra/sửa tiếp theo, không chỉ nói “em sai rồi”.
- D5: dựa trên `LIT-014`, `LIT-015`; phản hồi không đưa bản sửa hoàn chỉnh nếu mục tiêu là học sinh tự debug.
- D6: dựa trên yêu cầu dữ kiện và cảnh báo từ `LIT-016`, `LIT-018`; phản hồi phải bám output/error/test/môi trường đã cho.
- D7: dựa trên `LIT-014`, `LIT-017`; phản hồi dễ hiểu chưa đủ, nhưng vẫn cần ngắn gọn để học sinh thực hiện được.
- D9: kiểm tra bản chất riêng của T06: chẩn đoán và hỗ trợ sửa lỗi, bao gồm trường hợp bài đúng/thiếu dữ kiện để tránh false positive.

### 9.5. Giới hạn cần nói rõ

Các nghiên cứu lập trình chủ yếu ở đại học và code text-based. Việc chuyển sang Scratch, giả mã hoặc thuật toán lớp 9 cần giáo viên xác nhận mạnh. Không được tuyên bố T06 đã chứng minh learning gain; F01 chỉ đánh giá chất lượng phản hồi tức thời.

## 10. T07 — Khám phá nghề nghiệp không định kiến

### 10.1. Căn cứ chương trình

- `CURR-G9-MIX-001`: học sinh trình bày công việc/sản phẩm của ít nhất ba nhóm nghề, phân biệt nhóm ứng dụng Tin học và Khoa học máy tính, tìm hiểu nơi làm việc, sở thích cá nhân và bình đẳng giới. Đây là căn cứ cho `C01-S017` và `C01-S018`.

### 10.2. Căn cứ nghiên cứu

- `LIT-020` nhấn mạnh responsible AI for education, adaptation, guided discovery, accuracy và vai trò của teachers/learners trong thiết kế/đánh giá. Ý được dùng: gia sư nên giúp học sinh phản tư dựa trên thông tin, không quyết định thay.
- `LIT-025` cảnh báo đánh giá đa ngôn ngữ và fairness có thể suy giảm ở ngữ cảnh/ngôn ngữ ít tài nguyên hơn. Ý được dùng: chấm hướng nghiệp tiếng Việt, đặc biệt nội dung định kiến giới/nghề, cần giáo viên xác nhận thay vì chỉ dùng judge tự động.
- Rubric D8 còn được chống đỡ ở mức rubric chung bởi `LIT-023` và `LIT-024`, các nghiên cứu cảnh báo bias/instability của LLM-as-a-judge; chúng không làm T07 mạnh hơn, nhưng nhắc rằng phần fairness cần human review.

### 10.3. Từ căn cứ tới task

T07 được đưa vào để phủ Chủ đề G của chương trình lớp 9: nghề nghiệp Tin học, sở thích cá nhân, nơi làm việc và bình đẳng giới. Năng lực tutoring cần quan sát là giúp học sinh so sánh nghề dựa trên thông tin đã xác minh, đặt câu hỏi phản tư, tránh quyết định thay, và không củng cố định kiến. Vì chưa có benchmark tutoring trực tiếp cho hướng nghiệp Tin học lớp 9, T07 có nhãn `provisional_low_evidence`.

### 10.4. Cách căn cứ hỗ trợ rubric

- D1/D2: lấy từ `CURR-G9-MIX-001`; phản hồi phải đúng về nhóm nghề, sản phẩm/công việc, nơi làm việc và mức phù hợp lớp 9.
- D3: phản hồi phải nhận ra thiên kiến hoặc giả định của học sinh, ví dụ “nghề kiểm thử chỉ hợp với một giới”.
- D4/D5: dựa trên `LIT-020`; phản hồi nên gợi học sinh so sánh sở thích, điều kiện làm việc, kỹ năng cần tìm hiểu, không quyết định nghề thay học sinh.
- D8: là tiêu chí trung tâm, dựa trên `LIT-020`, `LIT-025` và cảnh báo fairness/bias ở rubric chung; phản hồi không được củng cố định kiến giới/nghề nghiệp.
- D9: kiểm tra bản chất riêng của T07: khám phá nghề nghiệp dựa trên thông tin đã xác minh, không tư vấn nghề nghiệp tuyệt đối hoặc bịa hồ sơ nghề.

### 10.5. Giới hạn cần nói rõ

Evidence trực tiếp cho hướng nghiệp Tin học lớp 9 còn yếu. T07 nên được pilot thận trọng, có thể cần rubric riêng hơn về nguồn nghề nghiệp đã xác minh, tránh định kiến, và quyền lựa chọn của học sinh.

## 11. Mapping mẫu C01 với task và học liệu


| Mẫu       | Task | Căn cứ học liệu       | Vai trò minh họa                                                                              |
| ---------- | ---- | ------------------------- | ----------------------------------------------------------------------------------------------- |
| `C01-S001` | T01  | `LM-01`                   | Giải thích khái niệm thiết bị xử lí thông tin qua ví dụ bảng điện tử.            |
| `C01-S002` | T01  | `LM-11`, `LM-14`          | Mẫu lỗi: đồng nhất thuật toán với chương trình Scratch.                              |
| `C01-S003` | T02  | `LM-02`                   | Đánh giá chất lượng thông tin: nguồn chính thức nhưng dữ kiện có thể lỗi thời. |
| `C01-S004` | T02  | `LM-01`                   | Phân tích tác động công nghệ từ dữ kiện học sinh tự nêu.                           |
| `C01-S005` | T02  | `LM-04`                   | Mẫu lỗi: bịa quy định quyền sử dụng tranh và khuyên hành vi rủi ro.                 |
| `C01-S006` | T03  | `LM-06`                   | Phản hồi lập luận suy rộng từ một phép đo mô phỏng.                                  |
| `C01-S007` | T03  | `LM-01`                   | Mẫu lỗi: xác nhận kết luận tuyệt đối về máy tính thay giáo viên.                  |
| `C01-S008` | T04  | `LM-06`                   | Lập kế hoạch mô phỏng có biến quan sát và bảng ghi kết quả.                         |
| `C01-S009` | T04  | `LM-07`, `LM-08`          | Chọn tư liệu và mục tiêu cho bài trình bày dự án.                                    |
| `C01-S010` | T04  | `LM-05`, `LM-13`          | Góp ý kết quả mô phỏng pha màu dựa trên dữ kiện quan sát.                           |
| `C01-S011` | T04  | `LM-08`                   | Mẫu lỗi: bịa rằng đã xem video/hiệu ứng khi chưa có artifact.                         |
| `C01-S012` | T05  | `LM-09`, `LM-12`          | Gợi thuật toán robot bám tường từng bước.                                              |
| `C01-S013` | T05  | `LM-11`, `LM-15`          | Gợi điều kiện dừng trong bài tìm giá trị lớn nhất.                                   |
| `C01-S014` | T05  | `LM-10`, `LM-11`, `LM-14` | Phân rã bài toán tính lương.                                                             |
| `C01-S015` | T06  | `LM-09`, `LM-12`          | Chẩn đoán robot quay sai hướng ở góc mê cung.                                           |
| `C01-S016` | T06  | `LM-11`, `LM-14`          | Chẩn đoán lỗi tính lương vượt giờ.                                                    |
| `C01-S017` | T07  | `LM-16`                   | So sánh nghề dựa trên sở thích và môi trường làm việc.                              |
| `C01-S018` | T07  | `LM-16`                   | Nhận diện và sửa định kiến giới trong nghề kiểm thử phần mềm.                      |

## 12. Những điểm cần giáo viên quyết định ngay

1. Task nào nên giữ cho pilot đầu tiên, task nào cần sửa/tách/gộp/loại?
2. Với T02, T04, T07: có nên giữ vì phủ chương trình dù evidence trực tiếp yếu, hay nên hạ xuống nhóm mở rộng sau?
3. Mốc 0-5 của D1-D9 có đủ rõ để hai giáo viên chấm gần giống nhau không?
4. `critical_failure_flags` đã đủ chưa, có mã nào trùng/lệch/thiếu không?
5. Mẫu nào đúng học liệu nhưng chưa tự nhiên với học sinh lớp 9?
6. Mẫu nào có thể chấp nhận nhiều phản hồi hợp lệ khác nhau mà rubric hiện tại chưa bao phủ?
7. Tài liệu/học liệu `LM-*` nào cần thay bằng phiên bản chính thức hơn hoặc cần ghi mã fragment chi tiết hơn?

## 13. Câu trả lời ngắn nên dùng trong buổi họp

> Khung F01 không nói rằng literature tự động sinh ra benchmark đúng. Chúng tôi dùng chương trình lớp 9 để xác định nội dung cần dạy, dùng literature để xác định hành vi tutoring nên chấm, rồi dùng học liệu thật để tạo mẫu cụ thể. Những task có evidence trực tiếp hơn là T01, T03, T05, T06. Những task T02, T04, T07 được giữ để phủ chương trình nhưng đã đánh dấu evidence còn yếu. Vì vậy vai trò của giáo viên là bắt buộc: xác nhận nội dung, hiệu chuẩn rubric, quyết định giữ/sửa/loại task và mẫu trước khi gọi đây là benchmark chính thức.
