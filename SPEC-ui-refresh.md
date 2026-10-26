# uMap Styler workflow navigation — acceptance criteria

## Goal
Give first-time community mappers a plain-language starting point, separate reviewing reports from preparing a map update, and keep specialist data tools accessible without cluttering the main workflow.

## Navigation
A sidebar workflow selector offers four destinations:
1. **Beginner guide** (default): explains the three-step process and translates review labels into plain language.
2. **Review ChatMap reports**: restore a review backup, load the latest ChatMap export, inspect text suggestions, and correct/approve individual reports.
3. **Prepare map for uMap**: preview and download only verified, conflict-free reports plus a review backup.
4. **Advanced tools**: GeoJSON combine/conversion, CSV attribute joins, HTML styling, and the quick HTML converter.

## Safety and data behavior
- The original report and source geometry remain preserved.
- Newer source changes are flagged for human review; they never silently overwrite reviewed data.
- Suggestions are advisory and never auto-applied.
- Only verified, conflict-free records are included in the map export.
- Exporting does not publish or sync anything to uMap; a person imports the approved file and checks the map manually.
- Switching destinations must not clear the review ledger or other session state.

## Acceptance criteria
1. First-time visitors land on the beginner guide, not a long utility page.
2. The guide explains the workflow without requiring users to understand GeoJSON or other technical terms.
3. Report review and map preparation appear as separate destinations.
4. All legacy tools remain accessible under Advanced tools.
5. Each destination renders without runtime exceptions; tests cover default navigation and switching through all destinations.
6. Existing review-ledger, source-preservation, conflict, correction, and verified-only export tests continue to pass.
7. `app.py` compiles and CI passes before merge.
8. No automatic publishing or source/review data semantics are introduced by this navigation change.
