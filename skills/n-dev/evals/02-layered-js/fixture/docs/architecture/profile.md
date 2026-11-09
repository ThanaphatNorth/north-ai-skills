# Architecture profile: orders

Verified at: `fixture` on 2026-11-09 · Enforced by: `.ndev.toml`
Shape: hexagonal (ports and adapters) · Intended = actual: yes

## Layers and dependency direction

| Layer | Holds | May import | Why |
|---|---|---|---|
| domain | pure order rules | nothing | rules must not depend on storage or HTTP |
| application | use cases; each takes its ports as arguments | domain | use cases are tested with in-memory ports |
| infrastructure | adapters for storage | application, domain | swap storage without touching rules |
| interface | HTTP handlers; call use cases only | application, domain | handlers never reach storage directly |

`src/main.js` is the composition root: the only file that builds adapters and hands them to handlers.

## Extension recipes

| To add | Create | Wire in |
|---|---|---|
| a route | a use case in `src/application/`, a handler factory in `src/interface/` | one line in `src/main.js` |

## Commands

| Purpose | Command |
|---|---|
| Full suite | `node --test` |
