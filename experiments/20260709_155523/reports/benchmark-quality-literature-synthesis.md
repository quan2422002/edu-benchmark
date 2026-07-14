# Tổng hợp Kế hoạch 01 — Các bài báo đánh giá chất lượng của bộ đánh giá như thế nào?

Thử nghiệm: `20260709_155523`
Kế hoạch: `01-benchmark-quality-literature-review.md`
Ngày: 12/07/2026
Trạng thái: bản tổng hợp v1, đã rà lại thuật ngữ để ưu tiên tiếng Việt.

## 1. Quy ước thuật ngữ trong bản này

Bản này ưu tiên tiếng Việt trong phần diễn giải. Các từ tiếng Anh chỉ được giữ khi là tên bài báo, tên mô hình, tên thước đo chính thức, tên trường dữ liệu, đường dẫn tệp hoặc đường dẫn web.

- “Bộ đánh giá” là cách gọi chính trong phần diễn giải; thuật ngữ tiếng Anh tương ứng chỉ giữ khi nằm trong tên bài báo, đường dẫn hoặc tên trường kỹ thuật.
- “Độ phủ” chỉ việc dữ liệu bao quát đủ chủ đề, dạng bài, mức nhận thức và hành vi gia sư cần đánh giá.
- “Tính nhất quán” chỉ sự khớp nhau giữa hội thoại và thông tin phụ trợ như chủ đề, bài học, dạng bài, mức nhận thức.
- “Trùng/gần trùng” chỉ mẫu lặp lại hoàn toàn hoặc chỉ thay đổi rất nhỏ.
- “Phản hồi tham chiếu” là lượt gia sư hoặc lời giải mẫu dùng làm căn cứ chấm.
- “Phản hồi gia sư mẫu” là phản hồi lý tưởng do chuyên gia viết hoặc duyệt.
- “Bộ chấm tự động” là mô hình hoặc quy trình tự động dùng để hỗ trợ chấm điểm; không được coi là chân lý nếu chưa kiểm tra với chuyên gia.

## 2. Kết luận ngắn gọn

Bốn bài báo không có một mục duy nhất tên là “đánh giá chất lượng của bộ đánh giá”. Thay vào đó, họ chứng minh bộ đánh giá đáng tin qua nhiều lớp bằng chứng:

1. **Độ phủ có cấu trúc**: phủ theo năng lực, nhiệm vụ, tình huống sử dụng, miền kiến thức, cấp học, mức nhận thức hoặc nguyên tắc sư phạm.
2. **Chất lượng dữ liệu**: nguồn dữ liệu rõ, chuyên gia tạo hoặc rà soát, loại mẫu lỗi, tránh biến thể tầm thường, kiểm tra rò rỉ hoặc trùng lặp.
3. **Độ tin cậy chấm điểm**: mô hình phần thưởng hoặc bộ chấm tự động phải được kiểm tra với chuyên gia con người; tốt hơn nữa là có độ đồng thuận hoặc Cohen’s Kappa giữa người chấm.
4. **Tính phân biệt**: bộ đánh giá phải tạo được chênh lệch điểm giữa mô hình/gia sư mạnh/yếu; không bị bão hòa; có thể chỉ ra mô hình giỏi giải bài nhưng kém sư phạm.
5. **Tính truy vết nguồn**: VietLegal đặc biệt nhấn mạnh cơ sở dữ liệu nguồn và công cụ truy xuất cho người gán nhãn; đây là điểm rất đáng chuyển sang SGK Tin học THCS.

## 3. Bài báo nào hữu ích nhất cho tiêu chí nào?


| Tiêu chí đánh giá bộ đánh giá                 | Bài báo hỗ trợ mạnh                         | Ý nghĩa cho dự án                                                                                                         |
| ------------------------------------------------------ | ------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------- |
| Tách năng lực giải đúng khỏi năng lực gia sư | MathTutorBench; KMP-Bench; TutorBench            | Không được chỉ đo đáp án đúng; phải đo gợi mở, phản hồi, hiểu học sinh.                                    |
| Kiểm soát dữ liệu có dùng AI để sinh           | KMP-Bench; VietLegal                             | Dữ liệu HNMU có dùng AI hỗ trợ nên bắt buộc kiểm tra lỗi, trùng/gần trùng và trình tự hội thoại.           |
| Độ phủ theo học liệu và nhiệm vụ               | KMP-Bench; TutorBench; VietLegal                 | Cần ma trận độ phủ theo SGK, mức nhận thức, dạng bài và hành vi gia sư.                                          |
| Phản hồi tham chiếu                                 | KMP-Bench; TutorBench; MathTutorBench            | Dùng làm căn cứ chấm hoặc viết tiêu chí, không dùng như đáp án câu chữ duy nhất.                            |
| Độ tin cậy của bộ chấm                           | TutorBench; KMP-Bench; VietLegal; MathTutorBench | Nếu dùng bộ chấm tự động, phải kiểm tra với chuyên gia con người.                                                |
| Bộ đánh giá phân biệt mô hình mạnh/yếu       | MathTutorBench; KMP-Bench; TutorBench; VietLegal | Cần thử nghiệm sau chuyển đổi để xem điểm có phân hóa không.                                                    |
| Hệ thống học liệu và truy xuất nguồn            | VietLegal                                        | Cần cơ sở dữ liệu SGK để giáo viên và mô hình truy xuất nguồn, không để mô hình trả lời không căn cứ. |

## 4. Khung đánh giá bộ đánh giá đề xuất cho dự án

### Tầng 1 — Dữ liệu thô HNMU

Áp dụng ngay khi nhận đợt dữ liệu dữ liệu.

Cần kiểm tra:

- độ phủ theo SGK Tin học THCS, chủ đề, bài học;
- độ phủ theo mức nhận thức: Biết, Hiểu, Vận dụng;
- độ phủ theo dạng câu hỏi/bài tập;
- tính nhất quán giữa hội thoại và thông tin phụ trợ;
- trùng/gần trùng;
- hội thoại có trình tự sư phạm hợp lý không;
- mẫu có dấu hiệu do AI sinh nhưng chưa được rà soát kỹ không.

Bằng chứng liên quan:

- KMP-Bench loại 7.6% luồng hội thoại sau kiểm tra thủ công.
- VietLegal có kiểm tra chéo, đo độ đồng thuận, phân xử và kiểm tra rò rỉ/trùng lặp.

### Tầng 2 — Mẫu bộ đánh giá sau chuyển đổi

Áp dụng sau khi cắt hội thoại thành ứng viên mẫu bộ đánh giá.

Cần kiểm tra:

- `student_prompt`, `conversation_history`, `gold_response`/phản hồi tham chiếu có đúng thứ tự không;
- `Đáp án` có tách khỏi phản hồi gia sư mẫu không;
- nhiệm vụ chính có phù hợp với lượt gia sư mục tiêu không;
- tiêu chí chấm có quan sát được từ phản hồi của mô hình không;
- phản hồi tham chiếu chỉ là căn cứ chấm, không phải câu chữ bắt buộc;
- mẫu có truy vết về hội thoại thô và học liệu SGK không.

Ghi chú: trong bullet đầu, mình giữ tên trường tiếng Anh vì đây là tên trường kỹ thuật/phiếu dữ liệu đang được dùng.

Bằng chứng liên quan:

- KMP-Bench cắt hội thoại tại lượt gia sư và dùng lượt gia sư gốc làm phản hồi tham chiếu.
- TutorBench dùng phản hồi gia sư mẫu để viết tiêu chí chấm, không chấm bằng độ giống câu chữ.
- MathTutorBench dùng mô hình phần thưởng để chấm chất lượng sư phạm thay vì so khớp đáp án.

### Tầng 3 — Bộ đánh giá khi dùng thực nghiệm

Áp dụng sau khi có mẫu bộ đánh giá hoàn chỉnh.

Cần kiểm tra:

- bộ đánh giá có còn đủ khó không, tức mô hình không dễ đạt điểm trần;
- điểm có phân biệt gia sư tốt, trung bình và kém không;
- mô hình giỏi giải bài có bị phát hiện khi kém gợi mở hoặc kém sư phạm không;
- người rà soát có đồng thuận khi chấm một tập nhỏ không;
- bộ chấm tự động, nếu dùng, có khớp với chuyên gia con người không.

Bằng chứng liên quan:

- TutorBench không mô hình nào vượt 56%, chứng tỏ bộ đánh giá chưa bị bão hòa.
- MathTutorBench và KMP-Bench đều cho thấy năng lực giải bài không đồng nghĩa với năng lực gia sư.
- VietLegal dùng đánh giá mù đôi để chứng minh phản hồi của mô hình còn kém phản hồi của chuyên gia.

## 5. Những điểm cần đưa vào lộ trình hoặc kế hoạch tiếp theo

### 5.1. Rà soát tài liệu không nên dừng ở nhiệm vụ/tiêu chí chấm

Từ giờ cần tách hai câu hỏi:

- Bộ đánh giá gồm nhiệm vụ và tiêu chí chấm gì?
- Bộ đánh giá có tốt và đáng tin không?

Kế hoạch 01 trả lời câu hỏi thứ hai ở mức bằng chứng hạt giống.

### 5.2. Học liệu SGK cần thành hệ thống dùng chung

VietLegal cho thấy bộ đánh giá chất lượng cao cần nguồn chính thức và công cụ truy xuất cho người gán nhãn. Với dự án này, điều tương tự là:

- SGK/SGV Tin học THCS cần được OCR và chuẩn hóa;
- mỗi chủ đề, bài học và đoạn học liệu cần mã truy vết;
- giáo viên cần tra được mã học liệu khi tạo hoặc rà soát mẫu;
- về sau, mô hình khi được đánh giá có thể truy vấn nguồn thay vì trả lời không căn cứ.

### 5.3. Dữ liệu HNMU cần kiểm toán trước khi chuyển đổi

Dữ liệu hội thoại HNMU không nên được đưa thẳng vào bộ đánh giá. Cần bước kiểm toán:

- thiếu trường;
- tính nhất quán giữa thông tin phụ trợ và hội thoại;
- trùng/gần trùng;
- vùng thiếu hoặc lệch về độ phủ;
- hội thoại kém trình tự sư phạm hoặc lộ đáp án không phù hợp.

### 5.4. Không dùng bộ chấm tự động như chân lý ngay

TutorBench và KMP-Bench đều kiểm tra bộ chấm tự động với chuyên gia con người. VietLegal có Cohen’s Kappa rất rõ. Vì vậy, dự án không nên dùng bộ chấm tự động để chấm chính thức nếu chưa có tập hiệu chỉnh với HNMU/UET.

## 6. Tiêu chí có thể dùng ngay trong dự án


| Nhóm tiêu chí                                             | Có thể dùng ngay?        | Ghi chú                                                          |
| ------------------------------------------------------------ | --------------------------- | ----------------------------------------------------------------- |
| Độ phủ theo SGK/chủ đề/bài học                       | Có                         | Cần kế hoạch học liệu để có bản đồ đối chiếu.       |
| Độ phủ theo mức nhận thức                              | Có                         | Giữ 3 mức: Biết, Hiểu, Vận dụng.                            |
| Độ phủ theo dạng bài                                    | Có                         | Bắt đầu bằng nhóm lớn, mở rộng theo dữ liệu thật.      |
| Tính nhất quán giữa hội thoại và thông tin phụ trợ | Có                         | Rất phù hợp đợt dữ liệu 500 mẫu HNMU.                     |
| Trùng/gần trùng                                           | Có                         | Bắt buộc vì dữ liệu có AI hỗ trợ tạo.                    |
| Kiểm tra chéo bởi con người                             | Có, nhưng cần công sức | Nên làm trên một tập mẫu hoặc đợt dữ liệu quan trọng. |
| Độ đồng thuận giữa người chấm                       | Nên có                    | Có thể bắt đầu nhỏ trước khi mở rộng.                   |
| Độ khớp của bộ chấm tự động với người chấm      | Chưa dùng ngay            | Chỉ sau khi có nhãn của con người.                          |
| Đánh giá khả năng phân biệt gia sư tốt/kém         | Chưa dùng ngay            | Cần mẫu bộ đánh giá hoàn chỉnh.                           |

## 7. Những điểm không nên áp dụng máy móc

1. Không bê 22 tiêu chí của KMP-Bench hoặc 3–39 tiêu chí mỗi mẫu của TutorBench vào phiếu tác giả; quá nặng cho HNMU.
2. Không coi mức nhận thức là độ khó tuyến tính tuyệt đối; TutorBench cho thấy điểm mô hình không đi theo thứ tự Bloom đơn giản.
3. Không dùng mô hình phần thưởng hoặc bộ chấm tự động nếu chưa kiểm tra bằng người chấm tiếng Việt/Tin học.
4. Không suy ra kết quả học tập của học sinh từ chất lượng phản hồi trong bộ đánh giá; các bài báo không chứng minh điều đó.
5. Không lấy kết quả từ Toán/Luật để khẳng định trực tiếp cho Tin học THCS; phải qua HNMU xác nhận.

## 8. Đề xuất cập nhật cho các kế hoạch sau

- Kế hoạch 02 nên chốt `shared/raw_data/`, `shared/learning_resources/`, `src/` trước khi nhận đợt dữ liệu HNMU.
- Kế hoạch 03 nên coi VietLegal là bằng chứng cho cơ sở dữ liệu và hệ thống truy xuất học liệu.
- Kế hoạch 04 nên bổ sung rõ kiểm tra trùng/gần trùng và tính nhất quán giữa thông tin phụ trợ–hội thoại là bắt buộc.
- Kế hoạch 05 nên thiết kế đánh giá khả năng phân biệt bằng ít nhất ba nhóm phản hồi: tốt, trung bình, kém; có người chấm kiểm tra trước khi dùng bộ chấm tự động.

## 9. Câu hỏi mở cho Quân/giáo sư/HNMU

1. Với đợt dữ liệu 500 mẫu đầu tiên, UET có được loại tạm các mẫu trùng/gần trùng khỏi tập chuyển đổi thử không?
2. HNMU có thể kiểm tra chéo thông tin phụ trợ–hội thoại trên một tập nhỏ không, hay UET tự gắn cờ rồi gửi danh sách cần xác nhận?
3. Có cần đo độ đồng thuận giữa các thầy cô HNMU trên một tập nhỏ không?
4. Khi phản hồi tham chiếu từ HNMU chưa thật lý tưởng, UET có được tạo bản phản hồi gia sư mẫu đã chỉnh sửa không, hay chỉ được lưu phản hồi gốc và chờ HNMU duyệt?
5. Cơ sở dữ liệu học liệu nên ưu tiên SGK lớp 9 trước hay toàn bộ SGK Tin học THCS 6–9?

## 10. Output vận hành đã bổ sung ngày 14/07/2026

Sau khi HNMU gửi batch dữ liệu thô ban đầu, Plan 01 được bổ sung một output vận hành:

- `reports/benchmark-quality-checklist-v0.md`

Checklist này không thay thế báo cáo tổng hợp nghiên cứu. Vai trò của nó là biến các kết luận từ MathTutorBench, KMP-Bench, TutorBench và VietLegal/V-Legal thành các tiêu chí có thể dùng trong Plan 04 để kiểm dữ liệu HNMU.

Checklist phân biệt ba lớp kiểm tra:

1. Code kiểm phần cơ học: thiếu trường, định dạng, thống kê độ phủ, trùng/gần trùng.
2. Agent hỗ trợ kiểm phần ngữ nghĩa: câu hỏi–đáp án–hội thoại có khớp nhau không, hội thoại có giàn giáo không, mẫu có đủ giá trị sư phạm không.
3. HNMU/UET xác nhận phần chuyên môn hoặc phần agent không đủ tự tin.

Checklist cũng đề xuất các trường `quality_decision`, `confidence_score`, `failure_reasons`, `suggested_reviewer_action` và `needs_sgv_verification` để Plan 04 dùng khi tạo báo cáo kiểm toán batch HNMU.
