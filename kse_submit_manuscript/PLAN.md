# Plan — Viết paper KSE 2026

Trạng thái: `APPROVED — IMPLEMENTATION_IN_PROGRESS`

- Hạn KSE: `31/07/2026`.
- Bản gửi giáo sư: trước `11:00, 29/07/2026`.
- Giới hạn: tối đa 6 trang, IEEE Conference LaTeX.

## 1. Câu chuyện khoa học

Working title:

> Building a Vietnamese LowerSecondary Informatics AI Tutor Benchmark
> from Teacher-Authored Dialogues

Paper trình bày **quy trình xây dựng và đặc tả đo lường benchmark**, chưa
khẳng định benchmark đã được chuyên gia freeze và chưa cần kết quả đánh
giá nhiều tutor model.

Ba câu hỏi nghiên cứu:

1. Làm thế nào chuyển hội thoại do giáo viên biên soạn thành candidate
   benchmark có truy vết và kiểm soát chất lượng?
2. Làm thế nào kết hợp sáu nguyên tắc sư phạm với sáu năng lực gia sư để
   xác định yêu cầu và tiêu chí chấm cho từng phản hồi?
3. Pool candidate hiện tại có phân bố yêu cầu sư phạm và mức sẵn sàng đưa
   vào benchmark như thế nào?

Ba đóng góp dự kiến:

1. Pipeline human-in-the-loop từ 1.050 hội thoại thô đến 665 hội thoại
   `pass` và 2.028 candidate, có provenance, family grouping và validator.
2. Phương pháp `requirement_score` cho sáu nguyên tắc và thư viện rubric
   hai tầng dựa trên sáu năng lực gia sư.
3. Phân tích pool hiện tại: 1.400 candidate ưu tiên, 628 candidate chờ UET
   review và phân bố tập nguyên tắc ở cấp candidate/family.

## 2. Giới hạn claim


| Loại              | Được viết                                                   | Cách diễn đạt                              |
| ------------------ | --------------------------------------------------------------- | ---------------------------------------------- |
| Kết quả pipeline | 665 hội thoại, 2.028 candidate, validation                    | Kết quả xác định của pipeline hiện tại |
| Kết quả Plan 03  | 12.168 score, 1.400/628/0 và phân bố nguyên tắc            | Model-assisted, single-run, provisional        |
| Rubric Plan 04     | 4 tiêu chí chung, 18 tiêu chí riêng, 6 lỗi nghiêm trọng | Thiết kế provisional, chờ UET/HNMU review   |
| Plan 05–07        | Panel model, judge và đánh giá khả năng phân biệt       | Giao thức dự kiến hoặc future work         |

Không tuyên bố learning gain, expert agreement, accuracy của
`requirement_score` hoặc benchmark đã được HNMU xác nhận.

## 3. Cấu trúc 6 trang


| Phần                              | Nội dung                                                     | Ngân sách |
| ---------------------------------- | ------------------------------------------------------------- | ----------: |
| Abstract + Introduction            | vấn đề, khoảng trống, ba đóng góp                     |   0,8 trang |
| Related Work + Background          | benchmark gia sư, KMP, sáu nguyên tắc và sáu năng lực |   0,9 trang |
| Dataset and Construction           | audit, conversion, provenance, family                         |   1,5 trang |
| Pedagogical Requirement and Rubric | requirement scoring và rubric hai tầng                      |   1,1 trang |
| Results                            | thống kê pipeline, Plan 03 và artifact Plan 04             |   0,8 trang |
| Discussion + Conclusion            | giới hạn, expert review, future evaluation                  |   0,4 trang |
| References                         | nguồn trực tiếp                                            |   0,5 trang |

Chỉ dùng một hình pipeline và tối đa hai bảng: thống kê dữ liệu và tóm tắt
khung đo lường/kết quả.

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
- `Format`: compile được, tối đa 6 trang, không sửa format IEEE.
- `Authority`: author, affiliation, track và bản nộp do người dùng/giáo
  sư duyệt; HNMU vẫn giữ thẩm quyền xác nhận sư phạm.

## 7. Thông tin cần chốt nhưng không chặn việc bắt đầu viết

1. Danh sách/thứ tự tác giả, affiliation và corresponding author.
2. Main Session hay Special Session.
3. Working title có cần đổi trước bản gửi giáo sư hay không.
