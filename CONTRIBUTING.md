# Contributing

Thank you for helping keep `ihc-obstruction-lab` reproducible and careful.

All obstruction-channel rows must include a `trust_level`. Rows marked as theorem-backed literature must include `citation_keys`.

Generated candidate rows must include a concrete proof bottleneck. A candidate without a bottleneck is not actionable and should not enter the seed dataset.

Rows extracted by an LLM or other unverified process cannot be used as theorem-backed data until independently checked and reclassified.

Please add tests for new validation rules, new row types, and any behavior that changes import/export semantics.
