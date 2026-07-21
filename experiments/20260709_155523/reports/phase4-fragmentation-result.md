# Kết quả Pha 4 — Tách fragment từ Markdown OCR của Nguyên

Ngày chạy bản đầu: 16/07/2026  
Ngày đồng bộ hiện tại: 18/07/2026  
Nguồn đầu vào chính: `shared/learning_resources/ocr_text/`  
Trạng thái: `draft`, dùng cho truy xuất/audit v0; chưa thay thế xác nhận chuyên môn của HNMU/UET.

## 1. Kết luận hiện tại

Pha 4 hiện đã được rebuild cho toàn bộ OCR Markdown SGK/SGV Tin học 6–9 do Nguyên gửi. Dữ liệu OCR Markdown nguồn được giữ nguyên ở `shared/learning_resources/ocr_text/`; kết quả tách đoạn được ghi thành artifact dẫn xuất.

Output chính:

```text
shared/learning_resources/registries/ocr_text_manifest.csv
shared/learning_resources/fragments/learning_resource_fragments.csv
shared/learning_resources/fragments/README.md
```

Kết quả hiện tại: **154** đơn vị OCR Markdown và **2750** fragment.

## 2. Manifest OCR Markdown

| Lớp | SGK | SGV |
| --- | --- | --- |
| 6 | 17 | 18 |
| 7 | 16 | 17 |
| 8 | 20 | 21 |
| 9 | 22 | 23 |

Trạng thái manifest:

| Trạng thái | Số dòng |
| --- | --- |
| draft | 154 |

Ghi chú đồng bộ: `build_ocr_text_manifest.py` hiện tự nối `sgk_thcs_topic_lesson_map_v0.csv` để bổ sung tên chủ đề/bài học từ mục lục SGK, kể cả các bài có hậu tố như 10A/10B. Vì vậy các bài SGK đều có `topic_title`; các bài SGV được nối theo bài SGK tương ứng. Các mục `hd_chung` của SGV không bắt buộc có topic bài học.

## 3. Fragment học liệu

| Lớp | SGK | SGV |
| --- | --- | --- |
| 6 | 223 | 383 |
| 7 | 302 | 414 |
| 8 | 315 | 400 |
| 9 | 296 | 417 |

Phân loại fragment:

| Loại fragment | Số lượng |
| --- | --- |
| activity | 1219 |
| content | 471 |
| table | 374 |
| teaching_objective | 276 |
| teaching_guidance | 246 |
| practice | 107 |
| application | 56 |
| answer_guidance | 1 |

Trạng thái fragment:

| Trạng thái | Số lượng |
| --- | --- |
| draft | 2750 |

Cờ cần HNMU review:

| needs_hnmu_review | Số lượng |
| --- | --- |
| false | 2503 |
| true | 247 |

Các fragment cần HNMU review chủ yếu là phần hướng dẫn dạy học, mục tiêu dạy học hoặc gợi ý đáp án trong SGV. Đây là quyết định bảo thủ: các đoạn này có thể hỗ trợ kiểm nhất quán nhưng không tự thay thế phán quyết chuyên môn.

## 4. Quy tắc tách fragment đã dùng

- Tách theo mốc trang trong Markdown OCR của Nguyên.
- Dùng heading để tạo `section_path`.
- Bảng Markdown được giữ thành fragment riêng khi phát hiện cấu trúc bảng.
- Loại các fragment chỉ có heading ngắn, không có nội dung đủ giá trị truy xuất.
- Mỗi fragment có `fragment_id` dạng `<learning_material_id>#F0001`.
- Không sửa file Markdown gốc của Nguyên.
- Với SGV, `topic_title` được nối theo bài SGK tương ứng để hỗ trợ lọc/truy xuất.

## 5. Cách chạy lại Pha 4

Dùng môi trường chính của dự án:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/learning_resources/build_ocr_text_manifest.py \
  --grade ""

/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/learning_resources/build_learning_resource_fragments.py
```

Không chạy OCR lại ở pha này. Nếu Nguyên gửi thêm OCR Markdown mới, đặt vào `shared/learning_resources/ocr_text/` theo đúng cấu trúc rồi chạy lại manifest → fragment → index.

## 6. Giới hạn hiện tại

1. Fragment vẫn là `draft`; chưa có xác nhận HNMU/UET cho ranh giới fragment.
2. OCR Markdown do Nguyên gửi khá tốt nhưng vẫn cần review mẫu trước khi dùng làm căn cứ chuyên môn cứng.
3. Lesson-position registry lấy từ dữ liệu HNMU thô, chưa phải kết quả audit đúng/sai.
4. Nếu sửa topic map hoặc OCR Markdown, phải rebuild lại manifest, fragment và index theo đúng thứ tự.
