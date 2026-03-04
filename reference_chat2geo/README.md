# Reference Chat2Geo-like Skeleton (CortexGIS)

This folder contains a minimal skeleton inspired by GeoRetina/chat2geo to help you bootstrap CortexGIS features: RAG, tool-calling, planner, and a simple API flow.

Structure:
- `app/api/chat/route.ts`: minimal API route demonstrating tool registration and streaming placeholder.
- `lib/tools.ts`: stubbed tool implementations (geospatial analysis, RAG query, report drafting).
- `prompts/cot_examples.md`: example Chain-of-Thought prompt templates.
- `schemas/workflow_schema.json`: JSON schema for workflow definitions.

Quick start (from workspace root):

```bash
cd reference_chat2geo
# install dependencies in your preferred package manager
# e.g. npm install
# run the Next.js dev server if you add a UI
# npm run dev
```

This is intentionally minimal — tell me which components you want expanded (RAG, LangChain, executor adapters, Streamlit UI, dataset ingest scripts), and I will scaffold them next.