# Plan 02 — Source scope, tài liệu hỗ trợ benchmark và chuẩn hóa chủ đề Tin học THCS

Trạng thái: `DRAFT` — chờ duyệt  
Experiment: `20260705_215045`  
Owner chính: `learning-resource-curator`  
Có thể chạy độc lập: Có, không phụ thuộc paper review.

## 1. Mục tiêu

Xác định rõ học liệu chủ đạo, tài liệu hỗ trợ benchmark do HNMU cung cấp, và chuẩn hóa tên chủ đề xuyên suốt bộ SGK/SGV Tin học THCS. Đây là plan kiểm soát rủi ro coverage: nếu chưa có taxonomy chủ đề ổn định, mọi tuyên bố “phủ kiến thức” đều dễ bị đếm sai.

Sau cập nhật 06/07/2026, P02 cũng cần đăng ký và đọc ở mức nguồn đối với một số tài liệu HNMU cung cấp để P04/P06 dùng tiếp:

- tài liệu mô tả mức độ nhận thức môn Tin học;
- tài liệu mô tả khung dàn giáo/hội thoại minh họa;
- tài liệu mô tả dạng bài tập trong ma trận đề.

P02 chỉ quản lý nguồn, trích ý chính và ghi giới hạn sử dụng của các tài liệu này. P02 **không** chốt task/rubric, không viết hướng dẫn giáo viên, và không quyết định cuối cùng cách chia mức độ nhận thức.

Học liệu chủ đạo:

```text
SGK và SGV môn Tin học THCS trên trang tập huấn:
https://taphuan.nxbgd.vn/tap-huan?subjects=11
```

Ưu tiên trước mắt: lớp 9 và tiền kiến thức liên quan trong lớp 6–8.

## 2. Không làm trong plan này

- Không thiết kế task/rubric.
- Không đọc/synthesis paper nghiên cứu.
- Không tạo ví dụ phiếu tác giả.
- Không triển khai database production.
- Không sửa artifact của `20260701_100006`.
- Không chốt chính thức bốn mức `Nhận biết`, `Thông hiểu`, `Vận dụng`, `Vận dụng cao`; P02 chỉ tạo mapping nháp từ tài liệu HNMU và đánh dấu phần cần HNMU xác nhận.
- Không biến khung dàn giáo thành hướng dẫn giáo viên; P02 chỉ ghi chú các chức năng dàn giáo để P04/P06 tiêu thụ.

## 3. Input

- Link tập huấn Tin học: `https://taphuan.nxbgd.vn/tap-huan?subjects=11`.
- Link SGK đã ghi trong `user_diary.md`:
  - Lớp 6: `https://taphuan.nxbgd.vn/tap-huan/doc-sach/sgk-tin-hoc-6.4699918592#page=5`
  - Lớp 7: `https://taphuan.nxbgd.vn/tap-huan/doc-sach/sgk-tin-hoc-7.4700056620#page=5`
  - Lớp 8: `https://taphuan.nxbgd.vn/tap-huan/doc-sach/sgk-tin-hoc-8.4700157933#page=5`
  - Lớp 9: `https://taphuan.nxbgd.vn/tap-huan/doc-sach/sgk-tin-hoc-9.4700233123#page=3`
- Artifact tham khảo từ `20260701_100006/learning_resources/`.
- Tài liệu HNMU mới trong `document/teacher_training_curriculum/benchmark_building_documents/`:
  - `Biểu hiện mức độ nhận thức _Tin học.docx`: nguồn mô tả các mức `Biết`, `Hiểu`, `Vận dụng`; dùng để tạo mapping nháp sang cột `Mức độ nhận thức` trong phiếu tác giả/metadata.
  - `KhungDanGiao_HoiThoaiMinhHoa.docx`: nguồn mô tả các chức năng dàn giáo và hội thoại minh họa; dùng để P04/P06 hiểu scaffolding nhưng chưa chốt rubric/task tại P02.
  - `Các dạng bài tập.txt`: nguồn mô tả dạng bài `MC`, `YN`, `ES` và cách tính lệnh hỏi; dùng để chuẩn hóa cột `Format/dạng bài` nếu P04/P05 cần coverage theo dạng bài.

## 4. Output sở hữu

Plan này chỉ ghi vào:

```text
experiments/20260705_215045/source_scope/
experiments/20260705_215045/topic_taxonomy/
experiments/20260705_215045/reports/P02-*.md
experiments/20260705_215045/handoffs/P02-*.md
```

Artifact dự kiến:

| File | Vai trò |
|---|---|
| `source_scope/sgk_sgv_source_scope.md` | Mô tả phạm vi SGK/SGV, lớp, loại tài liệu, nguồn link, trạng thái truy cập/snapshot. |
| `source_scope/sgk_sgv_source_registry.csv` | Registry nguồn SGK/SGV, gồm lớp, loại, URL, source_key, trạng thái. |
| `source_scope/benchmark_support_source_registry.csv` | Registry các tài liệu HNMU hỗ trợ xây benchmark, ví dụ mức độ nhận thức, khung dàn giáo, dạng bài. Tạo file này để các plan sau truy vết được nguồn local thay vì trích dẫn miệng. |
| `source_scope/cognitive_level_seed_map.md` | Mapping nháp từ `Biết`, `Hiểu`, `Vận dụng` trong tài liệu HNMU sang `Nhận biết`, `Thông hiểu`, `Vận dụng`, `Vận dụng cao`. Tạo file này vì P03/P04 đã tách Bloom thành cột `Mức độ nhận thức`, nhưng tài liệu HNMU hiện mới có 3 mức. |
| `source_scope/scaffolding_function_notes.md` | Ghi chú có truy vết về 5 chức năng dàn giáo và ví dụ hội thoại. Tạo file này để P04/P06 dùng khi định nghĩa task/rubric/hướng dẫn, nhưng không biến nó thành hướng dẫn giáo viên trong P02. |
| `source_scope/exercise_format_notes.md` | Ghi chú về các dạng bài `MC`, `YN`, `ES` và đơn vị `lệnh hỏi`. Tạo file này để P04/P05 có căn cứ khi thiết kế coverage theo format. |
| `topic_taxonomy/thcs_topic_taxonomy_v0.md` | Luận giải chủ đề chuẩn xuyên suốt Tin học THCS. |
| `topic_taxonomy/thcs_topic_taxonomy_v0.csv` | Bảng chủ đề chuẩn, mã chủ đề, mô tả, trạng thái HNMU review. |
| `topic_taxonomy/source_topic_alias_map.csv` | Map tên chủ đề gốc trong SGK/SGV về chủ đề chuẩn. |
| `topic_taxonomy/coverage_unit_registry.csv` | Đơn vị coverage: bài/mục/chủ đề nào được đếm khi đo độ phủ. |
| `reports/P02-topic-taxonomy-open-questions.md` | Câu hỏi cần HNMU xác nhận về chủ đề/coverage. |
| `reports/P02-benchmark-support-open-questions.md` | Câu hỏi cần HNMU/giáo sư xác nhận về mức độ nhận thức, chức năng dàn giáo và dạng bài. |

## 5. Acceptance criteria

- Có danh sách SGK/SGV lớp 6–9 hoặc ghi rõ nguồn nào chưa truy cập/snapshot được.
- Có registry riêng cho tài liệu HNMU hỗ trợ benchmark, tối thiểu gồm tài liệu mức độ nhận thức, khung dàn giáo và dạng bài.
- Có taxonomy chủ đề chuẩn tạm thời cho Tin học THCS.
- Mỗi tên chủ đề gốc được giữ lại trong alias map, không bị mất truy vết.
- Mapping từ `Biết`, `Hiểu`, `Vận dụng` sang bốn mức `Nhận biết`, `Thông hiểu`, `Vận dụng`, `Vận dụng cao` phải ghi rõ phần nào là nguồn trực tiếp, phần nào là suy luận cần HNMU xác nhận.
- Ghi chú khung dàn giáo phải giữ nguyên tinh thần “chức năng dàn giáo”, không diễn giải thành quy trình cứng theo thời gian.
- Mỗi quyết định suy luận đều gắn `needs_hnmu_review`.
- Plan sau có thể dùng `thcs_topic_taxonomy_v0.csv`, `coverage_unit_registry.csv` và các notes trong `source_scope/` mà không cần sửa lại plan này.

## 6. Validation

- Kiểm tra CSV có header bắt buộc, ID không trùng.
- Kiểm tra mỗi alias map trỏ tới topic chuẩn tồn tại.
- Kiểm tra `benchmark_support_source_registry.csv` có đường dẫn local hoặc ghi chú truy xuất cho từng tài liệu HNMU.
- Chạy validator học liệu nếu tạo source/fragment mapping theo schema hiện có.
- Chạy `pytest tests/agents -q` nếu có thay đổi tài liệu/validator liên quan.

## 7. Handoff

Handoff cần nêu rõ:

- nguồn nào đã snapshot/đọc được;
- nguồn nào mới chỉ có URL;
- tài liệu HNMU nào được dùng làm nguồn hỗ trợ benchmark và vai trò của từng tài liệu;
- chủ đề nào chắc từ SGK/SGV;
- chủ đề nào là suy luận cần HNMU xác nhận;
- điểm nào về mức độ nhận thức, dàn giáo và dạng bài cần P04/P06 hoặc HNMU quyết định tiếp.

## 8. Ghi chú cập nhật

- 06/07/2026: Bổ sung 3 tài liệu HNMU trong `document/teacher_training_curriculum/benchmark_building_documents/` vào input của P02. P02 vẫn ở trạng thái `DRAFT`; chưa triển khai source registry/taxonomy cho tới khi được duyệt.
