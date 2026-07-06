# Plan 07 — Nhận 20 mẫu pilot và kiểm tra lại thiết kế

Trạng thái: `DRAFT` — chờ duyệt sau khi HNMU có mẫu  
Experiment: `20260705_215045`  
Owner chính: orchestrator, phối hợp `benchmark-specification-designer` và `teacher-collaboration-designer`  
Phụ thuộc: P06 và dữ liệu pilot từ HNMU.

## 1. Mục tiêu

Nhận khoảng 20 mẫu pilot do HNMU tạo, kiểm tra xem phiếu tác giả, task theo Bloom, rubric rút gọn và bảng coverage có hoạt động trong thực tế không.

Plan này không sửa các plan trước. Nếu phát hiện cần đổi taxonomy/rubric/phiếu, tạo revision plan riêng.

## 2. Input

- 20 mẫu pilot từ HNMU.
- P06 teacher packet và ví dụ.
- P05 allocation matrix.
- P04 task/rubric.
- P02 topic taxonomy.

## 3. Không làm trong plan này

- Không sửa trực tiếp dữ liệu gốc của giáo viên nếu chưa có quy trình review.
- Không chốt benchmark chính thức.
- Không sửa artifact P02–P06 đã commit.
- Không tự động loại mẫu vì lý do chuyên môn nếu chưa có reviewer/HNMU xác nhận.

## 4. Output sở hữu

Plan này chỉ ghi vào:

```text
experiments/20260705_215045/pilot_intake/
experiments/20260705_215045/pilot_analysis/
experiments/20260705_215045/reports/P07-*.md
experiments/20260705_215045/handoffs/P07-*.md
```

Artifact dự kiến:

| File | Vai trò |
|---|---|
| `pilot_intake/pilot_sample_manifest.csv` | Danh sách mẫu nhận được, nguồn, trạng thái import. |
| `pilot_analysis/pilot_coverage_analysis.csv` | So sánh mẫu thật với allocation/coverage matrix. |
| `pilot_analysis/pilot_field_quality_notes.md` | Trường nào giáo viên điền khó/thiếu/không nhất quán. |
| `pilot_analysis/pilot_task_rubric_fit_notes.md` | Task/rubric có fit mẫu thật không. |
| `pilot_analysis/revision_requests.md` | Đề xuất revision plan nếu cần. |
| `reports/P07-pilot-analysis-summary.md` | Bản tóm tắt gửi Quân/giáo sư/HNMU. |

## 5. Acceptance criteria

- Mỗi mẫu pilot có trạng thái rõ: nhập được, thiếu dữ liệu, cần hỏi lại, hoặc chưa dùng được.
- Có phân tích phân bổ theo topic, Bloom, format.
- Có phân tích trường phiếu tác giả nào gây lỗi lặp lại.
- Có đề xuất rõ: giữ nguyên, cần revision plan, hay cần HNMU quyết định.
- Không sửa ngược artifact P02–P06.

## 6. Validation

- Kiểm tra manifest không trùng sample ID.
- Kiểm tra mọi sample map được tới topic/Bloom/format nếu đủ dữ liệu.
- Kiểm tra mọi revision request trỏ tới artifact liên quan nhưng không sửa trực tiếp artifact đó.

## 7. Handoff

Handoff cần nêu:

- 20 mẫu có đủ để kiểm tra thiết kế chưa;
- mẫu thiếu gì;
- taxonomy/rubric/phiếu tác giả cần revision ở đâu;
- plan mới nào nên được viết tiếp.
