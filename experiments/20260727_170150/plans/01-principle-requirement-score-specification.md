# Plan 01 — Đặc tả mức độ cần thiết của sáu nguyên tắc

Experiment: `20260727_170150`
Trạng thái: `COMPLETED — SPECIFICATION_V4_PUBLISHED`
Ngày soạn: 27/07/2026
Phụ thuộc: snapshot từ experiment `20260722_000940`

## 1. Mục tiêu

Khóa mô hình đo lường trước khi viết runner hoặc gọi model:

1. định nghĩa chính xác `requirement_score`;
2. xây anchor 1–5 cho cả sáu nguyên tắc;
3. khóa một lượt grounding duy nhất, input được phép đọc và các trường bị
   cấm;
4. viết system prompt canonical và response schema;
5. định nghĩa cách code dẫn xuất tập nguyên tắc bắt buộc/thay thế;
6. làm rõ quan hệ giữa score, instruction của tutor và rubric.

Plan này không cài Vertex runner, không gọi API và không tạo score cho
candidate thật. Việc triển khai và pilot thuộc Plan 02.

## 2. Căn cứ và giới hạn chuyển giao từ KMP-Bench

KMP-Bench cắt hội thoại trước lượt gia sư, tạo instruction riêng cho từng
mẫu và nêu rõ một hoặc hai nguyên tắc đích. Phản hồi mô hình sau đó được so
với phản hồi tham chiếu bằng bốn tiêu chí chung và ba tiêu chí cho mỗi
nguyên tắc được chỉ định.

Plan này kế thừa cấu trúc:

```text
context
→ xác định nguyên tắc đích
→ đưa nguyên tắc vào instruction của mẫu
→ sinh phản hồi
→ tiêu chí chung + tiêu chí theo nguyên tắc
```

Khác biệt cần kiểm định:

- KMP-Bench thiết kế nguyên tắc trước khi sinh dialogue/reference;
- dữ liệu HNMU đã có sẵn, nên dự án phải suy mức độ cần thiết trong một
  lượt grounding duy nhất, sử dụng đồng thời context và `gold_answer` nhưng
  không đọc `gold_response`;
- `gold_response` HNMU chưa chắc đã được viết để thể hiện đủ mọi nguyên tắc
  được suy ra, nên phải được audit trước khi dùng làm đối chứng.

## 3. Đại lượng cần chấm

Tên trường: `requirement_score`.

Câu hỏi vận hành:

> Để một phản hồi tiếp theo đáp ứng đúng nhu cầu quan sát được của học sinh
> trong context này, nguyên tắc sư phạm này cần thiết ở mức nào?

Không chấm:

- nguyên tắc mà `gold_response` tình cờ thể hiện;
- mức độ model thích dùng một chiến lược;
- sự xuất hiện của từ khóa bề mặt;
- chất lượng thực thi nguyên tắc; phần đó thuộc rubric.

### 3.1. Anchor chung 1–5


| Điểm | Ý nghĩa                                                                                     |
| -----: | --------------------------------------------------------------------------------------------- |
|      1 | Không phù hợp hoặc có nguy cơ làm lệch nhu cầu hiện tại.                           |
|      2 | Liên quan yếu/bề mặt; không tạo chức năng sư phạm độc lập.                       |
|      3 | Là chiến lược thay thế hợp lệ nhưng context không bắt buộc phải dùng.            |
|      4 | Rõ ràng nên có trong một phản hồi tốt cho tình huống này.                          |
|      5 | Chức năng cốt lõi; bỏ đi thì phản hồi không còn đáp ứng đúng nhu cầu chính. |

Mỗi nguyên tắc phải có anchor 1–5 cụ thể hóa riêng, nhưng không được đổi
nghĩa chung của năm mức.

### 3.2. Tập dẫn xuất

- `required_principle_set`: mọi nguyên tắc có
  `requirement_score >= 4`;
- `alternative_principle_set`: mọi nguyên tắc có điểm 3;
- điểm 1–2: không đưa vào instruction hoặc rubric riêng.

Các tập này do code dẫn xuất ở Plan 02, không cho model tự ghi.

### 3.3. Ranh giới model–code

Chỉ dùng model cho phần cần phán đoán ngữ nghĩa: chấm sáu
`requirement_score` và viết rationale/evidence tương ứng.

Mọi phần xác định phải dùng code, gồm:

- kiểm exact schema, ID, số lượng sáu nguyên tắc và miền điểm 1–5;
- lọc `requirement_score >= 4` thành `required_principle_set`;
- lọc `requirement_score == 3` thành `alternative_principle_set`;
- phát hiện tập rỗng, tập có hơn ba nguyên tắc và các điều kiện review;
- join dữ liệu, kiểm hash, loại trùng và tổng hợp coverage;
- so sánh các run và tính toàn bộ metric.

Không yêu cầu model hoặc agent tự chọn tập sau khi đã chấm điểm, tự áp
threshold, tự tính metric, tự xác nhận output hoặc thực hiện phép biến đổi
mà code có thể tái lập chính xác.

## 4. Một lượt grounding duy nhất

Mỗi candidate chỉ được chấm trong **một lượt**. Model nhận đồng thời toàn
bộ payload đã duyệt, gồm bối cảnh hội thoại, câu hỏi nguồn và
`gold_answer`, rồi trả về đủ sáu `requirement_score` trong một response.

Không còn:

- vòng context sơ bộ rồi mới mở thêm grounding;
- nhãn trước/sau hoặc thao tác sửa nhãn giữa hai vòng;
- trường `reference_effect`, phép so sánh trước–sau hoặc hợp hai tập nhãn;
- yêu cầu model truy ngược sang một file khác để lấy `gold_answer`.

`gold_answer` là neo chuyên môn giúp hiểu mục tiêu kiến thức và phát hiện
điểm học sinh đang thiếu hoặc sai. Nó không tự quyết định phải dùng nguyên
tắc sư phạm nào và không được coi là mẫu phản hồi gia sư.

### 4.1. Input bị khóa

Nguồn active:

`inherited_resources/from_20260722_000940/benchmark_specification/candidate_grounding/candidate_principle_grounding_pool.csv`

Grounding pool và `pilot_input.csv` giữ:

- `benchmark_candidate_id`, `sample_id`;
- `grade`, `lesson`, `position`, `bloom_level`;
- `student_prompt`, `conversation_history`;
- `source_question`, `gold_answer`.

Từ v2, payload thực sự gửi model chỉ chứa tám trường ngữ nghĩa từ `grade`
đến `gold_answer`. `benchmark_candidate_id` và `sample_id` chỉ phục vụ
điều phối/truy vết ở phía code, không được gửi model. Code tự nối
`benchmark_candidate_id` vào normalized result sau khi response hợp lệ.

Không được chứa:

- `gold_response`;
- nhãn của run cũ;
- expected label của forward test;
- output A/B hoặc `diagnostic_legacy/`;
- tên boundary được viết để gợi nhãn;
- các lượt sau target response.

Plan 01 phải xuất một bảng data contract có exact header, kiểu dữ liệu,
nullability và ý nghĩa từng trường. Payload gửi model phải chứa trực tiếp
các trường trên trong cùng một request. Plan 02 chỉ được triển khai đúng
contract đã duyệt.

## 5. System prompt contract

System prompt canonical phải được viết bằng **tiếng Việt** và dùng cho toàn
bộ run, gồm:

- mục tiêu `requirement_score`;
- quy định đây là một lượt grounding duy nhất và phải dùng đồng thời các
  bằng chứng được cung cấp;
- định nghĩa/ràng buộc của sáu nguyên tắc;
- anchor 1–5 chung và anchor riêng;
- phép kiểm tra chức năng độc lập;
- phân biệt “bắt buộc đồng thời” với “chiến lược thay thế”;
- cấm đọc hoặc suy diễn `gold_response`;
- yêu cầu trả đủ sáu nguyên tắc đúng một lần;
- quy tắc viết rationale/evidence ngắn gọn bằng tiếng Việt.

Chỉ giữ tiếng Anh cho:

- các ID ổn định như `PRINCIPLE-CHALLENGE`;
- tên trường JSON như `principle_id`, `requirement_score`;
- tên model/API hoặc thuật ngữ không có cách diễn đạt tiếng Việt tương
  đương rõ ràng.

Không viết hai bản Việt–Anh song song trong cùng prompt vì làm tăng token
và có thể tạo hai cách diễn giải. Nội dung giá trị trong payload được giữ
nguyên như dữ liệu nguồn; tên trường kỹ thuật không cần dịch.

Prompt không chứa ví dụ lấy từ output A/B hoặc forward test cũ. Nếu dùng
few-shot, ví dụ phải được tạo mới, có nguồn gốc và UET duyệt; không dùng
nhãn model cũ làm đáp án.

File prompt canonical được lưu tại:

`shared/prompts/benchmark_candidate_task_assigning/system_prompt_v4.md`

Các version sau không ghi đè version đã dùng trong run. Manifest phải ghi
đường dẫn tương đối, SHA-256 và `prompt_language: "vi"` của prompt.

## 6. Output schema

Model trả:

```json
{
  "principle_scores": [
    {
      "principle_id": "PRINCIPLE-CHALLENGE",
      "requirement_score": 1,
      "rationale": "...",
      "evidence": "..."
    }
  ]
}
```

Code sau đó nối `benchmark_candidate_id` từ request đang xử lý; model
không sinh hoặc lặp lại ID truy vết.

Schema phải yêu cầu:

- đúng sáu object;
- `principle_id` thuộc registry và không trùng;
- `requirement_score` là số nguyên 1–5;
- `evidence` chỉ viện dẫn các trường có trong payload grounding duy nhất;
- không có trường tập nhãn do model tự chọn;
- không có trường nhãn trước/sau hoặc `reference_effect`;
- không có trạng thái `confirmed`;
- không có nội dung `gold_response`.

## 7. Rationale và bằng chứng

Để giảm token nhưng vẫn truy vết, mỗi nguyên tắc chỉ dùng một trường
`evidence`; không tách `context_evidence` và `grounding_evidence`:

- điểm 4–5: rationale và evidence bắt buộc;
- điểm 3: rationale ngắn bắt buộc vì nằm sát ngưỡng;
- điểm 1–2: cho phép rationale rút gọn, nhưng vẫn phải giải thích khi
  nguyên tắc dễ nhầm với nhu cầu chính;
- rationale không được nhắc nội dung không có trong request.

Không dùng confidence tự khai của model thay cho bằng chứng hoặc độ ổn
định thực nghiệm.

## 8. Trường hợp mơ hồ phải biểu diễn thế nào?

Nếu hai nguyên tắc là hai chiến lược thay thế đều hợp lệ nhưng context
không bắt buộc chiến lược nào, cả hai nên nhận điểm 3. Không chấm cả hai là
4 chỉ vì cả hai đều có thể dùng.

Nếu context thực sự đòi hỏi hai chức năng cùng xuất hiện, cả hai có thể
nhận 4–5. Plan sau phải đưa cả hai vào instruction để tutor biết rõ yêu
cầu; khi đó rubric riêng cho cả hai không phải yêu cầu ẩn.

## 9. Quan hệ với instruction và rubric

```text
6 requirement scores
        ↓ code
required set (>=4) + alternative set (=3)
        ↓
instruction của tutor ghi rõ required set
        ↓
rubric chung + rubric riêng của required set
```

Không áp rubric riêng cho nguyên tắc điểm 3. Nếu không đưa
`required_principle_set` vào instruction của tutor, rubric riêng trở thành
yêu cầu ẩn và không được sử dụng.

`gold_response` chỉ được đọc sau khi requirement, instruction và rubric đã
khóa. Plan audit sau phải cho phép model response thắng `gold_response`.

## 10. Artifact dự kiến

Mục tiêu là tạo **một gói review tối thiểu**, không tách mỗi bảng hoặc
quyết định thành một file riêng.

Artifact đặc tả thuộc experiment:

```text
outputs/principle_requirement_scoring/
├── specification_v4.md
├── scoring_schema_v2.json
├── calibration_cases_v1.csv
└── specification_manifest_v4.json
```

`specification_v4.md` gom contract active, định nghĩa ranh giới và cơ chế
kiểm định. `calibration_cases_v1.csv` là ngoại lệ máy đọc duy nhất: 36 ca
positive/near-miss được runner dùng trực tiếp, nên không lặp lại thành một
bảng human-facing khác.

`scoring_schema_v2.json` chứa cả input schema và response schema bằng
`$defs`, tránh hai file JSON gần như luôn phải review cùng nhau.

System prompt dùng chung nằm ngoài output experiment:

```text
shared/prompts/benchmark_candidate_task_assigning/
└── system_prompt_v4.md
```

Các file V1–V3 được giữ để truy vết các pilot đã chạy. Mọi API call mới
dùng V4. System prompt V4 giữ nguyên input/schema/ngưỡng, bắt buộc điểm
4–5 nêu nhu cầu độc lập và hệ quả khi bỏ nguyên tắc, đồng thời siết riêng
ranh giới Feedback và Questioning.

Các tài liệu human-facing viết tiếng Việt. JSON schema và comment phục vụ
runner viết tiếng Anh.

Không tạo bản copy `specification_snapshot/` trong Plan 02. Run manifest
chỉ ghi đường dẫn và hash của ba artifact đặc tả cùng system prompt.

## 11. Trình tự thực hiện

1. Validate snapshot 41 file và active grounding pool.
2. Viết data contract cho một payload grounding duy nhất có
   `gold_answer`.
3. Viết anchor riêng 1–5 cho từng nguyên tắc.
4. Viết prompt tiếng Việt tại
   `shared/prompts/benchmark_candidate_task_assigning/` và response schema
   một lượt, không có trạng thái trước–sau.
5. Tạo ví dụ mới bao phủ ranh giới, không dùng output legacy.
6. UET review định nghĩa, anchor, prompt, schema và ví dụ.
7. Ghi disposition trực tiếp trong `specification_v4.md` và sửa đến khi
   toàn bộ câu hỏi mở được xử lý.
8. Tạo 36 ca calibration cân bằng và khóa version/hash trong manifest bàn
   giao cho Plan 02.

## 12. Quyền quyết định

- UET duyệt định nghĩa, anchor, prompt, schema và ví dụ.
- HNMU xác nhận ý nghĩa sư phạm trong gói tích hợp sau khi rubric đã có;
  việc UET duyệt Plan 01 chỉ là phê duyệt phương pháp tạm thời.
- Model không tham gia tự duyệt prompt hoặc anchor.
- Orchestrator chỉ tổng hợp, validate và áp quyết định đã ghi.

## 13. Điều kiện hoàn thành

Plan 01 chỉ `COMPLETED` khi:

1. snapshot và grounding pool đạt hash/schema;
2. `requirement_score` và năm anchor được định nghĩa không mâu thuẫn;
3. sáu nguyên tắc có anchor riêng và ví dụ biên;
4. input contract dùng một lượt grounding có `gold_answer` và vật lý loại
   `gold_response`;
5. prompt viết bằng tiếng Việt, yêu cầu rationale/evidence tiếng Việt và
   response schema yêu cầu đúng sáu score;
6. output chỉ có một kết quả cuối, không có nhãn trước–sau,
   `reference_effect` hoặc hai loại evidence;
7. mọi phép lọc, threshold, validation, join và metric xác định được giao
   cho code, không giao cho model/agent;
8. quy tắc tập bắt buộc/thay thế và quan hệ rubric được khóa;
9. UET review có disposition đầy đủ;
10. manifest V4 có hash của mọi artifact và prompt dùng chung;
11. gói V4 chỉ thêm một CSV máy đọc cần thiết cho calibration, không sinh
    thêm bản sao review;
12. report, paper update, coordination và handoff hoàn chỉnh.

Plan 01 không cài code gọi Vertex, không chọn model/quota, không chạy pilot
và không chấm candidate thật.
