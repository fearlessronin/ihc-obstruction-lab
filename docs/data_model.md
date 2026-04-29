# Data Model

This is a short guide to the v0.1.0 data model. See the project `README.md` for installation, report generation, and workflow notes.

## ObstructionChannel

The main row type. It records an identifier, display name, source corpus, trust level, geometry/package description, channel labels, active operations, survival status, obstruction status, computability level, bottleneck, citation keys, comments, and optional structured payloads.

## LocalPackage

Stores local singularity package data such as singularity type, dimension, finite local group, optional discriminant/link/lattice data, prime support, computability level, and comments.

## ShadowSelector

Records a selected subgroup, quotient, or shadow from a finite local group. The current helper validates the key `Z/4 -> Z/2` order-two shadow case.

## CupProductCandidate

Stores finite-coefficient inputs, target codimension, coefficient, survival and obstruction status, bottleneck, and degree/twist validation helpers for Bockstein targets.

## TrustLevel

Separates hand-verified rows, theorem-backed literature rows, computed or symbolic rows, unverified LLM extraction, generated candidates, and speculative templates.

## ComputabilityLevel

Records how computationally explicit a row is, from metadata-only through symbolic, computed-group, theorem-import, and candidate levels.

## BottleneckLabel

Names the proof or validation bottleneck, such as global transport survival, global relation rank, unramified nonvanishing, specialization bridge, or theorem-backed survival.
