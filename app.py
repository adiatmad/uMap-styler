import streamlit as st
import re

st.set_page_config(page_title="uMap HTML Generator Pro", page_icon="🗺️", layout="wide")

st.title("🗺️ uMap HTML Generator Pro")
st.caption("Transform your text into clean, formatted uMap HTML descriptions")

# --- Sidebar controls ---
st.sidebar.header("⚙️ Settings")
bg_color = st.sidebar.color_picker("🖌️ Pick background color", "#f8f9fa")
highlight_color = st.sidebar.color_picker("📦 Keterangan box color", "#fff3cd")
auto_preview = st.sidebar.checkbox("Auto-preview while typing", value=False)
auto_page_break = st.sidebar.checkbox("Auto page break after ':'", value=True)
show_keterangan_box = st.sidebar.checkbox("Show 'Keterangan Tambahan' as box", value=True)

# --- Input area ---
st.subheader("✏️ Live Editor")
input_data = st.text_area(
    "Paste or type your text below:",
    height=280,
    placeholder=(
        "Example:\n"
        "Nama POI: SDN 1 Tiyingtali\n"
        "Desa: Tiing tali\n"
        "Banjar: Banjar dinas Tiyingtali kelod\n"
        "Jenis Fasum: (Gedung sekolah)\n"
        "Daya Tampung: +-600\n"
        "Fasilitas Pendukung: (listrik, sumber air, toilet)\n"
        "Kontak person: \n"
        "Jenis Bangunan: permanen\n"
        "Luas Area Terbuka: 25 are\n"
        "Keterangan Tambahan: di rencanakan sebagai tempat pengungsian"
    ),
)

# --- Processing function ---
def generate_html(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    rows = []
    keterangan_value = ""

    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)
            key, value = key.strip(), value.strip()
            if key.lower().startswith("keterangan tambahan"):
                keterangan_value = value
            else:
                if auto_page_break:
                    value = re.sub(r":", ":<br>", value)
                rows.append(f"""
                    <tr>
                        <td style='font-weight:bold; color:#2c3e50; vertical-align:top; padding:6px 12px; width:180px;'>
                            {key}
                        </td>
                        <td style='padding:6px 12px;'>
                            {value}
                        </td>
                    </tr>
                """)

    # Main table
    table_html = f"""
    <table style='width:100%; border-collapse:collapse;'>
        {''.join(rows)}
    </table>
    """

    # Optional keterangan box
    if show_keterangan_box and keterangan_value:
        keterangan_box = f"""
        <div style='background:{highlight_color}; margin-top:12px; padding:10px; border-radius:6px;'>
            <strong>Keterangan Tambahan:</strong> {keterangan_value}
        </div>
        """
    else:
        keterangan_box = ""

    # Combine
    final_html = f"""
    <div style='font-family:Arial, sans-serif; background:{bg_color}; border:2px solid #dee2e6;
                border-radius:10px; padding:16px; line-height:1.5;'>
        {table_html}
        {keterangan_box}
    </div>
    """
    return final_html.strip()

# --- Run & Preview ---
run_clicked = st.button("🚀 Run & Preview")

if run_clicked or (auto_preview and input_data.strip()):
    if not input_data.strip():
        st.warning("⚠️ Please input some text first.")
    else:
        html_output = generate_html(input_data)
        st.success("✅ HTML Generated Successfully")
        st.components.v1.html(html_output, height=400, scrolling=True)
        st.code(html_output, language="html")

st.markdown("---")
st.caption("💡 Tip: Use sidebar to customize background color or toggle the Keterangan box.")
