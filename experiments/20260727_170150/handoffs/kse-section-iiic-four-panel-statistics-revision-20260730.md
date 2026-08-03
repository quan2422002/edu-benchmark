# Bàn giao — Figure 3 bốn panel cho mục III.C

- Delegation ID: `EXP-20260730-KSE-IIIC-FOUR-PANEL-001`
- Agent: parent thread dùng `benchmark-specification-designer` ở chế độ single-agent
- Status: hoàn thành
- Native thread ID/label: không tạo specialist thread

## Delegation prompt

Ghép hai bar chart về số lượt và độ dài ký tự mỗi lượt với hai pie chart đã có
trong Figure 3.

## Follow-up or steer messages

UET làm rõ rằng Figure 3 cần giữ cả hai bar chart tương tự Figure 2 của Phase 1.

## Inputs read

- `kse_submit_manuscript/manuscript/main.tex`
- `kse_submit_manuscript/manuscript/figures/statistic.png`
- `experiments/20260727_170150/outputs/benchmark_candidate_pool/eligible_without_plan03_review.csv`

## Outputs created

- Cập nhật `kse_submit_manuscript/analysis_code/plot_phase3_candidate_statistics.py`.
- Sinh lại `kse_submit_manuscript/manuscript/figures/phase3_candidate_statistics.png`.
- Cập nhật caption Figure 3 trong `kse_submit_manuscript/manuscript/main.tex`.
- Biên dịch lại `kse_submit_manuscript/manuscript/main.pdf`.

## Result summary

Figure 3 nay gồm bốn panel trên canvas 3552x1152: incidence của sáu nguyên tắc,
khối lớp, số lượt trong mỗi benchmark sample, và độ dài ký tự của mỗi lượt.
Số lượt được tính trên prompt, history và reference response; độ dài ký tự được
tính trên 5.508 lượt xuất hiện trong 1.400 sample. Script xác nhận các phân bố
số lượt là 631/414/194/103/49/7/2 cho 2/4/6/8/10/12/14 lượt và các bins ký tự
0--49/50--99/100--149/150--199/200--249/250--299 là
896/2.277/1.569/564/171/31. PDF biên dịch thành công ở 5 trang.

## Orchestrator decision

Chấp nhận cách tính ở cấp benchmark sample; không lặp lại thống kê hội thoại
nguồn của Figure 2.

## Uncertainty

Các lượt nguồn có thể xuất hiện trong nhiều candidate khác nhau; vì vậy panel
độ dài dùng thuật ngữ `turn occurrences`, không tuyên bố 5.508 lượt nguồn duy
nhất.

## Open questions and next human decisions

UET tiếp tục review manuscript.
