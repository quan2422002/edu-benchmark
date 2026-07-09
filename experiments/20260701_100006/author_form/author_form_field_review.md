# Rà soát phiếu tác giả — Bước 1

Ngày rà soát: 04/07/2026
Experiment: `20260701_100006`
Plan: `plans/02-author-form-rubric-task-and-learning-resource-sprint.md` — `APPROVED` giới hạn Bước 1
Nguồn chính: `review_form.xlsx` trên Google Drive, modified `2026-07-03T12:37:31.852Z`
Bản snapshot local: `drive_snapshot/files/teacher_packet/review_form.xlsx`; bản audit text: `drive_snapshot/review_form.extracted.txt`
Chế độ thực hiện: `single-agent fallback` với skill `teacher-collaboration-designer`; chưa spawn specialist thread.

## 0. Ghi chú về input Drive

Sau rà soát ban đầu, người phụ trách dự án nhắc lại rằng Bước 1 còn bao gồm phần lấy file/thư mục từ Google Drive của experiment. Phần này đã được bổ sung vào:

```text
drive_snapshot/
```

Snapshot hiện gồm manifest của folder Drive `version 20260701_100006`, bản tải/export của 14 file trong 3 thư mục `teacher_packet`, `literature_review`, `curriculum_sources`, và bản trích xuất text từ `review_form.xlsx`. Báo cáo dưới đây vẫn tập trung vào phiếu tác giả; các file literature/curriculum trong snapshot chỉ là input chuẩn bị cho các bước sau, chưa được diễn giải như kết luận chuyên môn.

## 1. Kết luận nhanh

Phiếu tác giả hiện đã đủ khung để bắt đầu thảo luận với HNMU, nhưng **chưa nên dùng để nhập dữ liệu số lượng lớn ngay** nếu chưa sửa một số điểm có nguy cơ làm dữ liệu không đồng nhất.

Các điểm nên giữ:

- Phiếu đã có các trường lõi: người tạo, mã task, chủ đề, yêu cầu học sinh, bài làm, lịch sử trao đổi, học liệu tham khảo, phản hồi mẫu, phản hồi khác hợp lệ, điểm rubric, người kiểm tra chéo và thời gian.
- Phiếu đã thể hiện đúng tinh thần cần truy vết học liệu.
- Phiếu đã bắt đầu mô tả cách xử lý câu hỏi lệch phạm vi: điều hướng về nội dung gần nhất, hoặc từ chối nếu học sinh cố tình lờ điều hướng.
- Phiếu có ý thức về phương pháp giàn giáo, không chỉ yêu cầu gia sư đưa đáp án cuối.

Các điểm cần sửa trước khi giáo viên nhập đại trà:

1. **Định nghĩa bước/lượt trong lịch sử trao đổi còn lệch.** Ghi chú mới của người phụ trách dự án chốt tạm “bước” là một cặp trao đổi học sinh–gia sư, trong khi sheet đang mô tả theo các bước tin nhắn xen kẽ.
2. **Mã task và chủ đề là nút chặn.** Hai trường này bắt buộc, nhưng danh sách mã task và danh sách chủ đề chuẩn chưa có trong repo/local artifact.
3. **Trường học liệu cần mã học liệu ổn định.** Ghi bài/sách/trang tự do có thể đủ cho vòng nháp, nhưng chưa đủ tốt để tạo benchmark có truy vết.
4. **Các trường điểm đang lẫn vai tác giả và vai người chấm.** `rubric_score_list`, `truthfulness_score`, `boundary_adherence_score_list` không nên chỉ do tác giả chính tự quyết nếu mẫu cần kiểm tra chéo.
5. **Vai trò người kiểm tra chéo đang mâu thuẫn với mức bắt buộc.** Phần đầu sheet nói một mẫu cần tác giả chính và người kiểm tra chéo đồng thuận; nhưng `cross_validator_name` lại là Ưu tiên 4.
6. **Một số tên kỹ thuật cần sửa sau khi ổn định.** Ví dụ `reference_curriculumn_list` sai chính tả, `Task_id` viết hoa không nhất quán, `Note` nên thống nhất thành `note`.

## 2. Khuyến nghị trước mắt

### 2.1. Dùng phiếu theo hai trạng thái: mẫu nháp và mẫu hoàn thành

Nên phân biệt rõ:

- **Mẫu nháp:** giáo viên tác giả có thể điền phần lớn nội dung, nhưng điểm rubric và kiểm tra chéo có thể chưa xong.
- **Mẫu hoàn thành:** phải có mã task hợp lệ, chủ đề hợp lệ, học liệu tham khảo, phản hồi mẫu, điểm đánh giá đã được người kiểm tra chéo/reviewer xác nhận, và `completed_at`.

Nếu không phân biệt hai trạng thái này, nhóm sẽ khó biết mẫu nào đủ điều kiện dùng cho paper hoặc benchmark release.

### 2.2. Tạm phân vai điền trường


| Nhóm trường                                                                                                 | Ai nên điền chính                                  | Ghi chú                                                                                              |
| -------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ | ----------------------------------------------------------------------------------------------------- |
| Người tạo, câu hỏi học sinh, bài làm, lịch sử trao đổi, phản hồi mẫu, phản hồi khác hợp lệ | Giáo viên HNMU là tác giả                         | UET cần cung cấp ví dụ điền đúng/sai.                                                         |
| Mã task                                                                                                       | UET                                                    | Giáo viên chỉ chọn/nhận mã, không tự đặt.                                                   |
| Chủ đề                                                                                                      | HNMU chọn từ danh sách đã chuẩn hóa             | Danh sách chủ đề cần HNMU xác nhận.                                                            |
| Học liệu tham khảo                                                                                          | Giáo viên chọn; UET cung cấp mã học liệu/lookup | Vòng đầu có thể ghi bài/sách/trang, nhưng nên tiến tới mã học liệu.                     |
| Điểm rubric, độ chính xác, ranh giới                                                                    | Người kiểm tra chéo hoặc reviewer                 | Tác giả có thể tự đề xuất điểm nháp, nhưng không nên là điểm chính thức duy nhất. |
| Thời gian tạo/hoàn thành                                                                                   | Nên do hệ thống/UET ghi                             | Tránh giáo viên nhập sai định dạng.                                                            |
| Ghi chú                                                                                                       | Bất kỳ người tham gia nào                         | Nên dùng để ghi lý do N/A, lý do bất đồng, hoặc điểm cần phân xử.                      |

### 2.3. Cần sửa ngay phần lịch sử trao đổi

Đề xuất diễn đạt lại cho giáo viên:

> Một bước hoàn chỉnh là một cặp trao đổi gồm: học sinh nêu vấn đề/trả lời/đưa bài làm, sau đó gia sư phản hồi. Nếu gia sư chỉ đặt câu hỏi gợi mở mà học sinh chưa trả lời, và hội thoại chưa chạm giới hạn số bước/lượt, thì bước đó chưa hoàn chỉnh. Khi đã chạm giới hạn hội thoại, gia sư cần kết luận bằng đáp án hoặc hướng dẫn đủ chi tiết.

Ví dụ định dạng nên dùng:

```text
Lượt 1
Bước 1
- Học sinh: ...
- Gia sư: ...

Bước 2
- Học sinh: ...
- Gia sư: ...
```

Không nên dùng một đoạn văn dài gộp nhiều lượt, vì người chấm khó đối chiếu gia sư đã dùng thông tin nào của học sinh.

## 3. Rà soát theo từng trường

Bảng chi tiết nằm ở:

```text
author_form/author_form_field_matrix.csv
```

Tóm tắt theo mức độ ưu tiên:

### Ưu tiên 1 — bắt buộc

- `author_name`: ổn, nhưng cần cân nhắc ẩn danh khi xuất bản.
- `Task_id`: đúng là UET phải chủ động, nhưng cần registry mã task trước khi nhập đại trà.
- `Topic`: cần danh sách chủ đề chuẩn.
- `student_prompt`: ổn, cần hướng dẫn case lệch phạm vi.
- `conversation_history`: cần sửa định nghĩa bước/lượt.
- `reference_curriculumn_list`: cần mã học liệu ổn định; tên kỹ thuật đang sai chính tả.
- `gold_response`: nên đổi nhãn hiển thị thành “phản hồi gia sư mẫu/ưu tiên” để tránh hiểu là chỉ viết đáp án cuối.
- `accepted_response_list`: hữu ích, nhưng mức bắt buộc cần cân nhắc vì có thể làm tăng tải cho giáo viên.
- `rubric_score_list`: cần chờ rubric ổn định và cần phân vai người chấm.

### Ưu tiên 2 — nên có

- `truthfulness_score`: có nguy cơ trùng với rubric D1 Tính đúng chuyên môn.
- `boundary_adherence_score_list`: có nguy cơ trùng với rubric D8 và danh mục lỗi nghiêm trọng.

Hai trường này nên được quyết định lại sau khi chốt rubric/mã lỗi nghiêm trọng.

### Ưu tiên 3 — có thì tốt

- `student_work`: rất hữu ích để cá nhân hóa và chẩn đoán lỗi học sinh, nhưng cần liệt kê rõ 5 dạng bài theo công văn 7991 để giáo viên không phải tự nhớ.

### Ưu tiên 4 — có thể không có

- `cross_validator_name`: đang mâu thuẫn với yêu cầu mẫu hoàn thành cần kiểm tra chéo; đề xuất bắt buộc với mẫu hoàn thành.
- `created_at`, `completed_at`: nên tự động hóa hoặc do UET ghi.
- `Note`: giữ, nhưng cần sửa ràng buộc “Z” và thống nhất tên kỹ thuật.

## 4. Điểm cần sửa trước khi gửi giáo viên nhập số lượng lớn

1. Tạo danh sách mã task tạm thời do UET kiểm soát.
2. Tạo danh sách chủ đề Tin học THCS tạm thời, chờ HNMU xác nhận.
3. Viết lại hướng dẫn `conversation_history` theo “bước = cặp trao đổi”.
4. Thêm ví dụ điền đúng/sai cho ít nhất 5 trường dễ nhầm: `student_prompt`, `conversation_history`, `reference_curriculumn_list`, `gold_response`, `rubric_score_list`.
5. Quyết định ai chấm điểm rubric chính thức.
6. Sửa hoặc ghi chú các tên kỹ thuật chưa ổn: `reference_curriculumn_list`, `Task_id`, `Note`.
7. Chuyển `cross_validator_name` thành bắt buộc đối với mẫu hoàn thành, hoặc giải thích rõ vì sao vẫn là tùy chọn.

## 5. Trạng thái đề xuất

Phiếu tác giả nên được coi là:

```text
usable_for_pilot_with_corrections
```

Nghĩa là có thể dùng để pilot nhỏ hoặc thảo luận với HNMU, nhưng chưa nên coi là form ổn định để nhập hàng trăm mẫu nếu chưa xử lý các điểm ở mục 4.
