# Vietnamese Lower-Secondary Informatics Tutor Benchmark

This repository is building a human-in-the-loop benchmark for evaluating how well large language models tutor Vietnamese lower-secondary Informatics students in grades 6–9.

## Quy ước tài liệu rà soát cho con người

- Tài liệu cần Quân, giáo viên, người rà soát hoặc người phân xử trực tiếp điền
  quyết định phải dùng workbook Excel (`.xlsx`) làm giao diện chính, trừ khi
  người dùng yêu cầu rõ một định dạng khác.
- CSV, JSON và JSONL chỉ là dữ liệu máy hoặc dữ liệu truy vết; không giao chúng
  như tài liệu rà soát duy nhất.
- Mỗi sheet chỉ hiển thị số cột tối thiểu cần cho một nhiệm vụ. Các trường kỹ
  thuật, mã băm, cấu hình mô hình và metadata không phục vụ quyết định phải để
  ngoài phiếu; mỗi dòng chỉ cần giữ một mã ổn định để nối lại dữ liệu máy.
- Phiếu phải có hướng dẫn tiếng Việt, đánh dấu rõ ô cần điền, cố định tiêu đề,
  ngắt dòng nội dung dài, bộ lọc và danh sách chọn khi nhãn là tập đóng. Trước
  khi bàn giao, mã sinh phiếu phải mở lại workbook và kiểm tra sheet, số dòng,
  mã mẫu cùng các ô lựa chọn.

## Current status

Experiment `20260903_135547` Plan 04 đã được Quân xác nhận hoàn thành
cho phạm vi hiện tại. Hai workbook lớp 6/lớp 8 bao
phủ 517 mẫu và 9.306 kết quả tiêu chí; cổng chỉ đọc tại
`http://127.0.0.1:8765` kiểm kê đủ 5.411 fragment, 2.130 tham chiếu ảnh và 11
PDF dẫn xuất. Mã nằm trong `src/edu_benchmark/review_delivery/`, CLI mỏng nằm
trong `scripts/review_delivery/`, còn config/runbook/output nằm trong experiment.
P04-A004 đã bổ sung một config riêng cho lượt thử HTTP trực tiếp
`0.0.0.0:8765`; URL dự kiến là `http://<IP-công-cộng>:8765` sau khi
Quân khởi động server và port-forward router. Config localhost không đổi.
Đây không phải deployment ổn định; phân phối chính thức cho HNMU
và publication vào `shared` vẫn chưa được mở.
Báo cáo kết thúc Plan 04 kiêm kiểm kê code toàn experiment nằm tại
`experiments/20260903_135547/reports/plan04-final-and-experiment-code-inventory.md`.
Toàn experiment chưa đóng vì Plan 03 vẫn `in_progress`.

Dự án đang ở giai đoạn proof-of-concept nhằm xây dựng benchmark gia sư AI môn Tin học THCS lớp 6–9. Experiment cải tổ repository `20260806_145124` đã hoàn thành Plan 01–07: quản trị kế hoạch, đóng gói Python, kho sản phẩm benchmark dùng chung, runtime khả chuyển, ranh giới model provider, chính sách lưu giữ và kiểm chứng snapshot sạch đều đã đạt. P06-A001 giữ payload tại ngữ cảnh experiment gốc, dùng `.gitignore` có mục tiêu cho 45 JSONL và không dùng Git LFS. Experiment `20260817_160800` đã sinh deterministic bộ PL-REQ v1 gồm 60 candidate chính cân bằng 15/lớp và 8 reserve; đây là tập hiệu chỉnh vận hành, chưa phải ground truth và còn chờ Nguyên cùng người chấm sư phạm rà soát. Experiment `20260829_175101` Plan 03 đã publish bundle `v2` vào `shared`: 154 SGK/SGV unit và 55 SBT unit theo bài/mục lục đều dùng `images/`, manifest active có 209 row, còn fragment/index giữ đúng 2.750 fragment SGK/SGV và zero SBT fragment/FTS row. Cả 53 Markdown bài SBT có nhãn riêng cho đề bài/hướng dẫn giải mà không đổi OCR source span; hai transaction E1/E2 đều có backup và hậu kiểm hash. Experiment benchmark `20260727_170150` vẫn là nguồn hiện trạng khoa học: đã khóa 1.400 candidate ưu tiên, sinh đủ 1.400 response cho ba target và hoàn thành full judge `gold-answer-only-v4` bằng Gemini cùng GPT, mỗi judge có đúng 4.200 phán quyết hợp lệ. Rubric, score model, instruction và phán quyết của model vẫn là kết quả tạm thời, chưa phải ground truth hoặc nội dung HNMU đã xác nhận. Bản thảo KSE nằm tại `kse_submit_manuscript/`.

Experiment `20260902_082403` đã hoàn thành Plan 01 cho local Ollama: 28 kiểm thử
đạt; service do Quân quản lý chạy Ollama `0.32.14` với Qwen3.8-27B Q4_K_M,
context 4096 và 100% GPU; live `OllamaProvider` probe đạt mà không lưu thinking
text. Plan 02 đã hoàn thành trên baseline tuần tự 30/30 với zero lỗi/review/
truncation, hash nguồn hợp lệ và GPU metric đủ; Quân đã review tối thiểu 10 mẫu
và chấp nhận ETA full khoảng 22,34 giờ hay 26,81 giờ có dự phòng cùng peak
87°C. P02-A007 hủy nhánh concurrency-2 vì Ollama `0.32.14` ép kiến trúc
`qwen35` về một slot; bundle chẩn đoán vẫn 0/30. Provider-neutral runner,
single-writer persistence, `tqdm` ETA và log vẫn được giữ. Plan 03 đã hoàn tất
bundle Qwen3.8 đúng 1.400 unique response `completed/STOP`: full run đầu đạt
1.397, P03-A001 recovery cap 3.072 đạt 3/3, rồi merge fail-closed có provenance
và backup. Bundle đã sẵn sàng làm target input cho workflow LLM judge riêng.
P03-A002 đã cài helper one-off để chuẩn hóa lossless 1.400 output Qwen3.8 BF16
nhập ngoài; preflight target/judge đều đạt 1.400 nhưng output chuẩn hóa chưa được
ghi cho đến khi Quân chủ động chạy `--execute`. Các provenance runtime chưa có
bằng chứng vẫn được ghi là unknown và file BF16 nguồn không bị sửa.

Experiment `20260904_093529` Plan 01 đã hoàn thành lớp Batch judge khả chuyển
cho target Qwen3.8: runner nhận experiment/plan/output root và cardinality động,
giữ tương thích nhánh 1.400 × ba target lịch sử, đồng thời preflight offline
đúng 30 và 1.400 comparison cho riêng Qwen trên cả Gemini 3.5 Flash và
GPT-5.4-mini. Prompt v4 được khóa bằng snapshot đúng hash lịch sử mà không sửa
file `shared` đang có thay đổi. Chưa tạo bucket hoặc gọi provider; cost-pilot 30
và full judge vẫn cần Plan 02/03 cùng phê duyệt ngân sách riêng. Sau đó hai
pilot Qwen đều đạt 30/30. Nhánh Gemini P03 đã đạt 1.400/1.400 sau recovery;
P03-A003 mở lại plan để chạy thêm 1.400 OpenAI judgment bằng snapshot
`gpt-5.4-mini-2026-03-17`, dùng calibration pilot Qwen và cap bảo thủ 33 USD.
Hai full judge sau đó đều đạt 1.400/1.400. Plan 04 đã hoàn thành
phân tích offline: Qwen đạt Overall Accuracy 83,80% theo GPT judge và
81,29% theo Gemini judge; kết luận Qwen vượt Llama bền vững qua hai
judge, còn so với hai Gemini tutor configuration thì phụ thuộc judge. Report
và audit 3.173 bất đồng nằm trong experiment; đây chưa phải human
ground truth.

Experiment `20260903_135547` Plan 01 đã sinh staging fragment v1 lossless cho
209 OCR unit. Ba lỗi section hierarchy được ghi ở P01-A001 và tạm hoãn theo
P01-A002 để dùng snapshot hiện tại cho Plan 02; chưa publish vào `shared`.
Plan 02 đã được Quân duyệt và có index hai bảng logic cùng API search hợp nhất
`section_keywords`/`content_keywords`. Lượt build/smoke v1.1 đầu tiên phát hiện
fragment zero-effective lọt top-5 và BM25 chọn mục con thay vì đầu mục bài học
khớp chính xác. P02-A002 đã cài semantics v1.2: bundle lossless vẫn giữ đủ row,
SQLite chỉ nhận `effective_content_length > 0`, khóa hash chính sách và ưu tiên
exact component trước BM25. Plan 02 đã hoàn thành: 71 test đạt, base/FTS cùng
3.825 row từ 5.411 fragment nguồn, đủ 209 unit, integrity đạt và ba smoke query
đều qua gate. Preflight ngoại tuyến Plan 03 với index v1.2 đã đạt 11/11 kiểm
tra mà không gọi mô hình; selection 16 mẫu tái lập đúng và run contract v3 có
fingerprint riêng. Vertex AI và publication `shared` vẫn đóng. Plan 03 được Quân
phê duyệt tạm thời cho cài đặt mã ngày 17/09/2026: luồng audit sáu cụm
bao phủ đúng 18 tiêu chí, gọi trực tiếp retrieval Plan 02 qua ranh giới
tool-calling đã khóa, ghi trace/hash và bắt buộc cờ `--execute-api` cho
Vertex AI. Mã, test, config và runbook đã được viết nhưng chưa chạy. P03-A001
đã chuyển config sang checklist chuẩn trong `shared`, Việt hóa chỉ dẫn mô hình
và thêm chú thích khối cho hàm chạy chính mà không đổi logic. Việc đổi tên
module, tích hợp vào entry point Phase 1 và mở rộng model provider dùng chung
cho tool calling được hoãn đến sau khi Quân duyệt logic. P03-A002 sau đó ghi
nhận module nghiệp vụ đã được đổi tên thành `agent_audit.py`; các tên `pilot`
experiment-scoped vẫn giữ cho lượt thử nghiệm 16 mẫu. P03-A003 đã ghép hai
nguồn chuẩn hóa thành đầu vào experiment-local 1.050 mẫu lớp 6–9, đưa đầy đủ
quy ước Bloom vào cụm nhận thức và thay criterion `uncertain` giả từ lỗi hệ
thống bằng retry có trace. P03-A004 chuyển retry sang một lượt đầu và tối đa ba
lượt quét lại toàn split: cụm thành công được checkpoint ngay, cụm lỗi không
chặn mẫu sau, và chỉ các cặp `(sample_id, cluster_id)` còn thiếu được gọi lại.
Resume phục hồi dòng JSONL cuối bị dở hoặc rollback một cụm criterion đã biết
nhưng chưa đủ; sau lượt cuối vẫn còn lỗi thì ghi summary `incomplete` rồi mới
thoát khác `0`. Sau chẩn đoán `development-v1`, P03-A005 đổi FTS nhiều token
sang tập ứng viên OR xếp hạng BM25 nhưng không fallback section cha/content
toàn cục; tool trả rõ trạng thái và section đã chọn, cache truy vấn lặp, tách
ngân sách ba kết quả hữu ích/tám yêu cầu tổng và khóa đúng quy tắc
`evidence_fragment_ids` theo cụm. CLI dùng Loguru với tiến độ/traceback an toàn;
quét trùng lặp 1.050 mẫu giảm xuống 9,539 giây nhờ pruning chính xác và tái sử
dụng chỉ mục `SequenceMatcher`. Quân đã chạy `development-v2` và một lượt
resume nhưng còn hai cụm B chưa hoàn thành. P01-A004 hiện bổ sung pipeline
fragment v1.1: đo `effective_content` theo ký tự mà không xóa nội dung, ghép lặp
lineage liên tiếp trong đúng `section_path`, có cận dưới/cận trên, cấm bảng–bảng
và chỉ cho bảng ngắn không caption nhập vào văn bản. P02-A001 khóa index bằng
bundle/validation/merge-contract hash. P03-A006 bổ sung hợp đồng phản hồi tool
có thể bật/tắt phần giải thích
trong prompt, ngân sách động với `must_finalize`, cache query chuẩn hóa dấu câu,
kết quả `uncertain` xác định khi cụm B không có fragment, và tách metrics phiên
hiện tại/tích lũy; P03-A007 ẩn metadata hợp nhất khỏi Gemini nhưng ghi lineage
và nguồn bảng vào trace/metrics. Survey/build v1.1 ngày 24–25/09 đạt lossless
nhưng bị loại khỏi downstream vì HTML comment SBT làm sai phép đo; P01-A005 đã
loại comment chỉ khỏi `effective_content`. Survey A006 đã sinh đủ 96 mẫu quanh
cận dưới/cận trên; CSV 39 cột được giữ làm provenance máy. P01-A007 tạo
workbook Excel ba sheet bằng tiếng Việt làm bề mặt review duy nhất, tách hai
nhiệm vụ và chỉ hiển thị tối đa 13 cột. 40 test fragment/retrieval/tài liệu đạt;
P01-A008 ghi nhận Quân đã hoàn tất 100% review, chốt cấu hình
`20/1500/50/prefer_short_group` và tiếp tục cấm bảng–bảng. Review cho thấy lỗi
chính nằm ở quan hệ caption/lời dẫn–bảng, ranh giới bài tập SBT và
OCR/`section_path`, không phải độ dài thuần túy. P01-A008 đã cài đặt nhận dạng
caption `Bảng`/`Hình` và caption nguồn kề bảng, đầu mục riêng cho từng số bài
SBT ở cả phần đề/lời giải, cùng phép ghép một bảng không caption với lời dẫn
cấu trúc trong đúng unit/section dưới cận 1.500. Merge contract tăng lên v3 và
kiểm thử ngoại tuyến đã đạt. Hai lượt rebuild đầu tiên phát hiện caption giữa
hai bảng bị dùng hai lần; mã đã khóa ownership một-một. Lượt build sau đó đạt
lossless nhưng hậu kiểm còn caption câu hỏi, nhãn bài tập/ancestor lặp và một
heading-only tail tạo path sai. Bốn lỗi xác định này đã được sửa; 50 test đạt
và preflight trong bộ nhớ qua 209 unit. Hậu kiểm tiếp theo trên toàn bộ 299 nhóm
bảng–văn bản phát hiện structural pass còn nhận quá rộng. Merge contract v4 nay
chỉ nhận lời dẫn/heading đứng trước bảng, loại ngữ cảnh rỗng không phải heading
và buộc fallback bảng ngắn có văn bản thực. Tiền kiểm trên 5.660 fragment v1
cho 228 nhóm `text → table`, lossless, không bảng–bảng hay vượt cận; 53 test đạt.
Quân đã chạy survey A008-v4 và build bundle chính trong
`outputs/fragment_v1_1_v4/`; hậu kiểm độc lập xác nhận 5.411 ID duy nhất trên
209 unit, lineage bao phủ đúng một lần toàn bộ 5.660 fragment v1, lossless và
hash khớp. Plan 01 và Plan 02 đã hoàn thành gate staging. Preflight ngoại tuyến
Plan 03 đã chạy `development-v3`: 31/32 cụm hoàn thành, cụm còn lại bị cắt bởi
`MAX_TOKENS` ở trần 4.096. P03-A009 đã cài runtime/config v4 để lưu raw response
trước parse, tách candidate/thinking/tool-use token, không retry truncation với
cùng hợp đồng và giới hạn phần giải thích ở 600 ký tự; config v4 giữ thinking
MEDIUM và tăng trần lên 8.192. 74/74 kiểm thử liên quan đạt. Quân đã chạy xong
`development-v4` với 8/8 mẫu, 32/32 cụm và 144/144 tiêu chí, sau đó hoàn tất rà
soát các ca cần chú ý. P03-A011 đã cài contract v5: kiểm evidence theo từng
criterion, phép chiếu hội thoại có raw/projected trace, cờ phụ thuộc ảnh và
selection mở rộng theo file. Input config giữ 1.050 ID lịch sử rồi thêm 147
hàng ghi rõ SBT lớp 6–8 bằng namespace nguồn; selection giữ 8/8 mẫu cũ và bổ
sung 12/12 mẫu mới cùng 6 reserve. `development-v5` đã chạy và được giữ làm
bằng chứng chẩn đoán. P03-A012 đã cài contract v5.1: chuẩn hóa hội thoại có
provenance trước mọi consumer, loại annotation giàn giáo sát nhãn nói theo quy
tắc fail-closed, dùng ma trận evidence có cấu trúc, tách ứng viên phụ thuộc ảnh
khỏi kết luận và hạ trần confidence của các cụm chủ quan. V5.1 dùng snapshot và
run-id mới nhưng giữ nguyên selection v5. Quân đã chạy xong các gate V5.1 và
hoàn tất human review. P03-A013 bổ sung candidate content của từng vòng Gemini vào
`model_round` trong trace, nhưng tiếp tục loại mọi private thought part; vì mã
runtime đã đổi nên offline test và preflight được chạy lại trước
`development-v5.1`. P03-A014 đã được duyệt và cài thành contract v5.2: siết
`RAW-CON-03 pass` phải có fragment, khóa độ đầy đủ của `RAW-CON-04`, giữ
`RAW-STR-04` ở nghĩa khả năng audit và trả `image_placeholder_count` cùng
`effective_content_length` ở từng fragment mà không gửi pixel ảnh. Config v5.2
giữ nguyên snapshot v5.1 và selection v5. `development-v5.2` đã checkpoint
119/120 cụm; chỉ `HNMU-G7-R0214-STT3 | B` bị `MAX_TOKENS`. P03-A016 đã cài
recovery một cụm: giữ cap 8.192/MEDIUM, giới hạn hai trường luận giải cụm B ở
300 ký tự, kiểm parent 354/19/119 và chỉ publish bundle con khi đạt
360 criterion/20 summary/120 cụm mà không đổi bản ghi kế thừa. Unit test và
preflight recovery chỉ đọc đã đạt; chờ Quân chủ động chạy đúng một lệnh Vertex
AI. P03-A017 bổ sung phân loại retry tối thiểu: HTTP 401/403 dừng ngay ở cả full
run và recovery, trong khi 429/5xx giữ chính sách retry hiện hành; không thay
đổi manifest, summary hay fingerprint. P03-A018 đưa toàn bộ câu lệnh hệ thống
của các cụm B–E vào bundle có phiên bản tại
`shared/prompts/hnmu_dialogue_audit/v1/`; manifest khóa SHA-256 từng thành phần,
runtime từ chối path/hash/schema sai và run fingerprint ghi nhận toàn bộ bundle.
Cụm A/F vẫn deterministic. Config v5.3 dùng bundle mới mà không sửa config hay
output lịch sử. P03-A019 tiếp tục tạo bundle v2 và một targeted regression
contract: 10 mẫu chỉ chạy 11 cụm B/E đã khóa, kiểm 11 nhãn/evidence case và ba
ca phụ thuộc ảnh từ workbook của Quân. Runtime bổ sung tín hiệu cú pháp cho
mâu thuẫn Bài/Hình và xác nhận đáp án sai rõ ràng, còn SBT dùng đúng section
`PHẦN I — ĐỀ BÀI`/`PHẦN II — HƯỚNG DẪN GIẢI`. P03-A020 dùng
`plan03-tool-calling-pilot-v5-5-regression.json`. Phiên bản này
đọc tương thích hai dạng trường evidence, cho đúng một lượt sửa output sau lỗi
validator, dành lượt truy xuất SBT cho phần lời giải, truyền ngữ cảnh ảnh dạng
text và đánh giá 18 nhãn ảnh theo từng tiêu chí. Prompt bundle v3, regression
spec v2, 50 test, preflight 10 mẫu/11 cụm và bốn smoke SBT đều đạt ngoại tuyến.
Lượt model v5.5 sau đó kết thúc `incomplete` với 9/10 mẫu và 10/11 cụm. Quân đã
duyệt P03-A021 và bản offline v5.6 đã được cài: repair cụm B chỉ nhận evidence
model-visible, adapter chuẩn hóa hai section SBT trước query signature/cache và
routing ảnh dùng `none → false`, `supporting → false` mặc định,
`required → true`. Prompt bundle v4, config v5.6, 81 test, preflight 10 mẫu/11
cụm và bốn smoke section đều đạt mà không gọi model. Quân cần tái lập R1–R3
trước khi chủ động quyết định R4. Chưa chạy holdout, chưa ghi output audit vào
`shared` và chưa mở Plan 04. P03-A022 sau đó mở một config riêng để chạy v5.6
trên đúng 20 mẫu development với đủ sáu cụm/18 tiêu chí; preflight config-only
đạt fingerprint `564e8379d4a9c9ae4f56b787ac8cbd8bb00e67885bde8083119839dbc937ba4c`.
Full run sau đó đạt 19/20 mẫu, 119/120 cụm và 354/360 tiêu chí; resume không
gọi model vì cụm B còn thiếu đã mang trạng thái lỗi hợp đồng không retryable.
P03-A023 khóa một recovery config bất biến cho đúng cụm này và chỉ tạo bundle
con. Recovery đã đạt 360/360 tiêu chí, 20/20 mẫu và 120/120 cụm. Báo cáo so
sánh v5.2–v5.6 cho thấy agreement 336/360; v5.6 tốt hơn ở target gate nhưng
kém hơn ở control và nhãn phụ thuộc ảnh. Holdout vẫn đóng, chờ human gate.
Batch audit nguồn v5.6 sau đó đã hoàn tất lớp 8 qua recovery/merge bất biến và
export đủ 280 mẫu, 5.040 kết quả. Tin 6 Bài 6–11 cũng đã hoàn tất theo cùng
nguyên tắc: P03-A030 chuẩn hóa offline cặp evidence-contract còn lại, còn
P03-A031 tạo hai child shard bất biến và export đủ 84 mẫu, 1.512 kết quả cùng
84 summary. Workbook ba sheet đã được mở lại kiểm tra; các parent shard và
recovery artifact không bị sửa.
P03-A032 sau đó mở nguồn `lop6_lan2`: 153 mẫu được giữ trong bốn shard
39/38/38/38, có wrapper chạy đủ shard và preflight ngoại tuyến đã đạt. Vertex
AI chỉ được gọi khi Quân chủ động chạy wrapper; wrapper không tự resume, merge,
export hoặc chuyển sang nguồn khác.
Lượt đầu của nguồn này ghi 145/153 mẫu và 2.710/2.754 kết quả. P03-A033 cho phép
resume riêng shard 001 để thử lại ba cụm lỗi 429, rồi chạy một recovery bất biến
cho đúng sáu cụm B non-retryable. Recovery có gate trạng thái cả bốn parent,
giữ nguyên runtime v5.6 và không tự merge/export; Quân vẫn là người duy nhất
thực hiện lời gọi Vertex AI.

Experiment `20260909_121749` đã hoàn tất Plan 01 cho camera-ready KSE 2026:
reviewer/action matrix và claim-evidence registry đã khóa quyết định 665,
phân biệt checklist 18 tiêu chí với 22 rubric, ghi 382 dialogue là set aside và
loại release statement khỏi scope manuscript. Thiết kế P02 ban đầu chia 48
coverage cases và 12 diagnostic cases, nhưng snapshot thực tế cung cấp gợi ý ẩn
nguồn ở toàn bộ 63 cases để tăng tốc cho một giáo viên chuyên môn. P02-A007 tạm
giữ cách hiểu independent human--LLM agreement; denominator và wording cuối vẫn
phải được Quân phân xử khi duyệt P03. P02 đã được Quân duyệt; CLI experiment-local đã qua unit
tests và full-data preflight. P02-A005 dùng Excel làm phiếu chấm; HTML chỉ đọc đã
tách thông tin bài học, kiến thức tham chiếu và transcript đúng thứ tự/role trước
khi hiển thị Phản hồi 1/2 theo GPT blind pair order. Mỗi write run nằm trong
`outputs/YYYYMMDD_HHMMSS/` bất biến; W/T/L được quy đổi offline sau khi khóa.
Output lịch sử được giữ nguyên; Quân xác nhận snapshot `outputs/20260910_135145/`
chủ ý dùng nhãn `Gợi ý để tham khảo` và cung cấp gợi ý ở toàn bộ mẫu để tăng tốc
độ chấm; kiểm tra xác nhận 63/63 cases và 717/717 judgments có gợi ý. Hai câu
hướng dẫn tĩnh vẫn nhắc `GPT`, nên nguồn chưa được ẩn tuyệt đối; Quân yêu cầu
không can thiệp thêm và không cần tạo lại snapshot vì hai điểm này. P03 vẫn là bản nháp và
chỉ được xem xét sau khi workbook đã chấm được trả lại. P02-A007 tạm giữ cách
hiểu independent human–LLM agreement theo quyết định của Quân, đồng thời giữ caveat
về all-case suggestion exposure để phân xử khi duyệt P03. P04 đã hoàn tất source
redline và Figure 1: acknowledgment tập thể cho giáo viên Tin học từ Liên Minh,
Yên Hòa và Nghĩa Tân Secondary Schools đã được thêm trước references, Workstream
1A/1B xếp trên-dưới cùng hội tụ vào Phase 3,
và smoke build đạt đúng sáu trang gồm acknowledgment cùng references.
P04-A001 tiếp tục giữ human validation hoàn toàn ở Future Work trong bản
manuscript hiện tại; câu giới thiệu checklist đã có citation và bảng 18 tiêu chí
trong appendix được thêm đúng một cột căn cứ khoa học/kỹ thuật. Bản main cộng
references vẫn đúng sáu trang; bản bật appendix cũng biên dịch thành công.
P04-A002 khóa ba đơn vị trên từ Google Sheet cộng tác viên do anh Chung tổng hợp,
không nêu tên cá nhân; smoke build sau sửa đổi vẫn đúng sáu trang.
P04-A003 đồng bộ corresponding author thành Thi-Mai Hoang, email
`htmai@hnmu.edu.vn`, trong active author block và hai block mẫu được comment;
build main cộng references vẫn đúng sáu trang và appendix build là 21 trang.

## Start here

- Canonical benchmark discovery: [shared/benchmark/README.md](shared/benchmark/README.md).
  From that page, the 665 Phase-1 dialogue families, 2,028-candidate pool,
  provisional 1,400-candidate selection, and PL-REQ-60 calibration bundle are
  each one direct path away.
- Current component and ownership map: [ARCHITECTURE.md](ARCHITECTURE.md).
- Repository operating rules for agents and contributors: [AGENTS.md](AGENTS.md).
- Current KSE 2026 camera-ready revision lifecycle:
  [experiments/20260909_121749/roadmap.md](experiments/20260909_121749/roadmap.md).
- Current PL-REQ selection lifecycle:
  [experiments/20260817_160800/roadmap.md](experiments/20260817_160800/roadmap.md).
- Current local Qwen3.8/Ollama lifecycle:
  [experiments/20260902_082403/roadmap.md](experiments/20260902_082403/roadmap.md).
- Current Qwen3.8 LLM-judge lifecycle:
  [experiments/20260904_093529/roadmap.md](experiments/20260904_093529/roadmap.md).
- Current lossless-fragment/retrieval/audit lifecycle:
  [experiments/20260903_135547/roadmap.md](experiments/20260903_135547/roadmap.md).

The shortest canonical data path is `README.md` → `shared/benchmark/README.md`
→ the selected bundle's `manifest.json` and data files. Read the manifest before
use: `shared` means canonical for discovery, not final HNMU/UET approval.

Judge cost-pilot v2 đã hoàn thành 90/90 phép chấm cho cả Gemini 3.5 Flash
và `gpt-5.4-mini-2026-03-17`. Đối chiếu phát hiện thành phần lỗi nghiêm
trọng không ổn định theo response đối đầu. Theo quyết định UET, contract
`rubric-only-v3` loại phần này khỏi cả system/user prompt, output model và
hậu xử lý; các trường tương thích trong record được giữ rỗng. Wrapper chung
cho hai judge đã hoàn thành đúng 90 phép so sánh mỗi mô hình, không ghi đè
bundle v2. Gemini và GPT đạt agreement 86,7% ở overall và 77,2% ở cấp
rubric; điểm tổng hợp kiểu KMP-Bench cùng xếp LearnLM-prompted cao nhất,
Gemini baseline thứ hai và Llama Maverick thứ ba. Cost-pilot vẫn chỉ là
bằng chứng thăm dò vì có 30 candidate và Gemini vừa là target vừa là judge.

Audit fragment trên 30 candidate cho thấy 2 mẫu có evidence sai, 20 mẫu có
evidence không đủ và chỉ 8 mẫu đủ hoặc gần đủ ở cấp candidate. UET vì vậy
đã mở contract `gold-answer-only-v4`: giữ nguyên v2/v3, bỏ fragment khỏi
judge input, dùng `gold_answer` làm neo duy nhất cho `RUB-GEN-ACC` và ghi
policy loại evidence trong manifest/record. Đoạn này ghi trạng thái lịch sử
trước khi v4 được chạy đủ và cổng batch được UET mở.

Lần chạy trả phí v4 đầu tiên giữ được 88/90 phán quyết Gemini; hai lỗi còn
lại là một biến thể tên tiêu chí tương đương và một output `MAX_TOKENS`.
Recovery đã được cô lập cho v4: chuẩn hóa đúng alias đã biết, chỉ chạy bù
hai request Gemini ở 12.288 token rồi mới chạy GPT ở giới hạn 8.192 token.

V4 hiện đã hoàn thành 90/90 cho cả Gemini và GPT. UET đã mở full judge cho
1.400 candidate × ba target bằng hai judge. Pipeline Batch API mới giữ
nguyên prompt/hậu xử lý v4, tách hoàn toàn khỏi runner synchronous, dùng p95
usage của pilot để khóa ngân sách. Sau collect và recovery, cả Gemini và
GPT đều hoàn thành 4.200/4.200 request; wrapper hoạt động là
`scripts/benchmark_evaluation/run_full_1400_judge_batch.sh`.

Phân tích Section V đã được tái lập hoàn toàn bằng code trên hai full judge
bundle. Artifact tinh gọn chứa instruction ablation, độ bền vững giữa hai
judge và descriptive position sensitivity tại
`experiments/20260727_170150/outputs/benchmark_evaluation/section_v_ablation_analysis_v1/results.json`;
mọi cổng 4.200/38.832 và các anchor đã khóa đều đạt. Không có model call mới
trong bước này.

Current PL-REQ selection roadmap: [experiments/20260817_160800/roadmap.md](experiments/20260817_160800/roadmap.md)
Current SBT ingestion/OCR roadmap: [experiments/20260829_175101/roadmap.md](experiments/20260829_175101/roadmap.md)
Current local Qwen3.8/Ollama roadmap: [experiments/20260902_082403/roadmap.md](experiments/20260902_082403/roadmap.md)
Current Qwen3.8 LLM-judge roadmap: [experiments/20260904_093529/roadmap.md](experiments/20260904_093529/roadmap.md)
Current fragment v1/retrieval/audit roadmap: [experiments/20260903_135547/roadmap.md](experiments/20260903_135547/roadmap.md)
Human-validation planning roadmap: [experiments/20260814_062402/roadmap.md](experiments/20260814_062402/roadmap.md)
Completed repository-refactor roadmap: [experiments/20260806_145124/roadmap.md](experiments/20260806_145124/roadmap.md)
Current benchmark/evaluation roadmap: [experiments/20260727_170150/roadmap.md](experiments/20260727_170150/roadmap.md)
Previous phase-2 construction roadmap: [experiments/20260722_000940/roadmap.md](experiments/20260722_000940/roadmap.md)
Previous raw-dialogue audit roadmap: [experiments/20260709_155523/roadmap.md](experiments/20260709_155523/roadmap.md)
Previous design roadmap: [experiments/20260705_215045/roadmap.md](experiments/20260705_215045/roadmap.md)
Historical baseline roadmap: [experiments/20260620_115236/roadmap.md](experiments/20260620_115236/roadmap.md)

Approved plans:

- [Experiment 20260904 Plan 01 — Portable single-target Batch judge](experiments/20260904_093529/plans/01-portable-single-target-batch-judge.md)
- [Experiment 20260903 Plan 01 — Lossless fragments and section hierarchy](experiments/20260903_135547/plans/01-lossless-fragments-retrieval-and-audit-tools.md)
- [Experiment 20260902 Plan 01 — Ollama/Qwen3.8 runtime and model provider](experiments/20260902_082403/plans/01-ollama-qwen38-runtime-and-provider.md)
- [Experiment 20260902 Plan 02 — Provider-neutral target runner and Qwen3.8 pilot](experiments/20260902_082403/plans/02-provider-neutral-target-runner-and-qwen38-pilot.md)
- [Experiment 20260829 Plan 03 — Unified OCR asset layout and SBT lessonization](experiments/20260829_175101/plans/03-sbt-lessonization-and-image-reorganization.md)
- [Experiment 20260829 Plan 02 — Datalab OCR for complete grades 6–8 SBT books](experiments/20260829_175101/plans/02-datalab-sbt-ocr.md)
- [Experiment 20260817 Plan 01 — PL-REQ-60 deterministic selection and shared publication](experiments/20260817_160800/plans/01-pl-req-60-selection-and-publication.md)
- [Experiment 20260722 Plan 01 — Raw-dialogue to benchmark-candidate conversion contract and pilot](experiments/20260722_000940/plans/01-audited-raw-dialogue-to-benchmark-candidate-conversion.md)
- [Experiment 20260722 Plan 02 — Multi-candidate conversion from every tutor turn](experiments/20260722_000940/plans/02-split-policy-and-full-benchmark-conversion.md)
- [Experiment 20260722 Plan 03 — Measurement foundations, six capabilities, six KMP principles, and two-tier rubrics](experiments/20260722_000940/plans/03-thcs-task-rubric-specification-and-coverage.md)
- [P01 — Specialist-agent foundation](experiments/20260620_115236/plans/01-specialist-agent-foundation.md)
- [Plan 01 — Specialist expansion for learning resources and benchmark specification](experiments/20260701_100006/plans/01-specialist-expansion-learning-resource-and-benchmark-spec.md)
- [Experiment 20260709 Plan 01 — Benchmark quality literature review](experiments/20260709_155523/plans/01-benchmark-quality-literature-review.md)
- [Experiment 20260709 Plan 02 — Shared data and code layout](experiments/20260709_155523/plans/02-shared-data-and-code-layout.md)
- [Experiment 20260709 Plan 03 — Learning resource normalization phases 0–2, derived PDFs, and OCR probes](experiments/20260709_155523/plans/03-learning-resource-normalization-and-retrieval-system.md)
- [Experiment 20260709 Plan 03.4–03.5 — Fragment and retrieval from Nguyen OCR Markdown](experiments/20260709_155523/plans/03-phase4-5-fragment-and-retrieval-from-nguyen-ocr.md)
- [Experiment 20260709 Plan 04 — HNMU dialogue intake, coverage, consistency, and dedup audit](experiments/20260709_155523/plans/04-hnmu-dialogue-intake-coverage-consistency-dedup.md)
- [Experiment 20260709 Plan 07 — HNMU dialogue auditor specialist](experiments/20260709_155523/plans/07-hnmu-dialogue-auditor-specialist.md)

Current plans:

- [Experiment 20260727 Plan 01 — Principle requirement-score specification](experiments/20260727_170150/plans/01-principle-requirement-score-specification.md)
- [Experiment 20260727 Plan 02 — Vertex AI requirement-scoring pilot](experiments/20260727_170150/plans/02-vertex-ai-requirement-scoring-pilot.md)
- [Experiment 20260727 Plan 03 — Full-run statistics and analysis](experiments/20260727_170150/plans/03-full-run-statistics-and-analysis.md)
- [Experiment 20260727 Plan 04 — Two-tier rubric library](experiments/20260727_170150/plans/04-two-tier-rubric-library.md)
- [Experiment 20260727 Plan 05 — Benchmark evaluation configuration](experiments/20260727_170150/plans/05-benchmark-evaluation-configuration.md)

## People and decision authority

- **AI engineers** build the codebase, adapters, validation, provenance, and evaluation infrastructure.
- **Expert teachers** author, review, and adjudicate pedagogical and subject-matter content. Their judgment is required; agents do not replace it.

## Language policy / Quy ước ngôn ngữ

- Code-facing and agent-facing materials should prefer English so future agents can parse and operate reliably. This includes `AGENTS.md`, runtime adapters, validator code, schema/reference docs mainly consumed by agents, and implementation tests.
- Human-facing materials should prefer Vietnamese. This includes plans, meeting notes, reports, handoffs, teacher-facing packets, HNMU-facing review materials, and final summaries to the project lead.
- Mixed-audience files such as this README should keep operational and runtime instructions English-first. Vietnamese can be used where the reader is primarily the project lead, HNMU, or teacher reviewers.
- Keep exact names unchanged for files, commands, field IDs, model/tool names, paper titles, DOI/URL strings, and source quotes.
- Explain unavoidable English terms in Vietnamese when they affect teacher-facing or HNMU-facing understanding.

## Current specialists

- `research-methodologist`: evidence-focused literature review, traceable claims, limitations, and open research questions.
- `learning-resource-curator`: v0 learning-resource source maps, simple learning-material IDs, fragments, topic maps, and grade-6–8 prerequisite grounding for grade 9.
- `benchmark-specification-designer`: benchmark task definitions, rubrics, serious-error catalogs, and provenance matrices grounded in research and learning resources.
- `teacher-collaboration-designer`: teacher-facing author/reviewer/adjudicator workflows, checklists, examples, and handoffs.
- `hnmu-dialogue-auditor`: raw HNMU dialogue audit specialist for checklist-level consistency, SGK/SGV evidence, confidence, and review-queue suggestions before benchmark conversion.
- `pedagogical-principle-annotator`: specialist thử nghiệm của phương pháp Plan 03 cũ; các run đã trở thành diagnostic legacy. Experiment active dùng Vertex AI API trực tiếp cho `requirement_score`, không dùng specialist này để chấm từng candidate.

Cost-control defaults are pinned in Codex adapters: `research-methodologist`, `learning-resource-curator`, `hnmu-dialogue-auditor`, and `pedagogical-principle-annotator` use `gpt-5.4-mini` with reasoning `medium`; `benchmark-specification-designer` uses `gpt-5.4-mini` with reasoning `high` for synthesis. Do not spawn multiple instances of the same specialist unless the project lead approves the instance count, rationale, model, reasoning effort, allowed writes, expected output, and merge plan.

The orchestrator delegates to specialists through native observable agent threads:

```text
User → Orchestrator → Specialist thread → Auditable artifact → Human review
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for component and runtime details.

## Runtime support

| Runtime | Status |
|---|---|
| Codex CLI | Runtime smoke-tested target; use `/agent` to inspect and steer specialist threads. |
| Codex App | Supported when native agent activity is visible. |
| Codex IDE Extension | Do not spawn hidden specialists when agent visibility is unavailable; use single-agent mode or switch to CLI/App. |
| Claude Code | Project adapters are generated and statically validated; runtime testing is deferred. |

Interactive specialist work must not be implemented with nested `codex exec`, `claude -p`, daemons, or hidden terminal processes.

## Repository map

```text
agents/                 Canonical specialist skills, references, and validators
.agents/skills/         Skill discovery links for Codex
.codex/agents/          Codex custom-agent adapters
.claude/agents/         Claude project-agent adapters; static validation only
docs/decisions/         Durable architecture decision records (ADRs)
experiments/            Plans, machine-readable status, runbooks, coordination, and reports
pyproject.toml           Src-layout package metadata and dependency groups
environment.yml          Human-maintained Conda environment specification
shared/benchmark/       Versioned benchmark registry, canonical datasets, selections, and provisional specifications
shared/                 Shared raw data, learning resources, prompts, and benchmark artifacts
src/edu_benchmark/      Shared project code for data I/O, audit, conversion, resources, and quality checks
src/edu_benchmark/experiment_runtime/ Portable YAML config, path resolution, preflight, and offline execution
src/edu_benchmark/model_providers/ Independent Vertex AI/OpenAI/Ollama transport and normalized model contracts
src/edu_benchmark/requirement_scoring/ Pedagogical-principle requirement-scoring business logic
src/edu_benchmark/learning_resources/ Reusable learning-resource parsing, retrieval, safe SBT crawling, and gated Datalab OCR
scripts/benchmark_registry/ Thin CLI for deterministic shared benchmark promotion/validation
scripts/governance/     Thin CLI for experiment-governance validation
scripts/requirement_scoring/ Thin CLI entry points for requirement scoring, analysis, and export
scripts/model_providers/ Thin launch/probe entry points for approved model runtimes
scripts/learning_resources/ Thin CLI entry points for learning-resource discovery, crawling, OCR preparation, and retrieval
src/edu_benchmark/repository_hygiene/ Non-destructive scoped inventory, privacy-safe untracked-file aggregation, hashing, duplicate grouping, and retention summaries
scripts/repository_hygiene/ Thin CLI for config-driven repository-hygiene inventory
experiments/20260806_145124/configs/ Requirement-scoring and portable analysis runtime configs
document/               User-provided project source documents
kse_submit_manuscript/  KSE 2026 writing plan, LaTeX source, evidence registry, and releases
tests/agents/           Agent and documentation tests
```

## Shared data and code layout

Experiment `20260709_155523` Plan 02 established the shared layout:

- Canonical benchmark discovery begins at `shared/benchmark/README.md` and
  `shared/benchmark/artifact_registry.csv`. The registry points to the
  18-criterion checklist, 665 Phase-1 dialogues, 2,028-candidate conversion
  pool, provisional 1,400-candidate selection with the 628/0 backlog state, and
  provisional capability/principle/rubric bundles. It also registers PL-REQ v1:
  60 primary candidate and 8 reserve for human calibration. Each bundle has a
  manifest with source hashes, counts, authority, access policy, and limitations.
- HNMU raw dialogue batches live under `shared/raw_data/HNMU-teacher_dialog_samples/` and are registered in `manifest.csv`. Do not edit the raw Excel files directly. When a batch stores one dialogue turn per row under a vertically merged `STT`, use the fail-closed derived-workbook normalizer in `scripts/dialogue_audit/normalize_hnmu_dialogue_workbooks.py`; it joins all non-empty cells of each logical field in source-row order and its output belongs in an experiment, not in `shared/raw_data/`. Use `--append-manifest` to add only a new source workbook to an existing verified manifest; it refuses to replace a recorded source.
- Shared SGK/SGV learning resources belong under `shared/learning_resources/`.
  This area contains copied source material, registries, OCR text, fragments,
  and the inputs used to rebuild the local retrieval index.
- The full-book SBT crawler keeps reusable discovery/download/manifest logic in
  `src/edu_benchmark/learning_resources/sbt_crawler.py` and exposes the thin CLI
  `scripts/learning_resources/crawl_sbt_images.py`. For grades 6–8, Tìm Đáp Án
  is recorded as the discovery page while every accepted image URL must be
  explicitly present in its HTML and hosted under
  `cdnelearning.nxbgd.vn/uploads/books/`. Preflight locks the complete sequences
  to 101/94/122 pages; grade 9 is unsupported until an approved complete source
  exists. Dry-run is write-free, TLS verification is mandatory, and generated
  rows remain `draft` with internal-research access notes pending rights review.
- The approved SBT OCR workflow lives in
  `src/edu_benchmark/learning_resources/sbt_ocr.py` with the thin CLI
  `scripts/learning_resources/ocr_sbt_with_datalab.py`. It verifies the 317
  registered source images and their checksums, excludes only the 12 locked
  cover/title/publication pages, and assembles three PDFs containing 97/90/118
  OCR pages. The CLI is preflight-only unless `--execute-api` is present; full
  execution additionally requires `--confirm-page-count 305`. Pilot output is
  experiment-scoped, while only validated full-book output may be atomically
  published to `shared/learning_resources/ocr_text/` as `draft`. See the
  [Plan 02 runbook](experiments/20260829_175101/runbooks/plan02-datalab-sbt-ocr.md).
- Processed learning-resource pages should use Markdown with front matter and stable anchors as the temporary human-readable source for review and retrieval indexing. These Markdown pages should be generated from OCR text plus bounding boxes through a layout-reconstruction step, not from plain text alone. JSON/crop debug artifacts are optional and should be generated only when bbox/table/cell-level inspection is needed.
- The active OCR manifest registers 209 units: 75 SGK, 79 SGV, and 55 draft SBT lesson/table-of-contents units. Fragmentation remains allowlisted to SGK/SGV in `shared/learning_resources/fragments/learning_resource_fragments.csv` (2,750 fragments), while the generated SQLite index stores all 209 source records but zero SBT fragment/FTS rows. The SQLite file is rebuildable and ignored by Git. `shared/learning_resources/agent_context/` is the navigation hub for audit agents that need the checklist, fragments, index, scaffolding notes, and retrieval tools without copying canonical source files.
- Reusable implementation code belongs under `src/edu_benchmark/`. Experiments should store run outputs, not reusable code.
- Plan 04 dialogue audit v0 reads HNMU raw Excel files through `src/edu_benchmark/data_io/` and `src/edu_benchmark/dialogue_audit/`, then writes experiment-scoped audit tables. The lớp 6–7 audit remains under `experiments/20260709_155523/outputs/hnmu_dialogue_audit/`; the separate lớp 8–9 follow-up audit is under `experiments/20260709_155523/outputs/hnmu_dialogue_audit_grade8_9/`. Both runs are draft audits and do not replace HNMU/UET subject-matter review.
- Agent-assisted Plan 04 outputs must aggregate the main sample-level `agent_shard_audit/merged/quality_check_suggestions.csv` from criterion-level `raw_dialogue_checklist_results*.csv` with the strict checklist rule implemented in `src/edu_benchmark/dialogue_audit/checklist_aggregation.py` and `scripts/dialogue_audit/sync_quality_suggestions_from_checklist.py`. This file uses the canonical `quality_decision` labels `pass`, `need_human_review`, and `failed`. A sample cannot remain `pass` if any required criterion is `fail` or `uncertain`.

## Experiment governance

New experiments use [experiments/_templates/README.md](experiments/_templates/README.md).
The concise Markdown plan is the approval surface; a machine-readable status
file cannot grant implementation authority. After approval, situational changes
go into one chronological amendment log rather than rewriting the baseline.

Validate a governed experiment from the repository root with:

```bash
/workspace/quannd/miniconda3/envs/benchmark_env/bin/python \
  scripts/governance/validate_experiment.py experiments/20260806_145124
```

The validator checks metadata, explicit approval, lifecycle/status consistency,
roadmap links, amendment references, coordination JSONL, registered artifacts,
and the default artifact budget. Historical experiments remain valid provenance
and do not require a cosmetic migration.

## Portable experiment runtime

Plan 04 established a config-driven runtime under
`src/edu_benchmark/experiment_runtime/`. Runtime YAML files use only
repository-relative paths. Loading fails closed on path escape, missing files,
checksum/count mismatch, unknown fields, or serialized credential material.

The representative Section V config is
`experiments/20260806_145124/configs/section-v-ablation-v1.yaml`. Preflight and
execution use the same command from the repository root or another working
directory after the editable package is installed:

```bash
/workspace/quannd/miniconda3/envs/benchmark_env/bin/python \
  -m edu_benchmark.experiment_runtime preflight \
  --config experiments/20260806_145124/configs/section-v-ablation-v1.yaml

/workspace/quannd/miniconda3/envs/benchmark_env/bin/python \
  -m edu_benchmark.experiment_runtime run \
  --config experiments/20260806_145124/configs/section-v-ablation-v1.yaml
```

This representative run is offline and requires no provider credential. Its
two large judge JSONL inputs remain historical experiment artifacts rather than
clean-clone CI fixtures; unit tests use self-contained temporary fixtures.
Running preflight after a completed run preserves the completed manifest.
Preflight returns `preflight_passed` only after the supported pipeline, runner,
input roles/formats, output schemas, resume policy, parameters, and offline
provenance contract pass. A failure is machine-readable as `preflight_failed`
with exit code 2. For a preserved completed manifest, preflight reports whether
it matches the current fingerprint. Validation recomputes that fingerprint and
checks the recorded config, inputs, outputs, code provenance,
resume/equivalence contracts, secret scan, and result hashes against the
current repository state.

## Config-driven requirement scoring

Requirement-scoring CLIs require the repository-relative YAML config at
`experiments/20260806_145124/configs/requirement-scoring-20260727-v1.yaml`.
The config owns the inherited experiment ID, paths, provider/model settings,
seeds, bundle names, concurrency, request ceilings, and retry defaults; explicit
CLI arguments override configured values. The business package contains no
hard-coded `20260727_170150` paths. New run manifests record the config ID,
portable path, and SHA-256.

P05-A003 also locks `include_thoughts=true` for current Gemini requirement,
target-generation, synchronous-judge, and batch-judge paths. Requirement
scoring retries only provider failures classified as retryable and model
responses that fail the task schema; unknown or non-retryable failures stop for
that candidate without discarding already appended JSONL responses.


## Project Python environment

The required project environment is the Conda environment `benchmark_env`. The current remote development machine is Ubuntu, so use the Linux executable by default:

```text
Linux (current server): /workspace/quannd/miniconda3/envs/benchmark_env/bin/python
Windows: D:\conda-envs\benchmark_env\python.exe
```

Activate it before installing packages or running Python tools:

```bash
conda activate benchmark_env
python -c "import sys; print(sys.executable)"
```

The executable must resolve to one of the paths above. All package installation, Python scripts, validators, and tests must use `benchmark_env`. Do not use Conda base or system Python. For reproducible commands, use the absolute interpreter path.

Create the environment from the repository root:

```bash
conda env create -f environment.yml
conda activate benchmark_env
```

For an existing `benchmark_env`, synchronize direct dependencies and install
the src-layout package editable:

```powershell
D:\conda-envs\benchmark_env\python.exe -m pip install -r requirements.txt
D:\conda-envs\benchmark_env\python.exe -m pip install --no-deps -e .
```

```bash
/workspace/quannd/miniconda3/envs/benchmark_env/bin/python -m pip install -r requirements.txt
/workspace/quannd/miniconda3/envs/benchmark_env/bin/python -m pip install --no-deps -e .
```

`pyproject.toml` separates core, `dev`, and `providers` dependency groups.
`requirements.txt` intentionally installs their union for the current full
runner environment. Direct dependencies and Python 3.12 are pinned; transitive
pip/Conda packages are not yet fully locked, so `environment.yml` is not a
bit-for-bit lockfile.

The offline GitHub Actions workflow has two clean-clone lanes. The first installs
only `.[dev]` and runs provider-independent tests. The second installs the full
runner requirements and runs self-contained offline tests without credentials.
Tests that consume intentionally ignored raw XLSX or experiment JSONL remain
local integration tests and are not clean-clone CI gates.

After installation, verify import portability from outside the repository:

```bash
cd /tmp
/workspace/quannd/miniconda3/envs/benchmark_env/bin/python -I -c \
  "from edu_benchmark import model_providers, requirement_scoring; print(model_providers.__file__); print(requirement_scoring.__file__)"
```

The earlier PaddleOCR, VietOCR, and MinerU extraction attempts did not become a
supported repository workflow. Their experimental code, tests, and environment
files are retained only in the project lead's ignored local workspace for
historical reference; they are not part of the tracked package or the
`benchmark_env` reproducibility contract. Do not rely on those local files from
a clean clone. The active SGK/SGV retrieval path consumes the registered Nguyen
OCR Markdown. Plan 03 has replaced the draft SBT full-book units with 53 lessons
and two tables of contents in the active OCR manifest. SBT remains discoverable
only at source-metadata level and is deliberately excluded from fragment/FTS
retrieval until a later content-review plan authorizes it.

## HNMU v5.6 source-batch audit

Experiment `20260903_135547` P03-A024 wraps the existing v5.6 dialogue-audit
runtime as source-scoped batches without changing reusable code. The immutable
source contract, derived seven-column workbooks, normalized 1,948-row snapshot,
balanced selection shards, per-shard configs, source runner, and offline exporter
live under that experiment. Start with
`experiments/20260903_135547/runbooks/plan03-gemini-tool-calling-pilot.md`
section 0.9. The shell runner accepts exactly one source key, stores logs and
outputs under the same source directory, and never advances to another source
automatically. Human-facing completed results are exported to XLSX; CSV/JSON
remain machine/provenance artifacts. Model execution remains an explicit,
project-lead-owned `--execute-api` action.

Completed v5.6 source exports currently cover `lop8_lan2` (280 samples),
`tin6_bai6_11` (84 samples), and `lop6_lan2` (153 samples). The primary
human-review workbook for `lop6_lan2` is
`experiments/20260903_135547/outputs/plan03_v5_6_batches/lop6_lan2/recovered_batch/exports/audit_results.xlsx`;
its validated machine artifacts contain 2,754 criterion results and 153 sample
summaries with no missing or duplicate sample-criterion pair.

The cross-source diagnostic report for the three completed v5.6 batches is at
`experiments/20260903_135547/reports/plan03-v5-6-three-source-audit-analysis.md`.
It analyzes 517 samples and 9,306 criterion results, while keeping the current
audit outputs unchanged and explicitly separating raw-data defects from
missing learning-resource evidence.

## Validate current specialists

Linux / current Ubuntu remote:

```bash
/workspace/quannd/miniconda3/envs/benchmark_env/bin/python \
  /home/quannda/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  agents/research-methodologist
/workspace/quannd/miniconda3/envs/benchmark_env/bin/python \
  /home/quannda/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  agents/learning-resource-curator
/workspace/quannd/miniconda3/envs/benchmark_env/bin/python \
  /home/quannda/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  agents/benchmark-specification-designer
/workspace/quannd/miniconda3/envs/benchmark_env/bin/python \
  /home/quannda/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  agents/hnmu-dialogue-auditor
/workspace/quannd/miniconda3/envs/benchmark_env/bin/python \
  /home/quannda/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  agents/teacher-collaboration-designer
/workspace/quannd/miniconda3/envs/benchmark_env/bin/python -m pytest tests/agents -q
```


Windows reference:

```powershell
D:\\conda-envs\\benchmark_env\\python.exe `
  C:\\Users\\Admin\\.codex\\skills\\.system\\skill-creator\\scripts\\quick_validate.py `
  agents/research-methodologist
D:\\conda-envs\\benchmark_env\\python.exe `
  C:\\Users\\Admin\\.codex\\skills\\.system\\skill-creator\\scripts\\quick_validate.py `
  agents/learning-resource-curator
D:\\conda-envs\\benchmark_env\\python.exe `
  C:\\Users\\Admin\\.codex\\skills\\.system\\skill-creator\\scripts\\quick_validate.py `
  agents/benchmark-specification-designer
D:\\conda-envs\\benchmark_env\\python.exe `
  C:\\Users\\Admin\\.codex\\skills\\.system\\skill-creator\\scripts\\quick_validate.py `
  agents/teacher-collaboration-designer
D:\\conda-envs\\benchmark_env\\python.exe -m pytest tests/agents -q
```

Runtime smoke testing must be performed in an interactive Codex CLI/App session using native subagent tools. It is not run through `codex exec`.

## Working agreements

Agents and contributors must follow [AGENTS.md](AGENTS.md). Architecture changes must update [ARCHITECTURE.md](ARCHITECTURE.md) in the same commit.

Last verified during experiment `20260817_160800` Plan 01 on 2026-08-17:
PL-REQ deterministic validation, shared-registry validation and all 309 offline
tests passed on the current server.
