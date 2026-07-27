# Plan 03 — Xây dựng và kiểm định benchmark theo năng lực gia sư và nguyên tắc sư phạm

Experiment: `20260722_000940`
Trạng thái: `SUPERSEDED_BY_20260727_170150` — Workstreams A–B và grounding pool được giữ làm nền; phương pháp chọn trực tiếp tập nguyên tắc ở C không chạy tiếp, vì experiment kế nhiệm chuyển sang `requirement_score` 1–5 và Vertex AI trực tiếp
Ngày cập nhật: 27/07/2026
Phụ thuộc: Plan 02 đã hoàn thành và công bố bundle `full_v0`

## 0. Phạm vi và cổng dừng hiện tại

Người phụ trách dự án đã duyệt phạm vi Workstreams A–D. Sau quyết định đơn giản hóa ngày 26/07/2026, trạng thái được khóa như sau:

- Workstream A đã hoàn tất nền tảng đo lường và truy vết nghiên cứu;
- Workstream B đã hoàn tất mô hình sáu năng lực ở mức **UET phê duyệt tạm thời**, chưa phải xác nhận HNMU;
- sáu năng lực là nền tảng xác định các chiều chất lượng và rubric, không phải nhãn phân loại bối cảnh;
- benchmark hiện chỉ có một nhiệm vụ: sinh phản hồi tiếp theo của gia sư AI cho một `benchmark_candidate_id`;
- sáu nguyên tắc `Challenge`, `Explanation`, `Modelling`, `Practice`, `Feedback`, `Questioning` do KMP-Bench vận hành là nhãn sư phạm đa nhãn cấp ứng viên;
- mỗi ứng viên có một tập nguyên tắc không thứ tự; không có giới hạn cứng ở hai, nhưng mỗi nguyên tắc phải vượt qua phép kiểm tra “không thể bỏ” và trường hợp có hơn ba nguyên tắc tự động vào hàng đợi UET;
- nhánh tám nhiệm vụ `TASK-PROBE` đến `TASK-CONSOLIDATE`, 20 nhãn thử và packet C1 cũ đã được chuyển vào `outputs/benchmark_specification/legacy/eight_task_candidate_branch/`; chúng không tham gia mã hóa, hiệu chỉnh, độ phủ hay rà soát hiện hành;
- thống kê 2.028 ứng viên, mẫu khám phá 160 hội thoại gốc và bảng đầu vào mã hóa vẫn được tái sử dụng;
- số nhãn nguyên tắc chính thức hiện là 0; C0a/C0b đầu tiên dùng schema chính–phụ và `gold_response`, nên toàn bộ metric cũ chỉ là bằng chứng chẩn đoán cho thiết kế đã bị thay thế;
- packet 29 dòng của lần chạy đầu được giữ làm bằng chứng chẩn đoán, nhưng UET không cần phân xử từng dòng; lần chạy mới chỉ được mở sau khi schema tập nhãn, grounding input không có `gold_response`, validator và lô phân tầng 6–9 đã hoàn tất;
- HNMU sẽ review một gói tích hợp gồm sáu nguyên tắc, sáu năng lực, rubric và ví dụ sau Workstream D; không review rời từng phần.

Workstreams E–G vẫn là bản nháp và chưa được phép chạy. Không artifact nào được gắn `confirmed` trước quyết định đúng thẩm quyền.

## 1. Mục tiêu

Plan 03 xây dựng đặc tả cho benchmark gia sư AI môn Tin học THCS lớp 6–9 từ căn cứ nghiên cứu, phương pháp HNMU và 2.028 ứng viên hiện có. Thiết kế hiện hành chủ động dùng hai nền tảng đã có ranh giới rõ nhất:

1. sáu nguyên tắc sư phạm được KMP-Bench vận hành để mô tả yêu cầu sư phạm nổi bật của từng mẫu;
2. sáu năng lực gia sư được Workstreams A–B xây dựng để mô tả chất lượng phản hồi cần đo.

Plan phải trả lời và tạo bằng chứng cho ba câu hỏi:

1. Một gia sư AI Tin học THCS tốt cần thể hiện những năng lực nào trong một lượt phản hồi?
2. Sáu nguyên tắc KMP có bao phủ được các yêu cầu sư phạm quan sát thấy trong dữ liệu hiện tại không?
3. Hệ tiêu chí dựa trên năng lực và nguyên tắc có phân biệt được phản hồi tốt, trung bình và kém hay không?

Kết quả cuối là đặc tả v1 đã qua thí điểm và được HNMU/UET xác nhận ở các cổng chuyên môn. Plan không tuyên bố đo tiến bộ học tập dài hạn, hiệu quả của cả hệ thống nhiều lượt hoặc kết quả học tập thật của học sinh.

## 2. Đối tượng đo và đơn vị đánh giá

### 2.1. Đối tượng đo

Benchmark đo chất lượng **phản hồi tiếp theo của gia sư AI** trong một bối cảnh hội thoại Tin học THCS cố định. Mỗi phản hồi được đánh giá theo:

- mức đáp ứng nhiệm vụ chung là sinh phản hồi gia sư tiếp theo;
- các chiều năng lực chung có thể quan sát từ phản hồi;
- các tiêu chí gắn với toàn bộ nguyên tắc trong tập nhãn của ứng viên;
- các lỗi nghiêm trọng có thể làm phản hồi không còn chấp nhận được.

### 2.2. Đơn vị đánh giá

Đơn vị benchmark là một `benchmark_candidate_id`, gồm:

- `student_prompt`;
- `conversation_history`, có thể rỗng;
- `gold_answer`;
- `gold_response`;
- bối cảnh học liệu và truy vết ở bảng riêng.

Một `sample_id` có thể sinh nhiều ứng viên. Mọi phân tích và phép chia dữ liệu phía sau phải giữ các ứng viên cùng `sample_id` trong một nhóm để tránh rò rỉ dữ liệu. Báo cáo kết quả phải có cả chỉ số trung bình theo ứng viên và theo hội thoại gốc, hoặc một cách gán trọng số tương đương đã được chốt trước khi chấm.

## 3. Phân loại phát biểu theo căn cứ

Mọi kết quả chuyên môn của Plan 03 phải phân loại phát biểu:

- `evidence`: có căn cứ trực tiếp từ bài báo, phương pháp HNMU, học liệu hoặc dữ liệu ứng viên;
- `inference`: suy luận thiết kế của UET/tác nhân từ bằng chứng;
- `teacher_decision_needed`: cần HNMU/UET quyết định về chuyên môn, sư phạm hoặc cách vận hành.

Tác nhân không được đổi `inference` thành “đã xác nhận” chỉ vì quy trình phần mềm chạy được. HNMU giữ quyền quyết định về năng lực gia sư, cách áp dụng nguyên tắc, nội dung tiêu chí, mốc chất lượng và lỗi chuyên môn/sư phạm.

## 4. Input chỉ đọc

### 4.1. Candidate và provenance từ Plan 02

- `outputs/benchmark_conversion/full_v0/benchmark_candidate_splits.csv`
- `outputs/benchmark_conversion/full_v0/conversion_trace.csv`
- `outputs/benchmark_conversion/full_v0/conversion_dispositions.csv`
- `outputs/benchmark_conversion/full_v0/conversion_summary.json`
- `reports/plan02-full-multi-candidate-conversion-summary.md`

Pool hiện tại gồm 2.028 candidate từ 665 raw dialogue `pass`.

### 4.2. Tổng hợp bốn paper trước Plan 03

- `literature_notes/pre_plan03_task_rubric_review/review_protocol.md`
- `literature_notes/pre_plan03_task_rubric_review/search_log.csv`
- `literature_notes/pre_plan03_task_rubric_review/evidence_matrix.csv`
- `literature_notes/pre_plan03_task_rubric_review/operational_claim_matrix.csv`
- `literature_notes/pre_plan03_task_rubric_review/paper_summaries/`
- `reports/pre-plan03-four-paper-task-rubric-operational-synthesis.md`

Các kết luận vận hành chính cần giữ:

- task trong MathTutorBench, KMP-Bench và TutorBench chủ yếu là bối cảnh/hợp đồng hành vi mà gia sư phải xử lý;
- `gold_response` là đối chứng hoặc căn cứ biên soạn, không phải chuỗi duy nhất được chấp nhận;
- KMP-Bench minh họa luồng từ nguyên tắc sư phạm tới tiêu chí quan sát được và chấm theo từng tiêu chí;
- TutorBench cho thấy rubric có thể thay đổi theo mẫu, nhưng 3–39 tiêu chí/mẫu quá tốn kém cho dữ liệu hiện tại;
- không paper nào tự nó chứng minh một thiết kế là phù hợp cho tiếng Việt và Tin học THCS.

### 4.3. Nghiên cứu và thiết kế kế thừa

- `experiments/20260705_215045/literature_notes/evidence_matrix.csv`
- `experiments/20260705_215045/literature_notes/evidence_to_design_matrix.csv`
- `inherited_resources/from_20260705_215045/benchmark_design/benchmark_tasks.csv`
- `inherited_resources/from_20260705_215045/benchmark_design/rubrics.csv`
- `inherited_resources/from_20260705_215045/benchmark_design/task_design_rationale_v0.md`
- `inherited_resources/from_20260705_215045/benchmark_design/rubric_design_rationale_v0.md`

T1–T4 và R1–R5 là artifact thử nghiệm. Plan 03 không có nghĩa vụ giữ ID hoặc semantics của chúng. Nếu tái sử dụng, hợp nhất, tách hoặc loại bỏ thì phải ghi `legacy_spec_dispositions.csv`.

### 4.4. Học liệu và phương pháp HNMU

- `shared/learning_resources/registries/sgk_thcs_topic_lesson_map_v0.csv`
- `shared/learning_resources/fragments/learning_resource_fragments.csv`
- `shared/learning_resources/agent_context/hnmu_cognitive_level_method_canonical.md`
- `shared/learning_resources/agent_context/hnmu_scaffolding_method_canonical.md`

Ma trận coverage cũ thiên về lớp 9 chỉ dùng để tham khảo cấu trúc, không phải target coverage của benchmark lớp 6–9.

## 5. Nguyên tắc thiết kế đã chốt ở mức plan

1. Benchmark có một nhiệm vụ chung: sinh phản hồi tiếp theo của gia sư AI.
2. Sáu nguyên tắc KMP là nhãn sư phạm đa nhãn cấp ứng viên, không phải sáu nhiệm vụ benchmark loại trừ lẫn nhau.
3. Mỗi ứng viên có một tập nguyên tắc không thứ tự; không giới hạn cứng số nhãn, không ép nhãn khi thiếu căn cứ và tự động đưa trường hợp có hơn ba nguyên tắc vào review.
4. Sáu năng lực Workstreams A–B là nền tảng của chiều chất lượng và rubric; chúng không bị nhập làm nhãn nguyên tắc.
5. Hệ tiêu chí chỉ có **hai tầng**:
   - tầng 1: chiều năng lực chung;
   - tầng 2: tiêu chí riêng theo nguyên tắc sư phạm áp dụng cho mẫu.
6. Không tạo tầng tiêu chí riêng theo từng ứng viên.
7. Quá trình **gán nguyên tắc** chỉ dùng context trước target, `source_question`, `gold_answer` và mảnh học liệu được phép; tuyệt đối không dùng `gold_response`. Sau khi tập nguyên tắc và rubric đã khóa độc lập, `gold_response` mới có thể tham gia ngữ cảnh **đánh giá response** như một response tham chiếu, không phải cách trả lời duy nhất được chấp nhận.
8. Lỗi nghiêm trọng được xử lý bằng danh mục và cổng riêng, không bị hòa tan trong điểm trung bình.
9. Không gán trước một mô hình là tốt, trung bình hoặc kém; mức chất lượng được xác định từ đánh giá mù.
10. Hệ tiêu chí chỉ được khóa sau bằng chứng nội dung, bằng chứng vận hành và thí điểm khả năng phân biệt.

## 6. Workstream A — Bổ sung căn cứ khoa học về đo lường

Bốn bài báo hiện tại giải thích benchmark gia sư nhưng chưa đủ cho hiệu lực nội dung, độ đồng thuận và khả năng phân biệt. Trước khi chốt đặc tả, Plan 03 mở rộng tổng quan nghiên cứu có truy vết về:

- thiết kế lấy bằng chứng làm trung tâm hoặc khung tương đương cho năng lực–nhiệm vụ–bằng chứng;
- hiệu lực nội dung và quy trình chuyên gia;
- độ tin cậy và đồng thuận giữa người chấm;
- độ khó, khả năng phân biệt và hiệu ứng sàn/trần;
- kiểm định LLM chấm điểm, gồm thiên lệch vị trí và độ khớp với người chấm;
- giới hạn của ưu tiên theo cặp khi phản hồi tham chiếu không phải đáp án duy nhất.

### Mã nguồn và kết quả

Không viết mã ở Workstream này. Dùng đúng một `research-methodologist` theo mục 15.1 và ghi:

`literature_notes/plan03_measurement_foundations/`

- `review_protocol.md`
- `search_log.csv`
- `source_registry.csv`
- `evidence_matrix.csv`
- `claim_matrix.csv`
- `measurement_design_synthesis.md`

Chỉ nguồn đã xác minh mới nhận `research_id`. Không bịa DOI, mã arXiv hoặc kết luận vượt quá nguồn.

### Gate A

- giao thức và tiêu chí nguồn được ghi trước bản tổng hợp;
- mỗi phát biểu thiết kế có vị trí nguồn hoặc nhãn `inference`;
- các giới hạn áp dụng cho dữ liệu tiếng Việt/Tin học THCS được nêu rõ.

## 7. Workstream B — Xây dựng mô hình năng lực gia sư AI

### 7.1. Sáu miền năng lực ban đầu

Plan bắt đầu khám phá từ sáu miền ban đầu, chưa coi là hệ tiêu chí cuối:

1. chính xác chuyên môn và bám học liệu;
2. mô hình hóa trạng thái học sinh;
3. lựa chọn chiến lược sư phạm;
4. điều chỉnh mức hỗ trợ;
5. thúc đẩy tư duy và quyền chủ động;
6. giao tiếp, động lực và phù hợp lứa tuổi.

Danh sách được phép hợp nhất, tách, đổi tên hoặc bổ sung nếu nghiên cứu, HNMU hoặc dữ liệu cung cấp bằng chứng.

### 7.2. Luồng xây dựng

Tham khảo logic của KMP-Bench nhưng không sao chép hệ thống phân loại:

```text
bằng chứng nghiên cứu + phương pháp HNMU + dữ liệu ứng viên
                              ↓
             miền năng lực ban đầu và định nghĩa ranh giới
                              ↓
      hành vi quan sát được + biểu hiện tốt/trung bình/kém
                              ↓
          đối chiếu chồng lấn/khoảng trống và phản ví dụ biên
                              ↓
              HNMU rà soát nội dung và mức cần thiết
                              ↓
             mô hình năng lực bản nháp để thí điểm
```

Mỗi năng lực phải có:

- định nghĩa và phạm vi;
- điều không thuộc năng lực đó;
- cơ sở nghiên cứu/phương pháp;
- bằng chứng quan sát được trong một phản hồi;
- mốc biểu hiện tốt, trung bình và kém;
- quan hệ với nhiệm vụ và tiêu chí;
- giới hạn suy luận;
- trạng thái và thẩm quyền cần duyệt.

### 7.3. Kết quả

`outputs/benchmark_specification/construct_v1_draft/`

- `tutor_capability_model.md`
- `tutor_capabilities.csv`
- `capability_observable_evidence.csv`
- `capability_overlap_matrix.csv`
- `capability_research_provenance.csv`
- `research_source_registry.csv`
- `research_support_matrix.csv`
- `capability_research_basis.md`
- `capability_open_questions.md`

### Gate B

- không còn hai năng lực có định nghĩa hoặc bằng chứng quan sát trùng nhau mà chưa có quy tắc ranh giới và quyết định xử lý tạm thời;
- không có năng lực chỉ được mô tả bằng tính từ chung chung;
- đại diện UET xác nhận tạm thời mỗi năng lực đủ rõ và có thể quan sát ở đơn vị “một phản hồi” để làm giả thuyết đầu vào của C;
- các giới hạn suy luận và câu hỏi cần HNMU quyết định được giữ nguyên trong hồ sơ;
- HNMU xác nhận hoặc yêu cầu sửa về tính đầy đủ, sự phù hợp với môn Tin học và lứa tuổi trong gói tích hợp sau Workstream D, trước khi khóa đặc tả.

## 8. Workstream C — Kiểm tra độ phủ sáu nguyên tắc KMP trên dữ liệu

### 8.1. Kiến trúc một nhiệm vụ

Mọi `benchmark_candidate_id` cùng thuộc nhiệm vụ:

`TASK-NEXT-TUTOR-RESPONSE` — sinh phản hồi tiếp theo của gia sư AI từ `conversation_history`, `student_prompt` và ngữ cảnh học liệu đã khóa.

Các khác biệt sư phạm giữa ứng viên được mô tả bằng nguyên tắc, không tách thành các nhiệm vụ benchmark mới. Quyết định này làm giảm gánh nặng phân xử hệ phân loại nhưng vẫn giữ khả năng phân tích theo yêu cầu sư phạm.

### 8.2. Sáu nguyên tắc được dùng làm nhãn cấp ứng viên

| ID | Tên tiếng Anh | Cách hiểu vận hành trong dự án |
|---|---|---|
| `PRINCIPLE-CHALLENGE` | Challenge | Đặt yêu cầu vừa sức nhưng có độ căng nhận thức để học sinh tiến thêm. |
| `PRINCIPLE-EXPLANATION` | Explanation | Làm rõ khái niệm, quan hệ, nguyên nhân hoặc cách hiểu cốt lõi. |
| `PRINCIPLE-MODELLING` | Modelling | Minh họa một cách làm, quy trình suy nghĩ hoặc sản phẩm mẫu có thể quan sát. |
| `PRINCIPLE-PRACTICE` | Practice | Tạo cơ hội cho học sinh thực hành, áp dụng hoặc củng cố. |
| `PRINCIPLE-FEEDBACK` | Feedback | Phản hồi dựa trên bài làm/ý kiến của học sinh để chỉ ra điểm đúng, điểm cần sửa và hướng tiến bộ. |
| `PRINCIPLE-QUESTIONING` | Questioning | Dùng câu hỏi có mục đích để thăm dò, kích hoạt suy nghĩ hoặc giúp học sinh tự kiến tạo bước tiếp theo. |

Định nghĩa đầy đủ, điều kiện gồm/loại và dấu hiệu quan sát nằm trong `pedagogical_principles.csv` và `task_discovery_codebook.md`. Sách gốc của Allison và Tharby mô tả sáu nguyên tắc có quan hệ qua lại, được kết nối linh hoạt và không tạo thành một chu trình hay sáu lớp loại trừ nhau. KMP-Bench chủ động gán một hoặc hai nguyên tắc khi **thiết kế trước** hành động gia sư, nhưng không chứng minh hai là giới hạn sư phạm phổ quát và không cung cấp quy tắc gán hậu nghiệm cho hội thoại đã tồn tại. Vì dữ liệu HNMU có thể chứa nhiều chức năng sư phạm đồng thời, dự án dùng một tập nhãn không thứ tự và không kế thừa giới hạn hai của pipeline sinh dữ liệu KMP-Bench.

### 8.3. Quy tắc đa nhãn và khoảng trống độ phủ

- Mỗi ứng viên có một `principle_set` là tập con không thứ tự của sáu nguyên tắc.
- Mỗi nguyên tắc chỉ được chọn khi tạo ra một yêu cầu sư phạm độc lập, quan sát được và vượt qua phép kiểm tra “không thể bỏ”: nếu bỏ nguyên tắc đó, một nhu cầu sư phạm riêng của học sinh sẽ không còn được đáp ứng.
- Không thêm nhãn chỉ vì hình thức bề mặt của response có câu hỏi, lời giải thích, ví dụ hoặc lời nhận xét. Không dùng thêm nhãn để lưu bất định hay hòa giải hai dự đoán khác nhau.
- Không đặt giới hạn cứng là hai. Candidate có hơn ba nguyên tắc vẫn hợp lệ nhưng tự động vào review; mỗi nguyên tắc phải có `selection_rationale`, `context_evidence` và, nếu có, `grounding_evidence` riêng.
- Nếu vòng context và vòng grounding tạo hai tập khác nhau, giữ hợp của chúng chỉ khi từng nguyên tắc đều vượt qua phép kiểm tra “không thể bỏ”; nếu không thì giữ tập có căn cứ tốt hơn hoặc chuyển UET review.
- Nếu không nguyên tắc nào phù hợp, để tập nhãn rỗng và ghi `coverage_gap_reason`.
- Không được tự thêm nguyên tắc thứ bảy chỉ từ một trường hợp. AI ghi nhận khoảng trống; UET xem xét bằng chứng lặp lại; HNMU quyết định trong gói tích hợp nếu khoảng trống có ý nghĩa chuyên môn–sư phạm.

Sáu năng lực không được gán thay cho nguyên tắc. Ví dụ, `CAP-DIAG` có thể được quan sát trong một mẫu `Questioning` hoặc `Feedback`, nhưng “chẩn đoán” không vì thế trở thành task hay nguyên tắc thứ bảy.

### 8.3.1. Thống kê và mẫu khám phá

Tái sử dụng census xác định của toàn bộ 2.028 ứng viên và mẫu 160 ứng viên thuộc 160 hội thoại gốc, mục tiêu 40 ứng viên mỗi lớp. Các tầng lấy mẫu gồm lớp, lịch sử hội thoại, độ sâu, mức nhận thức, chủ đề/bài học, dạng nội dung và vị trí lượt gia sư. Bước này chỉ hỗ trợ độ phủ; không tự sinh nhãn.

### 8.3.2. Tạo specialist `pedagogical-principle-annotator`

Trước khi mã hóa lô 40 đầu tiên, dự án phải tạo một specialist riêng để **áp dụng** codebook sáu nguyên tắc. Không dùng `benchmark-specification-designer` làm coder chính vì agent này sở hữu việc thiết kế và sửa codebook; tách hai vai trò giúp giảm nguy cơ agent tự củng cố hệ phân loại do chính nó xây dựng.

#### Phân công trách nhiệm

| Thành phần | Trách nhiệm | Không được làm |
|---|---|---|
| `benchmark-specification-designer` | Sở hữu định nghĩa, ranh giới, thay đổi codebook và thiết kế rubric. | Không tự coi nhãn mình gán là bằng chứng codebook đúng. |
| `pedagogical-principle-annotator` | Áp dụng codebook đã khóa lên candidate, tạo nhãn đề xuất và hàng đợi rà soát. | Không sửa `pedagogical_principles.csv`, codebook, rubric hoặc tự thêm nguyên tắc. |
| `UET-REVIEWER-01` | Review kết quả A/B, xem xung đột, khoảng trống, tác động của grounding và phân xử tạm thời. | Không phải gán mù trước run; không biến chỉ số AI–AI thành độ tin cậy giữa hai người chấm. |
| HNMU | Xác nhận chuyên môn–sư phạm trong gói tích hợp sau D. | Không bị thay thế bởi quyết định của agent hoặc validator. |

#### Cấu trúc specialist phải tạo

```text
agents/pedagogical-principle-annotator/
├── SKILL.md
└── references/
    └── two_pass_annotation_contract.md

.codex/agents/pedagogical-principle-annotator.toml
.claude/agents/pedagogical-principle-annotator.md
.agents/skills/pedagogical-principle-annotator
```

`SKILL.md` chỉ chứa quy trình cốt lõi, thẩm quyền và điều kiện đóng khi lỗi. `references/two_pass_annotation_contract.md` chứa bản tóm tắt vận hành ngắn về ranh giới sáu nguyên tắc, quan hệ nguyên tắc–năng lực và quy tắc đa nhãn; không sao chép toàn bộ lịch sử luận giải nghiên cứu. Hai file này phải nêu trực tiếp đường dẫn tới:

- `experiments/20260722_000940/outputs/benchmark_specification/task_discovery/pedagogical_principles.csv`;
- `experiments/20260722_000940/outputs/benchmark_specification/task_discovery/task_discovery_codebook.md`;
- `experiments/20260722_000940/outputs/benchmark_specification/construct_v1_draft/tutor_capabilities.csv`;
- `experiments/20260722_000940/outputs/benchmark_specification/construct_v1_draft/tutor_capability_model.md`;
- `experiments/20260722_000940/outputs/benchmark_specification/construct_v1_draft/capability_overlap_matrix.csv`.

Ba bảng CSV `pedagogical_principles.csv`, `tutor_capabilities.csv` và `capability_overlap_matrix.csv` là tài liệu bắt buộc đọc đầy đủ khi chạy. Hai file Markdown `task_discovery_codebook.md` và `tutor_capability_model.md` là tài liệu nguồn gốc được khóa hash nhưng chỉ mở khi ba bảng và hợp đồng ngắn chưa giải quyết được một ranh giới cụ thể. Cách này giảm lượng đọc lặp lại nhưng vẫn bảo toàn truy vết. Bảng nguyên tắc quyết định nhãn; hai bảng năng lực giúp specialist không trộn “nguyên tắc cần thực hiện” với “năng lực quyết định chất lượng thực hiện”. Specialist phải dừng đóng nếu thiếu file, lệch hash hoặc đường dẫn trong skill/reference không khớp manifest.

Model mặc định: `gpt-5.4-mini`, reasoning `medium`. Người phụ trách dự án đã duyệt **đúng hai instance** cho pilot đầu tiên với các điều kiện sau:

- lý do fan-out: kiểm tra khả năng chạy song song ở quy mô lớn và phát hiện chỗ skill/reference/codebook chưa đủ chặt khiến agent tự quyết định theo cảm tính;
- hai instance nhận cùng prompt, cùng skill, cùng tài liệu canonical, cùng hai input và cùng hash;
- hai instance chạy trong hai native thread quan sát được, không đọc output hoặc trao đổi với nhau trước khi hoàn tất;
- vùng ghi tách biệt: `dual_run/annotator_a/` và `dual_run/annotator_b/`; không instance nào được ghi file hợp nhất;
- output mong đợi của mỗi instance: nhãn vòng 1, nhãn cuối, review queue, run manifest và handoff riêng;
- phép hợp nhất chỉ do code so sánh xác định tạo ra; UET phân xử, còn `benchmark-specification-designer` chỉ sửa codebook sau quyết định của UET;
- mọi lần chạy nhiều hơn hai instance hoặc thay model/reasoning vẫn cần phê duyệt mới theo `AGENTS.md`.

Hai instance dùng cùng một loại specialist và cùng một họ mô hình, vì vậy kết quả chỉ đo **tính tái lập liên-instance của quy trình AI**, không phải độ tin cậy giữa hai người chấm độc lập.

#### Hợp đồng hai vòng bắt buộc

Pipeline phải sinh hai input có cùng tập `benchmark_candidate_id` và lưu hash:

1. `principle_annotation_pass1_input.csv` chỉ có `benchmark_candidate_id`, `sample_id`, `grade`, `lesson`, `position`, `bloom_level`, `student_prompt`, `conversation_history`. Specialist đề xuất nhãn từ nhu cầu sư phạm của tình huống, không được thấy `gold_response` hoặc `gold_answer`.
2. `principle_annotation_grounding_input.csv` bổ sung `source_question`, `gold_answer` và các trường học liệu/evidence đã được phép dùng. `source_question` phải được code ghép từ hai snapshot `normalized_dialogue_rows.csv` qua `sample_id`; specialist không tự truy ngược dữ liệu thô. View này không được chứa `gold_response`.

Nếu grounding làm thay đổi tập nguyên tắc đề xuất, candidate phải vào `principle_annotation_review_queue.csv`. `source_question`, `gold_answer`, `bloom_level`, tên bài và từ khóa chỉ là căn cứ bổ sung; không trường nào được ánh xạ máy móc sang nguyên tắc. `gold_response` chỉ được dùng ở giai đoạn xây và chấm rubric sau này, không được dùng để chọn nguyên tắc nhằm tránh tạo lợi thế vòng tròn cho response tham chiếu.

Sau khi specialist ghi quyết định vòng grounding, code phải so sánh trực tiếp tập nhãn trước–sau để suy ra `changed` hoặc `unchanged` và tự bổ sung hàng đợi bắt buộc. Agent chỉ quyết định trường hợp xung đột ngữ nghĩa; không dùng agent để tính một khác biệt có thể xác định bằng code.

Trước khi cắt lô cho specialist, pipeline phải tạo `candidate_principle_grounding_pool.csv` và manifest tương ứng cho toàn bộ pool. Join đóng khi lỗi nếu thiếu/trùng `sample_id`, câu hỏi nguồn rỗng hoặc các trường `grade`, `lesson`, `position`, `bloom_level`, `gold_answer` không khớp dữ liệu nguồn. Mỗi run tiếp theo phải khóa đường dẫn và SHA-256 của grounding pool, tài liệu nguồn gốc, skill, hợp đồng runtime và ba bảng bắt buộc đọc. Manifest dùng để chứng minh hai instance dùng cùng phiên bản; không yêu cầu mỗi dòng annotation phải viện dẫn lại các đường dẫn này.

Hai input `principle_annotation_reference_input.csv` và manifest phiên bản 2 của lần C0b đầu tiên được giữ nguyên như artifact chẩn đoán lịch sử. Không dùng chúng cho lần chạy phương pháp kế tiếp.

#### Artifact và code phải tạo trước khi chạy lô 40

- `src/edu_benchmark/benchmark_specification/principle_annotation.py`: tạo hai view input, kiểm tập ID/hash, đối chiếu hai vòng và build review queue;
- `src/edu_benchmark/benchmark_specification/principle_grounding.py`: ghép xác định `source_question` theo `sample_id`, loại `gold_response` khỏi grounding pool và đóng khi lỗi nếu provenance không nhất quán;
- `scripts/benchmark_specification/build_principle_grounding_pool.py`: CLI mỏng để tạo grounding pool và manifest;
- `scripts/benchmark_specification/build_principle_annotation_inputs.py`: CLI mỏng;
- `scripts/benchmark_specification/validate_principle_annotation_run.py`: validator đóng khi lỗi;
- `scripts/benchmark_specification/reconcile_principle_annotation_draft.py`: suy ra tác động grounding trên tập nhãn và hàng đợi bắt buộc bằng code trước khi đóng bundle;
- `scripts/benchmark_specification/compare_principle_annotation_runs.py`: so sánh hai run mà không cho hai instance thấy output của nhau;
- `tests/agents/test_pedagogical_principle_annotator.py`: kiểm discovery, adapter mỏng, model/reasoning pin, các đường dẫn tài liệu bắt buộc và ranh giới thẩm quyền;
- `tests/benchmark_specification/test_principle_annotation.py`: kiểm cô lập trường dữ liệu, schema tập nhãn, grounding manifest, vùng ghi tách biệt và phép so sánh xác định;
- một forward test nhỏ trên các ví dụ biên đã được UET xem, không tính vào 160 nhãn chính thức.

#### Cổng C0a — Cho phép mở pilot hai instance

Chỉ mở lô 40 khi:

- skill và adapter được phát hiện bằng validator của repository;
- skill/reference nêu đúng đường dẫn tới cả tài liệu sáu nguyên tắc và mô hình sáu năng lực;
- vòng 1 không thể đọc `gold_response`, `gold_answer` hoặc evidence ẩn;
- output không cho phép agent ghi `confirmed`;
- specialist không có quyền ghi vào codebook hoặc file nguyên tắc/năng lực;
- validator bác nhãn ngoài sáu nguyên tắc, cặp candidate–nguyên tắc trùng, đồng thời có tập nhãn và `coverage_gap_reason`, tập rỗng mà không có khoảng trống, trường hợp hơn ba nhãn không vào review, và tập ID/hash lệch;
- forward test cho thấy agent xử lý đúng ít nhất các biên `Questioning`–`Explanation`, `Feedback`–`Questioning`, `Challenge`–`Practice`, phân biệt nguyên tắc với năng lực và xử lý xung đột context–grounding;
- validator chứng minh hai instance không thể ghi cùng thư mục hoặc đọc output của nhau;
- đại diện UET cho phép spawn đúng hai instance trên cùng lô 40.

**Kết quả chạy phương pháp v3 ngày 27/07/2026.** Hạ tầng C0a, skill,
schema quan hệ, validator, lô 40 phân tầng 10 ứng viên mỗi lớp và ngưỡng v3
đã được cài đặt. Bundle forward test của specialist đạt toàn bộ kiểm tra cấu
trúc nhưng chỉ khớp 3/5 tập nhãn kỳ vọng. Hai ca chưa khớp là:

- `FT-C02`: kỳ vọng kế thừa là `Feedback + Questioning`, còn specialist v3
  chọn `Feedback + Explanation`;
- `FT-C04`: kỳ vọng kế thừa là `Questioning`, còn specialist v3 chọn
  `Modelling` và chủ động đưa ca này vào hàng đợi rà soát ranh giới.

Hai kỳ vọng trên được chuyển đổi từ bộ ví dụ của quy trình cũ có
`gold_response`, trong khi input v3 chủ động loại trường này. Vì cả hai dự
đoán mới đều có luận giải phù hợp với context/grounding, orchestrator không
tự thay kỳ vọng, không sửa codebook để khớp test và không mở C0b. Đại diện
UET phải quyết định sửa ngữ cảnh tổng hợp để ranh giới trở nên đơn nghĩa,
hoặc phê duyệt tập nhãn kỳ vọng mới; sau đó phải chạy lại C0a trong một
native thread mới.

#### Cổng C0b — Đánh giá tính tái lập liên-instance

Sau khi cả hai instance hoàn tất, script so sánh phải tạo:

- tỷ lệ trùng chính xác toàn bộ tập nguyên tắc của mỗi ứng viên;
- Jaccard trung bình trên tập nguyên tắc của mỗi ứng viên;
- precision, recall và F1 cho từng nguyên tắc trên phép so sánh A–B, chỉ dùng như chỉ số tái lập chứ không coi một agent là ground truth;
- tỷ lệ thống nhất về `coverage_gap_reason` và việc đổi tập nhãn sau vòng grounding;
- ma trận đồng xuất hiện, ma trận bất đồng thêm/bỏ theo từng nguyên tắc và danh sách mọi xung đột.

Đây là chỉ số chẩn đoán tính tái lập của hai lần chạy AI cùng cấu hình. Không gọi các chỉ số này là độ đồng thuận giữa hai người chấm độc lập. Trước khi chạy, UET phải khóa ngưỡng vận hành trong run manifest; chưa được chọn ngưỡng sau khi nhìn kết quả. Bất kể ngưỡng, mọi xung đột tập nhãn, khoảng trống hoặc tác động grounding khác nhau đều phải vào review queue, và không được hợp nhất output trước khi cả hai run đóng.

Các ngưỡng UET đã đăng ký cho schema cũ — nguyên tắc chính `1.00`, cặp chính–phụ `0.90`, Jaccard `0.90`, coverage gap `1.00`, tác động reference `0.90` — chỉ dùng để diễn giải lần C0b lịch sử. Chúng không được tự động chuyển sang schema tập nhãn v3. Trước khi chạy lại, UET phải đăng ký ngưỡng mới cho exact-set agreement, Jaccard, F1 từng nguyên tắc, coverage gap và tác động grounding.

Nếu không đạt ngưỡng đã đăng ký hoặc xuất hiện cụm xung đột có hệ thống, pilot dừng đóng: UET phân loại nguyên nhân, `benchmark-specification-designer` sửa skill/reference/codebook theo quyết định, rồi hai instance mới phải chạy lại trên cùng tập mẫu bằng version mới. Nhãn của run không đạt không được tính là nhãn chính thức.

Lần C0b đầu tiên không đạt và phát hiện ba vấn đề thiết kế: sáu nguyên tắc bị diễn giải quá giống các lớp loại trừ, cấu trúc chính–phụ/giới hạn hai không có đủ căn cứ cho dữ liệu HNMU, và lô 40 chỉ gồm lớp 6 do lấy offset đầu trên file đã sắp theo lớp. Bản sửa trước lần chạy kế tiếp phải:

1. dùng ranh giới theo **kết quả gần** và **chủ thể thực hiện hành động**: `Challenge` nâng yêu cầu nhận thức; `Explanation` làm rõ; `Modelling` cho thấy cách làm hoặc cách nghĩ; `Practice` yêu cầu học sinh thực hiện để tăng thành thạo/độc lập; `Feedback` đánh giá phần học sinh đã làm để dẫn hướng cải thiện; `Questioning` cần câu trả lời của học sinh để chẩn đoán, giữ mạch hoặc đào sâu tư duy;
2. dùng tập chức năng không thể bỏ, không thứ tự, không giới hạn cứng ở hai và tự động review khi có hơn ba nguyên tắc;
3. loại hoàn toàn `gold_response` khỏi gán nguyên tắc; vòng grounding chỉ dùng `source_question`, `gold_answer` và căn cứ học liệu được phép;
4. so sánh hai instance bằng exact-set agreement, Jaccard và F1 từng nguyên tắc;
5. tạo lô chạy lại phân tầng 10 ứng viên mỗi lớp 6–9;
6. giữ packet 29 dòng của lần đầu làm bằng chứng chẩn đoán, không yêu cầu UET phân xử toàn bộ trước khi duyệt bản sửa.

### 8.3.3. Quy trình với hai instance specialist AI + một đại diện UET

Nguồn lực mã hóa gồm:

- `PEDAGOGICAL-PRINCIPLE-ANNOTATOR-A` và `PEDAGOGICAL-PRINCIPLE-ANNOTATOR-B`: hai instance độc lập, cùng mã hóa toàn bộ lô pilot 40 theo đúng hai vòng;
- `UET-REVIEWER-01`: người phụ trách dự án, chỉ review và phân xử tạm thời sau khi có output A/B;
- HNMU: chưa mã hóa ở C, sẽ review gói tích hợp sau D.

Quy trình lô pilot 40:

1. Pipeline khóa hai input vòng context/vòng grounding, grounding manifest, tập ID và hash; không dùng một file đầy đủ rồi chỉ dặn agent “đừng nhìn” trường ẩn.
2. Orchestrator thông báo rõ hai delegation với cùng task/input/model/reasoning, hai vùng ghi riêng và merge plan, rồi spawn hai native thread đồng thời.
3. Mỗi instance mã hóa vòng 1 trong thư mục riêng chỉ từ context được phép thấy; không instance nào nhìn output của instance còn lại.
4. Mỗi instance đối chiếu vòng grounding, ghi tập đề xuất cuối và review queue trong thư mục riêng; mọi dòng giữ trạng thái `needs_uet_review`.
5. UET không gán mù trước run. `principle_calibration.csv` chỉ lưu quyết định miễn bước này và không tham gia tính metric hoặc làm ground truth.
6. Chỉ sau khi hai handoff đã đóng, script mới tạo bảng so sánh, ma trận nhầm lẫn và summary; không lấy output A làm đáp án để sửa B hoặc ngược lại.
7. UET review mọi bất đồng A–B, mọi `coverage_gap_reason`, mọi xung đột context–grounding, mọi trường hợp có hơn ba nguyên tắc, mọi đề xuất sửa nguyên tắc và ít nhất 8/40 trường hợp hai agent trùng tập nhãn được chọn xác định.
8. Nếu UET sửa quy tắc, `benchmark-specification-designer` cập nhật skill/reference/codebook theo quyết định; cả hai instance phải rà lại toàn bộ dòng bị ảnh hưởng trên version mới và giữ truy vết trước/sau.

Sau pilot trùng lặp toàn bộ 40 mẫu, các lô khám phá tiếp theo có thể chia cho nhiều instance để tăng tốc, nhưng phải giữ một tập overlap phân tầng được khóa trước nhằm theo dõi drift. Số instance, tỷ lệ overlap, model, reasoning, shard, vùng ghi và merge plan của mỗi đợt phải được duyệt/ghi trong run manifest. Với full assignment 2.028 ứng viên ở Workstream G, mặc định dùng ít nhất hai instance và chia shard theo `sample_id`; tỷ lệ overlap phân tầng sẽ được chọn từ kết quả pilot và phải được UET khóa trước khi chạy toàn bộ.

Có thể dừng ở mức **độ phủ tạm ổn định dưới quy trình một người–nhiều AI** khi hai lô liên tiếp không:

- tạo khoảng trống lặp lại đòi hỏi xem xét nguyên tắc mới;
- làm thay đổi định nghĩa hoặc ranh giới giữa sáu nguyên tắc;
- làm UET thay đổi quy tắc đa nhãn.

Kết luận này không thay thế xác nhận của HNMU.

### 8.3.4. Nội dung mã hóa cho mỗi ứng viên

Metadata cấp ứng viên nằm trong `candidate_principle_annotations.csv`:

| Trường | Nội dung |
|---|---|
| `benchmark_candidate_id` | Khóa candidate. |
| `sample_id` | Khóa hội thoại nguồn. |
| `student_state_summary` | Tóm tắt trạng thái học sinh có thể quan sát từ prompt và history. |
| `coverage_gap_reason` | Chỉ có giá trị khi tập nguyên tắc rỗng; nêu rõ khoảng trống. |
| `grounding_effect` | `unchanged`, `changed` hoặc `conflict`; `changed`/`unchanged` do code suy ra. |
| `grounding_change_reason` | Căn cứ mới hoặc xung đột xuất hiện ở vòng grounding. |
| `coder_id` | `PEDAGOGICAL-PRINCIPLE-ANNOTATOR-A`, `PEDAGOGICAL-PRINCIPLE-ANNOTATOR-B` hoặc `UET-REVIEWER-01`. |
| `review_status` | Trạng thái rà soát; AI không được ghi `confirmed`. |
| `adjudication_status` | Trạng thái phân xử tạm thời của UET. |

Tập nguyên tắc nằm trong bảng quan hệ `candidate_principle_labels.csv`, một dòng cho mỗi cặp candidate–nguyên tắc:

| Trường | Nội dung |
|---|---|
| `benchmark_candidate_id` | Khóa ngoại tới metadata cấp ứng viên. |
| `principle_id` | Một trong sáu nguyên tắc; không có thứ tự chính–phụ. |
| `selection_rationale` | Vì sao đây là một chức năng độc lập và không thể bỏ. |
| `context_evidence` | Bằng chứng từ `student_prompt`/`conversation_history`. |
| `grounding_evidence` | Bằng chứng bổ sung từ `source_question`, `gold_answer` hoặc fragment; có thể rỗng nếu context đã đủ. |
| `coder_id` | ID người/agent đề xuất. |
| `review_status` | Trạng thái rà soát; hơn ba nhãn bắt buộc `needs_uet_review`. |

### 8.4. Sản phẩm đầu ra

`outputs/benchmark_specification/task_discovery/`

| Tệp | Nội dung |
|---|---|
| `candidate_feature_census.csv` | Thống kê đặc điểm của 2.028 ứng viên. |
| `task_discovery_strata.csv` | Các tầng lấy mẫu khám phá. |
| `task_discovery_sample.csv` | 160 ứng viên được chọn. |
| `benchmark_tasks.csv` | Một nhiệm vụ benchmark hiện hành. |
| `pedagogical_principles.csv` | Sáu nguyên tắc, định nghĩa và truy vết KMP. |
| `task_discovery_codebook.md` | Quy tắc gán tập nguyên tắc không thứ tự và xử lý khoảng trống. |
| `principle_annotation_pass1_input.csv` | View chỉ chứa context mà mô hình benchmark được phép thấy. |
| `method_revision_v3/candidate_principle_grounding_pool.csv` | Pool 2.028 ứng viên đã có `source_question` ghép bằng code và `gold_answer`, không chứa `gold_response`. |
| `method_revision_v3/candidate_principle_grounding_pool_manifest.json` | Hash input/output, thống kê join và chính sách đóng khi lỗi của grounding pool. |
| `principle_annotation_grounding_input.csv` | View vòng grounding được cắt từ pool v3, có cùng tập ID với vòng 1. |
| `principle_annotation_grounding_manifest.json` | Đường dẫn/hash của grounding pool, tài liệu sáu nguyên tắc, codebook và mô hình sáu năng lực được ghi trong skill/reference. |
| `principle_annotation_reference_input.csv` và `principle_annotation_reference_manifest.json` | Artifact legacy của lần C0b đầu tiên; chỉ dùng để truy vết chẩn đoán, không dùng cho run mới. |
| `dual_run/annotator_a/` và `dual_run/annotator_b/` | Hai bundle tách biệt, mỗi bundle có metadata/tập nhãn vòng context, metadata/tập nhãn vòng grounding, review queue, run manifest và handoff. |
| `dual_run_comparison.csv` | Đối chiếu A–B theo từng ứng viên và trạng thái bất đồng. |
| `dual_run_principle_metrics.csv` | Precision, recall, F1 và bất đồng thêm/bỏ theo từng nguyên tắc giữa hai instance. |
| `dual_run_reproducibility_summary.json` | Chỉ số tính tái lập, ngưỡng đăng ký trước, kết quả gate và hash hai bundle. |
| `principle_calibration.csv` | Hồ sơ UET miễn bước gán mù; không chứa nhãn và không tham gia metric. |
| `principle_coverage_gaps.csv` | Bản lọc các trường hợp có tập nguyên tắc rỗng. |
| `principle_coverage_decisions.md` | Quyết định giữ/sửa/bổ sung nguyên tắc và thẩm quyền. |
| `legacy_spec_dispositions.csv` | Cách xử lý đặc tả thử nghiệm và tám task cũ. |

Nhánh tám nhiệm vụ cũ chỉ tồn tại tại `outputs/benchmark_specification/legacy/eight_task_candidate_branch/` và không phải đầu vào của quy trình hiện hành.

### Cổng C — Điều kiện chuyển sang Workstream D

- Cổng C0a và C0b của `pedagogical-principle-annotator` đã đạt trước mọi nhãn chính thức;
- hai instance pilot đã dùng cùng input và cùng phiên bản tài liệu canonical, có vùng ghi tách biệt và không truy cập chéo;
- báo cáo tính tái lập liên-instance và toàn bộ bất đồng đã được UET xem; không diễn giải chỉ số AI–AI thành độ tin cậy giữa người chấm;
- đủ 160 dòng mã hóa hoặc có biên bản dừng sớm được UET duyệt;
- mỗi candidate có tập nguyên tắc không rỗng hoặc `coverage_gap_reason`, không có cả hai;
- không có cặp candidate–nguyên tắc trùng và mọi candidate có hơn ba nguyên tắc đều nằm trong review queue;
- phạm vi UET review sau run được báo rõ; không có chỉ số UET–AI vì bước gán mù đã được miễn;
- đạt hai lô liên tiếp ổn định hoặc UET ghi rõ lý do cho phép chuyển tiếp có điều kiện;
- mọi khoảng trống lặp lại có quyết định tạm thời và thẩm quyền;
- đại diện UET cho phép dùng sáu nguyên tắc làm đầu vào xây rubric ở D;
- sáu nguyên tắc và sáu năng lực vẫn giữ trạng thái cần HNMU review trong gói tích hợp.

## 9. Workstream D — Xây dựng rubric hai tầng và cổng lỗi nghiêm trọng

### 9.1. Tầng 1 — Chiều năng lực chung

Tầng 1 được xây từ sáu năng lực Workstreams A–B. Mỗi chiều có tiêu chí nguyên tử, dấu hiệu quan sát, thang điểm và anchor tốt/trung bình/kém, quy tắc `not_applicable` nếu cần, giới hạn suy luận và truy vết nghiên cứu/HNMU.

Không bắt buộc cả sáu năng lực đều áp dụng cho mọi phản hồi. `applicability_rule` phải nêu rõ điều kiện quan sát; không được chấm thấp một năng lực chỉ vì candidate không tạo cơ hội biểu hiện nó.

### 9.2. Tầng 2 — Tiêu chí theo nguyên tắc sư phạm

Mỗi nguyên tắc có một tập nhỏ tiêu chí riêng để nhận biết phản hồi đã thực hiện nguyên tắc đó tốt đến đâu. Ví dụ:

- `Explanation`: làm rõ quan hệ cốt lõi, đúng mức hiểu của học sinh, không chỉ nêu kết luận;
- `Questioning`: câu hỏi có mục đích, vừa sức và tạo cơ hội cho học sinh suy nghĩ;
- `Feedback`: bám vào bài làm/ý kiến thực tế, chỉ ra điểm cần sửa và hướng tiến bộ;
- `Modelling`: minh họa quy trình suy nghĩ/cách làm có thể theo dõi, không biến thành chép đáp án.

Tiêu chí tầng 2 phải quan sát được từ response và evaluation context, không trùng tầng 1, không yêu cầu giống câu chữ `gold_response`, và chỉ dùng `gold_answer`/fragment đã truy vết làm căn cứ chuyên môn. Candidate áp dụng tiêu chí của **mọi nguyên tắc trong tập nhãn đã khóa**; không tạo tầng rubric thứ ba theo candidate.

### 9.3. Evaluation context theo candidate

`candidate_evaluation_context.csv` lưu `benchmark_candidate_id`, trạng thái học sinh, mục tiêu gia sư, `gold_answer`, `gold_response_reference`, learning/evidence IDs, các dữ kiện chuyên môn riêng và trạng thái review. File này cung cấp facts để áp dụng rubric; nó không chứa tiêu chí mới.

### 9.4. Cổng lỗi nghiêm trọng

Danh mục tối thiểu cần xem xét: sai kiến thức hoặc củng cố hiểu sai; bịa nguồn; hướng dẫn không an toàn/vi phạm đạo đức; làm thay làm mất quyền chủ động; bỏ qua thiếu nền tảng rõ ràng; tiết lộ đáp án trái mục tiêu sư phạm. Action chỉ là đề xuất `review`, `score_cap`, `fail` hoặc `exclude_response` cho tới khi HNMU/UET chốt.

### 9.5. Artifact

`outputs/benchmark_specification/rubric_v1_draft/`

- `rubric_dimensions.csv` — tầng năng lực chung;
- `principle_rubrics.csv` — tầng tiêu chí theo sáu nguyên tắc;
- `rubrics.csv` — bản phẳng phục vụ công cụ downstream, không tạo semantics mới;
- `rubric_anchors.md`;
- `serious_errors.csv`;
- `candidate_evaluation_context.csv`;
- `rubric_research_provenance.csv`;
- `rubric_open_questions.md`.

### Gate D

- mỗi tiêu chí tầng 1 liên kết tới năng lực hợp lệ;
- mỗi tiêu chí tầng 2 liên kết tới nguyên tắc và ít nhất một năng lực liên quan;
- không có tiêu chí riêng theo candidate;
- `gold_response` không được coi là cách trả lời duy nhất;
- tạo gói HNMU tích hợp gồm sáu năng lực, sáu nguyên tắc, rubric, lỗi nghiêm trọng và ví dụ phản hồi;
- HNMU/UET duyệt nội dung, anchor và chính sách lỗi ở mức tạm thời trước pilot response.

## 10. Workstream E — Tạo response đối chứng bằng nhiều LLM và biến đổi có kiểm soát

### 10.1. Mục tiêu

Kiểm tra nguyên tắc/rubric có tạo phân hóa chất lượng thật, thay vì chỉ “nghe hợp lý” trên giấy.

### 10.2. Chọn pilot candidate

Chọn sau khi hệ nguyên tắc/rubric tạm thời hoàn thành. Mẫu pilot phải phân tầng theo:

- từng nguyên tắc và các tổ hợp nguyên tắc phổ biến trong tập nhãn;
- lớp;
- có/không có history;
- dạng nội dung;
- mức nhận thức;
- độ dài và độ khó;
- family, không lấy quá nhiều candidate gần nhau từ một raw dialogue.

Kích thước pilot, số model và số lượt sinh được chốt trong `pilot_sampling_and_budget_decision.md` trước khi gọi model. Không dùng một con số tùy ý chỉ để lấp đủ quota.

### 10.3. Nguồn response

Mỗi candidate pilot có thể có:

- `gold_response` đã được rà soát như một response tham chiếu;
- response từ nhiều LLM khác family/kích thước hoặc mức instruction tuning;
- response biến đổi có kiểm soát từ một bản tốt để chèn đúng một lỗi;
- minimal pairs chỉ khác một năng lực/tiêu chí.

Ưu tiên sử dụng AI quota trên Kaggle cho generation batch nếu điều khoản sử dụng, model availability và quota được xác minh. Model roster không được ngầm đại diện cho ba mức chất lượng.

HNMU chấm mù response đã random hóa. Chỉ sau adjudication mới gán nhãn chất lượng quan sát được như tốt/trung bình/kém.

### 10.4. Reproducibility và an toàn quota

Trước mỗi run phải khóa:

- provider/model/version;
- prompt template;
- decoding parameters và seed nếu được hỗ trợ;
- candidate IDs;
- quota/cost ceiling;
- retry policy;
- raw output path;
- timestamp và hash input;
- policy về dữ liệu được phép gửi ra dịch vụ.

Không gọi Kaggle/model API chỉ vì Plan 03 được duyệt chung. Run manifest và quota ceiling cụ thể phải được người phụ trách dự án duyệt trước khi execution.

### 10.5. Artifact

`outputs/benchmark_specification/validity_pilot/`

- `pilot_sampling_and_budget_decision.md`
- `kaggle_generation_run_manifest.yaml`
- `model_response_pilot.csv`
- `controlled_response_pairs.csv`
- `blind_review_packet.csv`
- `human_response_ratings.csv`
- `response_adjudication.csv`

## 11. Workstream F — Kiểm định tính hợp lệ và khả năng phân biệt

### 11.1. Content/construct evidence

- ma trận bao phủ năng lực–nguyên tắc–rubric;
- tỷ lệ tiêu chí có research/HNMU provenance;
- content-validity judgment của HNMU;
- chồng lấn/khoảng trống và `principle_coverage_gap_rate`;
- mức khớp khi gán nguyên tắc và khi chấm rubric;
- kiểm tra rubric có đang đo văn phong thay vì năng lực gia sư hay không.

### 11.2. Phân biệt response tốt–trung bình–kém

Trên nhãn mù do HNMU xác nhận:

- phân bố điểm theo ba nhóm;
- monotonic ordering;
- pairwise accuracy và effect size giữa các nhóm;
- item difficulty và item discrimination;
- floor/ceiling effect;
- tiêu chí không có variance hoặc không phân biệt;
- stability theo lớp, nguyên tắc, history và dạng nội dung.

Không dùng IRT nếu ma trận model × candidate chưa đủ dày. Giai đoạn đầu dùng thống kê cổ điển và bootstrap; quyết định dùng IRT phải có plan riêng và kiểm tra giả định.

### 11.3. Kiểm định bộ chấm tự động

Nếu dùng LLM-as-a-judge:

- so với majority/adjudicated human rating;
- kiểm tra position swap trong pairwise judging;
- kiểm tra self-preference nếu judge cùng family với response model;
- báo theo từng nguyên tắc/rubric, không chỉ một accuracy chung;
- giữ rationale/evidence nhưng không coi rationale dài là đúng;
- không dùng judge để thay HNMU trong content validation.

### 11.4. Pre-registration threshold

Tạo `validation_thresholds.yaml` **trước khi xem kết quả pilot cuối**. Mỗi threshold cần:

- metric;
- level áp dụng;
- minimum sample requirement;
- pass/revise/retire action;
- rationale;
- decision owner;
- approval timestamp.

Plan không tự invent threshold số trước khi có literature extension, pilot design và HNMU/UET consultation.

### 11.5. Artifact

`outputs/benchmark_specification/validity_pilot/`

- `validation_thresholds.yaml`
- `content_validity_results.csv`
- `inter_rater_results.csv`
- `principle_assignment_validity.csv`
- `rubric_discrimination_results.csv`
- `judge_human_alignment.csv`
- `position_bias_results.csv`
- `validity_decisions.md`

### Gate F

- mọi metric có denominator và uncertainty;
- tiêu chí không đạt threshold được revise/retire, không giữ vì “có căn cứ lý thuyết”;
- kết luận phân biệt chỉ giới hạn trong pilot đã quan sát;
- HNMU/UET duyệt quyết định freeze/revise.

## 12. Workstream G — Freeze specification v1 và gán toàn bộ 2.028 candidate

Chỉ chạy sau khi Gate A–F đạt.

### 12.1. Specification v1

`outputs/benchmark_specification/spec_v1/`

- `benchmark_tasks.csv`
- `pedagogical_principles.csv`
- `tutor_capabilities.csv`
- `rubric_dimensions.csv`
- `principle_rubrics.csv`
- `rubrics.csv`
- `serious_errors.csv`
- `provenance_matrix.csv`
- `research_id_aliases.csv`
- `legacy_spec_dispositions.csv`
- `benchmark_open_questions.md`
- `spec_validation_report.json`

Status chỉ dùng:

- `draft`
- `needs_uet_review`
- `needs_hnmu_review`
- `confirmed`
- `retired`

Chỉ item có quyết định đúng authority mới được `confirmed`.

### 12.2. Assignment toàn pool

`outputs/benchmark_specification/candidate_assignment/`

- `benchmark_candidate_principle_rubric_suggestions.csv`
- `principle_rubric_review_queue.csv`
- `assignment_dispositions.csv`
- `candidate_coverage_long.csv`
- `coverage_summary.csv`
- `coverage_gaps.csv`

Mỗi converted candidate phải có một trong:

- assignment hợp lệ theo spec v1;
- `need_human_review`;
- `excluded_no_supported_principle`;
- `excluded_insufficient_context`.

Không xóa candidate âm thầm. Confidence của agent chỉ dùng routing, không dùng như ground truth.

Coverage là coverage quan sát được, không phải tuyên bố bao phủ toàn chương trình. Báo cả candidate-level và raw-dialogue-family-level.

## 13. Code cụ thể khi plan được duyệt

### 13.1. Package

Tạo dưới `src/edu_benchmark/benchmark_specification/`:

- `schema.py`: schema, enum và foreign-key validation;
- `research_ids.py`: source ID/alias validation;
- `constructs.py`: capability model schema và overlap checks;
- `principle_coverage.py`: census, lấy mẫu phân tầng, gán nguyên tắc và kiểm tra độ phủ;
- `principle_annotation.py`: tạo input hai vòng, kiểm field isolation/hash và build hàng đợi xung đột;
- `principle_grounding.py`: vật hóa `source_question` từ snapshot hội thoại nguồn qua `sample_id`, kiểm join và xuất pool không có `gold_response`;
- `rubrics.py`: two-tier rubric và flattened export;
- `serious_errors.py`: serious-error catalog validation;
- `provenance.py`: research/learning/HNMU provenance;
- `pilot_sampling.py`: pilot candidate selection;
- `response_generation.py`: provider-neutral generation contract;
- `blind_review.py`: randomization/de-identification packet;
- `validity.py`: agreement, discrimination, bias và bootstrap;
- `assignment.py`: full-pool suggestion/disposition contract;
- `coverage.py`: candidate/family coverage;
- `pipeline.py`: fail-closed orchestration và run manifests.

### 13.2. CLI

Tạo:

- `scripts/benchmark_specification/build_capability_model.py`
- `scripts/benchmark_specification/build_task_discovery_sample.py`
- `scripts/benchmark_specification/build_principle_annotation_inputs.py`
- `scripts/benchmark_specification/validate_principle_annotation_run.py`
- `scripts/benchmark_specification/build_rubric_specification.py`
- `scripts/benchmark_specification/build_response_pilot.py`
- `scripts/benchmark_specification/analyze_specification_validity.py`
- `scripts/benchmark_specification/freeze_spec_v1.py`
- `scripts/benchmark_specification/assign_candidate_principles.py`
- `scripts/benchmark_specification/build_candidate_coverage.py`

Kaggle notebook/script adapter, nếu cần, chỉ làm I/O mỏng và đọc run manifest; không chứa logic specification riêng.

### 13.3. Tests

Tạo `tests/benchmark_specification/`:

- `test_schema.py`
- `test_constructs.py`
- `test_principle_coverage.py`
- `test_principle_annotation.py`
- `test_rubrics.py`
- `test_serious_errors.py`
- `test_provenance.py`
- `test_pilot_sampling.py`
- `test_blind_review.py`
- `test_validity.py`
- `test_assignment.py`
- `test_coverage.py`
- `test_pipeline.py`

Test tối thiểu:

1. ID unique và foreign keys hợp lệ;
2. unknown research/learning IDs fail closed;
3. nguyên tắc không được suy máy móc từ mức nhận thức;
4. stratified sample deterministic với cùng seed;
5. family rule không bị vi phạm;
6. rubric chỉ có hai tầng và flattened export không đổi semantics;
7. evaluation context không bị nhập vào rubric;
8. blind packet không lộ model identity;
9. position-swap pair được tạo đúng;
10. metric dùng đúng denominator và báo nhóm thiếu mẫu;
11. threshold file tồn tại trước final analysis;
12. unsupported candidate có disposition;
13. coverage total khớp population;
14. input vòng context không chứa `gold_answer`, `gold_response` hoặc evidence ẩn; input grounding không chứa `gold_response`; hai vòng có cùng tập ID/hash;
15. thay đổi tập nhãn sau vòng grounding luôn đi vào review queue;
16. output bundle chỉ publish khi tất cả gate máy kiểm được đều pass.

## 14. Các vòng tham vấn HNMU/UET

| Vòng | Nội dung | Người quyết định | Output |
|---|---|---|---|
| UET-C | Mã hóa nguyên tắc và xử lý khoảng trống độ phủ | Đại diện UET phê duyệt tạm thời | `principle_calibration.csv`, `principle_coverage_decisions.md` |
| HNMU-D | Gói tích hợp sáu năng lực, sáu nguyên tắc, rubric, lỗi nghiêm trọng và ví dụ | HNMU về chuyên môn–sư phạm; UET về vận hành | `integrated_spec_review_decisions.csv` |
| HNMU/UET-EF | Chấm mù response pilot, phân xử và freeze/revise | HNMU/UET theo thẩm quyền | `validity_review_decisions.csv` |

Không gửi lại nhánh tám nhiệm vụ legacy cho UET/HNMU review trừ khi dữ liệu mới tạo một khoảng trống có bằng chứng đủ mạnh để mở lại quyết định thiết kế. Packet giáo viên tích hợp sẽ được thiết kế sau khi rubric bản nháp có ví dụ cụ thể; tác nhân không viết thay quyết định chuyên môn.

## 15. Specialist use khi plan được duyệt

### 15.1. Research-methodologist

- specialist: `research-methodologist`;
- model: `gpt-5.4-mini`;
- reasoning: `medium`;
- task: literature extension ở Workstream A;
- input: bốn-paper review, measurement questions, các nguồn gốc đã xác minh;
- allowed writes: `literature_notes/plan03_measurement_foundations/`;
- expected output: protocol, search log, evidence/claim matrices và synthesis tiếng Việt.

### 15.2. Benchmark-specification-designer

- specialist: `benchmark-specification-designer`;
- model: `gpt-5.4-mini`;
- reasoning: `high`;
- task: tổng hợp đặc tả năng lực–nguyên tắc–rubric–lỗi nghiêm trọng và sở hữu thay đổi codebook;
- input: Workstream A, học liệu/phương pháp HNMU và nhãn nguyên tắc Workstream C;
- allowed writes: `outputs/benchmark_specification/specialist_draft/` và codebook khi có quyết định UET/HNMU;
- expected output: draft specification, provenance và open questions tiếng Việt.

### 15.3. Pedagogical-principle-annotator

- specialist: `pedagogical-principle-annotator`;
- model: `gpt-5.4-mini`;
- reasoning: `medium`;
- task: áp dụng codebook sáu nguyên tắc lên candidate theo workflow hai vòng;
- input vòng 1: context trước target, không có `gold_answer`, `gold_response` hoặc evidence ẩn;
- input vòng 2: grounding view có `source_question`, `gold_answer` và evidence được phép, cùng tập ID/hash và không có `gold_response`;
- allowed writes khi chạy: chỉ các file annotation, review queue và handoff trong run được giao; không ghi codebook/spec;
- expected output: hai bundle tập nhãn không thứ tự tách biệt, bảng so sánh xác định và review queue bằng tiếng Việt ở phần luận giải;
- authority: chỉ đề xuất; không xác nhận nhãn, không sửa hệ nguyên tắc và không thay UET/HNMU.

Pilot đầu tiên được duyệt fan-out hai instance `A` và `B` trên cùng lô 40, chạy đồng thời với vùng ghi riêng và phép hợp nhất xác định như mục 8.3.2–8.3.3. Đây là ngoại lệ có chủ đích để kiểm tra tính tái lập và khả năng scale; không phải giấy phép fan-out không giới hạn. Các specialist khác vẫn mặc định một instance. Mọi delegation phải được announce, ghi coordination event và handoff.

## 16. Paper synchronization

Plan 03 không trực tiếp sửa manuscript. Sau mỗi gate, nó tạo:

`reports/plan03-paper-update-packet.md`

Packet ghi:

- claim mới có thể viết;
- artifact/source hỗ trợ;
- số liệu đã freeze;
- số liệu provisional;
- hình/bảng nên cập nhật;
- giới hạn và open questions.

Plan viết paper riêng sẽ đọc packet này. Nhờ vậy manuscript được cập nhật theo tiến độ mà không làm lẫn ownership giữa pipeline và LaTeX.

## 17. Allowed writes

Khi được duyệt, Plan 03 chỉ được ghi vào:

- `agents/pedagogical-principle-annotator/`
- `.codex/agents/pedagogical-principle-annotator.toml`
- `.claude/agents/pedagogical-principle-annotator.md`
- `.agents/skills/pedagogical-principle-annotator`
- `AGENTS.md` khi đăng ký specialist mới
- `src/edu_benchmark/benchmark_specification/`
- `scripts/benchmark_specification/`
- `tests/benchmark_specification/`
- `experiments/20260722_000940/literature_notes/plan03_measurement_foundations/`
- `experiments/20260722_000940/outputs/benchmark_specification/`
- `experiments/20260722_000940/reports/plan03-*`
- `experiments/20260722_000940/handoffs/plan03-*`
- `experiments/20260722_000940/coordination/coordination_log.jsonl` theo kiểu append-only;
- `README.md` và `ARCHITECTURE.md` khi component hoặc trạng thái thực sự thay đổi.

Không sửa output Plan 01/02, specification kế thừa, evidence matrix cũ hoặc shared learning-resource registry.

## 18. Trình tự thực hiện

1. Hash/snapshot input và tạo run manifest.
2. Workstream A: bổ sung căn cứ đo lường.
3. Workstream B: xây capability model và consultation vòng 1.
4. Workstream C0a: tạo, kiểm định và forward-test `pedagogical-principle-annotator`.
5. Workstream C0b: spawn đồng thời hai instance trên cùng lô 40, đo tính tái lập, phân tích xung đột và UET quyết định pass/fail.
6. Workstream C1: sau khi C0b đạt, tiếp tục mã hóa sáu nguyên tắc, hiệu chỉnh UET và kiểm tra độ phủ với overlap audit khi chia shard.
7. Workstream D: rubric hai tầng, lỗi nghiêm trọng và gói review HNMU tích hợp.
8. Đăng ký trước sampling/budget/threshold của validity pilot.
9. Workstream E: sinh response nhiều LLM và controlled pairs.
10. Workstream F: blind human review, judge calibration và validity analysis.
11. HNMU/UET phân xử pilot; sửa hoặc khóa đặc tả.
12. Workstream G: freeze spec v1, gán toàn pool bằng ít nhất hai instance có overlap audit và build coverage.
13. Chạy test/validator, viết report, paper update packet và handoff.

Mỗi bước semantic có thể lặp lại. Không được chạy generation hoặc full assignment khi gate trước chưa đạt.

## 19. Cổng hoàn thành

Plan 03 chỉ `COMPLETED` khi:

1. nền tảng đo lường có truy vết;
2. mô hình sáu năng lực có định nghĩa, dấu hiệu quan sát, ranh giới chồng lấn và quyết định HNMU/UET đúng thẩm quyền;
3. `pedagogical-principle-annotator` có skill canonical, adapter mỏng, cô lập trường dữ liệu hai vòng, đường dẫn trực tiếp tới tài liệu sáu nguyên tắc/sáu năng lực, validator/test và forward test đạt Cổng C0a;
4. pilot hai instance độc lập trên cùng lô 40 đạt Cổng C0b, có grounding manifest không chứa `gold_response`, báo cáo tính tái lập theo tập nhãn và phân xử UET;
5. kiến trúc một nhiệm vụ và sáu nguyên tắc có codebook, nhãn đa nhãn, hồ sơ hiệu chỉnh UET và báo cáo khoảng trống độ phủ;
6. nhánh tám nhiệm vụ cũ được giữ riêng dưới `legacy` và không được quy trình hiện hành đọc;
7. rubric đúng hai tầng năng lực–nguyên tắc; evaluation context tách riêng;
8. chính sách lỗi nghiêm trọng có quyết định thẩm quyền;
9. pilot nhiều LLM/response biến đổi có kiểm soát được chấm mù;
10. validation báo bằng chứng nội dung, mức nhất quán, khả năng phân biệt và thiên lệch bộ chấm;
11. threshold được đăng ký trước phân tích cuối;
12. item không đạt được sửa hoặc loại có truy vết;
13. spec v1 chỉ đánh dấu `confirmed` theo đúng quyết định HNMU/UET;
14. mọi candidate có assignment nguyên tắc/rubric hoặc disposition;
15. coverage báo cả candidate và family;
16. tests/validator pass bằng `benchmark_env`;
17. report, paper update packet, coordination event và handoff hoàn chỉnh.

Nếu chưa đủ HNMU review hoặc validity pilot, Plan giữ trạng thái đang thực hiện; không gọi bản nháp tạm thời là specification đã kiểm định.
## 20. Ngoài phạm vi

- audit evidence/chất lượng nội dung của toàn bộ candidate — thuộc Plan 04;
- HNMU review và adjudication toàn bộ benchmark sample — thuộc Plan 05;
- đo learning gain bằng học sinh thật;
- đánh giá một hệ thống gia sư thích ứng qua nhiều phiên;
- release benchmark công khai;
- commit hoặc submit paper.
