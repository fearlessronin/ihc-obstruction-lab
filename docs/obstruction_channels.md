# Obstruction Channels

An obstruction channel is a machine-readable description of a mechanism, candidate mechanism, calibration row, or proof bottleneck relevant to integral Hodge conjecture research.

Rows are designed to keep several questions separate:

- What geometric or cohomological package is being recorded?
- Which operations are active?
- Is the row theorem-backed, computed, hand-verified, or only a generated candidate?
- What must still be proved before a candidate can become an obstruction?

The codebase intentionally avoids automatic theorem discovery. Validation checks structural consistency, citation requirements, degree/twist arithmetic for finite-coefficient cup products, and known channel incompatibilities such as mixing nodal free-relation rows with local discriminant rows.
