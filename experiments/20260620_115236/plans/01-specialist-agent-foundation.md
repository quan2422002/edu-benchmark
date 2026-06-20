# P01 — Specialist-agent foundation

## Trạng thái

- Status: `IMPLEMENTED_PENDING_FRESH_SESSION_TEST`
- Approved at: `2026-06-20`
- Project environment: `benchmark_env` (`/home/quannda/miniconda3/envs/benchmark_env`)
- Priority: urgent
- Dependency: none
- Blocks: P02 literature review
- Implementation owner: AI engineering/orchestrator

## 1. Mục tiêu

Xây nền tảng agent tối thiểu, dùng được ngay cho PoC nhưng không khóa dự án vào riêng Codex hoặc Claude. Chỉ triển khai hai agent có nhu cầu đã xác nhận:

1. `research-methodologist`: thực hiện evidence-based literature review.
2. `teacher-collaboration-designer`: chuyển bằng chứng nghiên cứu thành chỉ dẫn/task dễ thực thi cho expert teachers.

Không xây cả tám agent trong plan cũ ở giai đoạn này.

Specialist phải được orchestrator spawn bằng cơ chế subagent native của phiên tương tác. P01 không dùng `codex exec`, `claude -p` hoặc một tiến trình CLI ẩn làm runtime mặc định cho specialist. PoC hiện tại chạy và smoke-test trên Codex; Claude adapter vẫn được xây nhưng chưa chạy runtime test.

## 2. Ranh giới trách nhiệm

### `research-methodologist`

- thiết kế search/review protocol;
- tìm, sàng lọc và trích xuất bằng chứng;
- duy trì evidence matrix và bibliography;
- phân biệt evidence, inference và open question;
- chỉ đề xuất benchmark requirement khi có nguồn truy vết được.

Agent không được tự coi taxonomy do nó tạo là ground truth và không thay giáo viên phán quyết tính phù hợp sư phạm.

### `teacher-collaboration-designer`

- chuyển requirement thành task card, checklist và ví dụ dễ hiểu;
- phân tách nhiệm vụ author, reviewer và adjudicator;
- tránh thuật ngữ kỹ thuật không cần thiết;
- thu nhận và cấu trúc phản hồi của giáo viên cho AI engineers.

Agent không được tự xác nhận nội dung chuyên môn thay giáo viên.

## 3. Cấu trúc file dự kiến

```text
agents/
├── research-methodologist/
│   ├── SKILL.md
│   ├── scripts/
│   │   └── validate_evidence_matrix.py
│   └── references/
│       ├── review-protocol.md
│       └── evidence-schema.md
└── teacher-collaboration-designer/
    ├── SKILL.md
    ├── scripts/
    │   └── validate_teacher_packet.py
    └── references/
        ├── plain-language-guidelines.md
        └── task-card-schema.md

.agents/skills/
└── <generated or linked skill adapters>

.codex/agents/
├── research-methodologist.toml
└── teacher-collaboration-designer.toml

.claude/agents/
├── research-methodologist.md
└── teacher-collaboration-designer.md

experiments/<run-id>/coordination/
├── delegations.jsonl
└── handoffs/

README.md
ARCHITECTURE.md
AGENTS.md
```

`agents/<name>/` là nguồn nội dung trung lập nền tảng. Adapter không được chứa logic nghiên cứu riêng; nếu có khác biệt runtime, chỉ cấu hình cách khởi chạy và quyền.

Ba tài liệu root có vai trò khác nhau và không được sao chép toàn bộ nội dung của nhau:

- `README.md`: cửa vào ngắn gọn cho thành viên mới, trả lời dự án là gì, đang ở trạng thái nào và bắt đầu từ đâu.
- `ARCHITECTURE.md`: nguồn chuẩn về cấu trúc thành phần, dependency, runtime, delegation, observability và ranh giới human/agent.
- `AGENTS.md`: chỉ dẫn vận hành dành cho Codex/orchestrator, được máy tự nạp; tham chiếu `ARCHITECTURE.md` thay vì lặp lại giải thích dài.

## 4. Mô hình runtime và khả năng quan sát

### 4.1. Phân biệt cài đặt và chạy agent

Các lệnh Python trong Mục 5 chỉ chạy ở **thời điểm cài đặt** để tạo/validate file `SKILL.md`, references và scripts. Chúng không khởi chạy LLM, không tạo phiên nền và không phải kênh giao tiếp giữa orchestrator với specialist.

Runtime mặc định:

- người dùng tương tác với orchestrator trong một phiên Codex/Claude interactive;
- orchestrator dùng native Agent/subagent tool để spawn specialist đã đăng ký;
- specialist có thread/context riêng trong cùng runtime;
- orchestrator gửi task, nhận kết quả, steer hoặc stop qua native runtime;
- không chạy nested `codex exec`, `claude -p`, shell daemon hoặc terminal ẩn để giả lập subagent.

`codex exec` chỉ được phép trong một plan automation/CI riêng, có sự duyệt rõ ràng và log JSONL đầy đủ. Nó không thuộc P01 interactive orchestration.

### 4.2. Hành vi theo runtime

| Runtime             | Cách spawn mặc định                                    | Cách người dùng quan sát                                                   | Giới hạn/ghi chú                                                                                                    |
| ------------------- | ---------------------------------------------------------- | ------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Codex CLI           | Native custom agent/subagent thread                        | Dùng `/agent` để mở, inspect, steer, stop hoặc close thread              | Được chọn làm bề mặt chuẩn cho PoC Codex.                                                                      |
| Codex App           | Native subagent thread                                     | Agent activity và thread được hiển thị trong app                          | Có thể dùng thay CLI nếu UI hỗ trợ trong môi trường người dùng.                                            |
| Codex IDE Extension | Không được coi là bề mặt quan sát chuẩn trong P01 | Tài liệu hiện hành chưa bảo đảm hiển thị đầy đủ subagent activity | Nếu cần multi-agent có thể audit, chuyển phiên sang CLI/App; không âm thầm fallback sang `codex exec`.      |
| Claude Code CLI/UI  | Native project subagent qua Agent tool                     | Dự kiến dùng `/agents` → Running để mở hoặc stop agent                | Vẫn tạo `.claude/agents/`, nhưng runtime test được hoãn vì người dùng hiện không sử dụng Claude Code. |
| Claude agent teams  | Ngoài phạm vi PoC hiện tại                             | Không test                                                                     | Experimental; chỉ xem xét trong một plan tương lai khi người dùng bắt đầu sử dụng Claude Code.            |

Nếu runtime/surface hiện tại không hỗ trợ quan sát native thread, orchestrator phải dừng và thông báo giới hạn, sau đó đề xuất surface phù hợp. Không được tự thay thế bằng một subprocess khó quan sát.

### 4.3. Observability contract

Trước mỗi delegation, orchestrator phải nói trong parent thread:

- agent nào sắp được dùng;
- mục tiêu và phạm vi task;
- input artifact/path;
- quyền đọc/ghi;
- output dự kiến.

Mỗi delegation phải có record trong `experiments/<run-id>/coordination/delegations.jsonl`:

```json
{
  "timestamp": "ISO-8601",
  "event_type": "delegation_started",
  "delegation_id": "d-001",
  "parent_session": "runtime-visible-id-or-label",
  "agent": "research-methodologist",
  "task": "Short task statement",
  "input_paths": [],
  "allowed_write_paths": [],
  "status": "started",
  "native_thread_id": "if exposed by runtime",
  "output_paths": [],
  "summary": null,
  "open_questions": []
}
```

Log là append-only. Mỗi lần steer, stop, fail hoặc complete tạo một event mới cùng `delegation_id`; không ghi đè lịch sử. Khi agent hoàn thành hoặc được stop, orchestrator tạo handoff ngắn chứa:

- delegation prompt đã gửi;
- các steer/follow-up message đã gửi sau đó;
- artifact đã đọc/tạo;
- kết quả tóm tắt trả về;
- quyết định của orchestrator dựa trên kết quả;
- uncertainty và việc còn lại.

Mục tiêu là audit được message, tool activity, artifact và quyết định. P01 không hứa hiển thị private chain-of-thought/reasoning ẩn của model; phần này không phải transcript có thể hoặc nên yêu cầu công khai.

### 4.4. Quyền kiểm soát của người dùng

Người dùng phải có thể:

- biết khi nào agent được spawn;
- mở native agent thread trên surface được hỗ trợ;
- yêu cầu orchestrator steer, stop hoặc close agent;
- đối chiếu native transcript với coordination record;
- từ chối delegation và yêu cầu orchestrator tự làm task;
- bật chế độ `single-agent` để cấm spawn specialist trong phiên hiện tại.

## 5. Quy trình triển khai

1. Kích hoạt Conda environment `benchmark_env` và xác nhận `sys.executable` trỏ tới `/home/quannda/miniconda3/envs/benchmark_env/bin/python`.
2. Chạy `skill-creator` initializer cho từng skill với `scripts,references`.
3. Viết `SKILL.md` ngắn, imperative, frontmatter chỉ có `name` và `description`.
4. Chỉ thêm script cho validation xác định; không viết script cho phần suy luận nghiên cứu.
5. Viết adapter Codex và Claude từ cùng nguồn hướng dẫn canonical; chỉ Codex được runtime smoke-test trong PoC.
6. Viết `README.md`, `ARCHITECTURE.md` và `AGENTS.md` theo contract ở Mục 6.
7. Tạo prompt fixtures để kiểm tra trigger đúng/sai.
8. Chạy quick validation, unit tests, documentation checks và forward-test agent.

Các command sau chỉ scaffold/validate file ở build time; chúng không chạy specialist agent:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  /home/quannda/.codex/skills/.system/skill-creator/scripts/init_skill.py \
  research-methodologist \
  --path agents \
  --resources scripts,references \
  --interface display_name="Research Methodologist" \
  --interface short_description="Evidence-based literature review for tutoring benchmarks" \
  --interface default_prompt="Conduct a traceable literature review before proposing benchmark requirements."

/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  /home/quannda/.codex/skills/.system/skill-creator/scripts/init_skill.py \
  teacher-collaboration-designer \
  --path agents \
  --resources scripts,references \
  --interface display_name="Teacher Collaboration Designer" \
  --interface short_description="Create clear human-in-the-loop tasks for expert teachers" \
  --interface default_prompt="Turn research requirements into plain-language teacher tasks and review workflows."

/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  /home/quannda/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  agents/research-methodologist

/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  /home/quannda/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  agents/teacher-collaboration-designer

/home/quannda/miniconda3/envs/benchmark_env/bin/python -m pytest tests/agents -q
```

Không dùng `/home/quannda/miniconda3/bin/python` (Conda base) cho project validation. Đường dẫn script hệ thống phải được kiểm tra lại khi triển khai; nếu runtime khác, dùng equivalent initializer/validator nhưng vẫn chạy qua `benchmark_env` và giữ cùng artifact contract.

## 6. Contract tài liệu repository

### 6.1. `README.md` — Tổng quan hệ thống hiện tại

Đối tượng đọc: người mới vào dự án, giáo sư, AI engineers và expert teachers cần hiểu bức tranh chung.

Nội dung bắt buộc:

1. Tên và mục tiêu dự án: benchmark gia sư LLM môn Tin học lớp 9 bằng tiếng Việt.
2. Trạng thái hiện tại: PoC; literature review và teacher workflow đang được xây, taxonomy/dataset chưa phải bản chính thức.
3. Hai nhóm con người và ranh giới trách nhiệm: AI engineers, expert teachers.
4. Hai specialist agent trong P01 và vai trò ngắn gọn.
5. Sơ đồ luồng ở mức cao: user → orchestrator → specialist → artifact → human review.
6. Cấu trúc thư mục quan trọng, chỉ mô tả những phần đã tồn tại hoặc được P01 tạo.
7. Cách sử dụng PoC trên Codex CLI/App, gồm native subagent và `/agent`.
8. Cảnh báo không dùng `codex exec` làm specialist runtime tương tác.
9. Link đến `ARCHITECTURE.md`, roadmap và các plan đang active.
10. Cách chạy validation/tests của P01.
11. Trạng thái hỗ trợ runtime: Codex tested; Claude adapter generated/static-validated nhưng runtime test deferred.

README không chứa toàn bộ schema, protocol literature hoặc chi tiết từng agent. Các phần đó chỉ được tóm tắt và link tới nguồn chuẩn.

### 6.2. `ARCHITECTURE.md` — Kiến trúc hệ thống

Đối tượng đọc: AI engineers, orchestrator maintainers và người audit hệ thống.

Nội dung bắt buộc:

1. Mục tiêu kiến trúc và các nguyên tắc: human-in-the-loop, modular plans, native observable delegation, platform adapters.
2. System context: user/project lead, orchestrator, specialist agents, expert teachers, repository artifacts và external literature sources.
3. Component map và ownership:
   - canonical agent definitions;
   - Codex/Claude adapters;
   - experiment plans và coordination logs;
   - teacher-facing artifacts;
   - phần chưa được xây như dataset/evaluation pipeline.
4. Runtime sequence cho một delegation, từ thông báo trước khi spawn đến handoff và human decision.
5. Observability model: native thread, append-only delegation events, artifact paths và giới hạn không hiển thị private chain-of-thought.
6. Security/quyền tối thiểu: read/write scope, fail-closed, single-agent fallback và cấm subprocess specialist ẩn.
7. Human-in-the-loop boundaries: agent đề xuất/tổng hợp; expert teacher quyết định chuyên môn/sư phạm.
8. Dependency direction và file ownership để plan sau không sửa chồng chéo.
9. Runtime support matrix cho Codex/Claude, gồm trạng thái tested/deferred.
10. Extension points cho agent/runtime mới nhưng không mô tả chúng như đã tồn tại.
11. Known limitations và open architectural decisions.

Ưu tiên Mermaid cho tối đa hai sơ đồ nhỏ nếu renderer hỗ trợ; luôn kèm mô tả chữ để tài liệu vẫn hiểu được khi không render Mermaid.

### 6.3. `AGENTS.md` — Chỉ dẫn bắt buộc cho orchestrator

Đối tượng đọc: Codex và các coding agents làm việc trong repository.

Nội dung bắt buộc, ngắn và có tính thực thi:

- đọc roadmap/plan active trước khi sửa file;
- không triển khai plan chưa `APPROVED`;
- chỉ sửa path thuộc file ownership của plan;
- thông báo trước khi spawn specialist;
- dùng native subagent thread, không dùng nested `codex exec`/`claude -p`;
- ghi coordination event/handoff theo contract;
- fail closed hoặc dùng `single-agent` khi surface không quan sát được subagent;
- không thay expert teacher phán quyết chuyên môn;
- chạy test liên quan và cập nhật tài liệu khi kiến trúc thay đổi;
- bảo toàn thay đổi không liên quan của người dùng.

`AGENTS.md` không phải bản sao README/ARCHITECTURE. Nó link tới hai file này cho phần giải thích.

### 6.4. Các file Markdown khác được cân nhắc

Không tạo mặc định trong P01:

| File                | Quyết định PoC       | Khi nào tạo                                                                                             |
| ------------------- | ----------------------- | --------------------------------------------------------------------------------------------------------- |
| `CONTRIBUTING.md` | Defer                   | Khi có contributor ngoài nhóm lõi hoặc quy trình PR/review ổn định.                              |
| `SECURITY.md`     | Defer                   | Trước public release hoặc khi xử lý dữ liệu/API credential nhạy cảm.                             |
| `CHANGELOG.md`    | Defer                   | Khi bắt đầu phát hành version/tag; hiện dùng Git history và experiment reports.                   |
| `GLOSSARY.md`     | Defer                   | Khi thuật ngữ Việt–Anh/giáo dục xuất hiện lặp lại và gây hiểu sai ở ít nhất hai artifact. |
| `DECISIONS.md`    | Không dùng file đơn | Khi cần ADR, tạo `docs/decisions/NNNN-title.md` để mỗi quyết định độc lập.                   |
| `CONTRIBUTORS.md` | Không cần             | Chỉ tạo nếu có yêu cầu attribution ngoài Git history.                                              |

Skill folders không có README riêng; theo skill convention, chúng chỉ chứa `SKILL.md` và resource cần thiết.

### 6.5. Chính sách đồng bộ tài liệu

- Thay đổi component/runtime/file ownership phải cập nhật `ARCHITECTURE.md` trong cùng commit.
- Thay đổi onboarding, command hoặc trạng thái PoC phải cập nhật `README.md`.
- Thay đổi quy tắc agent phải cập nhật `AGENTS.md` và test tương ứng.
- Mỗi tài liệu có mục “Last verified” trỏ tới plan/commit, nhưng không ghi tay danh sách changelog dài.
- Link nội bộ phải dùng relative path và được kiểm tra tự động.

## 7. Test cases

### Trigger positive

- “Tổng hợp literature về benchmark đánh giá LLM tutor và tạo evidence matrix.”
- “Tạo nhiệm vụ author/reviewer rõ ràng cho nhóm giáo viên từ các research findings này.”

### Trigger negative

- “Sửa lỗi unit test Python.”
- “Chạy benchmark model trên dataset.”

### Forward tests

- Research agent nhận 5 paper thô và phải tạo matrix có source, method, human role, limitations.
- Teacher agent nhận một đoạn research synthesis và phải tạo task card không yêu cầu giáo viên dùng code/YAML.
- Cả hai agent phải ghi rõ uncertainty và phần cần con người quyết định.

### Runtime/observability smoke tests

1. Mở một phiên Codex CLI interactive, yêu cầu orchestrator spawn `research-methodologist` bằng native subagent tool.
2. Xác nhận thread xuất hiện trong `/agent`, có thể mở và steer từ parent session.
3. Xác nhận không có process `codex exec` được orchestrator tạo ra.
4. Xác nhận delegation record chứa task, native thread ID/label nếu runtime cung cấp và output path.
5. Static-check Claude adapter: đủ frontmatter/trường bắt buộc, tham chiếu đúng canonical instructions và không chứa logic lệch khỏi agent gốc.
6. Không khởi chạy Claude Code hoặc yêu cầu người dùng cài/đăng nhập Claude trong P01.
7. Trên Codex surface không hỗ trợ visibility, xác nhận orchestrator từ chối spawn và hướng dẫn chuyển surface thay vì fallback ẩn.

### Documentation tests

1. Kiểm tra `README.md`, `ARCHITECTURE.md`, `AGENTS.md` tồn tại và không rỗng.
2. Kiểm tra link nội bộ không bị gãy.
3. Kiểm tra README chứa trạng thái PoC, human roles, active agents, quickstart và runtime support status.
4. Kiểm tra ARCHITECTURE chứa component map, delegation sequence, observability, human boundary và known limitations.
5. Kiểm tra AGENTS chứa native-only delegation, plan approval, file ownership và human-authority rules.
6. Kiểm tra không có nội dung mâu thuẫn như README nói Claude đã test trong khi P01 ghi deferred.
7. Chạy một onboarding review: người chưa đọc plan phải tìm được active roadmap và cách chạy tests từ README trong dưới ba phút.
8. Kiểm tra README/AGENTS/ARCHITECTURE cùng chỉ định `benchmark_env` và không có command project nào dùng Python từ Conda base.

## 8. Acceptance criteria

- Hai skill pass `quick_validate.py`.
- Script có docstring, type hints và unit tests.
- Không có TODO placeholder hoặc tài liệu thừa trong skill folder.
- Positive prompts trigger đúng; negative prompts không trigger sai.
- Research output không có claim thiếu source.
- Teacher-facing output dùng plain language và không giao việc kỹ thuật cho giáo viên.
- Codex adapter có thể spawn đúng custom agent; nếu runtime không hỗ trợ visibility, orchestrator chỉ được load `SKILL.md` và tự thực hiện task trong parent thread theo chế độ `single-agent`, không tạo tiến trình specialist ẩn.
- Interactive specialist execution không gọi `codex exec`, `claude -p` hoặc shell subprocess tương đương.
- Codex CLI smoke test cho phép inspect/steer specialist bằng `/agent`.
- Hai Claude adapter được tạo và pass static validation; runtime smoke test Claude được ghi rõ là `DEFERRED_NOT_FAILED`.
- Mỗi delegation có thông báo trong parent thread và coordination record truy vết được.
- Có `single-agent` fallback; surface thiếu visibility phải fail closed thay vì chạy agent ngầm.
- Tài liệu nói rõ native transcript không đồng nghĩa với private chain-of-thought.
- `README.md`, `ARCHITECTURE.md`, `AGENTS.md` được tạo đúng contract và tất cả link nội bộ pass.
- README mô tả đúng trạng thái PoC, không trình bày prototype taxonomy/dataset như artifact đã xác nhận.
- ARCHITECTURE phân biệt rõ canonical agent, runtime adapter và native agent thread.
- AGENTS enforce native-only delegation và plan/file ownership boundaries.
- Không tạo tài liệu Markdown deferred nếu chưa thỏa trigger nêu tại Mục 6.4.
- Tất cả project Python validation được chạy bằng `/home/quannda/miniconda3/envs/benchmark_env/bin/python`.
- Không sửa benchmark taxonomy, dataset schema hoặc evaluation pipeline trong P01.

## 9. File ownership

P01 được phép tạo/sửa:

- `agents/research-methodologist/**`
- `agents/teacher-collaboration-designer/**`
- `.agents/skills/**` chỉ cho hai agent trên
- `.codex/agents/**` chỉ cho hai agent trên
- `.claude/agents/**` chỉ cho hai agent trên
- project instructions/config cần thiết để enforce native-only delegation
- coordination log schema/template
- `tests/agents/**`
- `README.md`
- `ARCHITECTURE.md`
- `AGENTS.md`
- documentation validation tests/config trong phạm vi P01

P01 không được sửa:

- `src/` ngoài helper thật sự bắt buộc;
- dataset, rubric hoặc benchmark specification;
- teacher packet của P04.

## 10. Handoff và GitHub

Khi hoàn thành:

1. Tạo report gồm file đã tạo, test output và forward-test findings.
2. Ghi rõ limitation của từng agent.
3. Commit riêng với experiment/plan ID.
4. Push GitHub chỉ sau khi acceptance criteria đạt.

## 11. Tài liệu runtime tham chiếu

- Codex subagents: https://developers.openai.com/codex/subagents
- Codex non-interactive mode: https://developers.openai.com/codex/noninteractive
- Claude Code subagents: https://code.claude.com/docs/en/sub-agents
- Claude Code agent teams: https://code.claude.com/docs/en/agent-teams

Các link Claude chỉ dùng để thiết kế adapter tương thích. P01 không yêu cầu chạy Claude Code.

## 12. Quyết định duyệt

Người dùng có thể:

- `APPROVE P01`;
- yêu cầu sửa phạm vi/tên agent;
- từ chối và giữ workflow thủ công.
