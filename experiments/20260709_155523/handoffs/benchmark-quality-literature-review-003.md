# Bàn giao — Kế hoạch 01: rà soát chất lượng bộ đánh giá

- Mã điều phối: `research-methodologist-single-agent-20260712-001`
- Tác nhân chuyên trách: `research-methodologist`, chạy trong luồng cha; không gọi thêm luồng tác nhân chuyên trách.
- Trạng thái: hoàn thành
- Mã/nhãn luồng riêng: `null`

## Yêu cầu thực hiện

Thực hiện Kế hoạch 01: đọc lại 3 bài báo về gia sư và 1 bài báo VietLegal/V-Legal để xem các bài báo đánh giá chất lượng của chính bộ đánh giá như thế nào, không chỉ xem bộ đánh giá được dùng để chấm mô hình ra sao.

## Điều chỉnh trong quá trình làm

Không có điều chỉnh giữa chừng. Người dùng nói nếu cần gọi nhiều tác nhân chuyên trách thì phải báo trước; người điều phối chọn không gọi thêm vì phạm vi đủ để làm tuần tự trong luồng cha.

## Đầu vào đã đọc

- `README.md`
- `ARCHITECTURE.md`
- `experiments/20260709_155523/roadmap.md`
- `experiments/20260709_155523/plans/01-benchmark-quality-literature-review.md`
- `agents/research-methodologist/SKILL.md`
- `agents/research-methodologist/references/review-protocol.md`
- `agents/research-methodologist/references/evidence-schema.md`
- `agents/research-methodologist/scripts/validate_evidence_matrix.py`
- `document/paper/source_paper/2502.18940v2.pdf`
- `document/paper/source_paper/18426-AAAI26.ShiW-NLP.pdf`
- `document/paper/source_paper/2510.02663v1.pdf`
- `document/paper/source_paper/2512.14554v5.pdf`
- `experiments/20260705_215045/literature_notes/paper_summaries/P03-P001-mathtutorbench.md`
- `experiments/20260705_215045/literature_notes/paper_summaries/P03-P002-kmp-bench.md`
- `experiments/20260705_215045/literature_notes/paper_summaries/P03-P003-tutorbench.md`

## Tệp kết quả đã tạo hoặc cập nhật

- `experiments/20260709_155523/literature_benchmark_quality/review_protocol.md`
- `experiments/20260709_155523/literature_benchmark_quality/search_screening_log.md`
- `experiments/20260709_155523/literature_benchmark_quality/paper_summaries/BQ-P001-mathtutorbench.md`
- `experiments/20260709_155523/literature_benchmark_quality/paper_summaries/BQ-P002-kmp-bench.md`
- `experiments/20260709_155523/literature_benchmark_quality/paper_summaries/BQ-P003-tutorbench.md`
- `experiments/20260709_155523/literature_benchmark_quality/paper_summaries/BQ-P004-vietlegal.md`
- `experiments/20260709_155523/literature_benchmark_quality/benchmark_quality_evidence_matrix.csv`
- `experiments/20260709_155523/reports/benchmark-quality-literature-synthesis.md`
- `experiments/20260709_155523/handoffs/benchmark-quality-literature-review-003.md`

## Tóm tắt kết quả

Kế hoạch 01 cho thấy các bài báo không thường có một phần riêng tên “đánh giá chất lượng của bộ đánh giá”. Thay vào đó, họ chứng minh bộ đánh giá tốt qua bốn lớp: độ phủ có cấu trúc, kiểm soát chất lượng dữ liệu, kiểm tra độ tin cậy của bộ chấm/người chấm, và khả năng phân biệt mô hình/gia sư mạnh/yếu.

VietLegal là bài báo mạnh nhất cho quy trình dữ liệu tiếng Việt có nguồn chính thức, công cụ truy xuất, chuyên gia gán nhãn, độ đồng thuận và kiểm tra rò rỉ/trùng dữ liệu. KMP-Bench là bài báo mạnh nhất cho quy trình hội thoại thô sinh/kiểm tra/cắt lượt gia sư/phản hồi tham chiếu. TutorBench là bài báo mạnh nhất cho tiêu chí chấm riêng theo mẫu và kiểm tra bộ chấm tự động. MathTutorBench là bài báo mạnh cho việc tách năng lực giải bài khỏi năng lực gia sư.

## Quyết định của người điều phối

Không gọi thêm tác nhân chuyên trách vì phạm vi đủ để làm tuần tự. Các tệp kết quả được viết bằng tiếng Việt, chỉ giữ tiếng Anh ở tên bài báo, tên thước đo, tên mô hình, tên trường kỹ thuật, đường dẫn web và đường dẫn tệp khi cần. Ma trận bằng chứng được tạo theo lược đồ của `research-methodologist`.

## Điểm chưa chắc chắn

- VietLegal có tệp PDF cục bộ mang mã kiểu arXiv, nhưng lượt tra cứu trực tuyến không trả về kết quả rõ; ma trận dùng đường dẫn `https://arxiv.org/abs/2512.14554` theo mã PDF cục bộ.
- KMP-Bench có tệp PDF cục bộ là bản AAAI-26; ma trận dùng đường dẫn arXiv đã xác nhận qua tra cứu trực tuyến.
- Các kết luận chuyển sang Tin học THCS là suy luận, cần HNMU xác nhận.

## Kiểm tra đã chạy

- `/home/quannda/miniconda3/envs/benchmark_env/bin/python agents/research-methodologist/scripts/validate_evidence_matrix.py experiments/20260709_155523/literature_benchmark_quality/benchmark_quality_evidence_matrix.csv` — đạt.
- `/home/quannda/miniconda3/envs/benchmark_env/bin/python -m pytest tests/agents -q` — 26 kiểm thử đạt.

## Câu hỏi mở và quyết định cần người dùng/HNMU

1. Có đo độ đồng thuận giữa các thầy cô HNMU trên một tập mẫu nhỏ không?
2. UET có được loại tạm mẫu trùng/gần trùng khỏi đợt dữ liệu chuyển đổi thử không?
3. Phản hồi tham chiếu gốc của HNMU có được chỉnh thành phản hồi gia sư mẫu sau khi UET đề xuất và HNMU duyệt không?
4. Cơ sở dữ liệu học liệu nên ưu tiên SGK lớp 9 hay toàn THCS 6–9 trước?
