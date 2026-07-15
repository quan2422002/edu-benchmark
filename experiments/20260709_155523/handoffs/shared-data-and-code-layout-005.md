# Specialist handoff

- Delegation ID: `shared-data-and-code-layout-005`
- Agent: `single-agent/orchestrator`
- Status: completed
- Native thread ID/label: không dùng specialist thread; Plan 02 là việc tổ chức repo/layout nên được thực hiện trực tiếp trong parent thread.

## Delegation prompt

Quân duyệt Plan 02 và yêu cầu thực hiện/cài đặt các phần trong plan để sau đó có thể triển khai Plan 02 và Plan 03 song song một cách an toàn, tránh tối đa chồng lấn.

## Follow-up or steer messages

Không có steer bổ sung trong khi triển khai.

## Inputs read

- `README.md`
- `ARCHITECTURE.md`
- `experiments/20260709_155523/roadmap.md`
- `experiments/20260709_155523/plans/02-shared-data-and-code-layout.md`
- `experiments/_templates/handoff.md`
- `shared/raw_data/HNMU-teacher_dialog_samples/Lớp 6.xlsx`
- `shared/raw_data/HNMU-teacher_dialog_samples/Lớp 7.xlsx`

## Outputs created

- `shared/raw_data/HNMU-teacher_dialog_samples/README.md`
- `shared/raw_data/HNMU-teacher_dialog_samples/manifest.csv`
- `shared/learning_resources/README.md`
- `shared/learning_resources/registries/learning_resource_file_manifest.csv`
- `src/edu_benchmark/README.md`
- `src/edu_benchmark/__init__.py`
- `src/edu_benchmark/data_io/__init__.py`
- `src/edu_benchmark/dialogue_audit/__init__.py`
- `src/edu_benchmark/benchmark_conversion/__init__.py`
- `src/edu_benchmark/learning_resources/__init__.py`
- `src/edu_benchmark/benchmark_quality/__init__.py`
- `experiments/20260709_155523/outputs/README.md`
- các `.gitkeep` cho thư mục học liệu/output còn rỗng.

## Outputs updated

- `README.md`
- `ARCHITECTURE.md`
- `experiments/20260709_155523/roadmap.md`
- `experiments/20260709_155523/plans/02-shared-data-and-code-layout.md`
- `experiments/20260709_155523/metadata.yaml`

## Result summary

Plan 02 đã chốt layout dùng chung:

- Raw data HNMU nằm ở `shared/raw_data/HNMU-teacher_dialog_samples/`, có README và manifest.
- Học liệu SGK/SGV có vùng `shared/learning_resources/`, nhưng Plan 02 chưa copy ảnh, chưa crawl SGV, chưa OCR.
- Code dùng chung có package khung `src/edu_benchmark/`.
- Output riêng của experiment có vùng `experiments/20260709_155523/outputs/`.

Hai file Excel HNMU được giữ nguyên tại vị trí hiện có. Manifest ghi `sha256`, kích thước logic cơ bản và trạng thái `raw_registered_no_audit`.

## Orchestrator decision

Giữ phương án không di chuyển file Excel gốc để tránh làm gãy đường dẫn và để Plan 03 có thể chạy song song an toàn. Plan 03 sẽ chỉ cần ghi vào vùng học liệu dùng chung và manifest học liệu, không sửa manifest raw data HNMU của Plan 02 trừ khi nhận batch HNMU mới.

## Uncertainty

- Số dòng trong manifest là ước tính từ worksheet đầu tiên bằng thư viện chuẩn Python, chưa phải audit nội dung.
- Chưa quyết định có version hóa ảnh SGK/SGV trên GitHub hay chỉ lưu local/Drive; Plan 03 cần chốt tiếp.

## Open questions and next human decisions

- Có duyệt Plan 03 để copy ảnh SGK đã crawl sang `shared/learning_resources/` và lập manifest học liệu không?
- Với ảnh SGK/SGV, có commit vào GitHub không, hay chỉ commit manifest và giữ ảnh local/Drive?
