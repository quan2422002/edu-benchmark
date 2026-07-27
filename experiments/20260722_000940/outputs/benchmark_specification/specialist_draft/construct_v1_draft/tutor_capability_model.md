# Mô hình năng lực gia sư — bản nháp v1

Trạng thái: `uet_provisional_approved_for_principle_coverage_and_rubric_design` — đại diện UET cho phép dùng bản này làm nền kiểm tra độ phủ nguyên tắc và xây rubric ngày 26/07/2026. Đây không phải xác nhận cuối của HNMU và không cho phép gọi sáu năng lực là đã kiểm định.

## 1. Nguồn xây dựng

Bản nháp được tổng hợp từ:

- nền tảng đo lường ở `literature_notes/plan03_measurement_foundations/`;
- ba benchmark gia sư AI ở `literature_notes/pre_plan03_task_rubric_review/`;
- phương pháp mức nhận thức HNMU tại `shared/learning_resources/agent_context/hnmu_cognitive_level_method_canonical.md`;
- phương pháp dàn giáo HNMU tại `shared/learning_resources/agent_context/hnmu_scaffolding_method_canonical.md`;
- hệ thống học liệu Tin học THCS lớp 6–9.

Nguồn gốc từng mã nghiên cứu và nội dung mỗi bài báo hỗ trợ được trình bày trong `capability_research_basis.md`, `research_source_registry.csv` và `research_support_matrix.csv`.

## 2. Mục tiêu thiết kế

Bản nháp giữ bốn miền ban đầu (`ACC`, `STATE`, `STRAT`, `SCAFF`) và `CARE`, đồng thời thay cách biểu diễn miền “thúc đẩy tư duy và quyền chủ động” và bổ sung `DIAG` như giải thích ở Mục 5. Chúng là kết quả tổng hợp thiết kế từ nghiên cứu và phương pháp HNMU, chưa phải sáu năng lực đã được HNMU xác nhận.

Mỗi năng lực phải để lại dấu hiệu có thể quan sát trong **một lượt phản hồi của gia sư**. Nếu chỉ có thể suy ra năng lực từ nhiều lượt hoặc từ thông tin không có trong mẫu, HNMU/UET cần quyết định loại bỏ, gộp hoặc thay đổi đơn vị đánh giá.

## 3. Sáu giả thuyết năng lực

| Mã | Năng lực | Vai trò dự kiến | Ranh giới còn mở |
|---|---|---|---|
| `CAP-ACC` | Độ chính xác chuyên môn và bám học liệu | Kiểm nội dung, nguồn và thao tác | Không thay thế nhận diện trạng thái, chiến lược hay dàn giáo |
| `CAP-STATE` | Nhận diện trạng thái, mục tiêu và ngữ cảnh học sinh | Đọc đúng học sinh cần gì và đang vướng ở đâu | Cặp cần kiểm định ranh giới với `CAP-DIAG` |
| `CAP-STRAT` | Chọn chiến lược sư phạm phù hợp | Chọn hỏi, giải thích, gợi mở, làm mẫu hay phản hồi | Cặp cần kiểm định ranh giới với `CAP-SCAFF` |
| `CAP-SCAFF` | Điều chỉnh mức hỗ trợ và nhịp dàn giáo | Chia nhỏ vừa đủ, không cho quá nhiều hoặc quá ít | Cặp cần kiểm định ranh giới với `CAP-STRAT` |
| `CAP-DIAG` | Chẩn đoán lỗi, hiểu lầm và kiến thức nền còn thiếu | Xác định nguyên nhân gốc, không chỉ biểu hiện | Cặp cần kiểm định ranh giới với `CAP-STATE` |
| `CAP-CARE` | Giao tiếp hỗ trợ học tập, tôn trọng và phù hợp lứa tuổi | Diễn đạt dễ hiểu, không phán xét, khích lệ gắn với nỗ lực | Chỉ quan sát hành vi giao tiếp tức thời; không suy ra động lực thực tế hoặc kết quả học tập |

## 4. Dấu hiệu quan sát trong một lượt phản hồi

- `CAP-ACC`: nội dung phù hợp học liệu đã truy vết và đáp án chuyên môn.
- `CAP-STATE`: phản hồi bám đúng tình trạng cùng mục tiêu của học sinh.
- `CAP-STRAT`: phản hồi thể hiện cách hỗ trợ phù hợp với tình huống.
- `CAP-SCAFF`: lượng và nhịp hỗ trợ vừa đủ để học sinh tiếp tục.
- `CAP-DIAG`: phản hồi chỉ ra nguyên nhân gốc hoặc kiến thức nền còn thiếu.
- `CAP-CARE`: cách diễn đạt dễ hiểu, tôn trọng, không gây quá tải và phù hợp lứa tuổi; chỉ đánh giá hành vi giao tiếp trong lượt hiện tại.

## 5. Disposition của sáu miền ban đầu

- `CAP-DIAG` được bổ sung như một năng lực riêng vì ba benchmark gia sư đều có hành vi phát hiện, định vị hoặc giải thích lỗi; phương pháp dàn giáo HNMU cũng đặt “tiếp nhận và chẩn đoán” trước việc điều chỉnh hỗ trợ. UET giữ năng lực này ở mức tạm thời để Workstream D kiểm tra khả năng quan sát và xây tiêu chí; `CAP-DIAG` không phải task hay nguyên tắc độc lập, mà có thể biểu hiện trong các mẫu `Questioning` hoặc `Feedback`.
- Miền “thúc đẩy tư duy và quyền chủ động” không bị loại. Ở phiên bản hiện tại, nó được xem là **kết quả sư phạm xuyên suốt** của `CAP-STRAT` và `CAP-SCAFF`: chọn cách hỗ trợ khiến học sinh phải tự suy nghĩ tiếp, chỉ đưa lượng trợ giúp vừa đủ và giữ phần việc còn lại cho học sinh. Workstream D có thể tạo tiêu chí nguyên tử về bảo toàn quyền chủ động khi nguyên tắc và bối cảnh ứng viên tạo cơ hội quan sát; HNMU sẽ quyết định trong gói review tích hợp liệu có cần tách thành một chiều năng lực riêng.
- Lý do chưa tách ngay một `CAP-AGENCY`: từ một phản hồi, có thể quan sát gia sư **bảo toàn cơ hội chủ động**, nhưng không thể kết luận học sinh thực sự tăng quyền chủ động, động lực hoặc năng lực tự học nếu chưa quan sát hành vi tiếp theo.

## 6. Các ranh giới đã được UET duyệt provisional

- Giữ tạm cả sáu năng lực làm nền cho Workstreams C–D. Đại diện UET đã duyệt tạm thời việc giữ riêng `CAP-STRAT`–`CAP-SCAFF` và `CAP-STATE`–`CAP-DIAG`; HNMU vẫn có quyền yêu cầu sửa trong gói review tích hợp nguyên tắc–năng lực–rubric–ví dụ.
- `CAP-STATE` mô tả học sinh đang ở đâu, đã làm gì và cần gì; `CAP-DIAG` giải thích vì sao có lỗi, hiểu lầm hoặc bế tắc. Chẩn đoán chỉ áp dụng khi đầu vào có bằng chứng phù hợp.
- `CAP-STRAT` đo phương tiện/chức năng được chọn (hỏi, giải thích, làm mẫu, gợi ý, phản hồi); `CAP-SCAFF` đo cách điều tiết phương tiện đó theo năng lực hiện tại, mức độ, thời điểm, rút dần hỗ trợ và chuyển giao trách nhiệm. Van de Pol et al. phân biệt rõ “phương tiện” với các đặc trưng khiến hỗ trợ trở thành dàn giáo thích ứng; dùng một phương tiện đơn lẻ chưa đủ chứng minh có dàn giáo (xem `MTF-S013`).
- Với ứng viên chỉ có một lượt phản hồi, chỉ nên khẳng định sự điều tiết tại thời điểm hiện tại. Rút dần hỗ trợ và chuyển giao trách nhiệm cần lịch sử hoặc chuỗi lượt; không suy diễn chúng từ một câu trả lời đơn lẻ.
- Chỉ xem xét gộp lại nếu codebook, ví dụ đối chứng hoặc review tích hợp của HNMU cho thấy người chấm không thể phân biệt.
- `CAP-CARE` chỉ đo chất lượng giao tiếp hỗ trợ học tập quan sát được trong lượt hiện tại. “Duy trì động lực” ở đây có nghĩa là không làm suy giảm động lực bằng cách hạ thấp, gây áp lực hoặc khen chung chung; không phải tuyên bố đo được trạng thái động lực thật của học sinh. Lỗi nguy hiểm hoặc vi phạm đạo đức, pháp lý nghiêm trọng thuộc cổng lỗi riêng ở Workstream D.

## 7. Ví dụ về khả năng quan sát trong một phản hồi

| Năng lực | Bối cảnh rút gọn | Dấu hiệu quan sát được trong đúng một phản hồi | Điều không được suy ra |
|---|---|---|---|
| `CAP-ACC` | Học sinh hỏi vì sao phải đổi GB sang MB | Gia sư giải thích đúng quan hệ đơn vị và phép tính cần làm | Học sinh đã hiểu hoặc sẽ làm đúng ở lượt sau |
| `CAP-STATE` | Học sinh nói đã thử chia `16/12` nhưng mắc ở đơn vị | Gia sư bám đúng việc học sinh đã chọn phép chia và đang vướng ở quy đổi | Nguyên nhân sâu xa của lỗi nếu đầu vào chưa đủ bằng chứng |
| `CAP-STRAT` | Học sinh còn có thể tự thực hiện bước tiếp theo | Gia sư chọn hỏi gợi mở thay vì đưa toàn bộ đáp án | Lượng hỗ trợ đã vừa đủ; phần này thuộc `CAP-SCAFF` |
| `CAP-SCAFF` | Học sinh đã nhớ cần đổi đơn vị nhưng quên hệ số | Gia sư chỉ nhắc xem lại bảng đơn vị hoặc cho một gợi ý, giữ phép tính cho học sinh | Có “rút dần hỗ trợ” qua thời gian nếu lịch sử chưa cho thấy sự thay đổi |
| `CAP-DIAG` | Học sinh chia trực tiếp `16/12` | Gia sư chỉ ra lỗi cốt lõi là hai đại lượng khác đơn vị, không chỉ nói kết quả sai | Mọi trạng thái học sinh đều có nguyên nhân chẩn đoán được |
| `CAP-CARE` | Học sinh trả lời sai vì quên số 0 khi chia dãy | Gia sư nói rõ phần học sinh đã làm đúng, chỉ lỗi bằng ngôn ngữ tôn trọng và đưa yêu cầu vừa sức | Học sinh thực sự có thêm động lực hoặc thay đổi cảm xúc |

Ví dụ `CAP-CARE` đạt: “Em đã chia đúng mỗi nửa có 8 số. Mình kiểm lại điểm cuối nhé: từ 0 đến 8 có 9 số, vậy nửa trái nên kết thúc ở số nào để vừa đủ 8 số?”

Ví dụ `CAP-CARE` trung bình: “Em làm gần đúng rồi, cố lên nhé. Em kiểm tra lại đi.” Câu này lịch sự nhưng lời khen chung chung và chưa giúp học sinh biết cần kiểm tra phần nào.

Ví dụ `CAP-CARE` kém: “Bài dễ thế mà em cũng đếm sai à?” Nội dung có thể chỉ đúng vị trí lỗi nhưng cách diễn đạt hạ thấp học sinh và có nguy cơ làm các em ngại tiếp tục.

## 8. Ràng buộc

- Không định nghĩa năng lực chỉ bằng những tính từ chung chung.
- Không coi năng lực nào là đã được HNMU xác nhận chỉ vì UET cho phép dùng provisional trong task discovery.
- Chỉ suy luận từ phản hồi gia sư và ngữ cảnh có trong mẫu, không suy ra mức tiến bộ học tập dài hạn.
- Tín hiệu an toàn nghiêm trọng phải được ghi cho cổng lỗi riêng, không dùng để khẳng định `CAP-CARE` đã đầy đủ.
