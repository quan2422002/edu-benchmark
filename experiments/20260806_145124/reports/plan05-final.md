# Báo cáo cuối — Plan 05

Thử nghiệm: `20260806_145124`
Kế hoạch gốc: `plans/05-src-scripts-boundary-and-runtime-refactor.md`
Trạng thái kết luận: `completed`

## 1. Kết quả

Plan 05 đã tách ba trách nhiệm trước đây bị trộn lẫn:

- [`model_providers`](../../../src/edu_benchmark/model_providers/__init__.py)
  sở hữu hợp đồng trung gian cho yêu cầu, phản hồi và lỗi; bộ đăng ký; cùng kết
  nối đến bộ công cụ phát triển phần mềm (SDK);
- [`requirement_scoring`](../../../src/edu_benchmark/requirement_scoring/__init__.py)
  sở hữu dữ liệu chỉ dẫn, mã băm yêu cầu, phép chấm, phân tích và xuất dữ liệu;
- [`scripts/requirement_scoring`](../../../scripts/requirement_scoring/run_requirement_scoring.py)
  sở hữu `argparse`, nội dung trợ giúp và việc điều phối lệnh.

`model_providers` nằm trực tiếp dưới `src/edu_benchmark/`, cùng cấp với các gói
nghiệp vụ. Gói này không nhập `requirement_scoring` hoặc `benchmark_evaluation`, không đọc sản phẩm của thử nghiệm và không biết bảng tiêu chí, nguyên tắc sư phạm hoặc mẫu ứng viên. Phần cài đặt hiện hành gồm[`VertexAIProvider`](../../../src/edu_benchmark/model_providers/vertex_ai/provider.py) và [`OpenAIProvider`](../../../src/edu_benchmark/model_providers/openai/provider.py).
Bộ đăng ký chỉ tải nhà cung cấp khi có yêu cầu, nên việc nhập gói lõi không kéo
theo các SDK tùy chọn.

Không gian tên tạm `vertex_ai_call` đã được gỡ khỏi thông tin đóng gói, mã
nguồn, phép kiểm thử, quy trình tích hợp liên tục (CI) và tài liệu đang hoạt
động. Phép nhập từ ngoài kho mã nguồn xác nhận hai không gian tên mới có hiệu
lực; `import vertex_ai_call` trả về `ModuleNotFoundError`.

## 2. Ranh giới đã cài đặt

Hợp đồng tại
[`contracts.py`](../../../src/edu_benchmark/model_providers/contracts.py) nhận:

- `backend`, tên mô hình, chỉ dẫn hệ thống và chuỗi thông điệp;
- giới hạn token đầu ra, tham số lấy mẫu, hạt giống, thời gian chờ và cấu hình
  suy luận (`thinking` hoặc `reasoning`);
- tên/lược đồ của đầu ra có cấu trúc và tùy chọn riêng của nhà cung cấp được
  hợp đồng cho phép.

Kết quả chuẩn hóa gồm nội dung văn bản, nền tảng thực thi, tên và phiên bản mô
hình, mã phản hồi, lý do kết thúc, mức sử dụng token và siêu dữ liệu của nhà
cung cấp. Lỗi kỹ thuật ghi nền tảng thực thi, mã trạng thái HTTP, khả năng thử
lại và nội dung phản hồi lỗi khi có.

`GenerationConfig` lịch sử được giữ về cấu trúc để duy trì hợp đồng tệp kê khai
và cách tính mã băm. Cấu hình này hiện có hai góc nhìn tách biệt:
`ModelGenerationPolicy` dành cho một yêu cầu mô hình và `RunExecutionPolicy`
dành cho chính sách thử lại, mức đồng thời cùng giới hạn số yêu cầu. Bộ chuyển
đổi của nghiệp vụ chấm mức độ bắt buộc chỉ nhận góc nhìn thứ nhất; quy trình
nghiệp vụ sở hữu góc nhìn thứ hai.

Sau P05-A003, các giá trị riêng của lần chạy không còn nằm trong package nghiệp
vụ. Tệp
[`requirement-scoring-20260727-v1.yaml`](../configs/requirement-scoring-20260727-v1.yaml)
sở hữu experiment ID, đường dẫn, model, seed, bundle name, concurrency và giới
hạn request. Ba CLI bắt buộc nhận `--config` và vẫn cho phép override tường minh.
Manifest lần chạy mới ghi ID, đường dẫn tương đối cùng SHA-256 của config.
Giá trị `include_thoughts=true` được duyệt tại P05-A003 nên request hash mới có
thể khác output lịch sử dùng `false`; thay đổi này được ghi công khai, không bị
trình bày như một phép tương đương bit-for-bit.

## 3. Thành phần sử dụng đại diện


| Luồng                     | Trước Kế hoạch 05                                                                             | Sau Kế hoạch 05                                                                     |
| -------------------------- | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| Chấm mức độ bắt buộc | Bộ gọi Vertex mang tên tác vụ và nhập ngược cấu hình nghiệp vụ                       | `RequirementScoringModelClient` tạo `ModelRequest`, sau đó gọi `VertexAIProvider` |
| Bộ chấm Gemini           | `GeminiVertexJudgeCaller` tự tạo trình khách SDK, ánh xạ yêu cầu, lỗi và mức sử dụng | Thành phần gọi chỉ tạo lược đồ nghiệp vụ và gọi`VertexAIProvider`        |
| Bộ chấm OpenAI           | `OpenAIJudgeCaller` tự gọi Responses API và chuẩn hóa kết nối                              | Thành phần gọi chỉ tạo lược đồ nghiệp vụ và gọi`OpenAIProvider`          |

Các giao diện công khai của hai bộ chấm giữ nguyên tham số và cấu trúc kết quả.
Quy trình chấm theo lô dùng hàm chuẩn hóa lý do kết thúc từ phần Vertex dùng
chung; logic theo lô và bảng tiêu chí vẫn thuộc gói nghiệp vụ.

P05-A003 đặt `include_thoughts=true` nhất quán cho requirement scoring, target
generation, bộ chấm Gemini đồng bộ và bộ chấm Gemini theo lô. Đây là thay đổi
được người phụ trách dự án yêu cầu sau refactor; bảng tương thích và phép kiểm
thử khóa giá trị mới thay vì tuyên bố giữ nguyên payload `false` trước đây.

Workflow requirement scoring nay dùng phân loại `ProviderCallError.retryable`.
Lỗi provider có thể thử lại và phản hồi model không đạt lược đồ được đưa vào
retry sweep; lỗi provider không thể thử lại cùng lỗi chưa phân loại dừng ngay ở
candidate tương ứng. Mỗi bản ghi lỗi nêu rõ quyết định `retryable`.

## 4. Giao diện dòng lệnh và ánh xạ đường dẫn


| Đường dẫn cũ                                      | Đường dẫn hiện hành                                                                                                                 |
| ------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `src/vertex_ai_call/run_requirement_scoring.py`        | [`scripts/requirement_scoring/run_requirement_scoring.py`](../../../scripts/requirement_scoring/run_requirement_scoring.py)               |
| `src/vertex_ai_call/analyze_requirement_scoring.py`    | [`scripts/requirement_scoring/analyze_requirement_scoring.py`](../../../scripts/requirement_scoring/analyze_requirement_scoring.py)       |
| `src/vertex_ai_call/export_eligible_candidate_pool.py` | [`scripts/requirement_scoring/export_eligible_candidate_pool.py`](../../../scripts/requirement_scoring/export_eligible_candidate_pool.py) |
| `src/vertex_ai_call/requirement_scoring.py`            | [`src/edu_benchmark/requirement_scoring/core.py`](../../../src/edu_benchmark/requirement_scoring/core.py)                                 |
| `src/vertex_ai_call/vertex_client.py`                  | [`src/edu_benchmark/model_providers/vertex_ai/provider.py`](../../../src/edu_benchmark/model_providers/vertex_ai/provider.py)             |

Ba giao diện dòng lệnh (CLI) mới lần lượt có 140, 60 và 51 dòng. Toàn bộ
`argparse` của lát cắt này nằm trong `scripts/`; các hàm nghiệp vụ có thể được
nhập và kiểm thử trực tiếp.

## 5. Tính tương thích và thay đổi phụ thuộc

[`compatibility_matrix.csv`](../outputs/plan05/compatibility_matrix.csv) ghi các
cổng kiểm tra cho việc nhập gói, mã băm, lược đồ và thứ tự của nghiệp vụ chấm
mức độ bắt buộc; yêu cầu gửi đến SDK Vertex/OpenAI; đầu ra của bộ chấm; cùng
giao diện dòng lệnh. Chỉ dẫn, bảng tiêu chí, mẫu ứng viên, mẫu dữ liệu và kết
quả khoa học không bị sửa;
không có API trả phí nào được gọi.

P05-A001 cũng xử lý trở ngại đóng gói còn lại từ Kế hoạch 04:
`requirements.txt` và `pyproject.toml` cùng dùng `PyYAML==6.0.2`. Đây là phiên
bản cố định vốn đã được khai báo trong gói và phù hợp với phụ thuộc trong
`benchmark_env`; phép đối chiếu toàn bộ phụ thuộc trực tiếp cùng `pip check`
đều đạt.

## 6. Kiểm chứng

- Trình thông dịch:
  `/home/quannda/miniconda3/envs/benchmark_env/bin/python`.
- Phép kiểm thử mục tiêu cho cấu hình, provider, retry và các đường Gemini:
  `62 passed`.
- Toàn bộ kho mã nguồn sau P05-A003: `302 passed`.
- Bộ kiểm tra quản trị thử nghiệm: `passed`.
- `pip check`: `No broken requirements found`.
- Ba lệnh CLI `--help`: mã thoát `0`, không cần thông tin xác thực.
- Loader config từ chối repository escape; package nghiệp vụ không còn chứa ID
  hoặc đường dẫn gắn cứng với experiment `20260727_170150`.
- Quét đường nhập và đường dẫn đang hoạt động của `vertex_ai_call`: không có
  kết quả.
- Phép nhập cô lập từ `/tmp`: hai gói mới trỏ về `src/edu_benchmark/`; không
  gian tên cũ không nhập được.
- Quét chiều phụ thuộc của nhà cung cấp và `git diff --check`: `passed`.
- Không gọi API Vertex AI/OpenAI và không thay đổi nội dung bộ chuẩn đánh giá.

## 7. Sản phẩm quản trị

- [Bảng kê mô-đun](../outputs/plan05/module_inventory.csv)
- [Các cạnh phụ thuộc](../outputs/plan05/dependency_edges.csv)
- [Bảng tương thích](../outputs/plan05/compatibility_matrix.csv)
- [Nhật ký điều chỉnh P05-A001 và P05-A002](../decisions/plan05-amendments.md)
- [Hướng dẫn vận hành](../runbooks/plan05-provider-and-requirement-scoring-migration.md)

## 8. Giới hạn và phần việc còn lại

- Kế hoạch 05 chỉ chuyển nghiệp vụ chấm mức độ bắt buộc cùng hai thành phần gọi
  bộ chấm đồng bộ đại diện. Các API theo lô, điểm cuối tùy chỉnh, trình chạy sinh phản
  hồi lớn và tệp bọc lệnh lịch sử được phân loại nhưng không bị chuyển hàng
  loạt.
- Bộ đăng ký đã có điểm mở rộng nhưng chưa cài Kaggle, Ollama hoặc vLLM.
- Tài liệu và bản ghi điều phối lịch sử vẫn nhắc `vertex_ai_call` để giữ khả
  năng truy nguyên; chúng không phải phụ thuộc đang hoạt động.
- `model_providers` hiện cung cấp hợp đồng đồng bộ. Hợp đồng theo lô hoặc bất
  đồng bộ có thể được bổ sung khi một kế hoạch sau xác định nhu cầu thực tế;
  không ép chúng vào API đồng bộ hiện tại.

## 9. Cổng tiếp theo

Kế hoạch 05 hoàn tất. Kế hoạch 06 có thể được người phụ trách dự án đọc và
duyệt; trạng thái này không tự động phê duyệt việc lưu giữ, khử trùng lặp hoặc
xóa sản phẩm đầu ra.
