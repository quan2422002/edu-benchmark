# Plan — Viết paper KSE 2026

Trạng thái: `APPROVED — IMPLEMENTATION_IN_PROGRESS`

- Hạn KSE: `31/07/2026`.
- Bản gửi giáo sư: trước `11:00, 29/07/2026`.
- Giới hạn bản nộp cuối: tối đa 6 trang, IEEE Conference LaTeX.
- Quyết định ngày 30/07: bản làm việc tạm thời được phép vượt 6 trang để hoàn thiện đầy đủ phần thực nghiệm; việc rút gọn sẽ được thực hiện sau khi duyệt nội dung.

## 1. Câu chuyện khoa học

Working title:

> Building a Vietnamese LowerSecondary Informatics AI Tutor Benchmark
> from Teacher-Authored Dialogues

Paper trình bày **quy trình xây dựng, đặc tả đo lường và thực nghiệm đánh giá benchmark**; các kết luận thực nghiệm phải báo riêng theo từng judge và không được diễn giải thành chất lượng tuyệt đối.

Ba câu hỏi nghiên cứu:

1. Làm thế nào chuyển hội thoại do giáo viên biên soạn thành candidate
   benchmark có truy vết và kiểm soát chất lượng?
2. Làm thế nào kết hợp sáu nguyên tắc sư phạm với sáu năng lực gia sư để
   xác định yêu cầu và tiêu chí chấm cho từng phản hồi?
3. Trên tập benchmark hoàn chỉnh, bộ rubric phân biệt các cấu hình gia sư đến mức nào và kết luận có ổn định giữa hai judge cùng phép gộp candidate/family hay không?

Ba đóng góp dự kiến:

1. Pipeline human-in-the-loop từ 1.050 hội thoại thô đến 665 hội thoại
   `pass` và 2.028 candidate, có provenance, family grouping và validator.
2. Phương pháp `requirement_score` cho sáu nguyên tắc và thư viện rubric
   hai tầng dựa trên sáu năng lực gia sư.
3. Tập benchmark gồm 1.400 mẫu hoàn chỉnh cùng phân tích thực nghiệm ba cấu hình gia sư bằng hai LLM judge, có bootstrap theo family và kiểm tra độ nhạy.

## 2. Giới hạn claim


| Loại              | Được viết                                                   | Cách diễn đạt                              |
| ------------------ | --------------------------------------------------------------- | ---------------------------------------------- |
| Kết quả pipeline | 665 hội thoại, 2.028 candidate, validation                    | Kết quả xác định của pipeline hiện tại |
| Kết quả Plan 03  | 12.168 score, 1.400/628/0 và phân bố nguyên tắc            | Model-assisted, single-run, provisional        |
| Rubric Plan 04     | 4 tiêu chí chung, 18 tiêu chí riêng, 6 lỗi nghiêm trọng | Thiết kế provisional, chờ UET/HNMU review   |
| Kết quả Plan 05 | 4.200 response, hai judge, điểm theo rubric, bootstrap, agreement và sensitivity | Báo riêng từng judge; chỉ kết luận khác biệt lớn được cả hai judge hỗ trợ |
| Plan 06–07 | Human calibration và các kiểm định tiếp theo | Future work |

Không tuyên bố learning gain, expert agreement, accuracy của
`requirement_score` hoặc benchmark đã được HNMU xác nhận.

## 3. Cấu trúc mục tiêu cho bản nộp 6 trang


| Phần | Nội dung | Ngân sách |
| --- | --- | ---: |
| Abstract + Introduction | vấn đề, ba khoảng trống, ba đóng góp | 0,8 trang |
| Related Work + Background | nền tảng sư phạm; benchmark gia sư; tiếng Việt/Tin học | 0,8 trang |
| Dataset Construction | Phase 1 audit; Phase 2 xây 6 năng lực–6 nguyên tắc; Phase 3 conversion, gán nguyên tắc, lọc và thống kê | 2,0 trang |
| Evaluation Framework | nạp context native; rubric `4 + 3n`; blind judge và `Win/Tie/Lose` | 1,0 trang |
| Experiments and Analysis | model tutor/judge, generation config, metrics và kết quả | 0,7 trang |
| Discussion + Conclusion | giới hạn và kết luận | 0,3 trang |
| References | tính trong giới hạn 6 trang | 0,4 trang |

Giữ một sơ đồ tổng thể có source `.drawio`; hình quy trình/đặc trưng Phase 1
chỉ được giữ nếu toàn bộ PDF, kể cả tài liệu tham khảo, không vượt 6 trang.
Bản làm việc giữ các bảng thực nghiệm chi tiết để review. Trước khi nộp, các bảng sẽ được chọn lọc hoặc gộp lại, với mục tiêu cuối là bảng thống kê dữ liệu và bảng kết quả đánh giá chính.

## 4. Quy trình sau khi UET duyệt

### Bước 1 — Scaffold và nguồn (`28/07`)

- Copy template thành `manuscript/main.tex`; không sửa bản template gốc.
- Tạo `manuscript/references.bib` và `manuscript/figures/`.
- Điền working title, outline và placeholder author/affiliation.
- Compile một PDF tối thiểu trước khi viết dài.

### Bước 2 — Viết phần nền trước (`28/07`)

Viết theo thứ tự:

1. `Introduction`;
2. `Related Work`;
3. nền tảng sáu nguyên tắc và sáu năng lực;
4. `Dataset and Construction`.

Ưu tiên KMP-Bench, MathTutorBench, TutorBench, nền tảng đo lường và khoảng
trống benchmark gia sư tiếng Việt. Mọi claim nghiên cứu phải có citation;
không trình bày suy luận của dự án như kết luận của paper nguồn.

### Bước 3 — Method, results và hình (`28–29/07`)

- Viết requirement scoring, rubric hai tầng và serious-error gate.
- Tạo một hình pipeline từ raw dialogue đến evaluation-ready candidate.
- Nhập các số liệu đã có trong `claim_evidence_registry.csv`.
- Viết `Discussion`, `Conclusion`, rồi hoàn thiện `Abstract` sau cùng.

### Bước 4 — Release gửi giáo sư (`trước 11:00, 29/07`)

- Compile PDF đọc được từ đầu đến cuối, kể cả khi một số kết quả còn
  provisional.
- Kiểm claim–evidence, citation, hình/bảng và số trang.
- Lưu PDF tại `releases/professor_review/` và ghi source hash trong
  `notes/manuscript_status.md`.
- Người dùng gửi bản v0.1 cho giáo sư; Codex không tự gửi.

### Bước 5 — Sửa và nộp (`29–31/07`)

- `29–30/07`: sửa feedback, khóa author/affiliation/track và cắt còn 6
  trang.
- `30/07`: tạo release candidate; kiểm không còn placeholder/TODO.
- `31/07`: người dùng/giáo sư duyệt và nộp thủ công qua CMT.

## 5. Output tối thiểu

```text
kse_submit_manuscript/
├── manuscript/
│   ├── main.tex
│   ├── references.bib
│   └── figures/pipeline.pdf
├── notes/
│   ├── claim_evidence_registry.csv
│   └── manuscript_status.md
└── releases/professor_review/
```

Không chia section thành nhiều file và không tạo snapshot trung gian nếu
chưa cần.

## 6. Cổng chất lượng

- `Story`: một problem statement, ba RQ và tối đa ba contribution khớp
  nhau.
- `Evidence`: mọi số liệu/claim chính có nguồn; provisional được ghi rõ.
- `Coherence`: method trả lời RQ; results không vượt quá bằng chứng.
- `Format`: bản làm việc phải compile được và giữ format IEEE; bản nộp cuối mới bắt buộc tối đa 6 trang.
- `Authority`: author, affiliation, track và bản nộp do người dùng/giáo
  sư duyệt; HNMU vẫn giữ thẩm quyền xác nhận sư phạm.

## 7. Thông tin cần chốt nhưng không chặn việc bắt đầu viết

1. Danh sách/thứ tự tác giả, affiliation và corresponding author.
2. Main Session hay Special Session.
3. Working title có cần đổi trước bản gửi giáo sư hay không.
