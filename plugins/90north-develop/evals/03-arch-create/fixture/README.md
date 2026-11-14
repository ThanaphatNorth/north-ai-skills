# orders

A small order service. Layers, from the inside out:

- `src/domain/` holds the rules and knows nothing else.
- `src/application/` holds the use cases and may use the domain.
- `src/infrastructure/` holds storage and may use the application and the domain.
- `src/interface/` holds the HTTP handlers. A handler calls a use case; it never reaches storage itself.

Tests: `node --test`
