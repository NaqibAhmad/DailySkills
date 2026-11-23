# Frontend (React + TypeScript)

The One Pattern for the frontend: one predictable layout per feature.

```
src/features/<feature>/
├── types/        # shared TS types + factories: the source of truth for DTO shapes
├── services/     # one API client per backend (<feature>Api.ts): every fetch, auth header, error format
├── components/   # presentational components, one primary component per file
├── hooks/        # data-fetching/state hooks (useX) when state is non-trivial
└── index.ts      # barrel: the feature's public surface only
```

- **Components ~300 lines max.** Split by sub-panel into sibling files (`PreCallPanel.tsx`, `ResearchBucketCard.tsx`). Tiny shared primitives get their own file (`StubPrimitives.tsx`).
- **All server access goes through the feature's service module**, and auth token handling lives in exactly one place there. Components call the service, or a hook that does.
- **State lives at the lowest common owner**; lift it to the shell only when several panels share it. Apply server responses with functional `setState` so writes never use a stale closure.
- **Types mirror the API contract** (camelCase) and are imported from `types/`.
- **New code reads like the code around it**: same styling approach, import style and naming.

## Checks

- [ ] Components ~300 lines; one primary component per file
- [ ] Every request to the feature's backend goes through `services/`
- [ ] DTO types come from `types/`; new code has no `any`
- [ ] `tsc --noEmit` and eslint are clean on the touched feature folder
