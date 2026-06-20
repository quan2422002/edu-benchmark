# Kế hoạch xây dựng benchmark gia sư LLM môn Tin học lớp 9

> **Trạng thái tài liệu:** Kế hoạch tổng này được giữ làm tài liệu nền và lịch sử quyết định. Từ ngày 20/06/2026, việc duyệt và triển khai sử dụng các plan mô-đun tại [experiments/20260620_115236/roadmap.md](../20260620_115236/roadmap.md). Không dùng riêng tài liệu này để phê duyệt một đợt cài đặt mới.

## 0. Trạng thái tài liệu

- Mã kế hoạch: `20260618_150902`
- Ngày lập: 2026-06-18, múi giờ Asia/Ho_Chi_Minh
- Cập nhật phạm vi: 2026-06-18, sau khi thống nhất với giáo sư hướng dẫn
- Trạng thái: `SUPERSEDED_BY_MODULAR_PLANS`
- Phạm vi của kế hoạch: thiết kế kiến trúc dự án, quy trình nghiên cứu, codebase, specialist agents, dữ liệu dùng chung và hệ thống thử nghiệm.
- Chưa được phép triển khai: không tạo code sản phẩm, agent, dataset hoặc pipeline đánh giá trước khi người dùng chuyển trạng thái kế hoạch thành `APPROVED`.

## 1. Tóm tắt đề xuất

Phiên bản đầu tiên nên tập trung vào một bài toán đủ hẹp để tạo đóng góp khoa học rõ ràng:

> Đánh giá năng lực sư phạm của LLM khi đóng vai gia sư môn Tin học lớp 9 bằng tiếng Việt, ưu tiên chẩn đoán lỗi, phản hồi gợi mở và hỗ trợ học chủ động trong hội thoại.

Phiên bản đầu tiên không phải benchmark giáo dục tổng quát, cũng không bao phủ toàn bộ cấp THCS. Phạm vi nghiên cứu đã được khóa vào môn Tin học lớp 9. Kiến trúc và schema vẫn phải cho phép mở rộng về sau sang các lớp, cấp học và môn học khác mà không phải viết lại phần lõi.

Đóng góp khoa học mục tiêu:

1. Bộ taxonomy và rubric dành riêng cho gia sư môn Tin học lớp 9 bằng tiếng Việt.
2. Bộ test case bám theo chương trình/giáo trình Tin học lớp 9, lỗi sai của học sinh và rubric riêng cho từng mẫu.
3. Đánh giá đồng thời tính đúng đắn chuyên môn, khả năng hiểu học sinh và chiến lược sư phạm.
4. Quy trình đánh giá lai: luật xác định + LLM judge + chuyên gia con người, có kiểm định độ tin cậy.
5. Hỗ trợ multi-turn và theo dõi việc mô hình có điều chỉnh hướng dẫn theo phản hồi của học sinh hay không.

## 2. Căn cứ đã khảo sát

### 2.1. Slide dự án

Slide xác định bốn nhóm tiêu chí rộng:

- năng lực học thuật và tư duy;
- năng lực sư phạm và tương tác;
- an toàn, đạo đức và guardrails;
- hiệu năng kỹ thuật và bản địa hóa.

Phần cụ thể nhất của slide tập trung vào gia sư Tin học THCS. Sau buổi trao đổi với giáo sư hướng dẫn, phiên bản đầu tiên được thu hẹp tiếp vào lớp 9, với các hành vi:

- không đưa code hoàn chỉnh ngay khi học sinh cần được hướng dẫn tư duy;
- dùng câu hỏi gợi mở, pseudocode hoặc phân rã bài toán;
- nhận diện lỗi cú pháp, logic và lỗi biên;
- liên kết phản hồi với giáo trình;
- hướng dẫn học sinh tự sửa;
- nhắc an toàn số và liêm chính học thuật khi phù hợp.

### 2.2. Hai công trình tham chiếu

`MathTutorBench` chia năng lực thành chuyên môn, hiểu học sinh và năng lực sư phạm; đồng thời chỉ ra rằng giải bài giỏi không đồng nghĩa dạy tốt và chất lượng có thể giảm trong hội thoại dài.

`TutorBench` tổ chức dữ liệu quanh ba use case: giải thích thích ứng, đánh giá/phản hồi và hỗ trợ học chủ động. Mỗi mẫu có rubric riêng và được chấm bằng LLM judge đã qua kiểm tra.

Khoảng trống phù hợp với dự án:

- tiếng Việt và ngữ cảnh chương trình Việt Nam;
- Tin học lớp 9 trong bối cảnh giáo dục Việt Nam thay vì Toán hoặc STEM bậc THPT/AP;
- lỗi lập trình và tư duy thuật toán có thể kiểm tra bằng execution/static analysis;
- gắn rubric sư phạm với trạng thái kiến thức của học sinh;
- đánh giá multi-turn và khả năng “fading scaffolding”, tức giảm dần trợ giúp khi học sinh tiến bộ.

## 3. Các điểm cần phản biện và điều chỉnh

### 3.1. Phạm vi hiện tại quá rộng

Một benchmark đồng thời bao phủ đa môn, nhiều cấp học, sư phạm, an toàn, bản địa hóa, latency và cost sẽ cần nhiều nhóm chuyên gia và khó tạo một luận điểm khoa học sắc nét.

Phạm vi đã thống nhất:

- phiên bản đầu chỉ gồm môn Tin học lớp 9 bằng tiếng Việt;
- tập chủ đề cụ thể phải được chọn từ chương trình và nguồn giáo trình lớp 9 đã xác định, thay vì mặc định lấy toàn bộ kiến thức lập trình phổ thông;
- các tiêu chí hệ thống như latency/cost được báo cáo riêng, không trộn vào điểm sư phạm;
- các track an toàn chuyên sâu được thiết kế mở rộng sau khi lõi sư phạm ổn định;
- manifest cấp dataset phải có `schema_version`, `subject`, `grade` và nguồn chương trình; mỗi sample giữ `topic` ở dạng dễ hiểu. Cách tách hai tầng này cho phép mở rộng sang lớp hoặc môn khác mà không làm phức tạp biểu mẫu của giáo viên.

### 3.2. Quy tắc “tuyệt đối không viết code cho học sinh” quá cứng

Đưa code có thể là hành vi sư phạm phù hợp trong một số ngữ cảnh: minh họa cú pháp, so sánh hai cách giải, đưa ví dụ tối giản, hoặc sau khi học sinh đã thử và yêu cầu lời giải mẫu. Cấm tuyệt đối sẽ thưởng cho mô hình né tránh thay vì dạy tốt.

Đề xuất chấm “mức độ tiết lộ đáp án được hiệu chỉnh theo ngữ cảnh”:

- giai đoạn đầu: ưu tiên câu hỏi chẩn đoán và gợi ý;
- sau nỗ lực của học sinh: cho phép hint cụ thể hoặc đoạn code khuyết;
- khi kết thúc: có thể cung cấp lời giải mẫu kèm giải thích và câu hỏi kiểm tra hiểu biết;
- phạt việc đưa lời giải hoàn chỉnh quá sớm, không phạt mọi trường hợp có code.

### 3.3. Gian lận học tập không đồng nhất với an toàn

Prompt “làm hộ để chép” thuộc liêm chính học thuật và chiến lược sư phạm. Nội dung bạo lực, tự hại, tình dục, dữ liệu cá nhân và hành vi nguy hiểm thuộc safety. Trộn hai nhóm làm rubric khó diễn giải.

Đề xuất tách:

- `pedagogical_integrity`: không làm thay, chuyển thành hướng dẫn học;
- `student_safety`: bảo vệ trẻ vị thành niên và xử lý nội dung nguy hiểm;
- `digital_citizenship`: mật khẩu, bản quyền, lừa đảo, quyền riêng tư.

### 3.4. Chất lượng câu trả lời không chứng minh hiệu quả học tập

Benchmark phản hồi có thể đo chất lượng hành vi gia sư, nhưng chưa thể khẳng định học sinh học tốt hơn. Muốn tuyên bố learning gain cần nghiên cứu với người học, pre-test/post-test và quy trình đạo đức riêng.

Đề xuất:

- paper đầu chỉ tuyên bố đánh giá `tutoring behavior`;
- learner study là pha độc lập sau khi benchmark ổn định;
- mọi kết luận phải phân biệt proxy metric với learning outcome.

### 3.5. LLM-as-a-judge không được dùng như nguồn chân lý duy nhất

Judge có thể thiên vị độ dài, phong cách, họ model và đáp án tham chiếu. Điểm cao chưa chắc tương ứng với đánh giá của giáo viên.

Đề xuất:

- rubric phải atomic, kiểm chứng được và có ví dụ biên;
- tạo human gold set do ít nhất hai annotator chấm độc lập;
- báo Cohen's kappa hoặc Krippendorff's alpha tùy cấu trúc nhãn;
- đánh giá precision/recall/agreement của judge trên gold set;
- thử nhiều judge hoặc thay đổi thứ tự đầu vào để kiểm tra độ nhạy;
- giữ một phần test ẩn để giảm overfitting và contamination.

### 3.6. Cấu trúc thử nghiệm dạng cây chưa đủ

Một thử nghiệm có nhiều cha tạo thành DAG, không còn là cây. Chỉ dùng timestamp làm tên không biểu diễn quan hệ, cấu hình, phiên bản dữ liệu hoặc commit.

Đề xuất:

- vẫn giữ thư mục theo format `YYYYMMDD_HHMMSS`;
- thêm `metadata.yaml` chứa `parents`, `task`, `agent`, `status`, `git_commit`, `dataset_version`, `config`, `seed`;
- thêm registry `experiments/index.yaml`;
- kết quả đã công bố phải immutable; thử nghiệm kế thừa tạo node mới thay vì sửa node cũ.

### 3.7. “Agent luôn sống từ đầu phiên” không thể bảo đảm xuyên nền tảng

Định nghĩa agent trên đĩa không đồng nghĩa có một process/model đang chạy. Lifecycle phụ thuộc runtime:

- Codex hỗ trợ custom agents và thread con, nhưng chỉ spawn khi workflow yêu cầu rõ ràng.
- Claude Code có project subagents và agent teams, nhưng subagent vẫn chạy trong session/runtime và có vòng đời riêng.
- Việc giữ tất cả agent chạy thường trực gây tốn token, tăng context, tăng xung đột ghi file và không có lợi khi phần lớn agent chưa có việc.

Thiết kế thay thế:

1. Mọi specialist được đăng ký và discover ngay khi phiên bắt đầu.
2. Orchestrator chạy health check và hiển thị agent registry.
3. Chỉ spawn/resume agent cần thiết theo task.
4. Trạng thái bền vững nằm trong file chuẩn hóa, không phụ thuộc trí nhớ của thread.
5. Runtime nào hỗ trợ agent team có thể bật `warm_pool`, nhưng đây là adapter tùy chọn, không phải điều kiện đúng của hệ thống.

### 3.8. `agents/<name>/SKILL.md` chưa đủ để Codex và Claude tự nhận diện

Hai runtime dùng adapter và vị trí khám phá khác nhau. Không nên sao chép thủ công cùng một nội dung vào nhiều nơi vì sẽ nhanh chóng lệch phiên bản.

Đề xuất:

- `agents/<role>/` là nguồn sự thật trung lập nền tảng;
- sinh adapter Codex vào `.codex/agents/` và skill discovery vào `.agents/skills/`;
- sinh adapter Claude vào `.claude/agents/`;
- dùng `AGENTS.md` làm chỉ dẫn chung; `CLAUDE.md` import `AGENTS.md` và chỉ bổ sung khác biệt của Claude;
- viết validator để phát hiện adapter lỗi thời.

## 4. Các quyết định phạm vi và vấn đề còn cần chốt

### 4.1. Quyết định đã xác nhận

- Bài toán nghiên cứu: benchmark năng lực gia sư của LLM.
- Môn học: Tin học.
- Cấp/lớp của phiên bản đầu: lớp 9.
- Ngôn ngữ tương tác chính: tiếng Việt.
- Đối tượng đánh giá: hành vi và năng lực sư phạm của mô hình, không mặc định suy rộng thành learning gain của học sinh.
- Hướng phát triển: kiến trúc mở để bổ sung lớp khác, cấp học khác và môn học khác trong các phiên bản sau.

Các quyết định trên là ràng buộc của phiên bản đầu, không còn là câu hỏi mở.

### 4.2. Các quyết định còn cần chốt trước khi tạo dataset

1. Tên làm việc: `Vietnamese CS Tutor Benchmark` hay tên khác.
2. Chương trình, bộ sách hoặc giáo trình Tin học lớp 9 nào là nguồn chuẩn; phiên bản/năm áp dụng và điều kiện bản quyền.
3. Các chủ đề lớp 9 được đưa vào benchmark v1 và tiêu chí đảm bảo độ phủ chương trình.
4. Ngôn ngữ lập trình xuất hiện trong chương trình/giáo trình đã chọn; có cần nhiều ngôn ngữ trong v1 hay không.
5. Có giáo viên/chuyên gia Tin học lớp 9 tham gia viết, review và chấm rubric hay không.
6. Mức ngân sách cho API model và human annotation.
7. Dữ liệu có chứa bài làm thật của học sinh lớp 9 hay chỉ dùng dữ liệu do chuyên gia tạo và dữ liệu synthetic có kiểm soát.
8. Mục tiêu venue và mốc submission dự kiến để lập timeline ngược.

Giá trị mặc định được dùng nếu kế hoạch được duyệt mà chưa sửa:

- môn Tin học lớp 9 bằng tiếng Việt;
- chưa khóa Python hay C++ cho tới khi hoàn tất ánh xạ chương trình/giáo trình lớp 9;
- không thu thập dữ liệu học sinh thật trong MVP;
- expert-authored + controlled synthetic student errors;
- benchmark hành vi gia sư, chưa tuyên bố learning gain;
- repository Python 3.11+, package manager `uv`, test bằng `pytest`.

## 5. Câu hỏi nghiên cứu đề xuất

- `RQ1`: Các LLM hiện đại có chẩn đoán đúng lỗi và misconception của học sinh lớp 9 trong môn Tin học bằng tiếng Việt không?
- `RQ2`: Năng lực giải bài/lập trình có tương quan như thế nào với năng lực phản hồi sư phạm?
- `RQ3`: Chất lượng scaffolding thay đổi ra sao theo độ dài hội thoại và mức độ tiến bộ của học sinh?
- `RQ4`: Rubric theo từng mẫu và judge tự động có đồng thuận đủ cao với giáo viên hay không?
- `RQ5`: Việc cung cấp ngữ cảnh chương trình/giáo trình Tin học lớp 9 có cải thiện tính phù hợp lứa tuổi, độ chính xác và chất lượng gợi mở không?

## 6. Taxonomy MVP

### A. Chuyên môn Tin học

- correctness của kiến thức, thuật ngữ và artifact thuộc chương trình Tin học lớp 9;
- nhận diện cú pháp và semantics khi task có lập trình;
- chạy/giải thích trace khi nội dung chương trình yêu cầu;
- phát hiện lỗi cú pháp, runtime, logic hoặc misconception theo từng chủ đề lớp 9;
- phân rã bài toán và tư duy thuật toán ở mức phù hợp với học sinh lớp 9.

### B. Hiểu trạng thái học sinh

- xác định câu trả lời đúng/sai;
- định vị lỗi đầu tiên;
- phân loại lỗi: syntax, runtime, logic, misconception, careless error;
- suy ra mức hiểu hiện tại từ hội thoại;
- không giả định sai về nguyên nhân lỗi.

### C. Hành vi sư phạm

- hỏi để chẩn đoán trước khi kết luận khi thiếu dữ kiện;
- scaffolding theo mức: prompt → hint → partial solution → worked example;
- khuyến khích tự sửa;
- điều chỉnh ngôn ngữ theo trình độ và kiến thức tiên quyết của học sinh lớp 9;
- quản lý tải nhận thức;
- kiểm tra lại mức hiểu;
- liên kết giáo trình khi ngữ cảnh cho phép;
- fading scaffolding qua nhiều lượt.

### D. Liêm chính và an toàn

- xử lý yêu cầu làm hộ/chép bài;
- bảo vệ dữ liệu cá nhân;
- an toàn số;
- bản quyền và sử dụng phần mềm;
- từ chối nội dung nguy hiểm nhưng vẫn đưa hướng hỗ trợ phù hợp.

### E. Thuộc tính hệ thống, báo cáo riêng

- latency;
- token usage và chi phí;
- lỗi API;
- khả năng tái lập;
- phiên bản model và ngày chạy.

Không tạo một điểm tổng duy nhất trong MVP. Báo cáo profile theo dimension và macro/micro average có khoảng tin cậy.

## 7. Thiết kế dataset và task

### 7.1. Đơn vị dữ liệu

Thiết kế ban đầu dùng hai tầng để tránh lặp metadata và giúp giáo viên chỉ tập trung vào nội dung chuyên môn:

1. `dataset.yaml`: khai báo một lần các thông tin chung của toàn bộ bộ dữ liệu.
2. `samples.yaml`: chứa các tình huống mà giáo viên biên soạn.

#### 7.1.1. Metadata cấp dataset

```yaml
schema_version: "0.1"
name: grade_9_informatics_tutor_v0
subject: Tin học
grade: 9
language: vi
curriculum_source: null
```


| Trường            | Ý nghĩa                                                                                  |
| ------------------- | ------------------------------------------------------------------------------------------ |
| `schema_version`    | Phiên bản cấu trúc dữ liệu, dùng khi cần nâng cấp hoặc migration.               |
| `name`              | Tên kỹ thuật của bộ dữ liệu.                                                        |
| `subject`           | Môn học áp dụng cho toàn bộ dataset.                                                 |
| `grade`             | Lớp học áp dụng cho toàn bộ dataset.                                                 |
| `language`          | Ngôn ngữ chính của tương tác học sinh–gia sư.                                    |
| `curriculum_source` | Chương trình/bộ sách/giáo trình tham chiếu; để`null` cho tới khi được chốt. |

Các trường trên không lặp lại trong từng sample. Khi dự án mở rộng sang môn hoặc lớp khác, tạo dataset/manifest mới thay vì trộn nhiều lớp vào benchmark v1.

#### 7.1.2. Cấu trúc tối thiểu của một sample

```yaml
- id: cs9_0001
  topic: "Tên chủ đề dễ hiểu với giáo viên"
  student_prompt: |
    Câu hỏi hoặc lời nhờ trợ giúp của học sinh.
  student_work: null
  criteria:
    - "Một hành vi quan sát được mà câu trả lời tốt cần thực hiện."
    - "Một điều câu trả lời không nên làm."
  example_response: null
  extensions: {}
```

Chỉ có bốn trường bắt buộc:


| Trường         | Bắt buộc | Người điền               | Ý nghĩa                                                                                         |
| ---------------- | ---------: | ---------------------------- | ------------------------------------------------------------------------------------------------- |
| `id`             |        Có | Hệ thống có thể tự sinh | Mã duy nhất và ổn định của sample.                                                         |
| `topic`          |        Có | Giáo viên                  | Tên bài/chủ đề theo cách giáo viên đang sử dụng; chưa cần ontology phức tạp.       |
| `student_prompt` |        Có | Giáo viên                  | Nội dung chính xác mà học sinh nói hoặc hỏi gia sư.                                      |
| `criteria`       |        Có | Giáo viên                  | Danh sách ngắn các hành vi quan sát được để nhận biết câu trả lời đạt yêu cầu. |

Ba trường tùy chọn:


| Trường           | Khi nào dùng                                                             | Ý nghĩa                                                                                      |
| ------------------ | -------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `student_work`     | Khi học sinh gửi code, đáp án, lập luận hoặc sản phẩm đang làm | Giữ nguyên bài làm để mô hình chẩn đoán. Có thể là text hoặc code nhiều dòng. |
| `example_response` | Khi giáo viên muốn minh họa một cách phản hồi tốt                 | Chỉ là ví dụ tham khảo, không phải đáp án duy nhất.                                 |
| `extensions`       | Khi thử nghiệm cần thông tin chưa có trong schema lõi               | Không gian mở rộng có kiểm soát; giai đoạn đầu mặc định là`{}`.                  |

Ở bước biên soạn, giáo viên không cần điền weight, polarity, error taxonomy, split, author id, reviewer id hoặc model-facing metadata. Các thông tin vận hành này được hệ thống bổ sung ở pha chuẩn hóa/evaluation, sau khi thiết kế ban đầu đã được kiểm chứng.

YAML là định dạng lưu trữ chuẩn, không bắt buộc là giao diện nhập liệu. Trong đợt thu thập đầu, giáo viên có thể dùng [dataset_v0/teacher_template.csv](dataset_v0/teacher_template.csv) với các cột `topic`, `student_prompt`, `student_work`, `criterion_1` đến `criterion_5` và `example_response`. Công cụ nhập dữ liệu sẽ sinh `id`, bỏ các criterion trống, gom criterion thành danh sách và xuất sang YAML. `extensions` không hiển thị cho giáo viên khi chưa cần dùng.

#### 7.1.3. Quy tắc viết `criteria`

- Mỗi criterion là một câu ngắn, dùng ngôn ngữ chuyên môn quen thuộc với giáo viên.
- Mỗi criterion mô tả một hành vi có thể quan sát và chấm được.
- Tách riêng điều cần làm và điều cần tránh; không gộp nhiều yêu cầu không liên quan vào một câu.
- Không yêu cầu giáo viên gán trọng số trong bản đầu.
- Nên có 2–5 criteria cho một sample; nếu nhiều hơn, cân nhắc tách thành hai tình huống.

Ví dụ tốt:

- “Chỉ ra rằng dòng `print` chưa được thụt vào trong khối `if`.”
- “Đặt ít nhất một câu hỏi để học sinh tự nhận ra quy tắc thụt lề.”
- “Không đưa ngay toàn bộ đoạn code đã sửa nếu học sinh chưa thử sửa.”

Ví dụ chưa tốt:

- “Phản hồi hay, đầy đủ, dễ hiểu và có tính sư phạm.”

Câu chưa tốt chứa nhiều khái niệm chủ quan và không chỉ ra người chấm cần quan sát điều gì.

#### 7.1.4. Khả năng mở rộng mà không phá dữ liệu cũ

- Giữ ổn định bốn trường lõi; không đổi tên hoặc xóa chúng trong cùng major version.
- Trường mới ở cấp root phải là tùy chọn, vì sample cũ không có trường đó vẫn phải hợp lệ.
- Metadata thử nghiệm trước tiên đặt trong `extensions`, ví dụ `extensions.error_type` hoặc `extensions.student_profile`.
- Chỉ đưa một trường ra khỏi `extensions` thành trường chuẩn sau khi đã dùng ổn định và đội ngũ xác nhận nó cần thiết cho phần lớn sample.
- `schema_version` đặt ở manifest, không lặp trong từng sample.
- Thay đổi tương thích ngược tăng minor version (`0.1` → `0.2`); thay đổi buộc migration mới tăng major version (`0.x` → `1.0`).
- Công cụ đọc dữ liệu phải chấp nhận sample thiếu trường tùy chọn và giữ nguyên trường mở rộng chưa biết khi đọc–ghi lại.

#### 7.1.5. Mẫu minh họa sơ khởi

Mẫu dưới đây giúp giáo viên hình dung cách biên soạn, chưa đại diện cho độ phủ cuối cùng của chương trình Tin học lớp 9.

**Mẫu 1 — Chẩn đoán lỗi và gợi mở tự sửa**

```yaml
- id: cs9_0001
  topic: "Thụt lề trong câu lệnh điều kiện"
  student_prompt: "Code của em bị lỗi gì mà không chạy ạ?"
  student_work: |
    x = 10
    if x > 5:
    print("x lớn hơn 5")
  criteria:
    - "Xác định lỗi nằm ở việc dòng print chưa được thụt vào trong khối if."
    - "Giải thích ngắn gọn vai trò của thụt lề."
    - "Yêu cầu học sinh thử tự sửa trước khi đưa code hoàn chỉnh."
  example_response: |
    Em hãy nhìn dòng ngay sau dấu hai chấm của câu lệnh if nhé. Trong Python,
    lệnh thuộc khối if cần được đặt lùi vào trong. Em thử thêm thụt lề trước
    dòng print rồi chạy lại xem thông báo lỗi có còn không?
  extensions: {}
```

Tài liệu ngắn dành cho giáo viên và đủ ba mẫu được đặt tại [dataset_design_v0.md](dataset_design_v0.md) và [dataset_v0/samples.yaml](dataset_v0/samples.yaml).

### 7.2. Task families

1. `explain_concept`: giải thích thích ứng cho học sinh lớp 9.
2. `diagnose_error`: tìm và giải thích lỗi.
3. `give_feedback`: phản hồi bài làm mà không chiếm quyền giải.
4. `active_hinting`: tạo hint đúng mức.
5. `socratic_decomposition`: dẫn dắt phân rã thuật toán.
6. `multi_turn_tutoring`: thích ứng qua nhiều lượt.
7. `academic_integrity`: chuyển yêu cầu làm hộ thành hoạt động học.
8. `curriculum_grounding`: dùng đúng khái niệm và cách gọi của giáo trình.

### 7.3. Nguồn dữ liệu

- câu hỏi do chuyên gia tạo;
- lỗi sai do chuyên gia thiết kế dựa trên misconception thường gặp của học sinh lớp 9;
- lỗi biến đổi có kiểm soát từ chương trình đúng;
- hội thoại synthetic chỉ được dùng sau khi chuyên gia duyệt;
- không tự động lấy bài tập có bản quyền hoặc dữ liệu học sinh từ Internet.

### 7.4. Chống contamination

- công khai dev set và giữ hidden test;
- lưu hash của sample;
- không đưa hidden test vào prompt phát triển;
- tạo nhiều template và biến thể tham số;
- ghi nhận ngày phát hành và model cutoff nếu biết;
- kiểm tra near-duplicate giữa train/dev/test.

## 8. Thiết kế đánh giá

### 8.1. Ba lớp metric

`Deterministic`:

- compile/execute code trong sandbox;
- unit test;
- so khớp error location/type;
- kiểm tra tiết lộ code/đáp án;
- format và schema validation.

`Rubric judge`:

- chấm pass/fail hoặc ordinal cho từng criterion;
- judge không nhìn tên model;
- randomize vị trí khi pairwise;
- lưu đầy đủ raw judgment và rationale.

`Human evaluation`:

- double annotation trên gold subset;
- adjudication khi bất đồng;
- đo inter-rater reliability;
- hiệu chuẩn annotator bằng pilot set.

### 8.2. Báo cáo thống kê

- bootstrap confidence interval;
- paired comparison trên cùng sample;
- effect size, không chỉ p-value;
- phân tích theo chủ đề lớp 9, mức độ thành thạo, task, loại lỗi và số lượt;
- sensitivity analysis theo judge;
- error taxonomy và qualitative cases.

### 8.3. Baseline

- direct-answer baseline;
- generic helpful assistant prompt;
- explicit Socratic tutoring prompt;
- curriculum-grounded prompt;
- ít nhất một open-weight model và một frontier API model;
- human tutor response trên subset dùng làm reference ceiling, không coi là đáp án duy nhất.

## 9. Kiến trúc repository mục tiêu

```text
.
├── AGENTS.md
├── CLAUDE.md
├── pyproject.toml
├── configs/
│   ├── datasets/
│   ├── evaluations/
│   ├── judges/
│   └── models/
├── src/
│   └── edu_benchmark/
│       ├── cli/
│       ├── schemas/
│       ├── datasets/
│       ├── curriculum/
│       ├── code_analysis/
│       ├── inference/
│       ├── judges/
│       ├── metrics/
│       ├── experiments/
│       └── reporting/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── agents/
│   └── <specialist>/
│       ├── SKILL.md
│       ├── agent.yaml
│       ├── scripts/
│       └── references/
├── .agents/
│   └── skills/
├── .codex/
│   └── agents/
├── .claude/
│   └── agents/
├── experiments/
│   ├── index.yaml
│   └── YYYYMMDD_HHMMSS/
│       ├── metadata.yaml
│       ├── plan.md
│       ├── handoffs/
│       ├── configs/
│       ├── results/
│       ├── logs/
│       └── report.md
├── shared/
│   ├── datasets/
│   │   ├── manifests/
│   │   └── README.md
│   ├── schemas/
│   ├── rubrics/
│   ├── prompts/
│   ├── curriculum/
│   ├── registries/
│   ├── templates/
│   └── glossary/
├── utils/
│   ├── bootstrap/
│   ├── validation/
│   ├── experiment/
│   ├── provenance/
│   └── adapters/
└── document/
```

Nguyên tắc:

- code import được đặt trong `src`, không đặt logic nghiệp vụ ở `utils`;
- `utils` chỉ chứa công cụ vận hành repo và script nhỏ không thuộc package;
- `shared` chứa contract/tài nguyên dùng chung, không chứa bản sao code;
- dataset lớn, dữ liệu nhạy cảm và raw model output không mặc định commit vào Git;
- mọi artifact phải có manifest, checksum, license/provenance.

## 10. Specialist agents tối thiểu

### 10.1. `research-methodologist`

Vai trò:

- tổng hợp literature;
- xác định novelty, research question và threat to validity;
- duy trì evidence matrix và paper outline.

Công cụ dự kiến:

- trích metadata/tables từ paper;
- kiểm tra citation;
- tạo evidence matrix;
- so sánh taxonomy benchmark.

### 10.2. `curriculum-domain-expert`

Vai trò:

- ánh xạ chương trình và giáo trình Tin học lớp 9;
- xác định prerequisite, misconception và độ khó của từng chủ đề lớp 9;
- kiểm tra tính đúng chuyên môn và phù hợp với học sinh lớp 9;
- bảo đảm mọi sample v1 truy vết được tới topic/learning objective của lớp 9.

Công cụ dự kiến:

- curriculum mapper;
- concept graph validator;
- topic coverage report.

### 10.3. `dataset-curator`

Vai trò:

- tạo, nhập, chuẩn hóa, phân chia và version hóa sample;
- kiểm tra provenance, license, duplicate và leakage.

Công cụ dự kiến:

- schema validator;
- deduplication;
- split builder;
- dataset manifest/checksum.

### 10.4. `rubric-annotation-specialist`

Vai trò:

- viết rubric atomic;
- xây annotation guide;
- pilot annotation, adjudication và quality control.

Công cụ dự kiến:

- rubric linter;
- annotation agreement;
- adjudication queue;
- rubric coverage report.

### 10.5. `evaluation-engineer`

Vai trò:

- model adapters;
- inference, retry, caching;
- deterministic checks và judge pipeline;
- lưu provenance đầy đủ.

Công cụ dự kiến:

- model runner;
- code sandbox runner;
- judge runner;
- cost/latency recorder.

### 10.6. `statistical-analyst`

Vai trò:

- thiết kế phân tích;
- confidence interval, significance/effect size;
- reliability và sensitivity analysis;
- bảng/biểu đồ phục vụ paper.

Công cụ dự kiến:

- bootstrap;
- paired tests;
- inter-rater metrics;
- reproducible table/plot generator.

### 10.7. `safety-ethics-reviewer`

Vai trò:

- privacy, minors, consent, data handling;
- risk taxonomy;
- kiểm tra academic integrity và digital safety;
- chuẩn bị ethics/data statement.

Công cụ dự kiến:

- PII scanner;
- risk checklist;
- license/consent audit.

### 10.8. `reproducibility-paper-editor`

Vai trò:

- audit experiment;
- kiểm tra claim-evidence;
- tạo model card/dataset card;
- đồng bộ bảng kết quả với bản thảo.

Công cụ dự kiến:

- artifact audit;
- result-to-table;
- claim traceability;
- reproducibility checklist.

Không spawn toàn bộ tám agent cho mọi task. Orchestrator chọn tối thiểu agent cần thiết và chỉ cho một agent quyền sở hữu mỗi file tại một thời điểm.

## 11. Contract chung cho specialist agent

Mỗi `agents/<name>/SKILL.md` phải ngắn, theo imperative form và mô tả:

- khi nào agent được dùng;
- input bắt buộc;
- output contract;
- quy trình;
- tiêu chí hoàn thành;
- các điều không được làm;
- reference nào cần đọc theo từng trường hợp.

`agent.yaml` trung lập nền tảng dự kiến gồm:

```yaml
name: dataset-curator
description: "..."
capabilities: [read, write_dataset, run_validation]
default_mode: plan_first
allowed_paths:
  - shared/datasets
  - experiments
required_checks:
  - schema
  - provenance
adapters:
  codex: true
  claude: true
```

Quy tắc plan-first:

1. Tạo experiment node và `plan.md`.
2. Không triển khai khi `metadata.status` là `draft` hoặc `rejected`.
3. Orchestrator gửi link plan cho người dùng.
4. Người dùng sửa trực tiếp hoặc phản hồi.
5. Agent cập nhật plan và changelog quyết định.
6. Chỉ chạy khi trạng thái là `approved`.
7. Mọi lệch đáng kể so với plan phải quay lại review.

Plan phải có:

- lý do;
- scope và out-of-scope;
- input/output;
- file sẽ tạo/sửa;
- thuật toán hoặc logic;
- command cài đặt/chạy/test;
- validation và acceptance criteria;
- rủi ro, rollback;
- cách bàn giao cho người thực hiện.

## 12. Hệ thống experiments dạng DAG

`metadata.yaml` dự kiến:

```yaml
id: "20260618_150902"
title: "Project architecture planning"
status: draft
task_type: planning
owner_agent: research-methodologist
parents: []
created_at: "2026-06-18T15:09:02+07:00"
git_commit: null
dataset_versions: []
config_files: []
artifacts: []
```

Lifecycle:

`draft → under_review → approved → running → completed`

Nhánh lỗi:

- `under_review → rejected → draft`;
- `running → failed`;
- `running → blocked`;
- `completed` là immutable.

Mỗi handoff là file Markdown hoặc YAML có:

- source agent;
- target agent;
- experiment id;
- dữ liệu đầu vào;
- kết quả đã có;
- quyết định và giả định;
- việc còn lại;
- artifact paths;
- checksum nếu có.

## 13. Thành phần đề xuất cho `shared`

- `datasets/manifests`: chỉ mục dữ liệu, version, checksum, license.
- `schemas`: JSON Schema/Pydantic contracts.
- `rubrics`: rubric library và criterion definitions.
- `prompts`: prompt template có version.
- `curriculum`: concept map và prerequisite của lớp 9, kèm nguồn chương trình/giáo trình được cấp phép.
- `registries`: model, dataset, judge, metric và agent registry.
- `templates`: plan, report, handoff, dataset card, model result card.
- `glossary`: thuật ngữ Việt–Anh và cách gọi thống nhất.

Không nên lưu:

- secret/API key;
- output API khối lượng lớn chưa nén/version hóa;
- dữ liệu học sinh định danh;
- code trùng với `src`.

## 14. Thành phần đề xuất cho `utils`

- `bootstrap`: kiểm tra Python, package manager, runtime adapter.
- `validation`: validate schema, config, agent, plan và experiment.
- `experiment`: tạo node, cập nhật index, kiểm tra DAG, đóng experiment.
- `provenance`: checksum, git state, environment snapshot.
- `adapters`: sinh cấu hình Codex/Claude từ agent canonical.

Các tiện ích ổn định và được import bởi pipeline sẽ chuyển vào `src/edu_benchmark`; `utils` không trở thành “sọt rác” cho hàm dùng chung.

## 15. Kế hoạch triển khai theo pha

### Pha 0 — Chốt research charter

Đầu ra:

- `PROJECT_CHARTER.md`;
- scope, RQ, contribution, out-of-scope;
- target venue/timeline;
- risk register;
- quyết định dữ liệu và ethics.

Nghiệm thu:

- mọi quyết định ở Mục 4 đã được trả lời;
- có định nghĩa thành công định lượng;
- research charter khóa rõ benchmark v1 vào môn Tin học lớp 9 bằng tiếng Việt;
- roadmap mở rộng không làm tăng scope của benchmark v1.

### Pha 1 — Nền tảng repository

Đầu ra:

- `pyproject.toml`, package skeleton, tests;
- `AGENTS.md`, `CLAUDE.md`;
- schemas/config conventions;
- experiment CLI và validator tối thiểu;
- CI lint/type/test.

Commands dự kiến:

```bash
uv sync --all-groups
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest
```

Nghiệm thu:

- fresh clone có thể cài và chạy test theo một tài liệu duy nhất;
- không phụ thuộc riêng Codex hoặc Claude.

### Pha 2 — Agent framework và adapters

Đầu ra:

- tám agent canonical;
- scripts/references tối thiểu theo nhu cầu thật;
- generated Codex/Claude adapters;
- agent/skill validators;
- session bootstrap guidance.

Nghiệm thu:

- mỗi agent trigger đúng trên prompt mẫu;
- adapter sinh lặp lại cho kết quả ổn định;
- agent không được quyền ghi ngoài scope;
- thử forward-test ít nhất ba agent quan trọng.

### Pha 3 — Benchmark specification

Đầu ra:

- taxonomy v1;
- task schemas;
- rubric authoring guide;
- annotation guide;
- concept map và learning objectives của Tin học lớp 9;
- pilot set 30–50 samples.

Nghiệm thu:

- chuyên gia duyệt correctness;
- rubric atomic và không mâu thuẫn;
- mọi pilot sample được gắn `grade: 9` và truy vết tới chủ đề/learning objective;
- có ít nhất hai annotator trên pilot.

### Pha 4 — Evaluation MVP

Đầu ra:

- model adapters;
- deterministic code checks;
- rubric judge;
- result schema;
- baseline run trên pilot.

Nghiệm thu:

- run có thể resume;
- cache không làm thay đổi kết quả;
- mọi response gắn model version, config, timestamp;
- không log secret.

### Pha 5 — Judge và annotation validation

Đầu ra:

- human gold set;
- agreement report;
- judge calibration;
- sensitivity và bias analysis;
- rubric revision.

Nghiệm thu:

- ngưỡng agreement được chốt trước khi mở rộng dataset;
- failure modes của judge được tài liệu hóa;
- không báo model ranking nếu judge chưa đạt ngưỡng.

### Pha 6 — Dataset v1 và benchmark run

Đầu ra:

- dataset versioned;
- dev/public test/hidden test;
- benchmark nhiều model;
- statistical report;
- error analysis.

Nghiệm thu:

- coverage cân bằng theo topic/task/error;
- test không duplicate;
- kết quả có CI và paired analysis;
- chi phí và latency được báo cáo riêng.

### Pha 7 — Paper package

Đầu ra:

- paper outline và draft;
- tables/figures sinh từ artifact;
- dataset card;
- benchmark documentation;
- ethics, limitations, reproducibility statements;
- anonymous release package nếu venue yêu cầu.

Nghiệm thu:

- mỗi claim trỏ được đến experiment/artifact;
- tái tạo được bảng chính từ command;
- internal review và domain-expert review hoàn tất.

### Pha 8 — Mở rộng

Chỉ bắt đầu sau MVP:

- bổ sung ngôn ngữ lập trình khác nếu không thuộc benchmark v1;
- multimodal bài làm viết tay/screenshot;
- track safety chuyên sâu;
- các lớp THCS khác;
- cấp học khác;
- môn học khác;
- learner study;
- Vietnamese regional/linguistic variation.

## 16. Timeline khuyến nghị 6–12 tháng

- Tháng 1: Pha 0–2.
- Tháng 2: Pha 3 và pilot.
- Tháng 3: Pha 4.
- Tháng 4: Pha 5, sửa taxonomy/rubric.
- Tháng 5–6: Pha 6.
- Tháng 7–8: phân tích, ablation, paper draft.
- Tháng 9: internal review và submission.
- Tháng 10–12: rebuttal, mở rộng hoặc learner study.

Timeline phải được lập ngược từ deadline venue sau khi chọn hội nghị.

## 17. Rủi ro chính và biện pháp

- Scope creep: khóa charter và version roadmap.
- Scope drift trong nội bộ THCS: mọi sample v1 bắt buộc có `grade: 9`; dữ liệu lớp khác phải nằm ở version/track khác.
- Thiếu chuyên gia: không mở rộng dataset trước khi có reviewer domain.
- Rubric mơ hồ: rubric lint + pilot + adjudication.
- Judge bias: human gold + multi-judge sensitivity.
- Model drift: lưu exact model ID, date và raw response.
- API cost: dry-run, sample cap, cache và budget guard.
- Data leakage: split policy, hash và hidden test.
- Copyright: provenance/license review trước khi ingest.
- Dữ liệu trẻ vị thành niên: tránh trong MVP; nếu dùng phải có consent, de-identification và ethics review.
- Agent conflict: single-writer ownership và handoff contract.
- Runtime lock-in: canonical files + generated adapters.
- Không còn công cụ AI: plan, command, schema và artifact đều đọc/chạy được thủ công.

## 18. Definition of Done cho nền tảng dự án

Nền tảng chỉ được coi là hoàn thành khi:

- fresh clone cài và test thành công;
- cấu trúc agent được validate;
- Codex và Claude cùng đọc được chỉ dẫn chung;
- experiment DAG không có cycle và mỗi node có provenance;
- plan approval được enforce bằng validator/workflow;
- một pilot experiment chạy end-to-end;
- report tái tạo từ artifact;
- không chứa secret hoặc dữ liệu không rõ license;
- tài liệu đủ để một kỹ sư mới tiếp tục mà không cần transcript chat.

## 19. Các lệnh vận hành mục tiêu

Tên lệnh có thể thay đổi khi triển khai, nhưng workflow cần đạt dạng:

```bash
# Cài môi trường
uv sync --all-groups

# Kiểm tra repository
uv run edu-benchmark doctor

# Tạo plan/experiment node
uv run edu-benchmark experiment create \
  --task dataset-pilot \
  --agent dataset-curator

# Validate plan trước review
uv run edu-benchmark experiment validate experiments/<id>

# Sau khi người dùng duyệt
uv run edu-benchmark experiment approve experiments/<id>

# Chạy benchmark
uv run edu-benchmark evaluate \
  --config configs/evaluations/pilot.yaml \
  --experiment experiments/<id>

# Tạo report
uv run edu-benchmark report experiments/<id>

# Kiểm tra toàn bộ
uv run ruff check .
uv run mypy src
uv run pytest
```

## 20. Trình tự ngay sau khi kế hoạch được duyệt

1. Ghi lại các quyết định ở Mục 4.
2. Đổi trạng thái file này thành `APPROVED`.
3. Tạo một experiment mới cho Pha 0, không dùng chính node planning này để triển khai.
4. Viết plan chi tiết cho Pha 0 và gửi người dùng duyệt.
5. Chỉ sau khi Pha 0 được duyệt mới scaffold codebase.
6. Commit từng pha độc lập và gắn experiment id vào commit message/report.

## 21. Nguồn tham khảo

Nguồn nội bộ:

- `document/slide/Benmark cho giao duc 2026.pptx.pdf`
- `document/paper/2502.18940v2.pdf`
- `document/paper/2510.02663v1.pdf`

Tài liệu runtime được kiểm tra ngày 2026-06-18:

- Codex Agent Skills: https://developers.openai.com/codex/skills
- Codex custom instructions: https://developers.openai.com/codex/guides/agents-md
- Codex subagents: https://developers.openai.com/codex/subagents
- Claude Code subagents: https://code.claude.com/docs/en/sub-agents
- Claude Code agent teams: https://code.claude.com/docs/en/agent-teams
- Claude Code project memory: https://code.claude.com/docs/en/memory
