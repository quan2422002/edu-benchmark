# Căn cứ nghiên cứu của mô hình năng lực gia sư

Tài liệu này giải thích nguồn gốc các mã nghiên cứu và cách từng nguồn được dùng trong mô hình năng lực. Đây là bản nháp phục vụ HNMU/UET rà soát, chưa phải bằng chứng rằng sáu năng lực đã được xác nhận.

## 1. Hai nhóm mã nghiên cứu

### `TR-P001`–`TR-P003`: nghiên cứu về benchmark gia sư AI

Ba mã này đến từ đợt rà soát trước Plan 03, kế thừa các tóm tắt bài báo của thử nghiệm `20260705_215045`:

- `TR-P001`: MathTutorBench;
- `TR-P002`: KMP-Bench;
- `TR-P003`: TutorBench.

Đây là các nguồn trực tiếp nhất để nhận diện những hành vi gia sư đã từng được đưa vào nhiệm vụ hoặc tiêu chí đánh giá. Tuy nhiên, chúng thuộc miền dữ liệu khác và không tự động xác nhận hệ thống năng lực cho Tin học THCS Việt Nam.

### `MTF-S001`–`MTF-S002`: nền tảng phương pháp đo lường

Hai mã này đến từ Workstream A của Plan 03:

- `MTF-S001`: thiết kế lấy bằng chứng làm trung tâm, dùng để tổ chức chuỗi **năng lực cần đo → nhiệm vụ → bằng chứng quan sát**;
- `MTF-S002`: lý thuyết hiệu lực đo lường, dùng để yêu cầu nhiều nhóm bằng chứng thay vì coi một vòng hỏi ý kiến chuyên gia là đủ.

Hai nguồn này chỉ hỗ trợ cấu trúc và cách kiểm định **toàn bộ mô hình**. Chúng không được ghi như bằng chứng trực tiếp cho bất kỳ năng lực riêng lẻ nào.

### `MTF-S013`: nền tảng sư phạm về dàn giáo thích ứng

`MTF-S013` là bài tổng quan của Van de Pol và cộng sự (2010), *Scaffolding in Teacher–Student Interaction: A Decade of Research*. Bài báo phân biệt **phương tiện hỗ trợ** như hỏi, giải thích, làm mẫu, phản hồi, hướng dẫn và gợi ý với các đặc trưng khiến hỗ trợ trở thành dàn giáo thích ứng: điều chỉnh theo năng lực hiện tại, rút dần hỗ trợ và chuyển giao trách nhiệm. Vì vậy, bài báo là căn cứ trực tiếp để giữ ranh giới giữa `CAP-STRAT` (chọn phương tiện/chức năng) và `CAP-SCAFF` (điều tiết mức độ, thời điểm và chuyển giao), đồng thời hỗ trợ từng phần cho quan hệ giữa `CAP-STATE`, `CAP-DIAG` và hỗ trợ thích ứng. Bài báo không tự xác nhận ngưỡng chấm cho Tin học THCS Việt Nam; chi tiết được truy trong `research_source_registry.csv`, `research_support_matrix.csv` và `evidence_matrix.csv`.

### Phương pháp HNMU: căn cứ địa phương, không phải `research_id`

Hai tài liệu HNMU được truy trực tiếp bằng đường dẫn chuẩn:

- `shared/learning_resources/agent_context/hnmu_scaffolding_method_canonical.md`: hỗ trợ `CAP-STATE`, `CAP-DIAG`, `CAP-STRAT`, `CAP-SCAFF`, phần bảo toàn quyền chủ động và phần giao tiếp không gây thất vọng của `CAP-CARE`;
- `shared/learning_resources/agent_context/hnmu_cognitive_level_method_canonical.md`: hỗ trợ xác định yêu cầu nhận thức và độ vừa sức theo tình huống, nhưng không trực tiếp chứng minh một năng lực gia sư riêng.

Các tài liệu này là nguồn phương pháp địa phương do HNMU cung cấp, vì vậy không được giả làm paper hoặc cấp mã `MTF-*`. Đường dẫn và phần hỗ trợ được ghi trong `tutor_capabilities.csv` và `capability_research_provenance.csv`; quyết định sư phạm cuối vẫn thuộc HNMU.

## 2. Cách truy vết

Mỗi mã nghiên cứu được truy theo ba lớp:

1. `research_source_registry.csv`: bài báo nào, mã đến từ đợt rà soát nào, vị trí bằng chứng và vai trò trong dự án;
2. `research_support_matrix.csv`: bài báo hỗ trợ khía cạnh nào của từng năng lực, dự án sử dụng bằng chứng đó ra sao và giới hạn suy luận là gì;
3. `capability_research_provenance.csv`: tổng hợp ở cấp năng lực, kèm học liệu Tin học THCS và trạng thái cần chuyên gia xác nhận.

Trong `research_support_matrix.csv`:

- `claim_status=evidence` nghĩa là nội dung mô tả được bài báo hỗ trợ trực tiếp;
- `claim_status=inference` nghĩa là dự án đang suy luận từ kết quả bài báo sang mô hình địa phương;
- `support_level` cho biết mức hỗ trợ là trực tiếp mạnh, trực tiếp từng phần, gián tiếp, hỗ trợ cấu trúc hay hỗ trợ hiệu lực.

## 3. Kết luận hiện tại theo từng năng lực

| Năng lực | Kết luận từ nghiên cứu | Phần chưa được nghiên cứu xác nhận |
|---|---|---|
| `CAP-ACC` | Cả ba benchmark đều quan sát tính đúng đắn hoặc chất lượng chuyên môn. | Ngưỡng đúng và cổng lỗi nghiêm trọng cho Tin học THCS. |
| `CAP-STATE` | Cả ba benchmark đặt phản hồi trong trạng thái, câu hỏi hoặc bài làm của học sinh; `MTF-S013` yêu cầu xác định năng lực hiện tại trước hỗ trợ thích ứng. | Có phân biệt ổn định mô tả trạng thái hiện tại với giải thích nguyên nhân lỗi hay không. |
| `CAP-STRAT` | Các bài báo yêu cầu những hành vi sư phạm khác nhau theo nguyên tắc hoặc bối cảnh; `MTF-S013` gọi đây là các phương tiện hỗ trợ. | Hệ thống phương tiện/chức năng phù hợp dữ liệu HNMU và có tách được khỏi mức hỗ trợ hay không. |
| `CAP-SCAFF` | Có tiền lệ rõ cho gợi ý, dàn giáo, tự sửa và không làm thay; `MTF-S013` bổ sung tính thích ứng, rút dần và chuyển giao trách nhiệm. | Ngưỡng hỗ trợ vừa đủ theo từng nhóm nhiệm vụ; một lượt chỉ quan sát được điều tiết cục bộ. |
| `CAP-DIAG` | Có tiền lệ cho phát hiện, định vị và sửa lỗi hoặc hiểu lầm; `MTF-S013` xem chẩn đoán là công cụ để đạt tính thích ứng. | Có phân biệt ổn định giải thích nguyên nhân với mô tả trạng thái, và chẩn đoán chỉ áp dụng khi có bằng chứng lỗi hay không. |
| `CAP-CARE` | Chỉ có hỗ trợ từng phần hoặc gián tiếp về sự rõ ràng, giọng điệu, tránh quá tải và phù hợp người học. | Toàn bộ cấu trúc giao tiếp–động lực–lứa tuổi cần HNMU kiểm định; đây là dòng có căn cứ trực tiếp yếu nhất. |

## 4. Giới hạn sử dụng trong bài báo của dự án

Bài báo của dự án có thể viết rằng sáu miền năng lực được **hình thành bằng tổng hợp có truy vết từ tiền lệ benchmark, khung đo lường và phương pháp HNMU**, sau đó được đưa ra chuyên gia rà soát. Không được viết rằng ba benchmark trước đã “xác nhận” sáu năng lực này.

### Disposition của miền quyền chủ động và `CAP-DIAG`

- `CAP-DIAG` được bổ sung vì cả nguồn benchmark lẫn phương pháp dàn giáo HNMU đều mô tả hành vi phát hiện, định vị hoặc giải thích lỗi trước khi hỗ trợ.
- “Thúc đẩy tư duy và quyền chủ động” được giữ như kết quả xuyên suốt của lựa chọn chiến lược và điều tiết hỗ trợ. Mô hình chỉ quan sát việc phản hồi **bảo toàn cơ hội để học sinh tự làm**, không suy ra mức chủ động thực tế của học sinh.
- Workstream C–D phải kiểm tra xem hành vi bảo toàn quyền chủ động cần một task/tiêu chí riêng hay đủ để nằm trong `CAP-STRAT` và `CAP-SCAFF`. HNMU sẽ review disposition này cùng task, rubric và ví dụ cụ thể.

### Ranh giới giữa các năng lực gần nhau

- `CAP-STATE` là mô tả học sinh đang ở đâu, đã làm gì và cần gì; `CAP-DIAG` là giải thích vì sao có lỗi, hiểu lầm hoặc bế tắc. Hai năng lực có thể cùng xuất hiện nhưng không phải mọi mô tả trạng thái đều là chẩn đoán.
- `CAP-STRAT` là lựa chọn phương tiện/chức năng sư phạm; `CAP-SCAFF` là điều tiết phương tiện đó theo năng lực hiện tại, mức độ, thời điểm, rút dần hỗ trợ và chuyển giao trách nhiệm. Cùng một phương tiện có thể tạo dàn giáo tốt hoặc kém tùy cách điều tiết.
- Với mẫu một lượt, không suy diễn rút dần hoặc chuyển giao dài hạn nếu lịch sử không cung cấp bằng chứng. Hai cặp trên phải được kiểm định bằng bộ ví dụ đối chứng bốn ô trước khi cân nhắc gộp.

Để có luận giải khoa học hoàn chỉnh, các bước sau vẫn cần tạo thêm bằng chứng:

- HNMU đánh giá tính phù hợp, đầy đủ và rõ ràng của từng năng lực;
- kiểm mức nhất quán khi người chấm phân biệt các năng lực dễ chồng lấn;
- kiểm khả năng quan sát từng năng lực trên dữ liệu ứng viên;
- kiểm khả năng phân biệt phản hồi gia sư tốt, trung bình và kém ở giai đoạn thí điểm.
