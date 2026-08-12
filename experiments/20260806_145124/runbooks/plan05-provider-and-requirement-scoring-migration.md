# Hướng dẫn vận hành — Kế hoạch 05 / Ranh giới nhà cung cấp mô hình và nghiệp vụ chấm mức độ bắt buộc

Thử nghiệm: `20260806_145124`
Kế hoạch: `P05`

## Mục đích

Kiểm chứng ranh giới mới giữa giao diện dòng lệnh, nghiệp vụ chấm mức độ bắt
buộc và hạ tầng gọi mô hình mà không gửi yêu cầu đến Vertex AI hoặc OpenAI.
Tài liệu này cũng ghi điểm vào thay thế cho không gian tên `vertex_ai_call` đã
bị loại bỏ.

## Điều kiện trước khi chạy

Dùng đúng Python của môi trường dự án:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python -m pip install -r requirements.txt
/home/quannda/miniconda3/envs/benchmark_env/bin/python -m pip install --no-deps -e .
```

Không đặt `--execute-api` trong bất kỳ phép kiểm chứng nào của tài liệu này.
Không cần ADC, `OPENAI_API_KEY` hoặc thông tin xác thực khác.

## Bảng điểm vào

| Nghiệp vụ | Điểm vào hiện hành |
|---|---|
| Chuẩn bị, chạy và hoàn tất phép chấm mức độ bắt buộc | `scripts/requirement_scoring/run_requirement_scoring.py` |
| Phân tích xác định trên lần chạy đầy đủ | `scripts/requirement_scoring/analyze_requirement_scoring.py` |
| Xuất mẫu ứng viên đủ điều kiện | `scripts/requirement_scoring/export_eligible_candidate_pool.py` |
| Giao diện Python của nghiệp vụ | `edu_benchmark.requirement_scoring` |
| Hợp đồng nhà cung cấp dùng chung | `edu_benchmark.model_providers` |

Ba tệp giao diện dòng lệnh chỉ khai báo tham số và điều phối. Logic nghiệp vụ
nằm dưới `src/edu_benchmark/requirement_scoring/`; phần kết nối SDK nằm dưới
`src/edu_benchmark/model_providers/`.

## Cấu hình requirement scoring

Giá trị riêng của lần chạy kế thừa từ experiment `20260727_170150` nằm tại:

```text
experiments/20260806_145124/configs/requirement-scoring-20260727-v1.yaml
```

Tệp này sở hữu experiment ID, đường dẫn, cấu hình provider/model, seed, bundle
name, giới hạn request, concurrency và chính sách retry. Các đường dẫn đều tính
từ repository root và loader dừng khi schema sai, đường dẫn thoát khỏi repository
hoặc có trường chứa thông tin xác thực. Mỗi lệnh thực thi phải truyền
`--config`; tham số được viết trực tiếp trên CLI được ưu tiên hơn giá trị YAML.

Ví dụ chỉ chuẩn bị manifest, không gọi model:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/requirement_scoring/run_requirement_scoring.py prepare \
  --config experiments/20260806_145124/configs/requirement-scoring-20260727-v1.yaml \
  --output-root /tmp/edu-benchmark-requirement-scoring-check
```

Manifest mới ghi `config_id`, đường dẫn tương đối và SHA-256 của config. Cấu
hình hiện hành đặt `include_thoughts: true` cho Gemini theo quyết định
P05-A003.

## Kiểm tra việc nhập gói

Chạy từ ngoài kho mã nguồn:

```bash
cd /tmp
/home/quannda/miniconda3/envs/benchmark_env/bin/python -I -c \
  "from edu_benchmark import model_providers, requirement_scoring; print(model_providers.__file__); print(requirement_scoring.__file__)"
```

Hai đường dẫn phải trỏ vào `src/edu_benchmark/`. Lệnh sau phải thất bại với
`ModuleNotFoundError`, vì không gian tên tạm đã bị loại bỏ có chủ đích:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python -I -c "import vertex_ai_call"
```

## Kiểm tra giao diện dòng lệnh mà không gọi mạng

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/requirement_scoring/run_requirement_scoring.py --help
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/requirement_scoring/analyze_requirement_scoring.py --help
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/requirement_scoring/export_eligible_candidate_pool.py --help
```

Các lệnh chạy mô hình vẫn có cổng an toàn: nếu thiếu `--execute-api`, quy trình
trả mã thoát `2` trước khi tạo yêu cầu gửi đến nhà cung cấp.

Workflow chỉ tự thử lại lỗi provider có `retryable=true` và phản hồi model
không đạt lược đồ nghiệp vụ. Lỗi provider có `retryable=false` cùng lỗi không
được phân loại sẽ dừng tại candidate tương ứng; response đã hoàn thành vẫn được
ghi tăng dần và có thể tiếp tục từ JSONL hiện có.

## Kiểm tra ngoại tuyến theo lát cắt

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python -m pytest -q \
  tests/model_providers \
  tests/requirement_scoring \
  tests/benchmark_evaluation/test_claude_judge_runner.py \
  tests/benchmark_evaluation/test_batch_judge.py \
  tests/benchmark_evaluation/test_openai_judge.py
```

Các phép kiểm thử dùng trình khách SDK hoặc nhà cung cấp giả lập để đối chiếu:

- chỉ dẫn hệ thống, thông điệp, mô hình và cấu hình sinh/suy luận;
- lược đồ JSON của đầu ra có cấu trúc;
- mã phản hồi, phiên bản mô hình, lý do kết thúc và mức sử dụng token;
- siêu dữ liệu về khả năng thử lại của lỗi kết nối;
- dữ liệu chỉ dẫn, mã băm yêu cầu, thứ tự mẫu ứng viên và lược đồ đầu ra của
  nghiệp vụ chấm mức độ bắt buộc.

## Kiểm tra toàn bộ kho mã nguồn

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python -m pytest -q
/home/quannda/miniconda3/envs/benchmark_env/bin/python -m pip check
/home/quannda/miniconda3/envs/benchmark_env/bin/python \
  scripts/governance/validate_experiment.py experiments/20260806_145124
git diff --check
```

## Cổng rà soát thành phần sử dụng

```bash
rg -n "from vertex_ai_call|import vertex_ai_call|src/vertex_ai_call" \
  src scripts tests pyproject.toml README.md ARCHITECTURE.md AGENTS.md \
  .github/workflows/offline-tests.yml
```

Lệnh không được trả kết quả. Tài liệu và bản ghi điều phối lịch sử vẫn có thể
nhắc tên cũ để giữ khả năng truy nguyên; chúng không phải lệnh nhập, gói hoặc
điểm vào đang hoạt động.

## Quay lui

Không có lớp tương thích song song. Nếu cần quay lui, dùng bản ghi hoặc lát cắt
Git trước Kế hoạch 05 cùng bảng ánh xạ trong
[`compatibility_matrix.csv`](../outputs/plan05/compatibility_matrix.csv). Không
chạy lại mô hình chỉ để quay lui việc cải tổ mã nguồn.
