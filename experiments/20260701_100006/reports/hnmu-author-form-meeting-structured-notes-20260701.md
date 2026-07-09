# Ghi chú cuộc họp HNMU về phiếu tác giả — bản cấu trúc hóa

Ngày cấu trúc hóa: 03/07/2026
Cuộc họp được ghi nhận: 01/07/2026, 10:00
Experiment: `20260701_100006`
Nguồn ghi chú: phần `Update plan (01-07-2026)` trong `user_diary.md`

## 1. Mục đích của tài liệu này

Tài liệu này chỉ làm một việc: cấu trúc lại ghi chú cuộc họp ngày 01/07/2026 cho thống nhất, dễ đọc và dễ xử lý tiếp.

Tài liệu này chưa phải là bản phản biện đầy đủ, chưa phải kế hoạch triển khai và chưa thay thế ghi chú gốc trong `user_diary.md`.

Các bước xử lý sâu hơn sẽ cần làm riêng sau tài liệu này:

- kiểm tra file phiếu tác giả đã chốt;
- kiểm tra experiment `20260701_100006`;
- đối chiếu phiếu tác giả với task, rubric, mã lỗi và học liệu;
- chuẩn hóa nhóm chủ đề Tin học lớp 6–9;
- đánh giá phương án thu thập dữ liệu qua web học sinh tương tác với gia sư AI.

## 2. Thành phần tham gia và mục tiêu cuộc họp

### 2.1. Thành phần tham gia

- UET:
  - người phụ trách dự án;
  - giáo sư hướng dẫn.
- HNMU:
  - các giáo viên chuyên môn tham gia xây dựng và thẩm định dữ liệu.

### 2.2. Mục tiêu chính của cuộc họp

Chốt các trường trong **phiếu tác giả** để giáo viên chuyên môn có thể dùng khi tạo dữ liệu benchmark.

Nói ngắn gọn: cuộc họp nhằm chuyển từ “khung benchmark sơ bộ” sang một biểu mẫu làm việc cụ thể hơn cho giáo viên.

## 3. Các mốc thời gian đã nêu


| Mốc       | Nội dung                                                                                              | Mức độ quan trọng | Ghi chú cần kiểm tra tiếp                                                                                                                                                                                                         |
| ---------- | ------------------------------------------------------------------------------------------------------ | --------------------: | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 15/07/2026 | Deadline nộp bài cho hội nghị KSE.                                                                 |          Cực kỳ cao | Người phụ trách dự án sẽ hỏi lại giáo sư để xác nhận mốc và kỳ vọng nộp bài. Trước khi có xác nhận cuối, vẫn cần coi đây là mốc rủi ro rất cao và đánh giá kỹ tính khả thi của bài báo, phần benchmark tối thiểu và phần kết quả có thể kịp tạo. |
| 15/07/2026 | Cần đạt một số lượng mẫu đủ lớn để đánh giá tiến độ và chứng minh tính khả thi. |              Rất cao | Ghi chú gốc nêu mục tiêu có thể khoảng 700 mẫu. Cần kiểm tra lại tính khả thi sau khi biết tốc độ làm mẫu thực tế, đặc biệt vì mốc này trùng với deadline KSE.                                          |
| 01/08/2026 | Mục tiêu kích thước benchmark đạt 1000 mẫu.                                                    |              Rất cao | Cần tách rõ “1000 mẫu thô”, “1000 mẫu đã được giáo viên chấm”, hay “1000 mẫu đủ điều kiện đưa vào bản phát hành”.                                                                                     |

## 4. Các quyết định đã chốt trong cuộc họp

### 4.1. Phiếu tác giả là biểu mẫu làm việc chính cho giáo viên

Phiếu tác giả được dùng để giáo viên chuyên môn xây dựng dữ liệu.

Thông tin nguồn được ghi trong nhật ký:

- File Google Sheets chính: [https://docs.google.com/spreadsheets/d/1hx-bmX1hNfdFImfoKlXztGKp9QGCcou1/edit?gid=453913985#gid=453913985](https://docs.google.com/spreadsheets/d/1hx-bmX1hNfdFImfoKlXztGKp9QGCcou1/edit?gid=453913985#gid=453913985)
- Bản gốc xuất phát từ sheet `phiếu tác giả` trong file `teacher_packet/review_form` của experiment `20260621_135515`, nhánh `feature/C01_P02_P03`.
- Người phụ trách dự án đã chỉnh nhẹ bản gốc và upload lên thư mục Drive: [https://drive.google.com/drive/folders/1h23ty1pE0sD10JpCqUIkfyuIifCd_USi?usp=sharing](https://drive.google.com/drive/folders/1h23ty1pE0sD10JpCqUIkfyuIifCd_USi?usp=sharing)
- Phiếu tác giả đã chốt cũng được đưa vào experiment mới có mã `20260701_100006`, theo link Drive: [https://drive.google.com/drive/folders/18k6oGkD4RJMhcKNjsVc178x2S2f6iur5?usp=sharing](https://drive.google.com/drive/folders/18k6oGkD4RJMhcKNjsVc178x2S2f6iur5?usp=sharing)

Việc cần xử lý sau:

- kiểm tra bản phiếu tác giả đang được coi là bản chốt;
- so sánh bản chốt với bản gốc từ `feature/C01_P02_P03`;
- phát hiện trường thiếu, trường trùng nghĩa, trường mâu thuẫn hoặc trường chưa có hướng dẫn điền rõ ràng;
- xác định trường nào do UET điền trước, trường nào do HNMU hoàn thiện.

### 4.2. Trường “mã task” do UET chuẩn bị trước

Trong phiếu tác giả có trường **mã task**.

Quyết định đã chốt:

- UET phải điền hoặc cung cấp trước trường này;
- giáo viên chuyên môn cần biết mã task trước khi hoàn thiện các trường còn lại.

Ý nghĩa thực tế:

- giáo viên không tự phát minh mã task;
- UET phải có danh sách task đủ rõ để giáo viên chọn hoặc được phân công;
- nếu mã task chưa ổn định, toàn bộ phiếu tác giả sẽ dễ bị lệch hoặc phải sửa lại nhiều.

### 4.3. Cấu trúc lịch sử trao đổi giữa học sinh và gia sư

Trường **lịch sử trao đổi giữa học sinh và gia sư** đã được thảo luận và chốt ở mức ban đầu.

Quy ước được ghi nhận:

- mỗi mẫu có thể có nhiều lượt hội thoại;
- trung bình có khoảng 4 lượt;
- tối thiểu 1 lượt;
- tối đa 5 lượt;
- mỗi lượt có trung bình khoảng 4 bước trao đổi;
- tối thiểu 1 bước;
- tối đa 5 bước.

Định nghĩa đang được ghi nhận:

- **Lượt hội thoại**: tương đương một phiên trao đổi ngắn giữa học sinh và gia sư.
- **Bước hội thoại**: một đơn vị trao đổi trong lượt hội thoại, theo luồng học sinh nói hoặc làm gì đó, sau đó gia sư phản hồi.

Điểm cần chốt lại để tránh nhập liệu không đồng nhất:

- Cần phân biệt rõ **bước đơn** và **cặp trao đổi**.
- Nếu một học sinh hỏi và một gia sư đáp được tính là 1 bước, thì “bước” thực chất là một cặp trao đổi.
- Nếu mỗi phát ngôn của học sinh hoặc gia sư được tính là 1 bước, thì một câu hỏi và một câu trả lời sẽ là 2 bước.

Đề xuất thuật ngữ để dùng thống nhất về sau:

- **Lượt hội thoại**: một phiên ngắn trong lịch sử trao đổi.
- **Cặp trao đổi**: một lần học sinh nêu vấn đề và gia sư phản hồi.
- **Phát ngôn**: một tin nhắn đơn lẻ của học sinh hoặc gia sư.

### 4.4. Gia sư cần dùng phương pháp giàn giáo trong hội thoại

Yêu cầu đối với phản hồi của gia sư:

- không chỉ đưa ngay đáp án cuối;
- cần kiểm tra kiến thức nền của học sinh;
- cần đặt câu hỏi dẫn dắt;
- cần tiếp nhận câu trả lời của học sinh;
- cần xác định vấn đề hoặc lỗ hổng kiến thức của học sinh;
- cần đưa ra hướng giải quyết phù hợp với vấn đề đã xác định.

Ràng buộc đã nêu:

- vì số bước hội thoại bị giới hạn, khi gần hoặc chạm giới hạn, gia sư cần đưa ra câu trả lời cuối cùng;
- câu trả lời cuối cùng có thể là đáp án cuối hoặc hướng dẫn đủ chi tiết để học sinh tự giải tiếp.

Điểm cần làm rõ trong phiếu tác giả:

- khi nào gia sư nên hỏi tiếp;
- khi nào gia sư nên kết luận;
- tiêu chí nào cho thấy một lịch sử hội thoại đã thể hiện đủ “giàn giáo”;
- nếu học sinh thiếu kiến thức nền lớp 6–8 thì gia sư cần xử lý thế nào.

### 4.5. Phạm vi kiến thức được chốt

Phạm vi kiến thức hiện tại:

- chỉ nằm trong miền Tin học lớp 9;
- có kết nối đến các tiền kiến thức liên quan ở lớp 6, lớp 7 và lớp 8.

Ý nghĩa thực tế:

- benchmark không mở rộng sang toàn bộ các môn học;
- benchmark không đánh giá mọi tình huống gia sư tổng quát;
- nhưng mẫu lớp 9 có thể cần căn cứ thêm học liệu lớp 6–8 nếu đó là tiền kiến thức cần thiết.

### 4.6. Học liệu chính hiện tại là sách giáo khoa trên trang tập huấn

Nguồn học liệu chính được ghi nhận:

- Trang tập huấn môn Tin học: [https://taphuan.nxbgd.vn/tap-huan?subjects=11](https://taphuan.nxbgd.vn/tap-huan?subjects=11)
- SGK Tin học 6: [https://taphuan.nxbgd.vn/tap-huan/doc-sach/sgk-tin-hoc-6.4699918592#page=5](https://taphuan.nxbgd.vn/tap-huan/doc-sach/sgk-tin-hoc-6.4699918592#page=5)
- SGK Tin học 7: [https://taphuan.nxbgd.vn/tap-huan/doc-sach/sgk-tin-hoc-7.4700056620#page=5](https://taphuan.nxbgd.vn/tap-huan/doc-sach/sgk-tin-hoc-7.4700056620#page=5)
- SGK Tin học 8: [https://taphuan.nxbgd.vn/tap-huan/doc-sach/sgk-tin-hoc-8.4700157933#page=5](https://taphuan.nxbgd.vn/tap-huan/doc-sach/sgk-tin-hoc-8.4700157933#page=5)
- SGK Tin học 9: [https://taphuan.nxbgd.vn/tap-huan/doc-sach/sgk-tin-hoc-9.4700233123#page=3](https://taphuan.nxbgd.vn/tap-huan/doc-sach/sgk-tin-hoc-9.4700233123#page=3)

Nhận định đã ghi:

- xuyên suốt Tin học THCS có khoảng 6–7 chủ đề;
- tên và số thứ tự chủ đề giữa các lớp không hoàn toàn đồng nhất;
- nội hàm của các chủ đề về cơ bản có thể quy về các nhóm chung.

Việc cần xử lý sau:

- đọc mục lục SGK lớp 6–9;
- lập nhóm chủ đề thống nhất;
- ghi rõ quan hệ giữa chủ đề lớp 9 và tiền kiến thức lớp 6–8;
- nhờ HNMU xác nhận nhóm chủ đề trước khi dùng làm căn cứ tạo mẫu.

## 5. Các nội dung đang cân nhắc, chưa chốt

### 5.1. Thu thập dữ liệu bằng web cho học sinh tương tác với gia sư AI

Ý tưởng được giáo sư đề xuất:

- tạo một web để học sinh tương tác trực tiếp với gia sư AI;
- gia sư AI có thể dùng các mô hình như ChatGPT, Claude, Gemini hoặc mô hình tương tự;
- thu thập hội thoại để tạo mẫu chưa có điểm rubric;
- đưa hội thoại vào các trường như:
  - yêu cầu của học sinh về kiến thức thuộc chủ đề;
  - bài làm của học sinh;
  - lịch sử trao đổi giữa học sinh và gia sư;
  - các trường liên quan khác trong phiếu tác giả;
- sau đó giáo viên HNMU chấm rubric và ghi các thông tin đánh giá bổ sung.

Lợi ích ban đầu:

- có thể thu thập dữ liệu nhanh hơn;
- có dữ liệu hội thoại tự nhiên hơn so với việc viết mẫu hoàn toàn thủ công;
- giúp kiểm tra sớm tính khả thi của mục tiêu số lượng mẫu lớn.

Rủi ro đã được ghi nhận:

- chi phí token cho mô hình;
- chi phí hosting web;
- nếu gia sư AI không truy xuất học liệu chuẩn thì dữ liệu dễ kém chất lượng;
- cần hệ thống quản lý học liệu đủ tốt để mô hình có căn cứ khi tương tác;
- nếu để mô hình tự trả lời không căn cứ, hội thoại có thể sai chương trình hoặc lệch nội dung.

Điểm cần phân tích tiếp:

- nên làm web đầy đủ hay công cụ nhập liệu tối giản trước;
- có cần học sinh thật tham gia ngay không, hay trước mắt dùng giáo viên/UET đóng vai học sinh;
- mô hình có được phép truy xuất học liệu theo mã hay chỉ dùng prompt cố định;
- dữ liệu thu được sẽ là dữ liệu thô, dữ liệu ứng viên hay dữ liệu chính thức;
- quy trình xin phép, ẩn danh và bảo vệ dữ liệu người học nếu có học sinh thật tham gia.

## 6. Các điểm có nguy cơ mâu thuẫn hoặc cần chốt lại

### 6.1. Deadline KSE và mục tiêu số lượng mẫu có thể đang quá căng

Người phụ trách dự án sẽ hỏi lại giáo sư để xác nhận chính xác kỳ vọng về deadline KSE và mức tối thiểu cần có để nộp bài. Trước khi có xác nhận cuối, cần tạm coi mốc **15/07/2026** là mốc rủi ro rất cao.

Điều này làm cho hai mục tiêu sau trở nên căng hơn nhiều:

- có đủ nội dung bài báo để nộp KSE trước hoặc trong ngày 15/07/2026;
- có đủ số lượng mẫu ban đầu để chứng minh tính khả thi của benchmark trước mốc này.

Mục tiêu 700 mẫu vào 15/07/2026 và 1000 mẫu vào 01/08/2026 vẫn có thể được dùng làm mốc tham vọng, nhưng cần tách rõ mức chất lượng của từng loại mẫu.

Cần chốt lại:

- mẫu được tính là mẫu thô hay mẫu đã được giáo viên chấm;
- mỗi mẫu cần bao nhiêu thời gian tạo và rà soát;
- bao nhiêu giáo viên HNMU thực sự tham gia;
- mỗi giáo viên có thể làm bao nhiêu mẫu mỗi ngày;
- chất lượng tối thiểu của mẫu ở mốc 15/07/2026 là gì;
- bài KSE cần có tối thiểu bao nhiêu mẫu đã chấm, bao nhiêu mẫu ứng viên, và bao nhiêu bằng chứng về quy trình tạo dữ liệu.

### 6.2. Có sự căng giữa cách làm top-down và cách làm bottom-up

Theo tư duy hệ thống đã nêu trong ghi chú ngày 26/06/2026, hướng làm chặt chẽ nên là **top-down**:

```text
task → rubric/mã lỗi nghiêm trọng → metadata của từng mẫu trong phiếu tác giả
```

Lý do: task là đơn vị đánh giá chính; rubric và mã lỗi nghiêm trọng phải phục vụ task; metadata của từng mẫu cần được thiết kế để giáo viên tạo được dữ liệu đúng theo task và rubric.

Tuy nhiên, trong cuộc họp gần nhất, giáo sư UET và giáo viên HNMU muốn đẩy tiến độ rất nhanh. Vì vậy, hướng làm thực tế đang chuyển tạm sang **bottom-up**:

```text
metadata trong phiếu tác giả → rubric/mã lỗi nghiêm trọng → task
```

Như vậy, việc trước mắt là soi kỹ các trường trong phiếu tác giả:

- trường nào đã ổn;
- trường nào còn mơ hồ;
- trường nào thiếu người chịu trách nhiệm điền;
- trường nào có nguy cơ ép ngược lại rubric hoặc task theo cách không hợp lý;
- trường nào cần đổi tên hoặc tách nhỏ để giáo viên dễ điền hơn.

Rủi ro vẫn còn:

- nếu đi từ metadata quá nhanh, task/rubric về sau có thể bị méo theo biểu mẫu hiện tại;
- nếu mã task thay đổi sau khi giáo viên đã nhập nhiều mẫu, dữ liệu sẽ cần sửa hàng loạt;
- nếu task định nghĩa chưa rõ, các giáo viên khác nhau có thể hiểu cùng một mã task theo nhiều cách.

Cách xử lý tạm thời:

1. Chấp nhận rà soát phiếu tác giả trước để phục vụ tiến độ.
2. Ghi nhãn rõ trường nào là “đã chốt tạm thời”, trường nào là “cần xác nhận lại sau khi có rubric/task”.
3. Sau khi thống nhất phiếu tác giả, chuyển ngay sang rubric/mã lỗi nghiêm trọng.
4. Sau rubric/mã lỗi nghiêm trọng, quay lại chốt task để tránh mất hoàn toàn tư duy hệ thống.

Trạng thái sau phản hồi ngày 04/07/2026: người phụ trách dự án đồng ý với cách xử lý tạm thời này.

### 6.3. Định nghĩa “lượt” và “bước” cần chính xác hơn

Người phụ trách dự án đã làm rõ cách hiểu hiện tại:

- **bước** là một **cặp trao đổi**;
- một cặp trao đổi gồm một lần học sinh nêu vấn đề, đặt câu hỏi hoặc đưa bài làm, và một lần gia sư phản hồi.

Vì vậy, trong tài liệu hướng dẫn cho giáo viên nên dùng thống nhất:

- **lượt hội thoại**: một phiên trao đổi ngắn;
- **bước/cặp trao đổi**: một lần học sinh đưa vấn đề và gia sư phản hồi;
- **phát ngôn**: một tin nhắn đơn lẻ của học sinh hoặc gia sư, nếu cần mô tả chi tiết hơn.

Điểm còn cần làm rõ:

- cách biểu diễn bước trong phiếu tác giả để giáo viên không phải tự đoán.

Các điểm đã được người phụ trách dự án làm rõ ngày 04/07/2026:

- nếu một học sinh cố gửi nhiều tin nhắn liên tiếp trong khi gia sư đang suy nghĩ hoặc đang trả lời, hệ thống nên có cơ chế chặn để học sinh không spam nhiều tin nhắn trong cùng một thời điểm;
- nếu gia sư chỉ đặt câu hỏi gợi mở và học sinh chưa trả lời, đồng thời hội thoại chưa chạm giới hạn số bước/lượt, thì đó chưa được tính là một bước hoàn chỉnh.

Hệ quả khi thiết kế phiếu tác giả:

- cần phân biệt **bước đang mở** và **bước hoàn chỉnh**;
- một bước hoàn chỉnh nên có đủ dữ kiện để người chấm thấy gia sư đã phản hồi dựa trên thông tin học sinh cung cấp;
- trường lịch sử hội thoại nên có cách biểu diễn rõ ràng để giáo viên không phải tự đoán khi nào một bước được tính là hoàn chỉnh.

### 6.4. Phạm vi “Tin học lớp 9” và “tiền kiến thức lớp 6–8” cần có ranh giới thao tác

Đã chốt ưu tiên Tin học lớp 9 và tiền kiến thức lớp 6–8.

Phần này cần xác nhận thêm với các thầy cô HNMU trước khi biến thành hướng dẫn chính thức.

Cần làm rõ:

- khi nào một câu hỏi được coi là thuộc lớp 9;
- khi nào được phép kéo tiền kiến thức lớp 6–8 vào mẫu;
- nếu học sinh hỏi lệch khỏi Tin học lớp 9 thì giáo viên nên tạo mẫu hay loại;
- nếu học sinh thiếu nền tảng lớp 6–8 thì gia sư nên bù nền như thế nào.

Ghi chú sau phản hồi ngày 04/07/2026:

- trường hợp học sinh hỏi lệch khỏi Tin học lớp 9 đã được người phụ trách dự án đề cập trong file Google Sheets `review_form`;
- cần đọc file này trước khi kết luận cách xử lý chính thức.

### 6.5. Ý tưởng web thu thập dữ liệu phụ thuộc mạnh vào kho học liệu

Trạng thái sau phản hồi ngày 04/07/2026: tạm thời bỏ qua mục này, chưa phân tích sâu trong vòng xử lý hiện tại.

Nếu chưa có kho học liệu đã chia nhỏ và truy xuất được, gia sư AI dễ tạo hội thoại không bám chương trình.

Nguyên tắc tạm thời:

- gia sư AI phải dựa chủ đạo vào học liệu SGK;
- SGK là nguồn căn cứ chính khi tạo hội thoại và phản hồi;
- không nên để gia sư AI trả lời hoàn toàn theo kiểu không có căn cứ học liệu;
- về lâu dài, cần một hệ thống quản lý học liệu đủ chuẩn để mô hình có thể truy xuất đúng đoạn học liệu cần dùng.

Vì vậy, cần phân biệt:

- dữ liệu thu qua web để khảo sát hành vi;
- dữ liệu ứng viên để giáo viên sửa;
- dữ liệu đã đạt chuẩn đưa vào benchmark.

Không nên mặc định hội thoại thu được từ web là mẫu benchmark chính thức.

### 6.6. Đồng bộ experiment local với experiment trên Google Drive

Theo phản hồi ngày 03/07/2026, experiment local đã được đổi tên thành:

```text
experiments/20260701_100006
```

Mục tiêu là đồng bộ tên experiment local với experiment đã có trên Google Drive.

Việc cần làm tiếp sau khi có quyền truy cập Google Drive của toàn bộ dự án:

- kiểm tra file phiếu tác giả trong experiment mới;
- kiểm tra bản copy của `literature_review`;
- kiểm tra bản copy của `curriculum_sources`;
- phát hiện thiếu, mâu thuẫn hoặc chưa đồng bộ trong experiment này.

Trạng thái sau phản hồi ngày 04/07/2026: người phụ trách dự án đồng ý với hướng đồng bộ này.

## 7. Bản đồ việc cần xử lý tiếp

Sau phản hồi ngày 04/07/2026, có 5 việc nên làm ngay. Ba việc về phiếu tác giả/rubric/task nên làm lần lượt; hai việc về học liệu có thể chạy song song với chuỗi đó.

| Thứ tự | Nhóm việc | Cách chạy | Mục tiêu | Đầu ra mong muốn | Người quyết định/chốt |
|---:|---|---|---|---|---|
| 1 | Kiểm tra phiếu tác giả | Tuần tự, làm trước | Xác định trường nào đã chốt, trường nào còn mơ hồ, trường nào có nguy cơ làm lệch rubric/task. | Bảng rà soát trường dữ liệu và đề xuất chỉnh. | UET + HNMU |
| 2 | Chốt rubric và mã lỗi nghiêm trọng | Tuần tự, sau phiếu tác giả | Biến các trường đánh giá trong phiếu tác giả thành tiêu chí chấm có ý nghĩa sư phạm. | Danh sách rubric, thang điểm, mã lỗi nghiêm trọng và quan hệ giữa mã lỗi với rubric. | UET đề xuất, HNMU xác nhận |
| 3 | Chuẩn hóa mã task | Tuần tự, sau rubric/mã lỗi | Cung cấp mã task đủ ổn định cho giáo viên, sau khi đã đối chiếu lại với phiếu tác giả và rubric. | Danh sách mã task, tên task, định nghĩa ngắn, ví dụ đúng và ví dụ sai. | UET đề xuất, HNMU xác nhận |
| 4 | Chuẩn hóa chủ đề Tin học 6–9 | Chạy song song với việc 1–3 | Liên kết lớp 9 với tiền kiến thức lớp 6–8. | Bảng chủ đề thống nhất và mapping lớp 6–9. | HNMU xác nhận |
| 5 | Rà soát học liệu | Chạy song song với việc 1–3 | Đảm bảo mẫu có căn cứ học liệu. | Danh mục học liệu, mã học liệu, đoạn học liệu có thể trích dẫn. | UET xử lý, HNMU xác nhận |

Các việc tạm để sau:

- đánh giá phương án web thu thập dữ liệu;
- chốt quy trình chấm rubric ở mức teacher-facing đầy đủ;
- thiết kế database học liệu chuẩn chỉnh.

### 7.1. Phân công 4 specialist agent

Đề xuất phân công theo vai trò hiện tại của 4 specialist:

| Specialist | Cấu hình đã biết | Vai trò chính trong 5 việc trước mắt | Đầu ra phù hợp |
|---|---|---|---|
| `teacher-collaboration-designer` | Adapter chưa pin model; reasoning effort `high` | Đồng dẫn việc kiểm tra phiếu tác giả theo góc nhìn giáo viên: trường nào dễ hiểu, ai điền, trường nào bắt buộc, ví dụ đúng/sai cho cách điền. | Bản rà soát phiếu tác giả theo ngôn ngữ giáo viên; danh sách điểm gây hiểu nhầm; câu hỏi cần HNMU xác nhận. |
| `benchmark-specification-designer` | `gpt-5.4-mini`, reasoning effort `high` | Dẫn việc chốt rubric/mã lỗi nghiêm trọng và chuẩn hóa mã task; đồng thời kiểm tra xem metadata trong phiếu tác giả có ép sai task/rubric không. | `rubric_specification`, `serious_error_catalog`, `benchmark_task_specification`, ma trận truy vết task–rubric–metadata. |
| `learning-resource-curator` | `gpt-5.4-mini`, reasoning effort `medium` | Dẫn hai việc học liệu: chuẩn hóa chủ đề Tin học 6–9 và rà soát học liệu SGK/nguồn HNMU. | Bảng chủ đề lớp 6–9, bảng tiền kiến thức lớp 6–8 cho lớp 9, danh mục học liệu, mã học liệu/đoạn học liệu ở mức v0. |
| `research-methodologist` | `gpt-5.4-mini`, reasoning effort `medium` | Không làm review rộng ở vòng gấp này; chỉ rà soát có mục tiêu để kiểm tra các rubric/mã lỗi/task có căn cứ nghiên cứu hay chỉ là giả định. | Ghi chú bằng chứng ngắn, khoảng trống nghiên cứu, các điểm phải gắn nhãn “cần HNMU xác nhận”. |

### 7.2. Luồng chạy đề xuất

Luồng tiết kiệm và ít rủi ro nhất:

1. `teacher-collaboration-designer` rà soát phiếu tác giả theo góc nhìn giáo viên.
2. `learning-resource-curator` chạy song song để chuẩn hóa chủ đề Tin học 6–9 và rà soát học liệu.
3. `benchmark-specification-designer` nhận đầu ra từ bước 1 và phần học liệu đã có từ bước 2 để chốt rubric/mã lỗi nghiêm trọng.
4. `research-methodologist` rà soát nhanh các điểm rubric/mã lỗi/task nhạy cảm về căn cứ nghiên cứu.
5. `benchmark-specification-designer` chuẩn hóa mã task sau khi đã có phiếu tác giả, rubric/mã lỗi và input học liệu tối thiểu.
6. `teacher-collaboration-designer` chuyển phần đã chốt tạm thời thành hướng dẫn ngắn cho giáo viên HNMU, nếu cần gửi ngay.

### 7.3. Chỗ cần người phụ trách dự án xác nhận trước khi spawn song song

Nếu muốn tiết kiệm thời gian, có thể spawn đồng thời hai specialist khác nhau ở bước đầu:

- `teacher-collaboration-designer`: kiểm tra phiếu tác giả;
- `learning-resource-curator`: chuẩn hóa chủ đề Tin học 6–9 và rà soát học liệu.

Không cần spawn nhiều bản sao của cùng một specialist ở thời điểm này.

Nếu muốn chạy nhanh hơn nữa, có thể cân nhắc spawn thêm `benchmark-specification-designer` song song ở chế độ đọc phiếu tác giả để phát hiện sớm rủi ro rubric/task. Tuy nhiên, cách này dễ tạo trùng việc với `teacher-collaboration-designer`, nên chỉ nên làm nếu người phụ trách dự án xác nhận rõ phạm vi: `teacher-collaboration-designer` kiểm tra tính dễ hiểu với giáo viên, còn `benchmark-specification-designer` kiểm tra tính hợp lệ của metadata đối với rubric/task.

Tại thời điểm ghi chú này, chưa spawn specialist nào.

## 8. Cách hiểu thống nhất tạm thời

Từ ghi chú cuộc họp và phản hồi bổ sung ngày 03/07/2026, có thể tạm hiểu hướng đi như sau:

1. Về nguyên tắc, hướng top-down vẫn sạch hơn: task → rubric/mã lỗi → metadata.
2. Vì tiến độ đang rất gấp, hướng xử lý tạm thời là rà phiếu tác giả trước: metadata → rubric/mã lỗi → task.
3. Deadline KSE và mức tối thiểu cần có cho bài báo vẫn cần người phụ trách dự án hỏi lại giáo sư.
4. UET cần soi kỹ phiếu tác giả trước khi chuyển sang rubric và task.
5. Mỗi mẫu cần bám Tin học lớp 9, nhưng có thể viện dẫn tiền kiến thức lớp 6–8 khi cần; phần ranh giới cụ thể cần HNMU xác nhận.
6. Lịch sử trao đổi phải thể hiện gia sư có dẫn dắt theo phương pháp giàn giáo, không chỉ trả lời đáp án.
7. Trong lịch sử hội thoại, “bước” tạm hiểu là một cặp trao đổi giữa học sinh và gia sư; nếu gia sư chỉ hỏi gợi mở và học sinh chưa trả lời thì bước đó chưa hoàn chỉnh, trừ khi đã đến giới hạn hội thoại và gia sư phải kết luận.
8. Dữ liệu thu thập qua web tạm thời chưa phân tích sâu trong vòng này.
9. Trước khi mở rộng số lượng mẫu, cần chốt rõ tiêu chuẩn thế nào là một mẫu hợp lệ.

## 9. Ghi chú cho bước tiếp theo

Bước tiếp theo nên là **rà soát phiếu tác giả và experiment `20260701_100006`**.

Khi người phụ trách dự án cung cấp link thư mục và quyền truy cập Google Drive của toàn bộ dự án, cần đối chiếu bản local với bản trên Drive trước khi phản biện sâu.

Khi bắt đầu bước đó, nên tạo một báo cáo riêng gồm:

- danh sách toàn bộ trường trong phiếu tác giả;
- ý nghĩa từng trường;
- ai chịu trách nhiệm điền;
- trường nào bắt buộc;
- trường nào có thể để trống ở vòng đầu;
- ví dụ điền đúng;
- ví dụ điền sai;
- điểm mâu thuẫn với deadline, task/rubric, học liệu hoặc quy trình giáo viên.
