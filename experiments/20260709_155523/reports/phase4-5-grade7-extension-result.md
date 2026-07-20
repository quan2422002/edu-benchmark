# Kết quả mở rộng Pha 4–5 sang SGK/SGV Tin học 7 — mốc lịch sử

Ngày chạy: 17/07/2026  

## Cập nhật trạng thái ngày 18/07/2026

Báo cáo này là mốc lịch sử khi Pha 4–5 mới mở rộng đến lớp 7. Trạng thái hiện tại đã được rebuild cho SGK/SGV Tin học 6–9: 154 đơn vị OCR Markdown, 2.750 fragment và SQLite FTS index. Xem bản hiện tại ở `reports/phase4-fragmentation-result.md`, `reports/phase5-retrieval-index-result.md` và `reports/learning-resource-registries-sync-20260718.md`.

Nguồn đầu vào: `shared/learning_resources/ocr_text/`

## 1. Kết luận

Đã xử lý thêm SGK và SGV Tin học 7 do Nguyên bổ sung. Pipeline Pha 4–5 hiện index chung SGK/SGV Tin học 6–7.

Không chạy OCR lại, không sửa Markdown nguồn và không đụng vào các output/probe OCR-MinerU cũ.

## 2. Kết quả manifest

Manifest mới:

```text
shared/learning_resources/registries/ocr_text_manifest.csv
```

Có 68 dòng:

| Nhóm | Số file |
|---|---:|
| SGK Tin học 6 | 17 |
| SGV Tin học 6 | 18 |
| SGK Tin học 7 | 16 |
| SGV Tin học 7 | 17 |

Trạng thái manifest:

| Trạng thái | Số dòng |
|---|---:|
| `draft` | 29 |
| `needs_uet_review` | 39 |

Các dòng `needs_uet_review` chủ yếu do chưa suy ra chắc `topic_title` trực tiếp từ heading, cần nối thêm từ mục lục/registry ở vòng sau.

## 3. Kết quả fragment

Fragment mới:

```text
shared/learning_resources/fragments/learning_resource_fragments.csv
```

Có 1322 fragment:

| Nhóm | Số fragment |
|---|---:|
| SGK Tin học 6 | 223 |
| SGV Tin học 6 | 383 |
| SGK Tin học 7 | 302 |
| SGV Tin học 7 | 414 |

Phân loại fragment:

| Loại fragment | Số lượng |
|---|---:|
| `activity` | 618 |
| `table` | 220 |
| `content` | 194 |
| `teaching_guidance` | 117 |
| `teaching_objective` | 101 |
| `practice` | 49 |
| `application` | 22 |
| `answer_guidance` | 1 |

Có 118 fragment được đánh dấu `needs_hnmu_review=true`.

## 4. Kết quả index

Index được build lại tại:

```text
shared/learning_resources/indexes/learning_resources_v0.sqlite
```

Index hiện có:

| Thành phần | Số lượng |
|---|---:|
| Source OCR Markdown | 68 |
| Fragment | 1322 |

File SQLite là artifact sinh lại được và đang được `.gitignore` bỏ qua.

## 5. Query thử lớp 7

### “bảng tính điện tử” với `grade=7`

Kết quả đầu trả về SGV Bài 10 và SGK các bài về bảng tính, ví dụ:

```text
LM-SGV-TIN7-4920462481#F0270
Bài 10. HOÀN THIỆN BẢNG TÍNH
section_path: ... > A MỤC ĐÍCH, YÊU CẦU > 1. Kiến thức
```

### “thuật toán tìm kiếm tuần tự” với `grade=7`

Kết quả trả về đúng Bài 14 SGK Tin học 7, ví dụ:

```text
LM-SGK-TIN7-0001#F0255
Bài 14. THUẬT TOÁN TÌM KIẾM TUẦN TỰ
```

Một số kết quả đầu có thể là caption hình hoặc bảng trước khi tới đoạn giải thích chính; đây là điểm có thể tinh chỉnh ranking ở vòng sau.

## 6. Validation

Chạy bằng:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python -m pytest tests/learning_resources tests/agents -q
```

Kết quả:

```text
40 passed
```

## 7. Ghi chú tiếp theo

- Cần nối `topic_title` từ mục lục/registry để giảm số dòng `needs_uet_review`.
- Có thể tinh chỉnh ranking để ưu tiên đoạn giải thích nội dung hơn caption hình khi query khái niệm.
- Nên chốt chính sách Git cho ảnh `.jpg` trong `shared/learning_resources/ocr_text` trước khi push.
