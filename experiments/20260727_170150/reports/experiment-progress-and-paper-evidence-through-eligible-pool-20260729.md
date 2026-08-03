# Báo cáo tiến độ experiment `20260727_170150` và bằng chứng phục vụ paper

Ngày lập báo cáo: 29/07/2026  
Phạm vi: từ khi mở experiment `20260727_170150` đến khi xuất pool
1.400 candidate `eligible_without_plan03_review`  
Mục đích chính: làm tài liệu đầu vào cho việc viết Method, Dataset,
Experimental Setup, Results và Limitations của paper KSE  
Nguồn kế thừa: experiment `20260722_000940`

> Báo cáo này là một snapshot có truy vết tại thời điểm lập. Các
> workstream Plan 05 và manuscript đang được tiếp tục ở những phiên làm
> việc khác; trạng thái trong báo cáo không thay thế manifest hoặc handoff
> mới hơn nếu chúng được tạo sau ngày 29/07/2026.

## 1. Tóm tắt điều hành

Experiment này được mở để thay phương pháp gán trực tiếp một tập nguyên
tắc sư phạm bằng một phương pháp có nhiều thông tin hơn: model chấm độc
lập mức độ cần thiết của cả sáu nguyên tắc trên thang 1–5, sau đó code
dẫn xuất tập nguyên tắc bắt buộc bằng ngưỡng
`requirement_score >= 4`.

Đến thời điểm lập báo cáo, các kết quả chính đã đạt được là:

1. Kế thừa có kiểm soát 41 artifact từ experiment trước, gồm 2.028
   benchmark candidate được chuyển đổi từ 665 hội thoại thô, grounding
   pool, mô hình sáu năng lực, sáu nguyên tắc sư phạm và căn cứ nghiên
   cứu.
2. Khóa đặc tả requirement-scoring V4, schema V2, system prompt tiếng
   Việt và bộ calibration 36 ca có chủ đích.
3. Xây runner Vertex AI dùng Application Default Credentials, hỗ trợ đa
   luồng, ghi kết quả tăng dần, resume, retry sau lượt quét, progress bar,
   validation và lưu đúng user prompt đã gửi model.
4. Chạy một full run bằng `gemini-3.5-flash` trên đủ 2.028 candidate;
   sau khi chạy bù hai candidate lỗi, bundle có đúng 2.028 record,
   12.168 score, không còn failure hiện hành.
5. Phân tích full run hoàn toàn bằng code: 1.400 candidate không có cờ
   Plan 03, 628 candidate cần UET review và 0 candidate bị chặn.
6. Xây thư viện tiêu chí hai tầng gồm một nhiệm vụ sinh phản hồi gia sư,
   bốn tiêu chí chung, 18 tiêu chí riêng theo sáu nguyên tắc, sáu lỗi
   nghiêm trọng và 29 quan hệ truy vết.
7. Xây cấu hình đánh giá bước đầu, chạy smoke thành công cho Gemini 3.5
   Flash và Llama 4 Maverick trên cùng 10 candidate, chạy đủ 20 phán
   quyết judge bằng Gemini 3.5 Flash sau retry, và chuẩn bị manifest pilot
   80 candidate nhưng chưa chạy pilot.
8. Tạo source LaTeX theo mẫu IEEE, viết và chỉnh sửa Introduction cùng
   Related Work, rà lại claim tính mới và biên dịch được PDF ba trang.
9. Đóng gói 1.400 candidate ưu tiên thành một CSV tự chứa để dùng trực
   tiếp ở các plan sau.

Kết quả trên đủ để viết bản nháp có bằng chứng cho các phần mô tả dữ liệu,
phương pháp chấm nguyên tắc, kiến trúc tiêu chí và kết quả phân tích dữ
liệu. Tuy nhiên, chưa đủ để tuyên bố benchmark đã được kiểm định đầy đủ:
requirement score đến từ một full run duy nhất, 628 candidate chưa được
phân xử, rubric/instruction chưa được HNMU xác nhận, và pilot phân biệt
mô hình chưa hoàn tất.

## 2. Câu hỏi nghiên cứu và logic thiết kế của experiment

Experiment tập trung giải quyết ba câu hỏi phương pháp:

1. Làm thế nào xác định các yêu cầu sư phạm phù hợp cho phản hồi tiếp theo
   mà không chọn nguyên tắc dựa trên chính `gold_response`?
2. Làm thế nào chuyển sáu nguyên tắc sư phạm thành tiêu chí chấm có thể
   vận hành trên từng candidate, đồng thời dùng sáu năng lực gia sư làm
   nền bảo đảm độ phủ?
3. Làm thế nào xây pipeline chạy model có khả năng truy vết, khôi phục và
   kiểm toàn vẹn, trong khi các phép lọc, threshold, join và thống kê xác
   định đều do code thực hiện?

Kiến trúc đích được khóa như sau:

```text
Context hội thoại + câu hỏi nguồn + gold_answer
                    ↓
  Chấm cả 6 nguyên tắc trên thang 1–5
                    ↓
       Code lấy đúng tập có score >= 4
                    ↓
     Đưa tập bắt buộc vào instruction tutor
                    ↓
          Model sinh phản hồi gia sư
                    ↓
4 tiêu chí chung + 3 tiêu chí cho mỗi nguyên tắc bắt buộc
                    ↓
   Response mô hình ↔ gold_response theo Win/Tie/Lose
```

`gold_response` không được cung cấp cho model chấm nguyên tắc và không
được dùng để chọn tiêu chí. Nó chỉ xuất hiện sau khi tập nguyên tắc,
instruction và rubric đã được khóa, với vai trò response tham chiếu có
thể thắng, hòa hoặc thua response của model.

## 3. Trạng thái đầu vào được kế thừa

### 3.1. Dữ liệu và conversion

Snapshot kế thừa giữ:

- 1.050 hội thoại thô ban đầu của HNMU;
- 665 hội thoại đạt điều kiện chuyển đổi theo audit của phase trước;
- 2.028 candidate, mỗi candidate tương ứng một điểm cắt ngay trước một
  lượt phản hồi của gia sư;
- 665 family theo `sample_id`;
- `student_prompt`, `conversation_history`, `gold_response`,
  `gold_answer` và metadata lớp/bài học;
- bảng grounding có thêm `source_question`;
- conversion trace để quay về file và dòng nguồn.

Quy tắc conversion đã được kế thừa là: một lượt gia sư trong hội thoại
được tạo thành một candidate; các lượt trước nó trở thành lịch sử hội
thoại; lượt học sinh cuối bị loại khỏi candidate nếu hội thoại thô kết
thúc bằng học sinh. Vì vậy, một hội thoại thô có thể sinh nhiều candidate
với cùng `student_prompt` nhưng lịch sử khác nhau.

Con số 665 là pool đủ điều kiện vận hành theo audit hiện có, không nên
diễn đạt thành 665 hội thoại đã được chuyên gia HNMU xác nhận cuối cùng.

### 3.2. Căn cứ sư phạm và đo lường

Experiment kế thừa hai cấu trúc khác nhau nhưng bổ trợ nhau:

- sáu nguyên tắc `Challenge`, `Explanation`, `Modelling`, `Practice`,
  `Feedback`, `Questioning`, bắt nguồn từ Allison–Tharby và được
  KMP-Bench vận hành trong benchmark gia sư;
- sáu năng lực gia sư `CAP-ACC`, `CAP-STATE`, `CAP-STRAT`,
  `CAP-SCAFF`, `CAP-DIAG`, `CAP-CARE`, được tổng hợp từ literature,
  phương pháp HNMU và vòng làm rõ ranh giới ở experiment trước.

Nguyên tắc mô tả chức năng sư phạm cần xuất hiện trong phản hồi. Năng lực
mô tả thuộc tính chất lượng rộng hơn của một gia sư. Hai cấu trúc không
được đồng nhất:

- nguyên tắc được dùng để kích hoạt instruction và rubric riêng;
- năng lực được dùng để kiểm độ phủ của rubric chung và rubric riêng.

Các tổng hợp research được kế thừa gồm KMP-Bench, MathTutorBench,
TutorBench, VietLegal và nền tảng đo lường như evidence-centered design,
validity, content coverage và item analysis.

### 3.3. Kiểm soát snapshot

Experiment mới snapshot 41 file, tổng dung lượng khoảng 4,6 MB. SHA-256
của từng file nằm trong:

`experiments/20260727_170150/inherited_resources/snapshot_manifest.csv`

Artifact active được tách khỏi các run A/B và forward test cũ. Các nhãn
của phương pháp cũ chỉ được giữ làm bằng chứng chẩn đoán, không được
chuyển thành ground truth.

## 4. Quyết định phương pháp quan trọng

### 4.1. Từ chọn tập nhãn sang chấm mức độ cần thiết

Phương pháp cũ yêu cầu agent chọn trực tiếp một tập nguyên tắc. Cách này
gặp ba vấn đề:

- các nguyên tắc có quan hệ qua lại, nên ép chọn cứng dễ làm mất thông
  tin;
- nhiều chiến lược có thể đều hữu ích nhưng không đồng nghĩa đều bắt
  buộc;
- độ bất đồng giữa annotator cao khi ranh giới chỉ dựa trên quyết định
  chọn/không chọn.

Phương pháp mới chấm từng nguyên tắc độc lập:

| Score | Ý nghĩa vận hành |
| ---: | --- |
| 1 | Không phù hợp hoặc có nguy cơ làm lệch nhu cầu hiện tại |
| 2 | Liên quan yếu hoặc chỉ xuất hiện ở bề mặt |
| 3 | Chiến lược thay thế hợp lệ nhưng không bắt buộc |
| 4 | Rõ ràng nên có trong một phản hồi tốt |
| 5 | Chức năng cốt lõi; bỏ đi thì phản hồi không còn đáp ứng nhu cầu chính |

Tập bắt buộc được code dẫn xuất bằng điều kiện
`requirement_score >= 4`. Điểm 3 được giữ làm dữ liệu chẩn đoán, nhưng
không được dùng như một instruction thay thế trong Plan 05.

### 4.2. Một lượt grounding duy nhất

Thiết kế hai vòng context/grounding được bỏ để giảm độ phức tạp và chi
phí. Model nhận một JSON có đúng tám trường ngữ nghĩa:

1. `grade`;
2. `lesson`;
3. `position`;
4. `bloom_level`;
5. `student_prompt`;
6. `conversation_history`;
7. `source_question`;
8. `gold_answer`.

`benchmark_candidate_id` và `sample_id` không được gửi model vì không có
giá trị ngữ nghĩa. Code giữ hai ID để join output về candidate.

### 4.3. Loại `gold_response` khỏi bước chọn nguyên tắc

Đây là quyết định chống selection bias quan trọng. Nếu đọc
`gold_response` rồi chọn các nguyên tắc mà response đó thể hiện tốt, sau
đó lại dùng rubric của các nguyên tắc ấy để so model với
`gold_response`, reference sẽ được hưởng lợi thế cấu trúc.

Do đó:

- `gold_answer` được dùng làm neo nội dung chuyên môn;
- `source_question` và context được dùng để tái dựng nhu cầu;
- `gold_response` bị loại hoàn toàn khỏi requirement-scoring;
- evaluator ở giai đoạn sau được phép kết luận model response tốt hơn
  `gold_response`.

### 4.4. Phân vai model và code

Model chỉ làm phần cần phán đoán ngữ nghĩa:

- chấm sáu score;
- viết `rationale`;
- chỉ ra `evidence`.

Code làm toàn bộ phần xác định:

- chuẩn hóa và validate input/output;
- dẫn xuất tập `>= 4` và tập điểm 3;
- so sánh A/B;
- tính metric;
- lọc theo threshold;
- phát hiện lỗi schema và một số mâu thuẫn rõ bằng semantic lint;
- join dữ liệu;
- tạo review queue;
- thống kê và xuất pool.

Code không tự sửa score dựa trên regex hoặc lint.

## 5. Plan 01 — Đặc tả requirement-scoring

### 5.1. Các phiên bản đặc tả và prompt

Plan 01 phát triển qua bốn phiên bản:

- V1: khóa nhiệm vụ chấm đủ sáu nguyên tắc, schema và prompt ban đầu;
- V2: bỏ hai ID khỏi user prompt, giải thích rõ tám trường ngữ nghĩa và
  lưu đúng chuỗi user prompt đã gửi model vào từng run record;
- V3: bổ sung năm phép phân biệt chống gán tràn;
- V4: khóa cổng lập luận cho điểm 4–5 và xây calibration cân bằng.

V4 yêu cầu mọi score 4–5 phải trả lời được hai câu:

- `Nhu cầu độc lập:` nhu cầu nào khiến nguyên tắc là bắt buộc?
- `Nếu bỏ nguyên tắc này:` vì sao chiến lược phù hợp khác vẫn chưa đủ?

Lập luận chỉ nói “có thể hữu ích”, “nên cân nhắc” hoặc “chiến lược thay
thế” bị giới hạn tối đa ở điểm 3.

V4 còn có cổng riêng:

- Feedback 4–5 phải có đầu ra/cách nghĩ cụ thể của học sinh, nhận xét
  đúng–sai–thiếu và hướng cải thiện;
- Questioning 4–5 phải chứng minh câu trả lời của học sinh là thông tin
  cần thiết hoặc việc tự trả lời là mục tiêu thiết yếu.

### 5.2. Calibration 36 ca

Bộ calibration gồm:

- sáu nguyên tắc;
- ba positive case cho mỗi nguyên tắc, expected range 4–5;
- ba near-miss case cho mỗi nguyên tắc, expected range 1–3;
- tổng cộng 36 ca.

Các ca được viết để cô lập ranh giới định nghĩa, không đại diện cho phân
bố 2.028 candidate. Expected range là giả thuyết vận hành được UET dùng để
review, chưa phải nhãn HNMU.

### 5.3. Artifact chính

- `outputs/principle_requirement_scoring/specification_v4.md`;
- `outputs/principle_requirement_scoring/scoring_schema_v2.json`;
- `outputs/principle_requirement_scoring/calibration_cases_v1.csv`;
- `outputs/principle_requirement_scoring/specification_manifest_v4.json`;
- `shared/prompts/benchmark_candidate_task_assigning/system_prompt_v4.md`.

Trạng thái: đặc tả đã được khóa để chạy; nội dung sư phạm vẫn cần được xem
trong gói tích hợp cùng rubric và ví dụ.

## 6. Plan 02 — Pipeline Vertex AI, pilot, calibration và full run

### 6.1. Hợp đồng runtime

Code active nằm dưới `src/vertex_ai_call/` và có các đặc tính:

- xác thực bằng Application Default Credentials;
- project `edu-benchmark`;
- không đọc API key hoặc `.env`;
- đa luồng bằng thread pool;
- worker không ghi trực tiếp file;
- thread điều phối append từng record hợp lệ vào JSONL rồi
  `flush`/`fsync`;
- resume theo request hash;
- retry candidate lỗi chỉ sau khi lượt quét tổng thể hoàn thành;
- có `max_retries` và trần tổng request;
- có progress bar;
- lưu `user_prompt`, model/config, raw output, normalized output, usage,
  request hash và tập dẫn xuất trong từng record;
- validation đóng lỗi nếu thiếu candidate, sai schema, trùng ID, sai user
  prompt hoặc sai tập nguyên tắc dẫn xuất.

### 6.2. Pilot Gemini 2.5 Flash

Các pilot V1–V3 cùng dùng 40 candidate và hai lần chạy A/B. Cấu hình
Gemini 2.5 Flash ưu tiên ổn định: `temperature=0`, `top_p=1`,
`thinking_budget=0`, `seed=20260727`.

| Phiên bản | Exact score agreement | Exact required-set agreement | Jaccard | Review queue |
| --- | ---: | ---: | ---: | ---: |
| V1 | 1,000 | 1,000 | 1,000 | 5 |
| V2 | 1,000 | 1,000 | 1,000 | 6 |
| V3 | 1,000 | 1,000 | 1,000 | 4 |

Các con số này chứng minh tính lặp lại của cùng model/config trên tập
pilot, không chứng minh accuracy hoặc đúng đắn sư phạm. Review định tính
vẫn phát hiện nguy cơ gán cao Feedback/Questioning khi rationale chỉ nói
chiến lược “có thể” hữu ích; đây là lý do dẫn đến V4.

### 6.3. Calibration V4 bằng Gemini 2.5 và Gemini 3.5 Flash

Kết quả calibration:

| Model | Ca nằm trong expected range ở cả A/B | Semantic lint | Dòng review |
| --- | ---: | ---: | ---: |
| Gemini 2.5 Flash | 32/36 (0,889) | 13 | 20 |
| Gemini 3.5 Flash | 34/36 (0,944) | 4 | 18 |

Gemini 3.5 Flash cải thiện độ phù hợp expected range và giảm semantic
lint, nhưng chỉ 75% candidate có cùng tập bắt buộc giữa hai lần chạy.
UET quyết định dừng hiệu chỉnh ở đây, chấp nhận giới hạn độ lặp lại và
chuyển sang một full run duy nhất.

Cấu hình Gemini 3.5 Flash:

- không gửi `temperature`, `top_p` hoặc `top_k`;
- `thinking_level=MEDIUM`;
- `include_thoughts=false`;
- `max_output_tokens=4096`;
- `seed=20260727`.

### 6.4. Full run 2.028 candidate

Full run dùng:

- model `gemini-3.5-flash`;
- một run duy nhất;
- concurrency 20;
- bundle `full_gemini35_medium_v1`;
- output tăng dần trong `run_full.jsonl`.

Lần chạy đầu còn hai candidate thiếu:

- `BC-HNMU-G9-R0285-STT4-AI08`;
- `BC-HNMU-G9-R0294-STT13-AI10`.

Chế độ `retry-failed` chỉ gửi lại hai candidate này. Sau ba request bổ
sung:

- có 2.028 record và 2.028 ID duy nhất;
- có 12.168 score;
- cả hai record phục hồi kết thúc bằng `FinishReason.STOP`;
- `integrity.validated = true`;
- failure hiện hành bằng 0;
- lỗi lịch sử vẫn được giữ riêng để bảo toàn provenance.

Bundle kỹ thuật của Plan 02 đã hoàn thành. Score vẫn là output của một
model, không phải nhãn chuyên gia.

## 7. Plan 03 — Phân tích full run và tạo pool ưu tiên

### 7.1. Cổng toàn vẹn

Phân tích được chạy hoàn toàn bằng code. Validator kiểm:

- đủ 2.028 candidate và 665 family;
- đủ 12.168 score;
- mọi ID và join một–một;
- request hash;
- user prompt đã lưu;
- model và generation config;
- evidence có thể truy về payload;
- trạng thái failure hiện hành.

Không gọi model/agent và không sửa score trong Plan 03.

### 7.2. Phân bố toàn bộ 2.028 candidate

| Nguyên tắc | Số candidate bắt buộc | Candidate-macro | Family-macro |
| --- | ---: | ---: | ---: |
| Challenge | 17 | 0,008 | 0,006 |
| Explanation | 1.115 | 0,550 | 0,594 |
| Modelling | 107 | 0,053 | 0,050 |
| Practice | 60 | 0,030 | 0,025 |
| Feedback | 1.412 | 0,696 | 0,670 |
| Questioning | 976 | 0,481 | 0,462 |

Phân bố cho thấy Feedback, Explanation và Questioning chiếm ưu thế;
Challenge và Practice rất hiếm. Đây có thể phản ánh đặc tính dữ liệu hội
thoại thô, hành vi của score model, hoặc cả hai. Không được diễn giải trực
tiếp thành tần suất sư phạm thật nếu chưa có nhãn chuyên gia.

### 7.3. Eligibility

Plan 03 chia ba trạng thái loại trừ nhau:

| Trạng thái | Số lượng | Tỷ lệ |
| --- | ---: | ---: |
| `eligible_without_plan03_review` | 1.400 | 0,690 |
| `needs_uet_review` | 628 | 0,310 |
| `blocked` | 0 | 0,000 |

Một candidate được xem là `eligible_without_plan03_review` khi:

- có từ một đến ba nguyên tắc bắt buộc;
- không có lỗi cấu trúc/evidence;
- không có semantic lint;
- không thuộc một tập nguyên tắc hiếm theo quy tắc Plan 03.

Lý do review lớn nhất là `feedback_confirmation_only` với 592 candidate.
Các lý do khác gồm Questioning không phụ thuộc câu trả lời, tập rỗng,
rationale mâu thuẫn với điểm cao, tập hiếm và trên ba nguyên tắc.

UET quyết định:

- đóng Plan 03;
- hoãn disposition 628 candidate thành backlog;
- không coi 628 candidate là đã bị loại hoặc đã được sửa;
- ưu tiên 1.400 candidate không có cờ cho các plan sau.

### 7.4. Phân bố pool 1.400 candidate

Pool 1.400 candidate thuộc 655 family. Phân bố theo lớp:

| Lớp | Candidate |
| ---: | ---: |
| 6 | 193 |
| 7 | 280 |
| 8 | 412 |
| 9 | 515 |

Phân bố theo lịch sử:

- 631 candidate không có lịch sử;
- 769 candidate có lịch sử.

Phân bố theo số nguyên tắc bắt buộc:

| Số nguyên tắc | Candidate |
| ---: | ---: |
| 1 | 443 |
| 2 | 866 |
| 3 | 91 |

Incidence theo nguyên tắc:

| Nguyên tắc | Candidate | Tỷ lệ trên 1.400 |
| --- | ---: | ---: |
| Challenge | 8 | 0,006 |
| Explanation | 863 | 0,616 |
| Modelling | 93 | 0,066 |
| Practice | 27 | 0,019 |
| Feedback | 806 | 0,576 |
| Questioning | 651 | 0,465 |

Các tổ hợp lớn nhất:

| Tập nguyên tắc bắt buộc | Candidate | Tỷ lệ |
| --- | ---: | ---: |
| Feedback + Questioning | 325 | 0,232 |
| Explanation + Feedback | 315 | 0,225 |
| Explanation | 290 | 0,207 |
| Explanation + Questioning | 138 | 0,099 |
| Questioning | 91 | 0,065 |
| Explanation + Feedback + Questioning | 58 | 0,041 |
| Feedback | 55 | 0,039 |
| Explanation + Modelling | 43 | 0,031 |

### 7.5. Ý nghĩa đúng của từ “eligible”

`eligible_without_plan03_review` chỉ có nghĩa candidate không cần một
lượt review riêng tại Plan 03 trước khi chuyển tiếp. Trạng thái này không
khẳng định:

- score là ground truth;
- `gold_response` có chất lượng tốt;
- grounding đã được HNMU xác nhận;
- candidate chắc chắn có giá trị phân biệt;
- candidate đã đủ điều kiện phát hành trong benchmark cuối.

Audit `gold_response`, grounding, leakage, trùng lặp, giá trị đánh giá và
review tích hợp vẫn là công việc bắt buộc ở plan sau.

## 8. Plan 04 — Xây thư viện tiêu chí hai tầng

### 8.1. Đơn vị nhiệm vụ

Thay vì tiếp tục tám task ứng viên cũ, benchmark hiện dùng một nhiệm vụ
chính:

`TASK-TUTOR-RESPONSE-001 — Sinh phản hồi tiếp theo của gia sư Tin học
THCS`.

Một candidate là một điểm cắt hội thoại. Tutor nhận context, metadata cần
thiết và tập nguyên tắc bắt buộc; evaluator nhận thêm căn cứ chuyên môn và
response tham chiếu.

### 8.2. Cấu trúc tiêu chí

Thư viện hiện có:

- bốn tiêu chí chung:
  - chính xác chuyên môn và có thể kiểm chứng;
  - bám trạng thái và mục tiêu trước mắt của học sinh;
  - mức hỗ trợ vừa đủ, bảo toàn phần việc có ý nghĩa;
  - giao tiếp rõ ràng, tôn trọng và phù hợp THCS;
- 18 tiêu chí riêng, đúng ba tiêu chí cho mỗi nguyên tắc;
- sáu lỗi nghiêm trọng;
- 29 quan hệ provenance;
- sáu ca biên dùng context thật từ pool 1.400.

Một candidate có `n` nguyên tắc bắt buộc sẽ kích hoạt:

```text
4 tiêu chí chung + 3 × n tiêu chí riêng
```

Cấu trúc này học từ cách KMP-Bench kích hoạt tiêu chí theo nguyên tắc,
nhưng nội dung tiêu chí được viết lại theo sáu năng lực, learning
resources Tin học THCS và đặc tính dữ liệu HNMU.

### 8.3. Quy tắc chống chồng lấn đã được UET duyệt

- tiêu chí chung đo điều kiện nền của toàn response;
- tiêu chí riêng chỉ đo giá trị tăng thêm của nguyên tắc được kích hoạt;
- serious error là cổng, không phải một rubric độc lập;
- mỗi error chỉ áp `suggested_action` một lần;
- `affected_rubric_ids` phục vụ truy vết, không tự động nhân số lần phạt.

Các ranh giới chính đã được làm rõ:

- Explanation làm rõ điều gì/vì sao; Modelling biểu diễn làm như thế nào;
- Practice củng cố khả năng áp dụng; Challenge tăng yêu cầu nhận thức vừa
  sức;
- Feedback bắt đầu từ đầu ra học sinh; Explanation không bắt buộc có đầu
  ra học sinh;
- Questioning cần câu trả lời có chức năng; Challenge cần nỗ lực nhận
  thức đáng kể;
- `CAP-STATE` mô tả trạng thái hiện tại; `CAP-DIAG` giải thích nguyên
  nhân;
- `CAP-STRAT` chọn phương tiện; `CAP-SCAFF` điều tiết mức và thời điểm hỗ
  trợ.

### 8.4. Sáu lỗi nghiêm trọng

Catalog hiện gồm:

1. sai nội dung chuyên môn;
2. bịa căn cứ;
3. củng cố hiểu sai;
4. làm thay, làm mất chức năng học;
5. nội dung gây hại hoặc hạ thấp học sinh;
6. không đáp ứng nhu cầu.

Rubric, lỗi và hành động hiện vẫn có trạng thái `needs_hnmu_review`.
Desk check chưa chứng minh độ tin cậy, độ phân biệt mô hình hoặc độ đồng
thuận giữa người chấm.

### 8.5. Artifact chính

- `outputs/benchmark_rubric/benchmark_tasks.csv`;
- `outputs/benchmark_rubric/rubrics.csv`;
- `outputs/benchmark_rubric/serious_errors.csv`;
- `outputs/benchmark_rubric/provenance_matrix.csv`;
- `outputs/benchmark_rubric/rubric_review_packet.md`.

## 9. Plan 05 và workstream paper đang chạy song song

Phần này được ghi để paper có ảnh chụp đầy đủ về trạng thái experiment.
Nó không thay đổi mốc chính của báo cáo là pool 1.400 candidate.

### 9.1. Cấu hình đánh giá

Đã tạo:

- `evaluation_protocol.md`;
- `model_registry.csv`;
- `instruction_registry.csv`;
- `evaluation_schema.json`;
- bundle instruction gia sư tiếng Việt có version;
- transport giữ native multi-turn;
- provider adapter, budget guard, validator và smoke runner.

Panel mục tiêu gồm:

- Gemini 3.5 Flash: model đóng đa dụng;
- Llama 4 Maverick: model open-weight đa dụng qua Vertex MaaS;
- SocraticLM: ứng viên chuyên biệt giáo dục tự triển khai;
- Claude Sonnet 4.6: judge thứ hai tùy chọn.

### 9.2. Smoke target

- Gemini 3.5 Flash smoke v2: 10/10 candidate, manifest `completed`,
  validator đạt.
- Llama 4 Maverick smoke v2 retry1: 10/10 candidate, manifest
  `completed`, validator đạt.
- SocraticLM: tooling endpoint đã được xây nhưng deployment model server
  thất bại; manifest hiện có `status = failed`. Model resource và endpoint
  resource đã được tạo, nhưng không có `deployed_model_id`. Đây là khoảng
  trống vận hành, không phải target đã đạt smoke.

### 9.3. Smoke judge

- Claude Sonnet 4.6 thất bại 20/20 do sản phẩm Anthropic chưa được kích
  hoạt trên Marketplace; không có phán quyết và chi phí API bằng 0.
- Judge tạm chuyển sang Gemini 3.5 Flash.
- Lần đầu hoàn tất 11/20; chín request dừng ở `MAX_TOKENS`.
- Retry1 tăng `max_output_tokens` lên 8.192, dùng tám worker và hoàn tất
  đủ 20/20 phán quyết; manifest được validate.

Rà nhanh sau smoke cho thấy judge bỏ sót một lỗi nghiêm trọng đã được
chuyên gia xác nhận ở `BC-HNMU-G7-R0207-STT10-AI10`. Đây phải được giữ
làm anchor khi kiểm judge ở pilot. Chi phí được manifest retry1 ghi nhận
là 0,716343 USD.

Giới hạn phải báo trong paper: Gemini 3.5 Flash vừa là một target vừa là
judge. Kết quả target Gemini phải được tách riêng và không được dùng một
mình để kết luận thứ hạng.

### 9.4. Pilot 80

Đã tạo manifest 80 candidate:

- 20 candidate mỗi lớp;
- 80 family duy nhất;
- 54 cặp lớp–bài học;
- incidence Challenge/Explanation/Feedback/Modelling/Practice/Questioning
  lần lượt là 8/48/41/14/12/35;
- lịch sử rỗng/không rỗng là 39/41;
- Bloom remember/understand/apply là 24/31/25;
- tập nguyên tắc có kích thước 1/2/3 là 23/36/21.

Pilot cố ý lấy quá mẫu Challenge và Practice nên không đại diện phân bố
pool. Hai target runner đã preflight; pilot chưa được chạy tại thời điểm
snapshot này.

### 9.5. Manuscript KSE

Đã hoàn thành:

- tải và lưu template IEEE chính thức;
- tạo `main.tex` và `references.bib`;
- viết Introduction;
- viết Related Work and Background;
- rà claim tính mới bằng truy vấn Anh–Việt;
- cập nhật vị trí so với DeepEduBench và CSTutorBench;
- biên dịch thành công PDF ba trang.

Claim an toàn hiện tại không phải “benchmark gia sư AI tiếng Việt đầu
tiên”. Cách diễn đạt có căn cứ hơn là: trong phạm vi nguồn công khai đã
sàng lọc, chưa tìm thấy benchmark kết hợp đồng thời:

1. phản hồi bằng tiếng Việt;
2. chương trình Tin học lớp 6–9;
3. sinh phản hồi gia sư tiếp theo có điều kiện theo lịch sử hội thoại;
4. candidate chuyển từ hội thoại sư phạm do giáo viên biên soạn và có
   truy vết học liệu.

Abstract, Dataset/Method đầy đủ, Results, Discussion và Conclusion vẫn
chưa hoàn thành.

## 10. Công việc mới nhất — đóng gói pool 1.400 candidate

### 10.1. Mục tiêu

Trước bước này, danh sách 1.400 ID chỉ nằm lồng trong
`full_run_analysis.json`, còn nội dung candidate, score, rationale và
`gold_response` nằm ở nhiều nguồn. Điều đó khiến các plan sau phải lặp lại
join và dễ dùng nhầm nguồn.

### 10.2. Cách thực hiện

Đã viết code:

`src/vertex_ai_call/export_eligible_candidate_pool.py`

Code:

1. đọc trực tiếp
   `eligibility.candidate_ids.eligible_without_plan03_review`;
2. validate danh sách ID và số lượng báo cáo;
3. join grounding pool, conversion candidate, conversion trace và full
   run bằng `benchmark_candidate_id`;
4. validate đủ 2.028 ID ở mọi nguồn trước khi lọc;
5. chỉ xuất đúng 1.400 ID eligible;
6. kiểm mỗi candidate có từ một đến ba nguyên tắc bắt buộc;
7. kiểm tập bắt buộc đúng bằng toàn bộ nguyên tắc có score từ 4 trở lên;
8. ghi file nguyên tử để không để lại output nửa chừng;
9. sắp xếp theo `benchmark_candidate_id` để tái tạo ổn định.

Không gọi model, không suy nhãn và không đọc review queue để đoán trạng
thái.

### 10.3. File đầu ra

`experiments/20260727_170150/outputs/benchmark_candidate_pool/eligible_without_plan03_review.csv`

File có 1.400 dòng dữ liệu và 23 cột, gồm:

- nội dung candidate;
- `source_question`, `gold_answer`, `gold_response`;
- vị trí target và đặc trưng history/family;
- tập nguyên tắc bắt buộc và số lượng;
- tập điểm 3;
- toàn bộ sáu score;
- toàn bộ rationale/evidence;
- trạng thái eligibility;
- model và request hash.

Kết quả validation:

- 1.400 candidate duy nhất;
- 655 family;
- không thiếu `student_prompt`, `gold_answer` hoặc `gold_response`;
- mọi tập bắt buộc khớp threshold;
- chạy lại tạo cùng SHA-256:
  `7dec13c3cc3a53337bc6c5fdf800e6c89856f49a3b6b0626dca885e59cb0fed9`.

File này là pool ưu tiên có thể dùng trực tiếp cho audit, pilot và bước
đánh giá tiếp theo. Nó không phải bản benchmark cuối để phát hành.

## 11. Các đóng góp có thể phát triển thành paper

### 11.1. Đóng góp về xây dựng dữ liệu

Một pipeline có truy vết chuyển hội thoại gia sư Tin học THCS do giáo
viên biên soạn thành candidate ở cấp lượt:

```text
1.050 hội thoại thô
    → 665 hội thoại đủ điều kiện vận hành
    → 2.028 điểm cắt candidate
    → 1.400 candidate ưu tiên không có cờ Plan 03
```

Điểm đáng nhấn mạnh không chỉ là số lượng mà là:

- mỗi lượt gia sư có thể trở thành một candidate;
- history được bảo toàn theo role;
- cùng một dialogue có thể tạo các độ sâu lịch sử khác nhau;
- candidate có thể truy về `sample_id`, source file và source row;
- `source_question` và `gold_answer` được bổ sung làm grounding.

### 11.2. Đóng góp về phương pháp xác định yêu cầu sư phạm

Thay vì chọn một task loại trừ hoặc một tập nhãn trực tiếp, phương pháp:

- chấm cả sáu nguyên tắc;
- tách “có thể hữu ích” khỏi “bắt buộc”;
- dùng score 1–5 với cổng rationale;
- loại `gold_response` để giảm thiên lệch;
- dùng code dẫn xuất tập instruction.

Đây là một mở rộng phù hợp với dữ liệu hội thoại đã tồn tại, khác với
KMP-Bench vốn chọn nguyên tắc trước khi sinh dialogue.

### 11.3. Đóng góp về kiến trúc tiêu chí

Thiết kế kết hợp:

- sáu nguyên tắc làm trục instruction/rubric riêng;
- sáu năng lực làm bản đồ độ phủ chất lượng;
- bốn tiêu chí chung;
- ba tiêu chí riêng trên mỗi nguyên tắc được kích hoạt;
- serious error tách khỏi rubric.

Thiết kế này cho phép một candidate dùng tập tiêu chí động nhưng vẫn có
lõi chung để so sánh.

### 11.4. Đóng góp về kỹ thuật và reproducibility

Pipeline lưu:

- exact user prompt;
- model và configuration;
- request hash;
- raw và normalized output;
- usage;
- manifest;
- failure hiện hành và lỗi lịch sử;
- output tăng dần và resume.

Mọi phép threshold, join và thống kê đều có thể tái tạo bằng code.

## 12. Bảng claim–bằng chứng phục vụ viết paper

| Claim dự kiến | Loại phát biểu | Bằng chứng chính | Cách viết an toàn |
| --- | --- | --- | --- |
| Dữ liệu có 2.028 candidate từ 665 family | Bằng chứng | conversion bundle; full-run analysis | Báo số lượng cùng quy tắc mỗi lượt gia sư tạo một candidate |
| Full run có đủ 12.168 score | Bằng chứng | `run_manifest.json`; `full_run_analysis.json` | Nêu đây là output của một run Gemini 3.5 Flash |
| 1.400/628/0 theo ba trạng thái | Bằng chứng | `full_run_analysis.json` | Gọi là trạng thái vận hành Plan 03, không gọi là nhãn chuyên gia |
| Feedback/Explanation/Questioning chiếm ưu thế | Bằng chứng mô tả | phân bố full run và eligible pool | Không suy thành tần suất sư phạm thật |
| Phương pháp loại gold_response giúp tránh selection bias | Suy luận phương pháp | contract V4; trình tự KMP-Bench đã tổng hợp | Trình bày như lý do thiết kế, chưa phải hiệu ứng thực nghiệm đã đo |
| Cấu trúc `4 + 3 × n` bảo đảm lõi chung và tiêu chí động | Suy luận thiết kế có căn cứ | KMP-Bench synthesis; rubric artifacts | Nêu rubric đang provisional, chờ xác nhận |
| Pipeline có thể tái tạo | Bằng chứng kỹ thuật | hash, manifest, exporter, tests | Nêu phạm vi tái tạo dữ liệu và thống kê |
| Benchmark có tính phân biệt giữa tutor tốt–trung bình–kém | Câu hỏi mở | chưa có pilot đầy đủ | Không claim trước khi Plan 07/pilot hoàn tất |
| Benchmark đã được HNMU xác nhận | Câu hỏi mở | chưa có review tích hợp | Không claim ở phiên bản paper hiện tại |
| Đây là benchmark gia sư AI tiếng Việt đầu tiên | Claim bị bác bỏ ở dạng rộng | novelty search log | Chỉ dùng claim hẹp ở giao điểm bốn thuộc tính |

## 13. Giới hạn và đe dọa tới hiệu lực

### 13.1. Độ đúng của requirement score

- Full pool chỉ có một run.
- Không có nhãn chuyên gia cấp candidate để tính accuracy.
- Calibration 36 ca là ca đối chứng có chủ đích, không đại diện pool.
- Gemini 3.5 Flash chỉ đạt 75% exact required-set agreement giữa hai run
  calibration.

Do đó, paper phải gọi score là model-assisted requirement scoring hoặc
nhãn vận hành của pipeline, không được trình bày như chân lý sư phạm đã
được xác nhận độc lập.

### 13.2. Semantic lint và eligibility

- Lint bằng code chỉ phát hiện một số mẫu mâu thuẫn rõ.
- 592 candidate bị cờ vì Feedback có thể chỉ là xác nhận/khen.
- Không có cờ không đồng nghĩa không có lỗi.
- Tổ hợp hiếm là quy tắc lấy mẫu review, không chứng minh tổ hợp sai.

### 13.3. Chất lượng candidate và gold response

- Pool 1.400 chưa qua audit đầy đủ `gold_response`.
- Một số gold response có thể chỉ khen, xác nhận hoặc thực hiện nguyên tắc
  chưa tốt.
- Benchmark đánh giá so sánh phải cho phép model response thắng
  reference.

### 13.4. Mất cân bằng nguyên tắc

Challenge và Practice rất hiếm. Nếu chỉ lấy mẫu ngẫu nhiên theo phân bố,
pilot khó kiểm hai nguyên tắc này. Pilot 80 đã cố ý oversample hai nhóm,
vì vậy kết quả pilot không được dùng như ước lượng không trọng số của
quần thể.

### 13.5. Judge bias và model panel

- Judge Gemini cùng họ với một target.
- Claude judge chưa chạy được vì Marketplace.
- SocraticLM chưa deploy thành công.
- Chưa có calibration người–judge độc lập mới.

### 13.6. Hiệu lực ngoại suy

Dữ liệu thuộc Tin học THCS Việt Nam, dựa trên hội thoại do giáo viên biên
soạn và learning resources cụ thể. Không được ngoại suy trực tiếp sang
môn khác, cấp học khác hoặc learning gain thực tế.

## 14. Công việc còn lại ưu tiên cho paper

### 14.1. Có thể viết ngay

1. Dataset and Construction:
   - nguồn dữ liệu;
   - audit 1.050 → 665;
   - conversion 665 → 2.028;
   - đơn vị candidate và history;
   - grounding/provenance.
2. Pedagogical Requirement Scoring:
   - sáu nguyên tắc;
   - tám trường input;
   - thang 1–5;
   - cổng 4–5;
   - threshold bằng code;
   - model/config và full-run integrity.
3. Rubric Design:
   - sáu năng lực;
   - một task;
   - cấu trúc `4 + 3 × n`;
   - serious-error gate.
4. Data Analysis:
   - phân bố 2.028;
   - eligibility 1.400/628/0;
   - phân bố pool 1.400.

### 14.2. Cần hoàn thành trước khi viết Results cuối

1. Chạy pilot 80 target và judge.
2. Phân tích Win/Tie/Lose, lỗi nghiêm trọng và khả năng phân biệt model.
3. Tách kết quả khi Gemini vừa là target vừa là judge.
4. Audit một tập phân tầng bằng UET/HNMU hoặc ít nhất ghi rõ phạm vi review
   có thật.
5. Quyết định disposition cho các phát hiện nghiêm trọng từ smoke.
6. Chốt có giữ hay bỏ model chuyên biệt nếu SocraticLM không đạt cổng.

### 14.3. Cần HNMU/UET quyết định

- nội dung và ranh giới 22 tiêu chí;
- sáu serious-error action;
- mức tin cậy cho requirement score;
- phạm vi candidate đủ điều kiện đưa vào benchmark chính thức;
- cách trình bày “ground truth vận hành” so với xác nhận chuyên gia;
- claim cuối cùng về tính mới và đóng góp.

## 15. Thứ tự ưu tiên nguồn trạng thái và các sai lệch tài liệu

Để phục vụ paper, báo cáo dùng thứ tự ưu tiên: run manifest và artifact đã
validate; sau đó đến roadmap/handoff mới nhất; cuối cùng mới là metadata
và phần mô tả cũ trong plan. Audit phát hiện các sai lệch cần tránh khi
trích số liệu:

- `metadata.yaml` dừng ở trạng thái smoke, trong khi roadmap và artifact
  thực tế đã ở cổng pilot 80; danh sách artifact trong metadata chưa bao
  phủ output Plan 04–05 mới.
- `full_run_analysis.md` còn tiêu đề `AWAITING_UET_DISPOSITION`; quyết
  định mới hơn đã đóng Plan 03 với trạng thái `UET REVIEW DEFERRED`.
- Một số đoạn cuối Plan 05 còn nói judge retry1 chưa chạy hoặc yêu cầu
  Claude hoàn thành, trong khi manifest mới chứng minh Gemini retry1 đã
  hoàn thành 20/20 và Claude bị chặn bởi Marketplace.
- `manuscript_status.md` dùng cụm “ground truth vận hành”, nhưng run
  manifest, roadmap và claim registry đều nêu không có expert accuracy.
  Paper nên dùng “nhãn vận hành do model hỗ trợ” hoặc diễn đạt tương đương
  cho đến khi có review chuyên gia tương ứng.
- Cụm “ready for downstream construction” trong manuscript chỉ nên được
  hiểu là không có cờ Plan 03; không được diễn giải thành benchmark đã
  sẵn sàng phát hành.

Tại thời điểm snapshot, nhiều artifact Plan 03–05 và exporter còn chưa
được commit; `metadata.yaml` vẫn có `git_commit: null`. Người phụ trách dự
án dự kiến commit thủ công sau khi plan/roadmap và artifact được chốt.

## 16. Chỉ mục artifact chính

### Dữ liệu kế thừa

- `inherited_resources/snapshot_manifest.csv`
- `inherited_resources/from_20260722_000940/benchmark_conversion/full_v0/benchmark_candidate_splits.csv`
- `inherited_resources/from_20260722_000940/benchmark_conversion/full_v0/conversion_trace.csv`
- `inherited_resources/from_20260722_000940/benchmark_specification/candidate_grounding/candidate_principle_grounding_pool.csv`

### Requirement scoring

- `outputs/principle_requirement_scoring/specification_v4.md`
- `outputs/principle_requirement_scoring/scoring_schema_v2.json`
- `outputs/principle_requirement_scoring/calibration_cases_v1.csv`
- `outputs/principle_requirement_scoring/calibration_gemini35_medium_v1/`
- `outputs/principle_requirement_scoring/full_gemini35_medium_v1/run_full.jsonl`
- `outputs/principle_requirement_scoring/full_gemini35_medium_v1/run_manifest.json`
- `outputs/principle_requirement_scoring/full_gemini35_medium_v1/full_run_analysis.json`
- `outputs/principle_requirement_scoring/full_gemini35_medium_v1/full_run_analysis.md`

### Pool ưu tiên mới

- `outputs/benchmark_candidate_pool/eligible_without_plan03_review.csv`
- `src/vertex_ai_call/export_eligible_candidate_pool.py`

### Rubric

- `outputs/benchmark_rubric/benchmark_tasks.csv`
- `outputs/benchmark_rubric/rubrics.csv`
- `outputs/benchmark_rubric/serious_errors.csv`
- `outputs/benchmark_rubric/provenance_matrix.csv`
- `outputs/benchmark_rubric/rubric_review_packet.md`

### Cấu hình đánh giá

- `outputs/benchmark_evaluation/evaluation_protocol.md`
- `outputs/benchmark_evaluation/model_registry.csv`
- `outputs/benchmark_evaluation/instruction_registry.csv`
- `outputs/benchmark_evaluation/evaluation_schema.json`
- `outputs/benchmark_evaluation/pilot_80_v1/candidate_manifest.json`

### Paper

- `kse_submit_manuscript/manuscript/main.tex`
- `kse_submit_manuscript/manuscript/references.bib`
- `kse_submit_manuscript/manuscript/main.pdf`
- `kse_submit_manuscript/notes/claim_evidence_registry.csv`
- `kse_submit_manuscript/notes/manuscript_status.md`

## 17. Kết luận

Experiment đã chuyển dự án từ một nhánh task-label còn thay đổi nhiều
sang một pipeline có thể vận hành và truy vết:

- candidate được grounding độc lập với `gold_response`;
- sáu nguyên tắc được chấm theo mức cần thiết;
- code dẫn xuất instruction set;
- rubric được kích hoạt động theo nguyên tắc nhưng vẫn có lõi chung;
- full run và phân tích đã hoàn tất kỹ thuật;
- pool 1.400 candidate đã được đóng gói thành artifact tự chứa.

Đóng góp mạnh nhất hiện tại cho paper là sự kết nối có hệ thống giữa dữ
liệu hội thoại giáo viên, requirement scoring theo nguyên tắc, mô hình
năng lực, rubric hai tầng và pipeline đánh giá có truy vết. Phần còn thiếu
để chứng minh benchmark phân biệt được tutor tốt–trung bình–kém là pilot
đánh giá nhiều model cùng review chuyên gia. Vì vậy, paper có thể viết
ngay phần nền, dữ liệu và phương pháp; các claim về hiệu lực và thứ hạng
phải chờ kết quả pilot hoặc được trình bày rõ như giới hạn.
