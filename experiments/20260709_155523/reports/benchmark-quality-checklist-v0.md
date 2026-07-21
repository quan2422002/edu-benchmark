# Checklist kiểm định chất lượng benchmark v0

Experiment: `20260709_155523`
Plan: `01-benchmark-quality-literature-review.md`
Ngày tạo: 14/07/2026
Trạng thái: bản tổng hợp nền; checklist vận hành đã được tách thành checklist dữ liệu thô và checklist ứng viên benchmark.

## 0. Cách dùng hiện tại sau khi tách checklist

File này được giữ lại như bản tổng hợp nền từ Plan 01, ghi lại logic chung rút ra từ 4 bài báo. Từ ngày 17/07/2026, không dùng trực tiếp file này làm checklist vận hành cho specialist agent nữa.

Dùng hai checklist tách riêng sau:

| Giai đoạn | Checklist vận hành | Ghi chú |
|---|---|---|
| Kiểm dữ liệu thô HNMU trong Plan 04 | `experiments/20260709_155523/reports/raw-dialogue-quality-checklist-v0.md` | Chỉ kiểm file/dòng dữ liệu thô: câu hỏi, bài học, đáp án SGV, hội thoại, truy vết, evidence SGK/SGV. |
| Kiểm ứng viên mẫu benchmark sau chuyển đổi trong Plan 06 | `experiments/20260709_155523/reports/benchmark-candidate-quality-checklist-v0.md` | Chỉ kiểm mẫu đã có `student_prompt`, `conversation_history`, `gold_response`, task/rubric và truy vết benchmark. |

Nguyên tắc: agent kiểm Plan 04 chỉ dùng checklist dữ liệu thô; không áp tiêu chí của mẫu benchmark khi dữ liệu chưa được chuyển đổi.

## 1. Mục đích

Checklist này chuyển kết quả đọc 4 bài báo thành tiêu chí vận hành được khi kiểm dữ liệu HNMU. Nó dùng để đánh giá chất lượng của **dữ liệu thô và ứng viên mẫu benchmark**, chưa dùng để chấm model.

Checklist này trả lời ba câu hỏi chính:

1. Dữ liệu có đủ phủ các vùng cần phủ không?
2. Từng mẫu có chính xác, nhất quán và có giá trị sư phạm không?
3. Mẫu có đủ điều kiện chuyển sang bước tạo benchmark hoàn chỉnh không?

## 2. Căn cứ từ 4 bài báo


| Căn cứ          | Bài học rút ra cho checklist                                                                                                                                                                                                                   |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| MathTutorBench    | Không chỉ kiểm đáp án đúng; cần kiểm năng lực gia sư như hiểu học sinh, phản hồi sư phạm và giàn giáo. Hội thoại dài hơn/nhiều bước hơn có thể làm nhiệm vụ khó hơn.                                        |
| KMP-Bench         | Dữ liệu hội thoại cần kiểm trình tự sư phạm, học liệu bị bịa, lượt thừa không có giá trị, và cần kiểm thủ công/kiểm người với các flow có rủi ro. Bài báo loại 451 flow có vấn đề, tương đương 7.6%. |
| TutorBench        | Mẫu và tiêu chí chấm nên được chuyên gia tạo/kiểm tra; bộ chấm tự động phải được so với người chấm. Phản hồi mẫu dùng để xây tiêu chí, không nên chấm bằng so khớp câu chữ.                              |
| VietLegal/V-Legal | Cần nguồn chính thức, truy vết nguồn, kiểm tra chéo, phân xử, đo độ đồng thuận và kiểm trùng/rò rỉ. Với dự án này, SGK/SGV đóng vai trò tương tự nguồn chính thức.                                              |

## 3. Output tối thiểu cho mỗi mẫu

Mỗi mẫu sau kiểm định nên có các trường dẫn xuất sau:


| Trường                    | Ý nghĩa                                                                              |
| --------------------------- | -------------------------------------------------------------------------------------- |
| `raw_sample_id`             | Mã mẫu thô, truy vết về file/sheet/dòng gốc.                                    |
| `quality_decision`          | `pass`, `fail`, hoặc `needs_human_review`.                                            |
| `confidence_score`          | Mức tự tin của kiểm định tự động/agent, từ 0.00 đến 1.00.                  |
| `failure_reasons`           | Danh sách lý do nếu mẫu không đạt hoặc cần xem lại.                          |
| `suggested_reviewer_action` | `keep`, `ask_hnmu_review`, `exclude_from_current_batch`, hoặc `needs_uet_decision`.   |
| `needs_sgv_verification`    | `true` nếu kiểm đáp án cần SGV nhưng chưa tìm được evidence SGV đủ chắc, OCR/fragment còn mơ hồ, hoặc cần HNMU/UET xác nhận. |
| `audit_notes`               | Ghi chú ngắn, ưu tiên tiếng Việt, nêu rõ căn cứ kiểm tra.                   |

## 4. Quy tắc quyết định và điểm tự tin

### 4.1. `quality_decision`

- `pass`: mẫu đủ trường, không phát hiện lỗi rõ, hội thoại bám câu hỏi/đáp án, trình tự sư phạm hợp lý, không cần xác nhận chuyên môn đặc biệt.
- `fail`: mẫu có lỗi rõ ràng, ví dụ thiếu hội thoại, câu hỏi không khớp đáp án, hội thoại lệch chủ đề, hoặc trùng gần như hoàn toàn với mẫu khác.
- `needs_human_review`: mẫu có rủi ro ngữ nghĩa, độ tự tin thấp, thiếu SGV để xác minh đáp án, hoặc liên quan tới quyết định sư phạm/chuyên môn mà agent không nên tự chốt.

### 4.2. `confidence_score`

Ngưỡng đề xuất cho Plan 04:


| Khoảng điểm | Cách hiểu                                                  | Hành động đề xuất                                        |
| -------------- | ------------------------------------------------------------ | -------------------------------------------------------------- |
| `>= 0.80`      | Agent/code khá tự tin, không thấy lỗi nghiêm trọng.   | Có thể giữ nếu các kiểm tra cơ học cũng đạt.        |
| `0.50–0.79`   | Có dấu hiệu chưa chắc hoặc cần ngữ cảnh học liệu. | Đưa vào danh sách UET/HNMU xem lại nếu mẫu quan trọng. |
| `< 0.50`       | Rủi ro cao hoặc thiếu căn cứ.                           | Đưa vào`hnmu_review_queue.csv`.                             |

Điểm tự tin không thay thế quyết định của HNMU/UET. Nếu có cờ lỗi nghiêm trọng, mẫu không được tự động `pass` dù điểm tự tin cao.

## 5. Checklist cấp batch: độ phủ và phân bố

Các kiểm tra cấp batch chủ yếu do code thực hiện, sau đó người điều phối giải thích.


| Mã    | Tiêu chí                     | Cách kiểm                                                                                                                                  | Công cụ chính           | Căn cứ                              | Output                     |
| ------ | ------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------- | ------------------------------------- | -------------------------- |
| COV-01 | Phủ khối lớp                | Đếm số mẫu theo lớp 6, 7, 8, 9.                                                                                                         | Code                       | KMP-Bench; VietLegal/V-Legal          | `coverage_summary.csv`     |
| COV-02 | Phủ chủ đề/bài học       | Đếm theo`Bài`, `Vị trí`, và registry SGK/SGV khi có.                                                                                  | Code + học liệu registry | KMP-Bench; VietLegal/V-Legal          | Bảng vùng thiếu/lệch   |
| COV-03 | Phủ mức nhận thức          | Đếm theo`Mức Bloom`, chuẩn hóa về Biết, Hiểu, Vận dụng nếu cần.                                                                  | Code + kiểm nhãn         | TutorBench; VietLegal/V-Legal         | Phân bố mức nhận thức |
| COV-04 | Phủ dạng câu hỏi/bài tập | Gắn nhãn sơ bộ: câu hỏi lý thuyết, trắc nghiệm, bài có code, sửa lỗi, viết chương trình, bài làm học sinh, dạng khác. | Code + agent khi mơ hồ   | TutorBench; VietLegal/V-Legal         | Phân bố dạng bài       |
| COV-05 | Phủ hành vi gia sư          | Gắn nhãn hành vi chính: giải thích, gợi mở, phản hồi bài làm, sửa lỗi, định hướng khi lệch phạm vi, luyện tập.         | Agent + mẫu kiểm người | MathTutorBench; KMP-Bench; TutorBench | Bảng phủ hành vi        |
| COV-06 | Phân bố có chủ đích      | Không yêu cầu đều tuyệt đối; yêu cầu giải thích được vì sao vùng này nhiều/ít.                                           | Người điều phối       | Suy luận từ 4 bài báo             | Nhận xét trong báo cáo |

## 6. Checklist cấp mẫu: thiếu trường và định dạng

Các kiểm tra này nên chạy trước khi dùng agent.


| Mã    | Tiêu chí                        | Cách kiểm                                                                                             | Công cụ chính | Quyết định mặc định                                 |
| ------ | --------------------------------- | ------------------------------------------------------------------------------------------------------- | ---------------- | --------------------------------------------------------- |
| STR-01 | Có đủ cột bắt buộc          | Kiểm các cột`Bài`, `Vị trí`, `Câu hỏi`, `Mức Bloom`, `Đáp án (SGV)`, `Hội thoại gia sư`. | Code             | Thiếu cột →`fail` cấp file/batch.                     |
| STR-02 | Không thiếu trường lõi       | Kiểm ô trống ở câu hỏi, đáp án, hội thoại.                                                   | Code             | Thiếu trường lõi →`fail` hoặc `needs_human_review`. |
| STR-03 | Hội thoại có nhãn lượt nói | Kiểm có nhãn như`HS:` và `AI:` hoặc pattern tương đương.                                     | Code             | Thiếu nhãn →`needs_human_review`.                      |
| STR-04 | Hội thoại không quá ngắn     | Kiểm độ dài ký tự/từ và số lượt.                                                             | Code             | Quá ngắn →`needs_human_review`.                        |
| STR-05 | Có mã truy vết dòng gốc      | Gắn file, sheet, row index, batch ID.                                                                  | Code             | Thiếu truy vết → chưa được chuyển đổi.          |

## 7. Checklist cấp mẫu: độ chính xác và nhất quán nội dung

Các kiểm tra này cần agent hỗ trợ, nhưng quyết định cuối ở ca mơ hồ thuộc UET/HNMU.


| Mã    | Tiêu chí                    | Câu hỏi kiểm tra                                                                                    | Công cụ chính     | Căn cứ                      | Quyết định mặc định                                |
| ------ | ----------------------------- | ------------------------------------------------------------------------------------------------------ | -------------------- | ----------------------------- | -------------------------------------------------------- |
| CON-01 | Câu hỏi khớp bài/vị trí | Câu hỏi có thuộc đúng bài, mục, trang đã ghi không?                                         | Agent + học liệu   | VietLegal/V-Legal; KMP-Bench  | Không chắc →`needs_human_review`.                     |
| CON-02 | Đáp án khớp câu hỏi     | `Đáp án (SGV)` có trả lời đúng và đủ cho `Câu hỏi` không?                                | Agent; SGV khi có   | VietLegal/V-Legal             | Chưa có SGV →`needs_sgv_verification`.                |
| CON-03 | Hội thoại bám câu hỏi    | Nội dung hội thoại có giải quyết đúng vấn đề học sinh hỏi không?                         | Agent                | KMP-Bench; TutorBench         | Lệch rõ →`fail`.                                      |
| CON-04 | Hội thoại bám đáp án    | Gia sư có hướng học sinh tới hiểu biết/lời giải đúng, không mâu thuẫn đáp án không? | Agent; SGV khi có   | MathTutorBench; KMP-Bench     | Mâu thuẫn rõ →`fail`.                                |
| CON-05 | Mức nhận thức hợp lý     | `Mức Bloom` có hợp với yêu cầu trong câu hỏi không?                                           | Agent + rule sơ bộ | TutorBench; VietLegal/V-Legal | Không chắc →`needs_human_review`.                     |
| CON-06 | Không bịa học liệu        | Hội thoại có nêu khái niệm, ví dụ, nội dung không có căn cứ trong học liệu không?      | Agent + học liệu   | KMP-Bench; VietLegal/V-Legal  | Có dấu hiệu bịa →`needs_human_review` hoặc `fail`. |

## 8. Checklist cấp mẫu: chất lượng sư phạm của hội thoại

Nhóm này kiểm xem hội thoại có giá trị làm dữ liệu gia sư hay không, không chỉ đúng đáp án.


| Mã    | Tiêu chí                                         | Câu hỏi kiểm tra                                                                | Công cụ chính | Căn cứ                                | Quyết định mặc định                             |
| ------ | -------------------------------------------------- | ---------------------------------------------------------------------------------- | ---------------- | --------------------------------------- | ----------------------------------------------------- |
| PED-01 | Có giàn giáo                                    | Gia sư có hỏi/gợi mở/kiểm tra hiểu biết trước khi kết luận không?     | Agent            | MathTutorBench; KMP-Bench               | Thiếu hoàn toàn →`needs_human_review`.            |
| PED-02 | Không lộ đáp án quá sớm                     | Với mẫu cần gợi mở, gia sư có đưa thẳng đáp án khi chưa cần không? | Agent            | MathTutorBench; TutorBench              | Lộ đáp án quá sớm → gắn cờ.                  |
| PED-03 | Trình tự hội thoại hợp lý                    | Các bước có đi từ vấn đề → gợi mở → phản hồi → củng cố không?   | Agent            | KMP-Bench                               | Trình tự vô lý →`fail` hoặc review.             |
| PED-04 | Lượt nói có giá trị                          | Có lượt AI/HS thừa, lặp, khen chung chung, không phục vụ học tập không? | Agent            | KMP-Bench                               | Nhiều lượt thừa → review/cắt khi chuyển đổi. |
| PED-05 | Phù hợp lứa tuổi                               | Ngôn ngữ có phù hợp học sinh THCS không?                                    | Agent + HNMU     | TutorBench; suy luận sư phạm         | Không chắc → HNMU xác nhận.                      |
| PED-06 | Không thay thế bằng câu trả lời lạc hướng | Gia sư có né yêu cầu bằng nội dung không liên quan không?                | Agent            | KMP-Bench, lỗi evasion by substitution | Lạc hướng rõ →`fail`.                            |

## 9. Checklist trùng/gần trùng và rủi ro dữ liệu AI sinh


| Mã    | Tiêu chí               | Cách kiểm                                                                 | Công cụ chính | Căn cứ                     | Output                      |
| ------ | ------------------------ | --------------------------------------------------------------------------- | ---------------- | ---------------------------- | --------------------------- |
| DUP-01 | Trùng chính xác       | So sánh câu hỏi, đáp án, hội thoại sau chuẩn hóa whitespace.      | Code             | VietLegal/V-Legal            | `duplicate_candidates.csv`  |
| DUP-02 | Gần trùng              | So sánh tương đồng văn bản trên câu hỏi/hội thoại.              | Code             | VietLegal/V-Legal; KMP-Bench | Cụm mẫu gần trùng       |
| DUP-03 | Biến thể tầm thường | Mẫu chỉ đổi số/từ rất nhỏ nhưng hội thoại gần như giống hệt. | Code + agent     | KMP-Bench                    | Gắn cờ review             |
| DUP-04 | Khuôn AI lặp lại      | Nhiều hội thoại có cùng cấu trúc/khen/gợi mở máy móc.            | Code + agent     | KMP-Bench; TutorBench        | Báo cáo rủi ro đa dạng |

## 10. Checklist sẵn sàng chuyển đổi sang mẫu benchmark

Nhóm này dùng sau khi mẫu qua kiểm toán sơ bộ, trước Plan 06.


| Mã     | Tiêu chí                                    | Câu hỏi kiểm tra                                                | Công cụ chính           | Quyết định mặc định                                |
| ------- | --------------------------------------------- | ------------------------------------------------------------------ | -------------------------- | -------------------------------------------------------- |
| CONV-01 | Tách được`student_prompt`                 | Có xác định được yêu cầu ban đầu của học sinh không? | Code + agent               | Không tách được →`needs_human_review`.             |
| CONV-02 | Tách được`conversation_history`           | Có phần lịch sử trước phản hồi mục tiêu không?          | Code + agent               | Có thể rỗng nếu là mẫu một lượt; phải ghi rõ. |
| CONV-03 | Tách được`gold_response`                  | Có xác định được phản hồi gia sư mục tiêu không?      | Code + agent               | Không tách được → không chuyển đổi.            |
| CONV-04 | Tách riêng`Đáp án`                       | Đáp án đúng không bị lẫn với phản hồi gia sư mẫu?     | Code + agent               | Không rõ → review.                                    |
| CONV-05 | Lượt gia sư mục tiêu có giá trị chấm | Phản hồi mục tiêu có đủ nội dung để chấm rubric không? | Agent                      | Không có giá trị → loại khỏi chuyển đổi.       |
| CONV-06 | Có truy vết học liệu                      | Mẫu gắn được với bài/vị trí/nguồn học liệu không?     | Code + học liệu registry | Thiếu →`needs_human_review`.                           |

## 11. Hàng đợi HNMU/UET kiểm lại

Một mẫu nên vào `hnmu_review_queue.csv` nếu có ít nhất một điều kiện sau:

- Thiếu hoặc mơ hồ trường lõi.
- `confidence_score < 0.50`.
- Câu hỏi, đáp án, hội thoại hoặc mức nhận thức mâu thuẫn nhưng agent không đủ chắc.
- Cần SGV để xác minh nhưng evidence SGV chưa đủ chắc, không truy xuất được đúng đoạn, hoặc còn cần HNMU/UET xác nhận: `needs_sgv_verification = true`.
- Có dấu hiệu nội dung bịa, lệch học liệu, hoặc nhạy cảm về đạo đức/pháp lý.
- Hội thoại có giá trị sư phạm không rõ.
- Mẫu trùng/gần trùng với nhiều mẫu khác và cần quyết định giữ mẫu đại diện nào.

Các cột tối thiểu của hàng đợi:

```text
raw_sample_id,batch_id,source_file,sheet_name,row_number,review_reason,severity,confidence_score,suggested_action,notes
```

## 12. Gợi ý mức nghiêm trọng


| Mức      | Ý nghĩa                                     | Ví dụ                                                                                 |
| --------- | --------------------------------------------- | --------------------------------------------------------------------------------------- |
| `blocker` | Không thể dùng nếu chưa sửa/xác nhận. | Thiếu hội thoại, thiếu câu hỏi, không tách được phản hồi mục tiêu.       |
| `major`   | Có thể làm sai benchmark nếu bỏ qua.     | Câu hỏi không khớp đáp án, hội thoại lệch chủ đề, trùng gần hoàn toàn. |
| `minor`   | Không chặn ngay nhưng nên sửa/ghi chú.  | Lỗi trình bày, hội thoại hơi dài, nhãn mức nhận thức cần xem lại.          |
| `info`    | Chỉ ghi nhận để phân tích batch.        | Chủ đề xuất hiện quá nhiều, dạng bài chưa đa dạng.                          |

## 13. Cách dùng checklist trong Plan 04

Quy trình đề xuất:

1. Code đọc file gốc và tạo bảng trung gian có `raw_sample_id`.
2. Code chạy kiểm định cấu trúc, thiếu trường, định dạng và trùng/gần trùng.
3. Code tạo thống kê độ phủ cấp batch.
4. Agent kiểm một hoặc nhiều nhóm tiêu chí ngữ nghĩa theo checklist, nhưng phải trả về lý do và `confidence_score`.
5. Mẫu `pass` được đưa vào danh sách ứng viên Plan 06.
6. Mẫu `fail` hoặc `needs_human_review` được đưa vào `hnmu_review_queue.csv`.
7. UET/HNMU xác nhận các mẫu trong hàng đợi trước khi chuyển đổi hàng loạt.

## 14. Giới hạn của checklist v0

- Checklist được rút ra từ 3 paper gia sư chủ yếu thuộc Toán/STEM và 1 paper tiếng Việt thuộc Luật; không thể xem là kết luận cuối cùng cho Tin học THCS.
- Checklist chưa thay thế xác nhận chuyên môn của HNMU.
- SGV Tin học 6–9 hiện đã có OCR Markdown/fragment v0, nhưng vẫn ở trạng thái `draft`; kiểm đáp án vẫn là sơ bộ nếu evidence truy xuất chưa đủ chắc hoặc chưa được HNMU/UET xác nhận.
- Checklist chưa thiết kế bộ chấm model; phần đó thuộc Plan 05.

## 15. Câu hỏi cần chốt tiếp

1. UET có được tự loại tạm mẫu trùng/gần trùng khỏi batch chuyển đổi thử không?
2. Ngưỡng `confidence_score` nào đủ để không cần HNMU xem lại?
3. HNMU có thể kiểm tra chéo một tập nhỏ để đo độ đồng thuận không?
4. Khi phản hồi gia sư trong hội thoại gốc chưa lý tưởng, UET có được đề xuất bản `gold_response` chỉnh sửa để HNMU duyệt không?
5. Trong đợt đầu, kiểm đáp án theo SGV sẽ chỉ gắn cờ `needs_sgv_verification`, hay phải chờ SGV được crawl/OCR mới chuyển đổi?
