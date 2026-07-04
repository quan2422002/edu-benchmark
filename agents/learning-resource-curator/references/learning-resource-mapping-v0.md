# Learning-resource mapping v0

The v0 goal is retrieval, not a perfect ID formula.

## ID principle

- Keep IDs short and copyable.
- Use the mapping table to recover the source URL, local file, page range, and notes.
- Do not encode uncertain section boundaries into the ID.
- Do not reuse an ID for another source or fragment.

## Suggested source IDs

Prefer natural source keys when visible:

```text
LM-<TYPE>-TIN<GRADE>-<SOURCEKEY>
```

Examples:

```text
LM-SGK-TIN9-4700233123
LM-SGK-TIN8-4700157933
```

When no stable key is visible, use a registry sequence that is stable inside the mapping table:

```text
LM-SGK-TIN9-0001
LM-SGV-TIN9-0001
```

## Suggested fragment IDs

Use a simple fragment suffix:

```text
<learning_material_id>#F0001
<learning_material_id>#F0002
```

Store page ranges, section labels, and location notes in `learning_resource_fragments.csv`.

## Retrieval path

```text
fragment_id
  -> learning_resource_fragments.csv
  -> learning_material_id
  -> learning_resource_source_map.csv
  -> source_url/local_file_path + page/section/location note
```

## Later upgrade path

A durable formula for lessons, sections, page spans, and fragment boundaries should be designed only after `learning-resource-curator` has processed representative SGK/SGV/training materials and HNMU has confirmed the segmentation style.
