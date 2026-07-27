# Đặc tả v3 — Siết ranh giới tính cần thiết của sáu nguyên tắc sư phạm

Experiment: `20260727_170150`  
Phiên bản: `v3`  
Ngày cập nhật contract: 27/07/2026  
Trạng thái: UET yêu cầu thử nghiệm trong pilot; ý nghĩa sư phạm cuối cùng
chờ HNMU xác nhận

## 1. Lý do tạo v3

Pilot v2 đạt độ lặp lại kỹ thuật cao, nhưng rà soát ngữ nghĩa cho thấy model
còn gán quá rộng một số nguyên tắc. Các lỗi chính là:

- coi chiến lược “có thể hữu ích” như một yêu cầu bắt buộc;
- đồng nhất trả lời trực tiếp hoặc liệt kê với `Explanation`;
- đồng nhất danh sách bước với `Modelling`;
- đồng nhất bước đang làm trong bài hiện tại với `Practice`;
- đồng nhất xác nhận/khen với `Feedback`;
- chấm cao `Questioning` dù câu trả lời của học sinh không thực sự cần
  thiết.

V3 giữ nguyên construct, input, output, thang điểm, threshold và schema của
v2. Thay đổi duy nhất là làm rõ cổng đối chứng trước khi chấm `4`–`5`.

## 2. Cổng đối chứng v3

Một nguyên tắc chỉ được chấm `4`–`5` khi:

1. bằng chứng cho thấy nó đáp ứng một nhu cầu sư phạm độc lập;
2. bỏ nguyên tắc đó sẽ khiến phản hồi tốt không còn đáp ứng đầy đủ nhu cầu
   quan sát được;
3. nguyên tắc không chỉ là một chiến lược thay thế có thể hữu ích;
4. hành vi bề mặt vượt qua đúng phép phân biệt chức năng của nguyên tắc.

Nếu lập luận chỉ chứng minh “có thể hữu ích”, điểm tối đa là `3`.

Năm phép phân biệt được thêm trực tiếp vào prompt:

| Hành vi bề mặt | Không tự động được coi là |
|---|---|
| Trả lời trực tiếp, kể tên, liệt kê | `Explanation` |
| Nêu chuỗi bước | `Modelling` |
| Hoàn thành bước bắt buộc của bài đang giải | `Practice` |
| Xác nhận đúng hoặc khen | `Feedback` |
| Đặt một câu hỏi có thể hữu ích | `Questioning` |

Mỗi trường hợp vẫn có thể nhận `4`–`5` nếu context chứng minh đúng chức
năng và tính cần thiết; đây là ràng buộc chống gán tràn, không phải quy tắc
cấm tuyệt đối.

## 3. Thành phần giữ nguyên từ v2

- Một lượt grounding có tám trường ngữ nghĩa, gồm `gold_answer` nhưng
  không có `gold_response`.
- ID truy vết chỉ được code giữ và không gửi model.
- `requirement_score` là số nguyên 1–5 cho đủ sáu nguyên tắc.
- Code dẫn xuất `required_principle_set` từ điểm `4`–`5` và
  `alternative_principle_set` từ điểm `3`.
- Schema response tiếp tục dùng `scoring_schema_v2.json` vì hình dạng dữ
  liệu không thay đổi.
- Model/config pilot giữ nguyên để phép so sánh v2–v3 chỉ phản ánh thay đổi
  prompt.

## 4. Cách kiểm định

V3 phải chạy trên đúng 40 candidate của pilot v2, với cùng model và
generation config, nhưng ghi vào `pilot_v3/`. Không ghi đè hoặc resume từ
`pilot_v2/`.

So sánh cần tập trung vào:

- số lần `Explanation`, `Modelling`, `Practice`, `Feedback` và
  `Questioning` vượt ngưỡng `>= 4`;
- hai mẫu UET đã nhận định có dấu hiệu gán tràn:
  `BC-HNMU-G8-R0077-STT6-AI04` và
  `BC-HNMU-G9-R0147-STT6-AI04`;
- các trường hợp V2 có rationale chỉ nói “có thể” nhưng vẫn chấm `4`;
- độ lặp lại A/B và các lỗi ngữ nghĩa mới do siết prompt.

Kết quả v3 vẫn là đề xuất của model. UET review kết quả pilot; HNMU xác nhận
cuối cùng trong gói task–rubric–ví dụ tích hợp.

## 5. Quan hệ phiên bản

- `pilot_v1/` và `pilot_v2/` là provenance bất biến.
- V3 thay v2 cho mọi API call thử nghiệm mới.
- Không trộn record của các phiên bản trong cùng một bundle hoặc metric.
- Nếu v3 không cải thiện tính đúng ngữ nghĩa, rollback bằng cách trỏ lại
  manifest/prompt v2; không sửa artifact lịch sử.
