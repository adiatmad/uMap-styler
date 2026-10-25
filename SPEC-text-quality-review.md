# ChatMap text-quality review — acceptance criteria

## Goal
Extend the existing single-file Streamlit app so coordinators can detect likely text-quality issues and inconsistent labels in mixed Indonesian/English ChatMap reports, review suggested corrections, and explicitly approve safe bulk replacements without bypassing the review ledger or verified-only publishing gate.

## Design decisions
- Keep the application UI and production helpers in `app.py`; no second application.
- Use local deterministic checks by default: whitespace normalization and similarity clustering over values already present in the imported dataset. No report text is sent to third-party services.
- Treat similarity as a suggestion, never proof of equivalence. Do not ship a hard-coded Indonesian/English dictionary that would misclassify place names, local terms, or code-switching.
- Preserve raw source properties. Corrections only affect `reviewed_properties`.
- Explicit bulk mappings require human confirmation. Changed non-rejected, non-conflicted records become `Needs correction`; conflicted records are skipped; rejected records remain rejected.
- Keep current HTML styling tools and verified-only GeoJSON export behavior unchanged.

## Acceptance criteria
1. A quality scan flags leading/trailing or repeated whitespace and returns a proposed normalized value without mutating input.
2. Cross-record checks identify formatting variants (case/spacing differences) and likely near-duplicate text values in the same property field, with a similarity score and suggested canonical value.
3. Findings are labelled as suggestions, not asserted semantic corrections; local names and mixed-language text remain editable by a human.
4. Bulk replacement occurs only after an explicit mapping is supplied; it only touches exact matches in reviewed properties of non-conflicted records.
5. Any changed record that was not rejected is demoted to `Needs correction`, including previously verified records. Conflicted and rejected records are not changed.
6. Raw source snapshots are never changed by quality checks or bulk replacements.
7. Existing conflict and verified-only export gates remain intact.
8. Tests cover conservative normalization, non-mutating scan, formatting/typo clustering, approved bulk replacement, status demotion, conflict/rejected skips, and invalid inputs.
9. CI compiles `app.py` and runs all unit tests. Changes are proposed through a PR, not committed directly to `main`.

## Test plan
- Add failing unit tests first for each pure helper.
- Implement helpers in `app.py` and a review UI for scan findings and explicit bulk approval.
- Run `python -m py_compile app.py` and `python -m unittest discover -s tests -v` locally if execution is available; otherwise rely on GitHub Actions and inspect its actual logs before reporting pass/fail.
- Inspect the PR diff and CI status. Do not merge without separate user approval.
