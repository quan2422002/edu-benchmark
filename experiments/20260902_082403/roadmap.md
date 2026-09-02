# Roadmap — Sinh phản hồi Qwen3.8 bằng Ollama local

Experiment: `20260902_082403`  
Trạng thái: `PLAN 01 COMPLETED — PLAN 02 APPROVED/IN PROGRESS — PLAN 03 CLOSED`  
Nguồn hiện trạng chính: `20260727_170150`

## 1. Mục tiêu

Tích hợp Ollama như một model provider local có truy vết, nối provider này vào
workflow sinh target response đã có, kiểm chứng bằng pilot, rồi mới sinh đúng
một phản hồi gia sư cho mỗi candidate trong tập `full_1400_v1`.

Experiment chỉ tạo thêm một target-response bundle phục vụ nghiên cứu. Nó không
xác nhận Qwen3.8 tốt hơn model khác, không chạy LLM judge và không thay đổi trạng
thái khoa học của benchmark 1.400 mẫu.

## 2. Lý do chia thành ba plan

Code hiện tại đã có chuẩn bị `PreparedTutorRequest`, ghi JSONL tăng dần, retry,
resume, manifest và validation cho target response. Tuy nhiên, orchestration đó
vẫn nằm trong runner synchronous gắn với Vertex và chưa gọi qua contract
`ModelProvider` dùng chung.

Vì vậy experiment tách ba quyền thay đổi và ba gate độc lập:

1. **Plan 01** chỉ sở hữu Ollama runtime và provider; không sở hữu artifact
   target response.
2. **Plan 02** nối workflow target-response hiện có vào provider-neutral
   boundary, giữ nguyên semantics lưu trữ, rồi chạy technical smoke và pilot.
3. **Plan 03** chỉ chạy full 1.400 mẫu sau khi provider, runner và pilot đều đạt.

## 3. Nguyên tắc triển khai

1. Chỉ triển khai plan có dòng trạng thái `APPROVED`.
2. Ba plan cần ba lần duyệt riêng; qua một plan không tự động cho phép plan sau.
3. Giữ nguyên candidate manifest, requirement score, instruction bundle và các
   response cũ của experiment `20260727_170150`.
4. Dùng Ollama native `/api/chat`, không dùng đường OpenAI-compatible cho
   Qwen3.8 trong experiment này.
5. Pin Ollama version, model digest, quantization và provider mapping trước khi
   tích hợp benchmark.
6. Plan 02 tái sử dụng target-response record và persistence semantics hiện có;
   không phát minh một schema hoặc cơ chế checkpoint riêng cho Ollama.
7. Full run phải dùng đúng configuration đã khóa ở pilot, trừ khi Quân duyệt
   amendment trước khi chạy.
8. Mọi local-LLM framework dùng chung storage root
   `/workspace/quannd/local_llm_cache/`, chia namespace theo framework; model và
   cache lớn nằm ngoài Git và ngoài phân vùng `/`.

## 4. Workflow đích

```text
Plan 01: runtime/cache → OllamaProvider → fake-HTTP tests → provider probe
                                      │
                                      ▼
Plan 02: PreparedTutorRequest → ModelRequest → ModelProvider
                                      │
                                      ▼
          persistence hiện có → technical smoke 2 → resume pilot 30
                                      │
                                      ▼
                      Quân duyệt gate tài nguyên/chất lượng/ETA
                                      │
                                      ▼
Plan 03:                 full 1.400 có resume → validation/report
```

## 5. Trình tự plan

| Thứ tự | Plan | Trạng thái | Gate mở plan kế tiếp |
|---:|---|---|---|
| 01 | [Ollama/Qwen3.8 runtime và model provider](plans/01-ollama-qwen38-runtime-and-provider.md) | `COMPLETED` | Đã đạt: 28 test, runtime đúng version/digest/Q4_K_M, context 4096, 100% GPU và provider probe không lưu reasoning |
| 02 | [Provider-neutral target runner và pilot 2→30](plans/02-provider-neutral-target-runner-and-qwen38-pilot.md) | `APPROVED — IN PROGRESS` | Baseline tuần tự đã đủ 30/30; pilot đối sánh concurrency-2 phải đạt VRAM/integrity/throughput và được Quân chấp nhận |
| 03 | [Sinh full 1.400 response](plans/03-qwen38-full-1400-response-generation.md) | `DRAFT` | 1.400 ID duy nhất; output hoàn tất; provenance và validation đều đạt |

## 6. Gate chung

- Approval, phạm vi ghi và cách dừng runtime được xác nhận riêng cho từng plan.
- Không để Ollama, Hugging Face, vLLM hoặc local-LLM framework khác ghi model/
  cache lớn vào đường dẫn mặc định trên phân vùng `/`, hiện chỉ còn khoảng 19 GB.
- Trước mọi download, preflight phải in và xác nhận cache root thực tế nằm dưới
  `/workspace/quannd/local_llm_cache/`.
- Không thay thế binary/service Ollama dùng chung nếu chưa có approval riêng.
- Không mở API ra ngoài loopback.
- Không mở Plan 02 nếu provider chưa qua fake-HTTP test và runtime probe.
- Không mở Plan 03 nếu pilot cho thấy CPU offload, OOM, response bị cắt, thinking
  bị rò vào `response_text`, hoặc ETA vượt 24 giờ mà Quân chưa chấp nhận.
- Validation, status, coordination event và handoff phải hoàn tất trước khi đóng
  từng plan.

## 7. Ngoài phạm vi

- Chạy requirement scoring mới hoặc thay required-principle set.
- Sửa instruction bundle `v2` sau khi nhìn output Qwen3.8.
- Dùng image input hoặc đánh giá năng lực vision của Qwen3.8.
- LLM judge, human judge quy mô đầy đủ, xếp hạng model hoặc sửa manuscript.
- Promote output vào `shared/benchmark/`.
- Xóa model/cache hoặc thay đổi system service Ollama hiện có.
- Viết lại persistence target response nếu hành vi hiện có có thể được tái sử
  dụng và kiểm chứng tương đương.

## 8. Cổng dừng hiện tại

Plan 01 đã hoàn thành Gate A–C trên service do Quân giữ trong `screen`; final
report và hai machine artifact đều đã được ghi. Quân đã phê duyệt riêng Plan 02;
code, config, selection và runbook đã được cài; offline gate đạt. Theo
`P02-A002`, chỉ Quân được gọi benchmark model. `P02-A003` đã xóa bundle 4 mẫu,
bổ sung GPU sampling theo candidate và reset pilot về 0/30; Quân sẽ tự chạy
smoke 2 mẫu, resume 28 mẫu và review Gate C. Plan 03 tiếp tục đóng.
