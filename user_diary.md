# Plan ban đầu (18-06-2026)

Chào bạn đến với dự án mới của tôi. Đây là 1 dự án dài hơi, sẽ phát triển trong khoảng 6 tháng - 1 năm. Mục tiêu của dự án là phát triển 1 benchmark nhằm đánh giá khả năng sư phạm của mô hình trong việc giảng dạy/hỗ trợ học sinh học tập. Mục tiêu của tôi trong dự án này là sẽ có thể xuất bản được ít nhất 1 paper ở hội nghị có mức rank cao. Tôi cũng đã có trước 1 số tài liệu, nằm ở trong thư mục document cũng như dựng trước 1 số thư mục. Để đạt được mục tiêu của dự án, tôi cần bạn làm các điều sau:

1. Đọc kĩ phần slide có trong docs để nằm chắc về phạm vi và mục tiêu của dự án.
2. Xây dựng codebase trong thư mục src của dự án
3. Lên khung cho các specialist agent cần thiết nhất trong việc xây dựng,phân tích,đánh giá,.. và xây dựng chúng ở trong thư mục agents/. Mỗi thư mục làm việc của 1 specialist agent sẽ được đặt tên theo chức năng của agent tương ứng và sẽ chứa các thành phần sau:

   + SKILL.md: File markdown mô tả vai trò, chức năng và quy trình làm việc của agent
   + scripts/: Thư mục chứa các file python, gồm các hàm, có vai trò là bộ công cụ cho công việc của agent. Các hàm cần được code theo đúng chuẩn coding convention (logic rõ ràng, các biến được khai báo đều được sử dụng, có docstring,...)
   + reference: Chứa các tài liệu quan trọng về việc sử dụng bộ công cụ trong thư mục script.

   Đặc điểm của mỗi speicalist agent:

   + Specialist agent cần phải thật sự "sống" trong quá trình làm việc giữa người dùng và agent điều phối. Tức là agent điều phối không chỉ spawn câc specialist agent này khi cần sử dụng mà phải sqawn chúng ngay khi phiên làm việc giữa người dùng và agent điều phối bắt đầu và các specialist agent phải ở đó, sẵn sàng nhận lệnh của agent điều phối bất cứ khi nào có yêu cầu, không phải agent điều phối spawn ra 1 specialist agent mới rồi chỉ truyền prompt mới vào đó.
   + Trước khi làm task, với chế độ mặc định, các specialist agent sẽ lên kế hoạch và viết kế hoạch thực hiện chi tiết vào 1 file md nằm trong thư mục của thử nghiệm tương ứng và agent điều phối sẽ đưa lại link của file plan này cho người dùng. Người dùng review file plan này, có thể chỉnh sửa 1 chút nếu cần chỉnh sửa ít, hoặc có thể từ chối nếu plan đưa ra không đạt yêu cầu. Lúc này, agent điều phối sẽ nhận phản hồi từ chối của người dùng, rồi truyền đạt lại cho sub-agen tương ứng.
   + Trong file plan cần ghi rõ lý do thực hiện task này, làm task này như thế nào ... Đặc biệt, plan này cần được viết để ngay cả khi việc dùng agent là không khả thi (codex hết session, tài khoản Claude code/codex hết hạn,...) thì con người vẫn có thể tiếp tục task, tức là phải có đầy đủ chi tiết rằng sẽ code những gì, như thế nào, dùng câu lệnh nào để chạy,...
4. Trong thư mục experiments, sẽ lưu giữ các thử nghiệm được tiến hành. Tôi đang dự định xây dựng các thử nghiệm này có tính kế thừa. Tức là xây dựng thử nghiệm giống 1 cây, với các đặc tính sau:

   - Thử nghiệm đầu tiên là node gốc
   - Thử nghiệm sau là node con của thử nghiệm trước, tức là lấy cơ sở/kết quả đã đạt được ở thử nghiệm trước để tử đó phát triển lên. Một thử nghiệm sau có thể là con của nhiều thử nghiệm trước đó.
     Đặc điểm của mỗi thử nghiệm:
     - Được đặt tên dựa trên thời điểm bắt đầu thử nghiệm, theo format như sau: <năm><tháng><ngày>_<giờ><phút><giây>
     - Chứa các file plan, thư mục kết quả và report cho 1 task của 1 speicalist agent đã được nêu ở mục 3.
     - Chứa các handoff prompt, dùng làm không gian giao tiếp chung của các specialist agent. Về luồng giao tiếp/bàn giao công việc sẽ được làm rõ sau.
5. Trong thư mục shared, sẽ lưu giữ các tài nguyên dùng chung giữa các agent. Ở phần này tôi mới hình dung ra sẽ chỉ có dataset là sẽ dùng chung. Bạn thử brainstorm và đưa ra thêm các thành phần cần thiết khác nên có trong thư mục này nhé.
6. Trong thư mục utils, sẽ chứa các tiện ích dùng chung. Tôi cũng chưa biết sẽ nên có những thành phần nào trong thư mục này, nên bạn cũng thử brainstorm và đưa ra 1 vài đề xuất nhé.

Ngoài các yêu cầu trên ra, kiến trúc thư mục cũng cần được xây dựng theo hướng linh hoạt (có thể được dùng bởi codex, claude code,... thậm chí khi tất cả các phương án trên đều không khả thi thì người dùng có thể nhanh chóng hiểu trạng thái của hệ thống và thực hiện việc cần làm)

Dựa trên các nội dung trên, bạn hãy rà soát thật kĩ, phản biện lại tôi những điểm mà bạn thấy không phù hợp, sau đó thống nhất bằng cách viết ra 1 plan xây dựng hoàn chỉnh ra 1 file md để tôi duyệt trước khi đi vào cài đặt chi tiết nhé

# Update plan (20-06-2026)

Tôi đã thảo luận với giáo sư hướng dẫn của tôi và chốt lại được các ý sau:

- Lĩnh vực hiện tại mà dự án cần làm là môn tin học THCS, cụ thể là lớp 9
- Ngoài nhóm của chúng tôi (nhóm kĩ sư - AI engineers), còn có nhóm giáo viên chuyên môn (expert teachers), có vai trò trong việc xây dựng/đánh giá bộ dữ liệu (thực ra đây chỉ mới chỉ là vai trò mang tính phổ quát, chưa rõ ràng).
- Việc cần làm từ giờ đến chiều chủ nhật tuần này (21-06-2026) là phải đưa ra được chỉ dẫn cụ thể cho nhóm giáo viên chuyên môn, đồng thời đưa ra các task, kèm với một số mẫu data cụ thể để họ có thể xây dựng/đánh giá dữ liệu benchmark.

Sau khi chốt được các điểm này, cũng như đọc kĩ plan của bạn trong dự án , tôi rút ra được 1 số yêu cầu mới sau:

- Đội ngũ giáo viên chuyên môn là BẮT BUỘC PHẢI CÓ trong dự án, tức hệ thống này không phải thuần AI/Agent-native, mà là human-in-the-loop. Tuy nhiên, cần làm rõ 1 điều: họ CHỈ CÓ kỹ năng chuyên môn về Sư phạm, KHÔNG CÓ KHẢ NĂNG đóng góp cho công việc kĩ thuật (code, build codebase/system,...). Vì vậy, chúng ta cũng cần xác định rõ nhiệm vụ và vai trò của họ trong dự án này, và hệ thống mà tôi và bạn đang xây dựng cũng cần phải có khả năng đưa ra các chỉ dẫn THẬT RÕ RÀNG, kèm ví dụ minh họa để họ có thể thực thi nhiệm vụ của mình một cách mạch lạc.
- Tôi đã đọc plan của bạn (link: experiments/20260618_150902/plan.md) và nhận ra 1 điều: Nó quá dài, và chúng ta đang nhồi nhét quá nhiều thứ vào 1 file plan :). Vì vậy, tôi đề xuất 1 hướng làm mà tôi thấy hay hơn: Chia nhỏ plan này thành từng plan nhỏ, cài đặt cho từng phần một của dự án. Yêu cầu chia plan thành từng phần cần đáp ứng các yêu cầu sau:
  - Có thể duyệt và cài đặt từng plan tương đối độc lập với nhau (có thể duyệt song song hoặc tuần tự, hoặc kết hợp cả 2).
  - Khi 1 plan được duyệt, sẽ thực hiện cài đặt và test thử. Khi đã pass hết các test cases và đạt đến trạng thái hoàn thiện, code sẽ được đẩy lên github repo của dự án.
  - Không bị chồng chéo về mặt khái niệm, chức năng,.... để mà khi 1/nhiều plan đã được duyệt, đã được hoàn thiện cài đặt và đẩy lên github repo trước đó, việc duyệt và cài đặt plan tiếp theo sẽ HẠN CHẾ TỐI ĐA việc thêm/sửa/xóa các phần có liên quan đến 1/nhiều plan trước đó, hoặc tốt nhất là không đụng vào.
- Vì deadline của task hiện tại khá gấp (vào chiều chủ nhật tuần này), nên dự án hiện tại được xác định đang ở giai đoạn PoC, vậy nên codebase/plan nên được xây dựng ở mức tương đối đơn giản, gọn nhẹ, ở mức MVP. Tuy nhiên, việc literature review và đưa ra được những yêu cầu rõ ràng cho đội ngũ giáo viên ngay từ đầu vẫn sẽ rất quan trọng

Từ những ý trên, theo tôi thấy bạn nên xây dựng đội ngũ specialist agent trước đã, đặc biệt là agent `research-methodologist` để có thể tạo literature review, vì thực sự thì, tôi cũng không quá tin tưởng vào kết quả cho khung benchmark mà bạn đưa ra trong plan experiments/20260618_150902/plan.md đâu :), vì rõ ràng là chỉ với 2 paper mà tôi cung cấp, literature review đơn giản là chưa đủ sâu. Vì vậy, trước khi duyệt và xây dựng khung benchmark, tôi cần 1 literature review đủ sâu và rộng, được thực hiện bởi specialist agent, thay vì 1 agent tổng quát như bạn.

# Update plan (23-06-2026)

bạn có thể thấy là plan F01 là flash plan, lấy các ý cơ bản nhất của các plan full P02-P07 để có thể đưa ra 1 bộ benchmark sơ bộ, nhằm kịp tiến độ của chủ nhật tuần trước. Bây giờ, tôi sẽ note lại các ý sau, dựa trên những gì tôi thấy trước đó :

- Ở nhánh feature/C01\_P02\_P03, khi chạy plan F01, tôi thấy khi chạy thì có đến 3 specialist agent research-methodologist đã được spawn và được chạy với model mặc định là gpt-5 - thực sự là quá tốn token. Vì vậy, tôi muốn bạn setup mô hình mặc định là GPT-5.4-mini, ít nhất hiện tại là ở specialist agent này nhé.
- plan C01 và F01 chỉ là phiên bản mini, làm để kịp tiến độ. Tuy nhiên, việc lấy học liệu làm cơ sở tạo benchmark là BẮT BUỘC, không thể không có. Tôi nghĩ khi tạo/thẩm định các mẫu dữ liệu, giáo viên chuyên môn cũng cần phải đưa 1/nhiều mã học liệu tham khảo mà họ dùng làm cơ sở cho câu hỏi của học sinh/câu trả lời của tutor. Tuy nhiên, kho học liệu không bao giờ là cố định (có thể bị thêm/sửa/xóa). Vì vậy, tôi nghĩ về phần xây dựng benchmark, nên xây dựng 1 database để quản lý học liệu và benchmark (các task, các mẫu của task), đồng thời xây dựng cách mà đội ngũ giáo viên chuyên môn có thể dễ dàng update kho học liệu và truy xuất được mã của các đoạn học liệu mong muốn để họ có thể xây dựng benchmark một cách dễ dàng và rành mạch nhất. Bạn hãy xem xét phần code ở branch feature/C01\_P02\_P03 xem có hữu ích không, đồng thời cân nhắc thiết kế phần database học liệu/benchmark, từ đó có thể cập nhật thêm vào plan roadmap nhé.

# Update plan (24-06-2026)

Được rồi, tạm thời để roadmap đó qua 1 bên. Bây giờ tôi có task gấp hơn nhiều: Đội ngũ giáo viên chuyên môn đang yêu cầu nhóm tôi phải đưa ra được logic tại sao từ các nghiên cứu liên quan lại ra được benchmark này (các task của benchmark, các rubric dùng để chấm cho các task đó, nội dung các mẫu dữ liệu trong benchmark,...). Nên là bây giờ, tôi nghĩ bạn cần checkout sang nhánh feature/C01_P02_P03 để xem lại nội dung về việc xây dựng benchmark (có trong thử nghiệm experiments/20260621_135515 nhé). Trước khi bạn checkout sang nhánh đó, hãy đảm bảo code mà bạn đã sửa ở nhánh này được an toàn đã nhé (có thể push tạm lên nhánh main, tuy nhiên phải lưu lại git commit id của nó, vì thực tế các thay đổi này chưa được tôi duyệt chính thức đâu)

# Update plan (26-06-2026)

Note của buổi họp ngày 24-06-2026 giữa UET (là chúng tôi - đội ngũ engineer) và HNMU (đội ngũ giáo viên chuyên môn):

1. Đại ý: HNMU đã xem xét kĩ bộ khung benchmark của UET gửi vào chủ nhật tuần trước (vốn được làm trong một thời gian rất ngắn để kịp deadline tuần trước, nằm trong thử nghiệm 20260621_135515, thuộc nhánh feature/C01_P02_P03) và yêu cầu bên UET phải làm kĩ lại benchmark, tức là phần lớn các phần về task/rubric được xây dựng ở phần này sẽ phải bỏ. Tuy nhiên, tôi thấy bên HNMU cũng đã hiểu được bộ khung benchmark mà bên UET đã truyền tải, bao gồm:
   - Các task
   - Các rubric
   - Một số trường dữ liệu (metadata) trong phiếu tác giả (được nêu ở phiếu tác giả trong sheet Phieu_tac_gia trong file review_form.xlsx, nằm ở thư mục teacher_packet của thử nghiệm 20260621_135515, bên nhánh feature/C01_P02_P03).
   - Sự liên kết, có thể truy vết của mã nghiên cứu, mã chương trình/học liệu đến nghiên cứu và chương trình/học liệu thực thụ.
   - Sự liên kết, có thể truy vết của các lỗi nghiêm trọng với các rubric có liên quan đến lỗi nghiêm trọng đó.

Tuy nhiên, có 1 điểm nghiêm trọng mà bên HNMU có trê trách bên UET khá nhiều. Đó là chưa làm sáng tỏ và tường minh logic để từ nghiên cứu và chương trình/học liệu, có thể đưa ra được task/rubric, ĐẶC BIỆT là về ý nghĩa nội hàm của từng task/rubric đó.

2. Note chi tiết cuộc họp:
   a. Điều mà HNMU và UET đã thống nhất: Benchmark PHẢI ĐƯỢC XÂY DỰNG dựa trên các nghiên cứu uy tín và học liệu/chương trình giáo dục có liên quan (sách giáo khoa, sách giáo viên,...)
   b. Bên HNMU muốn bên UET làm rõ:
   - Về benchmark: PHẢI ĐỊNH NGHĨA RÕ benchmark là gì ? Dùng để làm gì ? Gồm những thành phần nào ? Được vận hành như thế nào ?
   - Về mỗi task trong benchmark: PHẢI KIẾN GIẢI RÕ RÀNG định nghĩa của mỗi task, bao gồm:

     + Task đó được hình thành dựa trên logic nào ? (Được tổng hợp từ bài báo khoa học uy tín có liên quan đến lĩnh vực tutoring benchmark, cũng như các chương trình/học liệu có liên quan (sách giáo khoa/sách giáo viên) như thế nào ?)
     + Yêu cầu về mặt nội dung, cấu trúc ... đối với đầu vào/đầu ra của một mẫu có trong mỗi task đó như thế nào ? Căn cứ vào đâu (dựa trên nghiên cứu uy tín, chương trình/học liệu giáo dục ) để có thể đưa ra được các yêu cầu đó (PHẢI KIẾN GIẢI RÕ)
     + PHẢI KIẾN GIẢI RÕ về số lượng task có trong benchmark (vì sao lại có con số bao nhiêu task với từng đó lĩnh vực ? Cơ sở khoa học cho số lượng task này là gì ? Số lượng task với các lĩnh vực này đã đủ để bao quát trong việc đánh giá tutor chưa ?)
   - Về các rubric được sử dụng để đánh giá cho 1 task cụ thể: cụ thể gồm những rubric nào ? lý do cụ thể nào khiến task này PHẢI được đánh giá bằng các rubric đó ? (dựa trên cơ sở khoa học nào ?)
   - Về các lỗi nghiêm trọng có trong danh sách lỗi nghiêm trọng: cũng tương tự như với rubric - phải có luận giải/cơ sở khoa học rõ ràng. Tuy nhiên, thêm vào đó, cần lý giải rõ: khi có mã lỗi này xuất hiện ở trong phản hồi của gia sư thì hành động quyết định dành cho giáo viên thẩm định nên là gì ? (Loại, chỉnh sửa, duyệt qua ,...)
   - Về các nghiên cứu được khảo sát và học liệu được dùng làm cơ sở xây dựng benchmark: Đã đủ tin cậy chưa ? Các nghiên cứu có uy tín không ? Quy tắc đặt tên mã cho nghiên cứu và học liệu là gì ? Các học liệu gốc được băm nhỏ và quản lý như thế nảo ?
     c. Tư vấn từ đội ngũ HNMU dành cho UET:
   - Cần nhìn vấn đề từ hướng tổng quát hơn, xuất phát từ tư duy hệ thống, tức là từ trên xuống. Gồm các bước lần lượt như sau:

     1) Trước hết là về bài toán đánh giá gia sư. PHẢI HIỂU RÕ: gia sư (tutor) là một người trực tiếp dìu dắt học sinh (kèm 1-1), KHÁC HOÀN TOÀN so với giáo viên hay trợ giảng (teacher/teaching assistant), vốn chỉ giảng dạy cho 1 lớp học có nhiều học sinh, dựa trên 1 học liệu/chương trình hoặc bài giảng cố định. Tức là gia sư sẽ không bó hẹp theo nội dung môn học (ở đây là Tin học lớp 9, dù benchmark hiện tại vẫn sẽ ưu tiên cho lĩnh vực này), mà phải đặt vấn đề là học sinh có thể hỏi BẤT KÌ câu hỏi nào. Vì vậy, mục tiêu của benchmark này không chỉ là đánh giá dựa trên giáo trình/học liệu hay bài giảng đã có sẵn như giáo viên hay trợ giảng ở trên 1 lớp học chính quy, mà còn phải là đánh giá được khả năng cá nhân hóa theo từng người học, từ đó giúp cải thiện trình độ của người học (phát hiện và bù đắp các lỗ hổng kiến thức của người học, dẫn dắt người học tự tiến bộ,...). Tóm lại là ở bước tư duy này, ta không nên bó hẹp vào một môn học cụ thể, mà nên nhìn nhận rõ vai trò của gia sư trong lĩnh vực sư phạm nói chung.
     2) Từ sự hiểu rõ về vai trò và chức năng của gia sư như vậy, thực hiện khảo sát kĩ lưỡng các bài báo khoa học úy tín liên quan đến tutoring assessment/toturing benchmark. Ưu tiên các bài báo đã được công bố ở các hội nghị và tạp chí có thứ hạng cao, hoặc các bài báo có nhiều citation,... nói chung là có chất lượng cao. Nên có công thức lượng hóa giá trị của bài báo đối với dự án này và ghi rõ giá trị này trong thử nghiệm.
     3) Từ sự hiểu rõ về vai trò và chức năng của gia sư như vậy, kết hợp với khảo sát kĩ lưỡng các bài báo khoa học úy tín liên quan đến tutoring assessment/toturing benchmark và các học liệu/chương trình giáo dục mà bên HNMU cung cấp (vẫn sẽ ưu tiên môn tin học lớp 9) - đã được chia theo lĩnh vực kiến thức và mỗi lĩnh vực này đã có cấu trúc riêng (do bên UET xây dựng), sẽ xây dựng được một nền tảng cơ sở lý thuyết vững chắc, từ đó đưa ra các tiêu chí để đánh giá trên từng lĩnh vực: như thế nào là 1 gia sư tốt ? Có thể kể ra 1 số tiêu chí như: Có tính đúng đắn; câu trả lời áp dụng đúng chuyên môn, phương pháp, kỹ thuật của giáo dục;... Từ đó tạo nên 1 bộ khung (framework) dùng để xây dựng benchmark.
     4) Sau khi có 1 bộ khung vững chắc và đầy đủ luận giải dựa trên cơ sở lý thuyết, sẽ lần lượt xây dựng các task/rubric và các thông tin liên quan (ví dụ: danh sách mã lỗi nghiêm trọng), đi kèm với đó là luận giải chặt chẽ cho các task và rubric này (như đã đề cập ở ý 2 của phần b). Luận giải cần trả lời được 1 số câu hỏi như sau (sau này có thể thêm để làm vững hơn về mặt lập luận):
        . Vì sao lại có số lượng task, với các lĩnh vực đó như vậy ?
        . Vì sao lại có số lượng rubric, với các khía cạnh đánh giá như vậy ? Đặc biệt, cần có 1 rubric/task nhằm đánh giá khả năng hỗ trợ học sinh đã hấp thụ kiến thức được đến đâu.
        . Trong 1 task, có bao nhiêu trường hợp có thể xảy ra ? từ đó lại suy ra thêm 1 câu hỏi: trong 1 task cụ thể, cần bao nhiêu mẫu là đủ và lý do vì sao ? và ở mỗi trường hợp, nên có khoảng bao nhiêu ví dụ để có thể bao trùm lấy nội dung tổng quát của task đó, từ đó giúp cho đội ngũ giáo viên chuyên môn có cái nhìn tổng quát và rõ ràng hơn về task có trong benchmark

     + Sau khi đã xác định rõ ràng được các task, rubric và các thông tin liên quan, sẽ vạch ra các trường dữ liệu (metadata) mà mỗi mẫu cần phải có trong mỗi task, đi kèm với các yêu cầu về định dạng dữ liệu, ý nghĩa,... đối với mỗi trường trong metadata đó. Tất nhiên, phải đi kèm luận giải logic rõ ràng và chắc chắn cho từng trường trong metadata này.
   - Học liệu/chương trình giảng dạy mà bên HNMU cung cấp: link https://taphuan.nxbgd.vn/tap-huan/chi-tiet-sach/tin-hoc-9-940119364.940119364
   - Về bối cảnh được cung cấp trong 1 mẫu của task, hướng đến tính cá nhân hóa: Vì mục tiêu là đánh giá khả năng của 1 gia sư, có khả năng cá nhân hóa theo người học với trình độ khác nhau giữa những người học (có em học giỏi, có em học trung bình,...). Tức là, trong bối cảnh được cung cấp, trình độ của học sinh phải được phản ánh ở một mức độ tương đối (có thể không cần rõ quá, do trên thực tế khá khó để có được 1 bối cảnh đầy đủ và rõ ràng). Bối cảnh này có thể được thể hiện thông qua lịch sử hội thoại giữa gia sư và học sinh. Ở đây, về tính cá nhân hóa, như tôi có nói, sẽ có cả những học sinh yếu, thậm chí kiến thức nền của em học sinh đó có thể chưa đủ để chạm đến môn tin học lớp 9. Vì vậy, khi xây dựng lịch sử hội thoại hay rubric đánh giá, ta đều phải có tiêu chí về việc xây dựng dữ liệu và rubric đánh giá phản hồi của gia sư về việc có thể đặt câu hỏi đáp ứng được các điều sau:

     + Có mức độ khó tăng dần, được nâng lên từng bước 1 qua từng câu hỏi và có tính xây dựng.
     + Phải đảm bảo các em học sinh đã có đầy đủ kiến thức của các lớp trước (các lớp 6,7,8), nói tóm lại là có đủ các kiến thức trước đó. Tức là ở đây, dù là ưu tiên xây dựng benchmark cho môn tin học lớp 9, ta vẫn phải đảm bảo cả các lớp trước đó. Từ đó, có thể suy ra rằng 1 mẫu dữ liệu có thể được xây dựng với nhiều hơn 1 học liệu/chương trình liên quan.
       Chính từ việc hỏi từng bước này, chúng ta cũng có thể đánh giá được khả năng xác định vùng kiến thức mà học sinh có vấn đề của 1 gia sư.
   - Cần có 1 hệ thống để quản lý học liệu/chương trình: Như bạn thấy là bên HNMU có cung cấp link học liệu cho UET. Vì vậy, cần có 1 cơ chế hiệu quả để băm nhỏ và quản lý học liệu, giúp giáo viên có thể dễ dàng truy xuất ra học liệu/chương trình mong muốn khi xây dựng mẫu dữ liệu, cũng như 1 cơ chế rõ ràng để tạo mã học liệu/chương trình tường minh, để giáo viên biết được học liệu/chương trình nào khi được thêm vào cơ sở dữ liệu sẽ có mã là gì.
   - Tương tự với đó là phải xây dựng cơ chế rõ ràng để gán mã cho các nghiên cứu đã được khảo sát, từ đó dễ dàng biết được nghiên cứu này khi được khảo sát sẽ có mã là gì.
   - Một lần nữa, làm rõ vai trò của đội ngũ giáo viên chuyên môn trong việc xây dựng và thẩm định các mẫu trong benchmark. Theo tôi thấy (ý kiến cá nhân của tôi thôi), trong quá trình xây dựng các mẫu benchmark, các thầy cô giáo viên có thể cung cấp các dữ liệu đầu vào cho 1 mẫu của 1 task (bối cảnh, lịch sử hội thoại, prompt của học sinh) rồi gửi lại bên UET. Bên UET có thể gọi LLM (tôi đang tính thông qua thư viện kaggle benchmark và kaggle CLI, kết hợp kaggle kernel) để tạo phản hồi của gia sư. Sau đó, các thầy cô bên HNMU sẽ chấm điểm rubric và đưa ra các quyết định đánh giá khác, từ đó hoàn thành 1 mẫu dữ liệu cho 1 task.

Việc của bạn bây giờ là phân tích kĩ các note này và phản biện lại tôi ở những điều bạn thấy chưa ổn và còn mâu thuẫn, sau đó đưa ra schedule cụ thể cho các việc chi tiết mà tôi cần làm (viết schedule này ra 1 file md mới). Trên thực tế, dự án này sẽ có 2 người làm chính là tôi - trình độ middle ai engineer và 1 bạn sinh viên - trình độ fresher ai engineer. Về effort cụ thể của từng thành viên thì như sau:

- Tôi từ giờ đến tuần đầu của tháng 8 sẽ vẫn phải làm việc full time trên công ty, tức là trong tuần tôi chỉ dành được khoảng 4 tiếng (~0.5 effort) cho dự án này. Sau đó thì tôi có thể dành 1.0 effort. Cuối tuần thì tôi có thể dành nhiều thời gian hơn.
- Bạn sinh viên kia thì từ giờ đến 15/7 sẽ chỉ dành được khoảng 2 tiếng (0.25 effort) cho dự án này. Sau 15/7 thì có thể dành ra 6 tiếng cho dự án (~0.75 effort).

# Update plan (01-07-2026)

Sáng hôm qua, lúc 10h, tôi đã họp với giáo sư của tôi (UET) và các giáo viên chuyên môn của HNMU. Các nội dung đã được chốt:

Về các deadline (QUAN TRỌNG NHẤT):

- 1/8/2026: PHẢI CÓ bài báo để  nộp cho hội nghị KSE (link: https://kse2026.kse-conferences.org/)
- 1/8/2026: Mục tiêu đạt được về kích thước của bộ benchmark là 1000 mẫu
- 15/7/2026: Phải đạt được số lượng mẫu nhất định, để có thể kịp đánh giá tiến độ và cho thấy tính khả thi của việc đạt được 1000 mẫu và hoàn thành bài báo vào đầu tháng 8 (có thể mục tiêu ở mốc này sẽ là khoảng 700 mẫu)

Về các nội dung đã chốt:

- Phiếu tác giả, dùng để giáo viên chuyên môn xây dựng dữ liệu (link gg drive của sheet: https://docs.google.com/spreadsheets/d/1hx-bmX1hNfdFImfoKlXztGKp9QGCcou1/edit?gid=453913985#gid=453913985), với bản gốc là từ sheet "phiếu tác giả" có trong file gg sheet teacher_packet/review_form, đã được làm ở experiment 20260621_135515 ở branch feature/C01_P02_P03 (tôi đã sửa nhẹ so với bản gốc ở trên branch feature/C01_P02_P03 và upload lên thư mục drive này: https://drive.google.com/drive/folders/1h23ty1pE0sD10JpCqUIkfyuIifCd_USi?usp=sharing) . Ngoài ra tôi cũng đã thêm các thông tin liên quan, bổ sung và giải thích rõ ràng các thông tin có trong sheet "phiếu tác giả" trong cùng 1 file gg sheet đó. Hơn nữa, tôi cũng đã ném file phiếu tác giả được chốt vào experiment mới, mã là 20260701_100006 (link drive: https://drive.google.com/drive/folders/18k6oGkD4RJMhcKNjsVc178x2S2f6iur5?usp=sharing), cùng với đó là copy 2 thư mục là literature_review và curriculum_sources từ experiment 20260621_135515 vào experiment 20260701_100006. Tất nhiên, ở experiment này có 1 số chỗ  vẫn chưa được thống nhất toàn bộ. Bạn hãy soi kĩ experiment này, phần nào còn thiếu/mâu thuẫn/chưa đồng bộ thì note lại. Sau đó phản biện nhé.
- Các trường trong phiếu tác giả, được kiến giải rõ ràng. Trong đó, có 1 trường là mã task. Đây là trường mà bên UET PHẢI điền và thông tin đến các giáo viên xây dựng trước khi các giáo viên chuyên môn tiếp tục hoàn thiện các trường còn lại.
- Về trường "lịch sử trao đổi giữa học sinh và gia sư": hiện tại, cả giáo sư UET và giáo viên chuyên môn HNMU đã thống nhất là trong 1 lịch sử trao đổi, sẽ có :

  + Trung bình 4 lượt hội thoại (min 1 lượt, max 5 lượt), với mỗi lượt cũng có trung bình 4 bước (max 5 bước, min 1 bước) trao đổi. Đây cũng là 1 con số mà tôi thấy phù hợp. dựa trên bài báo MathTutorBench mà tôi đã đọc trước đó. Bạn có thể xem lại phần này nhé. Ở đây, ta càn làm rõ định nghĩa của bước và lượt:
    a. Lượt: Tương đương với 1 chat session
    b. Bước: Là các bước trong 1 lượt hội thoại. Được chạy lần lượt theo: bước của học sinh và, bước của gia sư.
    Đối với các bước hội thoại trong 1 lượt hội thoại, yêu cầu dành cho các bước của gia sư là phải tổ chức hội thoại theo phương pháp giàn giáo. Với phương pháp này, trước khi đi vào giải quyết vấn đề mà học sinh đưa ra, gia sư sẽ kiểm tra kiến thức nền của học sinh thông qua việc hỏi học sinh và tiếp nhận câu trả lời, từ đó xác định vấn đề của học sinh và đưa ra được hướng giải quyết trong vấn đề của học sinh, thay vì chỉ đưa ra 1 câu trả lời cuối cùng. TUY NHIÊN, do có giới hạn max cho số bước hội thoại, nên khi chạm đến giới hạn này, gia sư cũng cần đưa ra câu trả lời cuối cùng. Câu trả lời này có thể là kết quả cuối cùng luôn, hoặc 1 hướng dẫn chi tiết nhất để giúp học sinh giải bài.
- Về phạm vi kiến thức được chốt: Đã được xác định rõ là CHỈ NẰM TRONG miền Tin học lớp 9 và kết nối đến các tiền kiến thức liên quan có trong các lớp 6-8. Sau khi trao đổi cùng các giáo viên chuyên môn bên HNMU, tôi thấy học liệu được sử dụng để xây dựng cho benchmark này có các đặc điểm sau:

  + Học liệu được lấy trên trang tập huấn, thuộc môn Tin học (link: https://taphuan.nxbgd.vn/tap-huan?subjects=11), hiện tại sẽ dùng sách giáo khoa (SGK) làm học liệu chủ đạo.
  + Xuyên suốt môn tin học của khối THCS sẽ có khoảng 6-7 chủ đề , với các bài thuộc cùng 1 chủ đề sẽ có độ khó tăng dần khi học ở các lớp trên. Bạn có thể  xem ở trang mục lục của các đầu sách SGK:
    Lớp 6: https://taphuan.nxbgd.vn/tap-huan/doc-sach/sgk-tin-hoc-6.4699918592#page=5
    Lớp 7: https://taphuan.nxbgd.vn/tap-huan/doc-sach/sgk-tin-hoc-7.4700056620#page=5
    Lớp 8: https://taphuan.nxbgd.vn/tap-huan/doc-sach/sgk-tin-hoc-8.4700157933#page=5
    Lớp 9: https://taphuan.nxbgd.vn/tap-huan/doc-sach/sgk-tin-hoc-9.4700233123#page=3
    Bạn có thể thấy rằng trong các mục lục này, tên và số thứ tự của các chủ đề không phải lúc nào cũng đồng nhất và sẽ có 1 chút sự khác nhau. Tuy nhiên ý nghĩa và nội hàm của mỗi chủ đề đó thì, về cơ bản, là 1. Bạn hãy xem và đưa ra cho tôi nhóm chủ đề thống nhất nhé.

Trên thực tế thì cá nhân tôi thấy, ngay cả những nội dung đã được chốt thì vẫn có nguy cơ bị mâu thuẫn. Bạn hãy soi kĩ các nội dung này và phản biện nhé.

Các nội dung đang cần nhắc và xem xét thêm:
Về ý tưởng thu thập dữ liệu: Giáo sư của tôi đã đề xuất 1 phương pháp như sau: Tạo 1 web để  học sinh có thể  tương tác trực tiếp với gia sư AI (Core LLM ở đây có thể sử dụng các model như chatGPT, Claude, Gemini,...). Sau đó sẽ thu thập hội thoại này để  làm các mẫu (chưa có điểm rubric). Các hội thoại được thu thập có thể được fill vào các cột như "Yêu cầu của học sinh về kiến thức thuộc chủ đề", "Bài làm của học sinh", "Lịch sử trao đổi giữa học sinh và gia sư", ....Các mẫu này sau đó sẽ được giaó viên chuyên môn chấm các điểm rubric ở trường "" và các thông tin khác (ví dụ: danh sách lỗi nghiêm trọng). Khi giáo sư của tôi đề xuất cách này, thì trước hết, cá nhân tối thấy đây là một cách làm rất hay, giúp thu thập dữ liệu trong thời gian ngắn. Tuy nhiên, tôi thấy có 1 số bất cập khi làm cách này:

- Chi phí token cho các model này
- Chi phí hosting cho web
- Phải xây dựng một db quản lý học liệu THẬT chuẩn chỉnh, tương tự 1 mcp server để  model (đóng vai MCP client) có thể truy cập và lấy làm cơ sở để tương tác với học sinh. Nếu để nó tự zero-shot thì khả năng chỉ toàn thu được các mẫu kém chất lượng.
  Bạn có thể xem xét phần này và đưa ra đề xuất tối ưu cho tôi nhé

# Update plan (05-07-2026)

Hôm nay, tôi đã họp với giáo sư và thầy cô bên HNMU. Có 1 số ý cần note lại như sau:

- Đọc kĩ 2 bài báo: 2502.18940v2.pdf (MathTutorBench) và 2512.14554v5.pdf (VietLegal), tập trung vào cách các task được phân chia theo 2 hướng: 1. Theo các khía cạnh, phẩm chất của 1 gia sư (MathTutorBench)  và 2. Theo độ khó, dựa trên thang đo Bloom (VietLegal). Tuần sau trao đổi.
- Đề nghị bên HNMU xem kĩ sheet "Luận giải chi tiết trường dữ liệu", vốn dùng để làm rõ các nội dung có trong sheet "phiếu tác giả" có trong file review_form.xlsx đã thống nhất trong buổi họp 01-07-2026, xem có phần nào chưa ổn không thì comment lại.
- Với các trường đã chốt trong phiếu tác giả, nhờ các thầy cô bên HNMU xây trước khoảng 20 mẫu, rồi đưa bên UET tổng hợp và thử chia task

Sau khi trao đổi riêng và kĩ hơn với giáo sư của tôi, thầy đã vạch rõ ra các ý sau:

- Coi như các trường trong sheet "phiếu tác giả" của file review_form.xlsx đã được chốt. Thực hiện xây dựng 1 số ví dụ dựa trên sheet này để giáo viên chuyên môn có thể hình dung ra cách sử dụng phiếu tác giả để xây dựng benchmark.
- Ưu tiên phân chia task theo độ khó, dựa trên thang đo Bloom. Về rubric đánh giá, ưu tiên tạo khoảng 3-4 rubric. Tuy nhiên, PHẢI CÓ bằng chứng khoa học rõ ràng về các task/rubric này (có thể ít paper khảo sát, tuy nhiên paper tham khảo PHẢI CHẤT LƯỢNG và liên quan cao đến benchmark gia sư. Bạn có thể ưu tiên tham khảo các bài báo mà tôi để trong thư mục document/paper/source_paper).
- Tiêu chí cho 1 benchmark tốt (hiện tại):
  + Độ phủ kiến thức (Coverage): Tỷ lệ phần trăm các chủ đề trong sách giáo khoa Tin học THCS (Lớp 6 - 9) được bao phủ bởi các câu hỏi trong bộ benchmark (Ưu tiên làm lớp 9 và các tiền kiến thức có trong khối THCS, như mục tiêu xuyên suốt từ đầu đến giờ).
  + Độ phân hóa (Difficulty Alignment): Tỷ lệ phân bổ các câu hỏi theo 4 mức độ nhận thức: Nhận biết, Thông hiểu, Vận dụng và Vận dụng cao (đã được chia theo task)
  + Độ đa dạng định dạng (Format Diversity): Sự cân bằng giữa các dạng câu hỏi khác nhau như trắc nghiệm, tự luận lý thuyết, sửa lỗi code (Scratch/Python) và viết chương trình.
    Dựa trên các tiêu chí này, hãy phân loại ra các case để có thể xảy ra ở mỗi task, từ đó vạch ra hướng làm ví dụ sao cho bao quát nhất có thể nhé.

Và một điều mà giáo sư của tôi luôn nhắc nhở tôi là: Cứ làm đi, cần thêm gì thì có thể bổ sung sau!

# Update plan (08-07-2026)

Hôm qua, tôi đã có 1 cuộc trao đổi ngắn với các thầy cô HNMU và nhận ra rằng: Họ đã bắt đầu làm dữ liệu rồi. Dữ liệu mà họ làm sẽ là các hội thoại kiểu mẫu giữa gia sư AI và học sinh, ngoài ra sẽ có thêm các thông tin phụ trợ như "Mức độ nhận thức", "Chủ đề", ... Tuy nhiên, thông tin chủ đạo vẫn sẽ là đoạn hội thoại kiểu mẫu. Hình ảnh document/ideal_dialog_example.png thể hiện 1 mẫu dữ liệu mà thầy cô HNMU đang tạo. Vì vậy, có lẽ từ giai đoạn này, chúng ta phải xác định rõ: Giáo viên HNMU CHỈ đóng vai trò xây dữ liệu thô (hội thoại và 1 số thông tin phụ trợ), không làm theo phiếu tác giả và sẽ không quan tâm đến task mà chúng ta xây dựng đâu. Vì thế, bây giờ sẽ có các việc cần làm như sau:

- Đưa ra một phương pháp ổn định (tốt nhất là code-base, có thể có 1 chút AI, tuy nhiên KHÔNG ĐƯỢC PHÉP sửa nội dung trong hội thoại) để có thể map một cách ổn định các mẫu mà thầy cô bên HNMU tạo vào phiếu tác giả mà chúng ta đang có (như trong sheet "Phiếu tác giả" và sheet "Luận giải chi tiết các trường dữ liệu" có trong file review_form.xlsx (link: https://docs.google.com/spreadsheets/d/1EhlzymX71I9q_dC42B8PPyAlBa1jcVfV/edit?usp=drive_link&ouid=116920641936184459712&rtpof=true&sd=true))
- Xây dựng dần task và rubric một cách thật chi tiết để khi dữ liệu thô hoàn thành xong, ta có thể có task và rubric để làm trụ cột để xây dựng benchmark từ dữ liệu thô.Sau khi có được dữ liệu với định dạng phù hợp để làm benchmark, ta cần lên kế hoạch sẽ sử dụng các benchmark này như thế nào, bao gồm:
  - Tiến hành những thử nghiệm nào ?
  - Chạy các thử nghiệm đó như thế nào ?
  - Chạy bao nhiêu thử nghiệm ?

Có thể phần note này sẽ vẫn hơi lộn xộn và chưa được rõ ràng

# Update plan (09-07-2026)

Tôi đã có 1 cuộc họp ngắn với giáo sư của tôi và các thầy cô HNMU vào hôm nay. Có 2 điểm chính:

- Các thầy cô HNMU đã và đang triển khai xây dưng các mẫu hội thoại. Theo như 1 thầy giáo ở bên HNMU đề cập, họ đang dùng AI để tạo được 1550 mẫu hội thoại và đang rà soát lại.
- giáo sư có góp ý cho tôi: Trước khi đi vào xây dựng benchmark, phải lên plan và code để đánh giá xem các mẫu hội thoại đã đủ bao phủ chưa. Cụ thể là bao phủ trên các trục gần tương tự như với experiment experiments/20260705_215045:
  + Bao phủ về vùng kiến thức (Đã bao phủ hết vùng kiến thức (chủ đề, bài học,...) của môn tin học khối THCS chưa ?)
  + Bao phủ về mức độ nhận thức (Biết, hiểu, vận dụng,...)
  + Bao phủ về dạng câu hỏi và bài tập (Trắc nghiệm, tự luận, ảnh, code scratch/python, hay đơn giản là 1 câu hỏi...)

Sắp tới, các thầy cô HNMU cũng sẽ chuyển giao các mẫu đã làm xong (không đợi đến lúc làm xong hết mới chuyển) nên tôi nghĩ đây là thời điểm tốt để bắt đầu lên kế hoạch cho phần này.

# Update plan (10-07-2026)

Hôm qua tôi có 1 buổi trao đổi với giáo sư của mình hôm qua. Trong cuộc trao đổi này, thầy đã giúp tôi làm rõ hơn mục tiêu cao nhất mà chúng ta cần đạt được: PHẢI LẤY BỘ BENCHMARK LÀM ĐỐI TƯỢNG ĐÁNH GIÁ CHÍNH, KHÔNG PHẢI MODEL. Tức là, trước khi dùng bộ benchmark mà chúng ta đã xây dựng để đánh giá model trong lĩnh vực gia sư mon tin học THCS, chúng ta phải đánh giá được xem bộ benchmark mà chúng ta xây dựng đã tốt hay chưa ? Thầy của tôi đã gợi ý về các khía cạnh để đánh giá 1 bộ benchmark như sau:

1) Độ phủ: Phải bao hàm và có phân bố đồng đều các mẫu dữ liệu trên các trục sau:

+ Kiến thức: Đầy đủ các bài học, chủ đề có trong bộ SGK Tin học THCS (gồm cả 4 lớp 6, 7, 8, 9)
+ Độ khó: Đầy đủ các mức nhận thức: Biết, hiểu, vận dụng.
+ Dạng câu hỏi/bài tập: Đầy đủ các dạng bài tập và đề bài của học sinh: Trắc nghiệm, tự luận, code mã giả, python/script,... hoặc chỉ đơn giản là 1 câu hỏi liên quan đến bài học/chủ đề

2) Độ chính xác: Các mẫu dữ liệu trong bộ benhmark phải có tính nhất quán và chính xác cao. Tiêu chí này đặc biệt quan trọng khi mà nguồn dữ liệu gốc của bộ benchmark được tạo bởi con người (Các thầy cô HNMU), dù rất chính xác nhưng VẪN LUÔN CÓ NGUY CƠ bị sai.
3) Tính có thể áp dụng được: Có thể được sử dụng để đánh giá gia sư 1 cách toàn diện, và đặc biệt là phải có khả năng phân biệt/phân loại giữa một tutor xuất xắc, một tutor trung bình và một tutor kém

Về 2 ý đầu, theo tôi thấy, trong 3 paper chủ chốt mà chúng ta đã đọc ở experiment experiments/20260705_215045, chưa được thể hiện rõ ràng. Theo những gì tôi đọc, các paper này chỉ đề cập đến việc dữ liệu được thu thập như thế nào, bao phủ những nội dung nào, ..., từ đó gián tiếp thể hiện bộ benchmark đó là tốt. Tuy nhiên, tôi thấy vẫn chưa có phần nào trong 3 paper đó thể hiện RÕ RÀNG cách họ đánh giá bộ benchmark như thế nào là tốt ? Tôi nghĩ ở plan sắp tới, ta cần đọc kĩ 3 paper này (cộng thêm bài V-legal) với mục tiêu là xem cách các benchmark được đánh giá, KHÔNG PHẢI là cách benchmark được dùng để đánh giá model.

Cũng về 2 ý đầu này, tôi nghĩ ta có thể đánh giá ngay từ dữ liệu thô là các mẫu hội thoại được tạo bởi các thầy cô HNMU. Còn ý 3 thì sẽ chỉ có thể được thực hiện sau khi ta chuyển hóa mẫu hội thoại thành các mẫu trong benchmark hoàn chỉnh.

Ngoài ra, về tiến độ, giáo sư của tôi đang mong muốn các thầy cô HNMU sẽ hoàn thành chuyển giao 500 mẫu trong tuần này/ đầu tuần sau.

# Update plan (14/7/2026)

Sáng nay, tôi có 1 buổi trao đổi ngắn với giáo sư của tôi. Thầy thấy flow hiện tại thì có thể coi là tạm thời ổn, tuy nhiên có 1 số phần cần lưu ý:

- Flow phải rõ ràng và chi tiết hơn, cụ thể là như sau:
  + Nêu rõ data flow/process flow từ dữ liệu thô (các mẫu hội thoại kiểu mẫu, đi kèm với các thông tin liên quan mà các thầy cô HNMU đã xây dựng) đến các mẫu dữ liệu hoàn chỉnh có trong benchmark, sau đó từ các mẫu dữ liệu hoàn chỉnh có trong benchmark sẽ được dùng để đánh giá gia sư AI như thế nào ?
  + Nêu rõ các thành phần được sử dụng tại từng bước trong flow (dùng AI agent hay con người, và dùng như thế nào ?)
- Ngoài ra, thầy cũng gợi ý cho tôi: khi sử dụng agent để check độ chính xác/tính nhất quán trong nội dung giữa các trường có trong 1 mẫu dữ liệu được xây dựng bởi các thầy cô HNMU thì nên lập 1 checklist gồm những tiêu chí để chấm chất lượng của các mẫu đó. Một mẫu được cho là có chất lượng tốt khi đáp ứng được tất cả các tiêu chí có trong checklist đó và các thầy cô HNMU sẽ được yêu cầu check lại các mẫu không đạt yêu cầu về chất lượng, dựa trên checklist, và đi kèm với lý do. Ngoài ra, trên thực tế, có những mẫu mà ngay cả agent cũng không thể đưa ra quyết định chất lượng 1 cách chắc chắn (ví dụ như các mẫu liên quan đến đạo đức, pháp lý,...) thì cũng cần có 1 chỉ số để thể hiện sự tự tin của agent khi đưa ra quyết định (ví dụ: confidence score, được lượng hóa).Nếu confidence thấp thì cũng nên trả về cho các thầy cô HNMU để xem xét thêm.

Dữ liệu thô cũng đã được gửi về. tôi đã để trong thư mục shared/raw_data/HNMU-teacher_dialog_samples

# Update plan (21/7/2026)

Sáng nay, tôi cũng có trao đổi với giáo sư và một số anh chị em Nghiên cứu sinh khác về tiến trình của phase 1 của dự án. Góp ý của các anh chị em Nghiên cứu sinh như sau:

- Cần làm rõ quy trình tạo dữ liệu hội thoại thô của các thầy cô HNMU
- Cần sự tham vấn của các thầy cô HNMU về bộ tiêu chí (checklist) dùng để chấm từng mẫu dữ liệu thô và cơ chế tổng hợp , để xem checklist hiện tại có phù hợp và toàn diện để đánh giá các mẫu dữ liệu thô không ?
- Thống kê và phân tích kết quả của phase 1. Nhiệm vụ của việc thống kê và phân tích này không chỉ là đưa ra các insight có từ kết quả hiện tại, mà còn là đưa ra hướng dẫn rõ ràng và dễ hiểu nhất để các thầy cô HNMU có thể cải tiến xây dựng dữ liệu thô:
  - Tỉ lệ pass/need_review/failed của từng khối lớp
  - Phân bố của các mẫu pass trên các trục
  - Phân tích các mẫu failed/need_review: điểm chung giữa chúng, tập trung vào các tiêu chí nào ?
  - Nguy cơ trong quá trình chấm điểm các mẫu của specialist agent, được thể hiện trong kết quả chấm (không đồng nhất giữa các shard, viện dẫn trạng thái draft của fragment làm lý do cho quyết định uncertain,....)

Tuy nhiên, tôi sẽ để các công việc này cho Nguyên. Còn tôi sẽ ưu tiên chạy tiếp phase 2: Xây dựng dữ liệu cho bộ benchmark và đánh giá dữ liệu của bộ benchmark (về độ phủ và chất lượng các mẫu trong benchmark)

# Update plan (23/07/2026)

Một số vấn đề khi xử lý dữ liệu thô ở phase 2:

- Dữ liệu kết thúc bằng lượt của học sinh
- Có 1 số mẫu có vài lượt liên tiếp của HS/AI, không sự xen kẽ toàn bộ
