# STDD Architecture Layers

```mermaid
flowchart TD

A[API / Interface]
B[Application Services]
C[Domain Logic]
D[Data Layer]
E[(Database)]

A --> B
B --> C
C --> D
D --> E
```
