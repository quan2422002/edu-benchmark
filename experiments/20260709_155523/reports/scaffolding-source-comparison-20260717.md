# Đối chiếu tài liệu phương pháp giàn giáo HNMU và bản ghi chú Markdown

Ngày tạo: 17/07/2026  
Phạm vi: kiểm tra xem `experiments/20260705_215045/source_scope/scaffolding_function_notes.md` có đủ chính xác để làm cơ sở chính cho agent kiểm dữ liệu HNMU hay không.

## 1. Nguồn được đối chiếu

| Loại | Đường dẫn | Vai trò đề xuất |
|---|---|---|
| Tài liệu gốc HNMU | `document/teacher_training_curriculum/benchmark_building_documents/KhungDanGiao_HoiThoaiMinhHoa.docx` | Nguồn chính khi kiểm dấu hiệu giàn giáo trong hội thoại. |
| Bản ghi chú Markdown cũ | `experiments/20260705_215045/source_scope/scaffolding_function_notes.md` | Bản diễn giải/rút gọn dùng cho P02; không nên coi là nguồn chính. |

## 2. Nội dung chính trong tài liệu gốc HNMU

Tài liệu gốc có ba phần lớn:

1. Khung dàn giáo cho gia sư ảo.
2. Hai hội thoại minh hoạ cụ thể trong SGK Tin học 6.
3. Tài liệu tham khảo.

Năm chức năng giàn giáo trong tài liệu gốc:

| Chức năng | Ý chính trong tài liệu gốc |
|---|---|
| Bước 1: Tiếp nhận và Chẩn đoán | Gia sư thu hút học sinh vào nhiệm vụ, yêu cầu học sinh nêu ý tưởng ban đầu, đánh giá vị trí của học sinh trong ZPD, không đưa lời giải ngay mà đặt câu hỏi gợi mở. |
| Bước 2: Giảm bậc tự do và Đặt mục tiêu | Gia sư chia bài toán phức tạp thành các mục tiêu phụ vừa sức, giúp học sinh xử lý từng bước để tránh quá tải nhận thức. |
| Bước 3: Đánh dấu đặc điểm quan trọng và Hỗ trợ thích ứng | Gia sư làm nổi bật lỗi sai/thông tin quan trọng; hỗ trợ theo nguyên tắc thích ứng từ thấp đến cao: Gợi mở → Giải thích → Gợi ý → Hướng dẫn → Làm mẫu. |
| Bước 4: Kiểm soát sự thất vọng và Khuyến khích tự sửa lỗi | Khi học sinh sai, gia sư không chỉ trích mà dùng câu hỏi kiểu Socrates để học sinh tự nhận ra lỗi và sửa lại. |
| Bước 5: Rút dần hỗ trợ và Đánh giá | Khi học sinh đã hiểu, gia sư rút dần trợ giúp, để học sinh tự hoàn thiện; cuối cùng khen ngợi, tóm tắt kiến thức và xác nhận mức làm chủ. |

Điểm rất quan trọng trong tài liệu gốc: các “bước” này không phải quy trình tuyến tính bắt buộc theo thời gian, mà là các **chức năng dàn giáo**. Gia sư chọn chức năng phù hợp theo diễn biến giải quyết vấn đề.

## 3. Bản Markdown hiện tại phản ánh đúng phần nào?

Bản `scaffolding_function_notes.md` phản ánh đúng một số ý cốt lõi:

- Giữ phương pháp giàn giáo để giải thích chất lượng hỗ trợ sư phạm của gia sư.
- Gắn phương pháp này với rubric R3.
- Ghi lại thang hỗ trợ tiếng Việt: Gợi mở, Giải thích, Gợi ý, Hướng dẫn, Làm mẫu.
- Có nêu nguyên tắc không bỏ mặc học sinh khi chạm giới hạn hỗ trợ.

## 4. Bản Markdown hiện tại thiếu hoặc làm mờ phần nào?

| Điểm thiếu/lệch | Mức độ ảnh hưởng | Ghi chú |
|---|---|---|
| Thiếu mô tả đầy đủ 5 chức năng giàn giáo | Cao | Agent có thể chỉ nhìn thấy thang hỗ trợ, nhưng không thấy các chức năng như chẩn đoán, giảm bậc tự do, kiểm soát thất vọng, rút dần hỗ trợ. |
| Thiếu lưu ý “không phải quy trình tuyến tính” | Cao | Nếu thiếu ý này, agent dễ hiểu sai rằng hội thoại bắt buộc phải đi theo Bước 1 → 2 → 3 → 4 → 5. |
| Thiếu hai hội thoại minh hoạ | Trung bình–cao | Ví dụ trong tài liệu gốc rất quan trọng để agent hiểu biểu hiện cụ thể của giàn giáo trong hội thoại. |
| Thiếu tài liệu tham khảo | Trung bình | Không ảnh hưởng trực tiếp khi kiểm mẫu, nhưng làm yếu truy vết học thuật. |
| Có thêm diễn giải dự án về R3 và cột `note` | Không sai, nhưng cần phân biệt | Đây là quyết định nội bộ của dự án, không phải nguyên văn nội dung trong tài liệu gốc HNMU. |

## 5. Kết luận

Bản `scaffolding_function_notes.md` **không nên được dùng làm cơ sở chính duy nhất** cho agent kiểm tính giàn giáo. Nó là bản ghi chú rút gọn, hữu ích để hiểu quyết định P02, nhưng chưa phản ánh đầy đủ tài liệu gốc HNMU.

Nguồn chính nên là:

```text
document/teacher_training_curriculum/benchmark_building_documents/KhungDanGiao_HoiThoaiMinhHoa.docx
```

Bản Markdown hiện tại chỉ nên được coi là:

```text
Bản diễn giải/dẫn xuất phục vụ dự án — cần đối chiếu với tài liệu gốc khi kiểm ngữ nghĩa.
```

## 6. Khuyến nghị cho Plan 04

Khi agent kiểm hội thoại HNMU, nên dùng tài liệu giàn giáo theo thứ tự ưu tiên:

1. Tài liệu gốc HNMU `KhungDanGiao_HoiThoaiMinhHoa.docx`.
2. Báo cáo đối chiếu này để biết bản Markdown cũ thiếu gì.
3. Bản `scaffolding_function_notes.md` như ghi chú nội bộ về cách dự án gắn giàn giáo với R3 và cột `note`.

Đã tạo bản Markdown chuẩn hóa mới từ file `.docx` gốc tại `shared/learning_resources/agent_context/hnmu_scaffolding_method_canonical.md`. Plan 04 và agent kiểm toán nên dùng file mới này làm nguồn Markdown chính, vì nó giữ đủ 5 chức năng, hai hội thoại minh hoạ, tài liệu tham khảo và nhãn “không phải quy trình tuyến tính”.
