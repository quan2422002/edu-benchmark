Tôi đọc bản thảo này theo góc nhìn **reviewer cho một bài benchmark/AI-in-Education**, không chỉ sửa câu chữ. Kết luận sơ bộ của tôi là:

**Bài có ý tưởng tốt, pipeline xây dựng dữ liệu khá công phu và phần appendix rất đáng giá, nhưng ở trạng thái hiện tại tôi nghiêng về _Major Revision / Weak Reject_ nếu gửi venue cạnh tranh.** Lý do không nằm ở việc benchmark nhỏ hay tiếng Việt, mà ở **construct validity và validation của chính benchmark**: benchmark nói rằng nó đánh giá năng lực gia sư, nhưng một số năng lực quan trọng lại được benchmark “làm hộ” cho model; đồng thời cả khâu gán yêu cầu sư phạm lẫn chấm điểm phụ thuộc quá mạnh vào LLM, đặc biệt là Gemini.

## 1. Tóm tắt đóng góp của bài

VEduTutorBench xây dựng benchmark gia sư AI Tin học THCS lớp 6–9 từ 1.050 hội thoại, qua ba pha: audit hội thoại, xây dựng khung 6 nguyên tắc sư phạm + 6 năng lực tutor, rồi chuyển các tutor turn thành ứng viên đánh giá. Sau lọc, benchmark có 1.400 mẫu thuộc 665 dialogue families. fileciteturn1file0L33-L50

Điểm hay là benchmark không chỉ chấm correctness mà cố gắng đo **learner-state alignment, scaffolding, communication và các hành vi sư phạm như Explanation, Modelling, Practice, Feedback, Questioning, Challenge**. Appendix cung cấp cả rubric, prompt gán principle, prompt sinh phản hồi và prompt judge khá đầy đủ. Đây là phần mạnh của bài.

---

# 2. Các điểm mạnh

**Thứ nhất, bài có pipeline traceable và được mô tả khá kỹ.** Việc giữ family ID, tách prompt/history/reference, giữ native conversational roles và công bố prompt trong appendix là tốt cho reproducibility. Mỗi tutor turn được biến thành một candidate có history tương ứng, và các candidate cùng hội thoại giữ chung family ID. fileciteturn1file2L156-L166

**Thứ hai, rubric tốt hơn nhiều benchmark “LLM-as-a-judge” thông thường.** Các tác giả không chỉ nói chung chung “pedagogy tốt hay xấu”, mà operationalize thành 22 tiêu chí với observable evidence, boundary, positive/near-miss/negative anchors. Ví dụ, rubric phân biệt rõ learner-state alignment, calibrated scaffolding, Explanation và Modelling. fileciteturn2file0L121-L172

**Thứ ba, bài chủ động báo cáo judge disagreement thay vì che nó đi.** Đây là điểm đáng khen. Tác giả thừa nhận benchmark hiện chỉ ổn để phân biệt chênh lệch lớn chứ chưa đủ đáng tin để rank các tutor gần nhau. fileciteturn1file1L78-L94

**Thứ tư, Figure 1 ở trang 3 trình bày pipeline khá rõ; Figure 2 ở trang 4 cũng hữu ích vì cho thấy ngay distribution của grade, turn depth, độ dài và principle incidence.** Đây là cách trình bày benchmark paper tốt.

Tuy nhiên, chính Figure 2 cũng làm lộ một vấn đề lớn về mất cân bằng principle mà tôi bàn dưới đây.

---

# 3. Major Concern 1 — Benchmark nói đo “pedagogical strategy selection”, nhưng model không thực sự phải chọn strategy

Đây là vấn đề conceptual nghiêm trọng nhất.

Bài định nghĩa một trong sáu tutor capabilities là **“pedagogical strategy selection”**. fileciteturn1file2L139-L149

Nhưng khi đánh giá tutor, system prompt **nói thẳng cho model principle nào là bắt buộc**, cùng objective, expected behavior, behavior to avoid và yêu cầu giữ learner agency. fileciteturn2file1L857-L876

Tức là benchmark đã thực hiện bước:

> “Context → chọn pedagogical move”

thay cho tutor.

Tutor thực chất chỉ làm:

> “Context + move đã được chỉ định → hiện thực hóa move thành câu trả lời.”

Do đó, benchmark này đánh giá khá tốt **pedagogical response realization / execution**, nhưng không đánh giá đầy đủ **pedagogical strategy selection**.

Điều này còn rõ hơn trong prompt LearnLM: model được yêu cầu **không tự thêm Questioning, Practice, Challenge, Modelling hay pedagogical move khác nếu principle đó không được benchmark yêu cầu**. fileciteturn2file1L913-L924

### Tôi sẽ yêu cầu tác giả sửa như sau

Tạo hai track riêng:

**Track A — Pedagogical policy selection**

Model chỉ nhận learner context. Model phải quyết định:
- cần Explanation không;
- cần Questioning không;
- Feedback hay Practice;
- có cần nhiều principle đồng thời không.

Sau đó so decision của model với human-validated principle requirements.

**Track B — Pedagogical response realization**

Cho model principle bắt buộc như setup hiện nay, rồi đo khả năng thực thi.

Nếu chưa làm được Track A thì claims phải thu hẹp. Không nên nói benchmark đo đầy đủ “strategy selection”.

---

# 4. Major Concern 2 — Toàn bộ benchmark bị “Gemini-conditioned” ở nhiều tầng

Gemini không chỉ là một evaluated tutor.

Gemini 3.5 Flash còn được dùng để **quyết định principle nào là required cho từng sample**. Các principle có score ≥4 được chọn; bài thừa nhận đây là một single Gemini scoring run. fileciteturn1file5L348-L351

Sau đó:
- Gemini lại là một trong hai judge;
- hai evaluated tutor configurations lại cùng là Gemini;
- chính sample composition phụ thuộc vào labels sinh bởi Gemini.

Như vậy dependence không chỉ là “same-family judge bias”. Nó là:

**Gemini principle selector → Gemini-conditioned benchmark pool → Gemini tutor → Gemini judge.**

Đây là một vòng phụ thuộc mạnh.

Tác giả có nhận ra một phần vấn đề: Gemini judge cho chênh lệch Gemini–Llama lớn hơn GPT judge rất nhiều, và chưa thể xác định đây là same-family preference hay judge severity. fileciteturn1file5L342-L347

Nhưng vấn đề còn sâu hơn vì **sample selection itself cũng do Gemini quyết định**.

### Cần bổ sung ít nhất

- human annotation trên một stratified subset;
- inter-rater agreement cho required-principle labels;
- một scorer khác độc lập với Gemini;
- sensitivity analysis với threshold 3/4/5;
- repeated scoring để kiểm tra stability;
- tốt nhất là consensus giữa human + ≥2 model families.

Nếu principle assignment chưa được independently validated, tôi chưa xem 1.400 sample đó là “gold benchmark labels”.

---

# 5. Major Concern 3 — Human validation hiện chưa đủ cho một benchmark mang claim về pedagogical quality

Rubric 22 tiêu chí mới chỉ được HNMU teachers **“preliminary confirmed”** về độ phù hợp. Tác giả nói rõ rằng experts **chưa độc lập áp dụng rubric lên các response pairs được đánh giá**. fileciteturn1file1L90-L94

Đây không phải chi tiết nhỏ.

Agreement giữa hai LLM judge chỉ chứng minh:

> Judge A và Judge B tương đối giống nhau.

Nó **không chứng minh**:

> Judge A/B đúng theo đánh giá của giáo viên.

Chính bài cũng thừa nhận điểm này. fileciteturn1file1L114-L123

Với một paper tập trung vào **measurement**, human criterion validity gần như là phần cốt lõi.

Tôi sẽ yêu cầu một human validation study, chẳng hạn:
- 150–300 samples stratified theo grade, principle và model;
- 2–3 giáo viên độc lập;
- adjudication;
- agreement human-human;
- agreement LLM-human;
- bias theo model;
- bias theo principle;
- confidence intervals.

Không nhất thiết annotate toàn bộ 1.400 mẫu.

---

# 6. Major Concern 4 — Judge disagreement trên Llama lớn đến mức không thể xem là chỉ khác “severity”

Đây là con số tôi nghĩ reviewer sẽ tập trung rất mạnh.

Holistic exact agreement là:
- Gemini baseline: **88.36%**
- Gemini+LearnLM: **89.79%**
- Llama: chỉ **63.21%**

Đặc biệt, trên Llama có **419 trường hợp Gemini judge = Lose nhưng GPT judge = Win**, trong khi chiều ngược lại chỉ có **65**. fileciteturn1file1L77-L88

Đây không giống noise đối xứng thông thường.

Ở criterion level:
- overall exact agreement = 73.24%;
- common criteria = 67.33%;
- communication = 61.90%;
- Questioning = 68.12%. fileciteturn1file1L97-L109

Nói cách khác, một phần đáng kể leaderboard phụ thuộc vào **judge identity**.

Bài có xử lý trung thực và không overclaim quá mức, nhưng để benchmark được sử dụng rộng rãi, cần xác định nguyên nhân.

### Tôi đề nghị

Chạy ít nhất ba kiểm tra:

1. **response-order swap test**  
   Chấm cùng pair nhưng đảo response_1 / response_2.

2. **test–retest judge stability**  
   Chấm lại subset qua nhiều run.

3. **human-adjudicated disagreement set**  
   Ưu tiên chính 419 directional disagreements.

Nếu human cho thấy Gemini judge thật sự thiên vị Gemini family thì đây là lỗi lớn của evaluation protocol.

---

# 7. Major Concern 5 — Có mismatch giữa rubric “accuracy & verifiability” và evidence thực tế judge nhận

Rubric chung `Subject-matter accuracy and verifiability` nói rằng response phải nhất quán với source question, gold answer **và traced textbook/teacher-guide evidence**. fileciteturn2file0L123-L147

Nhưng judge prompt lại quy định:

> Khi chấm correctness, chỉ dùng source question và gold answer; không sử dụng kiến thức ngoài input. fileciteturn2file2L1047-L1060

Judge không được thấy toàn bộ curriculum fragments đã dùng ở Phase 1.

Vì vậy “verifiability” đang mạnh hơn evidence mà judge thực sự có.

Ví dụ giả định:

- gold answer chỉ ghi một kết luận ngắn;
- model cho đúng kết luận nhưng thêm một factual claim sai;
- claim sai đó không trực tiếp mâu thuẫn với gold answer.

Judge bị cấm dùng external knowledge, nên có thể không đủ evidence để phát hiện hallucination.

Đây là vấn đề đặc biệt quan trọng với môn Tin học, nơi response có thể bổ sung:
- cú pháp;
- chức năng menu;
- file format;
- code;
- thuật toán;
- version-specific behavior.

### Cách sửa

Hoặc:

**A.** cung cấp curriculum evidence fragments cho judge;

hoặc:

**B.** đổi tên tiêu chí thành “consistency with provided curricular answer” thay vì “accuracy and verifiability”;

hoặc:

**C.** bổ sung một independent factuality checker có quyền dùng curriculum source.

---

# 8. Major Concern 6 — “Accuracy” đang được định nghĩa như win rate, và Tie bị tính giống Lose

Bài định nghĩa với criterion \(r\):

\[
A_r = \frac{W_r}{W_r+T_r+L_r}.
\]

fileciteturn1file12L687-L713

Đây **không phải accuracy theo nghĩa thông thường**. Nó là **pairwise win rate**.

Quan trọng hơn, một `Tie` nghĩa là hai responses tương đương, nhưng trong công thức trên Tie đóng góp 0 giống như Lose.

Nếu model response ngang chất lượng teacher reference:
- theo judge: Tie;
- theo metric: model không nhận điểm.

Điều đó có thể hợp lý nếu metric cố ý đo “probability of strictly beating reference”, nhưng khi đó phải gọi nó là **win rate**, không phải “Overall Accuracy”, “General-Level Accuracy” v.v.

Tôi đề nghị:
- giữ W/T/L riêng;
- dùng `Win rate` đúng tên;
- có thể bổ sung \(W+0.5T\) như preference score;
- hoặc dùng Bradley–Terry nếu muốn ranking pairwise.

Hiện tại nomenclature dễ khiến người đọc hiểu nhầm là 87% các câu trả lời “đúng”.

---

# 9. Major Concern 7 — Có sự không nhất quán trong mô tả cluster bootstrap

Mỗi dialogue sinh nhiều candidate và các candidate cùng giữ `family ID`. fileciteturn1file2L156-L166

Vì vậy đơn vị cluster hợp lý là **dialogue family**, không phải individual sample.

Nhưng Experimental Setup nói CI/differences dùng “cluster-bootstrap resamples over **sample_id**”. fileciteturn1file12L700-L713

Trong khi footnote của Table V lại nói bootstrap trên **665 families**. fileciteturn4file3L192-L195

Hai mô tả này không tương thích.

Đây có thể chỉ là typo trong paper, nhưng phải sửa vì ảnh hưởng trực tiếp đến confidence intervals. Nếu bootstrap thực tế ở sample level, uncertainty có thể bị underestimate do các candidate cùng family không độc lập.

Tác giả nên:
- mô tả chính xác cluster key;
- công bố pseudocode;
- chạy lại CI nếu cần;
- dùng paired family-cluster bootstrap cho model contrasts.

---

# 10. Major Concern 8 — Phân bố principle quá lệch nhưng macro score lại cho trọng số bằng nhau

Sample counts gồm:
- Challenge: **8**
- Practice: **27**
- Modelling: **93**
- Questioning: **651**
- Feedback: **806**
- Explanation: **863**.

Bản thân tác giả cũng thừa nhận Challenge với 8 mẫu vẫn nhận cùng principle-level weight với Explanation có 863 mẫu trong KMP-compatible Overall score. fileciteturn4file0L27-L32

Đây là vấn đề nghiêm trọng cho một headline metric.

Với n=8, Challenge không phải estimate ổn định của “Challenge capability”. Không nên cho nó cùng tác động lên summary score với n=863.

Tôi sẽ yêu cầu:
- micro score;
- support-weighted macro score;
- equal-principle macro score chỉ báo cáo như secondary metric;
- CI cho từng principle;
- không đưa Challenge vào strong principle-level claims cho tới khi bổ sung mẫu;
- tốt hơn là mở rộng dataset có chủ đích cho Challenge / Practice / Modelling.

---

# 11. Major Concern 9 — Benchmark là teacher-forced next-turn evaluation, không phải multi-turn tutor rollout

Mỗi candidate sử dụng **các tutor responses trước đó từ hội thoại nguồn** làm history. Ví dụ C3 chứa \(T_1,T_2\) trong context rồi model chỉ sinh \(T_3\). fileciteturn1file2L156-L166

Như vậy model không phải sống với hậu quả của chính các response trước đó của nó.

Đây là thiết kế hoàn toàn hợp lệ cho **context-conditioned next-response evaluation**, và bài thực ra nói khá rõ điều đó.

Nhưng cần tránh diễn giải nó như đánh giá đầy đủ “multi-turn tutoring ability”.

Một tutor thật có thể:
- tạo lời giải quá sớm ở turn 1;
- khiến learner state ở turn 2 khác;
- mắc lỗi rồi tiếp tục củng cố lỗi ở turn 3.

Teacher-forcing không đo được các lỗi này.

Tôi khuyến nghị paper gọi rõ:

> “teacher-forced, context-conditioned next-turn tutoring benchmark”

và xem self-rollout evaluation là future track.

---

# 12. Major Concern 10 — Ablation “LearnLM” chưa phải một ablation sạch

Baseline và LearnLM không chỉ khác một câu đơn giản.

LearnLM prompt thêm:
- active participation;
- manageable step/cognitive load;
- adaptation;
- curiosity/reflection constraints;
- và đặc biệt **cấm tự thêm các pedagogical move không nằm trong required principles**. fileciteturn2file1L913-L924

Vì vậy kết luận kiểu “LearnLM orientation does not improve” cần rất thận trọng.

Negative result có thể do:
- LearnLM principles;
- extra verbosity;
- stricter constraints;
- prohibition clauses;
- interaction giữa những clauses này.

Đây là một **prompt bundle ablation**, không phải causal ablation riêng của LearnLM philosophy.

Nên đổi cách diễn đạt thành:

> “an ablation of our LearnLM-oriented instruction bundle”

và không generalize sang LearnLM rộng hơn.

---

# 13. Major Concern 11 — “Teacher-authored dialogues” cần dùng thuật ngữ chính xác hơn

Title và phần đóng góp nhấn mạnh “teacher-authored dialogues”.

Nhưng Appendix A nói rõ LLM tạo dialogue drafts, còn teachers sở hữu framework, exemplars, prompts, review decisions và final revisions. fileciteturn4file1L72-L80

Đây không phải vấn đề integrity — bài có disclose.

Nhưng thuật ngữ **teacher-authored** dễ khiến người đọc hiểu là teachers viết conversation từ đầu.

Tôi nghĩ chính xác hơn là:

> **teacher-curated, teacher-validated, LLM-assisted dialogues**

hoặc

> **teacher-supervised LLM-assisted dialogues**.

Điều này còn quan trọng vì style của LLM dùng để draft data có thể tạo benchmark artifacts.

Tôi cũng muốn tác giả công bố:
- model nào được dùng để tạo draft;
- version;
- prompt;
- tỷ lệ / loại manual edits;
- có evaluated model nào cũng tham gia authoring pipeline hay không.

---

# 14. Major Concern 12 — Phase 1 audit chưa có validation đủ rõ

Phase 1 dùng `gpt-5.4-mini` để áp dụng 18 criteria lên 1.050 dialogues. Kết quả là 665 retained, 382 routed to human review và 3 rejected. fileciteturn4file8L531-L547

Tôi có hai câu hỏi lớn.

**Một là, chất lượng của AI auditor đã được kiểm chứng thế nào?** Tôi chưa thấy accuracy/recall hoặc agreement so với teacher audit trên một random subset.

**Hai là, số phận của 382 “need human review” cần được giải thích rõ.** 665 + 382 + 3 = 1.050, nên theo cách viết hiện tại dường như 382 này không nằm trong retained benchmark. Vậy “routed to human review” là:
- đã review rồi?
- hay pending?
- sau review có sample nào được đưa trở lại?
- vì sao paper không báo human-review outcome?

Reviewer nhiều khả năng sẽ hỏi ngay chỗ này.

---

# 15. Các vấn đề nhỏ hơn

Một số minor points tôi cũng sẽ ghi trong review:

- `Overall Judgement Accuracy`, `General-Level Accuracy`, `Principle-Level Accuracy` nên đổi tên để tránh nhập nhằng với classification accuracy.
- “Gold answer” thực chất là **curricular content anchor**, không phải gold tutor response; nên giữ distinction nhất quán.
- Một benchmark Việt Nam toàn quốc nhưng teacher validation chủ yếu từ một institution cần thảo luận về external validity.
- Nên báo distribution theo lesson/topic, không chỉ grade và principle.
- Nên báo số sample có 1, 2 và 3 principles.
- Nên có criterion correlations; 22 rubrics có khả năng chồng lấn. Chẳng hạn general scaffolding, Challenge calibration, Explanation adaptation và Modelling transfer đều có thành phần “calibrated to learner state”.
- Gwet's AC1 là lựa chọn hợp lý, nhưng nên giải thích vì sao chọn AC1 và báo confidence intervals.
- Nên thêm cost/runtime của benchmark vì full evaluation dùng hàng chục nghìn criterion judgments.
- Nên thêm test chống position bias của LLM judge.
- Nên thảo luận data contamination / benchmark release strategy nếu benchmark sẽ công khai.

---

# 16. Các thí nghiệm tôi cho rằng **bắt buộc** trước khi accept

Nếu tác giả chỉ có thời gian sửa một vòng, tôi ưu tiên 5 việc:

1. **Human validation subset**  
   Annotate principle labels + pairwise rubric judgments.

2. **Independent principle-label validation**  
   Không chỉ một Gemini run.

3. **Judge-bias analysis**  
   Đặc biệt 419 Gemini-Lose / GPT-Win cases của Llama.

4. **Fix metric/statistics**  
   Tên win rate, tie handling, family-cluster bootstrap.

5. **Add an unconditioned strategy-selection track hoặc hạ claim**  
   Đây là điểm construct validity quan trọng nhất.

Sau đó nếu còn tài nguyên:
- thêm model families;
- bổ sung Challenge/Practice/Modelling;
- position-swap judge test;
- controlled perturbation benchmark.

Một thí nghiệm controlled perturbation sẽ rất thuyết phục: lấy teacher response rồi cố tình tạo các phiên bản:
- sai factual detail;
- reveal answer too early;
- generic praise only;
- question rhetorical;
- excessive scaffolding;
- age-inappropriate language.

Nếu rubric và judges không consistently xếp bản corrupted thấp hơn, benchmark chưa chứng minh được discriminant validity.

---

# 17. Đề xuất wording cho contribution để tránh overclaim

Hiện tại claim hơi gần với “đánh giá năng lực gia sư AI” nói chung.

Tôi sẽ thu hẹp thành:

> **VEduTutorBench evaluates context-conditioned realization of specified pedagogical requirements in Vietnamese secondary-school Informatics tutoring.**

Sau khi có policy-selection track và human validation thì mới mạnh dạn nâng lên:

> “pedagogical intelligence of AI tutors”.

---

# 18. Đánh giá theo kiểu reviewer form

| Hạng mục | Điểm tôi cho |
|---|---:|
| Novelty | **7/10** |
| Importance | **8/10** |
| Dataset/pipeline engineering | **8/10** |
| Pedagogical framing | **7/10** |
| Construct validity | **5/10** |
| Evaluation validity | **4–5/10** |
| Statistical reporting | **6/10**, sau khi làm rõ bootstrap |
| Reproducibility từ mô tả | **7/10** |
| Human validation | **3/10** |
| Writing/presentation | **7/10** |

### Recommendation hiện tại

**Weak Reject / Major Revision.**

Không phải vì ý tưởng yếu. Ngược lại, tôi nghĩ đây là **một benchmark có tiềm năng tốt cho tiếng Việt**. Nhưng paper hiện đang mạnh ở **engineering + rubric design**, trong khi bằng chứng cho việc rubric/labels/judges thực sự đo đúng “quality of tutoring” vẫn chưa đủ mạnh.

Nếu bổ sung human calibration và sửa mismatch giữa **strategy selection** với **principle-conditioned generation**, tôi có thể chuyển đánh giá lên **Weak Accept / Accept**, tùy venue.

---

If you want, I can:

- Propose detailed plan for human validation study
- Outline sensitivity analyses for Gemini-conditioned benchmark
- Design follow-up experiment for multi-turn tutoring evaluation
