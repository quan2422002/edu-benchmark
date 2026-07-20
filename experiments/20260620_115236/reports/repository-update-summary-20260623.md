# Tóm tắt cập nhật repository đến ngày 23/06/2026

## Phạm vi đối chiếu

Báo cáo này tóm tắt hai nhóm thay đổi:

1. `main`: từ commit `59e16d1` (`P01: testing - done`) — trạng thái gần nhất trước khi tiếp tục làm việc trên thiết bị khác — đến commit `408405b` (`P01: complete fresh-session agent validation`).
2. `feature/C01_P02_P03`: từ base `408405b` đến commit mới nhất `c76bc20`, gồm ba commit:
   - `b3c5fd7` — `plan C01: Adding real curriculum into projects`;
   - `1851d66` — `plans mini P02 and P03: MVP version of full P02 and P03`;
   - `c76bc20` — `Update current status of project`.

Đây là báo cáo mô tả branch, không phải quyết định merge feature vào `main` và không thay thế report/plan của từng experiment.

## 1. Những thay đổi mới trên `main`

### 1.1. P01 được đóng hoàn chỉnh

P01 chuyển từ `IMPLEMENTED_PENDING_FRESH_SESSION_TEST` sang `COMPLETED` vào ngày 21/06/2026.

Kiểm tra còn thiếu trước đó — custom-agent discovery trong một phiên Codex mới — đã hoàn thành:

- `research-methodologist` được resolve trực tiếp bằng custom agent type;
- specialist chạy trong native observable thread;
- thread có thể được inspect và steer;
- agent phân biệt đúng evidence, inference, unsupported inference và open question;
- agent từ chối suy diễn learning gain từ kết quả đánh giá response;
- không sử dụng nested `codex exec`, `claude -p`, daemon hoặc hidden specialist process.

Audit trail mới gồm coordination events và handoff `p01-adapter-discovery-002.md`.

### 1.2. Hoàn tất kiểm tra cross-platform trên Windows

Hai skill discovery entry trong `.agents/skills/` đã được materialize và xác nhận là symbolic link trên Windows, đồng thời Git index giữ mode `120000`.

P01 được validate lại bằng `benchmark_env` trên Windows:

- Python `3.12.13`;
- `PyYAML 6.0.3`;
- `pytest 9.1.1`;
- hai skill pass `quick_validate.py`;
- test suite tăng từ 16 lên 17 test và đạt `17/17`;
- Python compilation, `pip check`, coordination JSONL parsing và `git diff --check` đều pass.

Claude adapter vẫn chỉ được static validation; runtime test tiếp tục mang trạng thái `DEFERRED_NOT_FAILED` theo scope P01.

### 1.3. Chuẩn hóa môi trường Python cho Windows và Linux

`README.md`, `ARCHITECTURE.md`, `AGENTS.md` và plan P01 được cập nhật để công nhận cùng một Conda environment `benchmark_env` với executable theo nền tảng:

- Windows: `D:\conda-envs\benchmark_env\python.exe`;
- Linux: `/home/quannda/miniconda3/envs/benchmark_env/bin/python`.

Quy tắc không thay đổi: mọi cài package, validator và test phải dùng `benchmark_env`, không dùng Conda base hoặc system Python.

Test tài liệu mới kiểm tra cả hai path trên, cùng các cảnh báo về Conda base và system Python.

### 1.4. Cập nhật tài liệu và vệ sinh repository

- `ARCHITECTURE.md` ghi Codex adapters đã fresh-session smoke-test và skill discovery links đã được validate.
- `README.md` bổ sung lệnh cài đặt/validation cho PowerShell và Linux.
- `.gitignore` bổ sung `.vscode/` và `__pycache__/`.
- Report P01 được cập nhật thành báo cáo hoàn tất, kèm kết quả Windows và audit artifact mới.
- Thêm `project-understanding.md`, ghi lại cách hiểu tổng thể về mục tiêu nghiên cứu, human-in-the-loop, kiến trúc agent, roadmap, prototype dữ liệu và các ranh giới cần giữ.

### 1.5. Ý nghĩa của bản `main` mới

So với mốc `59e16d1`, `main` mới không mở rộng benchmark science; thay đổi chủ yếu là đóng acceptance gate còn thiếu của P01 và làm nền tảng agent có thể tái lập trên cả Windows lẫn Linux. Sau commit `408405b`, P01 không còn chặn công việc downstream vì lý do custom-agent discovery.

## 2. Nội dung trên `feature/C01_P02_P03`

Feature branch kế thừa `main` tại `408405b` và bổ sung hai experiment chính: C01 và F01.

## 2.1. C01 — curriculum grounding có truy vết

Experiment: `experiments/20260621_052024/`

Trạng thái report: `AWAITING_EXPERT_TEACHER_REVIEW`.

### Mục tiêu

C01 đưa nguồn chương trình thực tế vào dự án để mọi ví dụ có thể truy ngược tới yêu cầu Tin học lớp 9 cụ thể. C01 không tuyên bố tạo benchmark specification, item bank đã duyệt hay production dataset.

### Nguồn và thứ bậc thẩm quyền

C01 sử dụng:

1. Chương trình GDPT môn Tin học ban hành kèm Thông tư 32/2018/TT-BGDĐT — nguồn chuẩn tắc;
2. Tài liệu tìm hiểu Chương trình môn Tin học của Bộ GDĐT và Trường ĐHSP Hà Nội năm 2019 — nguồn diễn giải;
3. workbook `Benchmark Tin học THCS.xlsx` — nguồn nội bộ chỉ dùng tham khảo cấu trúc và ví dụ, không phải ground truth.

Các yêu cầu lớp 9 được định vị tại trang in 37–40. Reference contract yêu cầu page, section/table, location note và paraphrase cụ thể; chỉ lưu URL là không đủ.

### Kết quả kiểm tra workbook

- 160 item ID duy nhất, trong đó có 40 item lớp 9;
- phân bố lớp 9: 12 DL, 12 ICT và 16 CS;
- tất cả item lớp 9 vẫn ở trạng thái `draft_v1`;
- các trường expert review và pilot đều trống;
- `Expert_Form` là snapshot tĩnh của các trường hiển thị;
- workbook hữu ích để tham khảo nhưng không chứng minh curriculum alignment, correctness, difficulty hoặc rubric validity;
- file nguồn được giữ nguyên hash và không bị sửa.

### Coverage và bộ mẫu C01

C01 đề xuất tám nhóm ví dụ lõi:

1. giải thích khái niệm lớp 9;
2. đánh giá thông tin hoặc hành vi số;
3. phản hồi lập luận của học sinh;
4. lập kế hoạch hoạt động/sản phẩm số;
5. review sản phẩm số hoặc kết quả mô phỏng;
6. xây dựng thuật toán;
7. chẩn đoán thuật toán/chương trình;
8. khám phá nghề nghiệp không định kiến.

Module bù prerequisite lớp dưới và các chủ đề lựa chọn về bảng tính nâng cao/video bị loại khỏi core hiện tại.

Project lead đã duyệt phân bố `2, 3, 2, 2, 2, 3, 2, 2`, tạo tổng cộng 18 mẫu `C01-S001` đến `C01-S018`.

Mỗi mẫu:

- có ít nhất một curriculum reference;
- có ba rubric criteria;
- tách criterion thành `supported`, `provisional` và `teacher_judgment`;
- không được trình bày như sample đã được giáo viên phê duyệt.

### Artifact chính

- source registry và Grade-9 reference matrix;
- reference contract;
- workbook audit notes;
- sample template;
- coverage proposal;
- 18 reference-grounded examples;
- teacher review questions;
- coordination log và bốn specialist handoff.

Acceptance gate còn lại là expert teachers review độc lập từng mẫu với quyết định `accept`, `revise` hoặc `reject` kèm lý do.

## 2.2. F01 — fast-track P02/P03/P04/P05 ở mức ứng viên

Experiment: `experiments/20260621_135515/`

Trạng thái report: `SẴN SÀNG ĐỂ GIÁO VIÊN THẨM ĐỊNH` / `ready_for_expert_review`.

F01 tích hợp phần tối thiểu cần thiết của:

- P02: rapid evidence review có truy vết;
- P03: vai trò và workflow giáo viên;
- P04: teacher packet và mẫu minh họa;
- P05: khung task/rubric ứng viên.

F01 không đánh dấu P02–P05 là hoàn thành và không gọi sản phẩm là benchmark v1 hay validated benchmark.

### 2.2.1. Curriculum source package

Feature lưu trực tiếp hai PDF chương trình bắt buộc trong experiment, kèm:

- URL gốc;
- SHA-256;
- số trang;
- vai trò nguồn;
- curriculum reference matrix có vị trí cụ thể.

Điều này giúp gói bàn giao tự chứa đủ nguồn cần đối chiếu và dễ audit hơn.

### 2.2.2. Rapid evidence review

F01 tạo:

- review protocol;
- review log gồm 93 dòng: 17 lượt search và 76 candidate records;
- evidence matrix gồm 28 nguồn nghiên cứu cốt lõi;
- rapid review và các audit note.

Các kết luận chính:

- năng lực giải bài không đồng nghĩa với năng lực gia sư;
- nên chấm theo vector tiêu chí quan sát được thay vì chỉ một total score;
- generic overlap metrics và LLM judge không đủ làm nguồn quyết định duy nhất;
- task lập trình cần correct-work negative controls, nhiều lời giải hợp lệ, expected behavior/test evidence và environment constraints;
- multi-turn evaluation nên xem learner uptake nhưng không được coi uptake là learning gain;
- expert teachers là structural gate, không phải bước tùy chọn.

Review cũng ghi rõ khoảng trống: chưa có benchmark gia sư Tin học lớp 9 tiếng Việt đã được kiểm định; bằng chứng hiện chủ yếu là tiếng Anh, môn Toán hoặc lập trình bậc đại học.

### 2.2.3. Khung benchmark ứng viên

F01 thu gọn tám loại ví dụ C01 thành bảy task ứng viên:

- T01 — giải thích khái niệm theo mức hiểu;
- T02 — hỗ trợ quyết định về thông tin/hành vi số;
- T03 — phản hồi lập luận;
- T04 — lập kế hoạch và góp ý sản phẩm số/mô phỏng;
- T05 — xây dựng thuật toán bằng gợi ý từng bước;
- T06 — chẩn đoán và hỗ trợ sửa thuật toán/chương trình;
- T07 — khám phá nghề nghiệp không định kiến.

T01, T03, T05 và T06 có bằng chứng trực tiếp mạnh hơn. T02, T04 và T07 được giữ ở trạng thái `provisional_low_evidence`.

Khung quy định:

- output chính là `tutor_response`;
- `conversation_history` là danh sách lượt có cấu trúc;
- `critical_failure_flags` là danh sách mã riêng;
- 9 chiều rubric D1–D9, mỗi chiều có anchor 0–5;
- `N/A` tách khỏi điểm 0;
- lỗi nghiêm trọng không được bù bằng điểm cao;
- chưa khóa trọng số, điểm tổng hoặc pass threshold trước teacher calibration.

Traceability matrix nối từng task với curriculum references, literature references, rubric criteria và 18 mẫu C01. Toàn bộ teacher decision hiện vẫn là `pending`.

### 2.2.4. Gói bàn giao cho giáo viên

F01 tạo teacher packet bằng tiếng Việt làm ngôn ngữ chính:

- hướng dẫn bắt đầu;
- guide cho teacher author, independent reviewer và adjudication;
- 18 ví dụ đã ánh xạ vào data contract;
- registry cho nguồn học liệu của ví dụ;
- workbook review form có hướng dẫn, task summary, author form, review form, calibration và open questions.

Nguyên tắc chính:

- tác giả không tự phê duyệt mẫu mình viết;
- reviewer không sửa âm thầm;
- điểm phải có lý do;
- critical failures được ghi riêng;
- bất đồng được chuyển cho adjudicator;
- không sử dụng dữ liệu nhận dạng của học sinh thật.

Ngoài các artifact máy đọc được, feature còn tạo `Khung_benchmark_Tin_hoc_9.docx` để bàn giao cho giáo viên và stakeholders.

### 2.2.5. Validation và giới hạn

F01 đã kiểm tra cấu trúc workbook, tài liệu, references, IDs và traceability bằng Windows `benchmark_env`.

Các con số chính:

- 28 nguồn nghiên cứu;
- 7 task ứng viên;
- 9 rubric dimensions;
- 18 dòng traceability và 18 ví dụ;
- hai PDF chương trình có đúng 85 và 57 trang;
- 17 agent tests từ P01 vẫn pass.

DOCX từng được render và kiểm tra trực quan ở bản trước khi mở rộng đủ 18 ví dụ. Sau khi mở rộng, cấu trúc được kiểm tra bằng `python-docx`, nhưng vòng render trực quan mới chưa hoàn tất do thiếu `pdf2image` và Word COM bị treo. Excel trên máy kia cũng báo hết hạn license khi gọi chức năng xuất ảnh/PDF.

Do đó, artifact hiện là candidate package sẵn sàng cho expert review, chưa phải artifact đã được teacher-validated.

## 2.3. Cập nhật trạng thái dự án trên feature branch

Commit `c76bc20` cập nhật root docs để phản ánh F01:

- `README.md` chuyển current status từ “chỉ có P01” sang “đã có candidate framework và teacher handoff chờ expert review”;
- bổ sung link tới F01 report và DOCX;
- nhấn mạnh F01 artifacts không phải production benchmark data;
- `ARCHITECTURE.md` thêm các component F01: literature, curriculum sources, candidate framework, teacher packet và DOCX;
- dependency direction cho phép P02/P03/P04 tiếp tục consume hoặc revise F01, còn P05–P07 vẫn sở hữu durable benchmark/dataset/evaluation artifacts;
- limitation được cập nhật: taxonomy và rubric F01 vẫn provisional, dataset schema và evaluation metrics chưa được triển khai.

## 3. Bức tranh tổng thể sau hai nhóm thay đổi

```text
main @ 408405b
└── P01 hoàn tất: specialist infrastructure + cross-platform validation
    └── feature/C01_P02_P03 @ c76bc20
        ├── C01: curriculum grounding + 18 provisional examples
        └── F01: rapid evidence review
            + 7-task candidate framework
            + 9-dimension rubric
            + teacher packet/workbooks/DOCX
            + status READY_FOR_EXPERT_REVIEW
```

Điểm thay đổi quan trọng nhất là dự án đã đi từ nền tảng agent sang một candidate benchmark package có curriculum grounding và literature traceability. Tuy nhiên, branch vẫn giữ đúng ranh giới khoa học: chưa có expert-teacher validation, chưa có production dataset, chưa có evaluation pipeline và chưa được phép gọi artifact là benchmark chính thức.

## 4. Những việc còn mở trước khi cân nhắc merge hoặc coi F01 là baseline

1. Expert teachers review 18 mẫu và bảy task với quyết định/rationale có truy vết.
2. Hiệu chuẩn anchor 0–5, critical failures, alternative valid responses và disagreement workflow.
3. Quyết định giữ/sửa/loại T02, T04 và T07 do bằng chứng trực tiếp còn yếu.
4. Xác nhận môi trường lập trình, công cụ, thuật ngữ và điều kiện lớp học địa phương.
5. Hoàn tất visual render check cho DOCX sau khi đã chứa đủ 18 ví dụ; kiểm tra workbook trực quan trên môi trường Office hoạt động bình thường.
6. Review hai helper script experiment trước khi merge nếu chúng được giữ lại; chúng là script tạo/chỉnh artifact theo experiment, không phải production tooling.
7. Quyết định F01 sẽ được merge nguyên trạng, chọn lọc artifact, hay tiếp tục phát triển trên feature branch sau teacher review.

## 5. Kết luận ngắn

- `main` mới đã đóng hoàn toàn P01 và chuẩn hóa vận hành trên Windows/Linux.
- `feature/C01_P02_P03` đã tạo curriculum-grounded evidence package và một khung benchmark ứng viên khá đầy đủ để giáo viên thẩm định.
- Giá trị lớn nhất của feature là chuỗi truy vết `curriculum + literature → task/rubric → example → teacher decision`.
- Gate quyết định tiếp theo thuộc về expert teachers; không nên biến trạng thái `ready_for_expert_review` thành `validated` chỉ bằng kiểm tra kỹ thuật.
