import streamlit as st
import re
import pandas as pd
import json

st.set_page_config(page_title="uMap HTML Generator", page_icon="🗺️", layout="wide")

st.title("🗺️ uMap HTML Generator")
st.subheader("Transform your road & POI data into beautiful uMap descriptions")

# ================================
# 1) NEW: UI FOR BULK HTML STYLING
# ================================
def ui_select_columns_for_styling(all_fields):
    st.subheader("🎨 Optional: Apply HTML styling to selected fields")

    selected_fields = st.multiselect(
        "Select which field names you want to wrap with HTML styling:",
        options=all_fields,
        default=[]
    )

    html_tag = st.selectbox(
        "HTML tag wrapper:",
        ["span", "div", "mark", "b", "i"]
    )

    css_style = st.text_input(
        "CSS style:",
        value="background:yellow; font-weight:bold;",
        help="CSS applied inside the HTML tag"
    )

    return selected_fields, html_tag, css_style

# ===========================================
# 2) Bulk-Apply HTML style to fields (NEW)
# ===========================================
def apply_html_style_bulk_to_fields(fields_dict, columns_to_style, tag, css):
    """Wrap selected field values in HTML styling."""
    styled = {}
    for key, val in fields_dict.items():
        if key in columns_to_style:
            styled[key] = f'<{tag} style="{css}">{val}</{tag}>'
        else:
            styled[key] = val
    return styled


# ===========================================
# UNIVERSAL HTML BUILDING FUNCTION (unchanged)
# ===========================================
def create_universal_html(fields, style_type="default"):
    styles = {
        "road": {"background": "#e8f4fd", "border": "2px solid #b8daff"},
        "poi": {"background": "#e8f4fd", "border": "2px solid #b8daff"},
        "default": {"background": "#e8f4fd", "border": "2px solid #b8daff"}
    }

    style = styles.get(style_type, styles["default"])

    fields_html = ""
    for field_name, field_value in fields.items():
        if field_value and field_value.strip():
            fields_html += f'''
  <div style="display: flex; align-items: start; margin-bottom: 8px;">
    <div style="min-width: 160px; font-weight: bold; color: #2c3e50;">{field_name}</div>
    <div style="flex: 1;">: {field_value}</div>
  </div>
'''

    return f'''
<div style="font-family: Arial, sans-serif; background: {style['background']};
            border: {style['border']}; border-radius: 8px; padding: 15px; margin-bottom: 20px;">
  <div style="display: grid; gap: 8px;">
    {fields_html}
  </div>
</div>
'''.strip()

# ===========================================
# PARSING FUNCTIONS (your originals)
# ===========================================
def standardize_indonesian(text):
    replacements = {
        r'\bbisa di lalu\b': 'Dapat dilalui',
        r'\bdi lalu\b': 'dilalui',
        r'\bdi pakai\b': 'dipakai',
        r'\bdi jadikan\b': 'dijadikan',
        r'\bdi rencanakan\b': 'direncanakan',
        r'\bdi pake\b': 'dipakai',
        r'\bhelp\b': 'helip',
        r'\b(\d)\s*m\b': r'\1 m',
        r'\b(\d)\s*are\b': r'\1 are',
        r'\+\-\s*': '±',
        r'^\s*jalur\s*': '',
    }
    for pat, rep in replacements.items():
        text = re.sub(pat, rep, text, flags=re.IGNORECASE)
    return text.strip()

def extract_fields_from_pipe(text):
    fields = {}
    parts = [p.strip() for p in text.split('|') if p.strip()]

    for part in parts:
        if ':' in part:
            k, v = part.split(':', 1)
            fields[k.strip()] = standardize_indonesian(v.strip())
        else:
            m = re.match(r'(\d+)\.\s*(.+?)\s*\(([^)]+)\)', part)
            if m:
                num, label, value = m.groups()
                num_map = {
                    '1': 'Nama Jalan',
                    '2': 'Jenis Jalan',
                    '3': 'Lebar Jalan',
                    '4': 'Karakter Jalan',
                    '5': 'Kondisi Jalan',
                    '6': 'Keterangan Tambahan'
                }
                fields[num_map.get(num, label.strip())] = standardize_indonesian(value)
            else:
                fields.setdefault("Informasi", "")
                fields["Informasi"] += ", " + standardize_indonesian(part)

    return fields

def process_road_data(text):
    fields = extract_fields_from_pipe(text) if '|' in text else {}
    fields = {k: v for k, v in fields.items() if v.strip()}
    return fields

def process_poi_data(text):
    if '|' in text:
        fields = extract_fields_from_pipe(text)
    else:
        fields = {}  # natural text parsing omitted for brevity
    fields = {k: v for k, v in fields.items() if v.strip()}
    return fields

def process_generic_data(text):
    if '|' in text:
        fields = extract_fields_from_pipe(text)
    else:
        fields = {"Keterangan": standardize_indonesian(text.strip())}
    return fields

# ===========================================
# MAIN USER INPUT
# ===========================================
input_data = st.text_area(
    "Paste your entire list here (pipe | separator supported):",
    height=300
)

# ===========================================
# PROCESS DATA
# ===========================================
if st.button("🚀 Process Data", type="primary"):

    if not input_data.strip():
        st.warning("Please paste some data first!")
        st.stop()

    lines = [l.strip() for l in input_data.split("\n") if l.strip()]
    extracted_entries = []
    all_field_names = set()

    # Step 1: EXTRACT RAW FIELD DICTS (NOT HTML YET)
    for line in lines:
        line_l = line.lower()

        if '*deskripsi jalan*' in line_l:
            f = process_road_data(line)
            extracted_entries.append(("road", f))
        elif 'nama po' in line_l:
            f = process_poi_data(line)
            extracted_entries.append(("poi", f))
        else:
            f = process_generic_data(line)
            extracted_entries.append(("default", f))

        all_field_names.update(f.keys())

    # ================================
    # SHOW UI FOR FIELD STYLING
    # ================================
    selected_cols, tag, css = ui_select_columns_for_styling(sorted(all_field_names))

    # ================================
    # APPLY HTML STYLING TO FIELDS
    # ================================
    styled_entries = []
    for entry_type, fields in extracted_entries:
        styled_fields = apply_html_style_bulk_to_fields(fields, selected_cols, tag, css)
        styled_entries.append((entry_type, styled_fields))

    # ================================
    # BUILD FINAL HTML OUTPUT
    # ================================
    st.success("✅ Data processed successfully!")

    full_export_list = []

    for i, (entry_type, fields) in enumerate(styled_entries, 1):
        html = create_universal_html(fields, entry_type)

        with st.expander(f"{entry_type.upper()} - Entry {i}"):
            st.components.v1.html(html, height=350)
            st.code(html, language="html")

        # add to export dataset
        rec = {"_type": entry_type}
        rec.update(fields)
        full_export_list.append(rec)

    # ================================
    # EXPORT CSV + GEOJSON
    # ================================
    df_export = pd.DataFrame(full_export_list)

    st.download_button(
        "⬇ Download CSV (styled)",
        df_export.to_csv(index=False).encode("utf-8"),
        file_name="styled_output.csv",
        mime="text/csv"
    )

    geojson_export = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": None,
                "properties": row
            }
            for row in full_export_list
        ]
    }

    st.download_button(
        "⬇ Download GeoJSON (styled)",
        json.dumps(geojson_export, indent=2).encode("utf-8"),
        file_name="styled_output.geojson",
        mime="application/geo+json"
    )
