# Learning-resource retrieval index v0

Index này được sinh từ `shared/learning_resources/fragments/learning_resource_fragments.csv`.

File SQLite là artifact sinh lại được và đang được `.gitignore` bỏ qua.

Build lại bằng:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python   scripts/learning_resources/build_learning_resource_index.py
```

Query thử bằng:

```bash
/home/quannda/miniconda3/envs/benchmark_env/bin/python   scripts/learning_resources/query_learning_resource_index.py   --query "Scratch trung bình cộng ba số" --grade 6
```


Tính đến 18/07/2026, index v0 được build từ 154 nguồn OCR Markdown và 2.750 fragment của SGK/SGV Tin học 6–9. File `.sqlite` là artifact sinh lại được, không nên commit.
