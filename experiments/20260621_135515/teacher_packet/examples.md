# 18 mẫu dùng để thảo luận và hiệu chuẩn

> Toàn bộ mẫu, phản hồi và điểm dưới đây đều **tạm thời**. Mục đích là giúp
> giáo viên thẩm định khung; chưa phải đáp án hoặc mẫu đã được phê duyệt.

## Hai trường dễ gây nhầm

- `conversation_history` là **danh sách có thứ tự**. Mỗi phần tử gồm `turn`
  (số lượt), `role` (`student` hoặc `tutor`) và `text` (nội dung lượt nói).
- `critical_failure_flags` là **danh sách mã lỗi nghiêm trọng**. Dùng `[]` khi
  không có lỗi; khi có nhiều lỗi, ghi nhiều mã trong cùng danh sách. Lỗi
  nghiêm trọng không được bù bằng điểm cao ở tiêu chí khác.

Ví dụ hình dạng dữ liệu:

```text
conversation_history = [{"turn": 1, "role": "student", "text": "..."},
                        {"turn": 2, "role": "tutor", "text": "..."}]
critical_failure_flags = []
critical_failure_flags = ["CF01_SAI_KIEN_THUC", "CF03_BO_QUA_DU_KIEN_HOC_SINH"]
```

## Danh mục mã lỗi nghiêm trọng

| Mã | Ý nghĩa |
|---|---|
| `CF01_SAI_KIEN_THUC` | Sai kiến thức trọng yếu hoặc tạo hiểu sai mới. |
| `CF02_VUOT_PHAM_VI_LOP_9` | Đòi hỏi kiến thức vượt rõ phạm vi lớp 9 mà không có lí do. |
| `CF03_BO_QUA_DU_KIEN_HOC_SINH` | Bỏ qua bài làm, câu trả lời hoặc điểm vướng đã được cung cấp. |
| `CF04_BIA_DU_KIEN_HOAC_KET_QUA` | Bịa dữ kiện, kết quả chạy hoặc phần sản phẩm chưa được quan sát. |
| `CF05_TIET_LO_TOAN_BO_LOI_GIAI` | Đưa toàn bộ lời giải khi mục tiêu là gợi ý từng bước. |
| `CF06_KHONG_AN_TOAN_HOAC_VI_PHAM` | Khuyên hành vi không an toàn, không phù hợp đạo đức hoặc có nguy cơ vi phạm. |
| `CF07_CUNG_CO_DINH_KIEN` | Củng cố định kiến giới, nghề nghiệp hoặc định kiến xã hội khác. |
| `CF08_GIA_DINH_CONG_CU_KHONG_CO` | Giả định học sinh có công cụ, tệp hoặc chức năng chưa được cung cấp. |
| `CF09_LOAI_BO_CACH_GIAI_HOP_LE` | Khẳng định chỉ có một cách giải dù còn cách hợp lệ khác. |
| `CF10_BIA_NGUON_HOAC_QUY_DINH` | Bịa nguồn, điều luật, quy định hoặc nội dung tham chiếu. |

## Bản đồ đủ 18 mẫu

| Nhiệm vụ | Mẫu được trình bày đầy đủ |
|---|---|
| T01 | C01-S001; C01-S002 |
| T02 | C01-S003; C01-S004; C01-S005 |
| T03 | C01-S006; C01-S007 |
| T04 | C01-S008; C01-S009; C01-S010; C01-S011 |
| T05 | C01-S012; C01-S013; C01-S014 |
| T06 | C01-S015; C01-S016 |
| T07 | C01-S017; C01-S018 |

Nguồn học liệu chi tiết, vị trí bài tập và mã kiểm tra tệp nằm trong
`example_source_registry.csv`. Các tệp học liệu gốc chỉ được đọc, không bị sửa.

## T01 — C01-S001: Nhận biết thiết bị có bộ xử lí thông tin

- **Tham chiếu chương trình:** `CURR-G9-DL-001`.
- **Tham chiếu nghiên cứu:** `LIT-001; LIT-005; LIT-020`.
- **Căn cứ học liệu:** `LM-01` — Bài 1, bài tập củng cố SGK trang 6; các ví dụ bảng điện tử, máy chụp cắt lớp, robot lắp ráp và ô tô lái tự động.

| Mã trường | Tên tiếng Việt | Giá trị trong mẫu |
|---|---|---|
| `task_context` | Bối cảnh nhiệm vụ | Học sinh lớp 9 đang giải thích vai trò của máy tính trong đời sống qua các thiết bị có bộ xử lí thông tin. |
| `student_prompt` | Câu hỏi/lời của học sinh | Vì sao bảng điện tử ở bến xe cũng được xem là có ứng dụng của máy tính? Nó chỉ hiện chữ thôi mà. |
| `student_work` | Bài làm hoặc cách nghĩ của học sinh | Em nghĩ chỉ robot và ô tô tự lái mới có máy tính vì chúng tự chuyển động. |
| `conversation_history` | Lịch sử trao đổi | 1. Học sinh: Em đã chọn robot lắp ráp và ô tô tự lái.<br>2. Gia sư: Em đang dựa vào dấu hiệu nào để nhận biết?<br>3. Học sinh: Chúng tự chuyển động nên chắc có máy tính. |
| `tutor_response` | Phản hồi của gia sư | Chuyển động không phải dấu hiệu duy nhất. Bảng điện tử phải nhận dữ liệu, xử lí dữ liệu rồi hiển thị đúng chuyến và thời gian. Em hãy dùng ba động từ “nhận – xử lí – đưa ra” để giải thích lại trường hợp bảng điện tử. |
| `criterion_scores` | Điểm theo từng tiêu chí | D1=5; D2=5; D3=5; D4=5; D5=5; D6=5; D7=5; D8=N/A; D9=5 |
| `critical_failure_flags` | Danh sách mã lỗi nghiêm trọng | [] |
| `reviewer_decision` | Quyết định của người thẩm định | Chấp nhận |
| `reviewer_rationale` | Lí do của người thẩm định | Phản hồi sửa đúng tiêu chí nhận biết, bám lịch sử trao đổi và yêu cầu học sinh tự diễn đạt lại. |

## T01 — C01-S002: Phân biệt thuật toán và chương trình trong bài toán tính lương

- **Tham chiếu chương trình:** `CURR-G9-CS-004`.
- **Tham chiếu nghiên cứu:** `LIT-001; LIT-005; LIT-006`.
- **Căn cứ học liệu:** `LM-11; LM-14` — Bài 16, nhiệm vụ 1 “Tính lương”, SGK trang 83–85; tệp Scratch 9-Bai16-NV1-TinhLuong.sb3.

| Mã trường | Tên tiếng Việt | Giá trị trong mẫu |
|---|---|---|
| `task_context` | Bối cảnh nhiệm vụ | Học sinh đã xem chương trình Scratch hỏi mức lương theo giờ và số giờ làm việc, sau đó tính lương định mức và lương vượt giờ. |
| `student_prompt` | Câu hỏi/lời của học sinh | Các khối Scratch trong bài tính lương chính là thuật toán, vậy thuật toán và chương trình là một phải không? |
| `student_work` | Bài làm hoặc cách nghĩ của học sinh | Em ghi: thuật toán là những khối lệnh có màu trong Scratch. |
| `conversation_history` | Lịch sử trao đổi | 1. Gia sư: Em hãy nói chương trình này nhận dữ liệu gì.<br>2. Học sinh: Mức lương theo giờ và số giờ làm.<br>3. Gia sư: Nếu chỉ viết các bước tính bằng lời mà chưa mở Scratch thì ta đã có gì?<br>4. Học sinh: Chắc vẫn là chương trình vì máy tính sẽ làm theo. |
| `tutor_response` | Phản hồi của gia sư | Đúng, thuật toán chỉ là tên khác của chương trình Scratch; hễ có các bước giải thì máy tính tự hiểu và chạy được. |
| `criterion_scores` | Điểm theo từng tiêu chí | D1=0; D2=2; D3=1; D4=0; D5=2; D6=1; D7=4; D8=N/A; D9=0 |
| `critical_failure_flags` | Danh sách mã lỗi nghiêm trọng | ["CF01_SAI_KIEN_THUC"] |
| `reviewer_decision` | Quyết định của người thẩm định | Loại |
| `reviewer_rationale` | Lí do của người thẩm định | Phản hồi đồng nhất thuật toán với chương trình và củng cố đúng hiểu sai mà nhiệm vụ cần sửa. |

## T02 — C01-S003: Đánh giá số điện thoại nông trại đã lỗi thời

- **Tham chiếu chương trình:** `CURR-G9-DL-002`.
- **Tham chiếu nghiên cứu:** `LIT-019; LIT-020`.
- **Căn cứ học liệu:** `LM-02` — Bài 2, hoạt động luyện tập SGK trang 11; thông tin của bạn An lấy từ website nông trại nhưng số điện thoại đã thay đổi.

| Mã trường | Tên tiếng Việt | Giá trị trong mẫu |
|---|---|---|
| `task_context` | Bối cảnh nhiệm vụ | Học sinh đánh giá chất lượng thông tin theo tính mới, chính xác, đầy đủ và sử dụng được. |
| `student_prompt` | Câu hỏi/lời của học sinh | Em lấy số điện thoại ngay trên trang web của nông trại mà gọi không được. Trang chính thức thì phải đúng chứ? |
| `student_work` | Bài làm hoặc cách nghĩ của học sinh | Nguồn đáng tin cậy nên thông tin chắc chắn chính xác. |
| `conversation_history` | Lịch sử trao đổi | 1. Học sinh: Em đã kiểm tra tên nông trại và địa chỉ đều khớp.<br>2. Gia sư: Em đã kiểm tra ngày cập nhật hoặc một kênh liên hệ khác chưa?<br>3. Học sinh: Chưa, em nghĩ trang chính thức là đủ. |
| `tutor_response` | Phản hồi của gia sư | Nguồn chính thức là một căn cứ tốt nhưng không bảo đảm mọi chi tiết luôn mới. Số điện thoại có thể đã thay đổi. Em hãy kiểm tra ngày cập nhật và đối chiếu thêm một kênh chính thức khác, rồi đánh giá riêng tính đáng tin cậy của nguồn và tính cập nhật của thông tin. |
| `criterion_scores` | Điểm theo từng tiêu chí | D1=5; D2=5; D3=5; D4=5; D5=5; D6=5; D7=5; D8=5; D9=5 |
| `critical_failure_flags` | Danh sách mã lỗi nghiêm trọng | [] |
| `reviewer_decision` | Quyết định của người thẩm định | Chấp nhận |
| `reviewer_rationale` | Lí do của người thẩm định | Phản hồi phân biệt đúng độ tin cậy của nguồn với tính cập nhật của một dữ kiện cụ thể. |

## T02 — C01-S004: Cân nhắc tác động của việc chơi game khuya

- **Tham chiếu chương trình:** `CURR-G9-DL-003`.
- **Tham chiếu nghiên cứu:** `LIT-019; LIT-020`.
- **Căn cứ học liệu:** `LM-01` — Bài 1, hoạt động luyện tập SGK trang 8 về mức độ sử dụng và tác động của công nghệ trong đời sống.

| Mã trường | Tên tiếng Việt | Giá trị trong mẫu |
|---|---|---|
| `task_context` | Bối cảnh nhiệm vụ | Học sinh cần nêu tác động tiêu cực của công nghệ số và đề xuất cách sử dụng phù hợp. |
| `student_prompt` | Câu hỏi/lời của học sinh | Em chơi game đến 1 giờ sáng nhưng vẫn đi học đủ. Như vậy chỉ hại mắt thôi đúng không? |
| `student_work` | Bài làm hoặc cách nghĩ của học sinh | Tác động tiêu cực duy nhất là mỏi mắt. |
| `conversation_history` | Lịch sử trao đổi | 1. Gia sư: Sáng hôm sau em có khó tập trung không?<br>2. Học sinh: Có buồn ngủ ở hai tiết đầu.<br>3. Gia sư: Việc đó ảnh hưởng gì đến học tập?<br>4. Học sinh: Em nghe bài không kịp nhưng chắc không liên quan đến game. |
| `tutor_response` | Phản hồi của gia sư | Dữ kiện em vừa nêu cho thấy còn có ảnh hưởng đến giấc ngủ và khả năng tập trung, không chỉ mắt. Em hãy lập bảng hai cột: biểu hiện em quan sát được và hậu quả có thể xảy ra; sau đó đề xuất một thay đổi nhỏ cho ba ngày tới để tự theo dõi. |
| `criterion_scores` | Điểm theo từng tiêu chí | D1=5; D2=5; D3=5; D4=5; D5=5; D6=5; D7=5; D8=5; D9=5 |
| `critical_failure_flags` | Danh sách mã lỗi nghiêm trọng | [] |
| `reviewer_decision` | Quyết định của người thẩm định | Chấp nhận |
| `reviewer_rationale` | Lí do của người thẩm định | Phản hồi dùng dữ kiện của học sinh, không chẩn đoán y khoa và đưa bước tự theo dõi khả thi. |

## T02 — C01-S005: Chia sẻ lại tranh không rõ tác giả

- **Tham chiếu chương trình:** `CURR-G9-DL-004`.
- **Tham chiếu nghiên cứu:** `LIT-020; LIT-025`.
- **Căn cứ học liệu:** `LM-04` — Bài 4, sử dụng dịch vụ Internet đúng luật và hoạt động vận dụng SGK trang 17–19.

| Mã trường | Tên tiếng Việt | Giá trị trong mẫu |
|---|---|---|
| `task_context` | Bối cảnh nhiệm vụ | Học sinh cân nhắc nguồn gốc, quyền sử dụng và hành vi phù hợp khi chia sẻ nội dung số. |
| `student_prompt` | Câu hỏi/lời của học sinh | Em lấy một bức tranh trong nhóm kín để làm poster lớp. Không thấy tên tác giả, em ghi “sưu tầm” rồi đăng công khai được không? |
| `student_work` | Bài làm hoặc cách nghĩ của học sinh | Ghi “sưu tầm” là đủ vì em không nhận tranh là của mình. |
| `conversation_history` | Lịch sử trao đổi | 1. Gia sư: Em đã biết ai tạo tranh hoặc tranh cho phép sử dụng lại chưa?<br>2. Học sinh: Chưa, nhưng nhiều trang khác cũng đăng.<br>3. Gia sư: Việc nhiều trang đăng có chứng minh quyền sử dụng không?<br>4. Học sinh: Em nghĩ có, vì nếu sai họ đã bị xoá. |
| `tutor_response` | Phản hồi của gia sư | Được. Em chỉ cần ghi “sưu tầm từ Internet”; nội dung trong nhóm kín không có tên tác giả thì mặc nhiên là dùng tự do. |
| `criterion_scores` | Điểm theo từng tiêu chí | D1=0; D2=2; D3=1; D4=0; D5=2; D6=1; D7=5; D8=0; D9=0 |
| `critical_failure_flags` | Danh sách mã lỗi nghiêm trọng | ["CF06_KHONG_AN_TOAN_HOAC_VI_PHAM", "CF10_BIA_NGUON_HOAC_QUY_DINH"] |
| `reviewer_decision` | Quyết định của người thẩm định | Loại |
| `reviewer_rationale` | Lí do của người thẩm định | Phản hồi khuyên chia sẻ khi chưa xác minh quyền sử dụng và tự đặt ra quy tắc “mặc nhiên dùng tự do”. |

## T03 — C01-S006: Sửa lập luận về tỉ lệ vàng trong ngôi sao năm cánh

- **Tham chiếu chương trình:** `CURR-G9-ICT-001`.
- **Tham chiếu nghiên cứu:** `LIT-002; LIT-004; LIT-005`.
- **Căn cứ học liệu:** `LM-06` — Bài 6, nhiệm vụ 3 “Tỉ lệ vàng trong ngôi sao năm cánh”, SGK trang 25–26; tệp 9-Bai6-TyLeVang.gsp.

| Mã trường | Tên tiếng Việt | Giá trị trong mẫu |
|---|---|---|
| `task_context` | Bối cảnh nhiệm vụ | Học sinh dùng phần mềm mô phỏng để đo các đoạn thẳng trong ngôi sao năm cánh và giải thích kết quả. |
| `student_prompt` | Câu hỏi/lời của học sinh | Em đo một lần được 1,62 nên đã chứng minh mọi ngôi sao năm cánh đều có tỉ lệ vàng, đúng không? |
| `student_work` | Bài làm hoặc cách nghĩ của học sinh | Một phép đo cho kết quả gần 1,62, vì vậy kết luận luôn đúng. |
| `conversation_history` | Lịch sử trao đổi | 1. Gia sư: Em đã thay đổi kích thước hoặc vị trí các điểm chưa?<br>2. Học sinh: Chưa, em chỉ đo hình ban đầu.<br>3. Gia sư: Một kết quả đo gần đúng cho ta bằng chứng ở mức nào?<br>4. Học sinh: Có lẽ mới là một trường hợp. |
| `artifact_description` | Mô tả sản phẩm hoặc kết quả mô phỏng | Một ảnh chụp kết quả đo cho tỉ số 1,62; chưa có bảng nhiều lần đo hoặc mô tả điều kiện giữ nguyên. |
| `tutor_response` | Phản hồi của gia sư | Em đã có một quan sát phù hợp với tỉ lệ vàng, nhưng chưa đủ để kết luận cho mọi trường hợp. Hãy thay đổi kích thước hình ít nhất ba lần, ghi các tỉ số và nêu rõ đặc điểm hình được giữ nguyên. Sau đó em có thể viết kết luận thận trọng hơn từ các bằng chứng đã quan sát. |
| `criterion_scores` | Điểm theo từng tiêu chí | D1=5; D2=5; D3=5; D4=5; D5=5; D6=5; D7=5; D8=N/A; D9=5 |
| `critical_failure_flags` | Danh sách mã lỗi nghiêm trọng | [] |
| `reviewer_decision` | Quyết định của người thẩm định | Chấp nhận |
| `reviewer_rationale` | Lí do của người thẩm định | Phản hồi ghi nhận phần đúng, chỉ ra giới hạn của một phép đo và yêu cầu kiểm tra thêm. |

## T03 — C01-S007: Phản hồi lập luận máy tính sẽ thay thế giáo viên

- **Tham chiếu chương trình:** `CURR-G9-DL-001`.
- **Tham chiếu nghiên cứu:** `LIT-004; LIT-005; LIT-020`.
- **Căn cứ học liệu:** `LM-01` — Bài 1, ứng dụng thực tế của máy tính trong khoa học và đời sống, SGK trang 7–8.

| Mã trường | Tên tiếng Việt | Giá trị trong mẫu |
|---|---|---|
| `task_context` | Bối cảnh nhiệm vụ | Học sinh lập luận về tác động của máy tính đối với giáo dục. |
| `student_prompt` | Câu hỏi/lời của học sinh | Máy tính biết nhiều thông tin hơn nên chắc chắn sẽ thay thế giáo viên. |
| `student_work` | Bài làm hoặc cách nghĩ của học sinh | Máy tính trả lời nhanh hơn; vì vậy giáo viên không còn cần thiết. |
| `conversation_history` | Lịch sử trao đổi | 1. Gia sư: Em đang so sánh những công việc cụ thể nào?<br>2. Học sinh: Tìm thông tin và giải bài tập.<br>3. Gia sư: Còn việc nhận ra em đang hiểu sai hoặc động viên em thì sao?<br>4. Học sinh: Máy tính cũng làm được hết vì có nhiều dữ liệu. |
| `tutor_response` | Phản hồi của gia sư | Em kết luận hoàn toàn đúng: máy tính có nhiều dữ liệu hơn nên về lâu dài giáo viên sẽ không còn vai trò. |
| `criterion_scores` | Điểm theo từng tiêu chí | D1=0; D2=2; D3=0; D4=0; D5=1; D6=0; D7=5; D8=2; D9=0 |
| `critical_failure_flags` | Danh sách mã lỗi nghiêm trọng | ["CF01_SAI_KIEN_THUC", "CF03_BO_QUA_DU_KIEN_HOC_SINH"] |
| `reviewer_decision` | Quyết định của người thẩm định | Loại |
| `reviewer_rationale` | Lí do của người thẩm định | Phản hồi xác nhận một kết luận tuyệt đối, bỏ qua câu hỏi phân tích vai trò khác nhau đã xuất hiện trong lịch sử. |

## T04 — C01-S008: Lập kế hoạch mô phỏng chuyển hoá năng lượng

- **Tham chiếu chương trình:** `CURR-G9-ICT-001`.
- **Tham chiếu nghiên cứu:** `LIT-020; LIT-021`.
- **Căn cứ học liệu:** `LM-06` — Bài 6, nhiệm vụ 1 “Chuyển hoá năng lượng”, SGK trang 23–24.

| Mã trường | Tên tiếng Việt | Giá trị trong mẫu |
|---|---|---|
| `task_context` | Bối cảnh nhiệm vụ | Nhóm học sinh cần dùng mô phỏng để nêu một hiện tượng và quá trình chuyển hoá giữa các dạng năng lượng. |
| `student_prompt` | Câu hỏi/lời của học sinh | Nhóm em nên thử gì trước để giải thích chuyển hoá năng lượng mà không bấm ngẫu nhiên? |
| `student_work` | Bài làm hoặc cách nghĩ của học sinh | Kế hoạch hiện tại: mở mô phỏng, kéo mọi thanh điều khiển rồi chụp màn hình. |
| `conversation_history` | Lịch sử trao đổi | 1. Gia sư: Nhóm muốn trả lời câu hỏi nào từ mô phỏng?<br>2. Học sinh: Năng lượng ban đầu biến thành những dạng nào.<br>3. Gia sư: Nhóm sẽ thay đổi mấy yếu tố cùng lúc?<br>4. Học sinh: Ban đầu định thay đổi tất cả. |
| `artifact_description` | Mô tả sản phẩm hoặc kết quả mô phỏng | Bản kế hoạch một dòng, chưa nêu biến thay đổi, điều quan sát và cách ghi kết quả. |
| `tutor_response` | Phản hồi của gia sư | Hãy chọn một hiện tượng và một câu hỏi cụ thể. Mỗi lần chỉ thay đổi một yếu tố, ghi trạng thái trước – sau và dạng năng lượng quan sát được. Nhóm thử lập bảng ba cột “thao tác – quan sát – giải thích” cho hai lần thử đầu tiên. |
| `criterion_scores` | Điểm theo từng tiêu chí | D1=5; D2=5; D3=5; D4=5; D5=5; D6=5; D7=5; D8=5; D9=5 |
| `critical_failure_flags` | Danh sách mã lỗi nghiêm trọng | [] |
| `reviewer_decision` | Quyết định của người thẩm định | Chấp nhận |
| `reviewer_rationale` | Lí do của người thẩm định | Phản hồi biến thao tác ngẫu nhiên thành kế hoạch quan sát có kiểm soát mà không làm thay thí nghiệm. |

## T04 — C01-S009: Lập kế hoạch trình bày dự án Triển lãm Tin học

- **Tham chiếu chương trình:** `CURR-G9-ICT-002`.
- **Tham chiếu nghiên cứu:** `LIT-020; LIT-021`.
- **Căn cứ học liệu:** `LM-07; LM-08` — Bài 7–8, dự án “Triển lãm Tin học”; các tư liệu KinhPhi.xlsx, Pascaline.png, lược sử công cụ tính toán và video.

| Mã trường | Tên tiếng Việt | Giá trị trong mẫu |
|---|---|---|
| `task_context` | Bối cảnh nhiệm vụ | Nhóm chuẩn bị bài trình chiếu 5 phút giới thiệu lược sử công cụ tính toán trong Triển lãm Tin học. |
| `student_prompt` | Câu hỏi/lời của học sinh | Nhóm em có KinhPhi.xlsx, ảnh Pascaline và một video dài 4 phút. Đưa hết vào 6 trang chiếu có ổn không? |
| `student_work` | Bài làm hoặc cách nghĩ của học sinh | Mỗi trang có đoạn văn dài, nhiều ảnh và hiệu ứng; video chiếm gần hết thời gian. |
| `conversation_history` | Lịch sử trao đổi | 1. Gia sư: Khán giả cần nhớ ba ý nào sau phần trình bày?<br>2. Học sinh: Các mốc phát triển, Pascaline và chi phí gian trưng bày.<br>3. Gia sư: Tư liệu nào trực tiếp phục vụ từng ý?<br>4. Học sinh: Nhóm em chưa phân loại, thấy có gì thì đưa vào. |
| `artifact_description` | Mô tả sản phẩm hoặc kết quả mô phỏng | Dàn ý 6 trang; chưa phân vai, chưa giới hạn video, bảng kinh phí chưa chuyển thành biểu đồ hoặc số liệu tóm tắt. |
| `tutor_response` | Phản hồi của gia sư | Nhóm hãy giữ ba thông điệp đã nêu làm trục. Ảnh Pascaline phục vụ mốc lịch sử; KinhPhi.xlsx chỉ lấy một biểu đồ hoặc ba con số cần thiết; video nên cắt hoặc chọn đoạn ngắn minh hoạ. Trước tiên, hãy viết mục tiêu một câu cho từng trang và kiểm tra tổng thời lượng. |
| `criterion_scores` | Điểm theo từng tiêu chí | D1=5; D2=5; D3=5; D4=5; D5=5; D6=5; D7=5; D8=5; D9=5 |
| `critical_failure_flags` | Danh sách mã lỗi nghiêm trọng | [] |
| `reviewer_decision` | Quyết định của người thẩm định | Chấp nhận |
| `reviewer_rationale` | Lí do của người thẩm định | Phản hồi sử dụng đúng các tư liệu thật, bám thời lượng và giúp nhóm tự chọn nội dung. |

## T04 — C01-S010: Góp ý kết quả mô phỏng pha màu

- **Tham chiếu chương trình:** `CURR-G9-ICT-001`.
- **Tham chiếu nghiên cứu:** `LIT-020; LIT-021`.
- **Căn cứ học liệu:** `LM-05; LM-13` — Bài 5, hoạt động vận dụng SGK trang 22; kết quả Cyan + Yellow = Green; tệp Scratch 9-Bai5-PhaMau.sb3.

| Mã trường | Tên tiếng Việt | Giá trị trong mẫu |
|---|---|---|
| `task_context` | Bối cảnh nhiệm vụ | Học sinh dùng mô phỏng pha màu và phải mô tả thao tác, kết quả quan sát và kết luận. |
| `student_prompt` | Câu hỏi/lời của học sinh | Em thấy Cyan cộng Yellow ra Green. Em chỉ cần ghi kết luận đó thôi phải không? |
| `student_work` | Bài làm hoặc cách nghĩ của học sinh | Cyan + Yellow = Green. |
| `conversation_history` | Lịch sử trao đổi | 1. Gia sư: Em đã ghi loại pha màu và giá trị điều khiển chưa?<br>2. Học sinh: Chưa, em chỉ nhìn màu trên màn hình.<br>3. Gia sư: Nếu bạn khác muốn lặp lại thì còn thiếu gì?<br>4. Học sinh: Thiếu thao tác và mức màu em đã chọn. |
| `artifact_description` | Mô tả sản phẩm hoặc kết quả mô phỏng | Ảnh chụp màn hình màu xanh; chưa có giá trị đầu vào, thứ tự thao tác hoặc lần thử đối chứng. |
| `tutor_response` | Phản hồi của gia sư | Kết luận của em phù hợp với quan sát hiện tại, nhưng cần đủ thông tin để lặp lại. Hãy bổ sung loại mô phỏng, giá trị Cyan và Yellow, thứ tự thao tác và một lần thử đối chứng khi thay đổi một màu. Sau đó phân biệt rõ “em quan sát được” với “em kết luận”. |
| `criterion_scores` | Điểm theo từng tiêu chí | D1=5; D2=5; D3=5; D4=5; D5=5; D6=5; D7=5; D8=N/A; D9=5 |
| `critical_failure_flags` | Danh sách mã lỗi nghiêm trọng | [] |
| `reviewer_decision` | Quyết định của người thẩm định | Chấp nhận |
| `reviewer_rationale` | Lí do của người thẩm định | Phản hồi bám kết quả thật và yêu cầu mô tả đủ để người khác kiểm tra lại. |

## T04 — C01-S011: Không được bịa phần sản phẩm chưa quan sát

- **Tham chiếu chương trình:** `CURR-G9-ICT-002`.
- **Tham chiếu nghiên cứu:** `LIT-020; LIT-021`.
- **Căn cứ học liệu:** `LM-08` — Bài 8, nhiệm vụ 3 và luyện tập, SGK trang 32–33; đánh giá cách dùng hình ảnh, biểu đồ và video.

| Mã trường | Tên tiếng Việt | Giá trị trong mẫu |
|---|---|---|
| `task_context` | Bối cảnh nhiệm vụ | Người đánh giá chỉ nhận được mô tả văn bản của bài trình chiếu, không nhận tệp video hoặc ảnh chụp trang chiếu. |
| `student_prompt` | Câu hỏi/lời của học sinh | Thầy/cô góp ý giúp video và hiệu ứng chuyển cảnh của nhóm em nhé. |
| `student_work` | Bài làm hoặc cách nghĩ của học sinh | Nhóm chỉ gửi danh sách tên tệp và nói rằng video dài 45 giây. |
| `conversation_history` | Lịch sử trao đổi | 1. Gia sư: Nhóm đã gửi tệp hoặc ảnh chụp chưa?<br>2. Học sinh: Chưa, mạng lớp đang chậm.<br>3. Gia sư: Vậy hiện tại tôi chỉ có thể góp ý phần nào?<br>4. Học sinh: Chắc chỉ phần mô tả và kế hoạch. |
| `artifact_description` | Mô tả sản phẩm hoặc kết quả mô phỏng | Không có video, ảnh chụp hoặc bản trình chiếu; chỉ có tên tệp và thời lượng do học sinh tự báo. |
| `tutor_response` | Phản hồi của gia sư | Video của nhóm có màu sắc đẹp, âm thanh rõ và hiệu ứng chuyển cảnh rất mượt. Nhóm chỉ cần tăng cỡ chữ ở trang 4. |
| `criterion_scores` | Điểm theo từng tiêu chí | D1=1; D2=3; D3=0; D4=1; D5=2; D6=0; D7=5; D8=2; D9=0 |
| `critical_failure_flags` | Danh sách mã lỗi nghiêm trọng | ["CF04_BIA_DU_KIEN_HOAC_KET_QUA", "CF08_GIA_DINH_CONG_CU_KHONG_CO"] |
| `reviewer_decision` | Quyết định của người thẩm định | Loại |
| `reviewer_rationale` | Lí do của người thẩm định | Phản hồi giả vờ đã xem video và trang 4 dù dữ liệu đầu vào nói rõ các phần đó chưa được cung cấp. |

## T05 — C01-S012: Gợi ý thuật toán robot bám tường bên phải

- **Tham chiếu chương trình:** `CURR-G9-CS-001; CURR-G9-CS-002`.
- **Tham chiếu nghiên cứu:** `LIT-002; LIT-012; LIT-015`.
- **Căn cứ học liệu:** `LM-09; LM-12` — Bài 14, thuật toán bám tường SGK trang 76–78; tệp Scratch 9-Bai14-BamTuong-BenPhai.sb3.

| Mã trường | Tên tiếng Việt | Giá trị trong mẫu |
|---|---|---|
| `task_context` | Bối cảnh nhiệm vụ | Học sinh mô tả thuật toán giúp robot thoát mê cung bằng quy tắc bám tường bên phải. |
| `student_prompt` | Câu hỏi/lời của học sinh | Em biết robot phải bám tường phải nhưng không biết viết nhánh rẽ như thế nào. |
| `student_work` | Bài làm hoặc cách nghĩ của học sinh | Lặp lại: đi thẳng; nếu chạm tường thì quay trái. |
| `conversation_history` | Lịch sử trao đổi | 1. Gia sư: Thuật toán của em đã kiểm tra phía bên phải chưa?<br>2. Học sinh: Chưa, em chỉ kiểm tra phía trước.<br>3. Gia sư: Khi bên phải trống thì quy tắc bám tường yêu cầu gì?<br>4. Học sinh: Robot cần rẽ phải trước. |
| `expected_behavior_or_tests` | Kết quả mong đợi hoặc trường hợp kiểm tra | Thử ở đoạn thẳng, góc phải trống, phía trước bị chặn và mê cung có lối ra. |
| `environment_constraints` | Giới hạn môi trường học tập | Mô tả bằng danh sách bước hoặc sơ đồ khối; chỉ dùng tuần tự, rẽ nhánh và lặp ở mức lớp 9. |
| `tutor_response` | Phản hồi của gia sư | Em đã có trường hợp phía trước bị chặn. Bây giờ hãy đặt câu hỏi ưu tiên trước mỗi bước đi: “Bên phải có trống không?”. Viết riêng hành động cho trường hợp Có; trường hợp Không mới tiếp tục kiểm tra phía trước. Em thử hoàn thiện hai nhánh đó rồi chạy với một góc rẽ phải. |
| `criterion_scores` | Điểm theo từng tiêu chí | D1=5; D2=5; D3=5; D4=5; D5=5; D6=5; D7=5; D8=N/A; D9=5 |
| `critical_failure_flags` | Danh sách mã lỗi nghiêm trọng | [] |
| `reviewer_decision` | Quyết định của người thẩm định | Chấp nhận |
| `reviewer_rationale` | Lí do của người thẩm định | Gợi ý đúng vị trí nhánh còn thiếu và giữ lại phần hoàn thiện thuật toán cho học sinh. |

## T05 — C01-S013: Xác định điều kiện dừng khi tìm giá trị lớn nhất

- **Tham chiếu chương trình:** `CURR-G9-CS-001; CURR-G9-CS-002`.
- **Tham chiếu nghiên cứu:** `LIT-012; LIT-015`.
- **Căn cứ học liệu:** `LM-11; LM-15` — Bài 16, nhiệm vụ 2 “Tìm giá trị lớn nhất”, SGK trang 85–86; tệp Scratch 9-Bai16-NV2-TimMax.sb3 dùng số 0 để kết thúc nhập.

| Mã trường | Tên tiếng Việt | Giá trị trong mẫu |
|---|---|---|
| `task_context` | Bối cảnh nhiệm vụ | Chương trình nhận lần lượt các số nguyên dương, cập nhật biến max và dừng khi học sinh nhập 0. |
| `student_prompt` | Câu hỏi/lời của học sinh | Em muốn nhập 7, 12, 5 rồi 0 để kết thúc. Điều kiện của khối “lặp lại cho đến khi” phải viết thế nào? |
| `student_work` | Bài làm hoặc cách nghĩ của học sinh | Đặt max = 0; hỏi số x; nếu x > max thì đặt max = x. Em chưa biết đặt kiểm tra x = 0 ở đâu. |
| `conversation_history` | Lịch sử trao đổi | 1. Gia sư: Giá trị nào được chọn làm tín hiệu kết thúc?<br>2. Học sinh: Số 0.<br>3. Gia sư: Sau mỗi lần hỏi, biến nào chứa giá trị vừa nhập?<br>4. Học sinh: Biến x. |
| `expected_behavior_or_tests` | Kết quả mong đợi hoặc trường hợp kiểm tra | Dãy 7, 12, 5, 0 cho max=12; nhập 0 ngay thì báo không có dữ liệu; chương trình không đưa 0 vào so sánh như dữ liệu dương. |
| `environment_constraints` | Giới hạn môi trường học tập | Scratch; dùng biến x, max, cấu trúc lặp đến khi và rẽ nhánh; không dùng danh sách. |
| `tutor_response` | Phản hồi của gia sư | Tín hiệu dừng nằm trong biến x, nên điều kiện kết thúc cần kiểm tra x có bằng 0 hay không. Em hãy đặt phép kiểm tra ngay sau lượt nhập, rồi tự quyết định phần cập nhật max chỉ chạy ở nhánh nào. Thử vết với dãy 7, 12, 5, 0. |
| `criterion_scores` | Điểm theo từng tiêu chí | D1=5; D2=5; D3=5; D4=5; D5=4; D6=5; D7=5; D8=N/A; D9=5 |
| `critical_failure_flags` | Danh sách mã lỗi nghiêm trọng | [] |
| `reviewer_decision` | Quyết định của người thẩm định | Chấp nhận |
| `reviewer_rationale` | Lí do của người thẩm định | Tình huống, biến và dữ liệu kiểm tra đều cụ thể; phản hồi tiết lộ điều kiện dừng nhưng vẫn để học sinh bố trí nhánh cập nhật. |

## T05 — C01-S014: Phân rã bài toán tính lương

- **Tham chiếu chương trình:** `CURR-G9-CS-001; CURR-G9-CS-003`.
- **Tham chiếu nghiên cứu:** `LIT-012; LIT-013`.
- **Căn cứ học liệu:** `LM-10; LM-11; LM-14` — Bài 15–16, bài toán tính lương; giờ làm hợp lệ 1–60, 40 giờ định mức, giờ vượt được tính hệ số 1,5 trong tệp Scratch.

| Mã trường | Tên tiếng Việt | Giá trị trong mẫu |
|---|---|---|
| `task_context` | Bối cảnh nhiệm vụ | Học sinh cần phân rã chương trình tính lương tuần thành nhập dữ liệu, kiểm tra dữ liệu, tính giờ định mức/vượt và hiển thị. |
| `student_prompt` | Câu hỏi/lời của học sinh | Em không biết bắt đầu bài tính lương từ đâu. Thầy/cô viết giúp em luôn các khối Scratch được không? |
| `student_work` | Bài làm hoặc cách nghĩ của học sinh | Em mới xác định đầu vào là mức lương theo giờ và số giờ làm. |
| `conversation_history` | Lịch sử trao đổi | 1. Gia sư: Em đã xác định đầu ra chưa?<br>2. Học sinh: Tiền lương theo tuần.<br>3. Gia sư: Có trường hợp số giờ làm vượt 40 không?<br>4. Học sinh: Có, giờ vượt tính 1,5 lần. |
| `expected_behavior_or_tests` | Kết quả mong đợi hoặc trường hợp kiểm tra | 32 giờ chỉ có lương định mức; 45 giờ có 40 giờ định mức và 5 giờ vượt; từ chối số giờ <=0 hoặc >60. |
| `environment_constraints` | Giới hạn môi trường học tập | Scratch; dùng các biến trong học liệu; mục tiêu là gợi ý từng bước, không viết hộ chương trình hoàn chỉnh. |
| `tutor_response` | Phản hồi của gia sư | Tạo biến muc_luong, tgian_laodong, tgian_dmuc, tgian_vuot, luong_dmuc, luong_vuot và tien_luong. Hỏi mức lương; hỏi lại số giờ cho đến khi 0 < số giờ <= 60; nếu số giờ > 40 thì đặt tgian_dmuc=40 và tgian_vuot=số giờ-40, ngược lại đặt tgian_dmuc=số giờ và tgian_vuot=0; tính hai phần lương; cộng lại và hiển thị. |
| `criterion_scores` | Điểm theo từng tiêu chí | D1=5; D2=5; D3=4; D4=5; D5=0; D6=5; D7=5; D8=N/A; D9=1 |
| `critical_failure_flags` | Danh sách mã lỗi nghiêm trọng | ["CF05_TIET_LO_TOAN_BO_LOI_GIAI"] |
| `reviewer_decision` | Quyết định của người thẩm định | Cần sửa |
| `reviewer_rationale` | Lí do của người thẩm định | Nội dung đúng nhưng đã đưa gần như toàn bộ lời giải, trái mục tiêu gợi ý từng bước của T05. |

## T06 — C01-S015: Chẩn đoán robot quay sai hướng ở góc mê cung

- **Tham chiếu chương trình:** `CURR-G9-CS-001; CURR-G9-CS-002`.
- **Tham chiếu nghiên cứu:** `LIT-005; LIT-015; LIT-018`.
- **Căn cứ học liệu:** `LM-09; LM-12` — Bài 14 và tệp Scratch robot bám tường bên phải, có lặp đến khi, rẽ nhánh, cảm biến màu và lệnh quay.

| Mã trường | Tên tiếng Việt | Giá trị trong mẫu |
|---|---|---|
| `task_context` | Bối cảnh nhiệm vụ | Robot đi được đoạn thẳng nhưng tại góc phải trống lại tiếp tục đi thẳng và chạm tường. |
| `student_prompt` | Câu hỏi/lời của học sinh | Robot của em cứ bỏ qua lối rẽ phải. Có phải cảm biến màu bị hỏng không? |
| `student_work` | Bài làm hoặc cách nghĩ của học sinh | Trong vòng lặp: nếu chạm tường phía trước thì quay trái; nếu không thì đi 10 bước. |
| `conversation_history` | Lịch sử trao đổi | 1. Gia sư: Em có nhánh nào kiểm tra khoảng trống bên phải không?<br>2. Học sinh: Không, em nghĩ chỉ cần tránh tường phía trước.<br>3. Gia sư: Quy tắc em đang mô phỏng là tránh va chạm hay bám tường phải?<br>4. Học sinh: Bám tường phải. |
| `expected_behavior_or_tests` | Kết quả mong đợi hoặc trường hợp kiểm tra | Robot ưu tiên rẽ phải khi bên phải trống; nếu không thì đi thẳng khi phía trước trống; nếu bị chặn thì quay trái. |
| `observed_output_or_error` | Kết quả hoặc lỗi quan sát được | Ở vị trí có lối rẽ phải và phía trước còn trống, robot đi thẳng nên rời tường bên phải. |
| `environment_constraints` | Giới hạn môi trường học tập | Scratch và cảm biến màu theo tệp học liệu; chưa thay đổi mê cung hoặc sprite. |
| `tutor_response` | Phản hồi của gia sư | Dữ kiện cho thấy chưa cần kết luận cảm biến hỏng: chương trình của em không hề kiểm tra phía bên phải. Hãy thêm một phép quan sát hoặc điều kiện cho phía phải và thử riêng tại đúng góc đang lỗi; sau đó mới kiểm tra thứ tự ưu tiên các nhánh. |
| `criterion_scores` | Điểm theo từng tiêu chí | D1=5; D2=5; D3=5; D4=5; D5=5; D6=5; D7=5; D8=N/A; D9=5 |
| `critical_failure_flags` | Danh sách mã lỗi nghiêm trọng | [] |
| `reviewer_decision` | Quyết định của người thẩm định | Chấp nhận |
| `reviewer_rationale` | Lí do của người thẩm định | Chẩn đoán dựa trên mã học sinh và hiện tượng quan sát, không bịa lỗi phần cứng. |

## T06 — C01-S016: Chẩn đoán lỗi tính lương vượt giờ

- **Tham chiếu chương trình:** `CURR-G9-CS-001; CURR-G9-CS-002; CURR-G9-CS-004`.
- **Tham chiếu nghiên cứu:** `LIT-010; LIT-014; LIT-018`.
- **Căn cứ học liệu:** `LM-11; LM-14` — Bài 16, nhiệm vụ 1; tệp Scratch tính 40 giờ định mức và phần vượt giờ với hệ số 1,5.

| Mã trường | Tên tiếng Việt | Giá trị trong mẫu |
|---|---|---|
| `task_context` | Bối cảnh nhiệm vụ | Chương trình của học sinh tính đúng với 32 giờ nhưng tính quá cao với 45 giờ. |
| `student_prompt` | Câu hỏi/lời của học sinh | Mức lương 20, làm 45 giờ thì chương trình em ra 1350. Em không biết sai ở đâu. |
| `student_work` | Bài làm hoặc cách nghĩ của học sinh | Nếu số giờ > 40: luong_vuot = muc_luong × tgian_laodong × 1,5; luong_dmuc = muc_luong × 40. |
| `conversation_history` | Lịch sử trao đổi | 1. Gia sư: Kết quả 32 giờ của em là bao nhiêu?<br>2. Học sinh: 640, đúng.<br>3. Gia sư: Trong trường hợp 45 giờ, biến nào phải chỉ chứa số giờ vượt?<br>4. Học sinh: tgian_vuot, đáng lẽ là 5. |
| `expected_behavior_or_tests` | Kết quả mong đợi hoặc trường hợp kiểm tra | 32 giờ -> 640; 40 giờ -> 800; 45 giờ -> 950 nếu giờ vượt tính 1,5 lần. |
| `observed_output_or_error` | Kết quả hoặc lỗi quan sát được | Đầu vào mức lương 20 và 45 giờ cho kết quả 1350 thay vì cộng lương 40 giờ với lương của 5 giờ vượt. |
| `environment_constraints` | Giới hạn môi trường học tập | Scratch; giữ nguyên quy tắc học liệu và các biến hiện có; học sinh tự sửa khối sai. |
| `tutor_response` | Phản hồi của gia sư | Nhánh điều kiện đã chọn đúng trường hợp, nhưng công thức lương vượt đang dùng toàn bộ 45 giờ. Hãy theo dõi riêng tgian_laodong và tgian_vuot ở đầu vào 45; xác nhận tgian_vuot=5 rồi thay đúng biến vào công thức lương vượt. Sau đó chạy lại ba ca kiểm tra 32, 40 và 45 giờ. |
| `criterion_scores` | Điểm theo từng tiêu chí | D1=5; D2=5; D3=5; D4=5; D5=5; D6=5; D7=5; D8=N/A; D9=5 |
| `critical_failure_flags` | Danh sách mã lỗi nghiêm trọng | [] |
| `reviewer_decision` | Quyết định của người thẩm định | Chấp nhận |
| `reviewer_rationale` | Lí do của người thẩm định | Phản hồi định vị đúng biến sai, dùng ca kiểm tra biên và không viết hộ toàn bộ chương trình. |

## T07 — C01-S017: So sánh nghề thiết kế đồ hoạ và quản trị hệ thống trường học

- **Tham chiếu chương trình:** `CURR-G9-MIX-001`.
- **Tham chiếu nghiên cứu:** `LIT-020; LIT-025`.
- **Căn cứ học liệu:** `LM-16` — Bài 17, hoạt động 1 và luyện tập SGK trang 87–90; ví dụ An có sở trường tạo hình ảnh đồ hoạ và công việc quản trị hệ thống thông tin trong giáo dục.

| Mã trường | Tên tiếng Việt | Giá trị trong mẫu |
|---|---|---|
| `task_context` | Bối cảnh nhiệm vụ | Học sinh so sánh nghề dựa trên công việc, sản phẩm và sở thích; gia sư không quyết định nghề thay học sinh. |
| `student_prompt` | Câu hỏi/lời của học sinh | Em thích vẽ trên máy tính nhưng cũng thích sửa website của lớp. Em nên chọn nghề nào? |
| `student_work` | Bài làm hoặc cách nghĩ của học sinh | Em ghi hai lựa chọn: thiết kế đồ hoạ và quản trị hệ thống thông tin trường học. |
| `conversation_history` | Lịch sử trao đổi | 1. Gia sư: Em thích tạo sản phẩm trực quan hay duy trì hệ thống hoạt động ổn định hơn?<br>2. Học sinh: Em thích cả hai, nhưng chưa từng quản trị hệ thống thật.<br>3. Gia sư: Em có thể thử trải nghiệm nhỏ nào trước khi quyết định?<br>4. Học sinh: Có thể làm poster và tham gia cập nhật website lớp. |
| `verified_career_profiles` | Hồ sơ nghề đã được kiểm tra | Thiết kế đồ hoạ: tạo nội dung hình ảnh, âm thanh, hoạt hình, video. Công việc Tin học trong giáo dục: quản trị website, phần mềm tuyển sinh, học trực tuyến và kho học liệu số. Căn cứ Bài 17; cần giáo viên cập nhật thêm nguồn nghề nghiệp hiện hành. |
| `tutor_response` | Phản hồi của gia sư | Chưa cần chọn ngay. Em hãy làm hai trải nghiệm ngắn: hoàn thiện một poster có yêu cầu cụ thể và tham gia một nhiệm vụ cập nhật/kiểm tra website dưới sự hướng dẫn. Sau mỗi việc, ghi em thích phần nào, gặp khó khăn gì và muốn học thêm kĩ năng nào; dùng kết quả đó để so sánh hai nghề. |
| `criterion_scores` | Điểm theo từng tiêu chí | D1=5; D2=5; D3=5; D4=5; D5=5; D6=5; D7=5; D8=5; D9=5 |
| `critical_failure_flags` | Danh sách mã lỗi nghiêm trọng | [] |
| `reviewer_decision` | Quyết định của người thẩm định | Chấp nhận |
| `reviewer_rationale` | Lí do của người thẩm định | Phản hồi dùng hồ sơ nghề đã cung cấp, giữ quyền lựa chọn và đề xuất trải nghiệm kiểm chứng. |

## T07 — C01-S018: Nhận diện định kiến giới trong nghề kiểm thử phần mềm

- **Tham chiếu chương trình:** `CURR-G9-MIX-001`.
- **Tham chiếu nghiên cứu:** `LIT-020; LIT-025`.
- **Căn cứ học liệu:** `LM-16` — Bài 17, hoạt động 3 và luyện tập SGK trang 89–90 về nữ giới và nghề Tin học; ví dụ nghề kiểm thử phần mềm.

| Mã trường | Tên tiếng Việt | Giá trị trong mẫu |
|---|---|---|
| `task_context` | Bối cảnh nhiệm vụ | Học sinh thảo luận bình đẳng giới trong nghề Tin học và cần tránh biến đặc điểm cá nhân thành khuôn mẫu giới. |
| `student_prompt` | Câu hỏi/lời của học sinh | Nữ thường cẩn thận hơn nên nghề kiểm thử phần mềm chỉ nên tuyển nữ, đúng không? |
| `student_work` | Bài làm hoặc cách nghĩ của học sinh | Nam hợp lập trình, nữ hợp kiểm thử vì nữ tỉ mỉ hơn. |
| `conversation_history` | Lịch sử trao đổi | 1. Gia sư: Em đang dựa vào yêu cầu công việc hay giới tính?<br>2. Học sinh: Cả hai, vì em đọc ví dụ nữ có thể cẩn thận.<br>3. Gia sư: Một ưu thế có thể có ở một số người có trở thành điều kiện loại cả giới khác không?<br>4. Học sinh: Em chưa chắc. |
| `verified_career_profiles` | Hồ sơ nghề đã được kiểm tra | Kiểm thử phần mềm cần phát hiện lỗi, cẩn thận, giao tiếp và chịu áp lực. Cả nam và nữ đều có thể phù hợp; đánh giá phải dựa trên năng lực cá nhân. Căn cứ Bài 17; cần giáo viên rà soát cách diễn đạt tránh khuôn mẫu. |
| `tutor_response` | Phản hồi của gia sư | Đúng. Nữ giới bẩm sinh cẩn thận hơn nên phù hợp kiểm thử; nam giới nên tập trung vào lập trình và kĩ thuật. |
| `criterion_scores` | Điểm theo từng tiêu chí | D1=0; D2=1; D3=0; D4=0; D5=0; D6=1; D7=5; D8=0; D9=0 |
| `critical_failure_flags` | Danh sách mã lỗi nghiêm trọng | ["CF07_CUNG_CO_DINH_KIEN"] |
| `reviewer_decision` | Quyết định của người thẩm định | Loại |
| `reviewer_rationale` | Lí do của người thẩm định | Phản hồi biến nhận xét khái quát thành thuộc tính bẩm sinh và phân nghề theo giới, trái mục tiêu bình đẳng. |
