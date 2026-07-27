# Báo cáo pilot hai specialist — Workstream C0b

Ngày chạy: 27/07/2026  
Trạng thái: **không đạt Cổng C0b; đã điều tra nguyên nhân và chờ UET duyệt bản sửa phương pháp**

## Kết quả chính

Hai instance `pedagogical-principle-annotator` dùng cùng model `gpt-5.4-mini`, reasoning `medium`, cùng 40 candidate, cùng input/hash và hai vùng ghi độc lập. Sau khi cả hai bundle qua validator, phép so sánh xác định cho kết quả:

| Chỉ số | Kết quả | Ngưỡng | Kết luận |
|---|---:|---:|---|
| Trùng nguyên tắc chính | 0,55 | 1,00 | Không đạt |
| Trùng cặp chính–phụ | 0,55 | 0,90 | Không đạt |
| Jaccard trung bình | 0,55 | 0,90 | Không đạt |
| Trùng khoảng trống độ phủ | 1,00 | 1,00 | Đạt |
| Trùng tác động reference | 0,70 | 0,90 | Không đạt |

Có 18/40 bất đồng về nguyên tắc chính. Cụm lớn nhất là A chọn `Feedback` còn B chọn `Explanation` ở 8 mẫu; tiếp theo là `Modelling`–`Practice` ở 3 mẫu. Hai agent đều không ghi coverage gap hoặc context–gold conflict.

## Sự cố validator và cách xử lý

Bundle B ban đầu có một dòng đổi nhãn nhưng ghi `reference_effect=unchanged`. Validator đã phát hiện đúng lỗi. Việc trả bundle cho specialist B để sửa là thừa đối với phần khác biệt có thể tính xác định: code có thể so sánh nhãn và quyết định khoảng trống trước–sau để suy ra `changed` hoặc `unchanged`. Agent chỉ còn cần chịu trách nhiệm về nhận định ngữ nghĩa `conflict` và lý do của nó.

Pipeline hiện đã có `reconcile_principle_annotation_draft.py` để thực hiện phép đối chiếu này, tự bổ sung hàng đợi bắt buộc, rồi mới cho phép tạo manifest/handoff. Hàm so sánh tiếp tục tự validate cả hai bundle và đóng khi lỗi trước khi ghi metric. Bundle B đã sửa qua validator với 14 thay đổi; A qua validator với 18 thay đổi. Phép so sánh trước sửa không được coi là kết quả.

## Điều tra lại nguồn gốc sáu nguyên tắc

Sách *Making Every Lesson Count* mô tả sáu nguyên tắc có quan hệ qua lại, được kết nối linh hoạt và không tạo thành một chu trình cố định. KMP-Bench gán một hoặc hai nguyên tắc cho hành động gia sư trong lúc thiết kế dữ liệu, nhưng không công bố quy tắc xếp thứ tự chính–phụ cho việc gán nhãn hậu nghiệm.

Vì vậy, pilot đầu tiên đã đặt gánh nặng quá lớn lên việc chọn đúng một nhãn chính. Bản sửa phương pháp xem nhãn là tập gồm một hoặc hai chức năng sư phạm không thể bỏ:

| Nguyên tắc | Ranh giới theo chức năng gần |
|---|---|
| `Challenge` | Duy trì nỗ lực có ích hoặc nâng yêu cầu nhận thức vượt mức thực hiện hiện tại. |
| `Explanation` | Làm cho khái niệm, quan hệ, cách thức hoặc lý do trở nên rõ ràng. |
| `Modelling` | Cho học sinh thấy cách áp dụng kiến thức qua quy trình, dòng suy nghĩ, quyết định hoặc mẫu. |
| `Practice` | Yêu cầu học sinh thực hiện/lặp lại việc áp dụng để tăng ghi nhớ, thành thạo hoặc độc lập. |
| `Feedback` | Dùng chính bài làm hoặc suy luận đã quan sát của học sinh làm đối tượng nhận xét để dẫn hướng cải thiện. |
| `Questioning` | Cần câu trả lời của học sinh để chẩn đoán hiểu biết, giữ mạch suy luận hoặc thúc đẩy suy nghĩ sâu. |

Nếu vòng 1 và reference gợi ra hai nguyên tắc khác nhau, chỉ giữ cả hai khi chúng có hai chức năng độc lập, đều tương thích với context và bỏ một chức năng sẽ làm phản hồi không còn đầy đủ. Không dùng nhãn phụ chỉ để che bất định hoặc hòa giải hai agent.

## Packet UET

`outputs/benchmark_specification/teacher_review_packets/workstream_c_c0b/dual_run_uet_review.csv` gồm:

- 21 mẫu có bất đồng nhãn hoặc tác động reference;
- 8 mẫu đồng thuận được chọn xác định để kiểm tra;
- tổng 29 dòng, không yêu cầu UET gán mù.

## Giới hạn

Lô 40 hiện tại đều thuộc lớp 6 vì được lấy bằng offset đầu từ tập 160 đang sắp theo lớp. Pilot đo được sự thiếu tái lập trên lô này nhưng chưa đại diện cho lớp 7–9. Trước lần C0b tiếp theo nên tạo lô 40 phân tầng 10 mẫu mỗi lớp.

Năm tài liệu canonical có tổng khoảng 43.853 ký tự. Runtime sửa đổi chỉ yêu cầu specialist đọc đầy đủ ba bảng CSV nhỏ: registry nguyên tắc, bảng năng lực và ma trận chồng lấn năng lực. Hai file Markdown dài vẫn được khóa hash để truy vết, nhưng chỉ mở khi hợp đồng ngắn và ba bảng chưa giải quyết được một ranh giới cụ thể. Manifest phiên bản 2 khóa thêm hash của skill và hợp đồng runtime để hai agent luôn dùng cùng bản tóm tắt.

## Trạng thái chuyển tiếp

Không mở Workstream C1 hoặc Workstream D. Packet 29 dòng được giữ làm bằng chứng chẩn đoán, nhưng UET chưa cần phân xử từng dòng. Quyết định tiếp theo là duyệt hoặc sửa bản ranh giới, quy tắc đa nhãn và yêu cầu lấy mẫu 10 ứng viên mỗi lớp; sau đó mới tạo manifest mới và chạy lại C0a/C0b.
