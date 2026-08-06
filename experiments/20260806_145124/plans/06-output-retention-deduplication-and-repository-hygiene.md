# Plan 06 — Retention output, khử trùng lặp và vệ sinh repository

Experiment: `20260806_145124`
Trạng thái: `DRAFT — AWAITING PLAN 05 COMPLETION AND PROJECT-LEAD APPROVAL`
Phụ thuộc: Plan 01–05

## 1. Mục tiêu

Giảm số file và dung lượng Git mà không mất provenance, khả năng tái lập hoặc
artifact duy nhất. Plan này đặc biệt xử lý JSONL lớn, snapshot lặp, file tạm,
log và output có thể dựng lại.

## 2. Phân lớp artifact

| Lớp | Ví dụ | Chính sách đích |
|---|---|---|
| Canonical shared | registry, selection, spec được promote | Track theo version nếu quyền/dung lượng cho phép |
| Reproducibility manifest | config/hash/count/cost/schema | Track trong Git |
| Human report | phân tích/gate/final report | Track, giữ cô đọng |
| Raw/provider output lớn | batch input/output, run JSONL lớn | Ignore hoặc external object store; track locator + checksum |
| Derived/rebuildable | bảng join, cache, generated request | Không track nếu dựng lại được |
| Ephemeral | `.orig`, log, temp, xdv/cache | Ignore; dọn sau duyệt |
| Historical unique | bằng chứng cũ không còn consumer | Archive có manifest, không xóa theo cảm tính |

Git LFS chỉ được cân nhắc khi project thực sự cần version payload lớn trong Git;
không dùng LFS để né việc phân loại raw/derived/canonical.

## 3. Quy tắc an toàn

- Inventory size, hash, tracked/untracked và reference trước mọi cleanup.
- Xác nhận shared promotion và consumer migration đã hoàn tất.
- Tạo archive/backup locator và verify checksum trước khi bỏ bản trong repo.
- Mọi thao tác xóa hoặc rewrite Git history là một quyết định phá hủy riêng,
  cần project lead phê duyệt chính xác target và cách khôi phục.
- Plan được `APPROVED` không mặc nhiên cho phép `git filter-repo`, xóa remote,
  hoặc xóa toàn bộ output cũ.

## 4. Các bước triển khai dự kiến

1. Sinh inventory theo size/type/hash/consumer/status.
2. Phát hiện duplicate nội dung và file có thể rebuild.
3. Đề xuất retention table theo từng target path, kèm reclaimed size.
4. Duyệt riêng các action `keep`, `promote`, `externalize`, `archive`, `delete`.
5. Cập nhật `.gitignore` theo thư mục output cụ thể; không dùng `*.jsonl` toàn repo.
6. Thực hiện action đã duyệt theo batch nhỏ, verify sau mỗi batch.
7. Chạy test/link/checksum và ghi manifest cleanup.

## 5. Phạm vi ghi dự kiến

- `.gitignore`, tài liệu retention và archive locator
- experiment outputs/snapshots chỉ sau target-specific approval
- cleanup tooling/tests
- experiment artifacts Plan 06

Không rewrite history trong phạm vi mặc định của plan.

## 6. Nghiệm thu

- Không còn file tracked vượt giới hạn GitHub 100 MB trong HEAD đích.
- JSONL cần thiết trong code/test không bị ignore bởi pattern toàn repo.
- Mỗi payload externalized có locator, checksum, schema/count và cách restore.
- Shared/canonical artifact vẫn truy cập được qua registry.
- Duplicate removal không làm hỏng consumer hoặc link tài liệu.
- Báo cáo trước/sau nêu file count, tracked size và dung lượng thu hồi.

## 7. Rủi ro và rollback

Đây là plan rủi ro cao nhất vì có thể mất dữ liệu. Mặc định chỉ inventory và
externalize có bản sao xác minh. Nếu checksum/restore drill thất bại, dừng trước
cleanup và giữ nguyên file nguồn.

## 8. Quyết định cần duyệt

- Kho external/archive chính thức và retention period.
- Danh sách target được xóa chính xác, nếu có.
- Có cần xử lý large file đã nằm trong commit chưa push bằng history rewrite hay
  chỉ sửa các commit local cụ thể; đây là approval riêng ngoài plan chung.
