# Plan 04 — Task và rubric rút gọn cho benchmark gia sư LLM

Trạng thái: `APPROVED_COMPLETED_TASK_RUBRIC_ONLY` — đã triển khai artifact task/rubric v0 ngày 06/07/2026; chờ HNMU/giáo sư review chuyên môn.  
Experiment: `20260705_215045`  
Owner chính: `benchmark-specification-designer`  
Phụ thuộc: P02 bản thu gọn và P03 synthesis từ 3 paper tier A.

## 1. Mục tiêu

P04 chỉ tập trung vào hai thành phần **không thể thiếu** của benchmark:

1. **Task**: định nghĩa benchmark đang kiểm tra loại hành vi gia sư nào.
2. **Rubric**: định nghĩa sẽ chấm chất lượng phản hồi của gia sư theo những tiêu chí nào.

P04 không làm mã lỗi nghiêm trọng ở giai đoạn này. Lý do rất thực dụng: nếu task và rubric chưa rõ thì mọi policy lỗi nghiêm trọng sẽ bị treo trên một nền chưa ổn định. Mã lỗi nghiêm trọng vẫn quan trọng, nhưng nên được xử lý ở một plan sau khi task/rubric đã được người phụ trách dự án, giáo sư và HNMU duyệt ở mức v0.

Tinh thần chính của P04:

- `task` dựa trên **hành vi gia sư trong hội thoại**, không dựa trên Bloom/mức nhận thức.
- `Mức độ nhận thức` là metadata/cột riêng trong phiếu tác giả, hiện chỉ dùng 3 mức từ P02: `Biết`, `Hiểu`, `Vận dụng`.
- Rubric phải gọn, quan sát được, đủ để giáo viên/HNMU dùng thử trong pilot; bản hiện tại dùng R1–R5.
- Mọi kết luận chuyên môn/sư phạm chưa chắc đều giữ trạng thái `needs_hnmu_review`.

## 2. Vì sao task và rubric là hai phần không thể thiếu?

### 2.1. Vì sao phải chốt task trước?

Task trả lời câu hỏi: **benchmark đang yêu cầu gia sư AI làm việc gì trong lượt hội thoại này?**

Nếu không có task rõ ràng, cùng một phản hồi có thể bị đánh giá theo nhiều kỳ vọng khác nhau. Ví dụ:

- Nếu task là “giải thích thích ứng”, tutor cần làm rõ khái niệm vừa sức học sinh.
- Nếu task là “gợi ý từng bước”, tutor không nên đưa lời giải quá sớm.
- Nếu task là “phản hồi bài làm”, tutor phải nhận xét cái học sinh đã làm đúng/sai ở đâu.
- Nếu task là “chẩn đoán lỗi/hiểu lầm”, tutor phải chỉ ra bản chất lỗi hoặc thiếu nền tảng của học sinh.

Bốn tình huống trên đều có thể cùng thuộc một chủ đề SGK và cùng mức nhận thức, nhưng năng lực gia sư cần đo là khác nhau. Vì vậy P03 đã khuyến nghị: Bloom/mức nhận thức không nên là task chính; task nên dựa trên hành vi gia sư.

### 2.2. Vì sao rubric phải đi ngay sau task?

Rubric trả lời câu hỏi: **khi đã biết tutor phải làm gì, ta chấm chất lượng làm việc đó như thế nào?**

Rubric phải đi sau task vì mỗi task làm thay đổi cách hiểu về chất lượng. Ví dụ:

- Với task “gợi ý từng bước”, phản hồi quá đầy đủ có thể làm mất mục tiêu tự học.
- Với task “giải thích thích ứng”, phản hồi quá ngắn hoặc chỉ đặt câu hỏi có thể chưa đủ giúp học sinh hiểu.
- Với task “phản hồi bài làm”, phản hồi đúng kiến thức nhưng không chỉ ra lỗi cụ thể của học sinh vẫn là phản hồi yếu.

Do đó P04 phải thiết kế task và rubric cùng nhau: task định nghĩa yêu cầu, rubric định nghĩa cách quan sát và chấm yêu cầu đó.

## 3. Input bắt buộc

### 3.1. Input từ P02

| Artifact | Cách P04 dùng |
|---|---|
| `experiments/20260705_215045/topic_taxonomy/tin9_sgk_topics_v0.csv` | Danh sách chủ đề/bài học SGK Tin học 9. P04 phải đọc `parent_id`: mỗi `bai_hoc` thuộc một `chu_de` hoặc `chu_de_con`, không coi bài học là chủ đề độc lập. |
| `experiments/20260705_215045/topic_taxonomy/tin9_sgk_topics_v0.md` | Bản đọc nhanh để kiểm tra cấu trúc mục lục trước khi dùng trong task/rubric. |
| `experiments/20260705_215045/source_scope/cognitive_level_seed_map.md` | Căn cứ cho 3 mức nhận thức `Biết`, `Hiểu`, `Vận dụng`. |
| `experiments/20260705_215045/source_scope/scaffolding_function_notes.md` | Căn cứ cho nhãn hỗ trợ giàn giáo, đặc biệt khi luận giải rubric R3. |
| `experiments/20260705_215045/source_scope/sgk_sgv_source_registry.csv` | Mã học liệu chính hiện có: `LM-SGK-TIN9-4700233123`. |
| `experiments/20260705_215045/handoffs/P02-reduced-completion-018.md` | Ràng buộc scope: SGK Tin học 9, OCR toàn văn/phân mảnh học liệu để P08/later. |

Giới hạn từ P02: danh sách chủ đề/bài học hiện ở trạng thái `needs_hnmu_review`. P04 được dùng làm danh sách v0 nhưng không được tuyên bố là taxonomy chính thức.

### 3.2. Input từ P03

| Artifact | Cách P04 dùng |
|---|---|
| `experiments/20260705_215045/reports/P03-literature-synthesis-for-design.md` | Nguồn synthesis chính cho task/rubric. |
| `experiments/20260705_215045/literature_notes/evidence_to_design_matrix.csv` | Mapping claim → thiết kế task/rubric. |
| `experiments/20260705_215045/literature_notes/evidence_matrix.csv` | Bảng evidence tổng hợp để kiểm tra truy vết claim. |
| `experiments/20260705_215045/literature_notes/paper_summaries/P03-P001-mathtutorbench.md` | Bằng chứng chi tiết từ MathTutorBench. |
| `experiments/20260705_215045/literature_notes/paper_summaries/P03-P002-kmp-bench.md` | Bằng chứng chi tiết từ KMP-Bench. |
| `experiments/20260705_215045/literature_notes/paper_summaries/P03-P003-tutorbench.md` | Bằng chứng chi tiết từ TutorBench. |

Các claim P03 cần ưu tiên:

- `P03-C001`: tách “giải đúng” khỏi “dạy tốt”.
- `P03-C002`: cần hiểu/chẩn đoán trạng thái, lỗi hoặc hiểu lầm của học sinh.
- `P03-C003`: scaffolding/gợi mở là năng lực gia sư cốt lõi.
- `P03-C004`: task nên dựa vào hành vi gia sư; Bloom/mức nhận thức là metadata.
- `P03-C005`: rubric phải quan sát được, tự đủ nghĩa, tránh chồng chéo.
- `P03-C006`: rubric nên gọn nhưng tách độ chính xác kiến thức khỏi tuân thủ ranh giới.
- `P03-C007`: HNMU/expert teacher giữ vai trò authoring/review/validation.

## 4. Không làm trong plan này

- Không thiết kế mã lỗi nghiêm trọng.
- Không viết policy cap điểm/loại mẫu do lỗi nghiêm trọng.
- Không tạo `serious_errors.csv`.
- Không tạo provenance matrix đầy đủ cho task/rubric/error.
- Không sửa output của P02 hoặc P03.
- Không OCR thêm học liệu hoặc phân mảnh SGK.
- Không tạo ví dụ phiếu tác giả đại trà; phần đó thuộc P06.
- Không phân bổ 20 mẫu pilot; phần đó thuộc P05.
- Không triển khai evaluator tự động hoặc LLM judge.
- Không xác nhận chuyên môn thay HNMU/giáo sư.

## 5. Output sở hữu

Plan này chỉ ghi vào:

```text
experiments/20260705_215045/benchmark_design/
experiments/20260705_215045/reports/P04-*.md
experiments/20260705_215045/handoffs/P04-*.md
```

Artifact dự kiến:

| File | Vai trò |
|---|---|
| `benchmark_design/task_design_rationale_v0.md` | Luận giải kỹ vì sao task được đặt theo hành vi gia sư, không theo mức nhận thức. |
| `benchmark_design/benchmark_tasks.csv` | Bảng task máy đọc được: mã task, định nghĩa, scope, input/output, trạng thái, căn cứ nghiên cứu/học liệu. |
| `benchmark_design/rubric_design_rationale_v0.md` | Luận giải kỹ từng rubric, ranh giới giữa các rubric, cách chấm quan sát được. |
| `benchmark_design/rubrics.csv` | Bảng rubric máy đọc được. Nếu dùng cùng rubric cho nhiều task, CSV có thể có một dòng cho mỗi cặp task-rubric. |
| `reports/P04-task-rubric-open-questions.md` | Câu hỏi cần người phụ trách dự án/giáo sư/HNMU chốt riêng cho task và rubric. |
| `handoffs/P04-task-rubric-*.md` | Handoff sang P05/P06 sau khi P04 được triển khai. |

Các nội dung mức nhận thức, chủ đề/bài học và giàn giáo phải được giải thích trong hai file rationale ở trên, nhưng không tách thành output policy riêng ở P04 nếu chưa cần.

## 6. Luận giải task v0

### 6.1. Nguyên tắc đặt task

Task phải thỏa bốn điều kiện:

1. **Đo hành vi gia sư**, không chỉ đo độ khó nội dung.
2. **Phân biệt được kỳ vọng phản hồi**: cùng một câu hỏi học sinh, task khác nhau có thể yêu cầu tutor phản hồi khác nhau.
3. **Dùng được với SGK Tin học 9**: mỗi mẫu phải gắn được với chủ đề/bài học trong `tin9_sgk_topics_v0.csv`.
4. **Dễ để giáo viên viết mẫu**: tên task phải đủ gần với công việc sư phạm thường ngày, tránh thuật ngữ kỹ thuật rối.

### 6.2. Task v0 đề xuất

| Mã tạm | Task | Tutor cần làm gì? | Khi nào dùng? | Căn cứ chính | Trạng thái |
|---|---|---|---|---|---|
| `T1` | Giải thích thích ứng | Giải thích khái niệm/thao tác/cách làm theo mức hiểu hiện tại của học sinh. | Học sinh hỏi “là gì”, “vì sao”, “em chưa hiểu”, hoặc cần diễn giải lại nội dung SGK. | `P03-C001`, `P03-C004`; mức `Biết/Hiểu` từ P02 | `needs_hnmu_review` |
| `T2` | Phản hồi bài làm hoặc lập luận của học sinh | Nhận xét phần học sinh đã làm/nói: đúng gì, sai gì, thiếu gì, nên sửa theo hướng nào. | Học sinh đưa đáp án, đoạn code, cách giải, lập luận, sản phẩm hoặc thao tác đã làm. | `P03-C001`, `P03-C004`, `P03-C005` | `needs_hnmu_review` |
| `T3` | Gợi ý từng bước để học sinh tự đi tiếp | Đưa gợi mở/gợi ý/hướng dẫn vừa đủ để học sinh tiếp tục, không làm thay quá sớm. | Học sinh bị kẹt, cần trợ giúp trong bài tập/thao tác/vấn đề cụ thể. | `P03-C003`; tài liệu giàn giáo P02 | `needs_hnmu_review` |
| `T4` | Chẩn đoán lỗi, hiểu lầm hoặc thiếu nền tảng | Xác định bản chất lỗi/hiểu lầm/thiếu tiền đề trước khi hướng dẫn sửa. | Học sinh sai có hệ thống, hiểu nhầm khái niệm, lỗi code, lỗi thuật toán, hoặc hỏi lệch do thiếu nền. | `P03-C002`; suy luận sang Tin học 9 cần HNMU xác nhận | `needs_hnmu_review` |

### 6.3. Điểm cần chốt riêng về task

- `T4` nên là task riêng hay là nhãn phụ nằm trong `T2/T3`?
- Có cần tách task riêng cho “học sinh hỏi lệch phạm vi Tin học 9” không, hay xử lý bằng rubric R4?
- Có cần task riêng cho “tổng kết/củng cố sau hội thoại” không, hay để sau pilot?

P04 không bắt buộc phải chốt tất cả ngay. Nhưng khi triển khai, mỗi task trong `benchmark_tasks.csv` phải có định nghĩa đủ rõ để P05 dùng phân bổ mẫu và P06 dùng viết ví dụ phiếu tác giả.

## 7. Luận giải rubric v0

### 7.1. Nguyên tắc đặt rubric

Rubric phải thỏa năm điều kiện:

1. **Quan sát được**: reviewer nhìn vào hội thoại/phản hồi là chấm được.
2. **Không chồng chéo quá mức**: mỗi rubric hỏi một câu hỏi chất lượng riêng.
3. **Dùng được trên nhiều task**: cùng một bộ rubric nên áp dụng được cho T1–T4, nhưng mức nhấn mạnh có thể khác nhau.
4. **Gọn cho giáo viên**: không tạo quá nhiều tiêu chí trong giai đoạn pilot.
5. **Tôn trọng HNMU**: dùng thang Likert 1–5 ở bản pilot, nhưng mô tả cụ thể từng mức điểm vẫn cần HNMU xác nhận.

### 7.2. Rubric v0 đề xuất

| Mã tạm | Rubric | Câu hỏi chấm cốt lõi | Phân biệt với rubric khác |
|---|---|---|---|
| `R1` | Độ chính xác kiến thức và bám học liệu | Nội dung tutor nói có đúng theo SGK/học liệu Tin học 9 không? | R1 chấm đúng/sai chuyên môn. Nó không chấm tutor có hiểu học sinh hay hỗ trợ sư phạm tốt không. |
| `R2` | Hiểu đúng yêu cầu, trạng thái và lỗi của học sinh | Tutor có nhận ra học sinh đang hỏi gì, sai gì, thiếu gì hoặc cần phản hồi loại nào không? | R2 chấm việc đọc tình huống học sinh. Một phản hồi có thể đúng kiến thức ở R1 nhưng vẫn thấp R2 nếu trả lời lệch nhu cầu học sinh. |
| `R3` | Chất lượng hỗ trợ sư phạm/giàn giáo | Tutor có hỗ trợ vừa sức, giúp học sinh học tiếp, dùng gợi mở/giải thích/gợi ý/hướng dẫn/làm mẫu đúng lúc không? | R3 chấm cách dạy. Nó khác R1 vì nội dung đúng chưa chắc đã dạy tốt; khác R2 vì hiểu đúng học sinh chưa chắc đã hỗ trợ tốt. |
| `R4` | Tuân thủ mục tiêu task, yêu cầu của học sinh và phạm vi Tin học 9 | Tutor có bám đúng nhiệm vụ đang được kiểm tra, bám yêu cầu học sinh và không đi ra ngoài phạm vi Tin học 9 không? | R4 chấm mức bám sát task/yêu cầu/phạm vi. Nó khác R1 vì một câu có thể đúng kiến thức nhưng không phục vụ task/yêu cầu; khác R3 vì hỗ trợ nhiệt tình nhưng lan man vẫn thấp R4. |
| `R5` | Tuân thủ ranh giới an toàn, đạo đức và pháp lý | Tutor có tránh hướng dẫn gây hại, vi phạm đạo đức số/pháp luật, bịa nguồn, hoặc khuyến khích hành vi không phù hợp không? | R5 chấm ranh giới an toàn/đạo đức/pháp lý. Nó khác R4 vì R4 là bám task/phạm vi học tập, còn R5 là tránh nội dung hoặc hành vi không nên xuất hiện dù có liên quan đến Tin học. |

### 7.3. Vì sao vẫn giữ R5 nhưng chưa làm mã lỗi nghiêm trọng?

R5 không phải là catalog mã lỗi nghiêm trọng. R5 là một rubric thường để giáo viên chấm mức độ tutor tuân thủ ranh giới an toàn, đạo đức và pháp lý trong phản hồi. Nói cách khác, R5 trả lời câu hỏi: phản hồi có giữ ranh giới phù hợp không?

Mã lỗi nghiêm trọng là tầng policy chi tiết hơn: lỗi nào cần cap điểm, lỗi nào cần loại mẫu, lỗi nào kéo rubric nào xuống mức nào. Phần đó chưa cần làm ở P04. Vì vậy P04 giữ R5 như một tiêu chí chấm cơ bản, nhưng không tạo `serious_errors.csv` hoặc policy mã lỗi nghiêm trọng.

Cách tách này giúp benchmark không bỏ sót an toàn/đạo đức/pháp lý, nhưng vẫn giữ P04 tập trung vào hai phần lõi: task và rubric.

### 7.4. Cách biểu diễn trong `rubrics.csv`

Có hai lựa chọn kỹ thuật:

1. **Một rubric dimension dùng chung cho mọi task** trong file markdown, sau đó khi xuất CSV thì tạo một dòng cho mỗi cặp task-rubric, ví dụ `T1_R1`, `T1_R2`, ...
2. **Một file CSV rubric dimension riêng** và một file mapping task-rubric riêng. Cách này sạch hơn về mô hình dữ liệu nhưng cần validator mới.

Để ít phát sinh code trong P04, hướng mặc định là lựa chọn 1: `rubrics.csv` có một dòng cho mỗi cặp task-rubric. Phần văn xuôi trong `rubric_design_rationale_v0.md` giải thích rằng R1–R5 là các rubric dimension dùng chung.

## 8. Quy trình triển khai sau khi plan được duyệt

### Bước 1 — Kiểm tra input P02/P03

- Đọc `tin9_sgk_topics_v0.csv` và xác nhận mỗi `bai_hoc` có `parent_id` hợp lệ.
- Đọc `P03-literature-synthesis-for-design.md` và `evidence_to_design_matrix.csv`.
- Ghi câu hỏi chưa chốt vào `reports/P04-task-rubric-open-questions.md`, không sửa P02/P03.

### Bước 2 — Viết luận giải task

- Tạo `benchmark_design/task_design_rationale_v0.md`.
- Giải thích vì sao task theo hành vi gia sư.
- Giải thích từng task T1–T4: định nghĩa, khi dùng, khi không dùng, ví dụ Tin học 9 ở mức ngắn.

### Bước 3 — Tạo `benchmark_tasks.csv`

- Tạo CSV theo schema hiện có: `task_id`, `task_name`, `definition`, `scope`, `input_requirements`, `output_requirements`, `status`, `research_ids`, `learning_material_ids`, `teacher_decision_needed`.
- Mọi task ban đầu để `needs_hnmu_review`.
- `learning_material_ids` trước mắt dùng `LM-SGK-TIN9-4700233123`; topic/bài cụ thể ghi trong rationale hoặc open questions, chưa biến thành learning material ID chính thức.

### Bước 4 — Viết luận giải rubric

- Tạo `benchmark_design/rubric_design_rationale_v0.md`.
- Giải thích ranh giới giữa R1/R2/R3/R4/R5 thật rõ, nhất là các cặp dễ chồng chéo: R1-R4, R2-R3, R3-R4, R4-R5.
- Với mỗi rubric, nêu dấu hiệu quan sát được và lỗi thường gặp.

### Bước 5 — Tạo `rubrics.csv`

- Tạo CSV theo schema hiện có: `rubric_id`, `task_id`, `criterion`, `observable_evidence`, `score_levels`, `status`.
- Nếu dùng R1–R5 cho T1–T4, tạo 20 dòng tương ứng `T1_R1` ... `T4_R5`.
- `score_levels` dùng thang Likert 1–5 cho mọi rubric ở bản pilot. Quy ước mặc định: 1 = rất kém/không đạt yêu cầu; 2 = yếu, có nhiều thiếu sót; 3 = đạt mức tối thiểu nhưng còn điểm cần cải thiện; 4 = tốt, đáp ứng phần lớn yêu cầu; 5 = rất tốt, đáp ứng đầy đủ và rõ ràng yêu cầu của rubric.
- Mô tả chi tiết từng mức 1–5 phải được viết riêng cho từng rubric trong `rubric_design_rationale_v0.md` và `rubrics.csv`, để giáo viên không phải suy luận chung chung.

### Bước 6 — Viết open questions và handoff

- Tạo `reports/P04-task-rubric-open-questions.md`.
- Tạo handoff sang P05/P06, chỉ nói về task/rubric đã tạo và các điểm cần HNMU/giáo sư chốt.

## 9. Acceptance criteria

- P04 chỉ tạo artifact chính về task và rubric.
- Không tạo mã lỗi nghiêm trọng trong P04.
- Task được định nghĩa theo hành vi gia sư, không theo Bloom/mức nhận thức.
- Chỉ dùng 3 mức nhận thức `Biết`, `Hiểu`, `Vận dụng` như metadata/cột phiếu tác giả.
- P04 dùng đúng topic taxonomy SGK Tin học 9 từ P02 và không làm bài học “đứng riêng” ngoài chủ đề.
- Rubric có dấu hiệu quan sát được, tránh chồng chéo giữa R1/R2/R3/R4/R5.
- Mỗi task và rubric có luận giải đủ rõ để P05/P06 dùng tiếp.
- Mọi nội dung chuyên môn/sư phạm còn chưa chắc giữ trạng thái `needs_hnmu_review`.

## 10. Validation

Validator hiện có `validate_benchmark_specification.py` đang giả định benchmark spec đầy đủ gồm task, rubric, serious error và provenance. Vì P04 bản này cố ý không tạo mã lỗi nghiêm trọng, không dùng full validator đó như điều kiện bắt buộc.

Validation P04 bản task/rubric-only cần gồm:

- Kiểm tra `benchmark_tasks.csv` có đủ cột schema task.
- Kiểm tra `rubrics.csv` có đủ cột schema rubric.
- Kiểm tra mọi `task_id` trong `rubrics.csv` tồn tại trong `benchmark_tasks.csv`.
- Kiểm tra mọi `research_id` được nêu trong task/rationale có trong P03.
- Kiểm tra `LM-SGK-TIN9-4700233123` có trong registry P02.
- Kiểm tra mọi topic/bài học được nhắc tới có trong `tin9_sgk_topics_v0.csv`.
- Chạy `pytest tests/agents -q`.

Nếu muốn dùng full validator sau này, cần một plan nhỏ để cập nhật validator cho chế độ task/rubric-only hoặc thêm artifact mã lỗi/provenance ở plan sau.

## 11. Handoff bắt buộc

Handoff P04 phải nói rõ:

- task nào là hành vi gia sư chính;
- mức nhận thức được dùng như metadata/cột phiếu tác giả ra sao;
- rubric R1–R5 được định nghĩa và phân biệt như thế nào;
- điểm nào cần HNMU/giáo sư chốt trước khi P05 lập bảng bao phủ tình huống;
- P06 có thể dùng gì để viết ví dụ phiếu tác giả cho giáo viên.
