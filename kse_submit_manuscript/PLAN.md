# Plan — Viết tăng dần manuscript KSE 2026

Trạng thái: `DRAFT` — chưa được duyệt, chưa tạo manuscript source  
Ngày lập: 25/07/2026  
Hạn nộp chính thức: 31/07/2026  
Mốc gửi giáo sư đề xuất: 27/07/2026, muộn nhất 28/07/2026

Pre-plan prerequisite đã hoàn thành: official IEEE Conference LaTeX package
đã được tải và giải nén dưới `kse_submit_manuscript/`; chưa tạo working
manuscript hoặc triển khai các bước authoring còn lại.

## 1. Mục tiêu

Tạo một bài full paper KSE 2026 tối đa 6 trang về quá trình xây dựng benchmark gia sư AI môn Tin học THCS Việt Nam. Việc viết chạy song song theo tiến độ khoa học: claim nào đã có evidence thì viết và khóa ngay; kết quả mới từ Plan 03–05 được cập nhật qua snapshot có truy vết.

Không đợi toàn bộ benchmark hoàn chỉnh mới bắt đầu. Bản gửi giáo sư ngày 27/07 phải đọc được như một paper hoàn chỉnh dù còn đánh dấu những kết quả chưa freeze trong notes nội bộ.

## 2. Nguồn template và quy tắc hội nghị

Canonical verification:

- `template_source_verification.md`

Quy tắc đã xác minh:

- dùng IEEE Conference LaTeX template;
- `\documentclass[conference]{IEEEtran}`;
- không quá 6 trang;
- nộp qua CMT;
- chọn Main Session hoặc một Special Session.

Không thay đổi format IEEE để ép số trang. Các điểm chưa rõ như anonymity, paper size và deadline timezone phải kiểm tra lại trên CMT trước submission.

## 3. Paper story và research questions

### 3.1. Working scope tối thiểu

Paper trình bày một pipeline human-in-the-loop, có truy vết để chuyển dữ liệu hội thoại giáo viên thành ứng viên benchmark đánh giá phản hồi gia sư AI tiếng Việt.

Minimum viable contribution không phụ thuộc Plan 03 phải hoàn tất toàn bộ:

1. quy trình audit dữ liệu thô Tin học THCS lớp 6–9 với quyền quyết định của chuyên gia;
2. contract chuyển 665 raw dialogue `pass` thành 2.028 candidate theo mỗi lượt gia sư;
3. provenance, correction overlay, family grouping và fail-closed validation;
4. mô hình thiết kế capability–task–rubric có căn cứ nghiên cứu; báo là phương pháp/provisional nếu validity pilot chưa hoàn thành.

Kết quả Plan 03 được thêm khi có, nhưng không được viết kết quả tương lai ở thì đã hoàn thành.

### 3.2. Research questions dự kiến

- `RQ1`: Làm thế nào chuyển hội thoại gia sư Tin học THCS do giáo viên cung cấp thành candidate-level benchmark có truy vết và kiểm soát chất lượng?
- `RQ2`: Làm thế nào xây capability, task và rubric vừa có căn cứ khoa học vừa phù hợp với dữ liệu và phán đoán chuyên gia HNMU?
- `RQ3`: Specification có phân biệt được response tốt, trung bình và kém hay không?

`RQ3` chỉ giữ trong bản nộp cuối nếu Plan 03 có validity evidence đủ trước results cutoff. Nếu không, chuyển thành future work/ongoing validation, không báo conclusion.

### 3.3. Working title

Ưu tiên:

> Toward a Human-in-the-Loop Benchmark for Vietnamese Lower-Secondary Informatics AI Tutors

Title cuối cần giáo sư duyệt. Không đưa số `2,028` vào title nếu pool chưa qua candidate audit.

## 4. Claim tiers để viết đến đâu chắc đến đó

### Tier A — Có thể viết ngay

- phạm vi Tin học THCS lớp 6–9;
- 1.050 raw dialogues đã qua phase-1 audit;
- 665 raw dialogues `pass` được ưu tiên;
- Plan 02 tạo 2.028 preliminary candidates;
- một candidate cho mỗi tutor turn;
- family grouping theo `sample_id`;
- deterministic conversion, correction overlay có hash, trace 1:1 và exhaustive structural validation.

Nguồn: reports/output Plans 01–02 và audit artifacts.

### Tier B — Chỉ viết khi Plan 03 tạo artifact

- capability model;
- taxonomy task mới;
- rubric hai tầng;
- HNMU content-validity decisions;
- multi-LLM response pilot;
- agreement/discrimination/judge alignment.

### Tier C — Chỉ viết khi Plan 04–05 hoàn thành

- số candidate pass sau candidate audit;
- coverage cuối;
- HNMU-confirmed benchmark pilot;
- claim về readiness hoặc release.

Không dùng số provisional của Tier B/C như số cuối.

## 5. Cấu trúc manuscript và page budget

Tổng tối đa gồm cả references: 6 trang.

| Phần | Nội dung | Budget mục tiêu |
|---|---|---:|
| Abstract + Introduction | vấn đề, khoảng trống, đóng góp | 0,8 trang |
| Related Work | tutoring benchmarks, Vietnamese/educational benchmarks, measurement | 0,55 trang |
| Data and Human-in-the-Loop Pipeline | nguồn dữ liệu, audit, authority, conversion/provenance | 1,45 trang |
| Capability–Task–Rubric Method | Plan 03, task discovery, rubric hai tầng, validity design | 1,10 trang |
| Results | audit/conversion chắc chắn; Plan 03 results nếu kịp | 1,00 trang |
| Discussion, Limitations, Conclusion | scope, threats, ethics, next steps | 0,45 trang |
| References | chỉ nguồn trực tiếp hỗ trợ claim | 0,65 trang |

Budget là gate biên tập, không sửa format để đạt.

Hình/bảng ưu tiên:

1. một pipeline figure từ raw dialogue → audit → candidate family → specification/audit;
2. một bảng thống kê dữ liệu 1.050 → 665 → 2.028 theo lớp;
3. một capability–task–rubric diagram hoặc validity table nếu Plan 03 có kết quả.

## 6. Cấu trúc thư mục sẽ tạo khi plan được duyệt

```text
kse_submit_manuscript/
  PLAN.md
  README.md
  template_source_verification.md
  manuscript/
    main.tex
    references.bib
    sections/
      01_introduction.tex
      02_related_work.tex
      03_data_pipeline.tex
      04_specification_method.tex
      05_results.tex
      06_discussion_conclusion.tex
    figures/
    tables/
    build/
  notes/
    outline_vi.md
    claim_evidence_registry.csv
    manuscript_status.md
    paper_todo.md
    professor_review_log.md
  snapshots/
    results_snapshot.yaml
    artifact_hashes.csv
  releases/
    professor_review/
    submission/
```

`build/` chứa artifact tái tạo được. PDF gửi giáo sư và PDF nộp được lưu trong `releases/` kèm source hash.

## 7. Contract viết tăng dần

### 7.1. Claim–evidence registry

`notes/claim_evidence_registry.csv` có:

- `claim_id`
- `manuscript_section`
- `claim_text`
- `claim_tier`
- `evidence_path`
- `evidence_locator`
- `evidence_status`: `verified`, `provisional`, `superseded`, `blocked`
- `owner`
- `verified_at`
- `notes`

Mỗi số liệu và kết luận chính trong manuscript phải có `claim_id`. Claim `provisional` không được xuất hiện như kết quả đã chốt trong release gửi/nộp.

### 7.2. Results snapshot

Mỗi lần cập nhật results:

1. đọc paper update packet/report chính thức;
2. ghi số mới vào `snapshots/results_snapshot.yaml`;
3. lưu hash artifact nguồn;
4. cập nhật bảng/hình;
5. compile;
6. kiểm tra các số cũ trong toàn manuscript;
7. ghi thay đổi vào `notes/manuscript_status.md`.

Không copy số từ chat hoặc memory nếu chưa có artifact.

### 7.3. Đồng bộ từ experiment

Plan 03 tạo `reports/plan03-paper-update-packet.md`. Với Plans 01–02, manuscript dùng report/output đã hoàn thành. Plan 04–05 phải có packet tương tự trước khi claim của chúng được nhập vào paper.

Paper plan sở hữu source LaTeX; các plan kỹ thuật không sửa trực tiếp manuscript.

## 8. Lịch làm việc bắt buộc

### 25/07 — Khóa hướng paper và tạo khung

- giáo sư/project lead chốt working contribution, track dự kiến và author list;
- import official IEEE conference template;
- tạo file structure, BibTeX và claim registry;
- viết skeleton toàn bài;
- viết ngay Tier A: Introduction, data source, phase-1 audit, conversion contract và current results;
- tạo pipeline figure và data summary table bản đầu.

Deliverable: source compile được và outline đầy đủ.

### 26/07 — Hoàn thiện bản đọc được từ đầu đến cuối

- hoàn thiện Related Work từ bốn paper và measurement sources đã xác minh;
- viết phương pháp capability–task–rubric đúng trạng thái hiện tại;
- viết limitations/ethics;
- đối chiếu mọi số với artifact;
- cắt về page budget;
- chốt các câu hỏi cần giáo sư quyết định.

Deliverable: PDF v0.1, không còn section rỗng.

### 27/07 — Gửi giáo sư

- cập nhật kết quả Plan 03 đã freeze trước cutoff;
- chạy compile, citation, page-count và claim checks;
- tạo `releases/professor_review/` gồm PDF, source hash và một note ngắn:
  - đóng góp chính;
  - điểm còn provisional;
  - 3–5 câu hỏi mong giáo sư review;
- gửi giáo sư trước cuối ngày.

Deliverable: professor-review draft, dù scientific pipeline chưa hoàn tất.

### 28/07 — Buffer và feedback vòng đầu

- nếu 27/07 không thể gửi vì build/authority blocker, 28/07 là hạn muộn nhất;
- xử lý feedback cấu trúc/contribution trước;
- cập nhật author/track/anonymity decision;
- không mở thêm workstream khoa học lớn.

### 29/07 — Results cutoff

- freeze tập số liệu được phép đưa vào submission;
- claim chưa đủ evidence chuyển sang limitation/future work hoặc bỏ;
- freeze figures/tables và bibliography candidates.

### 30/07 — Submission candidate

- kiểm tra 6 trang gồm references;
- proofread tiếng Anh;
- kiểm tra author names, affiliations, acknowledgments và anonymity theo CMT;
- kiểm tra figure readability, citation completeness và artifact hashes;
- compile PDF sạch.

### 31/07 — Human-controlled submission

- kiểm tra lại deadline/timezone trên website/CMT;
- giáo sư/project lead duyệt PDF cuối;
- người có quyền tác giả nộp qua CMT;
- lưu receipt/submission ID thủ công.

Agent không tự submit và không tự xác nhận thay tác giả.

## 9. Review gates

### Gate P0 — Scope

- một câu problem statement;
- tối đa ba contributions;
- RQ3 chỉ giữ nếu có evidence đúng hạn;
- track và author list có owner quyết định.

### Gate P1 — Evidence

- mọi số liệu có artifact locator;
- provisional/final tách rõ;
- paper không gọi 2.028 candidate là benchmark sạch/chính thức;
- HNMU authority và giới hạn agent-assisted audit được mô tả đúng.

### Gate P2 — Scientific coherence

- research questions khớp method/results;
- task/rubric claims khớp trạng thái Plan 03;
- `gold_response` không bị mô tả là exact-match target;
- limitation nêu rõ chưa đo learning gain và chưa đánh giá học sinh thật.

### Gate P3 — Format/build

- official IEEE conference template;
- không quá 6 trang;
- không có citation/reference lỗi;
- không còn template guidance text;
- PDF mở được, font/figure đọc được;
- author/anonymity rule theo CMT.

### Gate P4 — Professor release

- PDF, source hash, open-issues note;
- không có TODO nội bộ hiện trong PDF;
- gửi ngày 27/07 hoặc muộn nhất 28/07.

### Gate P5 — Submission

- giáo sư/project lead chấp thuận;
- deadline/timezone được kiểm tra lại;
- CMT metadata khớp PDF;
- submission do người có thẩm quyền thực hiện.

## 10. Công cụ và kiểm tra

### 10.1. Build

Hiện local chưa có LaTeX toolchain. Đường nhanh mặc định:

- giữ source canonical trong repository;
- compile trên Overleaf bằng official IEEE template;
- export PDF về `releases/`.

Nếu cài local toolchain, phải có phê duyệt riêng. Sau khi có:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error manuscript/main.tex
```

Không dùng project Python để thay thế LaTeX compiler. Các script kiểm claim/hash/page metadata, nếu tạo, phải chạy bằng:

```text
/home/quannda/miniconda3/envs/benchmark_env/bin/python
```

### 10.2. Check dự kiến

- missing citation/reference;
- unresolved `TODO`/`TBD`/`\ref`;
- page count;
- claim IDs thiếu evidence;
- số liệu xuất hiện không khớp snapshot;
- figure/table không được nhắc trong text;
- template guidance text còn sót;
- PDF/source hash.

## 11. Allowed writes sau khi plan được duyệt

- `kse_submit_manuscript/manuscript/`
- `kse_submit_manuscript/notes/`
- `kse_submit_manuscript/snapshots/`
- `kse_submit_manuscript/releases/`
- `kse_submit_manuscript/README.md`
- `kse_submit_manuscript/template_source_verification.md`
- `experiments/20260722_000940/reports/*paper-update-packet*`
- roadmap/README/ARCHITECTURE khi status/ownership thay đổi;
- coordination log và handoff tương ứng.

Không sửa kết quả experiment để làm claim đẹp hơn. Không ghi đè PDF/source đã gửi giáo sư; mỗi release có version và hash.

## 12. Quyết định cần chốt ngay khi duyệt

1. Main Session hay ELLMA?
2. Author list, thứ tự, affiliation và corresponding author?
3. Working title và tối đa ba contributions?
4. Review policy/anonymity trên CMT?
5. RQ3 có đủ khả năng hoàn thành trước results cutoff 29/07 không?
6. Dữ liệu/candidate nào được phép mô tả hoặc minh họa trong paper?
7. Ai là người compile trên Overleaf và ai là người submit CMT?

## 13. Cổng hoàn thành plan viết paper

Plan chỉ `COMPLETED` khi:

1. source LaTeX canonical tồn tại và compile bằng official template;
2. professor-review release đã được tạo và gửi;
3. feedback được ghi, xử lý hoặc disposition;
4. submission candidate không quá 6 trang;
5. mọi claim quan trọng có evidence;
6. provisional claim không bị báo như final;
7. giáo sư/project lead duyệt bản cuối;
8. receipt/submission ID được người nộp ghi lại.

Plan có thể hoàn thành phần authoring dù submission bị chặn bởi quyết định của tác giả; khi đó phải báo đúng blocker, không tự submit.
