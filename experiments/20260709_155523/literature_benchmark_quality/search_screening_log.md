# Nhật ký tìm kiếm và sàng lọc — Kế hoạch 01

Ngày: 12/07/2026

## 1. Tìm kiếm trong kho mã cục bộ

Đường dẫn đã kiểm tra:

- `document/paper/source_paper/`
- `experiments/20260705_215045/literature_notes/paper_summaries/`

Các bài báo được đưa vào:

| Bài báo | Tệp cục bộ | Quyết định |
|---|---|---|
| MathTutorBench | `document/paper/source_paper/2502.18940v2.pdf` | Đưa vào |
| KMP-Bench | `document/paper/source_paper/18426-AAAI26.ShiW-NLP.pdf` | Đưa vào |
| TutorBench | `document/paper/source_paper/2510.02663v1.pdf` | Đưa vào |
| VietLegal/V-Legal | `document/paper/source_paper/2512.14554v5.pdf` | Đưa vào |

## 2. Chuyển PDF thành văn bản tạm

Các PDF cục bộ được chuyển thành văn bản tạm trong `/tmp` bằng `pdftotext -layout`:

- `/tmp/BQ-P001-mathtutorbench.txt`
- `/tmp/BQ-P002-kmp-bench.txt`
- `/tmp/BQ-P003-tutorbench.txt`
- `/tmp/BQ-P004-vietlegal.txt`

## 3. Tra cứu trực tuyến để xác nhận đường dẫn ổn định

Các truy vấn chỉ dùng để xác nhận đường dẫn arXiv ổn định:

- `"TutorBench" "A Benchmark To Assess Tutoring Capabilities"`
- `"MathTutorBench" "A Benchmark for Measuring Open-ended Pedagogical"`
- `"From Solver to Tutor" "KMP-Bench"`
- `"2512.14554" VietLegal`

Kết quả dùng trong tài liệu:

- MathTutorBench: `https://arxiv.org/abs/2502.18940`
- KMP-Bench: `https://arxiv.org/abs/2603.02775`
- TutorBench: `https://arxiv.org/abs/2510.02663`
- VietLegal/V-Legal: `https://arxiv.org/abs/2512.14554`

## 4. Ghi chú sàng lọc

- Ba bài báo gia sư được giữ vì đã được đọc sâu ở thử nghiệm trước và trực tiếp liên quan đến đánh giá gia sư AI.
- VietLegal/V-Legal được giữ vì hữu ích cho kiểm soát chất lượng dữ liệu tiếng Việt, phân tầng nhận thức, chuyên gia xác thực, truy xuất nguồn và kiểm tra trùng/rò rỉ.
- Không mở rộng thêm bài báo mới trong lượt này để giữ đúng phạm vi Kế hoạch 01.
