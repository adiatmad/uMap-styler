# uMap Styler

A Streamlit tool for bulk editing GeoJSON properties through CSV/XLSX-style workflows, including attribute joins and HTML styling for uMap-oriented data.

## What it does

The application supports workflows for:

- reading GeoJSON features into a tabular representation;
- editing feature properties through CSV/XLSX data;
- joining attributes using a selected key;
- converting tabular data back to GeoJSON;
- combining GeoJSON files;
- generating HTML styling for feature properties.

CSV input is read with UTF-8, Latin-1, and CP1252 fallbacks.

## Requirements

Python 3 and the packages listed in `requirements.txt`.

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Important

Keep geometry data intact when using the tabular workflow. Review the resulting GeoJSON before publishing it to another service.

## License

See [LICENSE](LICENSE).

## AI-Assisted Development

This project was developed and/or maintained with AI assistance. AI was used to support parts of the design, implementation, documentation, and/or maintenance workflow. The human maintainer remains responsible for reviewing, validating, and approving the project's code and outputs.


## ChatMap review and uMap publication workflow

The **ChatMap → Review → Publish to uMap** section supports a deliberate, human-reviewed workflow for Brebes or another project:

1. In [ChatMap](https://chatmap.hotosm.org/), upload the exported WhatsApp/Telegram/Signal chat archive and download its GeoJSON.
2. Upload that GeoJSON in this app. Re-imports are compared with the current review ledger.
3. Review each report, edit its properties as JSON, add reviewer notes, and set its status to `New`, `Needs correction`, `Verified`, or `Rejected`.
4. Download **verified-only GeoJSON**. If this is the first publication, open [HOT uMap](https://umap.hotosm.org/), sign in, create and save a map, then import the GeoJSON in the map editor. Inspect the features and extent before saving/sharing.
5. Download the **review ledger backup** after changes and keep it with the project. Upload that ledger in a later session to continue reviewing.

### Text-quality and consistency review

The ChatMap review panel includes a local text-quality scan for whitespace issues and same-field value variants. It can suggest likely spelling variants by comparing strings already present in the imported records; similarity is a clue, not proof that two labels mean the same thing. This is designed for mixed Indonesian/English text and avoids sending reports to an external language service.

- Scanning is read-only and does not change source properties.
- Whitespace cleanup changes only the review copy after you explicitly approve it.
- Cluster replacements require an explicit canonical value and button click. Only exact matching values in non-conflicted, non-rejected review records are changed.
- Changed records are demoted to `Needs correction`, including previously verified records, so they must be reviewed again.
- Original source properties remain unchanged. No suggestion is auto-applied or auto-published.

### Safety and synchronization limits

- Only records marked `Verified` and without an unresolved source conflict are included in the publishable GeoJSON.
- Changed records are flagged for re-review instead of silently replacing corrected data. Where a ChatMap feature has no stable ID, the importer uses an unambiguous matching geometry as a fallback; reports at shared locations can be ambiguous and must be checked by a human.
- The review ledger is the working record. The verified-only GeoJSON is a publication snapshot, not an automatic sync.
- **This version does not write directly to HOT uMap.** The project map has not yet been created, and authenticated create/update behavior has not been verified. Create the map in [HOT uMap](https://umap.hotosm.org/), import the verified-only GeoJSON through the map editor, and inspect the result before sharing it. Do not upload the review ledger to uMap.
- ChatMap exports can include personal names, messages, coordinates, and media links. Check consent, data minimization, and public visibility before publishing.

### Tests

Run the review-ledger regression tests with Python 3:

```bash
python -m unittest discover -s tests -v
```

The tests load only pure helper functions from `app.py` so Streamlit UI startup is not required.
