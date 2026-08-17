# Kế hoạch nhóm rút gọn hướng tới Benchmark v2

Trạng thái: `DRAFT — CHỜ NGƯỜI PHỤ TRÁCH DỰ ÁN DUYỆT`

Thời gian thực hiện: 17/08/2026–18/09/2026

Kỳ nghỉ không bố trí công việc: 29/08/2026–02/09/2026

Hạn khóa Benchmark v2 và gói seminar: 18/09/2026

Tài liệu này là phương án rút gọn mới. Các tài liệu phân rã công việc chi tiết
đã có được giữ nguyên để tham khảo, nhưng không phải lịch điều hành chính của
phương án này.

## 1. Cách giao việc

Mỗi người nhận đúng một nhiệm vụ lớn và chịu trách nhiệm về một nhóm đầu ra.
Chậm nhất ngày 18/08, mỗi người tự chia nhiệm vụ lớn thành các nhiệm vụ con,
tự ước lượng thời gian và ghi vào trang `Kế hoạch cá nhân` của tệp Excel đi kèm.

Mỗi nhiệm vụ con chỉ cần nêu: việc cần làm, bằng chứng hoàn thành, ngày bắt đầu,
ngày kết thúc, phụ thuộc và rủi ro chính. Việc thay đổi cách chia nhỏ không cần
xin duyệt lại nếu không làm thay đổi đầu ra, hạn chót hoặc ranh giới thẩm quyền.

## 2. Nhiệm vụ nằm ở đâu trong pipeline xây dựng benchmark

### 2.1. Bản đồ chung

```text
Hội thoại HNMU + SGK/SGV
          │
          ▼
Phase 1 — Kiểm toán dữ liệu thô và truy xuất học liệu
1.050 hội thoại ──► 665 hội thoại đạt
          │
          ├──────────────────────────┐
          ▼                          ▼
Phase 2                        Phase 3
Nền đo lường sư phạm           Chuyển đổi và chọn mẫu
6 nguyên tắc                   665 dialogue family
6 năng lực                     ──► 2.028 candidate
rubric hai tầng                ──► 1.400 mẫu tạm chọn
          └─────────────┬────────────┘
                        ▼
Đánh giá sau Phase 3
3 bộ response của model ──► 2 bộ phán quyết của judge ──► phân tích
                        │
                        ▼
Khóa Benchmark v2 + tài liệu seminar
```


| Phần của pipeline                    | Dữ liệu chính                                                                               | Người phụ trách trong kế hoạch này                                                                                              |
| -------------------------------------- | ---------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| Phase 1 — học liệu và bằng chứng | 1.050 hội thoại HNMU, 665 hội thoại đạt, 2.750 fragment SGK/SGV và chỉ mục tìm kiếm | Hoàng xây cơ chế truy xuất; Nguyên kiểm nội dung và nguồn; Hiếu kiểm tính toàn vẹn đầu vào liên quan |
| Phase 2 — nền đo lường sư phạm  | 6 năng lực, 6 nguyên tắc, 4 tiêu chí chung, 18 tiêu chí riêng và hướng dẫn chấm | Thủy phụ trách 6 năng lực, 6 nguyên tắc và 4 rubric chung; Triệu phụ trách 18 rubric riêng; Hiếu hỗ trợ pilot LLM; nhóm giáo viên Tin học chấm mù cùng mẫu pilot |
| Phase 3 — xây tập benchmark | 665 dialogue family, 2.028 candidate và tập 1.400 mẫu tạm chọn | Quân kiểm chất lượng nội dung của phần được đưa vào v2; Hoàng cung cấp bằng chứng học liệu |
| Đánh giá sau Phase 3 | 3 bộ response trên 1.400 mẫu và 2 bộ judge, mỗi bộ 4.200 phán quyết | Hiếu đo độ tin cậy của requirement scoring và judge; Thủy và Triệu thực hiện pilot có LLM; nhóm giáo viên Tin học chấm mù trên tập hiệu chỉnh và tập kiểm định judge |
| Khóa phiên bản                      | Các đầu ra đã đạt cổng của bốn phần trên                                           | Quân tích hợp, công bố giới hạn và chuẩn bị seminar                                                                          |

Mỗi người vẫn chỉ nhận một nhiệm vụ lớn. Các con số thử nghiệm cụ thể do người
phụ trách đề xuất tại `M0`; không được báo đã kiểm toàn bộ một tập dữ liệu nếu
thực tế chỉ kiểm một mẫu đại diện.

### 2.2. `NV-01` — Quân: khóa Benchmark v2

- **Thuộc phần:** tích hợp và phát hành, đi xuyên qua cả ba phase và bước đánh giá.
- **Nhận đầu vào:** manifest của 665 hội thoại, 2.028 candidate, tập 1.400 mẫu,
  rubric đang dùng, kết quả của Hiếu–Hoàng–Nguyên–Thủy–Triệu và các giới hạn
  khoa học chưa giải quyết.
- **Công việc chính:** quyết định thành phần nào đủ điều kiện vào Benchmark v2;
  khóa phiên bản; bảo đảm dữ liệu, rubric và kết quả đánh giá trỏ đúng phiên bản;
  chuẩn bị cách giải thích tại seminar.
- **Không làm thay:** không tự xác nhận nội dung Tin học thay Nguyên hoặc quyết
  định sư phạm thay Thủy và Triệu.
- **Đầu ra tại `M6`:** một bản ứng viên Benchmark v2 có manifest, báo cáo giới
  hạn, danh sách thành phần được/không được đưa vào, slide và kịch bản seminar.
- **Kiểm tra:** cả nhóm kiểm tra chéo; Quân quyết định phát hành tại `M9`.

### 2.3. `NV-02` — Nguyên: kiểm nội dung Tin học và nguồn của mẫu benchmark

- **Thuộc phase:** cầu nối giữa Phase 1 và Phase 3.
- **Nhận đầu vào:** trường lớp/bài, câu hỏi nguồn, `gold_answer`, nội dung
  candidate, fragment SGK/SGV đã truy xuất và thông tin truy vết về hội thoại gốc.
- **Công việc chính:** xác nhận kiến thức Tin học có đúng không; `gold_answer` có
  thực sự trả lời câu hỏi không; bằng chứng SGK/SGV có hỗ trợ đúng nội dung không;
  mẫu có phụ thuộc thông tin bị thiếu hay mâu thuẫn không.
- **Không làm:** không đánh giá độ ổn định của LLM judge và không tự sửa hội thoại
  nguồn. Trường hợp cần sửa phải được ghi thành quyết định có truy vết.
- **Đầu ra tại `M6`:** sổ quyết định theo mẫu đã xem, danh sách lỗi chặn/cần phân
  xử, báo cáo mức phủ nguồn và danh sách mẫu chưa đủ bằng chứng.
- **Bàn giao:** kết quả được Quân dùng để quyết định mẫu nào đủ điều kiện vào v2;
  vấn đề truy xuất được trả lại Hoàng để sửa cơ chế. Nguyên có thể giải thích
  nguồn và ngữ cảnh dự án cho nhóm giáo viên Tin học, nhưng không chấm, không
  đối chiếu và không phân xử nhãn của các tập hiệu chỉnh/kiểm định dùng để đo
  LLM.

### 2.4. `NV-03` — Hoàng: truy xuất đúng fragment SGK/SGV cho Phase 1

- **Thuộc phase:** Phase 1 — học liệu và truy xuất bằng chứng; kết quả tiếp tục
  phục vụ kiểm chất lượng candidate ở Phase 3.
- **Nhận đầu vào:** dữ liệu hội thoại HNMU, metadata lớp/bài và 2.750 fragment
  SGK/SGV trong chỉ mục tìm kiếm hiện có.
- **Công việc chính:** để tác tử AI đọc dữ liệu thô, rút ra một hoặc nhiều nhu
  cầu thông tin, tạo truy vấn tìm kiếm, xem nhiều kết quả, tinh chỉnh truy vấn và
  chọn fragment có nội dung thực sự hỗ trợ kết luận. Fragment chỉ có tiêu đề hoặc
  chú thích không đủ nội dung phải được nhận diện để không dùng làm bằng chứng.
- **Khác cách cũ:** không mặc định lấy fragment đầu tiên có cùng lớp/bài; metadata
  chỉ dùng để thu hẹp phạm vi, không quyết định fragment cuối cùng.
- **Không làm:** không thay đổi rubric, requirement score hoặc phán quyết judge.
- **Đầu ra tại `M6`:** cơ chế chạy lại được; tập kiểm thử lưu nhu cầu thông tin,
  truy vấn, các kết quả đã xem và lý do chọn; so sánh với cách cũ; danh sách
  fragment ít nội dung; hướng dẫn chạy lại.
- **Kiểm tra:** Nguyên xác nhận fragment được chọn có giá trị nội dung; Quân kiểm
  phạm vi tích hợp.

### 2.5. `NV-04` — Hiếu: đo chất lượng requirement scoring và LLM judge

- **Thuộc phần:** phần đo lường cho hai chỗ có LLM được kiểm định bằng giáo viên:
  requirement scoring ở Phase 3 dựa trên định nghĩa Phase 2 và chấm response ở
  bước đánh giá sau Phase 3. Kiểm toán dữ liệu thô không nằm trong gói chấm giáo
  viên của kế hoạch này.
- **Nhận đầu vào:** output requirement scoring và judge; `PL-REQ` 60 candidate;
  `PL-JDG` 30 candidate sau cổng requirement; `BG-JDG` 60 candidate giữ kín;
  tập 1.400 mẫu, ba bộ response, rubric và hai bộ judge hiện có.
- **Công việc chính:** khóa danh sách mẫu dùng để so sánh; kiểm thiếu/trùng/sai
  ánh xạ; tính metric riêng cho từng công đoạn; phân tích sai số theo lớp, nguyên
  tắc và tiêu chí; với judge, đo thêm bất đồng giữa hai judge và thiên lệch vị
  trí. Hiếu đồng thời hỗ trợ Thủy và Triệu chuẩn bị lời gọi LLM, lưu output và
  đối chiếu hai pilot sư phạm với lượt chấm mù của giáo viên Tin học.
- **Ý nghĩa của “rà”:** vừa kiểm tính toàn vẹn dữ liệu, vừa kiểm độ ổn định của
  LLM so với quyết định giáo viên; không chỉ đọc xem output có nhất quán về câu
  chữ hay không. `PL-REQ` và `PL-JDG` dùng để hiệu chỉnh; chỉ `BG-JDG` được dùng
  như phép kiểm định giữ lại sau khi prompt và rubric đã đóng băng.
- **Không làm:** không tự viết lại rubric, response hay phán quyết để làm chúng
  giống tập chuẩn. Bất đồng phải được giữ lại làm bằng chứng.
- **Đầu ra tại `M7`:** bộ kiểm chạy lại được; báo cáo hiệu chỉnh requirement
  scoring, trong đó không gọi kết quả trên chính `PL-REQ` là accuracy cuối; và
  báo cáo kiểm định judge trên `BG-JDG`, có mức thống nhất, ma trận lỗi và phép
  kiểm tra thiên lệch vị trí bằng cách chạy lại LLM với thứ tự A/B đảo ngược.
- **Kiểm tra:** Quân kiểm kỹ thuật; nhóm giáo viên Tin học xác nhận cách diễn
  giải metric và các nhóm lỗi. Thủy, Triệu và Nguyên không sửa nhãn chuẩn sau
  khi xem kết quả LLM.

### 2.6. `NV-05` — Thủy: sáu nguyên tắc, sáu năng lực và bốn rubric chung

- **Thuộc phase:** Phase 2 — nền đo lường sư phạm và yêu cầu chung đối với mọi
  response gia sư.
- **Nhận đầu vào:** sáu năng lực, sáu nguyên tắc, neo điểm requirement score từ
  1–5, bốn rubric chung đang là bản tạm, candidate/response đại diện và nguồn
  nghiên cứu hiện có.
- **Công việc chính:** kiểm định ranh giới của sáu năng lực và sáu nguyên tắc;
  hoàn thiện neo điểm 1–5 và ý nghĩa của ngưỡng `>=4`; kiểm bốn rubric chung có
  đo đúng điều kiện nền của mọi response hay không; xây ví dụ đạt, chưa đạt và
  ca biên. Thủy dẫn pilot requirement có LLM trên tập nhỏ cùng Hiếu và nhận góp
  ý của Triệu về ranh giới với rubric riêng.
- **Không làm:** không sở hữu 18 rubric riêng của sáu nguyên tắc; không kiểm tính
  đúng kiến thức Tin học thay Nguyên; không dùng output LLM làm nhãn chuẩn.
- **Đầu ra tại `M3`:** đặc tả sáu năng lực; đặc tả sáu nguyên tắc và neo điểm;
  bốn rubric chung đã chỉnh; hướng dẫn chấm requirement; báo cáo pilot LLM có
  đánh dấu lỗi định nghĩa/neo điểm. Nhãn chuẩn vẫn thuộc giáo viên Tin học.
- **Bàn giao:** chuyển sáu nguyên tắc và các ranh giới đã khóa cho Triệu hoàn
  thiện rubric riêng; chuyển hướng dẫn requirement cho giáo viên Tin học chấm
  mù trên cùng tập pilot.

### 2.7. `NV-06` — Triệu: rubric riêng của sáu nguyên tắc sư phạm

- **Thuộc phase:** Phase 2 — tầng rubric riêng; kết quả được dùng ở bước judge
  sau Phase 3.
- **Nhận đầu vào:** sáu nguyên tắc và neo điểm do Thủy bàn giao; 18 rubric riêng
  hiện có, gồm ba tiêu chí cho mỗi nguyên tắc; `required_principles` của các
  candidate pilot; response và phán quyết judge hiện có.
- **Công việc chính:** kiểm từng rubric có đo đúng giá trị tăng thêm của nguyên
  tắc tương ứng không; loại chồng lấn với bốn rubric chung và với rubric của
  nguyên tắc khác; hoàn thiện mô tả, mức đạt/chưa đạt và ví dụ. Triệu dẫn pilot
  judge có LLM trên tập nhỏ cùng Hiếu và phối hợp với Thủy khi lỗi nằm ở định
  nghĩa nguyên tắc thay vì câu chữ rubric.
- **Không làm:** không tự định nghĩa lại sáu nguyên tắc hoặc sáu năng lực; không
  xác định lại `required_principles` trong bước judge; không dùng output LLM làm
  nhãn chuẩn; không xác nhận tính đúng kiến thức Tin học.
- **Đầu ra tại `M3`:** 18 rubric riêng đã chỉnh; bảng ranh giới rubric chung–riêng
  và giữa các nguyên tắc; ví dụ đạt/chưa đạt; báo cáo pilot judge có LLM và danh
  sách lỗi cần trả lại Thủy hoặc chuyển giáo viên Tin học xem xét.
- **Bàn giao:** chuyển rubric riêng đã khóa cho giáo viên Tin học chấm mù trên
  cùng tập pilot; tiếp nhận phản hồi về chỗ khó hiểu nhưng không sửa ngược nhãn
  chuyên môn của giáo viên.

### 2.8. Hai pilot hiệu chỉnh nối tiếp qua cổng requirement

Hai pilot không còn bắt buộc dùng đúng cùng toàn bộ candidate. `PL-REQ` có quy
mô lớn hơn để tạo một tập ground-truth hiệu chỉnh requirement scoring và cung
cấp đủ candidate hợp lệ cho `PL-JDG`:

| Mã pilot | Quy mô đã chọn | Nhánh có LLM | Nhánh giáo viên chuyên môn |
|---|---:|---|---|
| `PL-REQ` | 60 candidate × 6 nguyên tắc = 360 điểm/người chấm | Thủy dẫn nội dung; Hiếu chuẩn bị và lưu output requirement scoring; Triệu rà ranh giới với rubric | `GV-TIN-01` và `GV-TIN-02` chấm mù độc lập đủ sáu điểm 1–5; `GV-TIN-03` phân xử bất đồng còn lại |
| `PL-JDG` | 30 candidate qua cổng × 3 target response = 90 instance/người chấm | Triệu dẫn nội dung; Hiếu chuẩn bị và lưu output judge; Thủy rà bốn rubric chung | Hai giáo viên chấm mù độc lập theo rubric chung và rubric riêng; `GV-TIN-03` phân xử khi cần |

Danh sách chính `PL-REQ` 60 candidate và một danh sách dự phòng 6–10 candidate
phải được khóa trước khi xem output pilot. Việc lấy mẫu dùng các trường phân tầng
của pipeline hiện có, không coi chúng là ground truth, và phải bảo đảm:

- mỗi lớp 6–9 có ít nhất 12 candidate;
- cả sáu nguyên tắc đều được phủ; có ca dự kiến không có nguyên tắc bắt buộc, ca
  ranh giới 3–4 và ca rõ ràng ở hai phía của ngưỡng;
- có hội thoại ngắn, vừa, dài; không lấy quá một candidate từ cùng một dialogue
  family;
- ít nhất 40 candidate đã có đủ gold và ba target response để tăng khả năng lấy
  đủ 30 candidate cho `PL-JDG`; phần còn lại có thể ưu tiên ca requirement khó,
  backlog review hoặc ca có nguy cơ nhãn rỗng.

`PL-JDG` chỉ được chọn sau khi khóa kết quả người chấm của `PL-REQ`. Một candidate
qua cổng requirement khi thỏa đồng thời:

1. hai lượt chấm requirement độc lập đã hoàn thành và mọi bất đồng ảnh hưởng đến
   tập nguyên tắc bắt buộc đã được `GV-TIN-03` phân xử;
2. tập `required_principles` do giáo viên xác nhận không rỗng;
3. tập này khớp chính xác với tập nguyên tắc đã dùng để sinh ba target response;
4. gold và cả ba target response đều đầy đủ;
5. candidate được lấy theo quy tắc phủ lớp, nguyên tắc và mức khó đã khóa trước,
   không dựa vào output hoặc lỗi của LLM judge.

Hiếu khóa 30 candidate đầu tiên thỏa cổng theo quy tắc trên. Nếu 60 candidate
chính cho ít hơn 30 ca hợp lệ, mốc mở `PL-JDG` bị chặn và candidate dự phòng phải
đi qua đầy đủ hai lượt chấm requirement cùng quy trình phân xử; không được chọn
bổ sung sau khi đã xem output judge.

Ca có tập nguyên tắc rỗng vẫn là negative case quan trọng của `PL-REQ`, nhưng
không bị ép vào denominator sạch của `PL-JDG`. Ca mà nhãn giáo viên không khớp
tập nguyên tắc dùng khi sinh response được giữ trong báo cáo chẩn đoán lỗi
upstream. Bốn rubric chung không được dùng để biến hai loại ca này thành mẫu
thay thế cho kiểm định rubric riêng; nếu cần nghiên cứu judge chỉ với rubric
chung, nhóm phải mở một nhánh chẩn đoán riêng sau deadline.

Hai pilot là dữ liệu phát triển: được dùng để sửa định nghĩa, neo điểm, rubric,
threshold và prompt. Vì đã dùng kết quả của chúng để hiệu chỉnh, mọi agreement
hoặc accuracy trên chính `PL-REQ`/`PL-JDG` phải ghi là kết quả calibration, không
phải ước lượng cuối trên dữ liệu giữ lại.

### 2.9. Tập giữ lại để kiểm định LLM judge khi scale-up

Sau hiệu chỉnh chỉ mở một tập giữ lại cho judge. Kế hoạch này bỏ `BG-RAW` và
không tạo `BG-REQ`; do đó chưa có accuracy giữ lại cho requirement scoring trong
đợt trước seminar. Giới hạn này phải được ghi rõ trong báo cáo.

| Mã bàn giao | Mục đích | Quy mô đã chọn | Người chấm độc lập | Đầu ra sau đối chiếu | Phép đo tối thiểu |
|---|---|---:|---|---|---|
| `BG-JDG` | Kiểm tra mức đồng bộ giữa giáo viên và LLM judge sau khi scale-up | 60 candidate × 1 target response = 60 instance/người chấm; cân bằng 20 response cho mỗi target model | `GV-TIN-01` + `GV-TIN-02`; `GV-TIN-03` phân xử | Hai lượt chấm gốc; nhãn đã phân xử; hàng đợi bất đồng và lý do | Agreement/kappa theo tiêu chí và tổng thể; ma trận lỗi; thống kê theo target model và nguyên tắc; kiểm tra vị trí A/B bằng lượt chạy lại LLM |

`BG-JDG` không được trùng bất kỳ candidate nào trong toàn bộ `PL-REQ` 60 mẫu,
không chỉ không trùng 30 mẫu đã vào `PL-JDG`. Danh sách và target response được
khóa tại `M1`, nhưng niêm phong đến khi định nghĩa, rubric, prompt và threshold
được đóng băng tại `M4`. Mỗi candidate phải có tập `required_principles` không
rỗng, gold và target response đầy đủ; 60 target response được phân đều giữa ba
model. Tập này không chấm lại requirement, nên mọi kết luận judge đều có điều
kiện: chúng đánh giá việc áp dụng rubric với tập nguyên tắc đã khóa, không xác
nhận tập nguyên tắc đó đúng về mặt sư phạm.

Giao thức chung:

1. Thủy khóa sáu năng lực, sáu nguyên tắc, neo điểm và bốn rubric chung; Triệu
   khóa 18 rubric riêng sau khi hai người rà ranh giới chung–riêng.
2. Hiếu khóa `PL-REQ`, danh sách dự phòng và `BG-JDG` trước khi chấm; output LLM
   luôn tách khỏi phiếu giáo viên. `PL-JDG` chỉ được dẫn xuất bằng cổng ở mục 2.8.
3. `GV-TIN-01` và `GV-TIN-02` chấm mù độc lập `PL-REQ`; chỉ sau khi requirement
   được phân xử mới mở `PL-JDG`. Sau khi hiệu chỉnh hoàn tất và mọi phiên bản đã
   đóng băng, hai giáo viên mới nhận `BG-JDG`.
4. Người chấm không thấy output hoặc điểm của LLM trong lượt độc lập. Hai lượt
   chấm được lưu riêng và không sửa để làm giống nhau.
5. Chỉ sau khi cả hai hoàn thành mới mở phiên đối chiếu. Bất đồng chưa giải quyết
   được chuyển cho `GV-TIN-03`; nếu chưa phân xử trước `M6`, ca đó nằm ngoài
   denominator sạch nhưng vẫn nằm trong báo cáo.
6. Hiếu chỉ dùng nhãn đã thống nhất hoặc được giáo viên thứ ba phân xử để đo LLM;
   phải báo cả mức thống nhất giữa hai giáo viên. Thử đảo A/B chỉ chạy lại LLM,
   không yêu cầu giáo viên chấm lại cùng nội dung.
7. Không sửa prompt, rubric, threshold hoặc danh sách mẫu sau khi mở nhãn
   `BG-JDG`. Nếu phát hiện lỗi nghiêm trọng, giữ nguyên log, báo giới hạn và dừng
   claim kiểm định thay vì quay lại tuning trên tập giữ lại.

### 2.10. Ước tính công giáo viên chuyên môn

Quy ước một công bằng 8 giờ làm việc tập trung. Mỗi giáo viên dự kiến chấm 360
điểm requirement trên `PL-REQ`, 90 instance judge trên `PL-JDG` và 60 instance
judge trên `BG-JDG`. Với trung bình hiện tại khoảng 9,25 tiêu chí/instance, 150
instance judge tương đương xấp xỉ 1.387 quyết định theo tiêu chí và 150 quyết
định tổng thể cho mỗi người chấm, ngoài 360 điểm requirement.

Để tránh nhầm đơn vị khi so với KMP-Bench: con số 300 instance và hai phần 150
instance trong [bản paper đầy đủ](https://arxiv.org/pdf/2603.02775) là số phiếu
so sánh response, không phải số criterion. Mỗi instance còn chứa các criterion
chung, criterion theo nguyên tắc và một quyết định tổng thể. Kế hoạch này vì vậy
ước lượng công theo cả số instance lẫn số quyết định criterion.

| Người/nhóm | Trước kỳ nghỉ | Sau kỳ nghỉ | Tổng công cơ sở |
|---|---:|---:|---:|
| `GV-TIN-01` | 4,0 công: `PL-REQ` 60 và `PL-JDG` 30 × 3 | 2,5 công: `BG-JDG` 60 × 1, đối chiếu và hỗ trợ phân xử | 6,5 |
| `GV-TIN-02` | 4,0 công: `PL-REQ` 60 và `PL-JDG` 30 × 3 | 2,5 công: `BG-JDG` 60 × 1, đối chiếu và hỗ trợ phân xử | 6,5 |
| **Tổng** | **8,0 công** | **5,0 công** | **13,0 công = 104 giờ** |

Kế hoạch giữ dự phòng 20%, tương đương tối đa khoảng **16 công**, cho candidate
dự phòng, ca bất đồng, tốc độ chậm hơn ước tính hoặc `GV-TIN-03` phân xử. Tốc độ
thực tế phải được đo theo requirement và judge riêng trước `M3`; nếu khối lượng
không vừa trần, Quân phải giảm phạm vi hoặc báo phần bị chặn, không chuyển việc
vào kỳ nghỉ. Khối lượng nội bộ của Quân, Hiếu, Hoàng, Nguyên, Thủy và Triệu được
theo dõi riêng. Nếu hướng dẫn thay đổi sau pilot, dữ liệu pilot được gắn nhãn
calibration; không âm thầm chấm lại rồi gọi đó là kết quả giữ lại.

## 3. Việc phải hoàn thành trước kỳ nghỉ

Ngày 28/08 là cổng bắt buộc cho các phần có rủi ro cao. Trước khi nghỉ, nhóm cần
có đủ các thành phần sau:

- Hoàng có phiên bản truy xuất đầu tiên; Hiếu có pipeline pilot LLM và đo lường
  đầu tiên; cả hai lưu được bằng chứng chạy lại;
- Nguyên đã lập danh sách các lỗi nội dung hoặc nguồn có thể chặn Benchmark v2;
- `GV-TIN-01`, `GV-TIN-02` và phương án gọi `GV-TIN-03` khi cần phân xử đã
  được xác nhận;
- Hiếu đã khóa `PL-REQ` 60 candidate, danh sách dự phòng, `BG-JDG` 60 candidate
  giữ kín và các phiếu chấm mù; ID không được thay sau khi xem kết quả LLM;
- Thủy đã khóa sáu năng lực, sáu nguyên tắc, neo điểm và bốn rubric chung; Triệu
  đã khóa 18 rubric riêng sau khi hai người rà ranh giới;
- hai lượt chấm mù `PL-REQ` đã hoàn thành, bất đồng ảnh hưởng đến cổng requirement
  đã được phân xử và `PL-JDG` 30 candidate được dẫn xuất đúng quy tắc;
- nhánh có LLM và hai lượt chấm mù của giáo viên đã hoàn thành trên `PL-JDG`
  30 × 3; nhóm đã đo riêng thời gian chấm requirement/judge và ghi lại điểm chưa
  rõ trong hướng dẫn;
- Quân đã khóa phạm vi tối thiểu của Benchmark v2 và danh sách việc không đưa
  vào phiên bản seminar.

Không lên lịch công việc trong giai đoạn 29/08–02/09. Các đầu việc chưa đạt cổng
ngày 28/08 phải được báo là rủi ro, không mặc định chuyển sang kỳ nghỉ.

## 4. Các mốc quan trọng

| Mốc | Ngày | Người chủ trì | Bàn giao bắt buộc | Nếu chưa đạt |
|---|---:|---|---|---|
| `M0` — Khởi động | 18/08 | Quân | Lịch cá nhân; xác nhận `GV-TIN-01`, `GV-TIN-02`, phương án `GV-TIN-03`; trần 16 công | Báo thiếu nguồn lực; chưa khóa lịch pilot |
| `M1` — Khóa đặc tả và mẫu | 21/08 | Thủy, Triệu, Hiếu | Bản sáu năng lực/nguyên tắc/bốn rubric chung; 18 rubric riêng; `PL-REQ` 60, dự phòng 6–10, `BG-JDG` 60 giữ kín; phiếu chấm mù và quy tắc cổng requirement | Không được chạy LLM hoặc giao mẫu cho giáo viên |
| `M2` — Mở `PL-REQ` | 24/08 | Hiếu | Nhánh requirement scoring hoạt động; hai giáo viên nhận 60 candidate và phiếu sáu nguyên tắc không có output LLM | Dừng pilot nếu lộ nhãn, sai phiên bản hướng dẫn hoặc thiếu ID |
| `M2A` — Khóa cổng requirement | 26/08 | Hiếu, `GV-TIN-03` | Hai lượt `PL-REQ` đã nộp; bất đồng ảnh hưởng đến tập nguyên tắc đã phân xử; danh sách `PL-JDG` đủ 30 candidate hợp lệ được khóa | Chưa mở `PL-JDG`; đưa candidate dự phòng qua đầy đủ quy trình hoặc báo bị chặn |
| `M3` — Đóng calibration trước kỳ nghỉ | 28/08 | Quân | 360 điểm requirement và 90 instance judge từ LLM; hai lượt chấm mù tương ứng; log phân xử; thời gian thực tế; danh sách lỗi hướng dẫn | Không chuyển việc vào kỳ nghỉ; giảm phạm vi hoặc báo phần bị chặn |
| Kỳ nghỉ | 29/08–02/09 | Cả nhóm | Không bố trí công việc | Khởi động lại ngày 03/09 |
| `M4` — Đóng băng và mở tập giữ lại | 04/09 | Hiếu, Hoàng | Định nghĩa, rubric, prompt và threshold sau calibration đã khóa; mở `BG-JDG` mà không lộ output LLM; cơ chế truy xuất chạy lại được | Chưa mở `BG-JDG` hoặc chưa tích hợp truy xuất |
| `M5` — Kiểm tra giữa chặng | 08/09 | Hiếu | Ít nhất 30/60 instance `BG-JDG` đã được mỗi giáo viên chấm; hàng đợi bất đồng; báo cáo tiến độ truy xuất và lỗi LLM sơ bộ | Quân giảm phạm vi không thiết yếu hoặc bổ sung người phân xử |
| `M6` — Hoàn thành kiểm định giữ lại | 11/09 | Hai giáo viên Tin học, Hiếu | `BG-JDG` 60 × 1 đủ hai lượt; biên bản đối chiếu/phân xử; ca chưa thống nhất tách riêng; kết quả truy xuất của Hoàng | Không được gọi kết quả judge là kiểm định giữ lại ổn định |
| `M7` — Báo cáo chất lượng LLM | 14/09 | Hiếu | Báo cáo calibration requirement và báo cáo kiểm định judge; ma trận lỗi, mức thống nhất giữa giáo viên, kiểm tra vị trí và giới hạn | Không đưa kết luận định lượng vào Benchmark v2 |
| `M8` — Đóng băng Benchmark v2 | 16/09 | Quân | Bundle v2, manifest, báo cáo giới hạn và slide seminar đã kiểm tra | Chỉ sửa lỗi chặn hoặc dùng bản dự phòng |
| `M9` — Seminar | 18/09 | Quân | Benchmark v2 phát hành nội bộ và gói trình bày hoàn chỉnh | Trình bày bản dự phòng đã khóa và nêu rõ giới hạn |

Mỗi mốc kiểm đầu ra và quyết định tiếp tục/dừng. Không yêu cầu thành viên giữ
nguyên cách chia nhiệm vụ con nếu đầu ra, hạn và ranh giới thẩm quyền không đổi.

## 5. Phiếu nhiệm vụ của Thủy

Vai trò: người xây dựng nền đo lường sư phạm. Thủy sở hữu sáu năng lực, sáu
nguyên tắc và bốn rubric chung; không sở hữu rubric riêng và không xác nhận nhãn
chuẩn. Kết quả được Triệu rà ranh giới và giáo viên Tin học kiểm bằng chấm mù.

### Mục tiêu

Hoàn thiện sáu năng lực, sáu nguyên tắc, neo điểm 1–5 và bốn rubric chung; kiểm
chúng trên `PL-REQ` 60 candidate bằng một lượt LLM và hai lượt giáo viên chấm mù
độc lập.

### Vì sao cần task này

Sáu năng lực và sáu nguyên tắc định nghĩa phần cần quan sát; bốn rubric chung
đặt điều kiện nền cho mọi response. Nếu khối này chưa rõ, cả requirement scoring
và rubric riêng của Triệu sẽ kế thừa sai lệch.

### Bạn nhận được gì

Bản sáu năng lực, sáu nguyên tắc, neo điểm và bốn rubric chung hiện có; nguồn
nghiên cứu; `PL-REQ` 60 candidate; output LLM do Hiếu chuẩn bị; biểu mẫu ghi ca
biên. Thủy
không nhận phiếu chấm mù của giáo viên trước khi khóa nhận xét pilot của mình.

### Các bước thực hiện

Rà ranh giới sáu năng lực và sáu nguyên tắc; viết neo điểm 1–5; giải thích ngưỡng
`>=4`; rà bốn rubric chung; thêm ví dụ đạt, chưa đạt và ca biên; cùng Hiếu xem
LLM áp dụng hướng dẫn trên `PL-REQ`; ghi lỗi định nghĩa hoặc prompt; bàn giao
ranh giới nguyên tắc cho Triệu và chỉ đối chiếu với giáo viên sau khi lượt chấm
mù đã khóa.

### Ví dụ đạt yêu cầu

Với một candidate, Thủy nêu `Feedback=4` khi gia sư bắt buộc phải chỉ ra điểm
cần cải thiện và cách cải thiện; đồng thời chỉ ra bốn rubric chung vẫn áp dụng
cho mọi response, không phụ thuộc candidate có yêu cầu Feedback hay không.

### Ví dụ cần sửa

Viết lại cả rubric riêng của Feedback trong khi Triệu đang sở hữu phần đó. Cách
làm này tạo hai người cùng sửa một artifact và làm mờ trách nhiệm khi có lỗi.

### Bạn cần nộp gì

Đặc tả sáu năng lực; đặc tả sáu nguyên tắc và neo điểm 1–5; quy tắc ngưỡng
`>=4`; bốn rubric chung; ví dụ và ca biên; báo cáo calibration `PL-REQ` có LLM;
danh sách phản hồi chuyển Triệu. Báo cáo này không phải accuracy giữ lại.

### Checklist tự kiểm tra

Sáu năng lực và sáu nguyên tắc có ranh giới rõ; điểm requirement không bị suy từ
response; bốn rubric chung không lấn sang rubric riêng; output LLM chỉ được ghi
là kết quả pilot; ca chưa chắc chắn có hướng chuyển tiếp.

### Thời gian dự kiến

Tự phân rã và ước lượng trước 18/08; khóa bản cho `PL-REQ` trước `M1`; đối chiếu
với lượt chấm mù và hoàn thiện trước `M3`.

### Khi cần hỗ trợ

Hỏi Hiếu khi thiếu output LLM hoặc phiếu pilot; hỏi Triệu khi ranh giới chạm
rubric riêng; hỏi Nguyên khi ví dụ phụ thuộc kiến thức Tin học. Chuyển bất đồng
về phạm vi cho Quân; không tự sửa nhãn của giáo viên.

## 6. Phiếu nhiệm vụ của Triệu

Vai trò: người xây dựng rubric riêng. Triệu sở hữu 18 rubric của sáu nguyên tắc,
gồm ba rubric cho mỗi nguyên tắc; không sở hữu sáu năng lực, định nghĩa nguyên
tắc hoặc bốn rubric chung. Kết quả được Thủy rà ranh giới và giáo viên Tin học
kiểm bằng chấm mù.

### Mục tiêu

Hoàn thiện 18 rubric riêng và kiểm chúng trên `PL-JDG` bằng một lượt LLM và hai
lượt giáo viên chấm mù độc lập.

### Vì sao cần task này

Rubric riêng quyết định judge đo được giá trị tăng thêm của từng nguyên tắc hay
không. Nếu rubric chồng lấn với rubric chung hoặc với nhau, điểm judge không còn
cho biết response đã thực hiện nguyên tắc nào.

### Bạn nhận được gì

Sáu nguyên tắc và neo điểm do Thủy bàn giao; 18 rubric riêng hiện có; quy tắc
cổng requirement; `PL-JDG` gồm 30 candidate hợp lệ với ba target response mỗi
candidate; output LLM do Hiếu chuẩn bị; bốn rubric chung để kiểm ranh giới. Triệu
không nhận phiếu
chấm mù của giáo viên trước khi khóa nhận xét pilot của mình.

### Các bước thực hiện

Rà ba rubric của từng nguyên tắc; kiểm chồng lấn với bốn rubric chung và năm
nguyên tắc còn lại; viết mức đạt/chưa đạt và ví dụ; xác nhận Hiếu chỉ mở
`PL-JDG` sau khi đủ 30 candidate qua cổng requirement; dùng tập nguyên tắc đã
phân xử để cùng Hiếu xem LLM chấm `PL-JDG`; ghi lỗi rubric hoặc prompt; trả lỗi
định nghĩa nguyên tắc cho Thủy; chỉ đối chiếu với giáo viên sau khi lượt chấm mù
đã khóa.

### Ví dụ đạt yêu cầu

Với candidate đã có `required_principles=[Feedback]`, Triệu áp dụng đúng ba
rubric Feedback cùng bốn rubric chung để rà phán quyết của LLM; không dùng
response để thay đổi lại requirement score.

### Ví dụ cần sửa

Thêm một rubric riêng đo lại “tính đúng kiến thức” dù nội dung này đã thuộc
rubric chung. Cách làm đó đếm hai lần cùng một thuộc tính và làm sai kết quả.

### Bạn cần nộp gì

Mười tám rubric riêng đã chỉnh; bảng ranh giới chung–riêng và giữa nguyên tắc;
ví dụ đạt/chưa đạt; báo cáo calibration `PL-JDG` có LLM; danh sách lỗi trả Thủy
và điểm cần giáo viên xem xét. Báo cáo này không phải kết quả giữ lại.

### Checklist tự kiểm tra

Mỗi nguyên tắc có đúng ba rubric; không trùng bốn rubric chung; không áp rubric
ngoài `required_principles`; không dùng response sửa ngược requirement; output
LLM chỉ được ghi là kết quả pilot.

### Thời gian dự kiến

Tự phân rã và ước lượng trước 18/08; khóa rubric dùng cho calibration trước `M1`;
nhận danh sách `PL-JDG` đã qua cổng tại `M2A`; đối chiếu với lượt chấm mù và
hoàn thiện trước `M3`.

### Khi cần hỗ trợ

Hỏi Hiếu khi thiếu output LLM hoặc response; hỏi Thủy khi lỗi nằm ở định nghĩa
nguyên tắc hoặc bốn rubric chung; đánh dấu trường hợp cần kiến thức Tin học để
giáo viên chuyên môn xem. Quân xử lý vấn đề phạm vi hoặc thời gian.

## 7. Phiếu nhiệm vụ của giáo viên Tin học chấm calibration và tập giữ lại

Phiếu này được giao riêng cho `GV-TIN-01` và `GV-TIN-02`. Mỗi người là một
người chấm độc lập; không xem phiếu của người kia trước khi hoàn thành. Kết quả
được Hiếu tiếp nhận để đo LLM. Ca chưa thống nhất được chuyển cho
`GV-TIN-03`, không chuyển cho Quân, Nguyên, Thủy hoặc Triệu quyết định thay.

### Mục tiêu

Tạo nhãn calibration độc lập cho requirement scoring và judge, sau đó tạo tập
giữ lại độc lập để kiểm tra LLM judge khi tăng quy mô.

### Vì sao cần task này

Hai công đoạn requirement scoring và judge hiện dùng LLM nhưng chưa có thước đo
độc lập của giáo viên Tin học. Nếu dùng chính output LLM hoặc người xây hướng
dẫn làm đáp án, phép đo sẽ không phản ánh đúng chất lượng của LLM.

### Bạn nhận được gì

`PL-REQ` 60 candidate và phiếu chấm sáu nguyên tắc; sau khi cổng requirement
đóng, `PL-JDG` 30 candidate với ba target response/candidate; sau khi prompt và
rubric đóng băng, `BG-JDG` 60 candidate với một target response/candidate. Giáo
viên cũng nhận hướng dẫn thang điểm 1–5, rubric chung/riêng, nguồn SGK/SGV cần
thiết và phiếu không có điểm của LLM hoặc người chấm còn lại.

### Các bước thực hiện

1. Chấm mù đủ sáu nguyên tắc cho 60 candidate `PL-REQ`; trích bằng chứng, ghi
   mức chắc chắn và nộp phiếu độc lập.
2. Chỉ sau khi cả hai phiếu đã nộp, tham gia đối chiếu; chuyển bất đồng ảnh hưởng
   đến `required_principles` cho `GV-TIN-03` phân xử.
3. Nhận `PL-JDG` 30 candidate đã qua cổng; với mỗi candidate, chấm ba target
   response theo bốn rubric chung, rubric của các nguyên tắc bắt buộc và quyết
   định tổng thể. Nộp trước khi xem output LLM hoặc phiếu người kia.
4. Sau khi calibration kết thúc và mọi phiên bản đã đóng băng, nhận `BG-JDG` 60
   candidate × 1 target response; chấm độc lập bằng đúng phiên bản rubric đã
   khóa rồi mới đối chiếu/phân xử.
5. Giữ nguyên phiếu gốc và ca chưa thống nhất. Không quay lại sửa nhãn giữ lại
   để làm agreement với LLM cao hơn.

### Ví dụ đạt yêu cầu

Giáo viên chấm một nguyên tắc điểm 4, chỉ rõ bằng chứng trong candidate cho thấy
nguyên tắc là bắt buộc, rồi để quy tắc chung đưa nguyên tắc đó vào
`required_principles`. Nếu một candidate không có nguyên tắc nào đạt ngưỡng,
giáo viên vẫn giữ nhãn rỗng trong `PL-REQ`; không tự ép candidate đó vào
`PL-JDG`. Khi chấm response, giáo viên dùng tập nguyên tắc đã phân xử và rubric
tương ứng.

### Ví dụ cần sửa

Xem trước điểm của LLM hoặc của giáo viên còn lại rồi điều chỉnh cho giống nhau;
hoặc đổi tập nguyên tắc bắt buộc trong lúc chấm response. Kết quả như vậy không
còn độc lập và trộn lẫn requirement scoring với judge.

### Bạn cần nộp gì

Một phiếu riêng cho `PL-REQ`, `PL-JDG` và `BG-JDG`; bằng chứng và mức chắc chắn;
danh sách ca thiếu thông tin; sau đối chiếu, biên bản thống nhất và danh sách ca
cần `GV-TIN-03` phân xử. Phiếu gốc của hai người phải được lưu nguyên trạng.

### Checklist tự kiểm tra

Không xem nhãn LLM; không xem phiếu người kia trước khi nộp; mọi quyết định có
bằng chứng; requirement và chấm response được thực hiện thành hai bước riêng;
candidate nhãn rỗng/mismatch không bị ép qua cổng; không dùng calibration để sửa
nhãn `BG-JDG`; ca chưa chắc chắn không bị ép thành nhãn dứt khoát.

### Thời gian dự kiến

Mỗi người dự kiến 6,5 công: 4,0 công cho `PL-REQ` và `PL-JDG` trước kỳ nghỉ; 2,5
công cho `BG-JDG`, đối chiếu và hỗ trợ phân xử sau kỳ nghỉ. Hoàn thành calibration
trước `M3`, tập giữ lại trước `M6`; chỉ đối chiếu sau khi cả hai lượt đã nộp.

### Khi cần hỗ trợ

Hỏi Hiếu khi thiếu mẫu hoặc phiếu; yêu cầu bổ sung nguồn khi bằng chứng chưa
đủ; chuyển bất đồng chuyên môn cho `GV-TIN-03`. Người điều phối không quyết định
nhãn chuyên môn thay giáo viên.

## 8. Định hướng công bố sau Benchmark v2

Các hạn dưới đây được kiểm tra từ trang chính thức ngày 14/08/2026. Việc đưa một
kênh vào danh sách không đồng nghĩa nhóm đã quyết định nộp.

### 8.1. Hiểu đúng về xếp hạng

- [ICORE 2026](https://www.core.edu.au/icore-portal) xếp hạng hội nghị máy tính
  theo các mức `A*`, `A`, `B`, `C`. Trong 825 venue được xếp hạng, nhóm `A*`
  chiếm 7,52% và nhóm `A` chiếm 13,09%.
- [SIGCSE TS](https://portal.core.edu.au/conf-ranks/55/) và
  [LAK](https://portal.core.edu.au/conf-ranks/2268/) đều được xếp hạng `A`;
  [CHI](https://portal.core.edu.au/conf-ranks/1053/) được xếp hạng `A*`.
- Xếp hạng trên áp dụng cho venue nghiên cứu nói chung. Poster, demo hoặc báo cáo
  thực hành không có trọng lượng học thuật tương đương bài nghiên cứu đầy đủ/ngắn
  đã qua quy trình phản biện chính, dù được trình bày tại cùng hội nghị.
- Chỉ số trích dẫn và quartile giúp sàng lọc tạp chí, nhưng không thay thế việc
  kiểm tra phạm vi, loại bài, chất lượng phương pháp và chi phí công bố.

### 8.2. Danh sách cân nhắc


| Kênh                                                                                                                                                                | Uy tín/xếp hạng hiện biết                                                                                                   |                                                 Hạn hiện biết | Mức phù hợp và khuyến nghị                                                                                                                                                                                                                         |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------: | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [LAK 2027 — bài nghiên cứu đầy đủ/ngắn](https://www.solaresearch.org/events/lak/lak27/general-call/)                                                        | ICORE 2026 hạng`A`; đây là nhánh bài nghiên cứu chính                                                                   |                                                       28/09/2026 | Hội nghị tốt, nhưng chỉ chọn nếu bản thảo đã gần hoàn chỉnh và có đóng góp về phân tích học tập/vòng phản hồi với giáo viên hoặc người học. Benchmark thuần kỹ thuật có nguy cơ ngoài phạm vi; lịch rất gấp. |
| [SIGCSE TS 2027 — poster hoặc demo](https://2027.sigcse-ts.acm.org/)                                                                                               | Hội nghị ICORE 2026 hạng`A`, nhưng loại poster/demo không tương đương bài nghiên cứu đầy đủ                    |                                                       30/09/2026 | Phù hợp trực tiếp với giáo dục Tin học và hữu ích để giới thiệu Benchmark v2 sớm. Nên coi đây là phổ biến kết quả/nhận phản hồi, không phải mục tiêu bài nghiên cứu chính.                                            |
| [LAK 2027 — báo cáo thực hành](https://www.solaresearch.org/events/lak/lak27/general-call/)                                                                     | Hội nghị hạng`A`, nhưng bài nằm ở nhánh báo cáo thực hành                                                            |                                                       13/10/2026 | Chọn khi có bối cảnh triển khai, kết quả, bài học và phản hồi thực tế của bên liên quan. Không nên mô tả nó như bài nghiên cứu đầy đủ.                                                                                     |
| [LAK 2027 — poster/demo](https://www.solaresearch.org/events/lak/lak27/general-call/)                                                                               | Hội nghị hạng`A`, nhưng sản phẩm nằm trong kỷ yếu bổ trợ                                                              |                                                       09/11/2026 | Phương án ít gấp hơn để trình bày Benchmark v2 và quy trình kiểm định; phù hợp để lấy phản hồi trước khi nộp bài chính.                                                                                                       |
| [International Journal of Artificial Intelligence in Education](https://www.sciencedirect.com/journal/international-journal-of-artificial-intelligence-in-education) | Tạp chí chính thức của International AIED Society; Journal Impact Factor 8,5 và CiteScore 18,5 trên trang nhà xuất bản | Không có hạn kỳ cố định được ghi trên trang kiểm tra | Mục tiêu tạp chí ưu tiên vì khớp trực tiếp với đánh giá gia sư AI, intelligent tutoring system và kiểm định với chuyên gia. Đây là venue uy tín cao nhưng yêu cầu đóng góp phương pháp và kiểm định đủ mạnh.    |
| [Computers & Education: Artificial Intelligence](https://www.sciencedirect.com/journal/computers-and-education-artificial-intelligence)                              | SCImago`Q1`; CiteScore 28,7 trên trang nhà xuất bản                                                                          | Không có hạn kỳ cố định được ghi trên trang kiểm tra | Uy tín và chỉ số cao, phạm vi khớp AI trong giáo dục. Đây là tạp chí truy cập mở có phí; cần kiểm tra ngân sách và tránh chỉ mô tả một bộ dữ liệu mà thiếu đóng góp khoa học.                                        |
| [Journal of Computer Assisted Learning](https://onlinelibrary.wiley.com/journal/13652729)                                                                            | SCImago`Q1`; trang Wiley ghi CiteScore 10,8 và Journal Impact Factor 4,6                                                        | Không có hạn kỳ cố định được ghi trên trang kiểm tra | Venue tốt nhưng phù hợp hơn khi bài chứng minh được ý nghĩa đối với khoa học học tập, thiết kế dạy học hoặc đánh giá sư phạm, thay vì chỉ trình bày benchmark.                                                           |

[CHI 2027](https://chi2027.acm.org/authors/papers/) có hạn bài đầy đủ ngày
10/09/2026, sớm hơn thời điểm khóa Benchmark v2. Không nên ép nhóm chạy theo kỳ
này; chỉ giữ làm tham chiếu cho một nghiên cứu tương tác người–AI trong tương lai.

### 8.3. Khuyến nghị theo hai tầng

1. Tại `M9`, chọn **một** phương án phổ biến kết quả sớm: SIGCSE TS poster/demo
   ngày 30/09 hoặc LAK poster/demo ngày 09/11.
2. Sau seminar, dùng phản hồi để hoàn thiện kiểm định và chọn **một** tạp chí
   chính: ưu tiên International Journal of Artificial Intelligence in Education;
   cân nhắc Computers & Education: Artificial Intelligence nếu phù hợp ngân sách.
3. Chỉ chạy theo hạn LAK bài nghiên cứu ngày 28/09 nếu đến `M6` đã có bản thảo
   gần hoàn chỉnh. Không giảm chất lượng Benchmark v2 để đổi lấy một lần nộp gấp.

## 9. Điều kiện dừng và phân xử

- Tác tử AI chỉ chuẩn bị gợi ý, không thay giáo viên xác nhận quyết định sư phạm.
- Nguyên giữ thẩm quyền chuyên môn Tin học; Quân quyết định phạm vi phát hành.
- Bất đồng phải được lưu nguyên trạng trước khi phân xử.
- Phần không đạt `M6` được loại khỏi Benchmark v2 thay vì âm thầm hạ tiêu chí.
- Sau `M8`, chỉ sửa lỗi có thể làm sai kết quả hoặc chặn seminar.
