# Báo cáo cuối Plan 06 — Quản lý đầu ra và vệ sinh kho mã nguồn

Experiment: `20260806_145124`
Plan: `P06`
Trạng thái: `COMPLETED`

## 1. Kết luận

Plan 06 đã hoàn tất theo chính sách bảo toàn dữ liệu được chốt tại P06-A001 và
quy tắc bảo vệ thông tin mô tả tệp ngoài phạm vi tại P06-A002. Kho mã nguồn có công cụ
kiểm kê không phá hủy, bảng nhóm trùng lặp, tệp kê khai lưu giữ và quy tắc bỏ qua
JSONL giới hạn theo đúng thử nghiệm/họ đầu ra. Không dữ liệu nào bị xóa, di
chuyển, bỏ theo dõi, đưa vào Git LFS hoặc viết lại lịch sử.

## 2. Sản phẩm đã triển khai

- `src/edu_benchmark/repository_hygiene/`: mã quét, SHA-256, trạng thái Git,
  kiểm tra blob trong `HEAD`, tìm tham chiếu và nhóm nội dung trùng;
- `scripts/repository_hygiene/inventory_repository.py`: CLI mỏng nhận config;
- `configs/repository-hygiene-v1.yaml`: phạm vi và chính sách theo từng nhóm;
- `outputs/plan06/repository_inventory.csv`: kiểm kê cấp tệp;
- `outputs/plan06/duplicate_groups.csv`: nhóm trùng từ 1 MiB trở lên;
- `outputs/plan06/retention_manifest.json`: tệp tổng hợp máy đọc về lưu giữ và an
  toàn;
- `.gitignore`: mô tả rõ tên và vai trò của 45 JSONL, chỉ áp dụng cho hai họ đầu
  ra thuộc experiment `20260727_170150`.

## 3. Kết quả kiểm kê cuối

- Số tệp trong phạm vi: `6.942`.
- Tổng dung lượng trong phạm vi: `2.471.956.321` byte.
- Tệp được Git theo dõi: `1.127`.
- Dung lượng được Git theo dõi: `88.125.467` byte.
- Tệp chưa được theo dõi và ngoài phạm vi: `4`, tổng `1.817.234` byte; đường dẫn
  và SHA-256 của từng tệp không được ghi vào sản phẩm kiểm kê.
- Tệp được theo dõi vượt 100 MiB: `0`.
- Blob có thể truy cập từ `HEAD` vượt 100 MiB: `0`.
- Blob lớn nhất có thể truy cập từ `HEAD`: `6.695.416` byte.
- Nhóm trùng từ 1 MiB: `14`, với `27.993.399` byte dư thừa lý thuyết.
- Dung lượng thực tế giải phóng: `0` byte.

## 4. Chính sách JSONL

45 JSONL, tổng `945.654.076` byte, tiếp tục nằm tại ngữ cảnh gốc:

- 34 tệp đánh giá benchmark: phản hồi, phản hồi thử nhanh, phán quyết, lỗi, đầu
  vào theo lô và đầu ra thô của nhà cung cấp, gồm cả các lượt thử lại;
- 11 tệp chấm yêu cầu nguyên tắc: năm cặp `run_a`/`run_b` và một
  `run_full`.

Chúng được giữ cục bộ bằng hai quy tắc `.gitignore`. Không dùng mẫu `*.jsonl`
toàn kho mã nguồn, không dùng Git LFS và không tạo `shared/local_archives/`.

## 5. Các nhóm được giữ nguyên

- `437.181.981` byte dữ liệu nguồn/học liệu dùng chung;
- SQLite học liệu `12.525.568` byte;
- `431.562.328` byte đầu ra OCR thử nghiệm;
- `238.841.710` byte bản sao ảnh học liệu lịch sử;
- sáu bản chụp lịch sử được Git theo dõi, tổng `15.883.404` byte;
- 16 tệp trung gian/bản sao lưu, tổng `864.825` byte;
- `main.xdv`, `958.868` byte;
- một DOCX và ba PDF cục bộ được bảo toàn như thay đổi ngoài phạm vi; thông tin mô tả
  riêng lẻ của chúng không được ghi vào sản phẩm kiểm kê.

## 6. Đối chiếu nghiệm thu

- Không có tệp được Git theo dõi vượt giới hạn 100 MB của GitHub: đạt.
- Không có quy tắc bỏ qua JSONL toàn kho mã nguồn: đạt.
- Không chuyển dữ liệu ra kho ngoài nên không phát sinh địa chỉ lưu hoặc phép thử
  phục hồi mới. Hai nhóm dữ liệu giữ cục bộ vẫn mang cờ yêu cầu phục hồi để ghi
  nhận giới hạn của bản sao Git mới; đây là rủi ro tồn dư được chấp nhận theo
  P06-A001.
- Sổ đăng ký benchmark dùng chung và sản phẩm chuẩn không bị thay đổi: đạt.
- Không xóa bản trùng nên không có thành phần sử dụng hoặc liên kết bị hỏng: đạt.
- Có số liệu số tệp, dung lượng Git và dung lượng thu hồi: đạt; dung lượng thu
  hồi bằng 0 theo quyết định giữ dữ liệu.

## 7. Đối chiếu trước và sau khi làm mới

| Chỉ số | Sản phẩm trước commit | Sản phẩm đã làm mới |
| --- | ---: | ---: |
| Tệp trong phạm vi | 6.946 | 6.942 |
| Tệp được Git theo dõi | 1.123 | 1.127 |
| Dung lượng được Git theo dõi | 88.093.503 byte | 88.125.467 byte |
| Thông tin mô tả chi tiết của tệp người dùng ngoài phạm vi | Có 4 tệp | Không |
| Dung lượng thực tế giải phóng | 0 byte | 0 byte |

Chênh lệch số lượng là do bốn tệp triển khai Plan 06 đã được Git theo dõi và bốn
tệp người dùng ngoài phạm vi không còn được công bố chi tiết; không phải do xóa
hoặc di chuyển dữ liệu nguồn.

## 8. Kiểm chứng

Kết quả kiểm chứng cuối được thực hiện bằng Python:
`/home/quannda/miniconda3/envs/benchmark_env/bin/python`.

- Toàn bộ phép kiểm thử của kho mã nguồn: `306 passed`.
- Governance validator: đạt.
- `pip check`: không có gói phụ thuộc bị hỏng.
- CLI help, kiểm tra 45/45 JSONL và `git diff --check`: đạt.
- Không gọi API provider.

## 9. Giới hạn

Dữ liệu bị `.gitignore` loại trừ không được GitHub sao lưu và không xuất hiện
trong bản sao Git mới. Plan 06 ưu tiên giữ ngữ cảnh thử nghiệm theo quyết định
của người phụ trách dự án; nếu cần đồng bộ dữ liệu trong tương lai, phải có quyết
định mới về Git LFS hoặc kho đối tượng.
