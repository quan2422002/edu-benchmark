
# I. Trả lời review của KSE:

## Reviewer 1:
 Q1: Việc chỉ có 8 mẫu Challange và 27 mẫu Practice là quá ít, gây hạn chế cho tuyên bố ở mức phủ theo principle của bộ benchmark.

Trả lời: Đúng. vì thực tế các khi xây dựng các mẫu hội thoại thô, các thầy cô HNMU chỉ được yêu cầu xây dựng để phủ đều và đủ các bài trong bộ SGK/SGV. Việc định hướng để các thầy cô xây dựng thêm các mẫu Challange và Practice là một hướng phát triển trong tương lai, nhằm tăng cường tính đa dạng và phong phú của bộ benchmark. Chúng tôi sẽ cân nhắc việc mở rộng số lượng mẫu để đáp ứng tốt hơn nhu cầu đánh giá và nghiên cứu.

Q2: Việc thực hiện đánh giá thí điểm với chuyên gia con người là cực kì cần thiết, nhằm hiệu chỉnh quá trình đánh giá của LLM Judge và loại bỏ các thiên lệch tiềm tàng do cùng họ mô hình.

Trả lời: Đúng, việc có đánh giá thí điểm của chuyên gia con người là cực kì cần thiết. Tuy nhiên, trong paper của chúng tôi cũng đã nhấn mạnh là phiên bản hiện tại sẽ tập trung vào phân tích sự bền vững giữa nhiều LLM Judge. Còn đối với vấn đề thiên lệch cùng họ mô hình, trong paper chúng tôi cũng đã thực hiện LLM judge với cả Gemini và GPT. Kết quả cho thấy việc thiên lệch là có tồn tại, khi mà Gemini judge chấm rất cao cho 2 Gemini tutor nhưng lại chấm khá thấp cho llama-maverick tutor. Đối với GPT judge, thứ tự điếm cũng tương tự, thậm chí điểm của 2 Gemini tutor được chấm bởi GPT judge thấp hơn 1 chút so với Gemini Judge, nhưng về khoảng cách điểm thì llama-maverick tutor được chấm với số điểm không kém hơn quá nhiều so với 2 Gemini tutor. Điều đó cho thấy ở LLM judge hiện tại:
 + Sự thiên lệch là có, nhưng không nhiều ở các mô hình gia sư AI vốn có chất lượng phản hồi tốt. Bằng chứng là sự chênh lệch không đáng kể giữa Gemini judge và GPT judge khi chấm điểm cho 2 Gemini tutor.
 + Có thể phản ánh tương đối rõ chất lượng của các mô hình gia sư thông qua thứ tự xếp hạng.
 + Chưa có sự thống nhất cao về điểm số được chấm bởi các mô hình gia sư khác nhau khi chấm các mô hình gia sư có chất lượng không tốt hoặc không ổn định

Q3: Phase 1 (Data Audit) và Phase 2 (Measurement Foundation) là không có sự liên hệ với nhau và có thể được thực hiện song song.
Trả lời: Đúng. 2 phase này là độc lập. có thể cách đặt cho chúng là phase sẽ gây hiểu lầm là chúng được thực hiện theo thứ tự 1 -> 2 -> 3 ... . Nhóm tôi đã sửa lại thành process.

----------------------------------------------------------------------

## Reviewer 2: Chủ yếu nêu điểm mạnh vể đóng góp của paper, đồng thời đưa ra 4 gợi ý cho hướng cải tiến:

S1: Làm rõ phạm vi/quy mô của việc chọn chiến lược/quy tắc sư phạm
Paper nêu rõ việc chọn chiến lược/quy tắc sư phạm phù hợp là 1 năng lực quan trọng của gia sư AI. Nhưng AI tutor lại được cung cấp thông tin về các nguyên tắc bắt buộc cho 1 mẫu cụ thể ngay trong system prompt. => Cài đặt hiện tại chủ yếu đo khả năng của AI tutor trong việc nhận dạng 1 chiến lược sư phạm cụ thể thay vì đánh giá khả năng chọn chiến lược tự động dựa trên trạng thái của người học. Reviewer gợi ý làm rõ sự khác biệt này trong mô tả của benchmark trong phần Discussion. Một cài đặt tự động mà trong đó, mô hình phải tự suy luận các bước sư phạm hợp lý sẽ là một bước mở rộng có giá trị lớn trong tương lai

Trả lời: Đúng. Đây là 1 gợi ý rất có giá trị. Tôi sẽ cân nhắc thực hiện thêm thử nghiệm này. Tuy nhiên, về việc đánh giá thử nghiệm thì có thể sẽ phát sinh thêm. Ví dụ: 
- Đánh giá độ chính xác khi chọn tập nguyên tắc cần có
- Đánh giá khả năng bị lộ phần suy luận để chọn nguyên tắc sư phạm cần thiết trong câu phản hồi dành cho học sinh.
....
Hoặc có thể viện dẫn paper KMP-Bench để làm cơ sở vì sao lại thực hiện thử nghiệm như vậy

S2: Việc đánh giá bởi con người sẽ củng cố đáng kể cho bộ benchmark
Đánh giá hiện tại phụ thuộc vào 2 LLM Judge. Điều này cung cấp bằng chứng hữu dụng cho sự ổn định giữa các judge, nhưng chưa thể thay thế hoàn toàn đánh giá sư phạm bởi chuyên gia con người. Paper cũng thừa nhận việc đồng thuận giữa 2 LLM không khẳng định tính đúng đắn khi so sánh với kết quả tham chiếu độc lập từ con người. Điều này đặc biệt quan trọng vì một trong các mô hình đóng vai trò giám khảo thuộc dòng Gemini, trong khi hai cấu hình gia sư được đánh giá cũng dựa trên nền tảng Gemini; hơn nữa, kết quả đánh giá đối với mô hình Llama có sự khác biệt rõ rệt giữa giám khảo Gemini và giám khảo GPT. Tôi khuyến nghị các tác giả bổ sung—hoặc đưa ra kế hoạch cụ thể cho—một tập con dữ liệu được đánh giá bởi con người theo phương pháp phân tầng, trong đó báo cáo mức độ đồng thuận giữa con người và LLM cũng như phân tích các trường hợp bất đồng giữa các giám khảo.
Trả lời: Đồng ý. tôi sẽ bổ sung về quy trình đánh giá của chuyên gia con người và kết quả đánh giá đó

S3: Mất cân bằng nghiêm trọng trong phân bố của các nguyên tắc sư phạm
Các mẫu Explanation, Feedback và Questioning được thể hiện tượng đối tốt, trong khi các nguyên tắc sư phạm Modelling chứa 93 mẫu, Practice và Challange chỉ chứa lần lượt 27 và 8 mẫu. Do đó, các kết luận ở mức nguyên tắc cần được diễn giải thật cẩn trọng. Reviewer gợi ý nên nói rõ các kết quả này là sơ bộ và việc ưu tiên bổ sung các mẫu thuộc các nguyên tắc còn thiếu sẽ được thực hiện trong các phiên bản sau của bộ benchmark.
Trả lời: Đồng ý. Đây hiện tại mới chỉ là kết quả của phiên bản benchmark đầu tiên.

S4: Tính tái lập và chi tiết công bố cần được làm rõ hơn
Vì đây là một paper liên quan đến benchmark, bản cuối cùng nên nêu cụ thể về việc những sản phẩm nào sẽ được công bố, bao gồm các mẫu benchmark, split benchmark cố định, prompt dùng cho tutor response và llm judge, prompt cho principle-scoring, file script chạy đánh giá, phiên bản model, và các cài đặt decode. Nếu một số tài liệu SGK/SGV (được biên soạn dựa trên chương trình học) không thể được phân phối lại do các hạn chế về bản quyền, các tác giả cần giải thích cách thức vẫn có thể tái tạo quy trình đánh giá và bộ tiêu chuẩn tham chiếu đó. 
Một số vấn đề nhỏ hơn—chẳng hạn như thuật ngữ dùng cho "Accuracy" (độ chính xác), cách hiểu về "teacher-authored dialogues" (các đoạn hội thoại do giáo viên biên soạn) và đơn vị phân cụm bootstrap—cũng có thể được làm rõ hơn trong phiên bản cuối cùng.

Trả lời: Đúng, hiện tại về các phần sau: các mẫu benchmark, split benchmark cố định, prompt dùng cho tutor response và llm judge, prompt cho principle-scoring, chúng tôi đã có trong phần appendix của chính paper này. Còn các phần file script chạy đánh giá, phiên bản model, và các cài đặt decode thì chúng tôi sẽ public code và runbook để hướng dẫn chạy.
Còn đối với phần tài liệu SGK/SGV, do có liên quan đến bản quyền của nhà xuất bản, chúng tôi không thể công bố nội dung học liệu. Tuy nhiên, về cách xử lý học liệu, bóc tách và xây dựng cơ sở dữ liệu dựa trên học liệu và cách học liệu được dùng để kiếm toán dành cho specialist agent thì đã có trong code repo và sẽ được công bố.
Đối với các vấn đề nhỏ hơn, tôi sẽ nêu rõ hơn trong paper. Về diễn giải cho cụm từ "teacher-authored dialogues", tôi sẽ hỏi kĩ lại các thầy cô HNMU.

----------------------------------------------------------------------
## Reviewer 3: Các kết quả có trong các bảng III đến V cần được giải thích chi tiết hơn và các lỗi chính tả cần được sửa

Trả lời: Đồng ý.


**************************************************************************


# II. Trả lời review của thầy Hoàng - co-professor của tôi


## Các Major concern:
#1 (Ưu tiên: cao): Đúng, đã xử lý ở S1 của kse reviewer 2
Hành động: Chạy thêm thử nghiệm và phân tích, sau đó sửa trong paper.

#2 (Ưu tiên: cao): Đúng, cần cân nhắc chạy thêm GPT cho requirement scoring trên 1 tập pilot hoặc chạy full để xem độ đồng thuận. Về consensus giữa human và (các) llm, sẽ RẤT TỐN THỜI GIAN nên cần cân nhắc
Hành động: sẽ chạy thêm thử nghiệm và phân tích, sau đó sửa ở trong script

#3 (Ưu tiên: Trung bình): việc tiến hành human validation, trong bối cảnh hiện tại, có trở ngại to lớn sau: Việc chấm theo từng tiêu chí, ở mỗi mẫu là rất tốn công sức của con người, đặc biệt là trong bối cảnh hạn nộp bản final và camera-ready submisson sẽ là vào 15/9, còn khoảng 8 ngày để làm. => Nghiêng về giữ nguyên claim có trong paper: phương pháp đo lường hiện tại nhấn mạnh vào tính bền vững giữa các LLM Judge, thay vì khẳng định tính chính xác về điểm số so với kết quả đánh giá được chuyên gia con người thực hiện.
Hành động: Không sửa

#4 (Ưu tiên: Cao):Đúng, cần làm thêm ablation study về phần này. Cần điều tra kĩ trong response cụ thể của llama, kèm cả ví dụ cụ thể. Ưu tiên phân tích các trường hợp mismatch giữa 2 llm judge.
Hành động: 
#5 (Ưu tiên: Thấp): Thực tế, phản biện này sẽ khó có thể đáp ứng được. Có các nguyên nhân sau:
- Phần fragment có khá nhiều vấn đề, đặc biệt ngay ở phase 1, khi tôi check 1 số fragment được dùng làm evidence cho quyết định của specialist agent khi chấm các criterion cho 1 mẫu hội thoại, tôi thấy bản thân fragment đó chỉ là 1 đoạn ngắn, cơ bản là không đủ thông tin để đưa ra quyết định. Vì vậy, có thể coi phần fragment là 1 căn cứ không đủ tin cậy. Vì vậy, tôi nghĩ cần rất tránh hoặc đề cập thật cẩn trọng tới phần này trong paper.
- Hơn nữa, trong review chính thức của KSE, cũng chỉ đề cập đến evidence học liệu ở phần S4 của reviewer 2, mà chủ yếu liên quan đến tính tái lập, thay vì nhấn mạnh vào vai trò của evidence fragment trong llm judge.

Vậy nên, tôi đang nghiêng về hướng giữ nguyên, hoặc sẽ chỉ sửa lại nội dung của rubric từ "accuracy and verifiability" thành "“consistency with provided curricular answer".

#6 (Ưu tiên: trung bình): Cân nhắc không cần sửa do hiện tại, phương pháp và tên gọi có trong paper đang bám sát với paper KMP-Bench. Nếu điều tra lại mà không thấy có sự bám sát, có thể cân nhắc sửa
Hành động: ưu tiên giữ nguyên

#7 (Ưu tiên: cao): Đúng. đây là lỗi typo không nhất quán.
Hành động: Từ phần III.A, thống nhất 1 cách gọi là dialogue family.

#8 (Ưu tiên: trung bình): Xử lý tương tự Q1-KSE Reviewer 1 và S3-KSE Reviewer 2

#9 (Ưu tiên: trung bình): Cân nhắc không sửa, do paper đã nêu rõ, và KSE reviewer không đề cập

#10 (Ưu tiên: thấp): Còn thời gian thì tiến hành phân tích


#11 (Ưu tiên: trung bình): Cần làm rõ thêm với bên HNMU


#12 (Ưu tiên: trung bình): Phần này có thể diễn giải, kết hợp với phần teacher-authoed dialogue là: các dialogue này đã đi qua 2 lớp validation gồm human teacher và agent nên đảm bảo chất lượng cao ở từng mẫu. Hoặc tốt nhất là không đụng vào do đó là phần mà KSE reviewer không đề cập.

