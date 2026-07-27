# Sổ tay mã hóa sáu nguyên tắc sư phạm — Workstream C v3

Trạng thái: **UET đã phê duyệt kiến trúc tập nhãn không thứ tự ngày 27/07/2026; HNMU chưa xác nhận**.

## 1. Kiến trúc hiện hành

Toàn bộ dữ liệu dùng một nhiệm vụ benchmark:

```text
TASK-NEXT-TUTOR-RESPONSE
Sinh lượt phản hồi tiếp theo của gia sư
```

Mỗi ứng viên có một `principle_set` là tập con không thứ tự của:

`Challenge`, `Explanation`, `Modelling`, `Practice`, `Feedback`, `Questioning`.

Không có nguyên tắc chính/phụ và không giới hạn cứng ở hai. Nếu tập có hơn ba
nguyên tắc, candidate vẫn hợp lệ nhưng bắt buộc UET review. Sáu năng lực A–B
không phải nhãn; chúng là nền xây tiêu chí chấm ở Workstream D.

KMP-Bench dùng một hoặc hai nguyên tắc khi thiết kế trước hành động gia sư.
Nguồn này không chứng minh hai là giới hạn sư phạm phổ quát cho việc gán hậu
nghiệm hội thoại HNMU đã tồn tại.

## 2. Ba tầng không được trộn

| Tầng | Câu hỏi | Thành phần |
|---|---|---|
| Nhiệm vụ | Mô hình phải tạo đầu ra gì? | Một lượt phản hồi tiếp theo của gia sư. |
| Nguyên tắc | Phản hồi tốt phải thực hiện các chức năng sư phạm nào? | Sáu nguyên tắc KMP. |
| Năng lực | Phản hồi thực hiện các chức năng đó tốt đến đâu? | Sáu năng lực `CAP-*`. |

## 3. Quy trình hai vòng

### Vòng context

Chỉ đọc `student_prompt`, `conversation_history`, lớp, bài, vị trí và mức nhận
thức. Không đọc `source_question`, `gold_answer`, fragment ẩn hoặc
`gold_response`.

1. Tóm tắt trạng thái học sinh có thể quan sát.
2. Xác định từng nhu cầu sư phạm độc lập.
3. Với mỗi nguyên tắc ứng viên, hỏi: nếu bỏ nguyên tắc này, một nhu cầu độc lập
   có không còn được đáp ứng không?
4. Chỉ chọn khi câu trả lời là có và có `context_evidence` cụ thể.
5. Nếu không nguyên tắc nào phù hợp, ghi `coverage_gap_reason`.

### Vòng grounding

Đọc thêm `source_question`, `gold_answer` và fragment được phép. Không được đọc
hoặc tự truy vết `gold_response`.

- `source_question` làm rõ nhiệm vụ nguồn nhưng hình thức câu hỏi không tự tạo
  nhãn `Questioning`.
- `gold_answer` neo nội dung chuyên môn nhưng không tự quyết định chiến lược sư
  phạm.
- Chỉ đổi tập nhãn nếu grounding mới làm thay đổi một chức năng không thể bỏ.
- Code suy ra `changed`/`unchanged`; agent chỉ đề xuất xung đột ngữ nghĩa.

## 4. Sáu nguyên tắc

### `PRINCIPLE-CHALLENGE` — Thử thách

Chọn khi phản hồi cần nâng yêu cầu nhận thức hoặc duy trì trở ngại vừa sức để
học sinh tạo nỗ lực có ích. Không chọn chỉ vì bài khó hay có thêm việc.

### `PRINCIPLE-EXPLANATION` — Giải thích

Chọn khi phản hồi phải làm rõ khái niệm, quan hệ, nguyên lý, cách thức hoặc lý
do. Không chọn cho việc chỉ nêu đáp án hay lặp lại định nghĩa.

### `PRINCIPLE-MODELLING` — Làm mẫu

Chọn khi học sinh cần quan sát cách áp dụng kiến thức qua dòng suy nghĩ, quy
trình, điểm quyết định, thao tác hoặc sản phẩm mẫu. Không đồng nhất mọi ví dụ
với làm mẫu.

### `PRINCIPLE-PRACTICE` — Luyện tập

Chọn khi học sinh cần thực hiện hoặc lặp lại việc áp dụng nhằm tăng ghi nhớ,
thành thạo hoặc độc lập. Không chọn cho mọi bước học sinh phải làm.

### `PRINCIPLE-FEEDBACK` — Phản hồi

Chọn khi gia sư phải dùng câu trả lời, sản phẩm, thao tác hoặc suy luận đã quan
sát của học sinh làm đối tượng nhận xét có căn cứ để dẫn hướng cải thiện.

### `PRINCIPLE-QUESTIONING` — Đặt câu hỏi

Chọn khi câu trả lời của học sinh là cần thiết để chẩn đoán hiểu biết, giữ mạch
suy luận hoặc thúc đẩy tư duy sâu. Câu hỏi xã giao, tu từ hoặc do gia sư tự trả
lời ngay không đủ.

## 5. Đồng gán và chống gán tràn

Mỗi nguyên tắc phải có:

- `selection_rationale` riêng;
- `context_evidence` riêng;
- `grounding_evidence` riêng nếu quyết định dựa thêm vào vòng grounding.

Các tổ hợp như `Feedback`–`Questioning`, `Explanation`–`Modelling`,
`Challenge`–`Practice` có thể hợp lệ nhưng không tự động đồng xuất hiện.

Không dùng nhãn bổ sung để:

- lưu bất định;
- hòa giải hai agent;
- mô tả mọi động từ xuất hiện trong response giả định;
- sao chép cấu trúc câu của `source_question` hoặc `gold_answer`.

## 6. Quan hệ với sáu năng lực

| Năng lực | Vai trò |
|---|---|
| `CAP-ACC` | Kiểm tính đúng chuyên môn dưới mọi nguyên tắc. |
| `CAP-STATE` | Kiểm phản hồi có bám trạng thái học sinh không. |
| `CAP-STRAT` | Kiểm tập nguyên tắc được chọn có phù hợp không. |
| `CAP-SCAFF` | Kiểm lượng, thời điểm và chuyển giao hỗ trợ. |
| `CAP-DIAG` | Kiểm khả năng giải thích nguyên nhân lỗi/bế tắc. |
| `CAP-CARE` | Kiểm giao tiếp rõ ràng, tôn trọng và phù hợp lứa tuổi. |

## 7. Khoảng trống và review

`coverage_gap_reason` phải mô tả trạng thái học sinh, mục tiêu còn thiếu và vì
sao sáu nguyên tắc không biểu diễn được. Không tự thêm nguyên tắc thứ bảy.

UET review bắt buộc khi:

- hai agent có tập nhãn khác nhau;
- tập nhãn đổi sau grounding;
- có xung đột context–grounding;
- tập nhãn rỗng;
- tập có hơn ba nguyên tắc;
- agent đề xuất làm rõ codebook.

HNMU sẽ review sáu nguyên tắc cùng sáu năng lực, rubric và ví dụ sau Workstream D.

## 8. Nhánh legacy

Schema chính–phụ, input có `gold_response`, tám nhiệm vụ cũ và các bundle C0b
đầu tiên chỉ là artifact chẩn đoán lịch sử. Chúng không phải input của run v3.
