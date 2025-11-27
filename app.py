import streamlit as st
import pandas as pd
import io
import re

st.header("Step C – Styled HTML Generator (robust parser)")

uploaded = st.file_uploader("Upload CSV", type=["csv"])
if uploaded:
    # read CSV with pandas (let pandas guess delimiter inside cells)
    try:
        df = pd.read_csv(uploaded)
    except Exception as e:
        st.error(f"Error reading CSV: {e}")
        st.stop()

    st.write("Preview (first 5 rows):")
    st.dataframe(df.head())

    # choose column to transform
    column = st.selectbox("Choose the column containing the pipe-separated text:", df.columns)

    # separator option (in case user wants different char)
    sep_input = st.text_input("Separator (regex allowed). Default is pipe `|`:", value="|")
    try:
        sep_pattern = rf"\s*{sep_input}\s*" if sep_input == "|" else rf"\s*{re.escape(sep_input)}\s*"
    except Exception:
        sep_pattern = r"\s*\|\s*"

    # option: how to handle segments without colon
    handle_no_colon = st.selectbox("If a segment has no ':' — what to do?",
                                   ["Treat as single info row (label=Informasi)", "Skip segment"])

    generate_btn = st.button("Generate Styled HTML")

    def parse_to_html(raw_text, sep_regex, no_colon_mode="informasi"):
        """
        raw_text: original cell text
        sep_regex: regex pattern to split segments (string)
        no_colon_mode: "informasi" or "skip"
        """
        if pd.isna(raw_text) or str(raw_text).strip() == "":
            return ""

        s = str(raw_text).strip()

        # split using regex for robust trimming around separators
        parts = re.split(sep_regex, s)

        rows_html = []
        for part in parts:
            part = part.strip()
            if not part:
                continue

            # sometimes there are stray leading/trailing separators or double separators
            # try to split by first colon:
            if ":" in part:
                key, val = part.split(":", 1)
                key = key.strip()
                val = val.strip()
                if key == "":
                    key = "Informasi"
                if val == "":
                    val = "-"
                rows_html.append(f'''
  <div style="display: flex; align-items: start; margin-bottom: 8px;">
    <div style="min-width: 160px; font-weight: bold; color: #2c3e50;">{st.html_escape(key)}</div>
    <div style="flex: 1;">: {st.html_escape(val)}</div>
  </div>
                ''')
            else:
                # no colon present
                if no_colon_mode == "informasi":
                    # keep as Informasi
                    rows_html.append(f'''
  <div style="display: flex; align-items: start; margin-bottom: 8px;">
    <div style="min-width: 160px; font-weight: bold; color: #2c3e50;">Informasi</div>
    <div style="flex: 1;">: {st.html_escape(part)}</div>
  </div>
                    ''')
                else:
                    # skip this segment
                    continue

        if not rows_html:
            return ""

        card = f'''
<div style="font-family: Arial, sans-serif; background: #e8f4fd;
            border: 2px solid #b8daff; border-radius: 8px; padding: 15px; margin-bottom: 20px;">
  <div style="display: grid; gap: 8px;">
    {''.join(rows_html)}
  </div>
</div>
        '''
        return card

    # Helper to safely preview some rendered HTML (use components if many)
    import streamlit.components.v1 as components

    if generate_btn:
        # apply parser to the selected column for all rows
        st.info("Processing...")

        # compute styled_html for every row
        df = df.copy()
        df["styled_html"] = df[column].apply(lambda x: parse_to_html(x, sep_pattern,
                                                                    no_colon_mode="informasi" if handle_no_colon.startswith("Treat") else "skip"))

        st.success("Done — preview below (first 5 styled entries).")

        # show previews for first 5 non-empty styled_html
        preview_count = 0
        for idx, row in df.iterrows():
            html = row["styled_html"]
            if html and str(html).strip():
                st.markdown(f"**Row {idx} preview:**")
                components.html(html, height=260, scrolling=True)
                preview_count += 1
            if preview_count >= 5:
                break

        # prepare CSV for download
        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        csv_bytes = buffer.getvalue().encode("utf-8")

        st.download_button(
            label="⬇ Download CSV with styled_html column",
            data=csv_bytes,
            file_name="styled_output.csv",
            mime="text/csv"
        )

        st.write("If the output still looks identical to input, check the note below.")
        st.caption("Tips: make sure the selected column is the right one, and that the cell actually contains `|` separators. If your CSV contains quoted fields with `|` it should still work — pandas preserves quoted content.")

    # quick debug: show raw cell example for selected col
    st.markdown("### Debug: sample raw values from selected column")
    st.write(df[column].head(10))
