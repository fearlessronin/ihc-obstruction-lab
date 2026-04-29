# Schema Notes

The seed dataset is a list of `ObstructionChannel` JSON objects.

Finite groups are represented by numeric cyclic factors:

```json
{"cyclic_factors": [2, 4]}
```

This renders as `Z/2Z ⊕ Z/4Z`. The trivial group is represented by an empty factor list.

Rows should avoid symbolic theorem inference. If a template is symbolic, record it as metadata and place the symbolic expression in `comments`.

The `trust_level` field separates hand-verified calibration rows, theorem-backed literature imports, computed records, unverified extraction, and generated candidates. The `bottleneck` field records the next proof or validation obstruction for candidate rows.
