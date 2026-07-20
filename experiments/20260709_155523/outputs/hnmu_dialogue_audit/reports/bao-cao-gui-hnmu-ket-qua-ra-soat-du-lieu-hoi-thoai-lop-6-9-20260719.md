# Báo cáo rà soát bước đầu dữ liệu hội thoại gia sư Tin học THCS

Ngày cập nhật: 20/07/2026
Phạm vi: dữ liệu hội thoại do thầy cô HNMU xây dựng cho Tin học lớp 6, 7, 8 và 9.
Mục đích: giúp nhóm HNMU và UET nhìn nhanh mức độ sẵn sàng của dữ liệu trước khi chuyển sang bước tạo mẫu benchmark chính thức.

## 1. Kết luận ngắn gọn

Bộ dữ liệu hiện tại có nền tảng tốt để tiếp tục phát triển thành benchmark đánh giá gia sư AI. Điểm mạnh rõ nhất là độ phủ theo bài học rất đều: mỗi bài hoặc nhóm bài đang có 14 mẫu hội thoại. Điều này giúp dữ liệu không bị lệch mạnh vào một vài bài riêng lẻ.

So với bản rà soát trước, dữ liệu lớp 8–9 đã được đồng bộ lại theo danh mục SGK/SGV. Vì vậy, nhóm “chưa xác định rõ chủ đề” không còn xuất hiện trong thống kê hiện hành. Đây là cải thiện quan trọng, vì trước đó nhiều mẫu lớp 8–9 bị đưa vào nhóm cần xem lại chủ yếu do cách ghi tên bài/chủ đề chưa khớp với danh mục học liệu.

Tuy vậy, dữ liệu vẫn chưa nên chuyển thẳng toàn bộ sang mẫu benchmark chính thức. Các việc cần xử lý trước gồm: kiểm lại một số nhãn mức nhận thức chưa rõ, sửa rất ít lỗi định dạng hội thoại, quyết định cách xử lý một cặp câu hỏi trùng ở lớp 9, và rà sâu nhóm mẫu mà kết quả đối chiếu học liệu/SGV hoặc chất lượng dàn giáo còn chưa thật chắc.

## 2. Dữ liệu đã được rà soát

Tổng cộng đã rà soát 1.050 mẫu hội thoại:


| Khối lớp | Số mẫu | Nhận xét                                                  |
| ---------- | -------: | ----------------------------------------------------------- |
| Lớp 6     |      238 | Đủ 17 bài, mỗi bài 14 mẫu.                            |
| Lớp 7     |      224 | Đủ 16 bài, mỗi bài 14 mẫu.                            |
| Lớp 8     |      280 | Có 20 bài hoặc nhóm bài, mỗi bài/nhóm bài 14 mẫu. |
| Lớp 9     |      308 | Có 22 bài hoặc nhóm bài, mỗi bài/nhóm bài 14 mẫu. |

Phân bố theo lớp là hợp lý. Lớp 8 và lớp 9 có nhiều mẫu hơn vì số bài hoặc nhóm bài nhiều hơn, không phải vì dữ liệu bị lệch bất thường.

## 3. Độ phủ theo bài học

Độ phủ theo bài học là điểm mạnh nhất của bộ dữ liệu hiện tại.

Ở lớp 6, toàn bộ 17 bài đều có 14 mẫu. Ở lớp 7, toàn bộ 16 bài đều có 14 mẫu. Ở lớp 8 và lớp 9, toàn bộ 42 bài hoặc nhóm bài cũng đều có 14 mẫu. Như vậy, xét theo bài học, bộ dữ liệu hiện có độ phủ rất đều.

Tuy nhiên, “đều” không phải lúc nào cũng là mục tiêu cuối cùng. Một số bài có nội dung lớn hơn, nhiều thao tác hơn hoặc quan trọng hơn về mặt sư phạm thì có thể cần nhiều mẫu hơn trong các đợt dữ liệu sau. Ở giai đoạn hiện tại, phân bố 14 mẫu cho mỗi bài/nhóm bài là tốt để tạo nền kiểm thử ban đầu và giúp nhóm nhìn rõ dữ liệu đang phủ đến đâu.

## 4. Độ phủ theo chủ đề

Độ phủ theo chủ đề hiện đã được đồng bộ theo danh mục SGK/SGV, không lấy theo cách ghi tự do trong dữ liệu thô. Vì vậy, kết quả hiện tại đáng tin cậy hơn bản rà soát trước.

Với lớp 6–7, dữ liệu phủ các chủ đề chính như “Máy tính và cộng đồng”, “Tổ chức lưu trữ, tìm kiếm và trao đổi thông tin”, “Đạo đức, pháp luật và văn hoá trong môi trường số”, “Ứng dụng tin học” và “Giải quyết vấn đề với sự trợ giúp của máy tính”. Chủ đề “Ứng dụng tin học” có nhiều mẫu hơn vì trong SGK có nhiều bài thực hành và thao tác hơn. Các chủ đề ít bài hơn thì có ít mẫu hơn, đây là phân bố giải thích được theo cấu trúc SGK.

Với lớp 8–9, dữ liệu cũng đã phủ các mảng lớn như ứng dụng tin học, giải quyết vấn đề với sự trợ giúp của máy tính, bảng tính nâng cao, chỉnh sửa ảnh, làm video, soạn thảo/trình chiếu nâng cao, tổ chức và đánh giá thông tin, đạo đức trong môi trường số và hướng nghiệp. Không còn nhóm “chưa xác định rõ chủ đề”.

Nhận xét chung: độ phủ chủ đề hiện khá tốt. Điểm cần lưu ý tiếp theo không phải là “có thiếu chủ đề lớn không”, mà là sau này có muốn phân bố mẫu theo mức độ quan trọng của từng chủ đề hay không.

## 5. Độ phủ theo mức nhận thức

Dữ liệu hiện có ba mức nhận thức chính: Nhận biết, Thông hiểu và Vận dụng.

Tổng hợp cả bốn lớp:


| Mức nhận thức      | Số mẫu | Nhận xét                                                                                                                                   |
| --------------------- | -------: | -------------------------------------------------------------------------------------------------------------------------------------------- |
| Nhận biết           |      299 | Có đủ số lượng để kiểm các câu hỏi yêu cầu nhớ, nêu, nhận diện.                                                            |
| Thông hiểu          |      430 | Là nhóm nhiều nhất, phù hợp với mục tiêu đánh giá gia sư qua giải thích và gợi mở.                                         |
| Vận dụng            |      302 | Có số lượng tương đối cân bằng với Nhận biết, hữu ích cho các bài cần thao tác, giải quyết vấn đề hoặc lập trình. |
| Chưa nhận diện rõ |       19 | Cần rà lại cách ghi mức nhận thức, chủ yếu ở lớp 9.                                                                               |

Phân bố này nhìn chung tốt. Mức Thông hiểu nhiều hơn một chút là hợp lý vì hội thoại gia sư thường cần giải thích, đặt câu hỏi gợi mở và kiểm tra hiểu biết của học sinh. Nhóm 19 mẫu chưa nhận diện rõ không lớn, nhưng nên được chuẩn hóa trước khi dùng trong bộ dữ liệu chính thức.

## 6. Dạng bài và kiểu yêu cầu của học sinh

Ở lượt rà soát này, dữ liệu chưa có một trường thống nhất để kết luận chắc về dạng bài, ví dụ trắc nghiệm, tự luận lý thuyết, sửa lỗi chương trình, viết chương trình, thao tác phần mềm hoặc phân tích bài làm của học sinh.

Vì vậy, báo cáo này chưa kết luận chính thức về độ phủ theo dạng bài. Đây là phần nên bổ sung ở bước tiếp theo, vì dạng bài ảnh hưởng trực tiếp đến cách đánh giá gia sư AI. Ví dụ, một hội thoại hướng dẫn sửa lỗi chương trình cần tiêu chí khác với một hội thoại giải thích khái niệm lý thuyết.

## 7. Kết quả rà soát từng mẫu

Mỗi mẫu được xem xét theo các nhóm tiêu chí lớn: đủ thông tin, nhất quán với bài học và đáp án, chất lượng dàn giáo trong hội thoại, và rủi ro trùng lặp hoặc khuôn mẫu.

Tổng hợp toàn bộ 1.050 mẫu ở bước kiểm tra cơ bản:


| Kết quả sơ bộ                     | Số mẫu | Diễn giải                                                    |
| ------------------------------------- | -------: | -------------------------------------------------------------- |
| Có thể giữ để xử lý tiếp      |    1.045 | Mẫu đủ thông tin cơ bản và chưa có lỗi cơ học rõ. |
| Cần người xem lại                 |        2 | Chủ yếu do nghi vấn trùng câu hỏi ở lớp 9.             |
| Chưa nên dùng ở lượt hiện tại |        3 | Có lỗi định dạng hoặc thiếu thông tin quan trọng.     |

Ở bước rà soát sâu theo từng tiêu chí, tổng cộng có 18.900 lượt chấm tiêu chí cho 1.050 mẫu. Kết quả là khoảng 95,4% lượt tiêu chí đạt, khoảng 4,5% chưa chắc/cần xem lại, và số lượt không đạt là rất ít. Điều này cho thấy nền dữ liệu khá tốt, nhưng vẫn cần một vòng rà thủ công có trọng tâm trước khi chuyển đổi chính thức.

Khi tổng hợp nghiêm ngặt từ các tiêu chí chi tiết lên mức từng mẫu, quy tắc là: mẫu chỉ được xem là sạch nếu toàn bộ tiêu chí đều đạt hoặc không áp dụng; nếu còn bất kỳ tiêu chí “chưa chắc” thì mẫu được đưa vào nhóm cần người xem lại; nếu có tiêu chí không đạt rõ thì mẫu chưa nên dùng ở lượt hiện tại. Theo quy tắc này:

| Kết quả rà sâu theo từng mẫu | Số mẫu | Diễn giải |
| --- | ---: | --- |
| Sạch theo checklist hiện tại | 665 | Có thể ưu tiên chọn để chuyển đổi thử. |
| Cần người xem lại | 382 | Không có nghĩa là mẫu sai; nghĩa là còn ít nhất một điểm cần HNMU/UET xác nhận hoặc đối chiếu thêm. |
| Chưa nên dùng ở lượt hiện tại | 3 | Có lỗi rõ ở ít nhất một tiêu chí. |

### 7.1. Lớp 6–7

Kết quả lớp 6–7 nhìn chung khả quan, nhưng sau khi tổng hợp nghiêm ngặt từ checklist chi tiết, nhóm cần xem lại lớn hơn so với kiểm cơ bản.

Trong 462 mẫu, bước kiểm tra cơ bản chỉ phát hiện 2 mẫu có lỗi rõ. Khi rà soát sâu theo từng tiêu chí, có 238 mẫu sạch theo checklist hiện tại, 222 mẫu cần người xem lại và 2 mẫu chưa nên dùng ở lượt hiện tại. Các điểm chưa chắc chủ yếu liên quan đến việc đối chiếu đáp án với SGV hoặc kiểm lại mức nhận thức, không phải lỗi rõ của hội thoại.

Tóm tắt theo nhóm tiêu chí:


| Nhóm tiêu chí                 | Nhận xét                                                                                                                                                                                                           |
| -------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Đủ thông tin và định dạng | Rất tốt. Gần như toàn bộ mẫu có câu hỏi, đáp án và hội thoại đủ để kiểm. Chỉ có rất ít mẫu cần sửa định dạng lượt nói hoặc bổ sung thông tin.                                   |
| Nhất quán nội dung            | Tốt, nhưng vẫn có một số mẫu cần đối chiếu thêm với SGV hoặc kiểm lại mức nhận thức.                                                                                                              |
| Chất lượng dàn giáo         | Rất tốt. Hầu hết hội thoại có dấu hiệu gợi mở, dẫn dắt và phản hồi phù hợp.                                                                                                                        |
| Trùng lặp/khuôn mẫu          | Không phát hiện cặp trùng chính xác ở lượt kiểm này. Một số hội thoại có cấu trúc tương tự nhau, nhưng điều này có thể chấp nhận được nếu đó là cấu trúc dàn giáo hợp lý. |

Có thể xem lớp 6–7 là nhóm dữ liệu tương đối sẵn sàng để chọn một phần làm thử nghiệm chuyển đổi sang mẫu benchmark. Khi cần tiến độ nhanh, nên ưu tiên chọn trong 238 mẫu sạch theo checklist hiện tại; nhóm 222 mẫu còn lại nên được rà theo cụm lỗi thay vì xử lý rời rạc từng mẫu ngay từ đầu.

### 7.2. Lớp 8–9

Kết quả lớp 8–9 đã được cải thiện rõ sau khi đồng bộ lại theo danh mục SGK/SGV.

Trong 588 mẫu, bước kiểm tra cơ bản cho thấy 585 mẫu có thể giữ để xử lý tiếp, 2 mẫu cần người xem lại vì có nghi vấn trùng câu hỏi, và 1 mẫu chưa nên dùng ở lượt hiện tại vì lỗi định dạng hội thoại. Ngoài ra có 19 mẫu cần chuẩn hóa lại cách ghi mức nhận thức.

Khi rà soát sâu theo từng tiêu chí, lớp 8–9 có 10.584 lượt chấm tiêu chí. Trong đó 10.107 lượt đạt, 475 lượt chưa chắc/cần xem lại, và 2 lượt không đạt. Tổng hợp ở mức từng mẫu: 427 mẫu sạch theo checklist hiện tại, 160 mẫu cần người xem lại và 1 mẫu chưa nên dùng ở lượt hiện tại. Các điểm chưa chắc chủ yếu nằm ở phần đối chiếu học liệu/SGV hoặc mức độ rõ ràng của dàn giáo, không còn xuất phát từ lỗi ghép chủ đề hàng loạt như trước.

Tóm tắt theo nhóm tiêu chí:


| Nhóm tiêu chí                 | Nhận xét                                                                                                                                                                                  |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Đủ thông tin và định dạng | Nhìn chung rất tốt. Chỉ có một mẫu thiếu nhãn phản hồi của gia sư; một nhóm nhỏ cần chuẩn hóa mức nhận thức.                                                          |
| Nhất quán nội dung            | Khá tốt. Phần lớn hội thoại bám câu hỏi và đáp án. Một số mẫu cần đối chiếu thêm với học liệu/SGV để chắc chắn hơn.                                            |
| Chất lượng dàn giáo         | Tốt. Đa số hội thoại có dấu hiệu dàn giáo, phù hợp lứa tuổi và không đi lạc hướng. Một số mẫu cần xem lại vì mức hỗ trợ hoặc cách dẫn dắt chưa thật rõ. |
| Trùng lặp/khuôn mẫu          | Có một cặp câu hỏi trùng hoàn toàn cần thầy cô quyết định giữ một mẫu hay giữ cả hai nếu mục tiêu sư phạm khác nhau.                                               |

Có thể xem lớp 8–9 là nhóm dữ liệu đã đủ tốt để chuẩn bị chuyển đổi thử, nhưng nên xử lý trước nhóm ưu tiên cao trong hàng đợi rà soát.

## 8. Mức độ sẵn sàng của dữ liệu

Có thể chia dữ liệu thành ba nhóm:

1. Nhóm có thể dùng để chuyển đổi thử: 665 mẫu sạch theo checklist hiện tại, đủ phù hợp để chọn trước cho bước chuyển đổi thử.
2. Nhóm cần HNMU/UET xem lại: 382 mẫu có ít nhất một điểm chưa chắc, thường liên quan đến đối chiếu SGV/học liệu, mức nhận thức hoặc diễn giải dàn giáo.
3. Nhóm chưa nên dùng ở lượt hiện tại: 3 mẫu có lỗi rõ, cần sửa hoặc xác nhận lại trước khi dùng.

Theo kết quả hiện tại, cả bốn lớp đều có thể bắt đầu chọn mẫu chuyển đổi thử từ nhóm sạch theo checklist. Tuy nhiên, trước khi chuyển đổi rộng, nên xử lý trước các mẫu lỗi rõ và nhóm cần xem lại có ưu tiên cao. Không nhất thiết phải yêu cầu thầy cô xử lý toàn bộ 382 mẫu cùng lúc; có thể gom theo nhóm vấn đề để xác nhận nhanh hơn.

## 9. Việc đề nghị thầy cô HNMU hỗ trợ tiếp

Để dữ liệu có thể chuyển sang bước tạo benchmark chính thức, nhóm UET đề nghị thầy cô HNMU hỗ trợ bốn việc:

1. Rà lại 19 mẫu chưa nhận diện rõ mức nhận thức, chủ yếu ở lớp 9.
2. Sửa hoặc xác nhận các mẫu có lỗi định dạng hội thoại, đặc biệt trường hợp thiếu nhãn phản hồi của gia sư.
3. Quyết định cách xử lý một cặp câu hỏi trùng hoàn toàn ở lớp 9: giữ một mẫu đại diện, sửa để tạo khác biệt rõ, hoặc giữ cả hai nếu mục tiêu sư phạm khác nhau.
4. Rà trước nhóm mẫu được đánh dấu ưu tiên cao trong kết quả rà soát sâu, nhất là các mẫu cần xác nhận thêm với SGV hoặc mức độ dàn giáo. Với nhóm cần xem lại số lượng lớn, nên gom theo nhóm lỗi để thầy cô xác nhận theo cụm.

## 10. Kết luận

Bộ dữ liệu hiện tại có triển vọng tốt để phát triển thành benchmark đánh giá gia sư AI. Điểm mạnh nhất là số mẫu theo bài học rất đều và hội thoại nhìn chung có dấu hiệu dàn giáo. Đây là nền tảng quan trọng.

Phần cần cải thiện không nằm ở việc thiếu dữ liệu hàng loạt, mà chủ yếu ở chuẩn hóa một số thông tin đi kèm và xác nhận các mẫu chưa chắc. Nếu các điểm này được xử lý, dữ liệu sẽ phù hợp hơn để chuyển sang bước tạo mẫu benchmark có cấu trúc, có truy vết và có thể dùng để đánh giá phản hồi của gia sư AI.
