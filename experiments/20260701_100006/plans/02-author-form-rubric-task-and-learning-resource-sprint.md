# Plan 02 — Rà soát phiếu tác giả, rubric/task và học liệu cho sprint sau họp HNMU

Trạng thái: `APPROVED` — người phụ trách dự án đã duyệt tiếp tục triển khai các bước còn lại sau Bước 1 trong yêu cầu ngày 04/07/2026; mọi artifact Bước 2–7 vẫn là bản nháp chờ UET/HNMU xác nhận  
Ngày tạo: 04/07/2026  
Experiment: `20260701_100006`  
Người lập plan: orchestrator  
Phạm vi: lập kế hoạch cho 5 việc cần làm ngay sau phản hồi ngày 04/07/2026

## 1. Lý do cần plan này

Sau cuộc họp ngày 01/07/2026 giữa UET, giáo sư hướng dẫn và các thầy cô HNMU, dự án đã chuyển sang giai đoạn rất gấp: cần dùng **phiếu tác giả** để tạo dữ liệu thật, đồng thời vẫn phải giữ được tính truy vết và tính đúng đắn sư phạm.

Về nguyên tắc, cách làm chặt chẽ nên là:

```text
task → rubric/mã lỗi nghiêm trọng → metadata trong phiếu tác giả
```

Tuy nhiên, vì tiến độ đang bị ép rất mạnh, hướng xử lý tạm thời được chấp nhận là:

```text
metadata trong phiếu tác giả → rubric/mã lỗi nghiêm trọng → task
```

Plan này dùng để biến hướng xử lý tạm thời đó thành một sprint có kiểm soát, tránh tình trạng vừa chạy nhanh vừa làm lệch kiến trúc benchmark.

## 2. Mục tiêu

Hoàn thành 5 nhóm việc trước mắt:

1. Kiểm tra phiếu tác giả.
2. Chốt rubric và mã lỗi nghiêm trọng ở mức bản nháp có thể gửi HNMU xác nhận.
3. Chuẩn hóa mã task ở mức đủ dùng cho giáo viên tạo dữ liệu.
4. Chuẩn hóa chủ đề Tin học lớp 6–9.
5. Rà soát học liệu và lập danh mục học liệu/đoạn học liệu v0.

Trong đó:

- việc 1–3 chạy tuần tự;
- việc 4–5 có thể chạy song song với việc 1–3;
- mọi kết luận chuyên môn/sư phạm vẫn cần HNMU xác nhận;
- chưa triển khai web thu thập dữ liệu;
- chưa triển khai database học liệu production;
- chưa chốt benchmark chính thức.

## 3. Căn cứ đầu vào

### 3.1. Tài liệu trong repo

- `experiments/20260701_100006/reports/hnmu-author-form-meeting-structured-notes-20260701.md`
- `experiments/20260701_100006/metadata.yaml`
- `experiments/20260620_115236/roadmap.md`
- `README.md`
- `ARCHITECTURE.md`

### 3.2. Tài liệu cần lấy từ Google Drive hoặc nguồn ngoài repo

Cần người phụ trách dự án cung cấp link/quyền truy cập trước khi triển khai đầy đủ:

- Google Sheets `review_form`, đặc biệt sheet `phiếu tác giả`;
- thư mục Drive toàn dự án;
- experiment Drive `20260701_100006`;
- bản copy `literature_review`;
- bản copy `curriculum_sources`;
- học liệu SGK Tin học lớp 6, 7, 8, 9 trên trang tập huấn;
- nếu có: tài liệu HNMU đã chỉnh sửa, nhận xét, hoặc ví dụ mẫu.

### 3.3. Câu hỏi cần người phụ trách dự án xác nhận sớm

- Deadline KSE chính xác là ngày nào và yêu cầu tối thiểu để nộp là gì?
- Mốc số lượng mẫu cần báo cáo trước 15/07/2026 là mẫu thô, mẫu đã chấm hay mẫu đạt chuẩn?
- Google Sheets nào là bản phiếu tác giả đang được coi là bản chốt?
- HNMU có yêu cầu giữ nguyên tên trường nào trong phiếu tác giả không?

## 4. Phạm vi file

### 4.1. Được phép tạo/sửa trong plan này

Chỉ trong experiment hiện tại:

```text
experiments/20260701_100006/
```

Nguyên tắc của plan này: **mọi thư mục và file được tạo phải có vai trò rõ ràng**. Nếu trong lúc triển khai phát sinh file mới ngoài danh sách dưới đây, người thực hiện phải cập nhật plan hoặc handoff để ghi rõ:

- file/thư mục đó dùng để làm gì;
- vì sao cần tạo nó;
- ai sẽ đọc hoặc sử dụng nó;
- artifact nào là bản nháp, artifact nào có thể gửi HNMU xác nhận.

#### 4.1.1. Thư mục dự kiến tạo

| Thư mục | Vai trò | Lý do tạo | Người dùng chính |
|---|---|---|---|
| `author_form/` | Lưu toàn bộ kết quả rà soát **phiếu tác giả**: ý nghĩa từng trường, ai điền, trường bắt buộc/tùy chọn, ví dụ điền đúng/sai. | Phiếu tác giả là điểm bắt đầu của hướng bottom-up. Cần tách riêng để tránh trộn nhận xét về biểu mẫu với đặc tả rubric/task. | UET, `teacher-collaboration-designer`, `benchmark-specification-designer`, HNMU khi cần xác nhận trường. |
| `benchmark_spec/` | Lưu đặc tả benchmark bản nháp: rubric, mã lỗi nghiêm trọng, task, mã task, quan hệ truy vết. | Đây là lớp đặc tả lõi của benchmark. Cần tách khỏi phiếu tác giả và học liệu để dễ review, version hóa và gửi HNMU xác nhận từng phần. | UET, `benchmark-specification-designer`, `research-methodologist`, HNMU. |
| `learning_resources/` | Lưu các artifact về học liệu: danh mục học liệu, mã học liệu, đoạn học liệu, nhóm chủ đề lớp 6–9, tiền kiến thức lớp 6–8 cho lớp 9. | Học liệu là căn cứ bắt buộc của mẫu benchmark. Cần một vùng riêng để học liệu được xử lý song song mà không làm nhiễu phần rubric/task. | UET, `learning-resource-curator`, `benchmark-specification-designer`, HNMU. |
| `drive_snapshot/` | Lưu bản snapshot đầu vào lấy từ Google Drive của experiment `20260701_100006`: manifest folder/file, các bản export/download và bản trích xuất audit của `review_form.xlsx`. | Bước 0/Bước 1 cần đóng băng đúng phiên bản input đã dùng để tránh việc Google Drive thay đổi sau này làm mất khả năng truy vết. Snapshot này không thay thế Drive gốc và không phải database học liệu production. | UET, orchestrator, các specialist ở bước sau khi cần kiểm tra nguồn đầu vào. |
| `handoffs/` | Lưu bàn giao của từng specialist hoặc single-agent fallback: input đã đọc, output đã tạo, uncertainty, quyết định cần người xác nhận. | P01 yêu cầu mọi delegation có handoff quan sát được. Thư mục này giúp truy vết agent nào làm gì, dùng đầu vào nào, và còn vướng gì. | Orchestrator, người phụ trách dự án, specialist tiếp theo nhận việc. |
| `coordination/` | Lưu event log dạng append-only cho việc bắt đầu/kết thúc delegation hoặc single-agent fallback. | `AGENTS.md` yêu cầu ghi coordination events. Thư mục này tách log vận hành khỏi handoff đọc bằng mắt. | Orchestrator, người phụ trách dự án, auditor sau này. |
| `reports/` | Lưu báo cáo tổng hợp sprint, câu hỏi mở gửi UET/HNMU, ghi chú input đã dùng và trạng thái hoàn thành. | Reports là lớp đọc nhanh cho người điều phối và giáo viên; không nên bắt người đọc phải mở từng CSV/đặc tả kỹ thuật. | Người phụ trách dự án, giáo sư, HNMU, orchestrator. |

#### 4.1.2. File/artifact dự kiến tạo

| File/artifact | Vai trò | Lý do tạo | Người dùng chính |
|---|---|---|---|
| `drive_snapshot/README.md` | Giải thích cách đọc snapshot Drive, bản nào là raw download, bản nào là export đọc được, và giới hạn của snapshot. | Tránh hiểu nhầm snapshot là nguồn chân lý mới hoặc là bản mirror đầy đủ thay thế Google Drive. | UET, orchestrator, specialist tiếp theo. |
| `drive_snapshot/drive_file_manifest.csv` | Manifest toàn bộ folder/file đã thấy trong Drive experiment: mã Drive, tên, loại file, đường dẫn Drive, đường dẫn local, trạng thái tải, kích thước và SHA-256. | Cần một bảng audit để biết chính xác Bước 1 dùng input nào và các bước sau nên đọc file nào. | UET, orchestrator, auditor, specialist tiếp theo. |
| `drive_snapshot/files/**` | Bản tải/export local của các file trong Drive experiment, giữ cấu trúc gần với folder gốc: `teacher_packet`, `literature_review`, `curriculum_sources`. | Cần đóng băng input tối thiểu trong repo để không phụ thuộc hoàn toàn vào trạng thái sống của Google Drive. | UET, orchestrator, specialist tiếp theo. |
| `drive_snapshot/review_form.extracted.txt` | Bản trích xuất text audit từ `drive_snapshot/files/teacher_packet/review_form.xlsx`. | `review_form.xlsx` là Office file nên không đọc được bằng Google Sheets range API. Bản text giúp review nhanh và kiểm tra lại các trường đã phân tích. | UET, `teacher-collaboration-designer`, `benchmark-specification-designer`. |
| `author_form/author_form_field_review.md` | Bản giải thích bằng văn xuôi về từng trường trong phiếu tác giả: ý nghĩa, cách hiểu, điểm dễ nhầm, đề xuất sửa. | Giáo viên và người phụ trách dự án cần đọc được lý do từng trường tồn tại, không chỉ nhìn một bảng cột khô. File này phục vụ review bằng mắt và thảo luận với HNMU. | UET, HNMU, `teacher-collaboration-designer`. |
| `author_form/author_form_field_matrix.csv` | Bảng có cấu trúc cho từng trường: tên trường, mô tả, ai điền, bắt buộc/tùy chọn, trạng thái, liên hệ với rubric/task/học liệu. | Cần một bảng sạch để lọc, so sánh, cập nhật và sau này có thể nhập vào công cụ hoặc chuyển thành schema. | UET, orchestrator, `benchmark-specification-designer`. |
| `benchmark_spec/rubric_specification.md` | Đặc tả rubric bản nháp: tiêu chí chấm, mức điểm, dấu hiệu quan sát được, điểm cần HNMU xác nhận. | Rubric là cầu nối giữa phiếu tác giả và việc chấm mẫu. Cần bản văn bản dễ đọc trước khi chuyển sang bảng/validator. | UET, HNMU, `benchmark-specification-designer`, `teacher-collaboration-designer`. |
| `benchmark_spec/serious_error_catalog.md` | Danh mục mã lỗi nghiêm trọng: mô tả lỗi, ví dụ, phạm vi áp dụng, hành động gợi ý. | Cần tách lỗi nghiêm trọng khỏi rubric thường để tránh hiểu nhầm “cứ có lỗi nghiêm trọng là mọi rubric đều 0”. | UET, HNMU, `benchmark-specification-designer`. |
| `benchmark_spec/rubric_error_mapping.csv` | Bảng nối mã lỗi nghiêm trọng với rubric bị ảnh hưởng và hành động chấm/duyệt tương ứng. | Mối quan hệ lỗi–rubric cần có dạng bảng để kiểm tra nhất quán và tránh xử lý cảm tính giữa các giáo viên chấm. | UET, HNMU, orchestrator, validator tương lai. |
| `benchmark_spec/benchmark_task_specification.md` | Đặc tả task bản nháp: mã task, tên task, định nghĩa, phạm vi, đầu vào/đầu ra, ví dụ đúng/sai. | Sau khi đi bottom-up từ phiếu tác giả và rubric, cần quay lại task để giữ tư duy hệ thống và tránh task bị suy ra lỏng lẻo. | UET, HNMU, `benchmark-specification-designer`. |
| `benchmark_spec/task_code_registry.csv` | Registry mã task: mã, tên task, trạng thái, mô tả ngắn, quan hệ với rubric và trường phiếu tác giả. | Trường `mã task` trong phiếu tác giả do UET cung cấp. Cần registry ổn định để giáo viên không tự đặt mã hoặc dùng sai mã. | UET, giáo viên HNMU, orchestrator. |
| `benchmark_spec/provenance_matrix_v0.csv` | Ma trận truy vết bản v0 giữa task, rubric, mã lỗi, trường phiếu tác giả, căn cứ nghiên cứu và căn cứ học liệu. | Benchmark cần giải thích được vì sao task/rubric tồn tại. File này là xương sống để trả lời câu hỏi “căn cứ ở đâu?”. | UET, giáo sư, HNMU, `research-methodologist`, `learning-resource-curator`. |
| `learning_resources/topic_map_grade6_9.md` | Bản giải thích nhóm chủ đề Tin học lớp 6–9 bằng văn xuôi, kèm phần cần HNMU xác nhận. | Tên chủ đề giữa các lớp có thể lệch nhau; cần bản dễ đọc để HNMU review nội hàm chứ không chỉ review mã/bảng. | HNMU, UET, `learning-resource-curator`. |
| `learning_resources/topic_map_grade6_9.csv` | Bảng mapping chủ đề lớp 6–9: lớp, bài/chủ đề, nhóm chủ đề thống nhất, trạng thái xác nhận. | Dạng bảng giúp lọc theo lớp/chủ đề và làm đầu vào cho task/rubric hoặc công cụ tra cứu sau này. | UET, `learning-resource-curator`, `benchmark-specification-designer`. |
| `learning_resources/learning_resource_source_map.csv` | Danh mục học liệu gốc: mã học liệu, tên nguồn, lớp, loại học liệu, URL/file, trạng thái xử lý. | Mỗi mẫu benchmark cần tham chiếu học liệu. File này là bản đồ nguồn để mã học liệu truy hồi được về nguồn thật. | UET, HNMU, `learning-resource-curator`. |
| `learning_resources/learning_resource_fragments_v0.csv` | Bảng đoạn học liệu v0: mã đoạn, mã học liệu gốc, trang/mục/ghi chú vị trí, trạng thái review. | Giáo viên cần trích đúng đoạn/bài/mục khi tạo mẫu. Fragment giúp tham chiếu cụ thể hơn URL hoặc tên sách chung. | UET, HNMU, `learning-resource-curator`, `benchmark-specification-designer`. |
| `learning_resources/grade9_prerequisite_map.csv` | Bảng nối nội dung Tin học lớp 9 với tiền kiến thức lớp 6–8 liên quan. | Benchmark tập trung lớp 9 nhưng cần xử lý học sinh thiếu nền. File này giúp xác định khi nào cần viện dẫn kiến thức lớp 6–8. | HNMU, UET, `learning-resource-curator`, `benchmark-specification-designer`. |
| `learning_resources/learning_resource_open_questions.md` | Danh sách câu hỏi mở về học liệu/chủ đề/tiền kiến thức cần HNMU xác nhận. | Không nên để agent tự chốt nội dung sư phạm. File này gom các điểm cần hỏi HNMU thay vì rải rác trong nhiều bảng. | HNMU, UET, `learning-resource-curator`. |
| `benchmark_spec/benchmark_open_questions.md` | Danh sách câu hỏi mở về task, rubric, mã lỗi nghiêm trọng và truy vết cần giáo sư/HNMU quyết định. | Các điểm chưa đủ căn cứ cần được tách riêng để cuộc họp review tập trung, không bị lẫn với phần đã tương đối ổn. | Giáo sư, HNMU, UET, `benchmark-specification-designer`. |
| `benchmark_spec/targeted_research_evidence_notes.md` | Ghi chú rà soát nghiên cứu có mục tiêu cho các claim nhạy cảm trong rubric/task/mã lỗi. | Sprint này không làm literature review rộng, nhưng vẫn cần kiểm tra những điểm có nguy cơ thiếu căn cứ khoa học. | UET, `research-methodologist`, `benchmark-specification-designer`. |
| `reports/sprint-02-summary.md` | Báo cáo tổng hợp cuối sprint: đã làm gì, artifact nào tạo ra, còn thiếu gì, cần ai quyết định gì. | Người phụ trách dự án cần một bản đọc nhanh để quyết định bước tiếp theo mà không phải mở từng file chi tiết. | Người phụ trách dự án, giáo sư, orchestrator. |
| `reports/hnmu-open-questions.md` | Danh sách câu hỏi cần gửi HNMU, gom từ phiếu tác giả, học liệu, rubric, task. | HNMU cần nhận câu hỏi rõ, ít trùng lặp, viết bằng ngôn ngữ dễ hiểu. File này là bản chắt lọc từ các open questions kỹ thuật. | HNMU, UET, `teacher-collaboration-designer`. |
| `handoffs/*.md` | Handoff riêng cho từng specialist/task: nhiệm vụ, input, allowed writes, output, uncertainty, validation. | Cần tuân thủ yêu cầu quan sát được của hệ thống agent; cũng giúp specialist sau không phải đoán specialist trước đã làm gì. | Orchestrator, người phụ trách dự án, specialist kế tiếp. |
| `coordination/delegations.jsonl` | Nhật ký sự kiện delegation/fallback: started, completed, failed. | Cần log máy đọc được để biết khi nào Bước 1 bắt đầu/kết thúc, agent nào được dùng, output nằm ở đâu. | Orchestrator, người phụ trách dự án, auditor sau này. |

### 4.2. Không được sửa trong plan này

- Không sửa skill/adapter của specialist agent.
- Không sửa validator trong `agents/*/scripts/`.
- Không sửa artifact cũ trong `experiments/20260620_115236/` hoặc `experiments/20260621_*`.
- Không sửa trực tiếp Google Sheets nếu chưa có yêu cầu rõ.
- Không triển khai web, database production hoặc evaluation pipeline.
- Không chốt task/rubric/mã lỗi như bản chính thức nếu chưa có HNMU xác nhận.

## 5. Phân công specialist agent

### 5.1. Nguyên tắc chung

- Mặc định mỗi specialist chỉ chạy một instance cho một task.
- Không spawn nhiều bản sao cùng một specialist nếu chưa có xác nhận riêng của người phụ trách dự án.
- Không dùng `codex exec`, `claude -p`, tiến trình nền hoặc agent ẩn.
- Nếu runtime không cho thấy specialist thread, dùng single-agent fallback trong parent thread và ghi rõ trong handoff.
- Mỗi specialist chỉ ghi vào đường dẫn được giao.
- Mọi kết luận cần tách rõ: bằng chứng, suy luận, và phần cần HNMU xác nhận.

### 5.2. Vai trò từng specialist

| Specialist | Cấu hình đã biết | Vai trò trong plan này | Ghi chú ranh giới |
|---|---|---|---|
| `teacher-collaboration-designer` | Adapter chưa pin model; reasoning effort `high` | Rà soát phiếu tác giả theo góc nhìn giáo viên: trường nào dễ hiểu, ai điền, trường nào bắt buộc, ví dụ đúng/sai. | Không tự chốt task/rubric. Không yêu cầu giáo viên làm việc kỹ thuật. |
| `learning-resource-curator` | `gpt-5.4-mini`, reasoning effort `medium` | Chuẩn hóa chủ đề Tin học 6–9, rà soát học liệu, lập mã học liệu/đoạn học liệu v0. | Không tự quyết định nội dung sư phạm cuối cùng. Không thiết kế database production. |
| `benchmark-specification-designer` | `gpt-5.4-mini`, reasoning effort `high` | Chốt bản nháp rubric, mã lỗi nghiêm trọng, quan hệ mã lỗi–rubric, mã task và truy vết task–rubric–metadata–học liệu. | Không chốt chính thức nếu thiếu HNMU xác nhận. Không sửa evidence/resource mapping để làm đẹp đặc tả. |
| `research-methodologist` | `gpt-5.4-mini`, reasoning effort `medium` | Rà soát có mục tiêu các điểm rubric/task/mã lỗi cần căn cứ nghiên cứu. | Không làm literature review rộng trong sprint gấp này nếu chưa có yêu cầu riêng. |

## 6. Luồng triển khai đề xuất

```text
                      ┌─ learning-resource-curator
                      │   ├─ topic_map_grade6_9
                      │   ├─ learning_resource_source_map
                      │   └─ grade9_prerequisite_map
                      │
teacher-collaboration-designer
   └─ author_form_field_review
                      │
                      ▼
benchmark-specification-designer
   ├─ rubric_specification
   ├─ serious_error_catalog
   ├─ rubric_error_mapping
   └─ task_code_registry
                      │
                      ▼
research-methodologist
   └─ targeted_evidence_check
                      │
                      ▼
benchmark-specification-designer
   └─ benchmark_task_specification + provenance_matrix_v0
                      │
                      ▼
teacher-collaboration-designer
   └─ hướng dẫn ngắn cho HNMU nếu cần gửi ngay
```

## 7. Các bước chi tiết

### Bước 0 — Chuẩn bị dữ liệu đầu vào

Mục tiêu: đảm bảo các specialist không làm trên bản phiếu/học liệu cũ hoặc sai.

Việc cần làm:

1. Nhận quyền truy cập Google Drive từ người phụ trách dự án.
2. Xác định bản `review_form` đang được coi là bản chốt.
3. Tải hoặc xuất bản phiếu tác giả sang định dạng có thể audit trong repo, nếu được phép.
4. Liệt kê nguồn học liệu SGK lớp 6–9 và trạng thái xử lý.
5. Ghi lại mọi file/link đã dùng trong `reports/sprint-02-summary.md`.

Đầu ra:

- danh sách input đã xác nhận;
- danh sách input còn thiếu;
- ghi chú bản nào là bản chốt.
- snapshot Drive local trong `drive_snapshot/`, gồm manifest và bản tải/export của các file trong experiment Drive.

### Bước 1 — Kiểm tra phiếu tác giả

Specialist chính: `teacher-collaboration-designer`  
Specialist hỗ trợ: `benchmark-specification-designer`, nếu được người phụ trách dự án xác nhận chạy song song hoặc rà soát sau.

Mục tiêu:

- xác định từng trường trong phiếu tác giả dùng để làm gì;
- xác định ai điền: UET, HNMU, hay hệ thống/agent hỗ trợ;
- xác định trường bắt buộc, trường tùy chọn, trường có thể để trống ở vòng đầu;
- phát hiện trường mơ hồ, trùng nghĩa, thiếu ví dụ hoặc có nguy cơ làm lệch rubric/task.

Đầu ra:

```text
author_form/author_form_field_review.md
author_form/author_form_field_matrix.csv
reports/hnmu-open-questions.md
```

Tiêu chí hoàn thành:

- mọi trường trong phiếu tác giả đều có ý nghĩa và người chịu trách nhiệm điền;
- có danh sách trường cần HNMU xác nhận;
- có ít nhất một ví dụ điền đúng và một ví dụ điền sai cho các trường dễ nhầm;
- có ghi chú riêng cho trường `mã task`, `lịch sử trao đổi`, `điểm đánh giá`, `mã lỗi nghiêm trọng`, `mã học liệu`.

### Bước 2 — Chuẩn hóa chủ đề Tin học 6–9

Specialist chính: `learning-resource-curator`

Mục tiêu:

- lập nhóm chủ đề thống nhất xuyên suốt Tin học THCS;
- ghi rõ chủ đề lớp 9 liên hệ với nội dung lớp 6–8 nào;
- tách phần thấy trực tiếp từ SGK và phần suy luận cần HNMU xác nhận.

Đầu ra:

```text
learning_resources/topic_map_grade6_9.md
learning_resources/topic_map_grade6_9.csv
learning_resources/grade9_prerequisite_map.csv
learning_resources/learning_resource_open_questions.md
```

Tiêu chí hoàn thành:

- có danh sách chủ đề thống nhất lớp 6–9;
- mỗi mapping có trạng thái: `draft`, `needs_hnmu_review`, `confirmed` hoặc `retired`;
- không tự chốt nội dung sư phạm nếu chỉ dựa vào suy luận;
- câu hỏi cần HNMU xác nhận được tách riêng.

### Bước 3 — Rà soát học liệu

Specialist chính: `learning-resource-curator`

Mục tiêu:

- lập danh mục học liệu SGK/nguồn HNMU dùng cho benchmark;
- đặt mã học liệu v0;
- nếu đủ dữ liệu, chia một số đoạn học liệu/fragment v0 để giáo viên có thể trích dẫn;
- đảm bảo học liệu có thể truy hồi về nguồn gốc.

Đầu ra:

```text
learning_resources/learning_resource_source_map.csv
learning_resources/learning_resource_fragments_v0.csv
```

Tiêu chí hoàn thành:

- mỗi học liệu có mã riêng và nguồn truy hồi;
- mỗi fragment, nếu có, trỏ về học liệu gốc;
- không tự bịa trang, mục, file hash hoặc trạng thái xác nhận;
- có ghi rõ phần nào chưa OCR/chưa kiểm tra/chưa HNMU xác nhận.

### Bước 4 — Chốt rubric và mã lỗi nghiêm trọng bản nháp

Specialist chính: `benchmark-specification-designer`  
Specialist hỗ trợ: `research-methodologist` cho rà soát bằng chứng có mục tiêu.

Mục tiêu:

- biến các trường đánh giá trong phiếu tác giả thành rubric có thể chấm;
- lập danh mục mã lỗi nghiêm trọng;
- xác định mã lỗi nào ảnh hưởng đến rubric nào;
- xác định hành động gợi ý khi gặp lỗi: loại, yêu cầu sửa, hạ điểm, hoặc cần phân xử;
- đánh dấu rõ phần cần HNMU xác nhận.

Đầu ra:

```text
benchmark_spec/rubric_specification.md
benchmark_spec/serious_error_catalog.md
benchmark_spec/rubric_error_mapping.csv
benchmark_spec/benchmark_open_questions.md
```

Tiêu chí hoàn thành:

- mỗi rubric có định nghĩa ngắn, dấu hiệu quan sát được, mức điểm hoặc hướng chấm;
- mỗi mã lỗi nghiêm trọng có mô tả, ví dụ, rubric bị ảnh hưởng và hành động gợi ý;
- mọi điểm chưa có căn cứ nghiên cứu/học liệu phải gắn nhãn cần xác nhận;
- không tuyên bố đây là rubric chính thức nếu HNMU chưa duyệt.

### Bước 5 — Rà soát bằng chứng nghiên cứu có mục tiêu

Specialist chính: `research-methodologist`

Mục tiêu:

- kiểm tra nhanh các rubric/task/mã lỗi nhạy cảm có căn cứ nghiên cứu hay không;
- không mở literature review rộng nếu chưa có yêu cầu riêng;
- tách rõ bằng chứng, suy luận, và câu hỏi mở.

Đầu ra:

```text
benchmark_spec/targeted_research_evidence_notes.md
```

Tiêu chí hoàn thành:

- mỗi claim quan trọng được gắn nguồn hoặc nhãn suy luận/câu hỏi mở;
- có cảnh báo nếu bằng chứng đến từ môn học khác, cấp học khác hoặc bối cảnh đánh giá khác;
- có danh sách điểm nên hỏi HNMU thay vì để agent tự quyết.

### Bước 6 — Chuẩn hóa mã task

Specialist chính: `benchmark-specification-designer`

Mục tiêu:

- tạo danh sách mã task đủ ổn định để giáo viên dùng trong phiếu tác giả;
- định nghĩa ngắn từng task;
- liên kết task với rubric, mã lỗi, học liệu và trường phiếu tác giả;
- nêu ví dụ đúng/sai cho từng task nếu đủ thời gian.

Đầu ra:

```text
benchmark_spec/benchmark_task_specification.md
benchmark_spec/task_code_registry.csv
benchmark_spec/provenance_matrix_v0.csv
```

Tiêu chí hoàn thành:

- mỗi task có mã, tên, định nghĩa, phạm vi, đầu vào, đầu ra;
- mỗi task có liên kết đến rubric tương ứng;
- task chưa đủ căn cứ phải được đánh dấu `needs_hnmu_review`;
- mã task không trùng và không phụ thuộc vào thứ tự nhập mẫu ngẫu nhiên.

### Bước 7 — Gói tóm tắt gửi người phụ trách dự án/HNMU

Specialist chính: `teacher-collaboration-designer`

Mục tiêu:

- chuyển các kết quả kỹ thuật thành bản tóm tắt dễ đọc;
- không bắt giáo viên hiểu schema, CSV, Git hoặc pipeline;
- nêu rõ phần nào HNMU cần xác nhận.

Đầu ra:

```text
reports/sprint-02-summary.md
reports/hnmu-open-questions.md
```

Tiêu chí hoàn thành:

- có danh sách quyết định cần HNMU xác nhận;
- có hướng dẫn ngắn cho giáo viên nếu cần bắt đầu tạo mẫu ngay;
- không trình bày artifact nháp như bản chính thức.

## 8. Chạy song song và điểm cần duyệt

### 8.1. Chạy song song được khuyến nghị

Có thể chạy song song hai specialist khác nhau:

1. `teacher-collaboration-designer`
   - task: kiểm tra phiếu tác giả;
   - allowed writes: `author_form/`, `reports/`, `handoffs/`.
2. `learning-resource-curator`
   - task: chuẩn hóa chủ đề Tin học 6–9 và rà soát học liệu;
   - allowed writes: `learning_resources/`, `reports/`, `handoffs/`.

Hai việc này ít chồng chéo, nên có thể chạy đồng thời nếu người phụ trách dự án xác nhận.

### 8.2. Chạy song song cần cân nhắc

Có thể thêm `benchmark-specification-designer` chạy sớm để rà soát phiếu tác giả theo góc nhìn rubric/task, nhưng cần giới hạn rõ:

- `teacher-collaboration-designer`: xem phiếu tác giả có dễ hiểu và dễ dùng cho giáo viên không;
- `benchmark-specification-designer`: xem các trường metadata có đủ để phục vụ rubric/task không.

Nếu không giới hạn rõ, hai specialist dễ nhận xét trùng hoặc kéo phiếu tác giả theo hai hướng khác nhau.

### 8.3. Không khuyến nghị ở vòng này

- Không spawn nhiều bản sao của `learning-resource-curator` theo từng khối lớp, trừ khi người phụ trách dự án duyệt rõ input split và merge plan.
- Không spawn nhiều bản sao của `benchmark-specification-designer`.
- Không mở literature review rộng bằng nhiều `research-methodologist` vì rủi ro token cao và deadline gấp.

## 9. Handoff và phối hợp

Mỗi specialist, nếu được spawn, phải có handoff riêng trong:

```text
experiments/20260701_100006/handoffs/
```

Handoff tối thiểu gồm:

- specialist name;
- model và reasoning effort nếu biết;
- task được giao;
- input đã đọc;
- allowed writes;
- artifact đã tạo;
- điều chưa chắc;
- quyết định cần UET/HNMU xác nhận;
- validator/test đã chạy nếu có.

Nếu runtime không hỗ trợ native specialist visibility, ghi rõ dùng single-agent fallback.

## 10. Validation

Plan này là plan tạo artifact nghiên cứu/học liệu, không sửa code. Validation tương ứng:

1. Kiểm tra Markdown/CSV đọc được bằng Python trong `benchmark_env`.
2. Nếu tạo artifact học liệu dạng CSV, chạy:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  agents/learning-resource-curator/scripts/validate_learning_resource_registry.py \
  <artifact>
```

3. Nếu tạo artifact đặc tả benchmark dạng CSV, chạy:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  agents/benchmark-specification-designer/scripts/validate_benchmark_specification.py \
  <artifact>
```

4. Nếu tạo gói hướng dẫn giáo viên, chạy validator phù hợp nếu artifact khớp schema:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  agents/teacher-collaboration-designer/scripts/validate_teacher_packet.py \
  <artifact_or_folder>
```

5. Chỉ chạy `pytest tests/agents -q` nếu có sửa code, skill, adapter hoặc validator. Plan này không dự kiến sửa các phần đó.

## 11. Acceptance criteria

Plan được coi là hoàn thành khi có đủ:

- bản rà soát phiếu tác giả;
- bảng trường phiếu tác giả, người điền, trạng thái, ghi chú;
- rubric bản nháp;
- danh mục mã lỗi nghiêm trọng bản nháp;
- bảng quan hệ mã lỗi–rubric;
- danh sách mã task bản nháp;
- bảng chủ đề Tin học 6–9;
- danh mục học liệu/mã học liệu v0;
- danh sách câu hỏi cần HNMU xác nhận;
- report tóm tắt cho người phụ trách dự án.

Các artifact không cần được coi là chính thức; chỉ cần đủ rõ để UET/HNMU duyệt tiếp và để giáo viên không bị mơ hồ khi bắt đầu tạo dữ liệu.

## 12. Rủi ro và cách giảm nhẹ

| Rủi ro | Hệ quả | Cách giảm nhẹ |
|---|---|---|
| Deadline KSE quá gần | Không đủ thời gian vừa làm dữ liệu vừa viết paper. | Hỏi lại giáo sư về deadline và mức tối thiểu; tách mẫu thô/mẫu đã chấm/mẫu đạt chuẩn. |
| Bottom-up làm méo task/rubric | Metadata hiện tại ép benchmark theo biểu mẫu chưa tối ưu. | Ghi nhãn trường tạm thời; sau phiếu tác giả phải quay lại rubric/task. |
| Học liệu chưa xử lý đủ | Task/rubric thiếu căn cứ chương trình. | Chạy learning-resource stream song song; dùng trạng thái `needs_hnmu_review`. |
| Specialist chồng chéo | Nhận xét trùng hoặc mâu thuẫn. | Chia ranh giới theo vai trò; mỗi agent có allowed writes riêng. |
| Fan-out tốn token | Chi phí tăng, khó hợp nhất kết quả. | Không spawn nhiều bản sao cùng specialist nếu chưa được duyệt rõ. |
| Giáo viên khó hiểu artifact kỹ thuật | Phiếu tác giả khó dùng, dữ liệu nhập không đồng nhất. | `teacher-collaboration-designer` chuyển thành hướng dẫn ngắn, ví dụ đúng/sai. |

## 13. Cần người phụ trách dự án duyệt trước khi triển khai

Để triển khai plan này, cần người phụ trách dự án xác nhận:

1. Duyệt plan này hay cần sửa trước.
2. Có cho chạy song song hai specialist khác nhau ở bước đầu không:
   - `teacher-collaboration-designer`;
   - `learning-resource-curator`.
3. Có muốn thêm `benchmark-specification-designer` vào vòng rà soát phiếu tác giả sớm không.
4. Có link/quyền truy cập Google Drive và bản `review_form` chốt.
5. Có chốt tạm rằng vòng này bỏ qua phân tích web thu thập dữ liệu không.

Khi chưa có các xác nhận trên, không triển khai artifact nghiệp vụ và không spawn specialist.
