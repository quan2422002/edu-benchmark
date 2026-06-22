# Workbook field notes

## Input

`document/teacher_training_curriculum/Benchmark Tin học THCS.xlsx`

- Vai trò: `internal_draft`.
- SHA-256: `2CDAF31FF65B2BA65A4C167E97AAF9568A13795E14E39B847CE13C3D4E654001`.
- Kích thước: 324,959 bytes.
- Công cụ kiểm tra: `openpyxl==3.1.5`.
- Python: `D:\conda-envs\benchmark_env\python.exe`.
- Chế độ: read-only về mặt quy trình; workbook được mở để đọc với `data_only=False`, `keep_links=True` và không gọi `save()`.

## Cấu trúc đã xác nhận

| Sheet | Vai trò |
|---|---|
| `README` | Mục đích, trạng thái draft và hai nguồn chương trình |
| `Dashboard` | Thống kê bằng công thức |
| `Blueprint` | Phân bổ item dự kiến/thực tế |
| `Item_Bank` | 160 item, table `Table_1` tại `A1:Y161` |
| `Expert_Form` | Form review 160 item, table `Table_2` tại `A1:M161` |
| `Lists` | Giá trị dùng cho data validation |

Workbook có 40 item lớp 9:

- DL: 12;
- ICT: 12;
- CS: 16.

Toàn bộ field expert review, pilot accuracy và discrimination index của lớp 9 đang trống. Tất cả 40 item có status `draft_v1`.

## Field tham khảo

| Field | Ý nghĩa | Cách dùng trong C01 |
|---|---|---|
| `item_id` | Mã item | Tham khảo cách đặt mã; không tái sử dụng mặc định |
| `grade` | Lớp | C01 chỉ xét lớp 9 |
| `strand` | Mạch nội dung DL/ICT/CS | Đối chiếu với nguồn chương trình |
| `topic` | Chủ đề | Dùng để gợi ý phân nhóm, không coi là mapping đã duyệt |
| `competency` | NLa–NLe | Phải kiểm tra với chương trình và giáo viên |
| `cognitive_level` | Mức nhận thức | Tham khảo; chưa coi là taxonomy chính thức |
| `item_type` | MCQ/Short answer/Scenario/Performance | Tham khảo format, không dùng làm taxonomy tutoring |
| `question` | Câu hỏi hoặc tình huống | Dùng làm ví dụ cấu trúc |
| `correct_answer` | Đáp án/gợi ý đáp án | Chưa phải ground truth trước expert review |
| `rubric` | Hướng dẫn chấm | Cần tách thành criterion nhỏ và gắn reference |
| `expected_difficulty` | Độ khó dự kiến | Chưa được pilot xác nhận |
| `status` | Trạng thái nội bộ | `draft_v1` không đồng nghĩa approved |
| `expert_*` | Điểm chuyên gia | Hiện trống, không được suy diễn là pass |
| `pilot_accuracy` | Độ chính xác pilot | Hiện trống |
| `discrimination_index` | Chỉ số phân biệt | Hiện trống |

## `Expert_Form`

Form dùng năm tiêu chí 1–4:

- alignment;
- age appropriateness;
- clarity;
- answer/rubric correctness;
- competency relevance.

Quyết định: `keep`, `revise`, `remove`.

`Expert_Form` hiện khớp `Item_Bank` về ID, grade, strand, topic, item type và question, nhưng là snapshot tĩnh chứ không liên kết công thức. Nếu một sheet được sửa riêng, hai sheet có thể lệch. C01 chỉ tham khảo field; không cập nhật form gốc.

## Rủi ro kỹ thuật

- Các sheet được format tới `A1:Z1000`; số record phải lấy từ Excel table, không dùng `max_row=1000`.
- Hai URL trong README là text thường, không phải hyperlink object.
- Workbook không có external workbook link.
- Bảy ô nội dung bắt đầu bằng `=` được Excel/openpyxl nhận là formula. Chúng có vẻ là nội dung bài tập bảng tính, không phải công thức vận hành item bank:

```text
J52
M53
M56
I57:L57
```

Khi extraction phải giữ formula source, không thay bằng cached result. Các ô này nằm ngoài 40 item lớp 9 nhưng là regression case nếu sau này mở rộng audit.

## Kết luận sử dụng

Workbook cung cấp field names, review dimensions và ví dụ định dạng hữu ích. Nó không cung cấp evidence đủ để xác nhận curriculum alignment, đáp án, rubric, độ khó hoặc chất lượng item.
