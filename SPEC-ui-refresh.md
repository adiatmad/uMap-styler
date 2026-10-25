# uMap Styler UI refresh — acceptance criteria

## Goal
Make the existing single-file Streamlit application easier to navigate for the primary ChatMap review workflow while keeping every legacy GeoJSON/CSV/HTML tool accessible.

## Design
- A simple sidebar workspace selector with two destinations: ChatMap review (default) and GeoJSON / CSV / HTML tools.
- A clear title, concise privacy/review-gate explanation, restrained visual styling, and consistent section hierarchy.
- Keep all production app UI and logic in app.py. No new UI framework or second app.
- Keep the current review ledger, source-preservation rules, conflict handling, verified-only export gate, and HTML styling implementation unchanged.

## Acceptance criteria
1. First-time visitors land on ChatMap review rather than scrolling through every utility.
2. The legacy GeoJSON conversion, combine, attribute join, HTML styling, and quick converter remain available under the secondary workspace.
3. Switching workspaces does not clear session state or replace source/review data.
4. UI copy makes the verified-only manual publishing gate and no-auto-publish behavior clear.
5. CSS is cosmetic only and has a usable responsive layout; controls remain standard Streamlit controls.
6. Existing regression tests continue to pass and app.py compiles.
7. No publish logic or source/review data semantics change in this UI-only commit.
