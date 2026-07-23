# Báo cáo kiểm toán tổng thể dữ liệu hội thoại HNMU lớp 8–9

Ngày cập nhật: 20/07/2026  
Trạng thái: `draft_audit_latest_synced_outputs` — báo cáo này đã được đồng bộ theo bộ kết quả mới nhất trong thư mục output lớp 8–9. Các file debug/lần chạy trung gian đã được đưa vào `.gitignore`; phần dưới đây chỉ dùng các file kết quả hiện hành được giữ làm bản chính. Báo cáo này chưa thay thế phán quyết chuyên môn cuối cùng của HNMU/UET.

## 1. Phạm vi

Lượt kiểm toán này xử lý dữ liệu thô lớp 8 và lớp 9 do HNMU gửi trong thư mục dữ liệu dùng chung của dự án.

Nguồn chuẩn để ánh xạ chủ đề/bài học là registry SGK/SGV Tin học THCS đã được đồng bộ theo bộ SGK/SGV, không đồng bộ theo cách ghi trong dữ liệu thô. Nguyên tắc ánh xạ bài học hiện hành:

- không dùng fuzzy matching cho ánh xạ bài học;
- không dùng semantic similarity giữa tiêu đề cho ánh xạ bài học;
- chỉ dùng quy tắc nhận diện số bài và hậu tố A/B nếu có;
- ánh xạ vào tên bài chuẩn theo khóa lớp + mã bài trong registry SGK/SGV.

Ghi chú: bước lọc trùng/gần trùng văn bản vẫn có thể dùng so khớp chuỗi, nhưng bước này độc lập với ánh xạ bài học.

## 2. Bộ file kết quả hiện hành

Bộ output lớp 8–9 nằm tại:

```text
experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/
```

Các file kết quả nên dùng hiện tại:

- `normalized_dialogue_rows.csv`: bản dẫn xuất 588 mẫu, giữ truy vết về dữ liệu thô.
- `coverage_summary.csv`: thống kê độ phủ theo lớp, chủ đề, bài học và mức nhận thức.
- `missing_field_report.csv`: lỗi thiếu trường hoặc lỗi định dạng phát hiện bằng code.
- `duplicate_candidates.csv`: ứng viên trùng/gần trùng phát hiện bằng code.
- `agent_shard_audit/merged/raw_dialogue_checklist_results.regex_repaired.csv`: checklist chi tiết đã đồng bộ mới nhất, mỗi mẫu đủ 18 tiêu chí.
- `agent_shard_audit/merged/quality_check_suggestions.csv`: file chính ở cấp mẫu sau agent audit, dùng cột `quality_decision` với ba nhãn `pass`, `need_human_review`, `failed`.
- `agent_shard_audit/merged/hnmu_review_queue_suggestions.csv`: danh sách mẫu nên đưa vào hàng đợi người xem lại theo checklist mới nhất.
- `agent_shard_audit/merged/merge_validation_summary.json`: tóm tắt máy đọc cho lượt merge/sync mới nhất.

Các file root-level như `metadata_consistency_flags.csv`, `quality_check_results.csv`, `hnmu_review_queue.csv` vẫn còn trên máy để truy vết kiểm cơ học, nhưng hiện không phải bộ deliverable chính được giữ nổi bật qua Git. Khi báo cáo tổng thể, ưu tiên bộ checklist/suggestion đã đồng bộ ở `agent_shard_audit/merged/`.

## 3. Kết quả kiểm độ phủ lớp 8–9

Tổng số mẫu đã đọc: 588.

| Khối lớp | Số mẫu | Nhận xét |
| --- | ---: | --- |
| Lớp 8 | 280 | Gồm 20 bài hoặc nhóm bài; mỗi bài/nhóm bài có 14 mẫu. |
| Lớp 9 | 308 | Gồm 22 bài hoặc nhóm bài; mỗi bài/nhóm bài có 14 mẫu. |

Sau khi đồng bộ lại theo registry SGK/SGV, không còn nhóm “Không rõ chủ đề” trong thống kê độ phủ. Đây là thay đổi quan trọng so với các bản debug trước đó.

### 3.1. Độ phủ theo chủ đề

| Chủ đề | Số mẫu | Tỉ lệ |
| --- | ---: | ---: |
| Ứng dụng tin học | 98 | 16,67% |
| Giải quyết vấn đề với sự trợ giúp của máy tính | 98 | 16,67% |
| Sử dụng bảng tính điện tử nâng cao | 70 | 11,90% |
| Làm quen với phần mềm làm video | 70 | 11,90% |
| Tổ chức lưu trữ, tìm kiếm và trao đổi thông tin | 56 | 9,52% |
| Soạn thảo văn bản và trình chiếu nâng cao | 56 | 9,52% |
| Làm quen với phần mềm chỉnh sửa ảnh | 56 | 9,52% |
| Máy tính và cộng đồng | 28 | 4,76% |
| Đạo đức, pháp luật và văn hoá trong môi trường số | 28 | 4,76% |
| Hướng nghiệp với Tin học | 14 | 2,38% |
| Hướng nghiệp với tin học | 14 | 2,38% |

Hai dòng “Hướng nghiệp với Tin học” và “Hướng nghiệp với tin học” được giữ theo nhãn nguồn hiện có trong SGK/SGV lớp 8 và lớp 9. Nếu cần phân tích liên lớp ở mức chủ đề lớn, có thể gom hai nhãn này trong một bước chuẩn hóa nhãn hiển thị sau.

### 3.2. Độ phủ theo bài học

Toàn bộ 42 bài hoặc nhóm bài ở lớp 8–9 đều có 14 mẫu. Điều này cho thấy dữ liệu đang phân bố đều theo bài học. Cần lưu ý đây là “đều theo bài học”, không nhất thiết là đều theo độ quan trọng sư phạm; nếu HNMU/UET muốn ưu tiên một số bài trọng tâm hơn, phân bố ở các batch sau có thể điều chỉnh có chủ đích.

### 3.3. Độ phủ theo mức nhận thức

| Mức nhận thức | Số mẫu | Tỉ lệ | Nhận xét |
| --- | ---: | ---: | --- |
| Thông hiểu | 237 | 40,31% | Nhóm lớn nhất, phù hợp với dạng hội thoại giải thích/gợi mở. |
| Vận dụng | 170 | 28,91% | Đủ lớn để kiểm các tình huống cần thao tác, giải quyết vấn đề hoặc áp dụng kiến thức. |
| Nhận biết | 162 | 27,55% | Có số lượng gần tương đương Vận dụng. |
| Không rõ | 19 | 3,23% | Cần người xem lại cách ghi mức nhận thức, chủ yếu do định dạng nhãn chưa thống nhất. |

## 4. Kết quả kiểm cơ học

Các lỗi thiếu trường/định dạng còn lại:

| Nhóm lỗi | Số mẫu | Mức độ |
| --- | ---: | --- |
| Hội thoại không có nhãn AI | 1 | Cao |
| Mức nhận thức chưa nhận diện được theo quy ước hiện hành | 19 | Trung bình |

Ứng viên trùng/gần trùng:

- Có 1 cặp câu hỏi trùng chính xác sau chuẩn hóa khoảng trắng và chữ thường.
- Cặp này thuộc lớp 9 và cần người quyết định giữ một mẫu, sửa để tạo khác biệt rõ hơn, hoặc giữ cả hai nếu mục tiêu sư phạm khác nhau.

## 5. Kết quả checklist chi tiết theo từng mẫu

File checklist chính hiện tại đã qua validator:

```text
experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/raw_dialogue_checklist_results.regex_repaired.csv
```

Quy mô checklist:

- 588 mẫu;
- 18 tiêu chí cho mỗi mẫu;
- 10.584 dòng checklist;
- validator trả về `OK`.

Tổng hợp kết quả theo từng lượt chấm tiêu chí:

| Kết quả | Số lượt | Tỉ lệ |
| --- | ---: | ---: |
| Đạt | 10.107 | 95,49% |
| Chưa chắc/cần xem lại | 475 | 4,49% |
| Không đạt | 2 | 0,02% |

### 5.1. Nhóm cấu trúc và định dạng

Nhóm cấu trúc nhìn chung rất tốt. Toàn bộ 588 mẫu đều không thiếu trường lõi; chỉ có 1 mẫu không đạt ở tiêu chí nhãn lượt nói, khớp với lỗi cơ học “hội thoại không có nhãn AI”. Tiêu chí độ dài hội thoại có 586 mẫu đạt và 2 mẫu cần xem lại.

### 5.2. Nhóm nhất quán nội dung và học liệu

Nhóm này là nơi còn nhiều trạng thái “chưa chắc” nhất, nhưng đã tốt hơn đáng kể so với các bản debug trước. Cụ thể:

- Câu hỏi khớp bài/vị trí: 490 đạt, 98 chưa chắc.
- Đáp án SGV khớp câu hỏi: 532 đạt, 56 chưa chắc.
- Hội thoại bám câu hỏi: 588 đạt.
- Hội thoại bám đáp án: 531 đạt, 56 chưa chắc, 1 không đạt.
- Mức nhận thức hợp lý: 588 đạt theo checklist agent.
- Không bịa học liệu: 490 đạt, 98 chưa chắc.
- Nhất quán metadata: 490 đạt, 98 chưa chắc.

Các dòng “chưa chắc” chủ yếu liên quan đến mức độ truy xuất/đối chiếu học liệu chưa đủ chắc ở một số mẫu, không nên tự động hiểu là nội dung hội thoại sai.

### 5.3. Nhóm chất lượng dàn giáo

Nhóm dàn giáo nhìn chung tốt:

- Có dấu hiệu dàn giáo: 536 đạt, 52 chưa chắc.
- Không lộ đáp án quá sớm: 580 đạt, 8 chưa chắc.
- Trình tự hội thoại hợp lý: 587 đạt, 1 chưa chắc.
- Lượt nói có giá trị: 587 đạt, 1 chưa chắc.
- Phù hợp lứa tuổi: 588 đạt.
- Không thay thế bằng câu trả lời lạc hướng: 588 đạt.

Điều này cho thấy đa số hội thoại lớp 8–9 có thể dùng làm nguồn đầu vào tốt cho bước chuyển đổi thử, sau khi xử lý các mẫu cần rà lại.

### 5.4. Nhóm trùng lặp/khuôn mẫu

- Biến thể tầm thường: 586 đạt, 2 chưa chắc.
- Khuôn hội thoại lặp lại: 586 đạt, 2 chưa chắc.

Kết quả này tương thích với kiểm cơ học: chỉ có 1 cặp câu hỏi trùng chính xác cần quyết định.

## 6. Gợi ý quyết định tổng hợp từ checklist

File tổng hợp được tạo từ checklist chi tiết theo rule strict:

- có ít nhất một tiêu chí `fail` → mẫu tổng thể là `failed`;
- không có `fail` nhưng có ít nhất một tiêu chí `uncertain` → mẫu tổng thể là `need_human_review`;
- toàn bộ tiêu chí là `pass` hoặc `not_applicable` → mẫu tổng thể là `pass`.

`confidence_score` tổng thể là độ tin cậy của quyết định tổng thể: với `failed` lấy confidence thấp nhất trong các tiêu chí `fail`, với `need_human_review` lấy confidence thấp nhất trong các tiêu chí `uncertain`, với `pass` lấy confidence thấp nhất trong toàn bộ tiêu chí của mẫu.

Bản gợi ý tổng hợp mới nhất ghi nhận:

| Gợi ý | Số mẫu | Nhận xét |
| --- | ---: | --- |
| Giữ để dùng tiếp ở bước sau | 427 | Nhóm tương đối sạch, ít cờ cần xem lại. |
| Cần người xem lại | 160 | Chủ yếu do đối chiếu học liệu/SGV hoặc một số dấu hiệu dàn giáo chưa chắc. |
| Loại khỏi lượt hiện tại | 1 | Lỗi định dạng hội thoại rõ. |

Hàng đợi xem lại theo checklist hiện có 161 mẫu:

| Mức ưu tiên | Số mẫu | Ý nghĩa |
| --- | ---: | --- |
| Cao | 43 | Nên xem trước khi chuyển đổi batch này sang mẫu benchmark. |
| Trung bình | 118 | Có thể rà sau, hoặc xử lý theo nhóm lỗi nếu cần tiến độ nhanh. |

Các cờ xem lại trong file gợi ý tổng hợp:

- 161 mẫu cần HNMU/UET xem lại;
- 98 mẫu cần xem lại phần truy xuất/đối chiếu học liệu;
- 57 mẫu cần xác nhận thêm với SGV.

## 7. Diễn giải so với các bản debug trước

Các bản debug trước từng có số lượng lớn mẫu lớp 8–9 rơi vào nhóm chưa rõ chủ đề hoặc chưa tìm được evidence học liệu. Sau khi đồng bộ lại theo registry SGK/SGV và sửa các kết quả đánh giá bị ảnh hưởng, các vấn đề chính hiện còn là:

1. Một số mức nhận thức cần chuẩn hóa nhãn.
2. Một mẫu thiếu nhãn AI trong hội thoại.
3. Một cặp câu hỏi trùng chính xác.
4. Một nhóm mẫu cần người xem lại vì bằng chứng học liệu/SGV hoặc diễn giải dàn giáo chưa đủ chắc.

Nói cách khác, vấn đề lớp 8–9 hiện không còn là lỗi ánh xạ hàng loạt như trước. Trạng thái mới đã phù hợp hơn để đi tiếp sang bước chọn mẫu/chuyển đổi thử, với điều kiện các mẫu trong hàng đợi ưu tiên cao được xem lại trước.

## 8. Validation

Python executable đã dùng:

```text
/home/quannda/miniconda3/envs/benchmark_env/bin/python
```

Đã chạy validator checklist mới nhất:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python agents/hnmu-dialogue-auditor/scripts/validate_raw_dialogue_audit_output.py experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/agent_shard_audit/merged/raw_dialogue_checklist_results.regex_repaired.csv
```

Kết quả:

```text
OK
```

## 9. Kết luận

Bộ dữ liệu lớp 8–9 sau đồng bộ mới nhất có chất lượng khả quan hơn bản debug trước. Độ phủ theo bài học đã đều, không còn nhóm không rõ chủ đề, checklist chi tiết đủ 18 tiêu chí/mẫu và tỉ lệ đạt theo lượt chấm tiêu chí đạt 95,49%.

Trước khi chuyển đổi rộng sang mẫu benchmark, nên xử lý trước 43 mẫu ưu tiên cao trong hàng đợi xem lại, xác nhận 19 nhãn mức nhận thức chưa rõ, sửa 1 hội thoại thiếu nhãn AI và quyết định cách xử lý 1 cặp câu hỏi trùng ở lớp 9.
