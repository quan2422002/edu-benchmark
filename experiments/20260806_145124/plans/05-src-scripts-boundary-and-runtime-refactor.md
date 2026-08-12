# Plan 05 — Tách ranh giới `src/`, `scripts/` và tầng nhà cung cấp mô hình

Experiment: `20260806_145124`
Trạng thái: `APPROVED — NGƯỜI PHỤ TRÁCH DỰ ÁN DUYỆT NGÀY 2026-08-10`
Phụ thuộc: Plan 01–04 đã hoàn tất

## 1. Mục tiêu

Loại bỏ sự nhập nhằng chức năng giữa `src/` và `scripts/`, đồng thời tách rõ:

- phần xử lý nghiệp vụ của từng quy trình, chẳng hạn chấm mức độ bắt buộc của nguyên tắc sư phạm hoặc đánh giá phản hồi gia sư;
- kết nối kỹ thuật đến nhà cung cấp mô hình như Vertex AI và OpenAI;
- giao diện dòng lệnh dùng để vận hành một tác vụ cụ thể.

Thư viện phải có thể được kiểm thử và tái sử dụng trực tiếp. Tệp lệnh chỉ đọc tham số, gọi thư viện và trả trạng thái cho người vận hành.

## 2. Ranh giới trách nhiệm đích

`src/edu_benchmark/` chứa:

- kiểu dữ liệu nghiệp vụ, lược đồ và bộ kiểm tra;
- phép biến đổi, chấm điểm, tổng hợp và phân tích;
- giao diện cùng bộ chuyển đổi dùng chung cho nhà cung cấp mô hình;
- chính sách lưu kết quả, thử lại, tiếp tục và ngân sách có thể tái sử dụng;
- phần đọc cấu hình và xác định đường dẫn không gắn cứng với một thử nghiệm.

`scripts/` chứa:

- khai báo tham số `argparse`, nội dung trợ giúp và lựa chọn lệnh con;
- đọc cấu hình, gọi đúng hàm trong thư viện và ánh xạ mã thoát;
- thông báo tiến độ ở cấp câu lệnh.

`experiments/<id>/configs/` và `runbooks/` chứa giá trị riêng của từng lần chạy cùng câu lệnh vận hành. Chúng không chứa phần xử lý nghiệp vụ.

Tệp trong `scripts/` không được giữ chỉ dẫn (`prompt`), thuật toán, vòng đời nhà cung cấp phức tạp, đường dẫn tuyệt đối hoặc mã thử nghiệm. Khoảng 100–150 dòng chỉ là mốc tham khảo cho một CLI mới; tính tập trung trách nhiệm và khả năng kiểm thử quan trọng hơn giới hạn số dòng cơ học.

## 3. Tách tầng nghiệp vụ và tầng nhà cung cấp mô hình

Vertex AI, OpenAI và các dịch vụ tương tự là hạ tầng dùng chung. Chúng không thuộc riêng quy trình chấm mức độ bắt buộc (`requirement scoring`), sinh phản hồi (`target generation`) hoặc chấm phản hồi (`judging`).

`model_providers/` là một gói hạ tầng độc lập nằm trực tiếp dưới
`src/edu_benchmark/`. Nó cùng cấp với các gói nghiệp vụ, không nằm trong
`benchmark_evaluation/` hoặc `requirement_scoring/`.

Kiến trúc đích:

```text
src/edu_benchmark/
  model_providers/               hạ tầng gọi mô hình độc lập
    contracts.py                 kiểu yêu cầu/phản hồi trung gian
    registry.py                  chọn nền tảng thực thi theo cấu hình
    vertex_ai/                   Vertex AI
    openai/                      OpenAI API
    <nền tảng tương lai>/        Kaggle, Ollama, vLLM, ...
  requirement_scoring/           nghiệp vụ chấm mức độ bắt buộc
  benchmark_evaluation/          nghiệp vụ sinh và chấm phản hồi
  <quy trình nghiệp vụ tương lai>/

scripts/
  <tệp lệnh mỏng> ──> <gói nghiệp vụ> ──> model_providers/
```

Gói nghiệp vụ truyền một yêu cầu trung gian vào `model_providers`, tối
thiểu gồm:

- nền tảng thực thi (`backend`), vì một tên mô hình có thể được cung cấp qua
  nhiều nền tảng;
- tên mô hình;
- chỉ dẫn hệ thống (`system prompt`) và chuỗi thông điệp gồm prompt cùng lịch sử
  hội thoại (`conversation history`);
- cấu hình sinh, cấu hình suy luận và giới hạn token;
- định dạng hoặc lược đồ phản hồi khi có áp dụng;
- tham số riêng của nền tảng được hợp đồng cho phép.

Kết quả trả về chỉ chứa nội dung hoặc dữ liệu có cấu trúc, lý do kết thúc, mức
sử dụng token, định danh mô hình/nền tảng và lỗi kỹ thuật đã chuẩn hóa. Gói này
không biết yêu cầu được dùng để chấm nguyên tắc, sinh phản hồi hay làm bộ chấm.

`model_providers/` không `import` gói nghiệp vụ, không đọc sản phẩm benchmark và
không chứa mã thử nghiệm. Các nền tảng Kaggle, Ollama và vLLM là điểm mở rộng
tương lai; Plan 05 chỉ cài phần cần cho Vertex AI, OpenAI và các thành phần sử
dụng hiện có, không tự mở rộng sang việc triển khai mọi nền tảng.

Tầng nhà cung cấp mô hình chịu trách nhiệm cho:

- tạo và đóng SDK client;
- nhận thông tin xác thực từ cơ chế bên ngoài như ADC hoặc biến môi trường;
- ánh xạ yêu cầu trung gian sang định dạng đặc thù của từng nhà cung cấp;
- gửi yêu cầu đồng bộ hoặc theo lô;
- chuẩn hóa thông tin truy vết của phản hồi, mức sử dụng, lý do kết thúc và lỗi vận chuyển;
- phân loại lỗi kỹ thuật có thể thử lại ở cấp nhà cung cấp.

Tầng này không sở hữu prompt, rubric, nguyên tắc sư phạm, lược đồ kết quả nghiệp vụ, lựa chọn mẫu ứng viên, cách tính điểm hoặc quyết định ngân sách của một thử nghiệm. Nó cũng không được `import` ngược từ `requirement_scoring/` hoặc `benchmark_evaluation/`.

Tầng quy trình nghiệp vụ chịu trách nhiệm cho:

- tạo prompt và dữ liệu yêu cầu có ý nghĩa nghiệp vụ;
- kiểm tra phản hồi theo lược đồ của tác vụ;
- quản lý ID, thứ tự mẫu ứng viên, phép ghép dữ liệu và trạng thái hoàn tất;
- quyết định khi nào thử lại, tiếp tục hoặc dừng vì ngân sách;
- tạo tệp kê khai và sản phẩm mang ý nghĩa khoa học của quy trình.

Chiều phụ thuộc chỉ được đi từ quy trình nghiệp vụ đến giao diện nhà cung cấp,
không đi theo chiều ngược lại.

## 4. Các phần chuyển đổi ưu tiên

### 4.1. Tách `src/vertex_ai_call/`

Không chuyển nguyên thư mục này vào `requirement_scoring/`.

- Phần xử lý chấm mức độ bắt buộc, phân tích và xuất tập đủ điều kiện được chuyển vào `src/edu_benchmark/requirement_scoring/`.
- Phần xác thực ADC, tạo Google Gen AI SDK client, gửi yêu cầu và chuẩn hóa thông tin truy vết Vertex AI được chuyển vào tầng nhà cung cấp dùng chung.
- `GenerationConfig` hiện chứa cả chính sách nghiệp vụ và tham số đặc thù của Vertex AI; bước kiểm kê phải tách hai nhóm trước khi di chuyển.
- `VertexRequirementClient` hiện `import` trực tiếp từ requirement scoring và mang tên theo một tác vụ. Nó phải được thay bằng giao diện trung lập với tác vụ; phần đóng gói prompt/lược đồ riêng vẫn nằm ở requirement scoring.
- Namespace `vertex_ai_call` chỉ được giữ làm lớp chuyển tiếp trong giai đoạn
  đầu của Plan 05, không phải thành phần tương thích lâu dài.
- Sau khi `model_providers/`, `requirement_scoring/` và các thành phần sử dụng đại diện đã
  đạt kiểm thử ngoại tuyến, mọi import và cấu hình đóng gói phải chuyển sang
  không gian tên mới; `src/vertex_ai_call/` sau đó được loại bỏ hoàn toàn trước cổng
  hoàn tất Plan 05.
- Việc loại bỏ chỉ diễn ra sau khi bản rà soát thành phần sử dụng xác nhận không còn mã nguồn,
  phép kiểm thử, tệp lệnh hoặc tài liệu đang hoạt động phụ thuộc không gian tên cũ. Nếu cổng
  này chưa đạt, Plan 05 phải dừng ở trạng thái chưa hoàn tất thay vì giữ lớp chuyển tiếp vô
  thời hạn.

### 4.2. Chuẩn hóa kết nối nhà cung cấp trong benchmark evaluation

- Kiểm kê các phần Vertex/OpenAI đang nằm trong `provider_adapters.py`, `gemini_judge.py`, `claude_judge.py`, `openai_judge.py`, `batch_judge.py`, `vertex_endpoint.py` và các trình chạy tương ứng.
- Chỉ đưa phần thực sự độc lập với tác vụ vào tầng nhà cung cấp dùng chung.
- Phần phân tích rubric, phán quyết cặp, tạo yêu cầu chấm hoặc xử lý mẫu ứng viên vẫn thuộc `benchmark_evaluation/`.
- Ít nhất một đường gọi đại diện của requirement scoring và một đường gọi đại diện của benchmark evaluation phải dùng cùng ranh giới nhà cung cấp mới trong kiểm thử ngoại tuyến. Không gọi API trả phí để chứng minh chuyển đổi.

### 4.3. Làm mỏng các tệp lệnh đang hoạt động

- Tách phần xử lý nghiệp vụ còn nằm trong trình chạy lớn về gói phù hợp.
- Tệp lệnh chỉ đọc CLI/cấu hình, gọi dịch vụ nghiệp vụ và ánh xạ tiến độ hoặc mã thoát.
- Giữ tệp bọc lệnh tương thích cho những câu lệnh đã được runbook hoặc người dùng gọi; chưa xóa trong Plan 05.

## 5. Các bước triển khai dự kiến

1. Lập bản kiểm kê tệp, số dòng, đồ thị `import`/lời gọi, câu lệnh và thành phần sử dụng của các đường requirement scoring, target generation và judging đang hoạt động.
2. Phân loại từng hàm hoặc lớp thành: nghiệp vụ, nhà cung cấp dùng chung, điều phối CLI, riêng thử nghiệm hoặc chỉ dùng cho lịch sử.
3. Chốt giao diện nhà cung cấp, giao diện công khai của từng quy trình và bảng tương thích trước khi di chuyển mã nguồn.
4. Tách kết nối Vertex AI dùng chung khỏi requirement scoring; dùng lớp chuyển
   tiếp import ngắn hạn và kiểm thử bằng SDK client giả lập.
5. Chuyển phần xử lý requirement scoring về không gian tên nghiệp vụ mới mà không thay đổi prompt, mã băm yêu cầu, thứ tự mẫu ứng viên hoặc lược đồ đầu ra.
6. Kết nối một lát cắt đại diện của benchmark evaluation qua cùng ranh giới nhà cung cấp và đối chiếu yêu cầu/phản hồi ngoại tuyến.
7. Làm mỏng CLI theo từng lát cắt; kiểm thử trước và sau mỗi lần chuyển.
8. Chuyển runbook/cấu hình sang điểm vào mới khi điểm vào đó đã ổn định.
9. Chuyển toàn bộ thành phần sử dụng khỏi `vertex_ai_call`, bỏ không gian tên này
   khỏi cấu hình đóng gói rồi loại bỏ thư mục sau khi rà soát thành phần sử dụng đạt.
10. Cập nhật kiến trúc và bản đồ trách nhiệm sau khi mã nguồn thực tế đạt kiểm thử.

## 6. Phạm vi được phép sửa sau khi plan được duyệt

- `src/edu_benchmark/requirement_scoring/`;
- không gian tên của tầng nhà cung cấp mới dưới `src/edu_benchmark/`;
- phần được chọn trong `src/edu_benchmark/benchmark_evaluation/`;
- `src/vertex_ai_call/` để tạo lớp chuyển tiếp ngắn hạn rồi loại bỏ sau cổng rà
  soát thành phần sử dụng;
- các tệp lệnh được bản kiểm kê xác nhận thuộc lát cắt chuyển đổi;
- phép kiểm thử, cấu hình đóng gói, cấu hình vận hành, runbook và tài liệu trực tiếp liên quan;
- sản phẩm quản trị của Plan 05.

Plan 05 không cho phép:

- xóa tệp bọc lệnh lịch sử không liên quan; việc loại bỏ không gian tên
  `src/vertex_ai_call/` là mục tiêu riêng đã nêu rõ và chỉ được thực hiện sau
  cổng rà soát thành phần sử dụng;
- gọi API trả phí;
- thay prompt, rubric, nhãn, sample hoặc kết quả khoa học;
- chuyển toàn bộ mã nguồn nhà cung cấp vào một gói nghiệp vụ;
- sửa mọi trình chạy trong repository bằng một lần di chuyển hàng loạt.

## 7. Tiêu chí nghiệm thu

- `model_providers/` nằm cùng cấp với các gói nghiệp vụ và không có gói
  nhà cung cấp nào `import` từ gói nghiệp vụ hoặc thử nghiệm.
- Phần xử lý requirement scoring có thể gọi trực tiếp qua
  `edu_benchmark.requirement_scoring` mà không chạy tiến trình con.
- Giao diện dùng chung nhận nền tảng, tên mô hình, prompt/chuỗi thông điệp và cấu hình sinh
  hoặc suy luận mà không chứa tên, prompt hay lược đồ dành riêng cho requirement
  scoring hoặc judging.
- Một bộ dữ liệu kiểm thử requirement scoring và một bộ dữ liệu kiểm thử benchmark evaluation đi qua cùng giao diện nhà cung cấp bằng SDK client giả lập, không có kết nối mạng.
- CLI đại diện chủ yếu đọc tham số và điều phối; phần xử lý nghiệp vụ được kiểm thử trực tiếp trong gói.
- Trong giai đoạn chuyển tiếp, đường import/câu lệnh cũ chuyển tiếp đúng sang
  phần cài đặt mới; tại cổng cuối không còn `import`, gói hoặc kiểm thử nào
  phụ thuộc `vertex_ai_call`.
- Kiểm thử tương đương ngoại tuyến giữ nguyên thứ tự mẫu ứng viên, mã băm yêu cầu, dữ liệu yêu cầu gốc của nhà cung cấp, lược đồ đầu ra và chỉ số của bộ dữ liệu kiểm thử đại diện.
- Không có prompt hoặc cấu hình riêng của thử nghiệm bị sao chép thành hằng số trong mã nguồn.
- Trách nhiệm của mô-đun đang hoạt động được cập nhật trong `ARCHITECTURE.md`.

## 8. Rủi ro và cách quay lui

- Một lớp hiện tại có thể trộn trách nhiệm nhà cung cấp và nghiệp vụ; di chuyển nguyên tệp sẽ chỉ đổi vị trí của vấn đề. Vì vậy phải tách ở cấp hàm/lớp dựa trên đồ thị import/lời gọi.
- Hai quy trình có thể dùng cùng nhà cung cấp nhưng khác kiểu API, chẳng hạn Google Gen AI SDK, Vertex partner MaaS hoặc endpoint tùy chỉnh. Giao diện chung chỉ chuẩn hóa phần thực sự chung; không ép chúng vào một dữ liệu yêu cầu giả tạo.
- Việc đổi `import` có thể phá notebook hoặc câu lệnh cá nhân chưa được đăng ký. Không gian tên cũ được giữ làm lớp chuyển tiếp trong cửa sổ tương thích và bản rà soát thành phần sử dụng ghi rõ trường hợp chưa chuyển.
- Không gian tên cũ không được trở thành giải pháp quay lui lâu dài. Trước khi loại
  bỏ, phải lưu bảng ánh xạ import/câu lệnh cũ–mới và kết quả kiểm thử tương
  đương; việc quay lui dùng commit hoặc lát cắt trước đó thay vì duy trì hai
  phần cài đặt song song.
- Nếu phép đối chiếu mã băm yêu cầu, thứ tự hoặc lược đồ thất bại, lát cắt mới không trở thành điểm vào chính; tệp bọc lệnh cũ tiếp tục là đường quay lui.

## 9. Các quyết định cần người phụ trách dự án duyệt

- Xác nhận tên không gian tên nhà cung cấp dùng chung:
  `edu_benchmark.model_providers`.
- Lát cắt benchmark evaluation nào sẽ là thành phần sử dụng đại diện đầu tiên của tầng nhà cung cấp mới.
- Tên CLI công khai và thời điểm chuyển từ lớp `vertex_ai_call` tạm thời sang
  việc loại bỏ hoàn toàn trong Plan 05.
- Thành phần lịch sử nào chỉ cần phân loại và ghi tài liệu, thành phần nào phải  được chuyển đổi thật trong Plan 05.
