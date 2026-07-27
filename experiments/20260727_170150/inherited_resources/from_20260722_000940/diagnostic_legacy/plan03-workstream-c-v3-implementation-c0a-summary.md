# Báo cáo triển khai Workstream C v3 và kết quả Cổng C0a

Ngày: 27/07/2026  
Trạng thái: **cài đặt hoàn tất; C0a chưa đạt về ngữ nghĩa; C0b chưa được mở**.

## 1. Phần đã cài đặt

- Chuyển output từ cấu trúc nguyên tắc chính–phụ sang tập nguyên tắc không
  thứ tự và bảng quan hệ một dòng cho mỗi cặp candidate–nguyên tắc.
- Loại vật lý `gold_response` khỏi cả input context và input grounding.
- Dùng `source_question`, `gold_answer` và thông tin học liệu làm căn cứ
  grounding; tác động `changed`/`unchanged` được code suy ra.
- Thêm validator cho tập nhãn, khoảng trống độ phủ, nhãn trùng, nhãn ngoài
  taxonomy, trường hợp hơn ba nguyên tắc và tính toàn vẹn ID/hash.
- Thêm phép so sánh hai run bằng exact-set agreement, Jaccard trung bình,
  precision/recall/F1 từng nguyên tắc, coverage gap và tác động grounding.
- Đồng bộ skill, hợp đồng specialist, adapter, schema publication và test.

## 2. Input chạy lại

Grounding pool có 2.028 ứng viên thuộc 665 family. Lô pilot v3 gồm 40
candidate thuộc 40 family khác nhau, phân tầng 10 ứng viên cho mỗi lớp 6,
7, 8 và 9. Hash thứ tự candidate là
`454293f44b3adf5d49dabaf34add2ea6b3a55c297f00c603e0fcb0ca2027e866`.

Ngưỡng C0b đã được đăng ký trước khi nhìn output:

| Chỉ số | Ngưỡng |
|---|---:|
| Trùng chính xác toàn bộ tập nhãn | 0,90 |
| Jaccard trung bình | 0,90 |
| F1 tối thiểu của từng nguyên tắc | 0,90 |
| Thống nhất về khoảng trống độ phủ | 1,00 |
| Thống nhất về tác động grounding | 0,90 |

## 3. Xác thực kỹ thuật

- Skill validator: đạt.
- Validator input context/grounding: đạt.
- Bundle forward test: đạt kiểm tra cấu trúc, có 5 candidate và 1 hàng
  đợi UET review.
- Toàn bộ repository: 134/134 kiểm thử đạt.
- Python dùng để chạy:
  `/home/quannda/miniconda3/envs/benchmark_env/bin/python`.

## 4. Kết quả forward test ngữ nghĩa

Specialist chỉ được đọc input v3, không đọc file tập nhãn kỳ vọng, output
lịch sử hoặc `gold_response`. Kết quả khớp 3/5 ca:

| Ca | Tập kỳ vọng kế thừa | Tập specialist v3 | Kết quả |
|---|---|---|---|
| `FT-C01` | Explanation | Explanation | Khớp |
| `FT-C02` | Feedback + Questioning | Feedback + Explanation | Chưa khớp |
| `FT-C03` | Challenge + Practice | Challenge + Practice | Khớp |
| `FT-C04` | Questioning | Modelling | Chưa khớp |
| `FT-C05` | Explanation | Explanation | Khớp |

`FT-C02` đặt học sinh vào tình huống hỏi vì sao khởi tạo biến tổng bằng
0 thay vì 1. Specialist coi việc đánh giá phần học sinh đã làm là
`Feedback`, còn làm rõ nguyên nhân toán học/chương trình là
`Explanation`. Kỳ vọng `Questioning` trước đây có thể đã chịu ảnh hưởng
của response tham chiếu đặt câu hỏi, trường hiện không còn được phép dùng
để chọn nguyên tắc.

`FT-C04` yêu cầu bước đầu khi gỡ lỗi. Specialist coi “chạy và quan sát
triệu chứng đầu tiên” là thao tác mẫu nên chọn `Modelling`, đồng thời đưa
ca này vào review vì ranh giới với `Questioning` còn mơ hồ. Nếu yêu cầu
thực sự là phải thu nhận câu trả lời mới từ học sinh trước khi tiến tiếp,
`Questioning` mới là chức năng không thể bỏ.

## 5. Quyết định đóng cổng

C0a chưa đạt tiêu chí semantic forward test, nên hai specialist A/B
không được chạy trên lô 40. Không sửa codebook để ép khớp output và không
tự thay tập nhãn kỳ vọng, vì đây là quyết định sư phạm thuộc UET.

Đại diện UET cần quyết định một trong hai hướng cho từng ca:

1. sửa ngữ cảnh tổng hợp để nguyên tắc kỳ vọng trở nên đơn nghĩa rồi giữ
   kỳ vọng cũ; hoặc
2. phê duyệt tập nhãn mới nếu đó là cách hiểu đúng theo input v3 không có
   `gold_response`.

Sau quyết định, phải tạo một version forward test mới và chạy bằng một
native specialist thread mới. Chỉ khi đạt 5/5 mới mở C0b.
