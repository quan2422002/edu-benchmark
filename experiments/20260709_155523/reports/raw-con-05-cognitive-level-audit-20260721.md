# Rà soát tiêu chí RAW-CON-05 — Mức nhận thức hợp lý

Ngày rà soát: 21/07/2026  
Phạm vi: một số mẫu dữ liệu thô HNMU lớp 6–9 trong Plan 04  
Mục tiêu: kiểm tra xem tiêu chí `RAW-CON-05` đã được chấm dựa đúng vào tài liệu gốc về mức độ nhận thức hay chưa.

## 1. Kết luận nhanh

Có rủi ro thật sự ở tiêu chí `RAW-CON-05`.

Lý do chính:

1. Checklist và registry tiêu chí hiện tại chỉ mô tả chung rằng mức nhận thức phải khớp với câu hỏi/nhiệm vụ, nhưng chưa trỏ trực tiếp tới tài liệu gốc:
   `document/teacher_training_curriculum/benchmark_building_documents/Biểu hiện mức độ nhận thức _Tin học.docx`.
2. Kết quả chấm lớp 8–9 có dấu hiệu quá “thoáng”: 588/588 mẫu đều `pass` ở `RAW-CON-05`.
3. Lý do chấm của lớp 8–9 rất chung, ví dụ “mức nhận thức nằm trong 3 mức chuẩn”, nên chưa chứng minh được agent đã đối chiếu động từ/yêu cầu của câu hỏi với tài liệu HNMU.
4. Một số mẫu lớp 6–7 được đưa vào `uncertain` là hợp lý, nhưng cũng có mẫu có thể đã bị đánh `uncertain` hơi quá tay nếu bám sát tài liệu gốc.

Kết luận vận hành: chưa nên coi kết quả `RAW-CON-05` hiện tại là ổn định. Nên cập nhật tiêu chí để dùng tài liệu HNMU làm nguồn chuẩn, rồi chạy lại riêng `RAW-CON-05` cho toàn bộ lớp 6–9.

## 2. Nguồn chuẩn từ tài liệu HNMU

File gốc:

```text
document/teacher_training_curriculum/benchmark_building_documents/Biểu hiện mức độ nhận thức _Tin học.docx
```

Tài liệu mô tả ba mức:

- `Biết`
- `Hiểu`
- `Vận dụng`

Trong dự án, nhãn đang dùng thường là:

- `Nhận biết` tương ứng với `Biết`
- `Thông hiểu` tương ứng với `Hiểu`
- `Vận dụng` giữ nguyên

Một số dấu hiệu chính trong tài liệu:

- `Biết`: kể lại, nêu, biết, nhận biết, nhận ra, nhận diện, chỉ ra, thực hiện thao tác đơn giản.
- `Hiểu`: diễn tả, mô tả, trình bày, phát biểu, giải thích, hiểu, đọc hiểu, phân biệt, so sánh, phân tích ở mức hiểu quan hệ/ý nghĩa.
- `Vận dụng`: tìm, chuẩn bị, dùng, sử dụng, khai thác, chỉnh sửa, xác lập, thực hiện nhiệm vụ, kiểm thử, viết, thiết kế, quản lí, tạo sản phẩm.

Điểm cần chú ý: không thể chỉ nhìn một từ khóa đơn lẻ. Ví dụ `nêu ví dụ` có thể nghiêng về Biết/Hiểu, nhưng nếu yêu cầu học sinh tự áp dụng vào bối cảnh cá nhân hoặc thực hiện nhiệm vụ cụ thể thì có thể gần Vận dụng hơn. Vì vậy `RAW-CON-05` cần được chấm theo cả động từ, đối tượng hành động và mức độc lập của học sinh trong câu hỏi.

## 3. Tình trạng kết quả RAW-CON-05 hiện tại

Nguồn kết quả đã rà:

```text
experiments/20260709_155523/outputs/hnmu_dialogue_audit/agent_shard_audit/merged/raw_dialogue_checklist_results.repaired.csv
experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/raw_dialogue_checklist_results.regex_repaired.csv
```

Thống kê:

| Nhóm dữ liệu | Tổng mẫu | `pass` | `uncertain` | `fail` |
|---|---:|---:|---:|---:|
| Lớp 6–7 | 462 | 388 | 74 | 0 |
| Lớp 8–9 | 588 | 588 | 0 | 0 |
| Tổng lớp 6–9 | 1.050 | 976 | 74 | 0 |

Quan sát thêm:

- Toàn bộ 1.050 dòng `RAW-CON-05` hiện không có `evidence_fragment_id`.
- Lớp 8–9 chỉ có ba mẫu câu lý do lặp lại theo shard, mỗi mẫu câu xuất hiện 196 lần.
- Điều này cho thấy kết quả lớp 8–9 nhiều khả năng mới kiểm nhãn ở mức hợp lệ hoặc kiểm rất sơ bộ, chưa đủ truy vết theo tài liệu HNMU.

## 4. Rà mẫu cụ thể

### 4.1. Mẫu có vẻ chấm hợp lý

| Mẫu | Lớp | Mức ghi trong dữ liệu | Câu hỏi | Kết quả hiện tại | Nhận xét |
|---|---:|---|---|---|---|
| `HNMU-G6-R0002-STT1` | 6 | Nhận biết — nêu khái niệm | “Thông tin là gì?” | `pass` | Hợp lý. Đây là câu hỏi định nghĩa/khái niệm, khớp nhóm Biết/Nhận biết. |
| `HNMU-G7-R0044-STT1` | 7 | Nhận biết — biết khái niệm | “Mạng xã hội là gì?” | `pass` | Hợp lý. Câu hỏi yêu cầu nêu khái niệm. |
| `HNMU-G8-R0002-STT1` | 8 | Nhận biết — nhớ tên tác giả | “Ai là người đã sáng chế ra chiếc máy tính cơ học Pascaline?” | `pass` | Hợp lý về kết luận, nhưng lý do hiện tại quá chung. |
| `HNMU-G8-R0010-STT9` | 8 | Thông hiểu — giải thích tầm quan trọng | “Tại sao cấu trúc máy tính của Von Neumann lại được sử dụng cho đến tận ngày nay?” | `pass` | Hợp lý. `Tại sao/Giải thích` khớp nhóm Hiểu/Thông hiểu. |
| `HNMU-G9-R0029-STT14` | 9 | Vận dụng — tạo sản phẩm số | “Tạo một bài trình chiếu…” | `pass` | Hợp lý. `Tạo` sản phẩm khớp nhóm Vận dụng. |

### 4.2. Mẫu đang `uncertain` có vẻ hợp lý

| Mẫu | Lớp | Mức ghi trong dữ liệu | Câu hỏi | Kết quả hiện tại | Nhận xét |
|---|---:|---|---|---|---|
| `HNMU-G6-R0013-STT12` | 6 | Vận dụng — phân tích tình huống thực tế | “Em hãy nêu ví dụ về thông tin giúp em đảm bảo an toàn khi tham gia giao thông.” | `uncertain` | Có thể cần HNMU xác nhận. Câu hỏi chỉ yêu cầu nêu ví dụ nên có thể thấp hơn Vận dụng; nhưng vì gắn với tình huống cá nhân/thực tế nên không nên kết luận sai ngay. |

### 4.3. Mẫu có khả năng bị chấm chưa ổn

| Mẫu | Lớp | Mức ghi trong dữ liệu | Câu hỏi | Kết quả hiện tại | Nhận xét |
|---|---:|---|---|---|---|
| `HNMU-G7-R0047-STT4` | 7 | Nhận biết — biết quy định | “Theo quy định, lứa tuổi nào thường được phép tham gia mạng xã hội?” | `uncertain` | Có thể đã bị đánh `uncertain` hơi quá tay. Theo tài liệu HNMU, các câu hỏi biết/nêu nội dung liên quan đến quy định, luật, cảnh báo có thể thuộc Biết/Nhận biết. |
| `HNMU-G9-R0013-STT12` | 9 | Vận dụng — khai thác thông tin | “Kể về một ví dụ về kiến thức em học được từ nguồn thông tin trên Internet.” | `pass` | Nên xem lại. Nếu chỉ kể ví dụ thì gần Biết/Hiểu hơn; nếu học sinh phải tự khai thác nguồn thông tin thì mới nghiêng về Vận dụng. Câu hỏi hiện tại không thể hiện rõ thao tác khai thác. |
| `HNMU-G9-R0015-STT14` | 9 | Vận dụng — xác lập lựa chọn/giải thích theo tiêu chí | “Tại sao các thiết bị kĩ thuật số ngày càng nhỏ gọn nhưng lại mạnh mẽ hơn?” | `pass` | Nên xem lại. Câu hỏi chủ yếu yêu cầu giải thích, có vẻ gần Hiểu/Thông hiểu hơn Vận dụng nếu không kèm yêu cầu chọn/xác lập theo tiêu chí. |

## 5. Nhận định về cách chấm hiện tại

### Lớp 6–7

Lớp 6–7 có vẻ đã có một số logic phân biệt giữa mức ghi trong dữ liệu và yêu cầu câu hỏi, vì có 74 mẫu `uncertain`. Tuy nhiên logic này chưa được ghi thành quy tắc chuẩn dựa trên file docx HNMU. Vì vậy vẫn có rủi ro:

- một số mẫu bị đưa vào `uncertain` hơi quá tay;
- một số mẫu `pass` có thể chỉ là “phù hợp sơ bộ”, chưa chắc nếu đối chiếu kỹ động từ/yêu cầu;
- không có dẫn chiếu tới tài liệu mức nhận thức trong kết quả từng mẫu.

### Lớp 8–9

Lớp 8–9 đáng lo hơn:

- 588/588 mẫu đều `pass`;
- lý do chấm rất chung và lặp theo shard;
- không có evidence/căn cứ cụ thể;
- có mẫu đáng lẽ nên `uncertain` nhưng vẫn `pass`, đặc biệt khi câu hỏi chỉ yêu cầu giải thích/kể ví dụ nhưng mức ghi là Vận dụng.

Vì vậy không nên dùng kết quả `RAW-CON-05` lớp 8–9 hiện tại làm căn cứ cuối cùng.

## 6. Đề xuất sửa

Nên làm bốn việc trước khi chốt Plan 04:

1. Tạo một bản Markdown chuẩn hóa từ file gốc HNMU:

```text
shared/learning_resources/agent_context/hnmu_cognitive_level_method_canonical.md
```

Vai trò: mô tả ba mức Biết/Hiểu/Vận dụng, các động từ điển hình, các trường hợp mơ hồ, và quy tắc quy đổi sang Nhận biết/Thông hiểu/Vận dụng.

2. Cập nhật `raw-dialogue-audit-criteria-v0.csv` để `RAW-CON-05` trỏ trực tiếp tới tài liệu chuẩn hóa này và file docx gốc.

3. Cập nhật skill `hnmu-dialogue-auditor` để khi chấm `RAW-CON-05`, agent bắt buộc:

- kiểm động từ/yêu cầu trong câu hỏi;
- kiểm đối tượng học sinh phải thao tác với;
- phân biệt câu hỏi chỉ “nêu/kể/nhận biết” với câu hỏi yêu cầu “thực hiện/tạo/sử dụng/xác lập/kiểm thử”;
- dùng `uncertain` khi câu hỏi mơ hồ giữa hai mức.

4. Chạy repair riêng cho `RAW-CON-05` trên toàn bộ lớp 6–9, sau đó đồng bộ lại `quality_check_suggestions.csv` bằng rule strict.

## 7. Kết luận

Tiêu chí `RAW-CON-05` hiện có vấn đề về căn cứ nguồn. Không phải toàn bộ kết quả đang sai, nhưng kết quả hiện tại chưa đủ truy vết để bảo vệ trước HNMU/UET nếu bị hỏi “mức nhận thức được chấm theo chuẩn nào?”.

Việc cần làm tiếp theo không nên là sửa tay từng mẫu ngay, mà nên chuẩn hóa nguồn đánh giá mức nhận thức trước, rồi chạy lại đúng một tiêu chí `RAW-CON-05`.
