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
