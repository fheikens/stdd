
# STDD — Specification & Test-Driven Development

A software engineering methodology for the AI era.

Author: Frank Heikens

---

## The Core Idea

**Code is disposable. Behavior is permanent.**

STDD defines systems using specifications and tests. AI generates the implementation. If the implementation becomes outdated, complex, or broken, it is discarded and regenerated. The specifications and tests remain.

This is the **regeneration model**: code is deliberately disposable because the specification and test layers are strong enough to verify any new implementation from scratch.

---

## The Manifesto

- Specifications define intent.
- Tests verify behavior.
- Together, specifications and tests define the system.
- Implementations are replaceable artifacts.

Read the full [Manifesto](manifesto.md).

---

## How It Works

```
1. Define the specification
2. Define the expected behavior
3. Write tests that verify the behavior
4. Generate implementation with AI
5. Run the tests
6. Pass → accept. Fail → regenerate.
```

```mermaid
flowchart TD

A[Specification]
B[Behavior Definition]
C[Test Suite]
D[AI Generated Implementation]
E[Run Tests]
F{Tests Pass?}
G[Accept Implementation]
H[Regenerate Implementation]

A --> B
B --> C
C --> D
D --> E
E --> F
F -- Yes --> G
F -- No --> H
H --> D
```

---

## Reading Guide

Start with the Quick Start to build your first feature. Then go deeper based on your role.

### Quick Start

| Document | Description |
|----------|-------------|
| **[Quick Start](docs/quick-start.md)** | **Build your first STDD feature in 90 minutes** |

### Philosophy

| Document | Description |
|----------|-------------|
| [Manifesto](manifesto.md) | Why STDD exists and what it stands for |

### Core Methodology

| Document | Description |
|----------|-------------|
| [Method](docs/method.md) | The STDD workflow — how it works in practice |
| [Writing Specifications](docs/writing-specifications.md) | How to write precise, testable specifications |
| [Architecture](docs/architecture.md) | Designing systems for safe regeneration |
| [NFR Framework](docs/nfr-framework.md) | Non-functional requirements as testable constraints |
| [Engineering Playbook](docs/engineering-playbook.md) | Applying STDD in real projects |
| [Adoption Guide](docs/adoption-guide.md) | How to adopt STDD in existing teams and projects |
| [Versioning the Knowledge Layer](docs/versioning-the-knowledge-layer.md) | Version control for specifications and tests |
| [Features vs Implementations](docs/features-vs-implementations.md) | Language independence in STDD |

### Reference

| Document | Description |
|----------|-------------|
| [Glossary](docs/glossary.md) | Quick reference for all STDD terminology |
| [Anti-Patterns](reference/anti-patterns.md) | Common mistakes and how to avoid them |
| [STDD vs Existing Methods](reference/vs-existing-methods.md) | Comparison with TDD, BDD, and other approaches |

### Examples

| Document | Description |
|----------|-------------|
| [Seat Reservation API](examples/seat-reservation.md) | Full end-to-end walkthrough: specs, tests, implementation, regeneration |
| [Order Cancellation](examples/order-cancellation/) | Complete standalone feature: spec, tests, traceability, implementation |
| [Short Examples](examples/examples.md) | Single-feature STDD examples |

### Tooling

| Resource | Description |
|----------|-------------|
| [Templates](templates/) | Copy-paste starter files for new STDD features |
| [Tools](tools/) | CSI scripts (fingerprint, traceability) + acceptance-case test generator |
| [CI Workflow](.github/workflows/stdd.yml) | GitHub Actions reference workflow for CSI |

---

## Repository Structure

This repository contains the STDD methodology documentation **and** applies STDD to its own tools. The `features/` and `tests/` directories specify and verify the three Python tools — the CI workflow enforces all three CSI gates on every push.

```
stdd/
├── README.md
├── manifesto.md
├── .fingerprint                     ← specification fingerprint
│
├── features/                        ← STDD applied to its own tools
│   ├── compute-fingerprint/
│   │   ├── specification.md
│   │   └── acceptance-cases.yaml
│   ├── validate-traceability/
│   │   ├── specification.md
│   │   └── acceptance-cases.yaml
│   ├── yaml-to-pytests/
│   │   ├── specification.md
│   │   └── acceptance-cases.yaml
│   └── traceability-matrix.md
│
├── tests/                           ← 52 tests, 100% spec coverage
│   ├── test_compute_fingerprint.py
│   ├── test_validate_traceability.py
│   └── test_yaml_to_pytests.py
│
├── tools/                           ← reference CSI scripts
│   ├── compute_fingerprint.py
│   ├── validate_traceability.py
│   └── yaml_to_pytests.py
│
├── docs/
│   ├── quick-start.md               ← start here
│   ├── method.md
│   ├── writing-specifications.md
│   ├── architecture.md
│   ├── nfr-framework.md
│   ├── engineering-playbook.md
│   ├── adoption-guide.md
│   ├── versioning-the-knowledge-layer.md
│   ├── features-vs-implementations.md
│   └── glossary.md
│
├── reference/
│   ├── anti-patterns.md
│   └── vs-existing-methods.md
│
├── examples/
│   ├── seat-reservation.md
│   ├── examples.md
│   └── order-cancellation/          ← complete standalone feature
│       ├── specification.md
│       ├── acceptance-cases.yaml
│       ├── traceability-matrix.md
│       └── implementations/python/
│
├── templates/                       ← copy-paste starters
│   ├── specification.md
│   ├── acceptance-cases.yaml
│   ├── traceability-matrix.md
│   └── tfp-prompt.md
│
├── .github/workflows/stdd.yml      ← CI workflow (runs on every push)
│
└── diagrams/
    ├── stdd_development_loop.md
    ├── stdd_control_loop.md
    ├── stdd_vs_traditional.md
    ├── stdd_architecture_layers.md
    └── stdd_regeneration_model.md
```

---

## License

Licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

You are free to share and adapt this work, provided you give appropriate credit to the original author.

Author: Frank Heikens
