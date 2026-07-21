# Fragment học liệu SGK/SGV Tin học THCS

Thư mục này chứa các đoạn học liệu đã được tách từ OCR Markdown của SGK/SGV Tin học 6–9. Fragment là đơn vị nội dung nhỏ hơn một bài học, dùng để truy xuất bằng từ khóa, kiểm tra tính nhất quán của dữ liệu hội thoại HNMU, và sau này làm nền cho hệ thống học liệu/retrieval của benchmark.

Trạng thái hiện tại: `draft`. Các fragment đủ dùng cho audit v0, nhưng chưa thay thế xác nhận chuyên môn cuối cùng của HNMU/UET.

## 1. Thành phần trong thư mục

```text
shared/learning_resources/fragments/
├── README.md
├── learning_resource_fragments.csv
└── .gitkeep
```

| File | Vai trò |
| --- | --- |
| `README.md` | File mô tả thư mục này, cách hiểu fragment và cách dùng bảng fragment. |
| `learning_resource_fragments.csv` | Bảng fragment chính, được sinh từ OCR Markdown trong `shared/learning_resources/ocr_text/`. |
| `.gitkeep` | File rỗng để Git giữ thư mục khi chưa có dữ liệu hoặc khi dữ liệu nặng bị bỏ qua. |

## 2. `learning_resource_fragments.csv` là gì?

`learning_resource_fragments.csv` là bảng chứa các đoạn học liệu đã được tách từ file Markdown OCR. Mỗi dòng là một fragment có mã riêng, kèm metadata để biết fragment đó thuộc quyển nào, lớp nào, bài nào, chủ đề nào, trang nào và lấy từ file Markdown nào.

Tính đến 19/07/2026, bảng này có:

| Trục | Phân bố |
| --- | --- |
| Tổng số fragment | 2.750 |
| Theo loại học liệu | 1.136 SGK, 1.614 SGV |
| Theo lớp | Lớp 6: 606; lớp 7: 716; lớp 8: 715; lớp 9: 713 |
| Theo trạng thái | 2.750 `draft` |
| Cần HNMU review | 247 `true`, 2.503 `false` |

Phân bố theo loại fragment:

| `fragment_type` | Số lượng | Ý nghĩa sơ bộ |
| --- | ---: | --- |
| `activity` | 1.219 | Hoạt động, câu hỏi hoạt động, nhiệm vụ học sinh cần làm. |
| `content` | 471 | Nội dung kiến thức chính hoặc đoạn giải thích. |
| `table` | 374 | Bảng trong SGK/SGV hoặc mục lục dạng bảng. |
| `teaching_objective` | 276 | Mục tiêu/yêu cầu cần đạt, thường gặp trong SGV. |
| `teaching_guidance` | 246 | Gợi ý dạy học/hướng dẫn triển khai bài, thường gặp trong SGV. |
| `practice` | 107 | Luyện tập, thực hành, bài tập. |
| `application` | 56 | Vận dụng/ứng dụng. |
| `answer_guidance` | 1 | Gợi ý đáp án hoặc hướng dẫn trả lời. |

Các nhãn này là nhãn kỹ thuật v0 để hỗ trợ truy xuất; chưa phải phân loại sư phạm cuối cùng.

## 3. Vai trò của fragment trong pipeline

Fragment nằm giữa OCR Markdown và index truy xuất:

```text
OCR Markdown theo bài
→ learning_resource_fragments.csv
→ SQLite FTS index
→ agent/code truy xuất evidence_fragment_id
→ audit dữ liệu HNMU hoặc kiểm benchmark candidate
```

Nói nôm na: OCR Markdown là bản đầy đủ để người đọc, còn fragment là bản đã chia nhỏ để máy/agent tìm đúng vùng cần đọc.

## 4. Các cột trong `learning_resource_fragments.csv`

| Cột | Ý nghĩa |
| --- | --- |
| `fragment_id` | Mã định danh duy nhất của fragment, ví dụ `LM-SGK-TIN6-0001#F0003`. Đây là mã nên ghi vào output audit khi dùng fragment làm bằng chứng. |
| `learning_material_id` | Mã quyển SGK/SGV, liên kết với `shared/learning_resources/registries/sgk_sgv_source_registry.csv`. |
| `ocr_text_id` | Mã đơn vị OCR Markdown, liên kết với `shared/learning_resources/registries/ocr_text_manifest.csv`. |
| `material_type` | Loại học liệu: `SGK` hoặc `SGV`. |
| `grade` | Khối lớp của học liệu. |
| `book_title` | Tên quyển sách. |
| `lesson_key` | Khóa bài học dạng ổn định, ví dụ `bai_01`. |
| `lesson_title` | Tên bài học. |
| `topic_title` | Tên chủ đề chứa bài học. |
| `page_start` | Trang bắt đầu theo trang in/marker trong OCR Markdown. |
| `page_end` | Trang kết thúc. |
| `page_marker_start` | Chỉ số marker trang bắt đầu trong file Markdown. |
| `page_marker_end` | Chỉ số marker trang kết thúc trong file Markdown. |
| `section_label` | Nhãn mục/tiểu mục gần nhất của fragment. |
| `section_path` | Đường dẫn phân cấp của mục, ví dụ chủ đề → bài → mục → hoạt động. |
| `fragment_type` | Loại fragment v0, ví dụ `content`, `activity`, `table`, `practice`. |
| `order_index` | Thứ tự fragment trong đơn vị OCR Markdown. |
| `location_note` | Mô tả vị trí dễ đọc cho người, thường gồm bài, section và trang. |
| `source_markdown_path` | File Markdown OCR gốc sinh ra fragment. |
| `markdown_text` | Nội dung Markdown đầy đủ của fragment. Đây là nội dung chính để người/agent đọc. |
| `text_preview` | Bản rút gọn của nội dung, phục vụ xem nhanh hoặc index nhẹ. |
| `status` | Trạng thái của fragment, hiện là `draft`. |
| `needs_hnmu_review` | Cờ cho biết fragment hoặc cách tách fragment có cần HNMU/UET xem lại không. |
| `notes` | Ghi chú về cách sinh fragment hoặc bất định cần lưu ý. |

## 5. Cách dùng trong audit dữ liệu HNMU

Khi specialist agent hoặc code cần kiểm một mẫu hội thoại, không nên mở toàn bộ SGK/SGV hoặc đọc thủ công cả thư mục Markdown. Luồng đúng là:

1. Lấy `grade`, `Bài`, `Vị trí`, `Câu hỏi`, `Đáp án (SGV)` từ dữ liệu HNMU.
2. Ánh xạ bài/chủ đề bằng registry trong `shared/learning_resources/registries/`.
3. Tìm fragment liên quan bằng SQLite index hoặc retrieval API.
4. Đọc `markdown_text`, `section_path`, `page_start`, `source_markdown_path` của fragment được trả về.
5. Ghi `fragment_id` vào cột evidence, ví dụ `evidence_fragment_id`, trong output audit.
6. Nếu fragment có `status = draft` hoặc `needs_hnmu_review = true`, kết luận phải giữ mức sơ bộ hoặc đưa vào hàng đợi review.

Ví dụ evidence trong audit nên trỏ tới fragment như sau:

```text
evidence_fragment_id = LM-SGK-TIN6-0001#F0003
evidence_source = shared/learning_resources/ocr_text/sgk_tin_hoc_6/tin_6_bai_1/tin_6_bai_1.md
evidence_match_reason = Fragment cùng lớp, cùng bài, chứa nội dung liên quan đến câu hỏi.
```

## 6. Quan hệ với các thư mục/file khác

| Thành phần | Quan hệ với fragment |
| --- | --- |
| `shared/learning_resources/ocr_text/` | Nguồn Markdown OCR đầy đủ. Fragment được sinh từ đây. |
| `shared/learning_resources/registries/ocr_text_manifest.csv` | Manifest cho biết mỗi OCR Markdown thuộc quyển/bài/chủ đề nào. |
| `shared/learning_resources/registries/sgk_sgv_source_registry.csv` | Registry cấp quyển, giúp truy vết `learning_material_id`. |
| `shared/learning_resources/registries/sgk_thcs_topic_lesson_map_v0.csv` | Registry chủ đề/bài học, dùng để map coverage và đối chiếu bài học. |
| `shared/learning_resources/indexes/learning_resources_v0.sqlite` | Index truy xuất được build từ `learning_resource_fragments.csv`. |
| `src/edu_benchmark/learning_resources/` | Code sinh fragment, build index và truy xuất fragment. |
| `shared/learning_resources/agent_context/README.md` | Hub hướng dẫn agent tìm checklist, fragment, index và công cụ truy xuất. |

## 7. Nguyên tắc chỉnh sửa

Không nên sửa tay `learning_resource_fragments.csv` nếu thay đổi đó có thể tái sinh bằng code. Bảng này là artifact dẫn xuất từ OCR Markdown, nên quy trình an toàn là:

1. Sửa nguồn hoặc manifest nếu nguồn sai.
2. Rebuild fragment bằng script học liệu.
3. Rebuild SQLite index ngay sau đó.
4. Chạy test/validation liên quan.
5. Ghi lại báo cáo hoặc handoff nếu thay đổi ảnh hưởng đến audit/benchmark.

Không được đổi ý nghĩa của một `fragment_id` đã được dùng trong audit output. Nếu fragment không còn dùng được, nên chuyển trạng thái hoặc tái sinh toàn bộ output liên quan có truy vết rõ ràng.

## 8. Giới hạn hiện tại

- Tất cả fragment hiện vẫn là `draft`.
- Một số fragment được tách tự động từ OCR Markdown nên có thể chưa hoàn hảo về ranh giới đoạn.
- Các fragment dạng bảng giữ Markdown tốt hơn text thuần, nhưng vẫn cần kiểm người nếu dùng làm bằng chứng quan trọng.
- SGV thường có cấu trúc khác SGK; một số fragment SGV có thể dài hoặc thiên về hướng dẫn dạy học hơn là đáp án trực tiếp.
- Fragment phục vụ truy xuất và kiểm sơ bộ; phán quyết cuối cùng về đúng/sai kiến thức và sư phạm vẫn thuộc HNMU/UET.

## 9. Lệnh kiểm tra nhanh

Đếm số fragment theo loại:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python - <<'PY'
import csv
from collections import Counter
from pathlib import Path
p = Path('shared/learning_resources/fragments/learning_resource_fragments.csv')
rows = list(csv.DictReader(p.open(encoding='utf-8-sig', newline='')))
print('total', len(rows))
print('by_type', Counter(r['fragment_type'] for r in rows))
print('by_grade', Counter(r['grade'] for r in rows))
PY
```

Chạy test học liệu liên quan:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python -m pytest tests/learning_resources -q
```
