# Thiết kế dữ liệu tối giản v0

> **Lưu ý:** Đây là prototype tạo trước literature review. Không dùng như chỉ dẫn chính thức cho giáo viên; gói teacher pilot chính thức sẽ được tạo theo P04 trong [roadmap mô-đun](../20260620_115236/roadmap.md).

Tài liệu này dành cho giáo viên/chuyên gia môn Tin học tham gia đề xuất tình huống và tiêu chí đánh giá gia sư LLM.

## Mục tiêu

Mỗi sample mô tả một tình huống học sinh lớp 9 cần trợ giúp và những hành vi có thể quan sát để nhận biết một phản hồi sư phạm tốt.

Thiết kế v0 ưu tiên:

- ít trường và dễ điền;
- dùng ngôn ngữ quen thuộc với giáo viên;
- không yêu cầu kiến thức kỹ thuật về benchmark hoặc machine learning;
- có thể bổ sung metadata về sau mà sample cũ vẫn sử dụng được.

## Hai file dữ liệu

### `dataset.yaml`

Chứa thông tin chung, chỉ khai báo một lần:

```yaml
schema_version: "0.1"
name: grade_9_informatics_tutor_v0
subject: Tin học
grade: 9
language: vi
curriculum_source: null
```

### `samples.yaml`

Chứa các tình huống do giáo viên biên soạn:

```yaml
- id: cs9_0001
  topic: "Tên chủ đề"
  student_prompt: "Học sinh hỏi gì?"
  student_work: null
  criteria:
    - "Phản hồi tốt cần làm gì?"
    - "Phản hồi không nên làm gì?"
  example_response: null
  extensions: {}
```

## Giáo viên cần điền gì?

Giáo viên chỉ cần tập trung vào:

1. `topic`: bài hoặc chủ đề của tình huống.
2. `student_prompt`: câu nói/câu hỏi tự nhiên của học sinh.
3. `student_work`: bài làm hoặc code của học sinh, nếu có.
4. `criteria`: từ 2 đến 5 điều cụ thể mà phản hồi tốt cần đạt.
5. `example_response`: một phản hồi minh họa, nếu giáo viên thấy cần.

`id` có thể được hệ thống tự sinh. `extensions` để trống ở giai đoạn đầu.

Giáo viên không bắt buộc chỉnh YAML trực tiếp. Đợt thu thập đầu có thể dùng một bảng tính với các cột:

```text
topic | student_prompt | student_work | criterion_1 | criterion_2 |
criterion_3 | criterion_4 | criterion_5 | example_response
```

Sau đó hệ thống sẽ tự sinh `id`, loại bỏ ô criterion trống, gom các criterion thành danh sách và xuất sang YAML chuẩn.

File mẫu có thể mở bằng Excel hoặc Google Sheets: [dataset_v0/teacher_template.csv](dataset_v0/teacher_template.csv).

## Cách viết criteria

Mỗi criterion nên:

- chỉ mô tả một hành vi;
- có thể quan sát hoặc kiểm tra được;
- dùng câu ngắn, rõ nghĩa;
- nói rõ điều cần làm hoặc điều cần tránh.

Ví dụ rõ ràng:

- “Chỉ ra rằng dòng `print` chưa được thụt vào trong khối `if`.”
- “Đặt câu hỏi để học sinh tự nhận ra quy tắc thụt lề.”
- “Không đưa ngay toàn bộ code đã sửa.”

Ví dụ nên tránh:

- “Phản hồi hay và có tính sư phạm.”

Lý do: từ “hay” và “có tính sư phạm” chưa cho người chấm biết cần quan sát hành vi nào.

## Lưu ý về `example_response`

`example_response` chỉ minh họa một cách trả lời tốt. Nó không phải đáp án duy nhất và không nên được dùng để chấm theo mức độ giống câu chữ.

## Khả năng mở rộng

- Bốn trường lõi `id`, `topic`, `student_prompt`, `criteria` được giữ ổn định.
- Trường mới phải là tùy chọn để sample cũ vẫn hợp lệ.
- Metadata thử nghiệm được thêm dưới `extensions` trước khi trở thành trường chính thức.
- Phiên bản schema được quản lý ở `dataset.yaml`, không lặp trong mỗi sample.
- Khi mở rộng sang lớp hoặc môn khác, tạo manifest dataset mới thay vì trộn vào benchmark lớp 9.

## Mẫu tham khảo

Ba mẫu minh họa có tại [dataset_v0/samples.yaml](dataset_v0/samples.yaml). Chúng chỉ minh họa cách viết, chưa đại diện cho phạm vi kiến thức cuối cùng của chương trình Tin học lớp 9.
