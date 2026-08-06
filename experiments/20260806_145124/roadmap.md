# Roadmap — Cải tổ repository để con người và agent cùng vận hành được

Experiment: `20260806_145124`
Trạng thái: `PLANNING — AWAITING PLAN 01 APPROVAL`
Nguồn hiện trạng chính: `20260727_170150`

## 1. Mục tiêu

Experiment này tổ chức lại repository mà không thay đổi nội dung benchmark.
Kết quả đích là một codebase trong đó:

- con người tìm được artifact chuẩn mà không phải lần theo nhiều experiment;
- `src/` chứa logic tái sử dụng, còn `scripts/` chỉ là entry point mỏng;
- mỗi run có config, runbook, provenance và output dễ truy vết;
- plan đủ cô đọng để duyệt, còn trạng thái chi tiết dành cho máy đọc;
- môi trường Python và import có thể dựng lại trên máy sạch;
- output lớn, snapshot lặp và file tạm không tiếp tục làm phình Git.

Đây là experiment quản trị và kỹ thuật. Nó không có thẩm quyền xác nhận
nhãn sư phạm, sửa rubric, thay đổi sample, hoặc thay quyết định của UET/HNMU.

## 2. Nguyên tắc triển khai

1. Duyệt tuần tự: chỉ triển khai plan đang có dòng trạng thái `APPROVED`.
2. Mỗi plan có phạm vi ghi riêng và phải hoàn tất gate trước khi mở plan sau.
3. Baseline plan được giữ ổn định sau khi duyệt. Thay đổi tình thế được ghi
   theo thời gian trong amendment; không bắt người đọc theo một đồ thị quan hệ.
4. Quan hệ kỹ thuật giữa baseline, amendment, commit và artifact được để trong
   metadata máy đọc do Plan 01 quy định.
5. Không di chuyển hoặc xóa artifact chỉ vì tên/path có vẻ trùng. Mọi migration
   phải có inventory, checksum, consupp;mer audit và cách rollback.
6. Artifact chuẩn dùng chung chỉ được `promote` sau khi xác định authority,
   version, schema, provenance, quyền chia sẻ và trạng thái phê duyệt.
7. Không gọi API trả phí trong experiment này nếu một plan sau không nêu rõ và
   project lead không phê duyệt riêng. Roadmap hiện tại không cần API trả phí.

## 3. Kiến trúc đích

```text
README.md                     onboarding và trạng thái ngắn gọn
ARCHITECTURE.md               kiến trúc đang có hiệu lực
docs/decisions/               ADR cho quyết định kiến trúc dài hạn

src/edu_benchmark/            thư viện Python tái sử dụng
scripts/                      CLI/wrapper mỏng gọi thư viện
tests/                        test theo package đã cài

shared/
  benchmark/                  artifact benchmark chuẩn, có version và registry
  learning_resources/         học liệu dùng chung hiện hành
  prompts/                    prompt/bundle dùng chung có version
  raw_data/                   dữ liệu nguồn theo chính sách quyền truy cập

experiments/<YYYYMMDD_HHMMSS>/
  metadata.yaml               định danh và provenance cấp experiment
  roadmap.md                  trình tự plan và trạng thái cấp cao
  plans/                      baseline được duyệt theo thứ tự
  decisions/                  amendment theo thời gian của experiment
  configs/                    cấu hình run, không chứa secret
  runbooks/                   lệnh vận hành cụ thể của experiment
  outputs/                    kết quả run, không mặc nhiên là canonical
  reports/                    diễn giải kết quả
  handoffs/                   bàn giao ngắn gọn tại các gate
  coordination/               sự kiện máy đọc
```

ID experiment tiếp tục dùng timestamp `YYYYMMDD_HHMMSS`. `metadata.yaml` bổ
sung `slug` và `title` để con người hiểu mục đích. `runbooks/` lưu preflight,
lệnh chạy/resume/validate, config sử dụng và output dự kiến; không chứa logic
nghiệp vụ, secret, raw output hay bài phân tích kết quả.

## 4. Artifact benchmark dùng chung dự kiến

Plan 03 sẽ kiểm chứng rồi mới tạo cấu trúc này:

```text
shared/benchmark/
  README.md
  artifact_registry.csv
  checklists/raw_dialogue/v1/
    criteria.csv
    checklist.md
    manifest.json
  datasets/phase1_pass_dialogues/v1/
    dialogues.csv
    manifest.json
  datasets/candidate_pool/v1/
    candidates.csv
    trace.csv
    dispositions.csv
    manifest.json
  selections/provisional_evaluation_pool/v1/
    selection.csv
    requirement_scores.csv
    manifest.json
  specifications/
    tutor_capabilities/v0/
    pedagogical_principles/v0/
    rubric_library/v0/
```

Ý nghĩa các tập phải được giữ chính xác:

- `phase1_pass_dialogues/v1`: 665 hội thoại đã qua Phase 1, không phải raw gốc;
- `candidate_pool/v1`: 2.028 candidate được chuyển đổi từ 665 dialogue family
  và đã qua validation conversion; “pool” chỉ có nghĩa chưa áp lọc Plan 03;
- `provisional_evaluation_pool/v1`: selection 1.400 candidate từ pool 2.028,
  thuộc 655 family, cùng 628 candidate cần review và 0 blocked trong phân tích
  hiện hành; đây chưa phải benchmark đã freeze;
- selection chuẩn chỉ cần ID, disposition, lý do và provenance. Bảng 1.400 dòng
  đầy đủ có thể dựng bằng join thay vì sao chép thêm một dataset lớn.

Nếu dữ liệu không được phép lưu trong Git, registry và manifest vẫn được track,
còn payload được đặt tại kho được phép và manifest ghi locator/checksum.

## 5. Trình tự các plan


| Thứ tự | Plan                                                                                                                       | Trạng thái | Gate mở plan kế tiếp                                                                |
| -------: | -------------------------------------------------------------------------------------------------------------------------- | ------------ | -------------------------------------------------------------------------------------- |
|       01 | [Quản trị plan và bản ghi quyết định](plans/01-planning-governance-and-decision-records.md)                         | `DRAFT`      | Template, status machine-readable, amendment và artifact budget được duyệt        |
|       02 | [Đóng gói Python và kiểm chứng môi trường sạch](plans/02-python-packaging-and-clean-environment-validation.md)   | `DRAFT`      | Import/package/test chạy bằng`benchmark_env`; CI tối thiểu không gọi API         |
|       03 | [Registry và promotion artifact benchmark dùng chung](plans/03-shared-benchmark-artifact-registry-and-promotion.md)      | `DRAFT`      | Registry, manifest và các count/provenance được đối chiếu; authority rõ ràng |
|       04 | [Config, runbook và path khả chuyển](plans/04-experiment-configs-runbooks-and-portable-paths.md)                        | `DRAFT`      | Run đại diện preflight được từ repo root, không absolute path/secret           |
|       05 | [Tách ranh giới `src/` và `scripts/`](plans/05-src-scripts-boundary-and-runtime-refactor.md)                            | `DRAFT`      | CLI mỏng, logic dùng lại trong package, compatibility và test đạt                |
|       06 | [Retention output, khử trùng lặp và vệ sinh repo](plans/06-output-retention-deduplication-and-repository-hygiene.md)  | `DRAFT`      | Inventory đối chiếu, archive/ignore policy áp dụng, xóa chỉ sau duyệt riêng   |
|       07 | [Đồng bộ tài liệu, validation và đóng migration](plans/07-documentation-reconciliation-validation-and-closeout.md) | `DRAFT`      | Clean-clone drill, docs/current-state và final report được duyệt                  |

Project lead duyệt theo đúng thứ tự trên. Một plan được duyệt không tự động
duyệt plan kế tiếp.

## 6. Cách quản trị thay đổi tình thế

Người đọc chỉ cần theo timeline trong roadmap, amendment và handoff. Plan 01
sẽ thiết lập lớp máy đọc tối thiểu, ví dụ:

```yaml
plan_id: P05
baseline: plans/05-src-scripts-boundary-and-runtime-refactor.md
status: in_progress
current_step: compatibility_validation
last_amendment: P05-A002
```

Amendment dùng số tăng dần khi phát sinh (`P05-A001`, `P05-A002`, ...), không
cần đoán trước số work package. Nếu cần lưu quan hệ chi tiết, trường
`after_event`, `supersedes` hoặc `affected_scope` nằm trong YAML/JSONL cho máy;
phần Markdown chỉ ghi quyết định, lý do, ảnh hưởng và thứ tự thời gian.

## 7. Gate chung cho mọi plan

Trước khi triển khai:

- trạng thái plan phải là `APPROVED` và ghi ngày/người duyệt;
- working tree được kiểm tra để tránh đè thay đổi của người dùng;
- phạm vi ghi và rollback được xác nhận;
- mọi thao tác xóa/ghi đè/di chuyển hàng loạt cần duyệt rõ ràng.

Trước khi hoàn tất:

- chạy validator/test liên quan bằng
  `/home/quannda/miniconda3/envs/benchmark_env/bin/python` trên Linux;
- đối chiếu artifact/count/checksum theo acceptance criteria;
- cập nhật status, amendment nếu có, coordination log và handoff;
- chỉ cập nhật `README.md`/`ARCHITECTURE.md` khi thay đổi đã thực sự có hiệu lực.

## 8. Ngoài phạm vi

- Không sửa nhãn của 665/2.028/1.400 mẫu.
- Không xác nhận 628 review item hay rubric thay UET/HNMU.
- Không viết lại lịch sử Git hoặc dùng Git LFS như giải pháp mặc định.
- Không xóa output lớn trong lúc lập kế hoạch.
- Không tái chạy model/judge để chứng minh migration nếu có thể kiểm offline.
- Không biến mọi report cũ thành shared artifact; chỉ promote sản phẩm ổn định.

## 9. Cổng dừng hiện tại

Tất cả bảy plan đang là bản nháp. Chỉ Plan 01 được đưa ra duyệt đầu tiên.
Cho đến khi Plan 01 được project lead đổi rõ ràng sang `APPROVED`, experiment
này không cho phép thay đổi code, di chuyển dữ liệu, tạo packaging, sửa CI,
hoặc dọn file cũ.
