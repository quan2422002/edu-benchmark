# Kế hoạch sau buổi họp UET-HNMU ngày 24/06/2026

> Ngày lập: 27/06/2026
> Nguồn: `user_diary.md`, mục `Update plan (26-06-2026)`
> Trạng thái: bản phân tích và lịch làm việc, chưa phải plan triển khai được duyệt

## 1. Kết luận ngắn

F01 đã giúp HNMU hình dung được nhiệm vụ, tiêu chí chấm, trường dữ liệu, mã nghiên cứu, mã học liệu và lỗi nghiêm trọng. Nhưng F01 không nên được tiếp tục xem là nền bộ đánh giá chính. Nó nên được hạ cấp thành **bản mẫu giao tiếp và tài liệu tham khảo lịch sử**: có ích để học từ phản hồi giáo viên, nhưng không đủ nền lý thuyết để dùng làm bộ đánh giá v1 hoặc để lấy nguyên nhiệm vụ/tiêu chí/mẫu sang phiên bản sau.

Hướng tiếp theo nên là xây lại từ trên xuống:

```text
Định nghĩa bài toán gia sư
  -> tổng quan nghiên cứu có quy trình rõ
  -> mô hình năng lực của gia sư
  -> phạm vi Tin học lớp 9 và tiền kiến thức liên quan
  -> nhóm nhiệm vụ có luận giải
  -> tiêu chí chấm và lỗi nghiêm trọng có luận giải
  -> trường dữ liệu của mẫu
  -> danh mục quản lý/cơ sở dữ liệu học liệu và nghiên cứu
  -> thử nghiệm nhỏ với giáo viên
```

## 2. Phản biện các điểm còn chưa ổn

### 2.1. “Gia sư có thể nhận bất kỳ câu hỏi nào” không có nghĩa bộ đánh giá phải vô hạn

Gia sư 1-1 đúng là cần cá nhân hóa và xử lý câu hỏi mở. Nhưng bộ đánh giá vẫn cần ranh giới rõ. Nếu hiểu “bất kỳ câu hỏi nào” theo nghĩa không giới hạn, ta sẽ không thiết kế được nhiệm vụ, độ bao phủ hay số mẫu.

Điều chỉnh đề xuất:

- Giữ Tin học lớp 9 là phạm vi thử nghiệm chính.
- Cho phép câu hỏi lệch, thiếu nền tảng, hỏi sai hướng để kiểm tra cá nhân hóa.
- Thêm năng lực “nhận diện thiếu tiền kiến thức/ngoài phạm vi/thiếu dữ kiện”.
- Không yêu cầu gia sư trả lời mọi thứ; đánh giá cách gia sư định hướng học sinh.

Khi gặp câu hỏi lệch, thiếu nền tảng hoặc thiếu dữ kiện, gia sư **không nên** chỉ trả lời “tôi không biết” rồi dừng. Phản hồi tốt nên đi theo thứ tự sau:

1. **Ghi nhận câu hỏi của học sinh** bằng giọng tôn trọng, không làm học sinh xấu hổ.
2. **Xác định vấn đề chính**: câu hỏi đang lệch chủ đề, thiếu tiền kiến thức, thiếu dữ kiện, vượt phạm vi lớp 9, hay có rủi ro an toàn/đạo đức.
3. **Nói rõ giới hạn** nếu cần: ví dụ “với dữ kiện hiện có, thầy/cô chưa thể kết luận phần này” hoặc “câu này đang cần kiến thức nền trước khi vào nội dung lớp 9”.
4. **Đưa học sinh về đường học phù hợp**: gợi một câu hỏi nhỏ hơn, một bước ôn lại, hoặc một phần kiến thức nền cần kiểm tra trước.
5. **Kết nối lại với mục tiêu học tập** nếu câu hỏi vẫn liên quan: ví dụ “để trả lời câu này trong bài thuật toán, trước hết em cần xác định dữ liệu vào, dữ liệu ra và điều kiện dừng”.
6. **Từ chối và chuyển hướng an toàn** nếu câu hỏi yêu cầu hành vi không phù hợp, vi phạm đạo đức/pháp luật, hoặc yêu cầu bịa nguồn.

Ví dụ phản hồi tốt với học sinh thiếu nền tảng:

> “Câu hỏi của em đang chạm tới phần điều kiện lặp, nhưng trước khi sửa chương trình, mình cần kiểm tra lại em đã hiểu biến `x` đang lưu gì ở mỗi lần nhập chưa. Em thử nói: sau khi nhập số 7 thì `x` bằng bao nhiêu, và khi nhập 0 thì vòng lặp nên dừng ở bước nào?”

Ví dụ phản hồi tốt với câu hỏi lệch phạm vi:

> “Câu này đi xa hơn nội dung Tin học 9 hiện tại. Nếu mục tiêu của em là hoàn thành bài về chất lượng thông tin, mình nên quay lại câu hỏi gần hơn: thông tin này có mới, chính xác, đầy đủ và dùng được không? Em thử kiểm tra từng tiêu chí trước nhé.”

Trong tiêu chí chấm sau này, phần này nên trở thành một nhóm tiêu chí hoặc tiêu chí con về **định hướng lại câu hỏi, phát hiện thiếu tiền kiến thức và dẫn dắt từng bước**.

### 2.2. “Gia sư khác hoàn toàn giáo viên/trợ giảng” hơi quá mạnh

Gia sư khác giáo viên/trợ giảng ở mức cá nhân hóa, nhịp tương tác và trách nhiệm chẩn đoán từng học sinh. Nhưng gia sư vẫn dùng nền tảng sư phạm, chương trình, học liệu, phản hồi học tập, gợi mở từng bước và đánh giá trong quá trình học. Nếu tách hoàn toàn, ta có thể bỏ lỡ nhiều nghiên cứu tốt.

Điều chỉnh đề xuất:

- Dùng nghiên cứu trực tiếp về gia sư làm bằng chứng lõi.
- Dùng nghiên cứu về giáo viên, trợ giảng hoặc trao đổi trong lớp làm bằng chứng hỗ trợ nếu liên quan phản hồi học tập, gợi mở từng bước hoặc chẩn đoán lỗi.
- Ghi rõ giới hạn chuyển giao khi bằng chứng không phải bối cảnh gia sư 1-1.

### 2.3. Cần chấm giá trị bài báo, nhưng không nên chỉ dựa vào nơi công bố/số trích dẫn

Nơi công bố và số trích dẫn hữu ích nhưng không đủ. Bài báo mới, bài báo ở ngách hẹp hoặc bài báo về ngôn ngữ ít tài nguyên có thể ít trích dẫn nhưng rất liên quan.

Đề xuất chấm điểm 0-3 cho từng chiều:


| Chiều đánh giá | Câu hỏi |
|---|---|
| Mức liên quan | Có trực tiếp nói về đánh giá gia sư hoặc bộ đánh giá gia sư không? |
| Độ gần miền | Có gần K-12, Tin học, lập trình, hoặc tiếng Việt không? |
| Chất lượng phương pháp | Có dữ liệu, quy trình rà soát, nhãn người chấm, độ nhất quán người chấm không? |
| Độ tin cậy công bố | Đã qua phản biện, nơi công bố uy tín, có trích dẫn hoặc được lặp lại ở mức nào? |
| Khả năng dùng được | Có giúp thiết kế nhiệm vụ, tiêu chí chấm hoặc trường dữ liệu không? |

Điểm đánh giá dùng để phân tầng nguồn, không dùng để loại tự động.

### 2.4. Số lượng nhiệm vụ phải đi ra từ ma trận bao phủ

Không nên trả lời “có 7 nhiệm vụ vì F01 có 7 nhiệm vụ”. Số nhiệm vụ nên được suy ra từ:

```text
năng lực gia sư x vùng kiến thức x kiểu tương tác
```

Sau đó mới gộp/tách thành nhóm nhiệm vụ. Mỗi nhiệm vụ cần ghi rõ nó bao phủ gì và chưa bao phủ gì.

### 2.5. Tiêu chí “học sinh hấp thụ kiến thức đến đâu” cần tách dấu hiệu gần và kết quả học tập

Nếu chỉ nhìn một phản hồi của gia sư, ta không đo trực tiếp được tiến bộ học tập. Nên tách ba mức:

- Chất lượng phản hồi: phản hồi có kiểm tra hiểu biết và gợi bước tiếp theo không?
- Dấu hiệu tiếp nhận: trong nhiều lượt, học sinh có sửa, diễn đạt lại, hỏi sâu hơn không?
- Kết quả học tập: cần kiểm tra trước/sau hoặc bằng chứng dài hơn.

Tiêu chí chấm trước mắt có thể đo chất lượng phản hồi và dấu hiệu tiếp nhận, nhưng không nên tuyên bố đo tiến bộ học tập thật.

### 2.6. Tiền kiến thức lớp 6-8 cần có, nhưng không nên mở rộng thành toàn bộ THCS ngay

Nên thêm nhãn tiền kiến thức cho mẫu và học liệu. Chỉ nhập lớp 6-8 ở mức phục vụ Tin học 9. Không mở rộng bộ đánh giá chính sang toàn bộ THCS trước khi Tin học 9 ổn định.

### 2.7. Quy trình giáo viên đưa dữ liệu, UET gọi mô hình, giáo viên chấm nên để sau

Phần này nên để lại sau khi đã xác định rõ các trường dữ liệu và các trường này đã được HNMU duyệt. Khi đó ta mới biết trường nào do HNMU chuẩn bị, trường nào do UET bổ sung, trường nào do mô hình sinh, và trường nào do giáo viên chấm.

Khi quay lại phần này, cần phân biệt tối thiểu:

- dữ liệu đầu vào của mẫu do giáo viên và UET thiết kế;
- phản hồi của mô hình do UET chạy;
- điểm và quyết định do giáo viên chấm;
- phản hồi tham khảo nếu có chỉ để minh họa, không phải “đáp án duy nhất”.

Không nên để công cụ chạy mô hình quyết định ngược cấu trúc mẫu. Công cụ chỉ nên vào sau khi nhiệm vụ, tiêu chí chấm và trường dữ liệu đã đủ ổn.

### 2.8. Cơ sở dữ liệu học liệu là đúng, nhưng nên làm danh mục quản lý v0 trước

Cơ sở dữ liệu đầy đủ là cần thiết về lâu dài. Nhưng trong 1-2 tuần tới, ưu tiên nên là rà soát nghiên cứu. Danh mục học liệu có cấu trúc chỉ nên làm song song nếu còn thời gian. Danh mục này nên có: nguồn, phiên bản, mã băm, đoạn học liệu, lớp, chủ đề, tiền kiến thức và trạng thái. Sau khi hợp đồng dữ liệu ổn mới chuyển sang P06 cơ sở dữ liệu.

## 3. Nguyên tắc làm việc mới

1. Không coi F01 là bộ đánh giá v1.
2. Chỉ dùng F01 làm tài liệu tham khảo/đối chiếu; không lấy nguyên nhiệm vụ, tiêu chí chấm, mẫu, lỗi nghiêm trọng hoặc trường dữ liệu từ F01 nếu chưa có luận giải mới.
3. Không tiếp tục vá nhiệm vụ/tiêu chí chấm F01 như sản phẩm chính.
4. Viết khung lý thuyết trước danh sách nhiệm vụ.
5. Mọi nhiệm vụ, tiêu chí chấm và trường dữ liệu phải có luận giải.
6. Luận giải phải tách bằng chứng, suy luận thiết kế và quyết định giáo viên.
7. Tạm hoãn quy trình sinh phản hồi mô hình cho tới khi HNMU duyệt trường dữ liệu.
8. Giữ Tin học lớp 9 là phạm vi thử nghiệm trong giai đoạn này, ít nhất 3-6 tháng tới; thiết kế kiến trúc có thể mở rộng sau.

## 4. Giả định nguồn lực

- Người phụ trách dự án: từ nay tới tuần đầu tháng 8 chỉ khoảng 4 giờ trong tuần, thêm thời gian đệm cuối tuần. Nên đặt đường găng tối đa 8-10 giờ/tuần.
- Sinh viên: tới 15/07 khoảng 2 giờ/tuần; sau 15/07 khoảng 6 giờ/tuần.
- Sau tuần đầu tháng 8, người phụ trách dự án có thể tăng lên toàn thời gian.

## 5. Lịch đề xuất

Cập nhật theo ghi chú ngày 27/06: đã có thể mở thử nghiệm mới cho hướng sau HNMU. Cụm việc 27/06-30/06 có thể triển khai nhanh trong một ngày vì chủ yếu là chốt định nghĩa, viết tài liệu nền và chuẩn bị câu hỏi cho HNMU. Nếu phát sinh thay đổi code, kiến trúc hoặc quy trình chạy tự động, vẫn cần plan có trạng thái `APPROVED` trước khi triển khai.

Mục tiêu trong giai đoạn 29/06-15/07 nên được gọi chính xác là **rà soát nghiên cứu lõi có kiểm soát để dựng nền tảng lý thuyết v0**. Khoảng thời gian này là đủ nếu phạm vi được giữ chặt: ưu tiên gia sư LLM/AI, phản hồi học tập, chẩn đoán hiểu sai, gợi mở từng bước, đánh giá phản hồi và bối cảnh K-12/Tin học khi có. Khoảng thời gian này không đủ cho một tổng quan hệ thống đầy đủ theo nghĩa học thuật xuất bản được.

Phần học liệu/chương trình không nên chờ tới 16/07 mới bắt đầu từ con số 0. Link tập huấn HNMU/NXBGD cho Tin học 9 đang là nguồn web có khả năng phải xử lý ảnh/OCR, nên trong giai đoạn 29/06-15/07 cần chuẩn bị tối thiểu: xác nhận nguồn, liệt kê tài liệu con, kiểm tra cách lưu ảnh, thử OCR một mẫu nhỏ và ghi rủi ro chất lượng. Tuần 16/07-21/07 vẫn là tuần chốt danh mục học liệu v0, nhưng phải được bẻ nhỏ để không trễ deadline 21/07.

### 27/06-28/06 — Mở thử nghiệm mới và chốt hướng sau HNMU


| Việc | Người phụ trách | Sản phẩm |
|---|---|---|
| Mở thử nghiệm mới cho hướng sau HNMU | Người phụ trách dự án + Codex | thư mục thử nghiệm mới |
| Hạ cấp F01 thành bản mẫu giao tiếp/lịch sử | Người phụ trách dự án | `f01_retrospective.md` |
| Định nghĩa gia sư, bộ đánh giá, nhiệm vụ, tiêu chí chấm, mẫu, lỗi nghiêm trọng | Người phụ trách dự án + Codex | `benchmark_problem_definition_v0.md` |
| Lập câu hỏi cần HNMU chốt | Người phụ trách dự án | `hnmu_decision_questions.md` |

Tiêu chí hoàn thành:

- Có định nghĩa bộ đánh giá ngắn, rõ, không lẫn giáo viên/trợ giảng.
- Có danh sách phần F01 giữ/làm lại/bỏ.
- Có câu hỏi gửi HNMU.
- Có thử nghiệm mới để tách hướng sau HNMU khỏi F01/C01.

### 29/06-05/07 — Quy trình rà soát nghiên cứu và bảng chấm giá trị bài báo


| Việc | Người phụ trách | Sản phẩm |
|---|---|---|
| Viết câu hỏi rà soát và quy trình rà soát | Người phụ trách dự án + Codex | `literature_review_protocol_v0.md` |
| Thiết kế bảng chấm giá trị bài báo | Người phụ trách dự án | `paper_quality_and_relevance_scorecard.md` |
| Lập danh mục bài báo hạt giống độc lập với F01 | Người phụ trách dự án + Sinh viên | `seed_paper_registry.csv` |
| Chốt cấu trúc ma trận bằng chứng v2 | Người phụ trách dự án + Codex | `evidence_matrix_v2_schema.md` |
| Chuẩn bị sớm nguồn học liệu ảnh/OCR ở mức thăm dò | Sinh viên + Codex | `learning_resource_source_probe_v0.md` |

Tiêu chí hoàn thành:

- Có quy trình rà soát với câu hỏi tìm kiếm, tiêu chí chọn/loại và điểm dừng.
- Có bảng chấm giá trị bài báo nhiều chiều.
- Có danh mục bài báo hạt giống được lập từ câu hỏi rà soát, truy vấn tìm kiếm, nguồn gợi ý độc lập và lần theo trích dẫn; F01 chỉ dùng để đối chiếu xem có bỏ sót ý quan trọng, không dùng làm nguồn chọn chính.
- Có phạm vi đủ hẹp để hoàn thành nền tảng lý thuyết v0 vào ngày 15/07; nếu danh mục nguồn phình quá rộng thì ưu tiên nguồn lõi thay vì cố bao quát hết.
- Có ghi chú thăm dò nguồn học liệu ảnh/OCR: đường dẫn nguồn, tài liệu con, cách tải/lưu ảnh dự kiến, một mẫu OCR thử và rủi ro chất lượng.

### 06/07-15/07 — Rà soát lõi và nền tảng lý thuyết v0


| Việc | Người phụ trách | Sản phẩm |
|---|---|---|
| Rà soát sâu 15-25 nguồn lõi, tùy chất lượng nguồn tìm được | Người phụ trách dự án + Codex | `core_evidence_matrix_v0.csv` |
| Tổng hợp mô hình năng lực gia sư | Người phụ trách dự án | `tutor_capability_model_v0.md` |
| Viết nền tảng lý thuyết v0 cho khung đánh giá | Người phụ trách dự án + Codex | `theoretical_foundation_v0.md` |
| Kiểm tra DOI/URL/thông tin mô tả | Sinh viên | danh mục sạch |
| Tách năng lực chung và năng lực theo miền Tin học | Người phụ trách dự án + Codex | một mục trong mô hình năng lực |
| Chuẩn bị khung danh mục đầu mục học liệu từ nguồn HNMU | Sinh viên + Codex | nháp `learning_resource_toc_v0.csv` |

Tiêu chí hoàn thành:

- Có 5-8 năng lực gia sư ứng viên.
- Mỗi năng lực có bằng chứng hoặc được gắn nhãn khoảng trống bằng chứng.
- Có ghi rõ không suy tiến bộ học tập thật từ một lượt phản hồi.
- Mỗi năng lực trong khung v0 truy được tới nguồn nghiên cứu, nguồn chương trình/học liệu hoặc được ghi rõ là quyết định thiết kế cần HNMU xác nhận.
- Có bản tổng hợp đủ chắc để bước sau suy ra nhóm nhiệm vụ và tiêu chí chấm, nhưng chưa tự nhận là tổng quan hệ thống đầy đủ.
- Có nháp danh sách đầu mục học liệu đủ để tuần 16/07-21/07 tập trung OCR, kiểm tra và gắn mã thay vì vừa tìm nguồn vừa xử lý.

### 16/07-21/07 — Danh mục quản lý học liệu/chương trình v0 từ nguồn ảnh/OCR

Nguồn ưu tiên: trang tập huấn Tin học 9 của NXBGD/HNMU (`https://taphuan.nxbgd.vn/tap-huan/chi-tiet-sach/tin-hoc-9-940119364.940119364`) và các tài liệu con liên quan. Vì nguồn này có khả năng hiển thị dưới dạng ảnh hoặc trình đọc web, cần lưu bản nguồn, chạy OCR có kiểm tra và tạo danh sách đầu mục trước khi gắn mã đoạn học liệu.


| Việc | Người phụ trách | Sản phẩm |
|---|---|---|
| 16/07: Chốt danh sách tài liệu con và cách lưu bản nguồn | Sinh viên + Codex | `learning_resource_capture_manifest_v0.csv` |
| 17/07: Lưu ảnh/trang nguồn và chạy OCR thử toàn bộ hoặc phần ưu tiên | Sinh viên + Codex | thư mục ảnh nguồn + `ocr_raw/` |
| 18/07: Tạo danh sách đầu mục theo bài/mục/trang/hình/bảng/câu hỏi/thực hành | Sinh viên | `learning_resource_toc_v0.csv` |
| 19/07: Gắn mã học liệu/đoạn học liệu và thông tin phiên bản | Người phụ trách dự án + Codex | `learning_resource_registry_v0.csv`, `learning_material_id_convention.md` |
| 20/07: Ánh xạ Tin học 9 và tiền kiến thức lớp 6-8 | Người phụ trách dự án + Sinh viên | `curriculum_knowledge_map_v0.csv` |
| 21/07: Kiểm tra mẫu OCR, ghi lỗi còn lại và chốt danh mục v0 | Người phụ trách dự án + Sinh viên | `ocr_quality_notes_v0.md`, danh mục v0 đã rà soát |

Tiêu chí hoàn thành:

- Mỗi học liệu có nguồn, URL/đường dẫn, phiên bản/trạng thái và mã băm nếu có.
- Có quy tắc mã đoạn học liệu dễ đọc cho giáo viên.
- Có cột tiền kiến thức.
- Có bản lưu nguồn hoặc chỉ dẫn lưu nguồn đủ rõ để tái kiểm tra.
- Có ghi chú chất lượng OCR: phần nào đọc tốt, phần nào cần sửa tay, phần nào chưa dùng làm căn cứ benchmark.

### 22/07-28/07 — Khung đánh giá gia sư v0


| Việc | Người phụ trách | Sản phẩm |
|---|---|---|
| Xây ma trận năng lực x vùng kiến thức x kiểu tương tác | Người phụ trách dự án + Codex | `coverage_matrix_v0.csv` |
| Viết luận giải khung đánh giá | Người phụ trách dự án | `benchmark_framework_rationale_v0.md` |
| Xác định nhóm nhiệm vụ ứng viên | Người phụ trách dự án | `task_family_candidates_v0.md` |
| Ghi câu hỏi mở cho HNMU | Người phụ trách dự án | một mục trong khung đánh giá |

Tiêu chí hoàn thành:

- Số nhiệm vụ không còn là số cảm tính.
- Mỗi nhóm nhiệm vụ có năng lực gia sư, vùng kiến thức, bằng chứng và giới hạn.
- Có giải thích vì sao giữ/gộp/tách nhiệm vụ.

### 29/07-04/08 — Tiêu chí chấm, lỗi nghiêm trọng và hợp đồng trường dữ liệu v0


| Việc | Người phụ trách | Sản phẩm |
|---|---|---|
| Suy tiêu chí chấm từ mô hình năng lực gia sư | Người phụ trách dự án + Codex | `rubric_rationale_v0.md` |
| Thiết kế chính sách lỗi nghiêm trọng v0 | Người phụ trách dự án + Codex | `critical_failure_policy_v0.md` |
| Thiết kế trường dữ liệu tối thiểu của mẫu | Người phụ trách dự án + Codex | `sample_metadata_contract_v0.md` |
| Ghi phần trường dữ liệu F01 có thể tham khảo, cần sửa hoặc cần loại | Sinh viên | `f01_field_reference_notes.md` |

Tiêu chí hoàn thành:

- Mỗi tiêu chí chấm trả lời “vì sao cần tiêu chí này”.
- Mỗi lỗi nghiêm trọng có tiêu chí bị ảnh hưởng và hướng dẫn quyết định.
- Trường dữ liệu có ý nghĩa, định dạng, bắt buộc/tùy chọn, luận giải.

### 05/08-11/08 — Gói rà soát khung đánh giá v2 cho HNMU


| Việc | Người phụ trách | Sản phẩm |
|---|---|---|
| Viết tài liệu tiếng Việt dễ đọc cho HNMU | Người phụ trách dự án + Codex | `teacher_framework_review_packet_v2/` |
| Tạo phiếu rà soát nhiệm vụ/tiêu chí chấm/trường dữ liệu | Người phụ trách dự án + Sinh viên | biểu mẫu/bảng tính |
| Chuẩn bị 2-3 ví dụ minh họa mới | Người phụ trách dự án + HNMU nếu kịp | ví dụ v0 |
| Gửi HNMU trước buổi rà soát | Người phụ trách dự án | bàn giao/email |

Tiêu chí hoàn thành:

- HNMU có thể rà soát mà không cần hiểu mã nguồn/cấu trúc kỹ thuật.
- Phiếu rà soát có chỗ ghi đồng ý/sửa/loại và lý do.
- Có ví dụ tốt và phản ví dụ cho nhiệm vụ khó.

### 12/08-25/08 — Thử nghiệm nhỏ với giáo viên


| Việc | Người phụ trách | Sản phẩm |
|---|---|---|
| Chọn 2-3 nhóm nhiệm vụ để thử nghiệm | Người phụ trách dự án + HNMU | phạm vi thử nghiệm |
| Giáo viên tạo dữ liệu đầu vào của mẫu | HNMU | dữ liệu mẫu thô |
| UET chạy phản hồi mô hình, chỉ khi trường dữ liệu đã được duyệt | Người phụ trách dự án | tập phản hồi |
| Giáo viên chấm tiêu chí độc lập | HNMU | phiếu chấm |
| Phân tích bất đồng | Người phụ trách dự án + Sinh viên | `pilot_analysis.md` |

Tiêu chí hoàn thành:

- Có 8-12 mẫu thử nghiệm có rà soát độc lập.
- Có danh sách tiêu chí chấm/nhiệm vụ/trường dữ liệu cần sửa.
- Có quyết định tiếp tục, sửa lớn hoặc bỏ nhiệm vụ.

### 26/08-08/09 — Chốt khung đánh giá v1 ứng viên


| Việc | Người phụ trách | Sản phẩm |
|---|---|---|
| Sửa khung đánh giá theo thử nghiệm | Người phụ trách dự án + Codex | `benchmark_framework_v1_candidate.md` |
| Sửa tiêu chí chấm/lỗi nghiêm trọng | Người phụ trách dự án | tài liệu cập nhật |
| Viết nháp plan P05/P06 | Người phụ trách dự án + Codex | nháp plan |
| Viết báo cáo cho giáo sư/HNMU | Người phụ trách dự án | `post_pilot_report.md` |

Tiêu chí hoàn thành:

- Khung đánh giá có luận giải từ nghiên cứu/chương trình/học liệu.
- Có bằng chứng thử nghiệm từ giáo viên.
- Có quyết định rõ về cơ sở dữ liệu và quy trình đánh giá tiếp theo.

## 6. Phân vai

### Người phụ trách dự án

- Chốt phạm vi, khung đánh giá và quyết định thiết kế.
- Viết định nghĩa bài toán, mô hình năng lực gia sư, luận giải khung đánh giá.
- Là đầu mối HNMU.
- Rà soát sản phẩm của sinh viên.
- Quyết định khi nào chạy mô hình/Kaggle.

### Sinh viên mới

- Làm danh mục quản lý, làm sạch thông tin mô tả, kiểm tra DOI/URL, liệt kê học liệu.
- Hỗ trợ lưu nguồn học liệu dạng ảnh, chạy OCR thô, tạo danh sách đầu mục và ghi lỗi chất lượng để người phụ trách dự án rà soát.
- Chuẩn hóa bảng theo mẫu biểu.
- Không tự chốt nhiệm vụ, tiêu chí chấm hoặc logic nghiên cứu.

### Codex

- Hỗ trợ tổng hợp bằng chứng, viết nháp luận giải, tạo mẫu biểu và kiểm tra tính nhất quán.
- Không thay giáo viên quyết định đúng/sai chuyên môn.
- Không gọi nhiều chuyên gia phụ trùng vai nếu chưa được duyệt.

### HNMU

- Xác nhận thuật ngữ, mức lớp, học liệu, ví dụ và tính phù hợp sư phạm.
- Rà soát nhiệm vụ, tiêu chí chấm và trường dữ liệu.
- Viết hoặc rà soát dữ liệu đầu vào của mẫu.
- Chấm phản hồi của mô hình và phân xử bất đồng.

## 7. Sản phẩm nên tạo trong thử nghiệm mới

Vì đã chốt có thể mở thử nghiệm mới, thử nghiệm này nên tách rõ phần nền tảng lý thuyết và phần học liệu/OCR để tránh lẫn với F01/C01, ví dụ:

```text
plans/
  01-problem-definition-and-framework.md
  02-literature-review-protocol-v2.md
  03-learning-resource-capture-and-ocr-v0.md
  04-task-rubric-metadata-rationale.md
outputs/
  benchmark_problem_definition_v0.md
  literature_review_protocol_v0.md
  paper_quality_and_relevance_scorecard.md
  core_evidence_matrix_v0.csv
  tutor_capability_model_v0.md
  theoretical_foundation_v0.md
  learning_resource_source_probe_v0.md
  learning_resource_capture_manifest_v0.csv
  learning_resource_toc_v0.csv
  learning_resource_registry_v0.csv
  learning_material_id_convention.md
  research_id_convention.md
  curriculum_knowledge_map_v0.csv
  ocr_quality_notes_v0.md
  benchmark_framework_rationale_v0.md
  coverage_matrix_v0.csv
  task_family_candidates_v0.md
  rubric_rationale_v0.md
  critical_failure_policy_v0.md
  sample_metadata_contract_v0.md
reports/
  f01_retrospective.md
  hnmu_decision_questions.md
source_snapshots/
  raw_images_or_pages/
  ocr_raw/
```

## 8. Rủi ro chính


| Rủi ro | Cách giảm |
|---|---|
| Phạm vi phình sang mọi môn/cấp học | Giữ Tin học 9 là phạm vi thử nghiệm trong 3-6 tháng tới. |
| Rà soát nghiên cứu quá rộng | Dùng quy trình rà soát, điểm dừng và bảng chấm giá trị bài báo. |
| Làm cơ sở dữ liệu quá sớm | 29/06-15/07 tập trung nền tảng lý thuyết; chỉ làm thăm dò nguồn học liệu/OCR để chuẩn bị cho tuần 16/07-21/07, chưa dựng cơ sở dữ liệu đầy đủ. |
| Nguồn học liệu dạng ảnh làm chậm tiến độ | Chuẩn bị thăm dò từ 29/06, lưu nguồn có hệ thống, chạy OCR mẫu sớm, bẻ tuần 16/07-21/07 thành capture/OCR/mục lục/mã học liệu/QA. |
| OCR sai nhưng bị dùng như căn cứ chắc chắn | Ghi `ocr_quality_notes_v0.md`, đánh dấu phần cần sửa tay hoặc chưa được dùng làm căn cứ bộ đánh giá. |
| Tiêu chí chấm đo tiến bộ học tập quá mạnh | Tách chất lượng phản hồi, dấu hiệu tiếp nhận và kết quả học tập thật. |
| Sinh viên bị giao việc quá khó | Giao danh mục, làm sạch dữ liệu, kiểm tra danh sách yêu cầu; người phụ trách dự án rà soát logic. |
| HNMU rà soát quá muộn | Gửi định nghĩa bài toán và mô hình năng lực gia sư sớm. |
| Công cụ chạy mô hình quyết định ngược cấu trúc mẫu | Chỉ chạy mô hình sau khi cấu trúc mẫu/trường dữ liệu đã được HNMU duyệt. |

## 9. Quyết định cần chốt hoặc để lại

| Ý | Trạng thái hiện tại | Ghi chú |
|---|---|---|
| 1. Có tạo thử nghiệm mới cho hướng sau HNMU không? | Có thể chốt ngay | Mở thử nghiệm mới để tách hướng sau HNMU khỏi F01/C01 và quản lý riêng nền tảng lý thuyết, học liệu/OCR, khung đánh giá. |
| 2. Có hạ F01 thành bản mẫu giao tiếp/lịch sử, chỉ dùng để tham khảo và không tiếp tục vá nhiệm vụ/tiêu chí chấm F01 không? | Có thể chốt ngay | Nên chốt để tránh tiếp tục vá hoặc bê nguyên một nền không đủ chắc. |
| 3. Mốc rà soát đầu tiên với HNMU nên là sau định nghĩa bài toán hay sau mô hình năng lực gia sư? | Tạm thời chưa chốt | Cần cân nhắc lịch của HNMU và mức độ hoàn thiện tài liệu. |
| 4. Có giữ Tin học lớp 9 là phạm vi thử nghiệm không? | Có thể chốt trong giai đoạn này | Nên giữ ít nhất 3-6 tháng tới; sau đó có thể mở rộng. |
| 5. Có ưu tiên danh mục/cơ sở dữ liệu học liệu song song với rà soát nghiên cứu không? | Làm song song ở mức thăm dò, chưa dựng cơ sở dữ liệu đầy đủ | Từ 29/06-15/07 chỉ chuẩn bị nguồn, OCR mẫu và khung danh sách đầu mục; 16/07-21/07 chốt danh mục học liệu v0. |

## 10. Khuyến nghị

Nên ưu tiên mục tiêu đầu tiên là **Định nghĩa bài toán + Khung năng lực gia sư**, không phải danh sách nhiệm vụ. Đây là điểm HNMU đang đòi hỏi: thiếu logic nội hàm trước nhiệm vụ/tiêu chí chấm. Khi khung đã rõ, nhiệm vụ, tiêu chí chấm và trường dữ liệu sẽ có nền để tranh luận và hiệu chỉnh.

Trong 2 tuần đầu, nên gửi HNMU một tài liệu ngắn trả lời ba câu:

1. Bộ đánh giá này đánh giá điều gì ở một gia sư?
2. Vì sao Tin học lớp 9 là phạm vi thử nghiệm chứ không phải toàn bộ bản chất bài toán?
3. Mỗi nhiệm vụ/tiêu chí chấm sau này sẽ được sinh từ khung lý thuyết theo quy tắc nào?
