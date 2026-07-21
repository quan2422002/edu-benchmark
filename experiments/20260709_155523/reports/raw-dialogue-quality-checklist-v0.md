# Checklist kiểm định dữ liệu thô HNMU v0

Experiment: `20260709_155523`
Nguồn gốc: tách từ `benchmark-quality-checklist-v0.md` ngày 17/07/2026
Dùng cho: Plan 04 — kiểm toán dữ liệu hội thoại thô HNMU
Trạng thái: `v0_for_raw_dialogue_audit`

## 1. Phạm vi sử dụng

Checklist này chỉ dùng để kiểm dữ liệu thô do HNMU gửi, trước khi chuyển đổi thành mẫu benchmark. Ở giai đoạn này, dữ liệu chưa có các trường benchmark như `student_prompt`, `conversation_history`, `gold_response`, task/rubric chính thức hay mẫu chấm model.

Agent hoặc người kiểm chỉ được đánh giá những gì có thật trong dữ liệu thô:

- lớp;
- bài học/vị trí do HNMU ghi;
- câu hỏi;
- mức nhận thức;
- đáp án SGV;
- hội thoại gia sư theo phương pháp dàn giáo;
- truy vết file/sheet/dòng gốc;
- evidence học liệu SGK/SGV truy xuất được từ registry, fragment hoặc index.

Không dùng checklist này để chấm model và không dùng để phê duyệt mẫu benchmark cuối cùng.

## 2. Căn cứ


| Căn cứ          | Bài học dùng cho kiểm dữ liệu thô                                                                                                                                                                        |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| MathTutorBench    | Cần kiểm chất lượng gia sư trong hội thoại, không chỉ đúng đáp án. Với dữ liệu thô, trọng tâm là hội thoại có dấu hiệu hiểu học sinh, gợi mở và hỗ trợ đúng hướng không. |
| KMP-Bench         | Cần phát hiện hội thoại lỗi, trình tự sư phạm kém, lượt thừa, học liệu bịa hoặc flow có rủi ro.                                                                                             |
| TutorBench        | Dữ liệu nên được chuyên gia tạo/kiểm tra; agent chỉ hỗ trợ phát hiện lỗi và tạo hàng đợi review.                                                                                            |
| VietLegal/V-Legal | Cần nguồn chính thức, truy vết nguồn, kiểm trùng/rò rỉ và cơ chế review/phân xử. Với dự án này, SGK/SGV là nguồn học liệu chính thức.                                                  |

## 3. Output tối thiểu cho mỗi dòng dữ liệu thô

Checklist này có hai lớp output:

1. `raw_dialogue_checklist_results.csv`: kết quả chi tiết từng tiêu chí cho từng mẫu.
2. `agent_shard_audit/merged/quality_check_suggestions.csv`: kết luận tổng hợp chính theo mẫu sau agent audit.

Bảng chi tiết là bắt buộc cho phần agent kiểm ngữ nghĩa, vì nó giúp truy vết vì sao một mẫu được kết luận `pass`, `failed` hoặc `need_human_review`.

### 3.1. Bảng chấm từng tiêu chí: `raw_dialogue_checklist_results.csv`

Mỗi dòng là một cặp `sample_id` + `criterion_id`. Không dùng dạng mỗi mẫu một dòng với quá nhiều cột, vì danh sách tiêu chí có thể thay đổi theo thời gian.

| Trường | Ý nghĩa |
|---|---|
| `sample_id` | Mã mẫu thô được kiểm. |
| `criterion_id` | Mã tiêu chí, ví dụ `RAW-CON-01`, `RAW-PED-03`. |
| `criterion_group` | Nhóm tiêu chí, ví dụ `structure`, `consistency`, `pedagogy`, `duplicate_risk`. |
| `criterion_name` | Tên ngắn của tiêu chí. |
| `result` | `pass`, `fail`, `uncertain`, hoặc `not_applicable`. |
| `confidence_score` | Mức tự tin cho riêng tiêu chí đó. |
| `evidence_fragment_id` | Fragment học liệu dùng làm căn cứ, nếu có. |
| `evidence_source` | Đường dẫn hoặc mô tả nguồn evidence. |
| `evidence_match_reason` | Vì sao evidence được xem là liên quan. |
| `reason` | Lý do kết luận tiêu chí bằng tiếng Việt. |
| `suggested_reviewer_action` | `keep`, `ask_hnmu_review`, `exclude_from_current_batch`, hoặc `needs_uet_decision`. |
| `checked_by` | `code`, tên agent, hoặc người kiểm. |
| `checked_at` | Thời điểm kiểm, dùng định dạng ISO nếu có thể. |

Quy ước hiển thị: nếu cần giao diện dễ đọc, có thể hiển thị `pass` thành `o` và `fail` thành `x`. Tuy nhiên trong CSV nên lưu bằng chữ để tránh hiểu nhầm; `uncertain` và `not_applicable` không nên ép thành `o/x`.

### 3.2. Bảng tổng hợp chính theo mẫu: `quality_check_suggestions.csv`

Trong output Plan 04 có thể vẫn tồn tại `quality_check_results.csv` ở root output. File đó là kết quả nhanh từ code kiểm cơ học/truy xuất sơ bộ, không phải file review chính sau agent audit.

File chính để Quân/UET/HNMU review ở cấp từng mẫu sau agent audit là:

```text
agent_shard_audit/merged/quality_check_suggestions.csv
```

| Trường dẫn xuất                | Ý nghĩa                                                                                  |
| ---------------------------------- | ------------------------------------------------------------------------------------------ |
| `sample_id`                        | Mã mẫu thô, truy vết về file/sheet/dòng gốc.                                        |
| `source_file`, `source_row_number` | Nguồn gốc vật lý của dòng dữ liệu.                                                 |
| `grade`, `lesson`                  | Khối lớp và bài học đã chuẩn hóa từ dữ liệu thô/registry học liệu.                 |
| `quality_decision`                 | `pass`, `need_human_review`, hoặc `failed`.                                                |
| `confidence_score`                 | Độ tin cậy của quyết định tổng thể, từ 0.00 đến 1.00. Đây không phải điểm chất lượng của mẫu. |
| `failure_reasons`                  | Lý do mẫu không đạt hoặc cần xem lại.                                              |
| `blocking_criterion_ids`           | Các tiêu chí trực tiếp khiến mẫu bị `failed` hoặc `need_human_review`. Với mẫu `pass`, cột này để trống. |
| `suggested_reviewer_action`        | `keep`, `ask_hnmu_review`, `exclude_from_current_batch`, hoặc `needs_uet_decision`.       |
| `needs_hnmu_review`                | `true` nếu mẫu cần HNMU/UET xem lại trước khi chuyển đổi.                           |
| `needs_sgv_verification`           | `true` nếu kiểm đáp án cần SGV nhưng không tìm được evidence phù hợp, evidence mâu thuẫn hoặc quá mơ hồ. |
| `needs_learning_resource_review`   | `true` nếu evidence SGK/SGV còn mơ hồ, chưa có, hoặc có dấu hiệu lệch/mâu thuẫn. Fragment `draft` nhưng khớp metadata + nội dung thì không tự động bật cờ này. |
| `evidence_fragment_ids`            | Các fragment học liệu liên quan trực tiếp tới tiêu chí chặn, nếu có.               |
| `checked_by`, `checked_at`         | Ai/cơ chế nào đồng bộ kết quả và thời điểm đồng bộ.                                  |
| `source_shard`                     | Shard agent tạo ra mẫu đánh giá, nếu có.                                              |

Từ ngày 20/07/2026, các batch Plan 04 phải dùng cùng schema canonical cho `quality_check_suggestions.csv`. Không dùng lại các cột legacy như `quality_decision_suggestion`, `suggested_quality_decision`, `main_failure_reasons` hoặc `source_checklist_rows` trong file chính hiện hành.

## 4. Quy tắc quyết định


| Quyết định        | Dùng khi nào                                                                                                                                                                             | Hành động mặc định                                                        |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------- |
| `pass`               | Đủ trường lõi, không thấy lỗi định dạng rõ, hội thoại bám câu hỏi/đáp án, có evidence học liệu đủ dùng, không có dấu hiệu trùng/gần trùng nghiêm trọng. | Có thể đưa sang danh sách chờ chuyển đổi thử ở Plan 06.              |
| `need_human_review` | Có rủi ro ngữ nghĩa, evidence mơ hồ, mức nhận thức chưa chắc, hội thoại có dấu hiệu sư phạm cần HNMU/UET xem lại.                                                      | Đưa vào hàng đợi review.                                                  |
| `failed`             | Thiếu trường lõi, hội thoại không có giá trị, câu hỏi/đáp án/hội thoại lệch rõ, hoặc lỗi nghiêm trọng không thể dùng trong batch hiện tại.                     | Loại khỏi batch chuyển đổi hiện tại, trừ khi HNMU sửa/xác nhận lại. |

Điểm tự tin không thay thế quyết định chuyên môn. Nếu có lỗi nghiêm trọng, mẫu không được tự động `pass` dù `confidence_score` cao.

Quy tắc tổng hợp bắt buộc từ checklist chi tiết sang quyết định cấp mẫu:

1. Nếu mẫu có ít nhất một tiêu chí `fail` → quyết định tổng thể là `failed`.
2. Nếu mẫu không có `fail` nhưng có ít nhất một tiêu chí `uncertain` → quyết định tổng thể là `need_human_review`.
3. Nếu toàn bộ tiêu chí là `pass` hoặc `not_applicable` → quyết định tổng thể là `pass`.

Quy tắc này áp dụng cho kết quả agent audit và hàng đợi HNMU/UET xem lại. Nói cách khác, một mẫu không được ở trạng thái `pass` nếu vẫn còn tiêu chí `fail` hoặc `uncertain`.


| Khoảng điểm | Cách hiểu                                                  | Hành động đề xuất                       |
| -------------- | ------------------------------------------------------------ | --------------------------------------------- |
| `>= 0.80`      | Tương đối chắc nếu không có cờ lỗi nghiêm trọng. | Có thể giữ trong batch chuyển đổi thử. |
| `0.50–0.79`   | Có điểm chưa chắc hoặc cần thêm evidence.            | Nên đưa vào review nếu mẫu quan trọng. |
| `< 0.50`       | Rủi ro cao hoặc thiếu căn cứ.                           | Đưa vào`hnmu_review_queue.csv`.            |

## 5. Checklist cấp batch


| Mã        | Tiêu chí                     | Cách kiểm                                                                                                                                                                              | Công cụ chính           | Output                      |
| ---------- | ------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------- | --------------------------- |
| RAW-COV-01 | Phủ khối lớp                | Đếm số mẫu theo lớp trong phạm vi audit.                                                                                                                                           | Code                       | `coverage_summary.csv`      |
| RAW-COV-02 | Phủ chủ đề SGK/SGV         | Ánh xạ trường`Bài` sang `sgk_thcs_topic_lesson_map_v0.csv`; chủ đề lấy từ SGK/SGV, không lấy dữ liệu thô làm chuẩn.                                                     | Code + registry học liệu | `coverage_summary.csv`      |
| RAW-COV-03 | Phủ bài học theo lớp       | Đếm theo`lesson_by_grade`; mỗi bài phải kèm lớp vì bài học phụ thuộc từng lớp.                                                                                             | Code + registry học liệu | `coverage_summary.csv`      |
| RAW-COV-04 | Phủ mức nhận thức          | Chuẩn hóa `Mức Bloom` về ba mức trong tài liệu HNMU: Biết, Hiểu, Vận dụng; nếu dữ liệu thô ghi Nhận biết/Thông hiểu thì ánh xạ tương ứng về Biết/Hiểu. | Code | `coverage_summary.csv` |
| RAW-COV-05 | Phủ dạng câu hỏi/bài tập | Nếu dữ liệu có hoặc agent gán được nhãn, thống kê dạng bài: trắc nghiệm, tự luận lý thuyết, sửa lỗi code, viết chương trình, bài làm học sinh, dạng khác. | Code + agent khi mơ hồ   | Báo cáo coverage bổ sung |
| RAW-COV-06 | Phân bố có chủ đích      | Không yêu cầu đều tuyệt đối; vùng nhiều/ít mẫu phải giải thích được theo SGK/SGV và mục tiêu benchmark.                                                             | Người điều phối       | Nhận xét trong báo cáo  |

## 6. Checklist thiếu trường và định dạng


| Mã        | Tiêu chí                       | Cách kiểm                                                                                             | Quyết định mặc định                                                        |
| ---------- | -------------------------------- | ------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| RAW-STR-01 | Có đủ cột bắt buộc         | Kiểm các cột`Bài`, `Vị trí`, `Câu hỏi`, `Mức Bloom`, `Đáp án (SGV)`, `Hội thoại gia sư`. | Thiếu cột lõi ở file/batch → dừng hoặc`fail` cấp batch.                  |
| RAW-STR-02 | Không thiếu trường lõi      | Kiểm ô trống ở câu hỏi, đáp án, hội thoại.                                                   | Thiếu câu hỏi/hội thoại →`fail`; thiếu đáp án → `need_human_review`. |
| RAW-STR-03 | Có nhãn lượt nói            | Kiểm nhãn như`HS:` và `AI:` hoặc pattern tương đương.                                         | Thiếu nhãn →`need_human_review`.                                             |
| RAW-STR-04 | Hội thoại đủ dài để kiểm | Kiểm số lượt, độ dài ký tự/từ, tránh hội thoại quá ngắn.                                 | Quá ngắn →`need_human_review` hoặc `fail`.                                  |
| RAW-STR-05 | Có truy vết dòng gốc         | Gắn file, sheet, row index, batch ID.                                                                  | Thiếu truy vết → chưa chuyển đổi.                                         |
| RAW-STR-06 | Không sửa raw data             | Mọi chuẩn hóa phải tạo bản dẫn xuất.                                                            | Nếu phát hiện sửa file gốc → dừng kiểm toán.                            |

## 7. Checklist độ chính xác và nhất quán nội dung


| Mã        | Tiêu chí                    | Câu hỏi kiểm tra                                                                                            | Công cụ chính          | Quyết định mặc định                       |
| ---------- | ----------------------------- | -------------------------------------------------------------------------------------------------------------- | ------------------------- | ----------------------------------------------- |
| RAW-CON-01 | Câu hỏi khớp bài/vị trí | Câu hỏi có thuộc đúng bài/mục/trang mà dữ liệu ghi không?                                          | Agent + retrieval SGK/SGV | Không chắc →`need_human_review`.            |
| RAW-CON-02 | Đáp án SGV khớp câu hỏi | `Đáp án (SGV)` có trả lời đúng và đủ cho `Câu hỏi` không?                                        | Agent + SGV evidence      | Thiếu, mơ hồ hoặc mâu thuẫn SGV/evidence → `needs_sgv_verification`; fragment `draft` nhưng khớp metadata + nội dung thì không tự động bật cờ này. |
| RAW-CON-03 | Hội thoại bám câu hỏi    | Hội thoại có giải quyết đúng vấn đề học sinh nêu không?                                           | Agent                     | Lệch rõ →`fail`.                             |
| RAW-CON-04 | Hội thoại bám đáp án    | Gia sư có hướng học sinh tới hiểu biết/lời giải đúng, không mâu thuẫn đáp án không?         | Agent + SGV evidence      | Mâu thuẫn rõ →`fail`.                       |
| RAW-CON-05 | Mức nhận thức hợp lý     | `Mức Bloom` có hợp với yêu cầu trong câu hỏi không, khi đối chiếu với bản Markdown chuẩn hóa từ tài liệu HNMU về từ ngữ thể hiện mức độ đáp ứng yêu cầu cần đạt? | Agent + bản Markdown mức nhận thức HNMU | Không chắc →`need_human_review`.            |
| RAW-CON-06 | Không bịa học liệu        | Hội thoại có nêu nội dung không có căn cứ trong SGK/SGV không?                                       | Agent + retrieval         | Có dấu hiệu bịa → review hoặc`fail`.      |
| RAW-CON-07 | Nhất quán metadata          | Chủ đề, bài học, vị trí, câu hỏi, đáp án và hội thoại có nói về cùng một nội dung không? | Agent + registry          | Lệch rõ →`fail`; mơ hồ → review.          |

Ghi chú cho `RAW-CON-05`:

- Nguồn chính hiện dùng là bản Markdown chuẩn hóa: `shared/learning_resources/agent_context/hnmu_cognitive_level_method_canonical.md`.
- Nguồn gốc của bản Markdown là file HNMU: `document/teacher_training_curriculum/benchmark_building_documents/Biểu hiện mức độ nhận thức _Tin học.docx`.
- Chỉ dùng ba mức trong tài liệu gốc: `Biết`, `Hiểu`, `Vận dụng`. Nếu dữ liệu thô ghi `Nhận biết` hoặc `Thông hiểu`, có thể hiểu lần lượt tương ứng với `Biết` và `Hiểu`.
- Tài liệu gốc nêu rõ một số động từ có thể được dùng ở nhiều mức khác nhau; cần xét hành động cùng đối tượng và yêu cầu cụ thể, không ánh xạ máy móc theo một động từ đơn lẻ.
- Nếu câu hỏi có nhiều cách hiểu hoặc nhiều yêu cầu thuộc các mức khác nhau, ưu tiên `need_human_review`; chỉ `fail` khi nhãn mức nhận thức lệch rất rõ với nhiệm vụ.

## 8. Checklist chất lượng sư phạm của hội thoại thô

Nhóm này chỉ kiểm xem từng hội thoại thô có đủ giá trị sư phạm để xem xét tiếp hay không. Không dùng nhóm này để kết luận độ phủ hành vi gia sư của toàn bộ benchmark; độ phủ hành vi gia sư sẽ được kiểm sau khi mẫu đã được chuyển đổi và gán task trong checklist ứng viên benchmark.


| Mã        | Tiêu chí                                         | Câu hỏi kiểm tra                                                                | Công cụ chính                   | Quyết định mặc định                             |
| ---------- | -------------------------------------------------- | ---------------------------------------------------------------------------------- | ---------------------------------- | ----------------------------------------------------- |
| RAW-PED-01 | Có dấu hiệu dàn giáo                          | Gia sư có hỏi/gợi mở/kiểm tra hiểu biết trước khi kết luận không?     | Agent + tài liệu dàn giáo HNMU | Thiếu hoàn toàn → review.                         |
| RAW-PED-02 | Không lộ đáp án quá sớm                     | Gia sư có đưa ngay đáp án cuối/lời giải trọn vẹn trước khi có chẩn đoán, gợi mở, phản hồi của học sinh hoặc mức hỗ trợ phù hợp không? | Agent + tài liệu dàn giáo HNMU | Lộ đáp án rõ khi mẫu cần dẫn dắt → review hoặc `fail`; nếu đã hỗ trợ đủ rồi mới chốt đáp án thì không coi là lỗi. |
| RAW-PED-03 | Trình tự hội thoại hợp lý                    | Các lượt hội thoại có nối tiếp hợp lý theo diễn biến học sinh: tiếp nhận vấn đề → gợi mở/hỗ trợ → phản hồi theo câu trả lời → củng cố/chốt khi phù hợp không? | Agent + tài liệu dàn giáo HNMU | Trình tự nhảy cóc, bỏ qua phản hồi của học sinh hoặc mâu thuẫn giữa các lượt → review hoặc `fail`. |
| RAW-PED-04 | Lượt nói có giá trị                          | Có lượt AI/HS thừa, lặp ý, hoặc khen chung chung mà không đóng góp cho cùng mạch học tập không? | Agent                              | Nhiều lượt ít giá trị → review/cắt khi chuyển đổi. |
| RAW-PED-05 | Phù hợp lứa tuổi                               | Ngôn ngữ có phù hợp học sinh THCS không?                                    | Agent + HNMU                       | Không chắc → HNMU xác nhận.                      |
| RAW-PED-06 | Không thay thế bằng câu trả lời lạc hướng | Gia sư có né yêu cầu hoặc thay thế việc hỗ trợ bằng nội dung ngoài nhiệm vụ, ngoài bài học, ngoài câu hỏi, hoặc lời khuyên chung không giúp giải quyết vấn đề học sinh nêu không? | Agent                              | Lạc hướng rõ → `fail`; nếu chỉ là lời khen/lượt lặp còn nằm trong đúng mạch học tập thì xử lý ở RAW-PED-04. |

Ghi chú phân biệt các tiêu chí sư phạm dễ chồng chéo:

- `RAW-PED-01` chỉ kiểm xem hội thoại có dấu hiệu dàn giáo hay không, ví dụ hỏi gợi mở, đánh dấu đặc điểm quan trọng, giảm dần hỗ trợ hoặc kiểm tra hiểu biết.
- `RAW-PED-02` kiểm thời điểm và cách gia sư tiết lộ đáp án. Không phải cứ nhắc đến đáp án là lỗi; lỗi nằm ở việc đưa đáp án cuối/lời giải trọn vẹn quá sớm khi mẫu cần học sinh được dẫn dắt.
- `RAW-PED-03` kiểm mạch hội thoại qua nhiều lượt. Một hội thoại có thể có dấu hiệu dàn giáo ở `RAW-PED-01` nhưng vẫn trượt `RAW-PED-03` nếu thứ tự phản hồi nhảy cóc, bỏ qua câu trả lời của học sinh hoặc kết luận không theo diễn biến trước đó.
- `RAW-PED-04` kiểm các lượt ít giá trị trong cùng mạch học tập, ví dụ khen chung chung, lặp lại ý cũ hoặc không thêm gợi ý/phản hồi/nhiệm vụ học tập mới.
- `RAW-PED-06` kiểm lỗi lạc hướng hoặc né nhiệm vụ: gia sư chuyển sang nội dung không liên quan đến yêu cầu của học sinh, bài học hoặc câu hỏi cần xử lý. Tiêu chí này nặng hơn `RAW-PED-04`.

## 9. Checklist trùng/gần trùng và rủi ro dữ liệu AI sinh


| Mã        | Tiêu chí               | Cách kiểm                                                                          | Công cụ chính | Output                      |
| ---------- | ------------------------ | ------------------------------------------------------------------------------------ | ---------------- | --------------------------- |
| RAW-DUP-01 | Trùng chính xác       | So sánh câu hỏi, đáp án, hội thoại sau chuẩn hóa whitespace/chữ thường. | Code             | `duplicate_candidates.csv`  |
| RAW-DUP-02 | Gần trùng              | So sánh tương đồng văn bản trên câu hỏi/hội thoại/đáp án.             | Code             | Cụm mẫu gần trùng       |
| RAW-DUP-03 | Biến thể tầm thường | Mẫu chỉ đổi số/từ rất nhỏ nhưng hội thoại gần như giống hệt.          | Code + agent     | Gắn cờ review             |
| RAW-DUP-04 | Khuôn AI lặp lại      | Nhiều hội thoại có cùng cấu trúc/khen/gợi mở máy móc.                     | Code + agent     | Báo cáo rủi ro đa dạng |

## 10. Điều kiện chuyển dữ liệu thô sang Plan 06

Một mẫu thô chỉ nên chuyển sang bước tạo ứng viên benchmark khi:

1. Có truy vết file/sheet/dòng gốc.
2. Không thiếu câu hỏi và hội thoại.
3. Có hoặc có thể xác minh đáp án SGV.
4. Câu hỏi, bài học, vị trí, đáp án và hội thoại không mâu thuẫn rõ.
5. Không nằm trong cụm trùng/gần trùng nghiêm trọng, hoặc đã chọn được mẫu đại diện.
6. Có quyết định `pass` hoặc `need_human_review` nhưng được UET/HNMU duyệt cho chuyển đổi thử.

Checklist này không yêu cầu tách `student_prompt`, `conversation_history`, `gold_response`. Việc đó thuộc checklist ứng viên benchmark sau chuyển đổi.

## 11. Cách tổng hợp từ checklist chi tiết sang quyết định mẫu

`agent_shard_audit/merged/quality_check_suggestions.csv` phải được tổng hợp từ bốn nguồn:

1. kiểm tra cơ học bằng code;
2. `raw_dialogue_checklist_results.csv`;
3. evidence học liệu SGK/SGV;
4. kết quả trùng/gần trùng.

Quy tắc bắt buộc cho phần checklist chi tiết:

- Nếu có bất kỳ tiêu chí `fail`, mẫu tổng thể là `failed`.
- Nếu không có `fail` nhưng có bất kỳ tiêu chí `uncertain`, mẫu tổng thể là `need_human_review`. Không đưa mẫu vào review chỉ vì fragment khớp đang có trạng thái `draft`.
- Chỉ khi toàn bộ tiêu chí là `pass` hoặc `not_applicable`, mẫu mới được `pass`.
- Nếu tiêu chí không áp dụng cho mẫu, dùng `not_applicable`, không tính như lỗi.
- `confidence_score` tổng hợp không phải điểm chất lượng của mẫu; đó là độ tin cậy của chính quyết định tổng thể.

Quy tắc tổng hợp `confidence_score`:

- Nếu quyết định tổng thể là `failed`: lấy confidence thấp nhất trong các tiêu chí `fail`.
- Nếu quyết định tổng thể là `need_human_review`: lấy confidence thấp nhất trong các tiêu chí `uncertain`.
- Nếu quyết định tổng thể là `pass`: lấy confidence thấp nhất trong toàn bộ tiêu chí của mẫu.

Khi cần đồng bộ lại output, dùng code chung:

```bash
PYTHONPATH=src /home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/dialogue_audit/sync_quality_suggestions_from_checklist.py \
  --checklist path/to/raw_dialogue_checklist_results.csv \
  --quality-template path/to/quality_check_suggestions.csv \
  --review-template path/to/hnmu_review_queue_suggestions.csv \
  --output-quality path/to/quality_check_suggestions.csv \
  --output-review-queue path/to/hnmu_review_queue_suggestions.csv \
  --decision-column quality_decision \
  --pass-label pass \
  --normalized-rows path/to/normalized_dialogue_rows.csv \
  --canonical-quality-schema
```

## 12. Hàng đợi HNMU/UET kiểm lại

Một mẫu nên vào `hnmu_review_queue.csv` nếu có ít nhất một điều kiện sau:

- quyết định tổng thể là `failed` hoặc `need_human_review` theo quy tắc tổng hợp checklist;
- thiếu hoặc mơ hồ trường lõi;
- `confidence_score < 0.50`;
- câu hỏi, đáp án, hội thoại hoặc mức nhận thức mâu thuẫn nhưng agent không đủ chắc;
- cần SGV để xác minh nhưng evidence SGV chưa đủ chắc;
- có dấu hiệu nội dung bịa, lệch học liệu, hoặc nhạy cảm về đạo đức/pháp lý;
- hội thoại có giá trị sư phạm không rõ;
- mẫu trùng/gần trùng với nhiều mẫu khác và cần quyết định giữ mẫu đại diện nào.

Các cột tối thiểu:

```text
raw_sample_id,batch_id,source_file,sheet_name,row_number,review_reason,severity,confidence_score,suggested_action,notes
```

## 13. Giới hạn

- Checklist này chưa xác nhận chuyên môn thay HNMU.
- Checklist này chưa tạo mẫu benchmark hoàn chỉnh.
- Checklist này chưa kiểm task/rubric/gold_response.
- Checklist này chưa dùng để chấm model.
