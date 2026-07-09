# Plan 01 — Mở rộng specialist agent cho học liệu và đặc tả benchmark

Trạng thái: `APPROVED` — được người phụ trách dự án duyệt để triển khaiNgày tạo: 03/07/2026Experiment: `20260701_100006`Người lập plan: orchestratorPhạm vi: tạo và kiểm thử hai specialist agent mới:

- `learning-resource-curator`
- `benchmark-specification-designer`

Không bao gồm `dataset-quality-auditor` trong plan này.

## 1. Lý do cần plan này

Sau cuộc họp ngày 01/07/2026 giữa UET và HNMU, dự án đã chuyển sang giai đoạn cần tạo dữ liệu thật bằng **phiếu tác giả**. Để phiếu tác giả vận hành được, UET cần chuẩn bị ít nhất hai nhóm nền tảng:

1. Học liệu/chương trình phải được chia nhỏ, đặt mã và truy xuất được.
2. Task, rubric, mã lỗi nghiêm trọng và quan hệ truy vết phải được đặc tả rõ.

Hai specialist hiện có chưa bao phủ trực tiếp hai nhóm việc này:

- `research-methodologist` phụ trách nghiên cứu khoa học, bằng chứng, giới hạn và câu hỏi mở.
- `teacher-collaboration-designer` phụ trách chuyển yêu cầu thành hướng dẫn dễ làm cho giáo viên.

Vì vậy, cần thêm hai specialist mới để lấp đúng khoảng trống vai trò, nhưng vẫn tránh chồng chéo với agent hiện có.

## 2. Căn cứ từ roadmap

Plan này bám vào `experiments/20260620_115236/roadmap.md`:


| Roadmap | Nội dung liên quan                                                                                      | Specialist tương ứng            |
| ------- | --------------------------------------------------------------------------------------------------------- | ---------------------------------- |
| P05     | Benchmark taxonomy, task definitions, rubric specification, provenance contract                           | `benchmark-specification-designer` |
| P06     | Learning-resource registry, benchmark database, teacher-facing lookup/update workflow, dataset versioning | `learning-resource-curator`        |

Plan này chưa chạm tới:

- P07 — evaluation pipeline;
- P08 — workspace isolation và evaluator integrity;
- `dataset-quality-auditor`, vì hiện chưa phải nút thắt ngay lập tức.

## 3. Mục tiêu

Tạo được hai specialist agent mới ở mức tối thiểu nhưng dùng được:

1. Có skill gốc trong `agents/<name>/`.
2. Có adapter mỏng cho Codex và Claude, nhất quán với P01.
3. Có tài liệu tham chiếu đủ để agent tạo đầu ra có cấu trúc.
4. Có script kiểm định tối thiểu cho các artifact mà agent tạo ra.
5. Có test để đảm bảo agent được phát hiện, adapter không tách logic khỏi skill gốc, và validator chạy được.
6. Có hướng dẫn phối hợp để hai agent mới làm song song với `research-methodologist`, sau đó đưa đầu ra cho `benchmark-specification-designer` tổng hợp.

## 4. Nguyên tắc thiết kế

### 4.1. Không thay thế HNMU

Hai agent mới chỉ hỗ trợ UET chuẩn hóa và kiểm tra artifact. Chúng không được tự quyết định thay giáo viên HNMU về:

- nội dung sư phạm đúng/sai;
- nhóm chủ đề cuối cùng;
- task/rubric cuối cùng;
- việc duyệt, sửa hoặc loại mẫu dữ liệu.

### 4.2. Không tạo agent chung chung

Mỗi agent phải có ranh giới rõ:

- `learning-resource-curator`: chỉ xử lý học liệu/chương trình và mã học liệu.
- `benchmark-specification-designer`: chỉ tổng hợp bằng chứng + học liệu thành đặc tả benchmark.

Nếu một việc thuộc hướng dẫn giáo viên, giao cho `teacher-collaboration-designer`.

Nếu một việc thuộc rà soát paper, giao cho `research-methodologist`.

### 4.3. Ưu tiên tiếng Việt cho đầu ra dự án

Các báo cáo, handoff, plan và tài liệu gửi HNMU phải viết tiếng Việt. Thuật ngữ tiếng Anh chỉ dùng khi là tên trường, tên file, tên model, tên công cụ hoặc thuật ngữ chuyên ngành chưa có cách dịch đủ rõ.

### 4.4. Không dùng tiến trình ẩn

Tuân thủ P01:

- không dùng `codex exec` lồng nhau;
- không dùng `claude -p`;
- không chạy specialist ngầm bằng terminal;
- nếu runtime không hiển thị được specialist thread, dùng single-agent fallback bằng cách đọc skill trong parent thread.

### 4.5. Hợp đồng đầu ra trước, logic agent sau

Mỗi agent phải có hợp đồng đầu ra rõ ràng trước khi test. Nếu đầu ra không có cấu trúc, `benchmark-specification-designer` sẽ khó tổng hợp từ research và học liệu.

### 4.6. Pin model và reasoning effort để tránh fan-out tốn token

Plan này phải tính đến trường hợp cần spawn nhiều specialist cùng loại cùng lúc, ví dụ:

- nhiều `learning-resource-curator` xử lý song song các khối lớp 6, 7, 8, 9;
- nhiều `learning-resource-curator` xử lý song song SGK, SGV, tài liệu tập huấn;
- nhiều `benchmark-specification-designer` rà soát độc lập các nhóm task trước khi tổng hợp.

Rủi ro đã từng xảy ra trong dự án: khi để model và reasoning effort ở trạng thái mặc định, runtime có thể dùng model đắt hơn hoặc reasoning effort cao hơn cần thiết, làm token cost tăng rất mạnh.

Vì vậy, adapter của hai agent mới phải có setting cụ thể, không để mặc định mơ hồ:


| Agent                              | Model mặc định | Reasoning mặc định | Khi fan-out cùng loại                                                                                                                    |
| ---------------------------------- | ----------------- | --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `learning-resource-curator`        | `gpt-5.4-mini`    | `medium`              | Giữ`gpt-5.4-mini`; chỉ nâng reasoning nếu người phụ trách dự án duyệt rõ.                                                      |
| `benchmark-specification-designer` | `gpt-5.4-mini`    | `high`                | Mặc định không fan-out; nếu buộc phải fan-out thì dùng`medium` cho từng nhánh và chỉ dùng `high` ở bước tổng hợp cuối. |

Quy tắc vận hành:

1. Mặc định chỉ chạy một instance của mỗi specialist cho một task.
2. Nếu cần nhiều instance cùng loại, orchestrator phải xin duyệt rõ:
   - số lượng instance;
   - lý do phải tách nhánh;
   - model;
   - reasoning effort;
   - input của từng nhánh;
   - allowed writes của từng nhánh;
   - đầu ra mong đợi;
   - cách tổng hợp kết quả.
3. Không instance nào được ghi cùng một file đầu ra. Mỗi nhánh phải ghi vào thư mục hoặc file riêng, ví dụ `grade6/`, `grade7/`, `resource_sgk/`, `resource_sgv/`.
4. Khi fan-out kết thúc, chỉ orchestrator hoặc một task tổng hợp riêng mới được tạo artifact hợp nhất.
5. Handoff phải ghi lại token/cost risk nếu phải nâng model hoặc reasoning effort.

### 4.7. Mã học liệu v0 chỉ cần giúp truy hồi về nguồn gốc

Ở giai đoạn này, **không ưu tiên thiết kế công thức mã học liệu quá chi tiết**. Muốn có công thức mã học liệu bền vững cho từng bài, mục, trang hoặc đoạn, `learning-resource-curator` cần đọc và xử lý trực tiếp SGK/SGV/tài liệu tập huấn; việc đó mất thời gian và không nên chặn các tính năng khác của specialist agent.

Vì vậy, yêu cầu v0 là:

- mã học liệu ngắn, dễ copy;
- mỗi mã truy hồi được về học liệu gốc thông qua bảng mapping;
- bảng mapping là nguồn chân lý, không phải bản thân chuỗi mã;
- chưa bắt buộc mã phải tự biểu diễn đầy đủ bài/mục/trang/fragment;
- mã đã cấp không được tái sử dụng cho nguồn khác.

Nguyên tắc v0:

- Nếu nguồn có mã tự nhiên dễ lấy từ link, có thể dùng mã đó để mã dễ truy ngược.
- Nếu chưa có mã tự nhiên hoặc chưa đọc kỹ học liệu, dùng số thứ tự ổn định trong bảng mapping.
- Không gắn quá nhiều thông tin chưa chắc chắn vào mã.
- Khi cần chia nhỏ thành fragment, có thể dùng mã con đơn giản như `#F0001`, còn trang/mục/ghi chú vị trí lưu trong bảng mapping.

Ví dụ mã học liệu v0:

| Trường hợp | Mã v0 đề xuất | Cách truy hồi |
|---|---|---|
| SGK Tin học 9 từ taphuan có source key `4700233123` | `LM-SGK-TIN9-4700233123` | Tra `learning_resource_source_map.csv` để lấy URL, tên sách, lớp, loại học liệu, file gốc. |
| Chưa muốn dùng source key hoặc nguồn không có mã rõ | `LM-SGK-TIN9-0001` | Tra bảng mapping để biết đây là SGK Tin học 9 bản nào. |
| Một đoạn học liệu trong nguồn trên | `LM-SGK-TIN9-4700233123#F0001` | Tra bảng fragment mapping để biết trang, bài, mục, ghi chú vị trí. |

Bảng mapping tối thiểu cho học liệu gốc:

| Cột | Ý nghĩa |
|---|---|
| `learning_material_id` | Mã học liệu v0, ví dụ `LM-SGK-TIN9-4700233123`. |
| `source_title` | Tên học liệu gốc. |
| `material_type` | SGK, SGV, sách bài tập, tài liệu tập huấn, hoặc loại khác. |
| `grade` | Lớp hoặc phạm vi lớp. |
| `source_url` | Link gốc nếu có. |
| `source_key` | Khóa nguồn nếu có, ví dụ `4700233123`. |
| `local_file_path` | Đường dẫn file local nếu đã tải về. |
| `version_label` | Nhãn phiên bản hoặc ngày nhập. |
| `status` | `draft`, `needs_hnmu_review`, `confirmed`, hoặc `retired`. |
| `notes` | Ghi chú truy hồi hoặc cảnh báo. |

Bảng mapping tối thiểu cho fragment, nếu đã chia nhỏ:

| Cột | Ý nghĩa |
|---|---|
| `fragment_id` | Mã fragment, ví dụ `LM-SGK-TIN9-4700233123#F0001`. |
| `learning_material_id` | Mã học liệu gốc. |
| `page_start` / `page_end` | Khoảng trang nếu biết. |
| `section_label` | Bài/mục/tiểu mục nếu biết. |
| `order_index` | Thứ tự fragment trong học liệu hoặc trong trang. |
| `location_note` | Ghi chú vị trí bằng ngôn ngữ tự nhiên. |
| `status` | Trạng thái review. |

Công thức mã học liệu chi tiết hơn sẽ để sau, khi đã có dữ liệu thực tế từ SGK/SGV và HNMU xác nhận cách chia học liệu.

### 4.8. Mã nghiên cứu vẫn nên ưu tiên mã tự nhiên từ nguồn paper

Mã nghiên cứu đơn giản hơn mã học liệu vì paper thường có DOI, arXiv ID, OpenReview ID hoặc tên file ổn định. Vì vậy plan này vẫn giữ yêu cầu có quy tắc mã nghiên cứu đủ dễ truy hồi.

Nguyên tắc:

- Mã phải ổn định theo nguồn gốc, không phụ thuộc vào thứ tự nhập file.
- Nhìn vào citation, DOI, arXiv ID, OpenReview ID hoặc tên file paper thì suy ra được mã nghiên cứu trong các trường hợp phổ biến.
- Nếu có phiên bản, cần tách mã paper logic và mã phiên bản paper.
- Nếu công thức có nguy cơ trùng mã, phải có quy tắc xử lý trùng rõ ràng.

Ví dụ định hướng cho mã nghiên cứu:

| Nguồn | Thông tin nhìn thấy | Mã logic đề xuất | Mã phiên bản đề xuất |
|---|---|---|---|
| arXiv | file `2510.02663v1.pdf` | `RS-ARXIV-2510-02663` | `RS-ARXIV-2510-02663-V1` |
| arXiv | file `2502.18940v2.pdf` | `RS-ARXIV-2502-18940` | `RS-ARXIV-2502-18940-V2` |
| DOI | DOI trong citation | `RS-DOI-<doi-da-chuan-hoa>` | `RS-DOI-<doi-da-chuan-hoa>-V1` nếu chỉ có một bản |
| Không có DOI/arXiv | citation có tác giả, năm, tiêu đề | `RS-<FIRSTAUTHOR>-<YEAR>-<TITLEKEY>` | thêm hậu tố `-A`, `-B` nếu trùng |

## 5. Flow làm việc dự kiến

Hai luồng đầu tiên có thể chạy song song:

```text
                 ┌─ research-methodologist
Orchestrator ────┤
                 └─ learning-resource-curator

research outputs + learning-resource outputs
        ↓
benchmark-specification-designer
        ↓
teacher-collaboration-designer
        ↓
HNMU
```

Ý nghĩa:

- `research-methodologist` tạo cơ sở nghiên cứu: năng lực gia sư, bằng chứng, giới hạn, câu hỏi mở.
- `learning-resource-curator` tạo cơ sở học liệu: mã học liệu, nhóm chủ đề, đoạn học liệu, tiền kiến thức lớp 6–8.
- `benchmark-specification-designer` tổng hợp hai nguồn trên thành task, rubric, mã lỗi, quan hệ truy vết và câu hỏi cần HNMU xác nhận.
- `teacher-collaboration-designer` biến đặc tả thành phiếu/hướng dẫn giáo viên.

## 6. Specialist 1 — `learning-resource-curator`

### 6.1. Vai trò

`learning-resource-curator` phụ trách chuẩn hóa học liệu/chương trình để làm căn cứ xây dựng benchmark.

Agent này trả lời câu hỏi:

> Học liệu Tin học 6–9 nên được chia nhỏ, đặt mã, mô tả và liên kết với tiền kiến thức như thế nào để giáo viên có thể dùng làm căn cứ tạo mẫu?

### 6.2. Đầu vào

Các đầu vào dự kiến:

- SGK/SGV/tài liệu tập huấn do HNMU cung cấp;
- mục lục SGK Tin học 6, 7, 8, 9;
- file học liệu đã OCR hoặc trích xuất thô;
- note cuộc họp về phạm vi Tin học lớp 9 và tiền kiến thức lớp 6–8;
- các artifact cũ từ C01/F01 chỉ để tham khảo, không import nguyên trạng.

### 6.3. Đầu ra

Các đầu ra cần hỗ trợ:


| Artifact                                      | Mục đích                                                                                                        |
| --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `learning_resource_registry.csv` hoặc `.md`  | Danh mục học liệu gốc, nguồn, lớp, loại tài liệu, trạng thái xử lý.                                   |
| `learning_resource_fragments.csv` hoặc `.md` | Danh sách đoạn/mục/bài đã được chia nhỏ, có mã ổn định để giáo viên trích dẫn.               |
| `topic_map_grade6_9.csv` hoặc `.md`          | Nhóm chủ đề thống nhất xuyên suốt Tin học THCS.                                                           |
| `grade9_prerequisite_map.csv` hoặc `.md`     | Bảng nối nội dung lớp 9 với tiền kiến thức lớp 6–8.                                                      |
| `learning_resource_open_questions.md`         | Câu hỏi cần HNMU xác nhận về nhóm chủ đề, tiền kiến thức, đoạn học liệu hoặc phạm vi sử dụng. |

### 6.4. Ranh giới

Agent này không được:

- tự quyết định nhóm chủ đề cuối cùng thay HNMU;
- tự viết task/rubric benchmark;
- tự chấm mẫu dữ liệu;
- tự thiết kế database production;
- tự coi OCR hoặc chia đoạn tự động là đúng nếu chưa có kiểm tra của con người.

### 6.5. Cấu trúc skill cần tạo

```text
agents/learning-resource-curator/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── learning-resource-schema.md
│   ├── learning-resource-mapping-v0.md
│   ├── topic-mapping-guidelines.md
│   └── resource-fragmentation-guidelines.md
└── scripts/
    └── validate_learning_resource_registry.py
```

### 6.6. Nội dung chính của `SKILL.md`

`SKILL.md` cần có:

- frontmatter với `name` và `description`;
- chính sách ngôn ngữ;
- workflow xử lý học liệu;
- hợp đồng đầu ra;
- quy tắc dùng mã học liệu v0 và bảng mapping truy hồi nguồn gốc;
- ranh giới với `research-methodologist`, `benchmark-specification-designer` và `teacher-collaboration-designer`;
- yêu cầu ghi rõ phần nào là đã xác nhận, phần nào là suy luận, phần nào cần HNMU xác nhận;
- completion check.

### 6.7. Validator tối thiểu

`validate_learning_resource_registry.py` cần kiểm tra tối thiểu:

- mỗi học liệu có mã duy nhất;
- mỗi fragment có mã duy nhất;
- mỗi fragment trỏ tới một học liệu gốc hợp lệ;
- mỗi fragment có lớp hoặc phạm vi lớp;
- mỗi fragment có vị trí nguồn: trang, bài, mục hoặc ghi chú vị trí;
- mỗi fragment có trạng thái: `draft`, `needs_hnmu_review`, `confirmed`, hoặc `retired`;
- không có fragment lớp 9 thiếu thông tin chủ đề;
- nếu có tiền kiến thức lớp 6–8 thì phải ghi rõ lớp và chủ đề liên quan.

## 7. Specialist 2 — `benchmark-specification-designer`

### 7.1. Vai trò

`benchmark-specification-designer` phụ trách tổng hợp cơ sở nghiên cứu và cơ sở học liệu thành đặc tả benchmark.

Agent này trả lời câu hỏi:

> Dựa trên bằng chứng nghiên cứu và học liệu đã mã hóa, benchmark nên có task, rubric, mã lỗi và quan hệ truy vết như thế nào?

### 7.2. Đầu vào

Các đầu vào dự kiến:

- evidence matrix từ `research-methodologist`;
- capability model hoặc danh sách năng lực gia sư ứng viên;
- learning-resource registry từ `learning-resource-curator`;
- topic map Tin học 6–9;
- grade-9 prerequisite map;
- phiếu tác giả đã chốt hoặc đang chờ chỉnh;
- feedback của HNMU từ các cuộc họp.

### 7.3. Đầu ra

Các đầu ra cần hỗ trợ:


| Artifact                                      | Mục đích                                                                                                  |
| --------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `benchmark_task_specification.md`             | Định nghĩa task, phạm vi, đầu vào/đầu ra, ví dụ tình huống và câu hỏi cần HNMU xác nhận.  |
| `rubric_specification.md`                     | Mô tả rubric, mức điểm, tiêu chí quan sát được và quan hệ với task.                            |
| `serious_error_catalog.md`                    | Danh mục lỗi nghiêm trọng, ý nghĩa, hành động gợi ý và rubric bị ảnh hưởng.                  |
| `benchmark_provenance_matrix.csv` hoặc `.md` | Bảng nối task/rubric/mã lỗi với mã nghiên cứu và mã học liệu.                                    |
| `author_form_field_review.md`                 | Rà soát phiếu tác giả: trường nào cần UET điền, HNMU điền, bắt buộc/tùy chọn, còn mơ hồ. |
| `benchmark_open_questions.md`                 | Câu hỏi cần giáo sư/HNMU chốt trước khi mở rộng dữ liệu.                                         |

### 7.4. Ranh giới

Agent này không được:

- tự kết luận task/rubric là chính thức nếu chưa có HNMU xác nhận;
- tạo task chỉ dựa vào trực giác, không có bằng chứng hoặc học liệu;
- sửa evidence matrix hoặc learning-resource registry để hợp thức hóa đặc tả;
- viết hướng dẫn giáo viên chi tiết thay `teacher-collaboration-designer`;
- chấm mẫu dữ liệu hoặc đánh giá mô hình.

### 7.5. Cấu trúc skill cần tạo

```text
agents/benchmark-specification-designer/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── benchmark-spec-schema.md
│   ├── research-id-convention.md
│   ├── rubric-and-serious-error-guidelines.md
│   └── provenance-matrix-guidelines.md
└── scripts/
    └── validate_benchmark_specification.py
```

### 7.6. Nội dung chính của `SKILL.md`

`SKILL.md` cần có:

- frontmatter với `name` và `description`;
- chính sách ngôn ngữ;
- workflow tổng hợp research + học liệu;
- hợp đồng đầu ra;
- quy tắc dùng mã nghiên cứu, mã học liệu, mã task, mã rubric và mã lỗi;
- quy tắc tách rõ `evidence`, `inference`, `teacher_decision_needed`;
- ranh giới với các specialist khác;
- completion check.

### 7.7. Validator tối thiểu

`validate_benchmark_specification.py` cần kiểm tra tối thiểu:

- mỗi task có `task_id`, tên, định nghĩa, phạm vi, đầu vào/đầu ra;
- mỗi rubric có `rubric_id`, task liên quan, tiêu chí quan sát được, mức điểm;
- mỗi mã lỗi nghiêm trọng có `error_id`, mô tả, hành động gợi ý, rubric bị ảnh hưởng;
- mỗi task có ít nhất một căn cứ nghiên cứu hoặc được đánh dấu rõ là cần bổ sung nghiên cứu;
- mỗi task có ít nhất một căn cứ học liệu hoặc được đánh dấu rõ là chưa đủ học liệu;
- provenance matrix không tham chiếu mã nghiên cứu/học liệu rỗng;
- mọi mục chưa được HNMU xác nhận phải có trạng thái `needs_hnmu_review`.

## 8. Công việc triển khai chi tiết

### Phase 0 — Kiểm tra nền hiện có

Việc cần làm:

1. Đọc lại `agents/research-methodologist/` và `agents/teacher-collaboration-designer/`.
2. Đọc test hiện có trong `tests/agents/`.
3. Đọc adapter trong `.codex/agents/` và `.claude/agents/`.
4. Xác định pattern hiện tại cho:
   - `SKILL.md`;
   - `agents/openai.yaml`;
   - adapter Codex;
   - adapter Claude;
   - skill discovery link;
   - validator script;
   - pytest.

Đầu ra:

- danh sách pattern cần giữ nhất quán;
- quyết định model mặc định cho hai agent mới;
- quyết định fan-out policy cho từng agent.

Đề xuất model ban đầu:

- `learning-resource-curator`: `gpt-5.4-mini`, reasoning medium.
- `benchmark-specification-designer`: `gpt-5.4-mini`, reasoning high.

Lý do: giai đoạn này cần tiết kiệm token, nhưng `benchmark-specification-designer` cần lập luận tổng hợp nhiều nguồn hơn.

Khi fan-out:

- `learning-resource-curator` vẫn giữ `gpt-5.4-mini`, reasoning medium;
- `benchmark-specification-designer` chỉ fan-out khi thật sự cần; từng nhánh dùng reasoning medium, bước tổng hợp cuối dùng reasoning high;
- mọi fan-out cùng loại phải được người phụ trách dự án duyệt rõ số lượng instance và lý do.

### Phase 1 — Chốt hợp đồng đầu ra

Việc cần làm:

1. Viết schema tham chiếu cho `learning-resource-curator`.
2. Viết schema tham chiếu cho `benchmark-specification-designer`.
3. Viết công thức mã nghiên cứu:
   - ưu tiên mã tự nhiên như arXiv ID, DOI, OpenReview ID;
   - với paper trong `document/paper/source_paper`, ví dụ `2510.02663v1.pdf`, mã phải suy ra được từ tên file;
   - tách mã paper logic và mã phiên bản paper khi cần.
4. Viết quy ước mã học liệu v0 và bảng mapping:
   - mã học liệu gốc đơn giản;
   - bảng mapping từ mã về URL/file gốc;
   - mã fragment đơn giản nếu đã chia nhỏ;
   - quy tắc không tái sử dụng mã đã cấp.
5. Chốt các trạng thái chuẩn:
   - `draft`;
   - `needs_uet_review`;
   - `needs_hnmu_review`;
   - `confirmed`;
   - `retired`.
6. Chốt quy tắc mã tối thiểu:
   - mã nghiên cứu;
   - mã học liệu;
   - mã fragment;
   - mã task;
   - mã rubric;
   - mã lỗi nghiêm trọng.

Đầu ra:

- `agents/learning-resource-curator/references/learning-resource-schema.md`;
- `agents/learning-resource-curator/references/learning-resource-mapping-v0.md`;
- `agents/benchmark-specification-designer/references/benchmark-spec-schema.md`;
- `agents/benchmark-specification-designer/references/research-id-convention.md`.

### Phase 2 — Tạo `learning-resource-curator`

Việc cần làm:

1. Tạo thư mục skill bằng quy trình `skill-creator`.
2. Viết `SKILL.md`.
3. Viết `agents/openai.yaml`.
4. Viết các file reference:
   - `learning-resource-schema.md`;
   - `learning-resource-mapping-v0.md`;
   - `topic-mapping-guidelines.md`;
   - `resource-fragmentation-guidelines.md`.
5. Viết validator:
   - `scripts/validate_learning_resource_registry.py`.
6. Tạo adapter:
   - `.codex/agents/learning-resource-curator.toml`;
   - `.claude/agents/learning-resource-curator.md`.
7. Tạo link discovery:
   - `.agents/skills/learning-resource-curator`.

Đầu ra:

- specialist mới có thể được phát hiện bởi runtime;
- adapter pin model/reasoning rõ ràng, không để runtime dùng mặc định mơ hồ;
- validator chạy được với fixture nhỏ.

### Phase 3 — Tạo `benchmark-specification-designer`

Việc cần làm:

1. Tạo thư mục skill bằng quy trình `skill-creator`.
2. Viết `SKILL.md`.
3. Viết `agents/openai.yaml`.
4. Viết các file reference:
   - `benchmark-spec-schema.md`;
   - `research-id-convention.md`;
   - `rubric-and-serious-error-guidelines.md`;
   - `provenance-matrix-guidelines.md`.
5. Viết validator:
   - `scripts/validate_benchmark_specification.py`.
6. Tạo adapter:
   - `.codex/agents/benchmark-specification-designer.toml`;
   - `.claude/agents/benchmark-specification-designer.md`.
7. Tạo link discovery:
   - `.agents/skills/benchmark-specification-designer`.

Đầu ra:

- specialist mới có thể được phát hiện bởi runtime;
- adapter pin model/reasoning rõ ràng, không để runtime dùng mặc định mơ hồ;
- validator chạy được với fixture nhỏ.

### Phase 4 — Cập nhật test

Việc cần làm:

1. Mở rộng `tests/agents/test_adapters.py` để kiểm tra adapter của hai agent mới.
2. Mở rộng `tests/agents/test_documentation.py` để kiểm tra README/ARCHITECTURE nhắc đúng specialist mới sau khi triển khai.
3. Thêm test validator tối thiểu nếu cần:
   - fixture hợp lệ;
   - fixture thiếu mã;
   - fixture tham chiếu mã không tồn tại;
   - fixture thiếu trạng thái review.

Đầu ra:

- test fail rõ khi adapter tách khỏi skill gốc;
- test fail rõ khi validator không bắt được lỗi dữ liệu tối thiểu.

### Phase 5 — Cập nhật tài liệu hệ thống

Việc cần làm:

1. Cập nhật `README.md`:
   - danh sách specialist mới;
   - vai trò ngắn của từng agent;
   - quy tắc không spawn nhiều agent cùng loại nếu chưa được duyệt;
   - model/reasoning mặc định của agent mới để kiểm soát token.
2. Cập nhật `ARCHITECTURE.md`:
   - sơ đồ flow song song research/học liệu;
   - vai trò của `benchmark-specification-designer` trong bước tổng hợp;
   - ranh giới ownership;
   - fan-out policy khi nhiều instance cùng specialist phải chạy song song.
3. Nếu cần, cập nhật roadmap hoặc tạo ghi chú kế thừa cho P05/P06.

Đầu ra:

- tài liệu onboarding không còn chỉ nhắc hai specialist cũ.

### Phase 6 — Kiểm thử tĩnh và kiểm thử chức năng nhỏ

Lệnh kiểm thử bắt buộc dùng môi trường:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python
```

Các lệnh dự kiến:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  /home/quannda/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  agents/learning-resource-curator

/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  /home/quannda/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  agents/benchmark-specification-designer

/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  agents/learning-resource-curator/scripts/validate_learning_resource_registry.py \
  <fixture-learning-resource>

/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  agents/benchmark-specification-designer/scripts/validate_benchmark_specification.py \
  <fixture-benchmark-spec>

/home/quannda/miniconda3/envs/benchmark_env/bin/python -m pytest tests/agents -q
```

Không cài thêm package trong plan này nếu không thật sự cần.

### Phase 7 — Smoke test bằng single-agent fallback

Nếu runtime chưa đảm bảo quan sát được specialist thread, kiểm thử bằng single-agent fallback:

1. Load skill `learning-resource-curator` trong parent thread.
2. Giao một fixture nhỏ gồm 2–3 mục học liệu giả.
3. Kiểm tra agent có tạo được registry và open questions đúng format không.
4. Load skill `benchmark-specification-designer` trong parent thread.
5. Giao một fixture nhỏ gồm:
   - 2 capability từ research;
   - 2 fragment học liệu;
   - 1 task ứng viên.
6. Kiểm tra agent có tạo được provenance matrix và câu hỏi HNMU cần chốt không.

Nếu dùng native subagent thật, orchestrator phải thông báo trước:

- tên specialist;
- model nếu được pin;
- reasoning effort;
- task;
- input;
- allowed writes;
- expected output.

Nếu dùng nhiều instance cùng loại, orchestrator phải thông báo thêm:

- số lượng instance;
- cách chia input;
- lý do tách nhánh;
- file/thư mục riêng của từng nhánh;
- cách tổng hợp kết quả;
- xác nhận rằng model/reasoning không dùng mặc định mơ hồ.

## 9. File dự kiến được phép sửa khi triển khai

Khi plan này được duyệt, phạm vi file được phép sửa/tạo:

```text
agents/learning-resource-curator/
agents/benchmark-specification-designer/
.codex/agents/learning-resource-curator.toml
.codex/agents/benchmark-specification-designer.toml
.claude/agents/learning-resource-curator.md
.claude/agents/benchmark-specification-designer.md
.agents/skills/learning-resource-curator
.agents/skills/benchmark-specification-designer
tests/agents/
README.md
ARCHITECTURE.md
experiments/20260701_100006/
```

Không sửa:

```text
agents/research-methodologist/scripts/
agents/teacher-collaboration-designer/scripts/
experiments/20260620_115236/
experiments/20260621_135515/
```

trừ khi người phụ trách dự án duyệt riêng.

## 10. Acceptance criteria

Plan triển khai chỉ được coi là hoàn thành khi:

1. Có đủ hai thư mục skill mới.
2. Mỗi skill có `SKILL.md`, `agents/openai.yaml`, `references/` và `scripts/` tối thiểu.
3. Mỗi skill pass `quick_validate.py`.
4. Mỗi validator chạy được trên fixture hợp lệ và bắt được ít nhất một fixture lỗi.
5. Adapter Codex/Claude là lớp mỏng, không chứa logic fork khỏi `SKILL.md`.
6. Adapter Codex pin rõ model và reasoning effort cho hai agent mới.
7. Có quy tắc fan-out cùng loại trong adapter/developer instructions hoặc tài liệu vận hành.
8. Có quy ước mã nghiên cứu và bảng mapping học liệu v0 đủ rõ để truy hồi từ mã về citation/tên file/link học liệu trong các trường hợp phổ biến.
9. Discovery links trong `.agents/skills/` hoạt động.
10. `tests/agents -q` pass bằng `benchmark_env`.
11. README và ARCHITECTURE phản ánh đúng danh sách specialist mới.
12. Không có agent nào tự nhận quyền thay HNMU quyết định chuyên môn/sư phạm.
13. Handoff cuối nêu rõ:
    - file đã tạo/sửa;
    - lệnh kiểm thử;
    - Python executable;
    - giới hạn còn lại;
    - câu hỏi cần người phụ trách dự án quyết định.

## 11. Rủi ro và cách giảm rủi ro


| Rủi ro                                                     | Cách giảm rủi ro                                                                                                                        |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| Chồng vai trò với`research-methodologist`                | `learning-resource-curator` không review paper; `benchmark-specification-designer` chỉ dùng evidence đã được trích xuất.         |
| Chồng vai trò với`teacher-collaboration-designer`        | Không viết hướng dẫn giáo viên chi tiết trong hai agent mới; chỉ tạo đặc tả và câu hỏi cần chuyển hóa.                 |
| Agent tự quyết chuyên môn thay HNMU                     | Mọi nội dung chưa được xác nhận phải đánh dấu`needs_hnmu_review`.                                                              |
| Tốn token do agent mới đọc quá nhiều tài liệu       | Pin model/reasoning trong adapter, chia task theo artifact nhỏ, không fan-out nhiều bản sao cùng agent nếu chưa được duyệt rõ. |
| Fan-out cùng loại vô tình dùng model mặc định đắt | Bắt buộc thông báo model/reasoning trước khi spawn; adapter của agent mới không được thiếu model pin.                         |
| Mã nghiên cứu/học liệu đặt tùy hứng, khó suy ra   | Tạo công thức mã hóa trước khi tạo registry; validator kiểm tra định dạng mã.                                                 |
| Validator bị dùng để “hack điểm”                    | Validator chỉ kiểm tra cấu trúc/tính nhất quán, không chấm chất lượng sư phạm.                                               |
| Plan bị kéo sang xây database thật                      | Giới hạn plan ở skill + validator + adapter; database thuộc plan P06 riêng.                                                           |

## 12. Quyết định cần người phụ trách dự án chốt trước khi triển khai

1. Có duyệt tạo cả hai agent trong cùng một plan không?
2. Có pin cả hai agent về `gpt-5.4-mini` không?
3. Có chốt reasoning mặc định như plan đề xuất không?
4. Khi cần fan-out cùng loại, có cần giới hạn cứng số instance tối đa không? Đề xuất mặc định: tối đa 2 nếu chưa duyệt riêng.
5. Có cần Claude adapter ở giai đoạn này không, hay chỉ tạo để tương thích tĩnh như P01?
6. Fixture test nên dùng dữ liệu giả tối giản hay lấy một phần nhỏ từ experiment `20260701_100006`?
7. Có cần cập nhật roadmap ngay khi triển khai không, hay chỉ cập nhật README/ARCHITECTURE trước?
8. Quy ước mã nghiên cứu nên ưu tiên `RS-ARXIV-*`/`RS-DOI-*` như plan đề xuất, hay dùng tiền tố khác?
9. Quy ước mã học liệu v0 nên dùng tiền tố `LM-*` và bảng mapping như plan đề xuất, hay giữ tiền tố khác gần với thói quen của HNMU/UET?

## 13. Lý do chưa tạo `dataset-quality-auditor`

`dataset-quality-auditor` là agent hợp lý nhưng chưa cấp thiết trong bước này.

Lý do:

- hiện nút thắt là học liệu, task, rubric, mã lỗi và phiếu tác giả;
- chưa có đủ dữ liệu thật để audit chất lượng ở quy mô lớn;
- nếu tạo quá sớm, agent này dễ lấn sang kiểm tra schema hoặc đánh giá chuyên môn khi tiêu chuẩn chưa ổn định;
- nên tạo sau khi phiếu tác giả, mã task, mã học liệu và rubric đã có vòng xác nhận đầu tiên từ HNMU.

Tạm thời, kiểm tra chất lượng dữ liệu có thể được xử lý bằng validator cấu trúc nhỏ trong từng agent mới.
