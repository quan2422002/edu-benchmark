# Rà soát metadata tài liệu tham khảo

Phạm vi: các citation còn được gọi từ `manuscript/main.tex` sau khi rút gọn
Related Work. Đối chiếu ưu tiên trang proceedings, DOI publisher hoặc OpenReview
chính thức; không suy đoán venue, trang hoặc DOI.

| Citation key | Metadata đã kiểm | Trạng thái | Nguồn chính thức / điểm chưa rõ |
|---|---|---|---|
| `macina2025mathtutorbench` | EMNLP 2025, pp. 204--221, DOI `10.18653/v1/2025.emnlp-main.11` | Đúng, giữ nguyên | ACL Anthology: `2025.emnlp-main.11` |
| `shi2026kmpbench` | AAAI 2026, vol. 40(39), pp. 32965--32973, DOI `10.1609/aaai.v40i39.40578` | Đúng, giữ nguyên | AAAI proceedings article `40578` |
| `srinivasa2025tutorbench` | arXiv preprint `2510.02663` | Giữ preprint | Chưa có proceedings publication được xác minh trong phạm vi audit |
| `nguyen2024vimath` | CoNLL 2024, pp. 259--268, DOI `10.18653/v1/2024.conll-1.20` | Đúng, giữ nguyên | ACL Anthology: `2024.conll-1.20` |
| `bui2025vmlu` | ACL 2025 Volume 1: Long Papers, pp. 11495--11515, DOI `10.18653/v1/2025.acl-long.563` | Chuẩn hóa capitalization tiêu đề | ACL Anthology: `2025.acl-long.563` |
| `nguyen2025vietnamtutor` | Sáu tác giả theo OpenReview; ICLR 2025 Workshop AI4CHL, poster/tiny paper | Đã sửa tên tác giả, venue và trạng thái | OpenReview: `EN8dGvVtIp` |
| `lane2026cstutorbench` | H. Chad Lane; Bryson Kageler; SLM4ED'26 / AIED 2026; online arXiv `2607.05571` | Đã sửa venue; không thêm DOI/trang proceedings | arXiv `2607.05571`; metadata proceedings còn không có trang/DOI chính thức trong repository |
| `shin2026psychometric` | Jinnie Shin; Zhe Li; Pauline Aguinalde; Laura M. Cruz Castro; EDM 2026 full paper | Giữ DOI đã liên kết từ proceedings; dùng DOI URL ngắn; không thêm trang chưa xác minh | EDM 2026 official proceedings, full paper 41 |
| `allison2015making` | Sách Crown House, ISBN hiện có | Giữ nguyên | Không cần sửa metadata hiện có |
| `vandepol2010scaffolding` | *Educational Psychology Review* 22(3), pp. 271--296, DOI hiện có | Đúng, giữ nguyên | Springer Nature DOI page |
| `mislevy2003ecd` | ETS Research Report Series 2003(1), pp. i--29, DOI hiện có | Giữ nguyên | DOI publisher record chưa yêu cầu sửa |
| `reeves2016validity` | *CBE---Life Sciences Education* 15(1), rm1, DOI hiện có | Giữ nguyên | DOI publisher record chưa yêu cầu sửa |
| `dao2023vnhsge` | arXiv preprint `2305.12199` | Giữ nguyên | Không có venue peer-reviewed được xác minh trong phạm vi audit |
| `jordan2024programming` | SIGCSE 2024, pp. 618--624, DOI hiện có | Giữ nguyên | ACM DOI record chưa yêu cầu sửa |
| `most2026deepedubench` | Không còn citation sau khi rút gọn Related Work | Đã xóa khỏi `.bib` | Không thêm literature chỉ để giữ reference |

Các nguồn chính thức đã kiểm trong lượt này: ACL Anthology cho
MathTutorBench, ViMath và VMLU; AAAI proceedings cho KMP-Bench; arXiv cho
TutorBench và CSTutorBench; OpenReview cho Vietnamese virtual-tutoring pilot;
và EDM 2026 proceedings cho psychometric framework. Các trường không có bằng
chứng proceedings chính thức (đặc biệt trang/DOI của CSTutorBench) được để
trống thay vì suy đoán.
