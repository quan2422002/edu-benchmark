# Rà soát căn cứ chấm cho các tiêu chí agent trong checklist dữ liệu thô

Ngày rà soát: 21/07/2026  
Phạm vi: `raw-dialogue-audit-criteria-v0.csv`, `raw-dialogue-quality-checklist-v0.md`, hub ngữ cảnh `shared/learning_resources/agent_context/`  
Mục tiêu: xác định tiêu chí nào đã có căn cứ đủ rõ để specialist agent chấm, tiêu chí nào còn dựa quá nhiều vào cảm nhận của agent.

## 1. Kết luận nhanh

Nhận định của Quân là đúng: vấn đề không chỉ nằm ở `RAW-CON-05`. Trong 18 tiêu chí cấp từng mẫu, có một nhóm tiêu chí hiện chưa có “nguồn chuẩn/căn cứ chấm” đủ rõ cho agent.

Có thể chia thành bốn nhóm:

1. **Đã có căn cứ khá tốt**: các tiêu chí dựa trên trường dữ liệu thô, SGK/SGV fragment, registry học liệu, hoặc output code.
2. **Có căn cứ nhưng cần viết rõ hơn**: các tiêu chí có thể dựa vào raw row hoặc học liệu, nhưng thiếu quy tắc quan sát/threshold cụ thể.
3. **Thiếu căn cứ chuẩn**: agent đang phải tự suy luận dựa trên kinh nghiệm chung, dễ chấm không nhất quán giữa shard.
4. **Nên chuyển bớt sang HNMU/UET xác nhận**: những tiêu chí mang tính sư phạm/ngôn ngữ/lứa tuổi nếu chưa có hướng dẫn cụ thể.

Điểm đáng lo nhất:

- `RAW-CON-05` thiếu nguồn chuẩn về mức nhận thức.
- `RAW-PED-02`, `RAW-PED-03`, `RAW-PED-04`, `RAW-PED-05` chưa có rubric quan sát đủ rõ.
- `RAW-DUP-04` cần output thống kê khuôn lặp hoặc quy tắc nhận diện khuôn AI, nếu không agent dễ chấm theo cảm giác.

## 2. Nguyên tắc nên áp dụng

Một tiêu chí giao cho agent chấm chỉ nên được dùng khi có ít nhất một trong các loại căn cứ sau:

| Loại căn cứ | Ví dụ | Agent dùng như thế nào |
|---|---|---|
| Trường dữ liệu thô | câu hỏi, đáp án, hội thoại, mức nhận thức, bài, vị trí | Đối chiếu trực tiếp, không cần nguồn ngoài. |
| Học liệu truy xuất | SGK/SGV fragment, SQLite full-text search, registry bài học/chủ đề | Tìm evidence, ghi `evidence_fragment_id`, giải thích vì sao khớp/không khớp. |
| Tài liệu phương pháp HNMU | phương pháp dàn giáo, mức nhận thức | Dùng làm chuẩn để nhận diện hành vi/cấp độ. |
| Output code | thiếu trường, nhãn lượt nói, độ dài, trùng/gần trùng | Agent chỉ diễn giải hoặc kiểm thêm, không tự thay code. |
| Chính sách/HNMU review | phù hợp lứa tuổi, giá trị sư phạm, trường hợp mơ hồ | Agent chỉ gắn cờ và nêu câu hỏi cần HNMU xác nhận. |

Nếu một tiêu chí không có căn cứ thuộc các nhóm trên, agent không nên `pass` tự tin. Kết quả nên là `uncertain` hoặc tiêu chí cần được tạm loại khỏi vòng chấm tự động cho đến khi có hướng dẫn.

## 3. Bảng rà soát 18 tiêu chí cấp từng mẫu

| Tiêu chí | Tên tiêu chí | Căn cứ hiện có | Đánh giá | Cần bổ sung |
|---|---|---|---|---|
| `RAW-STR-02` | Không thiếu trường lõi | Raw row fields; code đọc Excel; danh sách trường bắt buộc trong Plan 04 | **Đủ căn cứ** | Nên để code chấm chính, agent chỉ xem lại ngoại lệ. |
| `RAW-STR-03` | Có nhãn lượt nói | Raw dialogue text; regex trong `hnmu_audit.py` kiểm `HS:` và `AI:` | **Đủ căn cứ cơ học, thiếu quy ước mở rộng** | Nếu HNMU dùng nhãn khác, cần file quy ước nhãn lượt nói được chấp nhận. |
| `RAW-STR-04` | Hội thoại đủ dài để kiểm | Raw dialogue text; code đang dùng ngưỡng độ dài sơ bộ | **Cần viết rõ hơn** | Cần nêu ngưỡng tối thiểu: số lượt HS/AI, độ dài, trường hợp một lượt vẫn đủ/không đủ. |
| `RAW-CON-01` | Câu hỏi khớp bài/vị trí | SGK/SGV fragment, registry bài học/chủ đề, vị trí học liệu | **Đủ căn cứ** | Cần yêu cầu agent ghi rõ fragment hoặc lý do retrieval không chắc. |
| `RAW-CON-02` | Đáp án SGV khớp câu hỏi | Trường `Đáp án (SGV)`, SGV fragment nếu truy xuất được | **Đủ căn cứ tương đối** | Nếu không tìm được SGV fragment, phải gắn `needs_sgv_verification`, không pass tự tin. |
| `RAW-CON-03` | Hội thoại bám câu hỏi | Câu hỏi + hội thoại thô | **Có căn cứ trực tiếp nhưng thiếu rubric quan sát** | Cần mô tả thế nào là “bám”: trả lời đúng vấn đề, không đổi chủ đề, không bỏ qua ràng buộc chính. |
| `RAW-CON-04` | Hội thoại bám đáp án | Hội thoại + đáp án SGV + SGV fragment nếu có | **Đủ căn cứ tương đối** | Cần phân biệt “hướng tới đáp án” với “nói thẳng đáp án”; phần sau liên quan `RAW-PED-02`. |
| `RAW-CON-05` | Mức nhận thức hợp lý | Hiện chỉ có câu hỏi + mức nhận thức; chưa trỏ tới docx HNMU | **Thiếu căn cứ chuẩn** | Bắt buộc thêm bản Markdown chuẩn hóa từ `Biểu hiện mức độ nhận thức _Tin học.docx`. |
| `RAW-CON-06` | Không bịa học liệu | SGK/SGV fragment + hội thoại | **Đủ căn cứ nếu retrieval tốt** | Cần agent nêu rõ nội dung nào trong hội thoại được/không được học liệu hỗ trợ. |
| `RAW-CON-07` | Nhất quán metadata | Registry học liệu + raw metadata + câu hỏi/đáp án/hội thoại | **Đủ căn cứ tương đối** | Cần nhấn mạnh nguồn chuẩn là SGK/SGV registry, không phải cột raw của HNMU. |
| `RAW-PED-01` | Có dấu hiệu dàn giáo | `hnmu_scaffolding_method_canonical.md` và docx gốc HNMU | **Đủ căn cứ tương đối** | Có thể cần thêm ví dụ đạt/chưa đạt theo từng kỹ thuật dàn giáo. |
| `RAW-PED-02` | Không lộ đáp án quá sớm | Hội thoại + đáp án SGV | **Thiếu căn cứ vận hành rõ** | Cần quy tắc: khi nào “đưa đáp án” là quá sớm, khi nào được phép chốt đáp án sau gợi mở. |
| `RAW-PED-03` | Trình tự hội thoại hợp lý | Hội thoại thô; có thể liên hệ phương pháp dàn giáo | **Thiếu rubric quan sát** | Cần checklist nhỏ về trình tự: nêu vấn đề → gợi mở → học sinh phản hồi → củng cố/sửa sai. |
| `RAW-PED-04` | Lượt nói có giá trị | Hội thoại thô | **Thiếu căn cứ chuẩn** | Cần quy tắc nhận diện lượt thừa: khen chung chung, lặp ý, không thêm hỗ trợ, không phản hồi nội dung HS. |
| `RAW-PED-05` | Phù hợp lứa tuổi | Hội thoại thô; HNMU review khi không chắc | **Thiếu tiêu chí ngôn ngữ/lứa tuổi** | Cần file hướng dẫn ngôn ngữ phù hợp học sinh THCS; agent chỉ gắn cờ khi rõ rủi ro. |
| `RAW-PED-06` | Không thay thế bằng câu trả lời lạc hướng | Câu hỏi + hội thoại | **Có căn cứ trực tiếp nhưng chồng với `RAW-CON-03`** | Cần định nghĩa ranh giới: `RAW-CON-03` kiểm khớp nội dung, `RAW-PED-06` kiểm hành vi né/đánh tráo nhiệm vụ. |
| `RAW-DUP-03` | Biến thể tầm thường | `duplicate_candidates.csv`, text mẫu, cụm gần trùng | **Đủ nếu có output code** | Agent không nên tự tìm toàn batch; phải dựa vào cụm ứng viên do code tạo. |
| `RAW-DUP-04` | Khuôn AI lặp lại | Batch context, hội thoại nhiều mẫu | **Thiếu căn cứ/tool đủ rõ** | Cần báo cáo pattern bằng code hoặc quy tắc nhận diện khuôn lặp; agent không nên đọc toàn batch thủ công. |

## 4. Các tiêu chí cần ưu tiên sửa trước

### 4.1. Ưu tiên rất cao

#### `RAW-CON-05` — Mức nhận thức hợp lý

Vấn đề: thiếu nguồn chuẩn trực tiếp.  
Nguồn cần thêm:

```text
document/teacher_training_curriculum/benchmark_building_documents/Biểu hiện mức độ nhận thức _Tin học.docx
```

Đề xuất tạo:

```text
shared/learning_resources/agent_context/hnmu_cognitive_level_method_canonical.md
```

Sau đó cần chạy repair riêng cho `RAW-CON-05`.

#### `RAW-PED-02` — Không lộ đáp án quá sớm

Vấn đề: tiêu chí này phụ thuộc rất mạnh vào ý đồ của mẫu. Một số mẫu hội thoại thô có thể được viết để minh họa đáp án, không nhất thiết là benchmark task cuối cùng. Nếu không có quy tắc, agent sẽ dễ chấm theo cảm tính.

Cần bổ sung:

- thế nào là “đưa thẳng đáp án”;
- thế nào là “gợi mở đủ rồi mới chốt”;
- khi câu hỏi của học sinh đã quá cụ thể thì gia sư có được trả lời trực tiếp đến đâu;
- khi nào chỉ nên `uncertain`, không `fail`.

#### `RAW-PED-03` và `RAW-PED-04`

Vấn đề: “trình tự hợp lý” và “lượt nói có giá trị” hiện chưa có mô tả quan sát cụ thể.

Cần bổ sung một tài liệu ngắn kiểu:

```text
shared/learning_resources/agent_context/hnmu_raw_dialogue_pedagogy_audit_guide.md
```

Nội dung nên gồm:

- hội thoại tối thiểu có những bước nào;
- lượt AI có giá trị là gì;
- lượt HS có giá trị là gì;
- ví dụ đạt/chưa đạt;
- trường hợp cần HNMU xác nhận.

### 4.2. Ưu tiên cao

#### `RAW-PED-05` — Phù hợp lứa tuổi

Vấn đề: agent không nên tự quyết định sâu về mức phù hợp lứa tuổi nếu không có style guide.

Cần bổ sung:

- hướng dẫn ngôn ngữ phù hợp học sinh THCS;
- ví dụ ngôn ngữ quá khó/quá trẻ con/không phù hợp;
- quy tắc: agent chỉ đánh `fail` khi có lỗi rõ, còn lại `uncertain` để HNMU xem.

#### `RAW-DUP-04` — Khuôn AI lặp lại

Vấn đề: muốn chấm tiêu chí này cần nhìn nhiều mẫu trong batch, không thể chỉ đọc một mẫu đơn lẻ.

Cần bổ sung:

- thống kê cụm câu/khuôn hội thoại lặp lại bằng code;
- danh sách pattern ứng viên để agent kiểm;
- quy tắc không nhầm lẫn giữa “cấu trúc dàn giáo hợp lý” và “khuôn AI máy móc”.

### 4.3. Ưu tiên trung bình

#### `RAW-STR-04` — Hội thoại đủ dài để kiểm

Cần ghi rõ ngưỡng vận hành. Hiện code có kiểm hội thoại dưới một ngưỡng ký tự, nhưng checklist chưa nói rõ. Nếu không ghi, agent có thể dùng ngưỡng khác.

#### `RAW-CON-03` và `RAW-PED-06`

Hai tiêu chí này có phần giao nhau. Cần định nghĩa:

- `RAW-CON-03`: hội thoại có giải quyết đúng nội dung câu hỏi không.
- `RAW-PED-06`: gia sư có né nhiệm vụ, thay bằng lời khuyên chung chung/lạc hướng không.

## 5. Đề xuất cập nhật hệ thống tài liệu về dài hạn

Về dài hạn, có thể thêm một lớp tài liệu kiểu **criteria evidence map** — bản đồ căn cứ cho từng tiêu chí. Tuy nhiên, theo phản hồi hiện tại của Quân, **chưa tạo thêm file mới ở bước này** để tránh làm repo loạn hơn. Các nội dung dưới đây chỉ là hướng thiết kế nếu sau này cần tách thành artifact riêng.

File có thể cân nhắc sau này:

```text
experiments/20260709_155523/reports/raw-dialogue-audit-criteria-evidence-map-v0.csv
```

Cột nên có:

```text
criterion_id
criterion_name
evidence_basis_status
primary_basis_files
primary_tools
human_review_owner
default_result_when_basis_missing
notes
```

Trong đó `evidence_basis_status` có thể dùng:

- `ready`: đủ căn cứ để agent chấm;
- `partial`: có căn cứ nhưng thiếu quy tắc/threshold/ví dụ;
- `missing`: chưa đủ căn cứ, không nên pass tự tin;
- `human_only_when_uncertain`: agent chỉ hỗ trợ phát hiện rủi ro, HNMU/UET quyết định.

## 6. Quy tắc có thể thêm vào skill `hnmu-dialogue-auditor` sau khi được duyệt

Khi đã chốt việc sửa skill vận hành, có thể bổ sung nguyên tắc sau:

> Agent không được chấm `pass` tự tin cho một tiêu chí nếu tiêu chí đó chưa có nguồn căn cứ được chỉ định trong criteria evidence map. Khi căn cứ thiếu hoặc không truy xuất được, agent phải ghi `uncertain`, nêu rõ `criteria_basis_missing` hoặc `evidence_unavailable`, và đề xuất HNMU/UET xem lại.

Quy tắc này giúp tránh việc mỗi shard tự diễn giải khác nhau.

## 7. Ảnh hưởng tới kết quả đã chạy

Không nhất thiết phải bỏ toàn bộ kết quả Plan 04 hiện tại. Tuy nhiên, các kết quả ở những tiêu chí sau nên được xem là **chưa ổn định** cho đến khi bổ sung căn cứ và chạy repair:

- `RAW-CON-05`
- `RAW-PED-02`
- `RAW-PED-03`
- `RAW-PED-04`
- `RAW-PED-05`
- `RAW-DUP-04`

Các tiêu chí liên quan trực tiếp tới SGK/SGV, registry và code vẫn có giá trị tốt hơn:

- `RAW-STR-02`
- `RAW-STR-03`
- `RAW-CON-01`
- `RAW-CON-02`
- `RAW-CON-04`
- `RAW-CON-06`
- `RAW-CON-07`
- `RAW-DUP-03` nếu có cụm ứng viên từ code.

## 8. Khuyến nghị bước tiếp theo

Trong lượt ghi nhận phản hồi này, không sửa checklist/registry/skill và không tạo thêm file mới. Nếu sau này chốt triển khai repair chính thức trên dữ liệu lớp 6–9, nên làm tuần tự:

1. Chốt lại ngay trong report/họp nội bộ cách xử lý `RAW-CON-05`, `RAW-PED-02`, `RAW-PED-03`, `RAW-PED-04`, `RAW-PED-06`.
2. Khi đã được duyệt, mới cập nhật các file vận hành như `raw-dialogue-audit-criteria-v0.csv`, `raw-dialogue-quality-checklist-v0.md`, `shared/learning_resources/agent_context/README.md`, và skill `hnmu-dialogue-auditor`.
3. Nếu cần artifact riêng, khi đó mới cân nhắc tạo bản đồ căn cứ hoặc tài liệu canonical mới.
4. Chạy repair trước cho các tiêu chí thiếu căn cứ, không cần chạy lại toàn bộ 18 tiêu chí ngay.

Nếu cần giảm công việc trước mắt, nên ưu tiên repair `RAW-CON-05` trước, vì đây là tiêu chí đã phát hiện bằng chứng bất ổn rõ nhất trong kết quả hiện tại.

## 9. Bổ sung sau khi soi workspace và skill của `hnmu-dialogue-auditor`

Sau phản hồi của Quân, mình rà lại không chỉ checklist/registry mà cả workspace trực tiếp của agent `hnmu-dialogue-auditor`. Kết luận cần chỉnh lại cho công bằng hơn:

- Agent **không hoàn toàn thiếu căn cứ**. Skill và workspace hiện đã cung cấp một số nguồn nền quan trọng, đặc biệt là SGK/SGV fragment, SQLite truy xuất học liệu, checklist dữ liệu thô, registry 18 tiêu chí và tài liệu dàn giáo HNMU.
- Tuy nhiên, phần lớn căn cứ đang nằm ở mức **nhóm tiêu chí** hoặc **nguyên tắc chung**, chưa có một bản đồ bắt buộc kiểu “tiêu chí này phải dùng nguồn nào, công cụ nào, nếu thiếu nguồn thì xử lý ra sao”.
- Vì vậy, vấn đề chính không phải là “agent không có gì để dựa vào”, mà là **căn cứ chưa được ràng buộc đủ chặt theo từng tiêu chí**. Điều này giải thích vì sao các shard có thể chấm khác nhau hoặc quá tự tin ở một số tiêu chí.

### 9.1. Các file trong workspace agent đã rà

| File/thư mục | Vai trò hiện tại | Nhận xét |
|---|---|---|
| `agents/hnmu-dialogue-auditor/SKILL.md` | Chỉ dẫn chính cho agent khi kiểm dữ liệu thô HNMU. | Có yêu cầu dùng checklist, registry tiêu chí, SGK/SGV retrieval, tài liệu dàn giáo và rule tổng hợp strict. Đây là nguồn điều phối tốt, nhưng chưa có bản đồ căn cứ riêng cho từng tiêu chí. |
| `agents/hnmu-dialogue-auditor/references/raw-dialogue-audit-workflow.md` | Quy trình kiểm từng shard/mẫu. | Có hướng dẫn rõ về truy xuất SGK/SGV, kiểm độc lập từng tiêu chí, dùng tài liệu dàn giáo, hạ confidence khi evidence yếu. Tuy nhiên vẫn chưa định nghĩa chi tiết threshold cho các tiêu chí sư phạm khó. |
| `agents/hnmu-dialogue-auditor/references/raw-dialogue-audit-output-schema.md` | Schema output cho `raw_dialogue_checklist_results.csv` và file tổng hợp. | Đã nói `raw_dialogue_checklist_results.csv` là nguồn sự thật và quy định cách tổng hợp sample-level. Nhưng schema cho phép `evidence_fragment_id` trống khi tiêu chí không cần học liệu, nên không bắt buộc được căn cứ phi học liệu. |
| `agents/hnmu-dialogue-auditor/scripts/validate_raw_dialogue_audit_output.py` | Kiểm schema, nhãn kết quả, confidence và đủ 18 tiêu chí/mẫu. | Validator hiện kiểm rất tốt về hình thức và coverage tiêu chí, nhưng không kiểm được “tiêu chí này đã dùng đúng nguồn căn cứ chưa”. |
| `.codex/agents/hnmu-dialogue-auditor.toml` | Adapter runtime mỏng cho Codex specialist. | Có nhắc dùng checklist, SGK/SGV evidence và hướng dẫn dàn giáo; không chứa logic chi tiết. |
| `agents/hnmu-dialogue-auditor/agents/openai.yaml` | Metadata hiển thị/khởi tạo agent. | Chỉ là adapter mỏng, không có nội dung đánh giá. |
| `tests/agents/test_hnmu_dialogue_auditor.py` | Test scaffold của agent. | Kiểm skill có trỏ tới các file ngữ cảnh quan trọng, nhưng chưa kiểm tiêu chí nào phải có căn cứ nào. |
| `shared/learning_resources/agent_context/README.md` | Hub ngữ cảnh cho agent. | Có chỉ đúng nơi lấy dữ liệu thô, fragment, SQLite, checklist, registry, tài liệu dàn giáo và hàm truy xuất. Đây là nguồn rất quan trọng cho các tiêu chí học liệu và dàn giáo. |
| `shared/learning_resources/agent_context/hnmu_scaffolding_method_canonical.md` | Bản Markdown chuẩn hóa phương pháp dàn giáo từ tài liệu HNMU. | Có căn cứ trực tiếp cho `RAW-PED-01`, và hỗ trợ một phần cho `RAW-PED-02`, `RAW-PED-03`, `RAW-PED-04`. Nhưng chưa đủ để chấm thật chặt các tiêu chí như “lộ đáp án quá sớm” hoặc “lượt nói có giá trị”. |

### 9.2. Điều chỉnh đánh giá sau khi soi workspace agent

| Nhóm tiêu chí | Đánh giá sau khi soi workspace agent | Ý nghĩa |
|---|---|---|
| Tiêu chí học liệu và metadata: `RAW-CON-01`, `RAW-CON-02`, `RAW-CON-04`, `RAW-CON-06`, `RAW-CON-07` | Căn cứ khá tốt. Agent đã được yêu cầu dùng SGK/SGV fragment, registry và SQLite truy xuất. | Có thể giữ là nhóm tương đối ổn, miễn là output phải ghi rõ evidence hoặc lý do không tìm được evidence. |
| Tiêu chí cấu trúc: `RAW-STR-02`, `RAW-STR-03`, `RAW-STR-04` | Có căn cứ từ raw row và code. | `RAW-STR-04` vẫn nên viết rõ ngưỡng tối thiểu để tránh mỗi agent tự hiểu khác nhau. |
| Dàn giáo tổng quát: `RAW-PED-01` | Có căn cứ tốt từ `hnmu_scaffolding_method_canonical.md`. | Tiêu chí này ổn hơn nhận định ban đầu, vì agent đã có tài liệu HNMU chuẩn hóa để dựa vào. |
| Không lộ đáp án quá sớm và trình tự hội thoại: `RAW-PED-02`, `RAW-PED-03` | Có căn cứ gián tiếp từ tài liệu dàn giáo, nhưng chưa đủ quy tắc vận hành. | Không nên gọi là “thiếu căn cứ hoàn toàn”; chính xác hơn là “có căn cứ nền nhưng thiếu tiêu chí quan sát/threshold cụ thể”. |
| Lượt nói có giá trị: `RAW-PED-04` | Có thể dựa vào hội thoại và tinh thần dàn giáo, nhưng chưa có hướng dẫn nhận diện lượt thừa/lượt máy móc. | Cần bổ sung ví dụ đạt/chưa đạt, nếu không agent dễ chấm theo cảm giác. |
| Phù hợp lứa tuổi: `RAW-PED-05` | Chưa thấy nguồn chuẩn riêng trong workspace agent. | Nên có hướng dẫn ngôn ngữ phù hợp học sinh THCS; khi chưa có, agent chỉ nên gắn cờ khi rủi ro rõ hoặc đưa HNMU xác nhận. |
| Mức nhận thức hợp lý: `RAW-CON-05` | Workspace hiện chưa trỏ tới tài liệu HNMU về mức nhận thức. | Đây vẫn là lỗ hổng rõ nhất. Cần thêm bản Markdown chuẩn hóa từ file `Biểu hiện mức độ nhận thức _Tin học.docx`. |
| Khuôn AI lặp lại: `RAW-DUP-04` | Skill có nhắc batch context, nhưng chưa có tool/báo cáo pattern đủ rõ. | Cần code thống kê pattern hoặc danh sách cụm nghi vấn để agent kiểm, tránh đọc thủ công cả batch. |

### 9.3. Kết luận cập nhật

So với phần rà ban đầu, cần sửa sắc thái như sau:

- Với `RAW-PED-01`, căn cứ đã đủ tốt hơn mình ghi ban đầu vì workspace agent có bản Markdown chuẩn hóa phương pháp dàn giáo HNMU.
- Với `RAW-PED-02` và `RAW-PED-03`, không nên nói là “thiếu căn cứ” theo nghĩa tuyệt đối. Đúng hơn là **có căn cứ nền từ phương pháp dàn giáo, nhưng thiếu quy tắc quan sát cụ thể để chấm ổn định**.
- Với `RAW-PED-04`, `RAW-PED-05`, `RAW-DUP-04`, rủi ro vẫn lớn vì căn cứ hiện tại chưa đủ cụ thể hoặc chưa có công cụ hỗ trợ.
- Với `RAW-CON-05`, kết luận vẫn giữ nguyên: chưa có căn cứ chuẩn trong workspace agent, dù tài liệu gốc đã tồn tại ở thư mục `document/teacher_training_curriculum/benchmark_building_documents/`.

Do đó, bước tiếp theo nên không phải chỉ “thêm nguồn mới”, mà là tạo một lớp ràng buộc rõ ràng:

```text
tiêu chí → căn cứ bắt buộc → công cụ/file cần dùng → cách xử lý khi thiếu căn cứ
```

Về dài hạn, lớp này có thể được tách thành `raw-dialogue-audit-criteria-evidence-map-v0.csv` hoặc một tài liệu tương đương. Ở thời điểm hiện tại, theo phản hồi của Quân, chỉ ghi nhận trong report này và chưa tạo artifact riêng.

## 10. Ghi nhận phản hồi của Quân về các tiêu chí cần xử lý

Ghi chú vận hành: phần này chỉ ghi nhận hướng xử lý trong report. Trong lượt này, không sửa trực tiếp checklist, registry hay skill vận hành cho đến khi chốt rõ thứ tự cập nhật và phạm vi repair.

### 10.1. `RAW-CON-05` — Mức nhận thức hợp lý

Quân đồng ý cần sửa tiêu chí này.

Hướng xử lý nên giữ:

- Trỏ tiêu chí này về tài liệu gốc HNMU: `document/teacher_training_curriculum/benchmark_building_documents/Biểu hiện mức độ nhận thức _Tin học.docx`.
- Khi chấm, agent không được chỉ nhìn một động từ đơn lẻ. Cần xét đồng thời:
  - động từ trong câu hỏi;
  - đối tượng của hành động;
  - mức độc lập mà học sinh cần thực hiện.
- Nên chuẩn hóa cách gọi mức nhận thức về ba mức HNMU đang dùng: `Biết`, `Hiểu`, `Vận dụng`. Nếu dữ liệu thô ghi `Nhận biết` hoặc `Thông hiểu`, cần quy ước ánh xạ rõ.

### 10.2. `RAW-PED-02` — Không lộ đáp án quá sớm

Quân đồng ý triển khai làm rõ tiêu chí này.

Hướng xử lý nên giữ:

- Tiêu chí này không chấm “có nêu đáp án hay không” một cách máy móc.
- Trọng tâm là **thời điểm** và **cách** gia sư đưa đáp án.
- Có thể coi là rủi ro nếu gia sư đưa ngay đáp án cuối, công thức hoặc chương trình hoàn chỉnh khi chưa có chẩn đoán, gợi mở hoặc phản hồi theo bước.
- Không nên coi là lỗi nếu học sinh đã được gợi mở đủ, đã tự làm gần xong, hoặc đang cần gia sư xác nhận/chốt lại.

### 10.3. `RAW-PED-03` — Trình tự hội thoại hợp lý

Quân lưu ý tiêu chí này dễ chồng chéo với `RAW-PED-01`, vì cả hai đều dựa trên phương pháp dàn giáo.

Điểm cần chốt trước khi sửa checklist:

- `RAW-PED-01` nên chỉ kiểm **có dấu hiệu dàn giáo hay không**.
- `RAW-PED-03`, nếu giữ riêng, phải kiểm **trình tự diễn tiến** của hội thoại: các lượt có phản hồi đúng theo câu trả lời trước đó của học sinh không, có nhảy cóc không, có kết luận không ăn khớp với diễn biến trước đó không.
- Nếu không mô tả ranh giới này đủ rõ, `RAW-PED-03` có nguy cơ trở thành một bản lặp của `RAW-PED-01`.

Vì vậy, trước khi triển khai repair cho `RAW-PED-03`, nên quyết định một trong hai hướng:

1. Giữ `RAW-PED-03` nhưng viết rõ nó là tiêu chí về **mạch hội thoại qua nhiều lượt**.
2. Gộp/giảm trọng số `RAW-PED-03` nếu thấy nó không tạo thêm thông tin đáng kể so với `RAW-PED-01`.

### 10.4. `RAW-PED-04` và `RAW-PED-06`

Quân yêu cầu làm rõ ranh giới giữa “khen chung chung” và “lạc hướng/không liên quan”.

Hướng phân biệt nên giữ:

- `RAW-PED-04` kiểm **lượt nói ít giá trị nhưng vẫn nằm trong cùng mạch học tập**. Ví dụ:
  - khen chung chung kiểu “Tốt lắm, cố gắng lên” nhưng không chỉ ra học sinh đúng ở đâu;
  - lặp lại ý trước đó mà không thêm gợi ý, phản hồi, sửa sai hoặc bước tiếp theo;
  - lượt AI/HS không làm rõ thêm vấn đề, nhưng cũng chưa kéo hội thoại sang chủ đề khác.
- `RAW-PED-06` kiểm **lạc hướng hoặc né nhiệm vụ**. Ví dụ:
  - học sinh hỏi về bài cụ thể nhưng gia sư chuyển sang lời khuyên học tập chung;
  - gia sư trả lời sang chủ đề ngoài bài học;
  - gia sư không hỗ trợ vấn đề học sinh nêu mà thay bằng nội dung không liên quan.

Nói ngắn gọn:

- `RAW-PED-04`: vẫn đúng hướng, nhưng lượt nói nghèo giá trị.
- `RAW-PED-06`: sai hướng hoặc né yêu cầu chính.
