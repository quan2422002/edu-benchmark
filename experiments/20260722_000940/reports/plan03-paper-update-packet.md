# Gói cập nhật nội dung bài báo — Plan 03 sau quyết định kiến trúc Workstream C

Ngày cập nhật: 27/07/2026  
Trạng thái: bản nháp phục vụ viết phương pháp; chưa có xác nhận HNMU hoặc kết quả hiệu lực.

## 1. Phát biểu hiện có thể viết

- Đối tượng đo là chất lượng phản hồi tiếp theo của gia sư AI trong một bối cảnh hội thoại Tin học THCS cố định.
- Benchmark dùng một nhiệm vụ chung: sinh phản hồi tiếp theo của gia sư.
- Sáu nguyên tắc `Challenge`, `Explanation`, `Modelling`, `Practice`, `Feedback`, `Questioning` bắt nguồn từ Allison và Tharby (2015), được KMP-Bench vận hành bằng cách gán một hoặc hai nguyên tắc cho hành động gia sư.
- Nguồn gốc mô tả sáu nguyên tắc có quan hệ qua lại, không phải sáu lớp loại trừ. Cấu trúc nhãn chính–phụ khi gán hậu nghiệm là quy ước của dự án, chưa phải kết quả được nguồn gốc chứng minh.
- Sáu năng lực Workstreams A–B cung cấp nền tảng cho các chiều chất lượng; chúng được phân biệt với nhãn nguyên tắc và không bị dùng làm hệ phân loại nhiệm vụ.
- Rubric dự kiến có hai tầng: chiều năng lực chung và tiêu chí theo nguyên tắc; không có tầng tiêu chí riêng theo từng mẫu.
- `gold_response` là phản hồi tham chiếu, không phải cách diễn đạt hợp lệ duy nhất.
- Đầu vào gồm 2.028 ứng viên từ 665 hội thoại gốc; census và mẫu khám phá 160 hội thoại đã được khóa.
- Nhánh tám nhiệm vụ ứng viên là một nhánh thiết kế đã bị thay thế và được giữ dưới `legacy` để truy vết.

## 2. Phát biểu chỉ được viết ở trạng thái giả thuyết

- Sáu nguyên tắc KMP có thể bao phủ phần lớn yêu cầu sư phạm trong dữ liệu Tin học THCS; điều này chưa được kiểm tra trên mẫu 160.
- Sáu năng lực có thể tạo một hệ rubric toàn diện và phân biệt được phản hồi tốt–trung bình–kém; chưa có pilot response để chứng minh.
- Van de Pol và cộng sự (2010, `MTF-S013`) hỗ trợ ranh giới phương tiện sư phạm–dàn giáo thích ứng; UET giữ riêng `STATE–DIAG` và `STRAT–SCAFF`, HNMU chưa xác nhận.
- `CAP-CARE` chỉ đo hành vi giao tiếp hỗ trợ học tập tức thời, không đo thay đổi động lực hoặc kết quả học tập.

## 2.1. Hạ tầng annotation đã triển khai; pilot A/B không đạt cổng tái lập

- Specialist riêng `pedagogical-principle-annotator` đã có skill canonical, adapter mỏng và hợp đồng hai lượt; agent thiết kế không đồng thời là coder chính.
- Runtime mới yêu cầu đọc đầy đủ ba bảng CSV ngắn và chỉ mở hai tài liệu Markdown dài khi còn ranh giới chưa giải quyết; manifest phiên bản 2 khóa cả năm tài liệu nguồn gốc, skill và hợp đồng runtime.
- View vòng 1 chỉ có context; view vòng 2 bổ sung `gold_response` và `gold_answer`, giữ cùng tập ID và thứ tự. Field-isolation và hash-drift đều có kiểm thử đóng khi lỗi.
- `reference_effect=changed/unchanged` được suy ra bằng code từ quyết định trước–sau; agent chỉ đưa ra nhận định ngữ nghĩa `conflict`.
- C0a đạt `5/5` ca biên sau khi hợp đồng được gia cố để reference không ghi đè nhu cầu sư phạm không thể bỏ của context.
- Hai instance A/B đã mã hóa độc lập cùng lô 40. Các chỉ số lần lượt là 0,55 cho nguyên tắc chính, 0,55 cho cặp chính–phụ, 0,55 cho Jaccard, 1,00 cho quyết định khoảng trống và 0,70 cho tác động reference. Chỉ ngưỡng khoảng trống đạt; C0b không đạt.
- Kết quả này có thể viết như bằng chứng pilot cho thấy codebook/skill hiện chưa đủ tái lập giữa hai instance AI; không được trình bày 40 nhãn như ground truth.
- Việc đọc lại Allison–Tharby và KMP-Bench dẫn tới giả thuyết sửa: mã hóa một tập một hoặc hai chức năng không thể bỏ, không dùng nhãn phụ để hấp thụ bất định; so sánh tập nhãn và độ ổn định thứ tự chính–phụ thành hai vấn đề riêng.

## 3. Phát biểu chưa được viết như kết quả

- Workstream C đã hoàn tất hoặc sáu nguyên tắc đã bao phủ đầy đủ dữ liệu;
- rubric hai tầng đã được HNMU xác nhận;
- chỉ số nhất quán, khả năng phân biệt hoặc hiệu lực đã đạt;
- hiệu năng mô hình hoặc đặc tả v1 đã được khóa.

## 4. Artifact hỗ trợ

- `outputs/benchmark_specification/task_discovery/benchmark_tasks.csv`;
- `outputs/benchmark_specification/task_discovery/pedagogical_principles.csv`;
- `outputs/benchmark_specification/task_discovery/task_discovery_codebook.md`;
- `outputs/benchmark_specification/construct_v1_draft/`;
- `outputs/benchmark_specification/task_discovery/principle_annotation_reference_manifest.json`;
- `reports/plan03-workstream-c-c0a-implementation-summary.md`;
- `literature_notes/plan03_measurement_foundations/`;
- `literature_notes/pre_plan03_task_rubric_review/paper_summaries/P03-P002-kmp-bench.md`.

## 5. Hình và bảng có thể chuẩn bị

- hình: nghiên cứu/HNMU → sáu năng lực + sáu nguyên tắc → rubric hai tầng → response pilot;
- bảng sáu năng lực, nguồn hỗ trợ và ranh giới;
- bảng sáu nguyên tắc, điều kiện áp dụng và dấu hiệu quan sát;
- sơ đồ một nhiệm vụ, nhãn nguyên tắc đa nhãn và gói HNMU tích hợp.

## 6. Giới hạn bắt buộc phải nêu

- Số nhãn nguyên tắc chính thức hiện là 0.
- Chỉ có AI và một đại diện UET; đối chiếu UET–AI không phải độ tin cậy giữa hai người chấm độc lập.
- Lô C0b đầu tiên gồm 40 mẫu lớp 6 do input 160 đang sắp theo lớp; chưa đại diện cho lớp 7–9.
- Sáu nguyên tắc và sáu năng lực chưa được HNMU xác nhận.
- Nguồn quốc tế không tự chứng minh khả năng chuyển sang tiếng Việt và Tin học THCS.
- Nhánh tám nhiệm vụ legacy không được trình bày như taxonomy kết quả.
