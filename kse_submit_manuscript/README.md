# KSE 2026 manuscript workspace

Thư mục này dành cho source, notes, figures và các bản PDF của bài nộp KSE 2026 về benchmark gia sư AI môn Tin học THCS.

Canonical writing plan:

- [PLAN.md](PLAN.md)

Xác minh template và yêu cầu hội nghị:

- [template_source_verification.md](template_source_verification.md)

Trạng thái hiện tại:

- plan đã được UET duyệt và đang `APPROVED — IMPLEMENTATION_IN_PROGRESS`;
- source `manuscript/main.tex` đã có bản nháp `Introduction` và
  `Related Work and Background`, cùng `manuscript/references.bib`;
- Section V giữ nguyên `Experimental Setup`, đã gom kết quả full vào
  `Main Results` và hoàn thành `Ablation Study` gồm instruction ablation,
  judge robustness và descriptive position sensitivity; đặc tả và bundle
  đã validate được liên kết trong
  `notes/section-v-ablation-analysis-requirements.md`;
- evidence registry đã nhận ba claim tạm thời từ Plan 03 tại
  `notes/claim_evidence_registry.csv`; mọi claim requirement-scoring đều
  ghi rõ giới hạn single-run và trạng thái chờ UET;
- official IEEE Conference LaTeX package đã được lưu nguyên bản tại
  `conference-latex-template.zip` và giải nén vào
  `IEEE-conference-template-062824/`;
- file mẫu để đối chiếu là
  `IEEE-conference-template-062824/IEEE-conference-template-062824.tex`;
- hạn KSE chính thức: 31/07/2026;
- mốc gửi giáo sư bản review đầu tiên: trước 11:00 ngày 29/07/2026;
- template: IEEE Conference LaTeX, `IEEEtran` ở conference mode;
- giới hạn: không quá 6 trang theo Call for Papers.

# Cài đặt

Nếu máy Ubuntu chưa có toolchain LaTeX, chạy lệnh sau để cài:

```
sudo apt update
sudo apt install -y \
  latexmk \
  texlive-latex-base \
  texlive-latex-extra \
  texlive-fonts-recommended \
  texlive-publishers
```

Sau đó, biên dịch file .tex thành file  pdf bằng 2 câu lệnh sau:

```
cd edu-benchmark/kse_submit_manuscript/manuscript

latexmk -pdf \
  -interaction=nonstopmode \
  -halt-on-error \
  main.tex

```

`latexmk` sẽ tự chạy `pdflatex`, `bibtex` và lặp lại số lần cần thiết để cập nhật citation. File kết quả sẽ là:

```
edu-benchmark/kse_submit_manuscript/manuscript/main.pdf
```
