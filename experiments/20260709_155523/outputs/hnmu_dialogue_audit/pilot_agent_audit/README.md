# Pilot agent audit — kết quả chạy thử

Thư mục này chỉ lưu kết quả chạy thử nghiệm/pilot của `hnmu-dialogue-auditor` cho batch lớp 6–7.

## Vai trò

- Dùng để kiểm thử checklist, schema output, cách agent diễn giải tiêu chí và cách chia shard theo bài học.
- Không phải output chính cuối cùng của Plan 04.
- Không nên dùng trực tiếp làm nguồn chính cho Plan 06.

## Các file đáng chú ý

- `raw_dialogue_checklist_results.csv`: checklist thử nghiệm trên tập mẫu nhỏ.
- `quality_check_suggestions.csv`: gợi ý tổng hợp thử nghiệm.
- `hnmu_review_queue_suggestions.csv`: review queue thử nghiệm.
- `lesson_based_shards/`: kế hoạch chia shard được tạo trong giai đoạn pilot, sau đó đã được copy sang `../agent_shard_audit/lesson_based_shards/` để đồng bộ cấu trúc output chính.

## Output chính nên dùng

Với batch lớp 6–7, output agent chính nằm ở:

```text
../agent_shard_audit/
```

Trong đó file checklist chi tiết mới nhất là:

```text
../agent_shard_audit/merged/raw_dialogue_checklist_results.repaired.csv
```
