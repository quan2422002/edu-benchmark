# Plan 02 — Đóng gói Python và kiểm chứng môi trường sạch

Experiment: `20260806_145124`
Trạng thái: `DRAFT — AWAITING PLAN 01 COMPLETION AND PROJECT-LEAD APPROVAL`
Phụ thuộc: Plan 01

## 1. Mục tiêu

Biến `src/edu_benchmark/` thành package có thể cài và import nhất quán, thay vì
phụ thuộc working directory hoặc `sys.path` injection. Ghi rõ dependency để
một máy sạch có thể dựng lại môi trường và chạy test offline tối thiểu.

`pyproject.toml` giải quyết metadata build/install và mapping package từ `src/`.
Nó không tự khóa toàn bộ environment; vì vậy plan còn cần một bản khai môi
trường/lock phù hợp với `benchmark_env`.

## 2. Phạm vi

- Tạo `pyproject.toml` theo src-layout và editable install.
- Chuẩn hóa import thành `edu_benchmark...`; loại `src.edu_benchmark...` và
  `sys.path` injection khỏi production/test khi migration hoàn tất.
- Phân loại dependency runtime, development/test và provider-optional.
- Chọn một nguồn tái tạo môi trường có version; không dùng system/base Python.
- Thêm CI offline tối thiểu cho format/lint cần thiết, unit test và validator.
- Không cài credential và không gọi Vertex/OpenAI/paid API trong CI.

## 3. Khảo sát bắt buộc trước khi sửa

- Import graph của `src/`, `scripts/`, `tests/`.
- Nội dung `requirements.txt`, các import chỉ xuất hiện ở runner provider và
  dependency hệ thống ngoài pip nếu có.
- Các shell wrapper chứa absolute path hoặc giả định Conda hiện hành.
- Test đang dựa vào `tests/conftest.py` để sửa `sys.path`.

## 4. Các bước triển khai dự kiến

1. Chụp baseline lệnh test/import hiện tại bằng `benchmark_env`.
2. Viết `pyproject.toml` và environment specification được chọn.
3. Sửa import theo từng nhóm nhỏ, giữ behavior cũ.
4. Thay test path injection bằng package install.
5. Thêm CI offline trên hệ điều hành được project lead chọn.
6. Thử cài editable và chạy smoke import/test trong môi trường sạch có kiểm soát.
7. Ghi exact interpreter, dependency resolution và giới hạn tái lập.

## 5. Phạm vi ghi dự kiến

- `pyproject.toml`, dependency/environment files
- `.github/workflows/` nếu project lead duyệt CI GitHub Actions
- `src/edu_benchmark/`, `scripts/`, `tests/` chỉ cho import/entry point cần thiết
- docs và experiment artifacts của Plan 02

Plan này chưa thực hiện refactor nghiệp vụ lớn của Plan 05.

## 6. Nghiệm thu

- `benchmark_env` cài project editable và import `edu_benchmark` từ ngoài repo
  root mà không sửa `sys.path`.
- Test offline liên quan chạy bằng đúng interpreter bắt buộc.
- Không còn production import theo prefix `src.`.
- Dependency provider tùy chọn không làm unit test offline thất bại vô cớ.
- CI không đọc secret và không phát sinh network/API charge ngoài bước cài đặt.
- Có hướng dẫn dựng môi trường và ghi rõ phần nào được lock/phần nào chưa.

## 7. Rủi ro và rollback

Import migration có thể phá các wrapper lịch sử. Phải giữ compatibility entry
point tạm thời hoặc rollback từng nhóm import; không xóa wrapper trước Plan 05.

## 8. Quyết định cần duyệt

- Loại environment lock chính thức: Conda explicit/environment lock hay cơ chế
  tương đương phù hợp Linux/Windows.
- Phạm vi OS của CI ban đầu.
- Dependency provider nào là core, dependency nào là optional.
