# Specialist handoff

- Delegation ID: `EXP-20260727-CODE-FIRST-PATHS-001`
- Agent: orchestrator single-agent với `benchmark-specification-designer`
- Status: `completed_planning_only`
- Native thread ID/label: không có

## Delegation prompt

Rà lại Plans 01–02 để ưu tiên code cho mọi xử lý xác định, khóa nơi đặt
code Vertex, system prompt, credential cục bộ và kết quả chạy.

## Inputs read

- README, ARCHITECTURE và active roadmap;
- Plans 01–02;
- cấu trúc hiện có của `src/vertex_ai_call/`,
  `shared/prompts/benchmark_candidate_task_assigning/` và output
  experiment;
- trạng thái Git ignore của `src/vertex_ai_call/.env`;
- skill `benchmark-specification-designer`.

## Outputs updated

- Plan 01 khóa ranh giới model–code và vị trí system prompt;
- Plan 02 khóa vị trí code, prompt, credential và output;
- artifact Plan 01 và bundle pilot được thu gọn để UET review;
- roadmap, README và ARCHITECTURE được đồng bộ;
- `.gitignore` bảo vệ `src/vertex_ai_call/.env`.

## Result summary

Model chỉ chấm sáu score và sinh rationale/evidence. Code thực hiện mọi
threshold, lọc tập, validation, join, review-rule, coverage và metric có
thể tái lập xác định.

Đường dẫn đã khóa:

- code: `src/vertex_ai_call/`;
- secret: `src/vertex_ai_call/.env`, chỉ đọc cục bộ và bị ignore;
- prompt:
  `shared/prompts/benchmark_candidate_task_assigning/system_prompt_v1.md`;
- output:
  `experiments/20260727_170150/outputs/principle_requirement_scoring/`.

Giới hạn artifact:

- Plan 01 chỉ publish `specification_v1.md`, `scoring_schema_v1.json` và
  `specification_manifest_v1.json`;
- system prompt là file dùng chung thứ tư, không copy vào output;
- pilot dùng một thư mục phẳng với input, hai JSONL run, review queue,
  manifest và summary; comparison đầy đủ được tái tạo bằng code, không
  publish thành file riêng;
- code Vertex dùng ba module chính, không tạo package con.

System prompt và yêu cầu rationale/evidence dùng tiếng Việt. Chỉ giữ tiếng
Anh cho ID, JSON key, tên trường kỹ thuật và tên model/API; không tạo một
bản prompt tiếng Anh song song.

## Safety note

Trong quá trình rà soát không đọc hoặc hiển thị nội dung `.env`. Trước khi
cập nhật, file đang untracked và chưa được ignore; rule bảo vệ đã được bổ
sung vào `.gitignore`.

## Open questions and next human decisions

- UET review Plan 01 sau các thay đổi.
- Plan 02 vẫn bị chặn cho đến khi Plan 01 hoàn thành.
