# Báo cáo cuối — Plan 04

Experiment: `20260806_145124`
Baseline: `plans/04-experiment-configs-runbooks-and-portable-paths.md`
Trạng thái kết luận: `completed`

## 1. Kết quả

Plan 04 đã tạo một hợp đồng cấu hình YAML và bộ chạy khả chuyển dùng chung tại
`src/edu_benchmark/experiment_runtime/`. Bộ nạp cấu hình xác định repository độc
lập với thư mục làm việc, chỉ chấp nhận đường dẫn tương đối, kiểm mã băm và số
dòng, dừng khi đường dẫn thoát khỏi repository, đồng thời chặn thông tin xác
thực bị ghi trực tiếp vào cấu hình.

Phân tích Section V trên 1.400 mẫu được chọn làm quy trình đại diện. Điểm vào
đang hoạt động không còn chứa mã experiment hoặc đường dẫn mặc định; mọi giá trị
được đọc từ
[`section-v-ablation-v1.yaml`](../configs/section-v-ablation-v1.yaml).
Preflight từ repository root và `/tmp` cho cùng fingerprint
`7db20cf65ea89508365f1313ae42670dd90cbcf03fd5238d907308455e0c49ac`.

Kết quả dựng lại có SHA-256 tệp
`d35f8512b0ea059fea4c1c9b912f5f7ef4c8332c4719fef58b07b47d14d98469`.
Hash tệp khác baseline vì ba đường dẫn provenance cũ là đường dẫn tuyệt đối;
sau khi chỉ chuẩn hóa ba đường dẫn này thành đường dẫn tương đối, kết quả mới và
baseline có cùng SHA-256 ngữ nghĩa
`791e282fed16c2ee1f6b38f0ad94b3b47fd74ea6f54f130f1106de850d75348a`.

## 2. So với baseline

| Tiêu chí | Kết quả | Bằng chứng |
|---|---|---|
| Không có đường dẫn máy người phát triển trong runbook/wrapper đang hoạt động | `pass` | [Runbook](../runbooks/plan04-portable-section-v-analysis.md), điểm vào `scripts/benchmark_evaluation/analyze_section_v_ablation.py` và phép quét đường dẫn |
| Preflight từ ít nhất hai thư mục xác định cùng input | `pass` | Cùng config SHA-256 `bda7e8…a205` và fingerprint `7db20…49ac` từ repository root và `/tmp` |
| Cấu hình/manifest không chứa credential | `pass` | [`section_v_run_manifest.json`](../outputs/plan04/section_v_run_manifest.json) ghi `secret_scan.status: passed`; phép quét credential không có kết quả |
| Đổi cấu hình không yêu cầu sửa hằng số trong thư viện | `pass` | CLI chỉ nhận `--config`; test cấu hình kiểm khả năng độc lập với thư mục làm việc |
| Resume chỉ xử lý phần chưa hoàn tất | `not_applicable` cho Section V | Quy trình offline là phép dựng lại nguyên tử và ghi `resume.policy: unsupported`; runner trả phí tương thích vẫn giữ cơ chế pending-ID riêng và không bị chạy lại |
| Dữ liệu dẫn xuất bằng baseline hoặc khác biệt được duyệt | `pass` | [`section_v_results.json`](../outputs/plan04/section_v_results.json) có cùng semantic SHA-256 với baseline; khác biệt duy nhất là đường dẫn provenance tương đối theo `P04-A001` |
| Inventory phân loại trước khi migration | `pass` | [`active_pipeline_inventory.csv`](../outputs/plan04/active_pipeline_inventory.csv) phân loại chín entrypoint thành `active`, `compatibility` và `historical-only` |

## 3. Amendment đã áp dụng

- [`P04-A001`](../decisions/plan04-amendments.md): chọn Section V làm quy trình
  đại diện, YAML làm định dạng cấu hình và giữ wrapper tương thích đến Plan 07.

## 4. Validation

- Trình thông dịch chính xác:
  `/home/quannda/miniconda3/envs/benchmark_env/bin/python`
- Governance validator: `passed`.
- Test governance, agent, runtime config và Section V: `50 passed`.
- Toàn repository ngoài một lỗi dependency có sẵn: `279 passed, 1 deselected`.
- Full suite khi không loại trừ: còn đúng một lỗi không do Plan 04 —
  `requirements.txt` ghi `PyYAML==6.0.3` trong khi `pyproject.toml` ghi
  `PyYAML==6.0.2`; cả hai file không có thay đổi trong working tree và không
  thuộc phạm vi ghi Plan 04.
- `pip check`: không có package bị hỏng.
- Quét đường dẫn tuyệt đối và credential trên config/runbook/manifest/output:
  `passed`.
- `git diff --check`: `passed`.
- Không có API trả phí hoặc provider call.

## 5. Artifact chính

- [Cấu hình Section V](../configs/section-v-ablation-v1.yaml)
- [Runbook](../runbooks/plan04-portable-section-v-analysis.md)
- [Inventory pipeline](../outputs/plan04/active_pipeline_inventory.csv)
- [Kết quả Section V tái lập](../outputs/plan04/section_v_results.json)
- [Manifest lần chạy](../outputs/plan04/section_v_run_manifest.json)

## 6. Giới hạn và backlog

- Hai JSONL phán quyết lớn là artifact lịch sử local, không phải fixture của CI
  clean-clone; test tự chứa dùng dữ liệu tạm nhỏ.
- Các wrapper sinh/chấm trả phí đã hoàn tất được giữ làm
  `compatibility`/`historical-only`; Plan 04 không chuyển đổi hàng loạt hoặc xóa.
- `code_commit` trong manifest còn `null` cho đến khi project lead tự commit.
- Quy trình Section V không có resume cấp mẫu vì output được dựng lại nguyên tử.
- Lệch phiên bản PyYAML giữa hai file dependency là lỗi packaging nền cần được
  xử lý trong phạm vi packaging riêng; Plan 04 không tự mở rộng quyền sửa.

## 7. Gate tiếp theo

Plan 04 hoàn tất. Plan 05 có thể được project lead đọc và quyết định duyệt nhưng
vẫn là `DRAFT`; closeout này không tự động cấp quyền triển khai Plan 05.
