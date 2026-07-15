# Kết quả tạo PDF dẫn xuất cho SGK/SGV Tin học 6–9

Ngày thực hiện: 15/07/2026
Experiment: `20260709_155523`

## 1. Mục tiêu

Tạo bản PDF từ ảnh từng trang đã có trong `shared/learning_resources/raw_page_images/` để người dùng mở xem và đối chiếu thuận tiện hơn.

PDF chỉ là **bản dẫn xuất để xem nhanh**, không thay thế ảnh gốc theo trang và không thay thế manifest truy vết.

## 2. Kết quả

| Tài liệu | PDF | Số trang | Kích thước byte | SHA-256 |
| --- | --- | ---: | ---: | --- |
| SGK Tin học 6 | `shared/learning_resources/compiled_documents/sgk_tin_hoc_6.pdf` | 78 | 14893080 | `74c270b3c2244782daeaeb1c3ded5dd01fb87528467bdab8d80fc9de5edaf19c` |
| SGK Tin học 7 | `shared/learning_resources/compiled_documents/sgk_tin_hoc_7.pdf` | 86 | 17013398 | `384973b98774f6567d06df38fcf5cea2586f0d3e3e1ad52f1a498cc144e0de40` |
| SGK Tin học 8 | `shared/learning_resources/compiled_documents/sgk_tin_hoc_8.pdf` | 98 | 19655808 | `781071b4a94082dd154623a58e871a99368f3edca562ad409ce937e97c969042` |
| SGK Tin học 9 | `shared/learning_resources/compiled_documents/sgk_tin_hoc_9.pdf` | 94 | 19092547 | `7ba77621644c002713ab50ff49a246ed6ec250140acbae5d2b6f4222ede99916` |
| SGV Tin học 6 | `shared/learning_resources/compiled_documents/sgv_tin_hoc_6.pdf` | 98 | 18979747 | `9ae8eadcd2e91ca3d48a3136847a945df8042633407642828f149a8f23655da1` |
| SGV Tin học 7 | `shared/learning_resources/compiled_documents/sgv_tin_hoc_7.pdf` | 94 | 19116815 | `32d158f69b5f037b1eef17014b0d5585173d96e1a0fb4cddb4ff5452532e2f07` |
| SGV Tin học 8 | `shared/learning_resources/compiled_documents/sgv_tin_hoc_8.pdf` | 102 | 19947668 | `2aad7100ac74d3bdcfdda817293f4068d45fedf610f85cf0914a6c2913cda81a` |
| SGV Tin học 9 | `shared/learning_resources/compiled_documents/sgv_tin_hoc_9.pdf` | 102 | 20055540 | `e576adb75aeb7d8d91e900ae03dae26e9586cb7d2cd5de58efa9e9c97b57fce0` |

Tổng số PDF đã tạo: **8**.

## 3. Manifest/registry

- `shared/learning_resources/registries/learning_resource_file_manifest.csv`: đã thêm các dòng `SGK_PDF_DERIVED` và `SGV_PDF_DERIVED`.
- `shared/learning_resources/registries/sgk_sgv_source_registry.csv`: đã bổ sung ghi chú đường dẫn PDF dẫn xuất vào từng nguồn học liệu.

## 4. Quy tắc sử dụng

- Khi cần OCR hoặc truy vết chính xác, vẫn dùng ảnh từng trang và manifest theo trang.
- Khi cần đọc nhanh, trình bày với người dùng, hoặc kiểm tra thủ công, có thể mở PDF dẫn xuất.
- Chưa quyết định có commit PDF/ảnh lên GitHub hay chỉ giữ local/Drive; cần Quân chốt trước khi push.
