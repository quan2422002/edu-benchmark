# Lesson-based shards for `hnmu-dialogue-auditor`

Mục đích: chia toàn bộ 462 mẫu lớp 6–7 thành 3 shard theo **bài học**, để một bài học không bị chia cho nhiều sub-agent.

Nguyên tắc chia:

1. Nhóm theo cặp `grade` + `lesson`.
2. Sắp xếp nhóm bài học theo số mẫu giảm dần.
3. Gán từng nhóm vào shard đang có ít mẫu nhất.
4. Mỗi shard ghi một file input riêng.

File:

- `lesson_based_shard_plan.csv`: mỗi dòng là một bài học được giao cho một shard.
- `shard_01_input_samples.csv`, `shard_02_input_samples.csv`, `shard_03_input_samples.csv`: danh sách mẫu đầu vào cho từng sub-agent.

Phân bố mẫu:

- `shard_01`: 154 mẫu, 11 bài học, phân bố lớp {'6': 84, '7': 70}.
- `shard_02`: 154 mẫu, 11 bài học, phân bố lớp {'6': 84, '7': 70}.
- `shard_03`: 154 mẫu, 11 bài học, phân bố lớp {'6': 70, '7': 84}.

Lưu ý: đây mới là shard manifest. Chưa spawn sub-agent và chưa tạo output audit rộng.
