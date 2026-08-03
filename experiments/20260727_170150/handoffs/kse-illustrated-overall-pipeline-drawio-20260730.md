# Bàn giao — Sơ đồ pipeline tổng thể có minh họa

- Delegation ID: `EXP-20260730-KSE-ILLUSTRATED-PIPELINE-001`
- Agent: parent thread dùng `benchmark-specification-designer` ở chế độ single-agent
- Status: hoàn thành
- Native thread ID/label: không tạo specialist thread

## Delegation prompt

Tạo một file Draw.io mới cho Figure 1, dùng khung nét đứt khoanh ba phase và
các hình minh họa thay cho sơ đồ chủ yếu bằng chữ.

## Follow-up or steer messages

Không có.

## Inputs read

- `kse_submit_manuscript/diagrams/overall_pipeline.drawio`
- `kse_submit_manuscript/manuscript/main.tex`
- `experiments/20260727_170150/roadmap.md`
- Ảnh flow KMP-Bench do UET cung cấp trong hội thoại

## Outputs created

- `kse_submit_manuscript/diagrams/overall_pipeline_illustrated.drawio`

## Result summary

Sơ đồ landscape mới có ba khung nét đứt. Phase 1 minh họa hội thoại thô,
SGK/SGV, full-text search, hybrid audit và 665 family. Phase 2 minh họa căn cứ
nghiên cứu, phương pháp HNMU, synthesis, sáu nguyên tắc và sáu năng lực. Phase
3 minh họa turn-level conversion, 2.028 candidate, LLM requirement scoring,
code gates, rubric foundation và output 1.400 mẫu/655 family. File gồm 63
mxCell, 46 vertex và 15 edge; XML, ID, source/target và màu đều hợp lệ.

## Orchestrator decision

Giữ file mới độc lập; chưa ghi đè sơ đồ cũ, chưa export ảnh và chưa thay Figure
1 trong LaTeX trước khi UET duyệt trực quan.

## Uncertainty

Chưa có Draw.io CLI trên máy nên chưa render/export để kiểm tra pixel-level;
file đã được kiểm tra ở mức cấu trúc XML và graph references.

## Open questions and next human decisions

UET mở file bằng diagrams.net/Draw.io, góp ý bố cục; sau khi duyệt mới export và
thay Figure 1.
