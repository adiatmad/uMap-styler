import streamlit as st
import pandas as pd
import io

st.header("Step C – Styled HTML Generator")

uploaded = st.file_uploader("Upload CSV", type=["csv"])
if uploaded:
    df = pd.read_csv(uploaded)
    st.write("Preview:", df.head())

    # Pick column to transform
    column = st.selectbox("Choose the column containing the 'key | value | key | value' text:", df.columns)

    def parse_to_html(raw):
        if pd.isna(raw):
            return ""

        # Split by |
        parts = [p.strip() for p in raw.split("|") if ":" in p]
        rows = []

        for item in parts:
            key, value = item.split(":", 1)
            key = key.strip()
            value = value.strip()

            rows.append(f"""
  <div style="display: flex; align-items: start; margin-bottom: 8px;">
    <div style="min-width: 160px; font-weight: bold; color: #2c3e50;">{key}</div>
    <div style="flex: 1;">: {value}</div>
  </div>
            """)

        return f"""
<div style="font-family: Arial, sans-serif; background: #e8f4fd;
            border: 2px solid #b8daff; border-radius: 8px; padding: 15px; margin-bottom: 20px;">
  <div style="display: grid; gap: 8px;">
    {''.join(rows)}
  </div>
</div>
        """

    if st.button("Generate Styled HTML"):
        df["styled_html"] = df[column].apply(parse_to_html)

        # Export
        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        st.download_button(
            "Download CSV with Styled HTML",
            buffer.getvalue(),
            "styled_output.csv",
            "text/csv"
        )

        st.success("Done! Preview below:")
        st.markdown(df["styled_html"].iloc[0], unsafe_allow_html=True)
