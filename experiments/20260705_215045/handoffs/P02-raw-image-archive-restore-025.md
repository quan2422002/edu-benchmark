# Specialist handoff

- Delegation ID: `P02-raw-image-archive-restore-025`
- Agent: `learning-resource-curator-single-agent-fallback`
- Status: `completed`
- Native thread ID/label: `null` — dùng skill trong parent thread, không spawn subagent ẩn.

## Delegation prompt

Khôi phục lại ảnh raw SGK Tin học 6–8 vì P02 chỉ được yêu cầu xử lý SGK lớp 9, không được xóa ảnh của các lớp khác đã crawl.

## Follow-up or steer messages

- Không đụng vào thư mục `SGK_TIN9`.
- Crawl lại SGK Tin học 6–8 từ trang tập huấn NXBGD.
- Ghi rõ lớp 6–8 chỉ là raw archive, chưa xử lý trong P02 bản thu gọn.

## Inputs read

- `agents/learning-resource-curator/SKILL.md`
- `experiments/20260705_215045/source_scope/sgk_sgv_source_registry.csv`
- `experiments/20260705_215045/source_scope/tin9_raw_page_images_report.md`
- `experiments/20260705_215045/coordination/delegations.jsonl`
- Trang tập huấn NXBGD cho SGK Tin học 6, 7, 8

## Outputs created or updated

- `experiments/20260705_215045/source_scope/raw_page_images/SGK_TIN6/`
- `experiments/20260705_215045/source_scope/raw_page_images/SGK_TIN7/`
- `experiments/20260705_215045/source_scope/raw_page_images/SGK_TIN8/`
- `experiments/20260705_215045/source_scope/raw_page_images_manifest.csv`
- `experiments/20260705_215045/source_scope/tin6_raw_page_images_manifest.csv`
- `experiments/20260705_215045/source_scope/tin7_raw_page_images_manifest.csv`
- `experiments/20260705_215045/source_scope/tin8_raw_page_images_manifest.csv`
- `experiments/20260705_215045/source_scope/raw_page_images_restore_report.md`
- `experiments/20260705_215045/source_scope/sgk_sgv_source_registry.csv`
- `experiments/20260705_215045/source_scope/sgk_sgv_source_scope.md`
- `experiments/20260705_215045/plans/02-source-scope-topic-taxonomy.md`

## Result summary

Đã khôi phục kho ảnh raw SGK Tin học 6–8 và giữ nguyên thư mục SGK Tin học 9. Manifest tổng hiện có 356 dòng, khớp với coordination log trước đó.

| Sách | Thư mục | Số ảnh | Dung lượng |
|---|---|---:|---:|
| Tin học 6 | `SGK_TIN6/` | 78 | 51.05 MB |
| Tin học 7 | `SGK_TIN7/` | 86 | 54.12 MB |
| Tin học 8 | `SGK_TIN8/` | 98 | 65.31 MB |
| Tin học 9 | `SGK_TIN9/` | 94 | 57.30 MB |

## Orchestrator decision

P02 bản thu gọn vẫn chỉ xử lý SGK Tin học 9. Ảnh SGK Tin học 6–8 chỉ được lưu để bảo toàn nguồn học liệu cho P08 hoặc một plan học liệu sau.

## Uncertainty

- Chưa OCR hoặc phân mảnh SGK Tin học 6–8.
- Chưa có HNMU/UET xác nhận trạng thái dùng chính thức của các nguồn lớp 6–8.

## Open questions and next human decisions

- Có cần backup ảnh raw ra ngoài Git/workspace không, vì ảnh đang bị `.gitignore`?
- P08 có nên xử lý toàn bộ SGK Tin học 6–9 hay vẫn ưu tiên Tin học 9 trước?
