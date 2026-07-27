# Xác minh yêu cầu và LaTeX template cho KSE 2026

Ngày xác minh: 25/07/2026  
Mục đích: khóa nguồn chính thức trước khi tạo manuscript

## 1. Kết quả đã xác minh

| Nội dung | Kết quả | Nguồn |
|---|---|---|
| Hội nghị | The 18th International Conference on Knowledge and Systems Engineering — KSE 2026 | [Trang chính thức KSE 2026](https://kse2026.kse-conferences.org/) |
| Hạn full paper | 31/07/2026, đã được gia hạn | [Trang chính thức KSE 2026](https://kse2026.kse-conferences.org/) và [News](https://kse2026.kse-conferences.org/news/) |
| Giới hạn độ dài | Không quá 6 trang | [Call for Papers chính thức](https://kse2026.kse-conferences.org/call-for-papers/) |
| Định dạng | LaTeX series format theo IEEE | [Call for Papers chính thức](https://kse2026.kse-conferences.org/call-for-papers/) |
| Cổng nộp | Microsoft CMT, conference `KSE2026` | [Call for Papers chính thức](https://kse2026.kse-conferences.org/call-for-papers/) |
| Track | Main Session hoặc một Special Session | [Call for Papers chính thức](https://kse2026.kse-conferences.org/call-for-papers/) |
| Template | IEEE Conference Template, `\documentclass[conference]{IEEEtran}` | [IEEE Author Center](https://conferences.ieeeauthorcenter.ieee.org/write-your-paper/authoring-tools-and-templates/) và [IEEE Conference Template — Official trên Overleaf](https://www.overleaf.com/latex/templates/ieee-conference-template/grfzhhncsfqn) |

KSE không công bố một class LaTeX riêng mang tên hội nghị. “Template chính thức của KSE” trong thực tế là IEEE conference LaTeX template mà Call for Papers của KSE dẫn tới.

## 2. Template sẽ dùng khi plan được duyệt

Nguồn ưu tiên:

1. IEEE Template Selector: `https://template-selector.ieee.org/secure/templateSelector/publicationType`
2. IEEE Conference Template có nhãn `Official` trên Overleaf:
   `https://www.overleaf.com/latex/templates/ieee-conference-template/grfzhhncsfqn`

Contract tối thiểu:

```latex
\documentclass[conference]{IEEEtran}
```

Không sửa margin, font, column width hoặc các quy tắc format của `IEEEtran`.

### 2.1. Bản đã tải vào repository

Theo yêu cầu của project lead ngày 25/07/2026, package đã được tải từ một
official IEEE-hosted event path:

`https://attend.ieee.org/e12-2025/wp-content/uploads/sites/684/conference-latex-template.zip`

Canonical IEEE download URL mà trang template của IEEE công bố là:

`https://www.ieee.org/content/dam/ieee-org/ieee/web/org/conferences/conference-latex-template.zip`

Canonical URL trả WAF challenge trong môi trường hiện tại, nên byte package được
lấy từ `attend.ieee.org`, vẫn thuộc hạ tầng chính thức của IEEE. Nội dung archive
là bản template ngày 28/06/2024 và có cùng contract IEEE conference:

- `IEEE-conference-template-062824.tex`;
- `IEEEtran.cls`;
- `IEEEtran_HOWTO.pdf`;
- PDF mẫu và `fig1.png`.

Vị trí:

- archive nguyên bản: `conference-latex-template.zip`;
- thư mục đã giải nén: `IEEE-conference-template-062824/`.

SHA-256:

```text
conference-latex-template.zip
516252d9ac6e974af3a1d9aa72f97ecc462b9a47556225019fb0adef69bba78a

IEEE-conference-template-062824.tex
48b482fe3200577267ccf0b6359cab61e62ac1fadaa87c935f644bb313fdafa9

IEEEtran.cls
c972aca108fda004c3514d63658e02816da2e54d9a1451e870b9bd970e003f55
```

Các file trong thư mục này là bản nguồn để đối chiếu. Khi bắt đầu viết, tạo
manuscript working copy riêng; không sửa archive hoặc bản giải nén nguyên gốc.

## 3. Những điểm chưa thấy KSE công bố rõ trên website

Các điểm sau chưa được tự suy diễn:

- review single-blind hay double-blind;
- khổ giấy bắt buộc A4 hay US Letter;
- deadline theo múi giờ nào;
- tài liệu bổ sung có được phép hay không;
- copyright notice/PDF eXpress áp dụng ở submission đầu hay chỉ camera-ready;
- có cho phép trang vượt quá 6 trang kèm phí hay không.

Trước khi nộp, cần kiểm tra form CMT và email/announcement mới nhất. Nếu CMT và website khác nhau, dừng và hỏi ban tổ chức hoặc giáo sư thay vì tự chọn.

## 4. Track có khả năng phù hợp

- `Main Session – KSE 2026`: phương án tổng quát cho benchmark, human–AI interaction và machine learning applications.
- `Special Session – ELLMA`: trang chính thức nêu các chủ đề như data resource construction and analysis, multilingual/cross-lingual modeling và efficient LLM applications in education.

Việc chọn track là quyết định của tác giả/giáo sư. Plan manuscript đặt hạn chốt track trước khi gửi bản đầu cho giáo sư.

## 5. Tình trạng công cụ local

Tại thời điểm xác minh, workspace chưa có `latexmk`, `pdflatex`, `bibtex`, `biber` hoặc `chktex` trên `PATH`.

Do hạn gần, đường build mặc định trong plan là:

- soạn source trong repository;
- compile bằng official IEEE template trên Overleaf;
- chỉ cài local LaTeX toolchain nếu có phê duyệt riêng và không làm chậm bản gửi giáo sư.

Không tải một ZIP không xác minh từ mirror bên thứ ba để thay cho template chính thức.
