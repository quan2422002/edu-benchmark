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
