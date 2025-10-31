import streamlit as st
import re

st.set_page_config(page_title="uMap HTML Generator Pro", page_icon="🗺️", layout="wide")

st.title("🗺️ uMap HTML Generator Pro")
st.caption("Transform your text or POI data into beautiful HTML instantly — live editor mode")

# --- Sidebar controls ---
st.sidebar.header("⚙️ Settings")
bg_color = st.sidebar.color_picker("Pick background color", "#fff3cd")
auto_preview = st.sidebar.checkbox("Auto-preview on edit", value=False)
auto_page_break = st.sidebar.checkbox("Auto page break after ':'", value=True)
use_table = st.sidebar.checkbox("Render text in table", value=True)

# --- Editor ---
st.subheader("✏️ Live Text Editor")
input_data = st.text_area(
    "Write or paste your text below:",
    height=250,
    placeholder="Example:\nNama Jalan: Jl. Merdeka\nJenis Jalan: Aspal\nKondisi Jalan: Baik\nKeterangan: Jalan evakuasi utama",
)

# --- Processing Function ---
def process_text(text: str) -> str:
    if auto_page_break:
        text = re.sub(r":", ":<br>", text)

    if use_table:
        rows = [
            f"<tr><td style='font-weight:bold; padding-right:8px;'>{line.split(':', 1)[0]}</td><td>{line.split(':', 1)[1] if ':' in line else ''}</td></tr>"
            for line in text.splitlines() if line.strip()
        ]
        html = f"""
        <div style='font-family:Arial, sans-serif; background:{bg_color}; border:2px solid #ccc; border-radius:8px; padding:12px;'>
            <table style='width:100%; border-collapse:collapse; font-size:14px;'>
                {"".join(rows)}
            </table>
        </div>
        """
    else:
        html = f"""
        <div style='font-family:Arial, sans-serif; background:{bg_color}; border:2px solid #ccc; border-radius:8px; padding:12px; line-height:1.6;'>
            {text.replace("\\n", "<br>")}
        </div>
        """
    return html.strip()

# --- Run Button ---
run_clicked = st.button("🚀 Run & Preview")

if run_clicked or (auto_preview and input_data.strip()):
    if not input_data.strip():
        st.warning("⚠️ Please enter some text first.")
    else:
        html_output = process_text(input_data)
        st.success("✅ Generated HTML below")
        st.components.v1.html(html_output, height=350, scrolling=True)
        st.code(html_output, language="html")

# --- Footer ---
st.markdown("---")
st.caption("💡 Tip: Adjust background color and toggles in the sidebar to experiment with layout and style.")
