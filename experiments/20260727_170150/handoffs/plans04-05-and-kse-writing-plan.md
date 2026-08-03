# Specialist handoff

- Delegation ID: `EXP-20260728-FORWARD-PLANS-001`
- Agent: `benchmark-specification-designer` + `research-methodologist`
- Status: `completed_in_parent_single_agent_mode`
- Native thread ID/label: `null`

## Delegation prompt

Biên soạn ngắn gọn plan cho rubric hai tầng, cấu hình đánh giá nhiều LLM
và viết paper KSE, kế thừa experiment trước và không triển khai code/API.

## Inputs read

- `README.md`, `ARCHITECTURE.md`, roadmap active;
- Plan 03 active và Plans 03–05 của experiment trước;
- tổng hợp KMP-Bench, sáu nguyên tắc, sáu năng lực;
- `kse_submit_manuscript/PLAN.md` và template verification;
- tài liệu Vertex AI chính thức về Google, Claude và Llama models.

## Outputs created

- `plans/04-two-tier-rubric-library.md`;
- `plans/05-benchmark-evaluation-configuration.md`;
- bản rút gọn `kse_submit_manuscript/PLAN.md`;
- đồng bộ roadmap, README và metadata.

## Result summary

Ba plan đều ở trạng thái nháp chờ UET review. Output được giới hạn còn năm
artifact rubric, bốn artifact cấu hình đánh giá và một workspace paper
tối thiểu. Không gọi API, không sửa full-run output và không triển khai
plan chưa được duyệt.

## Orchestrator decision

Thứ tự phụ thuộc: Plan 03 → Plan 04 → Plan 05 → audit candidate/gold →
pilot đánh giá. Paper bắt đầu độc lập từ phần nền, không chờ chuỗi này.

## Follow-up ngày 28/07/2026 — native conversation history

Plan 05 đã được làm rõ ở mức đặc tả, chưa triển khai. Target tutor không
nhận candidate dưới dạng một chuỗi JSON. `student_prompt` là message
`user` đầu tiên; các lượt history giữ nguyên ranh giới và được ánh xạ
`student → user`, `tutor → assistant/model`. System instruction và dữ
liệu evaluator-only được tách riêng. Kiểm tra chỉ đọc trên 2.028 candidate
cho kết quả 665 history rỗng, 1.363 history không rỗng và 0 chuỗi sai cấu
trúc role.

## Follow-up ngày 28/07/2026 — panel model theo vai trò

UET chọn panel tinh gọn nhưng bắt buộc có model đóng, model mở và model
chuyên biệt cho giáo dục/gia sư. Danh sách không sao chép tên model của
KMP-Bench; paper chỉ làm căn cứ cho cấu trúc so sánh. Gemini 3.5 Flash và
Llama 4 Maverick là ứng viên vận hành cho hai nhóm đầu. Nhóm chuyên biệt
chưa khóa: SocraticLM được ưu tiên thẩm định và phải vượt cổng giấy phép,
tiếng Việt, native multi-turn, schema đầu ra và hạ tầng. LearnLM không còn
là model độc lập nên Gemini 2.5 không được dùng để lấp slot chuyên biệt.

## Follow-up ngày 28/07/2026 — Vertex AI và ngân sách 250 USD

Panel lõi được giới hạn ở ba nhóm: Gemini 3.5 Flash, Llama 4 Maverick và
một model chuyên biệt qua cổng thẩm định; Claude Sonnet 4.6 là tùy chọn.
Ngân sách 250 USD bao gồm 56 USD lịch sử, 20 USD smoke/endpoint, 40 USD
pilot, 109 USD phần chạy chính và 25 USD dự phòng. Dự toán phải bao gồm
target, judge, retry và endpoint tự triển khai. Claude chỉ làm judge thứ
hai trên tập con 60 candidate phân tầng. Nếu vượt trần, bỏ model tùy chọn
hoặc giảm số candidate; không bỏ một nhóm model bắt buộc.

## Follow-up ngày 28/07/2026 — triển khai Plan 05

- Đã cài `dialogue_transport.py`, provider adapters, prompt builder,
  budget guard, config builder, validator và smoke preparation.
- Hai CLI nằm tại `scripts/benchmark_evaluation/`: một CLI sinh đúng bốn
  artifact, một CLI smoke Gemini/Llama có preflight, progress, JSONL tăng
  dần, resume và retry.
- Bốn artifact hiện nằm dưới
  `outputs/benchmark_evaluation/`: protocol, model registry, instruction
  registry và evaluation schema. Các run smoke/pilot/full của cùng phase
  dùng thư mục con bên dưới gốc này.
- Validator kiểm đủ 2.028 history, pool ưu tiên 1.400, 22 rubric, 6 lỗi,
  4 model và 7 instruction.
- Test Plan 05 đạt 18/18 và toàn bộ `tests/` của dự án đạt 181/181 bằng
  `benchmark_env`; Gemini và Llama preflight đạt nhưng không gọi API.
- Trạng thái bàn giao: chờ người dùng review code/artifact và chủ động
  chạy smoke bằng cờ `--execute-api`; instruction vẫn chờ HNMU review.

## Follow-up ngày 28/07/2026 — progress, provenance instruction và TutorChat

- Smoke runner đã thay progress bar tự viết bằng `tqdm`; thanh tiến trình
  hiển thị số mẫu xử lý trên tổng số, ETA, tốc độ, số thành công, số lỗi
  đang chờ thử lại và vòng retry.
- `instruction_registry.csv` vẫn là nguồn instruction duy nhất nhưng nay
  có thêm `basis_summary` và `source_locator`; hai cột này chỉ phục vụ
  review/provenance, không được gửi vào tutor model.
- Instruction nguyên tắc là bản tổng hợp của registry sáu nguyên tắc
  (Allison–Tharby + KMP-Bench), ranh giới include/exclude và mô hình sáu
  năng lực; không phải bản sao nguyên văn prompt của KMP-Bench.
- KMP-Bench Table 1 xác nhận `TutorChat-LLM` tốt hơn SocraticLM và
  MathChatsync-LLM trong ba baseline chuyên biệt bên ngoài. Tuy nhiên,
  checkpoint này là Qwen2.5-Math-7B do nhóm KMP fine-tune trên TutorChat,
  chưa có model ID công khai trong paper và không đồng nhất với
  `Llemma-7B-32K-MathMix`. Do đó chưa thay registry chạy được; cần xác
  minh checkpoint/giấy phép trước.

## Follow-up ngày 28/07/2026 — kế hoạch viết paper khẩn

Plan paper được khóa lại quanh ba đóng góp: pipeline 1.050→665→2.028,
requirement/rubric sáu nguyên tắc–sáu năng lực và phân tích pool
1.400/628. Sau khi UET duyệt, source LaTeX được tạo ngay; Introduction,
Related Work và nền tảng được viết trước. Bản v0.1 compile được phải sẵn
trước 11:00 ngày 29/07 để người dùng gửi giáo sư.

## Open questions and next human decisions

- UET duyệt hoặc sửa Plans 04–05.
- UET/giáo sư chốt title, contributions, authors và track KSE.
- HNMU review rubric/instruction sau khi có gói tích hợp và ví dụ.

## Follow-up ngày 28/07/2026 — khả thi Vertex AI và ngân sách

- `hard_budget_usd = 250` nay bao gồm cả chi phí đã phát sinh.
- Usage metadata Plan 02 quy đổi theo giá Standard hiện tại thành khoảng
  55,41 USD; cần thay bằng số billing thật trước run tiếp theo.
- Giá chính thức được snapshot cho Gemini 3.5 Flash, Llama 4 Maverick và
  Claude Sonnet 4.6.
- Dự toán API tương lai theo giả định bảo thủ là 124,80 USD, chưa gồm
  endpoint model chuyên biệt.
- Claude judge bị giới hạn ở tập con 60 candidate × 3 target response;
  Gemini judge chấm toàn bộ.
- Endpoint chuyên biệt có upper bound 40 USD và time-to-live cứng.
- Runner tương lai phải cộng chi phí lịch sử, current spend, upper bound
  batch kế tiếp và reserve trước khi cho phép gửi request.

## Follow-up ngày 28/07/2026 — khóa ngưỡng nguyên tắc Plan 05

- UET xác nhận Plan 05 chỉ dùng đúng tập nguyên tắc có
  `requirement_score >= 4`; điểm `3` không phải lựa chọn thay thế.
- Rà toàn bộ 2.028 record cho thấy 0 mismatch giữa sáu score và
  `required_principle_set`, 0 nguyên tắc điểm 3 lọt vào tập bắt buộc và
  0 nguyên tắc điểm 4–5 bị thiếu.
- Runner Plan 05 nay tự tái lập tập `>= 4` từ score và dừng đóng nếu
  trường lưu sẵn không trùng; `alternative_principle_set` không được đọc.
- Target response lưu `required_principle_ids`. Evaluation schema bắt
  buộc bốn rubric chung và đúng ba rubric riêng cho mỗi nguyên tắc bắt
  buộc, đồng thời cấm rubric của nguyên tắc ngoài tập.
- Preflight 10 mẫu đạt, 20 test Plan 05 và 183 test toàn dự án đạt bằng
  `benchmark_env`; không gọi Vertex AI.
