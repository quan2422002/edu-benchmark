# Agent audit notes — shard_01

Ngày chạy: 2026-07-17T23:19:58+07:00
Chế độ: `hnmu-dialogue-auditor` single-agent shard audit; không merge output và không ghi đè shard khác.
Python dùng cho script tạo output: `/home/quannda/miniconda3/envs/benchmark_env/bin/python`

## Phạm vi

- Input shard: `experiments/20260709_155523/outputs/hnmu_dialogue_audit/pilot_agent_audit/lesson_based_shards/shard_01_input_samples.csv`
- Số mẫu: 154
- Phân bố lớp: {'6': 84, '7': 70}
- Số bài học: 11
- Không có mẫu shard 01 nằm trong `hnmu_review_queue.csv` chính trước audit này.

## Output đã tạo

- `raw_dialogue_checklist_results.csv`: 2464 dòng checklist, 154 mẫu × 16 tiêu chí.
- `quality_check_suggestions.csv`: 154 dòng gợi ý cấp mẫu.
- `hnmu_review_queue_suggestions.csv`: 61 dòng gợi ý review.
- `agent_audit_notes.md`: ghi chú phạm vi, giới hạn và pattern lỗi.

## Kết quả tóm tắt

- Kết quả theo tiêu chí: {'pass': 2241, 'uncertain': 223}
- Gợi ý quyết định cấp mẫu: {'pass': 93, 'needs_human_review': 61}
- Evidence theo loại học liệu trong `metadata_consistency_flags.csv`: {'SGK': 105, 'SGV': 49}
- Tất cả evidence metadata của shard 01 đang có `evidence_status=draft`, nên confidence cho tiêu chí học liệu được giữ thận trọng.

## Pattern bất định/chưa chắc chính

1. `RAW-CON-02` chiếm phần lớn `uncertain`: raw data có `Đáp án (SGV)`, nhưng evidence SGV/SGK truy xuất vẫn là fragment `draft` hoặc top-1 retrieval, chưa đủ để specialist tự xác nhận chuyên môn cuối cùng.
2. Một số mẫu cần HNMU/UET xem lại do `Mức Bloom` có dấu hiệu lệch với động từ trong câu hỏi hoặc lượt AI đầu có khả năng giải thích quá nhiều trước khi học sinh tự thử.
3. Không phát hiện thiếu trường lõi, nhãn lượt nói lạ, hoặc trùng/gần trùng cơ học trong shard 01; `duplicate_candidates.csv` hiện trống.
4. Kiểm sư phạm là heuristic theo phương pháp dàn giáo HNMU: ưu tiên phát hiện dấu hiệu hỏi/gợi mở, chia nhỏ, phản hồi và rút dần hỗ trợ; chưa thay thế phán đoán giáo viên.

## Tiêu chí uncertain nổi bật

{'RAW-CON-02': 154, 'RAW-CON-05': 52, 'RAW-DUP-04': 9, 'RAW-CON-04': 8}

## Giới hạn

- Không sửa raw Excel, normalized data, checklist, skill hoặc output chính của Plan 04.
- Không tạo benchmark samples và không tách `student_prompt`, `conversation_history`, `gold_response`.
- Vì evidence học liệu còn `draft`, các mẫu `pass` vẫn nên được hiểu là đủ dùng cho chuyển đổi thử có điều kiện, không phải xác nhận chuyên môn cuối cùng.
