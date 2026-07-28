# GyroOS v4 jxiv Reference Design

## 1. Purpose

This document defines the reference architecture for:

```text
paper/gyroos_v4_jxiv_full_draft_en.md
```

The bibliography must support adjacent-work positioning, implementation reproducibility, provenance, canonical history, and software citation without implying that GyroOS is identical to any cited architecture.

## 2. Reference Strategy

References are divided into three classes:

```text
A. Required foundational references
B. Required software and archival references
C. Optional comparative or discussion references
```

The paper should not use references merely as decoration. Each reference must support a specific sentence, comparison, or methodological decision.

## 3. Required Foundational References

### R1. Event Sourcing

**Martin Fowler. “Event Sourcing.” 2005.**

Purpose:

```text
support the established idea of retaining changes or events rather than only current state
position GyroOS canonical Process and Trajectory history relative to event-history architectures
```

Use in manuscript:

```text
Related Work
Canonical Runtime Ownership
Discussion: What Must Be Retained
```

Required distinction:

```text
GyroOS is not presented as a full Event Sourcing implementation
GyroOS records bounded Process and Trajectory relations under its own Runtime contracts
full event replay and retroactive correction are not claimed
```

### R2. CQRS and Read-Model Separation

Preferred source:

```text
Greg Young's original CQRS materials or an authoritative CQRS description
```

Fallback source:

```text
Martin Fowler, CQRS
```

Purpose:

```text
support separation between state-changing commands and read-oriented models
position vNext read-only projection as adjacent to, but not identical with, a read model
```

Use in manuscript:

```text
Related Work
Read-Only vNext Projection
```

Required distinction:

```text
GyroOS projection is defined by no Runtime mutation and explicit source input
it is not necessarily a persisted materialized view
it is not a separate distributed read database in v4.0.0
```

### R3. W3C PROV Data Model / PROV-O

Preferred references:

```text
W3C PROV-DM Recommendation
W3C PROV-O Recommendation
```

Purpose:

```text
support established provenance concepts and explicit derivation relations
compare explicit Inspection references and source/view distinction with provenance representation
```

Use in manuscript:

```text
Related Work
Canonical Runtime Ownership
Inspection API
Discussion: Explicit References
```

Required distinction:

```text
GyroOS F–W contracts are not claimed to implement PROV-O
no RDF or OWL interoperability claim is made
PROV is used as an adjacent provenance framework
```

### R4. Domain-Driven Design / Bounded Context

Preferred reference:

```text
Eric Evans. Domain-Driven Design: Tackling Complexity in the Heart of Software. 2003.
```

Purpose:

```text
support explicit domain and semantic boundaries
position GyroOS/GyroAuth separation as a dependency and responsibility boundary
```

Use in manuscript:

```text
Related Work
Consumer Boundary and GyroAuth Isolation
```

Required distinction:

```text
GyroOS does not claim to implement all DDD patterns
Gyro Logic, GyroOS, and GyroAuth are project layers, not automatically DDD bounded contexts
```

### R5. SQLite Atomic Commit

Preferred reference:

```text
SQLite official documentation: Atomic Commit In SQLite
```

Purpose:

```text
support implementation statements about SQLite transaction and atomic publication behavior
```

Use in manuscript:

```text
Canonical Runtime Ownership
Implementation and Verification appendix
```

Required limitation:

```text
cite SQLite guarantees accurately
avoid extending single-database transaction guarantees into distributed claims
```

## 4. Required Software and Archival References

### R6. GyroOS v4.0.0 Zenodo Archive

Metadata:

```text
Gyro Logic Lab. GyroOS v4.0.0. Zenodo record 21641158. 2026.
```

Final DOI:

```text
insert the DOI displayed by Zenodo record 21641158
```

Purpose:

```text
identify the immutable implementation snapshot examined by the paper
```

Use in manuscript:

```text
Abstract or Introduction
Software and Archival Availability
References
```

### R7. GyroOS GitHub Release

Metadata:

```text
GyroOS v4.0.0 — Bounded Runtime and Experimental Inspection Architecture
GitHub Release
```

Purpose:

```text
provide navigable source, release notes, tests, and documentation
```

Use in manuscript:

```text
Software and Archival Availability
Implementation appendix
```

The archival DOI should be the primary citation. The GitHub URL is supplementary.

### R8. Software Citation Principles

Preferred reference:

```text
Smith, Katz, Niemeyer, and FORCE11 Software Citation Working Group.
Software Citation Principles.
PeerJ Computer Science 2:e86, 2016.
DOI: 10.7717/peerj-cs.86
```

Purpose:

```text
justify version-specific software citation and archival identification
```

Use in manuscript:

```text
Methods or Availability note
```

### R9. Citation File Format

Preferred reference:

```text
Citation File Format specification, version 1.2.0
Zenodo DOI: 10.5281/zenodo.5171937
```

Purpose:

```text
support machine-readable software citation metadata if discussed
```

This reference is optional in the paper body but useful in the software availability appendix.

## 5. Optional Comparative References

### R10. Functional Core / Imperative Shell

Purpose:

```text
compare isolation of pure transformations from stateful effects
```

Caution:

```text
use only if an authoritative primary source can be cited
avoid relying on informal gists as a scholarly reference
```

### R11. Layered or Hexagonal Architecture

Possible sources:

```text
Alistair Cockburn, Hexagonal Architecture
Robert C. Martin, Clean Architecture
```

Purpose:

```text
contextualize dependency direction and external adapter boundaries
```

Caution:

```text
these are practitioner sources and should not dominate the bibliography
```

### R12. Workflow Provenance or Scientific Workflow Systems

Possible areas:

```text
scientific workflow provenance
immutable experiment records
reproducible computational pipelines
```

Purpose:

```text
broaden comparison beyond enterprise application architecture
```

Add only after identifying a precise connection to GyroOS Process/Trajectory records.

## 6. Proposed Related Work Structure

### 2.X Event History and Canonical Records

Cite:

```text
R1 Event Sourcing
R5 SQLite Atomic Commit
```

Argument:

```text
Retaining history rather than only current state is established.
GyroOS contributes a project-specific bounded Process and Trajectory contract and does not claim general Event Sourcing novelty.
```

### 2.X Read Models and Non-Canonical Projection

Cite:

```text
R2 CQRS
```

Argument:

```text
Separation of read-oriented representations from state-changing execution has precedent.
GyroOS defines a narrower prohibition: vNext projection must not mutate Runtime state, select OperatorResponse, or infer a hidden latest source.
```

### 2.X Provenance and Explicit References

Cite:

```text
R3 PROV-DM / PROV-O
```

Argument:

```text
Explicit derivation and provenance relations are established concerns.
GyroOS Inspection contracts use explicit request-local references but do not claim PROV interoperability.
```

### 2.X Domain and Consumer Boundaries

Cite:

```text
R4 Domain-Driven Design
R11 optional architecture source
```

Argument:

```text
Responsibility and dependency boundaries are established architectural concerns.
GyroOS applies them to preserve the one-way Gyro Logic → GyroOS → GyroAuth relationship.
```

### 2.X Reproducible Software Artifact

Cite:

```text
R6 Zenodo archive
R8 Software Citation Principles
R9 Citation File Format if used
```

Argument:

```text
The implementation snapshot is versioned and archived as a research software artifact.
```

## 7. Conceptual Comparison Table

Recommended table:

| Concern | Established adjacent concept | GyroOS v4.0.0 position |
|---|---|---|
| Retaining change history | Event Sourcing | Retains bounded Process, Trajectory, current-scope, and Memory records; no complete event-replay claim |
| Separate read representation | CQRS/read models | vNext projection is read-only and non-canonical; no separate distributed read store required |
| Provenance and derivation | W3C PROV | Uses explicit request-local references; no RDF/OWL or PROV compliance claim |
| Domain responsibility boundary | DDD/layered architecture | Preserves Gyro Logic → GyroOS → GyroAuth and prohibits reverse semantic dependency |
| Reproducible implementation | Software citation principles | Fixes v4.0.0 through GitHub Release and Zenodo archive |

The table must be introduced as conceptual positioning, not an empirical performance comparison.

## 8. Citation Placement Map

| Manuscript claim | Citation |
|---|---|
| Current state alone may not explain how a system reached it | R1 |
| Read-oriented representations can be separated from state-changing paths | R2 |
| Provenance models represent entities, activities, agents, and derivation relations | R3 |
| Domain models and responsibility boundaries help organize complex software | R4 |
| SQLite transactions provide documented atomic commit behavior within their stated scope | R5 |
| The evaluated implementation snapshot is GyroOS v4.0.0 | R6 and R7 |
| Research software should be cited by identifiable version and artifact | R8 |

## 9. Bibliography Quality Rules

```text
prefer primary sources and official standards
prefer DOI-bearing publications where available
use official documentation for implementation guarantees
avoid blog sources for theoretical claims when a book, paper, or standard exists
use practitioner sources only for named architecture patterns
never claim compliance with a cited standard unless demonstrated
```

## 10. Preliminary Reference List

1. Fowler, M. Event Sourcing. 2005.
2. Young, G. CQRS materials; or Fowler, M. CQRS. Final source to be selected.
3. Moreau, L., Missier, P., et al. PROV-DM: The PROV Data Model. W3C Recommendation, 2013.
4. Lebo, T., Sahoo, S., McGuinness, D., et al. PROV-O: The PROV Ontology. W3C Recommendation, 2013.
5. Evans, E. Domain-Driven Design: Tackling Complexity in the Heart of Software. Addison-Wesley, 2003.
6. SQLite Project. Atomic Commit In SQLite. Official documentation.
7. Gyro Logic Lab. GyroOS v4.0.0. Zenodo record 21641158, 2026. Insert final DOI.
8. Smith, A. M., Katz, D. S., Niemeyer, K. E., and FORCE11 Software Citation Working Group. Software Citation Principles. PeerJ Computer Science 2:e86, 2016. DOI: 10.7717/peerj-cs.86.
9. Druskat, S., Spaaks, J. H., et al. Citation File Format specification 1.2.0. Zenodo, 2021. DOI: 10.5281/zenodo.5171937.

## 11. Current Status

```text
scientific reference categories
= DESIGNED

citation placement map
= DESIGNED

final Zenodo DOI insertion
= PENDING

final CQRS primary source selection
= PENDING

Related Work manuscript section
= NEXT
```
