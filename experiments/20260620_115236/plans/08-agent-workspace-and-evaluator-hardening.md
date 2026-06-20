# P08 — Agent workspace isolation and evaluator integrity

## Trạng thái

- Status: `BACKLOG_POST_POC`
- Approval: `NOT_APPROVED`
- Implementation timing: sau phase PoC, trước khi chạy nhiều write-capable agent song song hoặc dùng evaluator cho quyết định có hệ quả
- Priority: deferred hardening
- Dependencies: P01; cần đồng bộ thiết kế với P06 dataset tooling và P07 evaluation pipeline
- Blocks: production-scale parallel agent execution và automated quality gates có tính quyết định
- Implementation owner: AI engineering/orchestrator
- Security reviewer: project lead hoặc reviewer độc lập không phải producer của cùng thay đổi

File này là thiết kế để dành. Sự tồn tại của plan không cho phép triển khai. Trước khi bắt đầu phải đổi trạng thái thành `APPROVED` sau khi review lại runtime, threat model, chi phí vận hành và kiến trúc P06/P07 tại thời điểm đó.

## 1. Mục tiêu

Tạo cơ chế kỹ thuật để:

1. hai specialist không vô tình hoặc chủ ý ghi đè workspace/artifact của nhau;
2. producer agent không thể sửa validator, rubric, test hoặc evaluator nhằm làm output của chính nó đạt điểm;
3. mọi thay đổi ngoài phạm vi được phát hiện và làm delegation thất bại;
4. chỉ orchestrator/integrator được đưa artifact từ workspace cô lập vào nhánh chính;
5. mức bảo vệ thực tế được mô tả trung thực, không gọi Git worktree hoặc prompt instruction là security sandbox.

## 2. Ngoài phạm vi

P08 không:

- thay đổi benchmark taxonomy, rubric sư phạm hoặc tiêu chí đúng chuyên môn;
- thay expert teacher bằng automatic evaluator;
- xây distributed scheduler hoặc platform nhiều máy nếu quy mô chưa cần;
- bảo vệ trước administrator/root trên máy host;
- coi hidden test là bằng chứng duy nhất về chất lượng;
- tự động merge output của agent vào nhánh chính;
- chuyển runtime tương tác sang nested `codex exec`, `claude -p`, daemon hoặc tiến trình agent ẩn.

## 3. Rủi ro hiện tại

P01 hiện có plan ownership, `allowed writes`, coordination log và native observable thread. Đây là control ở tầng quy trình, chưa phải filesystem enforcement.

Các specialist hiện có thể cùng làm việc trên một repository checkout. Nếu runtime cấp quyền ghi toàn workspace thì agent về kỹ thuật vẫn có thể:

- sửa cùng một file với agent khác;
- sửa artifact đã được agent khác tạo;
- thay đổi `agents/**/scripts/`, test hoặc schema đánh giá;
- làm validator dễ hơn rồi tạo output đạt validator mới;
- để lại thay đổi ngoài phạm vi mà orchestrator không nhận ra nếu chỉ xem output cuối.

## 4. Threat model

### 4.1 Tác nhân

- **Producer specialist:** tạo artifact/code/dữ liệu được đánh giá.
- **Concurrent specialist:** thực hiện delegation khác trong cùng thời gian.
- **Orchestrator/integrator:** cấp scope, chạy gate, review diff và tích hợp kết quả.
- **Evaluator:** chạy validator/test/rubric độc lập với producer.
- **Human approver:** duyệt thay đổi evaluator và quyết định chuyên môn.

### 4.2 Sự cố cần ngăn hoặc phát hiện

- lost update và overwrite do hai agent sửa cùng path;
- ghi ngoài `allowed_writes`;
- symlink/path traversal để thoát output root;
- sửa evaluator hoặc test trong cùng delegation tạo sản phẩm;
- evaluator chạy trên code đã bị producer thay đổi;
- producer tự báo điểm mà không có lần chạy độc lập;
- stale workspace hoặc untracked file làm kết quả không tái lập;
- integration nhầm cả thay đổi không thuộc delegation.

### 4.3 Giả định tin cậy

- host, Git và orchestrator/integrator thuộc trusted computing base;
- producer specialist là untrusted đối với evaluator integrity;
- prompt compliance hữu ích nhưng không phải security boundary;
- Git worktree cách ly lịch sử làm việc và giảm xung đột vô ý, nhưng không ngăn agent truy cập path khác nếu filesystem permission vẫn cho phép;
- chỉ OS/container sandbox với allowlist thực sự mới được ghi nhận là filesystem enforcement.

## 5. Nguyên tắc bắt buộc

1. **One delegation, one writable root:** mỗi delegation có output/workspace ghi riêng.
2. **No overlapping leases:** không chạy song song hai delegation có write set giao nhau.
3. **Producer cannot mutate evaluator:** evaluator path là read-only hoặc hoàn toàn không được mount vào producer workspace.
4. **Independent evaluation:** orchestrator/evaluator chạy đánh giá sau khi producer kết thúc, từ trusted evaluator revision.
5. **Fail closed:** không chứng minh được isolation hoặc integrity thì dừng, chuyển sang single-writer tuần tự.
6. **Artifact promotion, not shared editing:** producer bàn giao patch/artifact; integrator mới promote vào repository chính.
7. **Evaluator changes are separate:** thay evaluator phải dùng task/plan/PR riêng và không được đồng thời tạo output đang được evaluator đó chấm.
8. **Human authority remains:** gate kỹ thuật không thay quyết định chuyên môn của expert teacher.

## 6. Thiết kế đề xuất

### 6.1 Delegation manifest

Trước khi spawn specialist, orchestrator tạo manifest bất biến hoặc append-only gồm tối thiểu:

- `delegation_id`;
- base commit SHA;
- agent/specialist name;
- declared inputs;
- `allowed_reads`;
- `allowed_writes`;
- `protected_paths`;
- isolation mode và enforcement level;
- evaluator revision/hash;
- expected outputs;
- timeout/status;
- integration owner.

Manifest phải được validate trước khi chạy. Path được canonicalize; path tuyệt đối ngoài root, `..`, symlink escape và write-set overlap bị từ chối.

### 6.2 Write-set lease

Orchestrator duy trì lease registry theo canonical path:

- path cha và path con được coi là overlap;
- lease chỉ được cấp sau validation;
- delegation hoàn tất/thất bại mới giải phóng lease;
- lease stale cần explicit recovery và audit event;
- nếu runtime không hỗ trợ enforcement, mọi write-capable delegation chạy tuần tự.

Lease ngăn scheduler tạo xung đột; nó không thay filesystem sandbox.

### 6.3 Workspace isolation

Mỗi delegation dùng một checkout/worktree và branch riêng, tên gắn với `delegation_id`. Shared main working tree là read-only đối với specialist.

Mức bảo vệ phải được ghi trong report:

| Level | Cơ chế | Được phép tuyên bố |
|---|---|---|
| L0 | Prompt/allowed-writes instruction | Quy ước, không có isolation kỹ thuật |
| L1 | Git worktree riêng + write-set lease | Tránh xung đột vô ý và dễ audit |
| L2 | Filesystem/container sandbox với writable allowlist | Enforced workspace isolation |

Production-scale parallel writes yêu cầu L2. Nếu native runtime không hỗ trợ L2 mà vẫn giữ observable specialist thread, hệ thống phải fail closed hoặc chạy single-writer tuần tự; không được âm thầm hạ cấp rồi gọi là isolated.

### 6.4 Artifact handoff và integration

Producer chỉ trả về:

- artifact trong output root;
- patch/diff giới hạn bởi manifest;
- provenance và command đã chạy;
- open questions/limitations.

Integrator thực hiện:

1. kiểm tra base SHA và workspace cleanliness;
2. so sánh actual changed paths với `allowed_writes`;
3. từ chối protected-path mutation;
4. chạy evaluator độc lập;
5. review patch;
6. promote/cherry-pick có chọn lọc;
7. ghi coordination event và handoff.

Không merge nguyên branch của specialist nếu chưa qua path gate và integrity gate.

### 6.5 Protected evaluator boundary

Danh sách protected paths ban đầu phải bao gồm tối thiểu:

- `agents/**/scripts/**` khi script dùng để validate sản phẩm;
- `tests/**` liên quan quality gate;
- future rubric, judge prompt, scoring code và evaluation fixtures của P07;
- schema/contract quyết định pass/fail;
- CI workflow chạy evaluator.

Trong producer delegation, các path này phải read-only hoặc absent. Trước khi chạy, orchestrator ghi trusted revision và digest. Sau khi producer kết thúc:

- bất kỳ mutation nào ở protected path làm delegation thất bại;
- evaluator được load từ trusted clean checkout, không từ producer branch;
- score do producer tự chạy chỉ là diagnostic, không phải acceptance result;
- acceptance result phải kèm evaluator revision, input artifact digest và command/output log.

### 6.6 Quy trình thay đổi evaluator

Thay validator/rubric/scoring code phải:

1. có issue/plan hoặc change request riêng;
2. giải thích lỗi evaluator hoặc requirement mới;
3. thêm regression test chống nới lỏng ngoài ý muốn;
4. được reviewer độc lập duyệt;
5. không chấm lại output do cùng agent tạo trong cùng task mà không có human review;
6. version evaluator để score cũ vẫn truy vết được;
7. ghi rõ score giữa hai evaluator version có so sánh được hay không.

Với tiêu chí chuyên môn/sư phạm, expert teacher phải tham gia duyệt thay đổi; test kỹ thuật không thay thế phán quyết này.

### 6.7 Independent evaluation runner

Runner tối thiểu nhận:

- immutable artifact path hoặc artifact digest;
- evaluator version/revision;
- environment identity;
- command timeout;
- output report path.

Runner không cấp write permission vào evaluator source. Report phải chứa pass/fail, lỗi, version, digest và timestamp; không chỉ chứa một score tổng hợp.

## 7. Các giai đoạn triển khai dự kiến

### Stage A — Capability audit và ADR

- kiểm tra Codex/Claude runtime tại thời điểm triển khai hỗ trợ cwd, sandbox và writable allowlist đến đâu;
- xác định L2 có thể giữ native observable thread hay không;
- lập ADR chọn isolation backend và fallback policy;
- benchmark chi phí tạo worktree/sandbox.

### Stage B — Contracts và static gates

- định nghĩa delegation manifest schema;
- canonical path/overlap validator;
- protected-path policy;
- lease registry và stale recovery contract;
- cập nhật coordination event/handoff contract nếu cần.

### Stage C — Isolated execution và integration gate

- tạo/dọn workspace theo delegation ID;
- áp dụng read/write mount policy;
- thu actual diff và provenance;
- từ chối out-of-scope changes;
- chỉ integrator được promote artifact.

### Stage D — Evaluator integrity

- tách evaluator execution khỏi producer workspace;
- digest/version evaluator và artifact;
- thêm independent evaluation report;
- thêm review policy cho evaluator changes.

### Stage E — Migration và rollout

- pilot với hai specialist P01 ở chế độ không song song;
- chạy fault-injection tests;
- sau khi đạt acceptance mới bật parallel writes;
- cập nhật README, ARCHITECTURE, AGENTS và operator runbook.

## 8. Test và fault injection

Phải có automated/integration tests cho ít nhất các trường hợp:

1. Hai delegation xin ghi cùng file: delegation thứ hai bị từ chối trước khi spawn.
2. Một delegation xin ghi thư mục cha, delegation khác xin ghi thư mục con: phát hiện overlap.
3. Producer sửa file ngoài `allowed_writes`: integration thất bại.
4. Producer sửa validator/test/protected schema: kết quả bị từ chối dù output pass.
5. Producer tạo symlink trỏ ra ngoài output root: write/promotion bị từ chối.
6. Producer tự báo pass nhưng independent evaluator fail: acceptance là fail.
7. Evaluator source trong producer branch bị sửa: trusted clean evaluator vẫn được dùng và mutation được báo cáo.
8. Workspace bắt đầu từ sai base SHA hoặc chứa file stale: fail closed.
9. Agent/runtime không hỗ trợ L2: scheduler chuyển sang single-writer hoặc dừng, không chạy parallel.
10. Integrator chỉ promote allowlisted artifact, không mang theo untracked file khác.
11. Evaluator version thay đổi: report ghi version mới và không âm thầm so sánh score không tương thích.
12. Cleanup thất bại: workspace được quarantine và lease không bị tái sử dụng thiếu audit.

## 9. Observability và audit

Mỗi delegation phải truy vết được:

- ai/agent nào được giao;
- base commit và workspace ID;
- declared/actual writes;
- lease acquisition/release;
- isolation level thực tế;
- protected-path digest trước/sau;
- evaluator version và artifact digest;
- integration decision;
- cleanup/quarantine result.

Audit log không chứa hoặc tuyên bố chứa private chain-of-thought.

## 10. Deliverables dự kiến

Tên/path dưới đây là đề xuất, phải xác nhận lại khi P08 được duyệt:

```text
docs/decisions/
└── ADR-agent-isolation-backend.md
coordination/
├── schemas/delegation-manifest.schema.json
└── policies/protected-paths.yaml
src/orchestration/
├── leases/
├── workspace/
└── integration/
src/evaluation/
└── runner/
tests/hardening/
└── ...
```

P08 có thể tái sử dụng hoặc migrate contract hiện ở `experiments/_templates/`, nhưng không được di chuyển/xóa chúng nếu chưa có migration plan và cập nhật toàn bộ consumer.

## 11. File ownership khi triển khai

P08 dự kiến sở hữu:

- isolation/lease/integration-gate code;
- evaluator runner boundary;
- hardening tests và fault-injection fixtures;
- ADR/runbook/policy do P08 tạo;
- thay đổi tài liệu kiến trúc liên quan.

P08 không được tự ý thay đổi:

- nội dung benchmark/rubric do P05/P07 và expert teachers sở hữu;
- artifact nghiên cứu P02;
- teacher packet P04;
- validator semantics hiện có nếu không có evaluator change request riêng;
- user data hoặc unrelated working-tree changes.

## 12. Acceptance criteria

- Không có hai write-capable delegation song song với write set overlap.
- Production parallel mode đạt L2; nếu không đạt thì fail closed/single-writer.
- Producer không có quyền ghi evaluator/protected paths.
- Actual changed paths được machine-check với manifest trước integration.
- Independent evaluator chạy từ trusted revision và report đủ version/digest.
- Mọi protected-path mutation làm delegation thất bại.
- Fault-injection suite ở Mục 8 pass.
- Không có auto-merge từ specialist workspace.
- Evaluator change có separate review và regression test.
- README, ARCHITECTURE, AGENTS và runbook mô tả đúng mức enforcement thực tế.
- Có rollback/quarantine procedure và audit trail tái lập được.

## 13. Rollback và vận hành sự cố

- Tắt parallel scheduler và quay về single-writer khi isolation backend lỗi.
- Quarantine workspace có integrity violation; không tái sử dụng artifact trước review.
- Release lease bằng audited recovery, không xóa cưỡng bức thiếu record.
- Không promote patch khi base SHA, digest hoặc evaluator revision không khớp.
- Khi phát hiện evaluator compromise, invalidate các acceptance result bị ảnh hưởng và chạy lại từ trusted revision sau human review.

## 14. Câu hỏi cần review lại trước approval

1. Native runtime khi đó có hỗ trợ L2 allowlist mà vẫn giữ thread quan sát được không?
2. Worktree nằm trong hay ngoài repository root để vừa dễ cleanup vừa không mở rộng sandbox?
3. Protected-path policy nên dùng YAML, TOML hay generated manifest?
4. P07 sẽ đặt rubric/judge/scoring code ở đâu và phần nào cần expert-teacher approval?
5. Có cần hidden holdout evaluator hay chỉ cần immutable independent evaluator ở scale đầu tiên?
6. Artifact store dùng filesystem content-addressed hay object storage?
7. Ai là reviewer độc lập khi thay evaluator trong nhóm nhỏ?

## 15. Quyết định duyệt

Ở thời điểm hiện tại: giữ `BACKLOG_POST_POC`, không triển khai.

Sau PoC, người dùng có thể:

- đổi thành `APPROVED` sau capability audit và review scope;
- tách workspace isolation và evaluator integrity thành hai plan nếu P06/P07 phát triển khác nhịp;
- tiếp tục single-writer mode và hoãn parallel execution;
- hủy plan nếu runtime/platform cung cấp isolation được kiểm chứng tương đương.
