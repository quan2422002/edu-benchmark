# Bàn giao — Nhãn số và thống kê độ dài ở Figure 3

- Delegation ID: `EXP-20260730-KSE-FIG3-LABELS-SUMMARY-001`
- Agent: parent thread dùng `benchmark-specification-designer` ở chế độ single-agent
- Status: hoàn thành
- Native thread ID/label: không tạo specialist thread

## Delegation prompt

Hiển thị trực tiếp số liệu trên hai pie chart, sửa nhãn cột dựng đứng ở panel
(d), và bổ sung trung bình/trung vị của độ dài lượt.

## Follow-up or steer messages

Không có.

## Inputs read

- `kse_submit_manuscript/analysis_code/plot_phase3_candidate_statistics.py`
- `experiments/20260727_170150/outputs/benchmark_candidate_pool/eligible_without_plan03_review.csv`
- `kse_submit_manuscript/manuscript/main.tex`

## Outputs created

- Cập nhật script sinh Figure 3.
- Sinh lại `phase3_candidate_statistics.png`.
- Cập nhật caption trong `main.tex` và biên dịch lại `main.pdf`.

## Result summary

Hai pie chart nay ghi count và percentage trực tiếp trên từng lát; các nguyên
tắc hiếm dùng callout để không mất nhãn. Nhãn số trên các cột panel (d) nằm
ngang. Panel (d) và caption báo mean 96,6 và median 90 ký tự trên 5.508 lượt
xuất hiện. Script khóa hai thống kê này và dừng nếu dữ liệu nguồn thay đổi.
PDF biên dịch thành công ở 5 trang.

## Orchestrator decision

Chấp nhận bản sửa, giữ nguyên bốn panel và định nghĩa dữ liệu.

## Uncertainty

Không có.

## Open questions and next human decisions

UET tiếp tục review manuscript.
