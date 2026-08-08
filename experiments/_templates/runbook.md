# Runbook — Plan NN / <Tên thao tác>

Experiment: `<YYYYMMDD_HHMMSS>`
Plan: `PNN`

## Mục đích

Nêu thao tác cụ thể mà runbook giúp thực hiện.

## Điều kiện trước khi chạy

- Plan có dòng trạng thái `APPROVED`.
- Working tree và input đã được kiểm tra.
- Secret chỉ đến từ cơ chế ngoài repository.

## Cấu hình và input

- Config/version/hash:
- Input artifact/version/hash:
- Expected output:

## Preflight

```bash
<exact command>
```

## Chạy chính

```bash
<exact command>
```

## Resume

Nêu command hoặc ghi rõ thao tác không hỗ trợ resume.

## Validation

```bash
<exact command>
```

## Failure và rollback

Nêu dấu hiệu dừng, dữ liệu nào được giữ và cách quay lại trạng thái an toàn.

## Cleanup

Chỉ nêu action đã được plan cho phép; không đưa lệnh xóa rộng hoặc secret.

