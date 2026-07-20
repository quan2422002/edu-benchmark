# Specialist handoff
## Cập nhật trạng thái ngày 18/07/2026

Handoff này ghi trạng thái lịch sử của Pha 1 tại ngày 15/07/2026. Sau đó, OCR Markdown SGK/SGV Tin học 6–9 do Nguyên gửi đã được xử lý ở Plan 03 Pha 4–5, đồng bộ vào manifest/fragment/index. Vì vậy câu “không OCR, không fragment” trong handoff này chỉ đúng với phạm vi Pha 1, không phải trạng thái hiện tại của toàn bộ học liệu.


- Delegation ID: `learning-resource-phase1-sgv-crawl-007`
- Agent: `learning-resource-curator` skill in single-agent/orchestrator mode
- Status: completed
- Native thread ID/label: không spawn specialist thread; dùng trực tiếp canonical skill trong parent thread.

## Delegation prompt

Quân yêu cầu tiếp tục thực hiện Pha 1 của Plan 03: crawl ảnh SGV Tin học 6–9 từ các link `taphuan.nxbgd.vn` đã cung cấp trước đó.

## Follow-up or steer messages

Không có steer bổ sung trong quá trình chạy.

## Inputs read

- `README.md`
- `ARCHITECTURE.md`
- `experiments/20260709_155523/roadmap.md`
- `experiments/20260709_155523/plans/03-learning-resource-normalization-and-retrieval-system.md`
- `agents/learning-resource-curator/SKILL.md`
- `agents/learning-resource-curator/references/learning-resource-schema.md`
- `agents/learning-resource-curator/references/learning-resource-mapping-v0.md`
- SGV Tin học 6: `https://taphuan.nxbgd.vn/tap-huan/doc-sach/sgv-tin-hoc-6.4918798731#page=0`
- SGV Tin học 7: `https://taphuan.nxbgd.vn/tap-huan/doc-sach/sgv-tin-hoc-7.4920462481#page=0`
- SGV Tin học 8: `https://taphuan.nxbgd.vn/tap-huan/doc-sach/sgv-tin-hoc-8.4923610683#page=0`
- SGV Tin học 9: `https://taphuan.nxbgd.vn/tap-huan/doc-sach/sgv-tin-hoc-9.4923777498#page=0`

## Outputs created or updated

- `shared/learning_resources/raw_page_images/sgv/tin_hoc_6/`
- `shared/learning_resources/raw_page_images/sgv/tin_hoc_7/`
- `shared/learning_resources/raw_page_images/sgv/tin_hoc_8/`
- `shared/learning_resources/raw_page_images/sgv/tin_hoc_9/`
- `shared/learning_resources/registries/learning_resource_file_manifest.csv`
- `shared/learning_resources/registries/sgk_sgv_source_registry.csv`
- `experiments/20260709_155523/reports/sgv-crawl-source-and-risk-notes.md`
- `experiments/20260709_155523/plans/03-learning-resource-normalization-and-retrieval-system.md`
- `experiments/20260709_155523/roadmap.md`
- `README.md`
- `ARCHITECTURE.md`
- `experiments/20260709_155523/metadata.yaml`

## Result summary

Đã crawl ảnh SGV Tin học 6–9 từ HTML của `taphuan.nxbgd.vn` và CDN ảnh `cdn3.olm.vn`. Tổng số ảnh SGV đăng ký: **396**.

| Sách | Số ảnh SGV |
| --- | ---: |
| Tin học 6 | 98 |
| Tin học 7 | 94 |
| Tin học 8 | 102 |
| Tin học 9 | 102 |

## Orchestrator decision

Pha 1 chỉ crawl ảnh SGV và cập nhật truy vết. Không OCR, không fragment, không xác nhận nội dung chuyên môn thay HNMU.

## Uncertainty

- Chưa quyết định có commit ảnh SGK/SGV lên GitHub hay chỉ giữ ảnh local/Drive.
- Chưa kiểm tra chất lượng từng ảnh sau crawl bằng thị giác/OCR.
- Chưa xác nhận số trang với HNMU.

## Open questions and next human decisions

- Có duyệt Pha 2 để tạo danh mục chủ đề/bài học/trang v0 không?
- Với ảnh SGK/SGV, có commit vào GitHub không, hay chỉ commit manifest/registry và giữ ảnh ở local/Drive?
