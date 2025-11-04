import streamlit as st
import re

st.set_page_config(page_title="uMap HTML Generator", page_icon="🗺️", layout="wide")

st.title("🗺️ uMap HTML Generator")
st.subheader("Transform your road & POI data into beautiful uMap descriptions")

# Instructions
with st.expander("📋 How to use"):
    st.markdown("""
    1. **Paste your raw data** in the text area below (use | as separator)
    2. **Click 'Process Data'** 
    3. **Copy the HTML output** for each entry
    4. **Paste into uMap** description fields
    
    The app automatically detects:
    - 🛣️ **Road descriptions** (starts with '*Deskripsi jalan*')
    - 🏢 **POI/Facilities** (starts with 'Nama PO')
    - 🔄 **Other entries** (kept as-is)
    
    **New features:**
    - Use `|` as field separator
    - Page breaks after each separator
    - Bold titles for all sections
    - Universal styling for any input type
    - Automatic field name extraction (removes "Info 1", "Info 2", etc.)
    - Bold field names before colons
    """)

# Input area
input_data = st.text_area(
    "Paste your entire list here (use | as separator):",
    height=300,
    placeholder="Paste your data here...\n\nExample:\n*Deskripsi jalan* | nama jalan (jalur contoh) | Jenis jalan (jalan aspal) | Lebar Jalan (5m)...\nNama POI | Contoh Facility | Jenis Fasum (sekolah) | Daya Tampung (100 orang)...\n\nOr like your example:\nSDN 2 Tiying tali | Desa: Tiying tali | Banjar: Banjar dinas tiyingtali kaler | Jenis: Gedung sekolah..."
)

# Universal styling function
def create_universal_html(title, fields, style_type="default"):
    """
    Create HTML for any type of data with universal styling
    
    Parameters:
    - title: The main title (will be bold)
    - fields: Dictionary of field_name: field_value pairs
    - style_type: "road", "poi", or "default"
    """
    
    # Define styles based on type
    styles = {
        "road": {
            "background": "#fff3cd",
            "border": "2px solid #ffeaa7",
            "title_color": "#2c3e50"
        },
        "poi": {
            "background": "#e8f4fd",
            "border": "2px solid #b8daff", 
            "title_color": "#2c3e50"
        },
        "default": {
            "background": "#f8f9fa",
            "border": "2px solid #dee2e6",
            "title_color": "#495057"
        }
    }
    
    style = styles.get(style_type, styles["default"])
    
    # Build fields HTML
    fields_html = ""
    for field_name, field_value in fields.items():
        if field_value:  # Only add if value exists
            fields_html += f'''
<div style="display: flex; align-items: start; margin-bottom: 8px;">
<div style="min-width: 160px; font-weight: bold; color: {style['title_color']};">{field_name}:</div>
<div style="flex: 1;">{field_value}</div>
</div>
'''
    
    html_template = f'''
<div style="font-family: Arial, sans-serif; background: {style['background']}; border: {style['border']}; border-radius: 8px; padding: 15px; margin-bottom: 20px;">
<div style="font-size: 18px; font-weight: bold; color: {style['title_color']}; margin-bottom: 12px; border-bottom: 1px solid {style['border'].split(' ')[2]}; padding-bottom: 5px;">{title}</div>
<div style="display: grid; gap: 8px;">
{fields_html}
</div>
</div>
'''
    return html_template.strip()

def extract_field_name_value(part):
    """
    Extract field name and value from a part.
    Removes 'Info 1', 'Info 2' etc and uses text before colon as field name.
    """
    # Remove "Info X:" patterns
    cleaned_part = re.sub(r'^Info\s*\d+\s*:\s*', '', part.strip())
    
    # Split by first colon to separate field name and value
    if ':' in cleaned_part:
        field_name, field_value = cleaned_part.split(':', 1)
        field_name = field_name.strip()
        field_value = field_value.strip()
    else:
        # If no colon, use generic field name
        field_name = "Informasi"
        field_value = cleaned_part
    
    return field_name, field_value

def process_road_data(text):
    """Process road data with pipe separator support"""
    parts = [part.strip() for part in text.split('|')]
    
    # Extract data using both regex and pipe parsing
    fields = {}
    
    # If we have pipe-separated parts, use them
    if len(parts) > 1:
        for i, part in enumerate(parts[1:], 1):  # Skip first part (title)
            field_name, field_value = extract_field_name_value(part)
            if field_value:  # Only add if value exists
                fields[field_name] = field_value
    
    # Fallback to regex parsing if pipe parsing didn't work well
    if not fields:
        nama_match = re.search(r'nama jalan\s*\(\s*(jalur[^)]+)', text, re.IGNORECASE)
        jenis_match = re.search(r'Jenis jalan\s*\(\s*([^)]+)', text, re.IGNORECASE)
        lebar_match = re.search(r'Lebar Jalan\s*\(\s*([^)]+)', text, re.IGNORECASE)
        karakter_match = re.search(r'karakter jalan\s*\(\s*([^)]+)', text, re.IGNORECASE)
        kondisi_match = re.search(r'Kondisi Jalan\s*\(\s*([^)]+)', text, re.IGNORECASE)
        keterangan_match = re.search(r'Keterangan Tambahan\s*:([^<]*)', text, re.IGNORECASE)
        
        fields = {
            'Nama Jalan': nama_match.group(1).strip() if nama_match else "jalur",
            'Jenis Jalan': jenis_match.group(1).strip() if jenis_match else "",
            'Lebar Jalan': lebar_match.group(1).strip() if lebar_match else "",
            'Karakter Jalan': karakter_match.group(1).strip() if karakter_match else "",
            'Kondisi Jalan': kondisi_match.group(1).strip() if kondisi_match else "",
            'Keterangan': keterangan_match.group(1).strip() if keterangan_match else "jalan evakuasi"
        }
    
    # Clean up fields - remove empty ones
    fields = {k: v for k, v in fields.items() if v and v.strip()}
    
    return create_universal_html("🛣️ Deskripsi Jalan", fields, "road")

def process_poi_data(text):
    """Process POI data with pipe separator support"""
    parts = [part.strip() for part in text.split('|')]
    
    fields = {}
    
    # If we have pipe-separated parts, use them
    if len(parts) > 1:
        for i, part in enumerate(parts[1:], 1):  # Skip first part (title)
            field_name, field_value = extract_field_name_value(part)
            if field_value:  # Only add if value exists
                fields[field_name] = field_value
    
    # Fallback to regex parsing
    if not fields:
        nama_match = re.search(r'Nama POI?\s*:?\s*([^\n\(]+)', text, re.IGNORECASE)
        jenis_match = re.search(r'Jenis Fasum:\s*\(([^)]+)', text, re.IGNORECASE)
        daya_match = re.search(r'Daya Tampung:\s*([^\n]+)', text, re.IGNORECASE)
        fasilitas_match = re.search(r'Fasilitas Pendukung\s*\(([^)]+)', text, re.IGNORECASE)
        keterangan_match = re.search(r'Keterangan Tambahan:\s*([^\n]+)', text, re.IGNORECASE)
        
        fields = {
            'Nama Fasilitas': nama_match.group(1).strip() if nama_match else "",
            'Jenis': jenis_match.group(1).strip() if jenis_match else "Fasilitas Umum",
            'Daya Tampung': daya_match.group(1).strip() if daya_match else "",
            'Fasilitas': fasilitas_match.group(1).strip() if fasilitas_match else "",
            'Keterangan': keterangan_match.group(1).strip() if keterangan_match else "tempat pengungsian"
        }
    
    # Clean up fields
    fields = {k: v for k, v in fields.items() if v and v.strip()}
    
    return create_universal_html("🏢 Fasilitas Umum", fields, "poi")

def process_generic_data(text):
    """Process any generic data with pipe separator"""
    parts = [part.strip() for part in text.split('|')]
    
    if len(parts) == 1:
        # Single part - just return as is
        field_name, field_value = extract_field_name_value(parts[0])
        fields = {field_name: field_value}
        title = "📌 Informasi"
    else:
        # Multiple parts - use first as title, rest as fields
        title = f"📌 {parts[0]}"
        fields = {}
        for i, part in enumerate(parts[1:], 1):
            field_name, field_value = extract_field_name_value(part)
            if field_value:  # Only add if value exists
                fields[field_name] = field_value
    
    return create_universal_html(title, fields, "default")

# Process button
if st.button("🚀 Process Data", type="primary"):
    if not input_data.strip():
        st.warning("Please paste some data first!")
    else:
        # Process data
        lines = input_data.strip().split('\n')
        results = []
        stats = {"roads": 0, "pois": 0, "other": 0}
        
        for line in lines:
            if not line.strip():
                continue
            
            line_lower = line.lower()
            
            if '*deskripsi jalan*' in line_lower or 'deskripsi jalan' in line_lower:
                html = process_road_data(line)
                results.append(("🛣️ ROAD", html))
                stats["roads"] += 1
            elif 'nama po' in line_lower:
                html = process_poi_data(line)
                results.append(("🏢 POI", html))
                stats["pois"] += 1
            else:
                html = process_generic_data(line)
                results.append(("📌 OTHER", html))
                stats["other"] += 1

        # Display results
        st.success(f"✅ Processed {len(results)} entries (Roads: {stats['roads']}, POIs: {stats['pois']}, Other: {stats['other']})")
        
        # Add page break styling
        st.markdown("""
        <style>
        .page-break {
            page-break-after: always;
            break-after: page;
        }
        </style>
        """, unsafe_allow_html=True)
        
        for i, (entry_type, result) in enumerate(results, 1):
            with st.expander(f"{entry_type} - Entry {i}"):
                st.components.v1.html(result, height=400)
                st.code(result, language='html')
                
                # Add page break after each entry in code view
                if i < len(results):
                    st.markdown('<div class="page-break"></div>', unsafe_allow_html=True)

# Example data
with st.expander("📝 Example Input Format"):
    st.markdown("""
    **Using Pipe Separators (Recommended):**
    ```
    SDN 2 Tiying tali | Desa: Tiying tali | Banjar: Banjar dinas tiyingtali kaler | Jenis: Gedung sekolah | Daya Tampung: +-400 | Fasilitas: listrik, sumber air, tollet | Bangunan: permanent | Luas Area: 15 are | Keterangan: di rencanakan sebagai tempat pengungsian
    ```
    
    **Or with your original format:**
    ```
    *Deskripsi jalan* | Jalan Evakuasi Utama | Jenis jalan (jalan aspal) | Lebar Jalan (8 meter) | Karakter jalan (lurus) | Kondisi Jalan (baik) | Keterangan Tambahan: jalan utama evakuasi
    Nama POI | SDN Contoh Sekolah | Jenis Fasum (sekolah) | Daya Tampung (200 orang) | Fasilitas Pendukung (lapangan, ruang kelas) | Keterangan Tambahan: tempat pengungsian sementara
    ```
    
    **The app will automatically:**
    - Remove "Info 1", "Info 2", etc. labels
    - Make field names before colons bold
    - Create clean, professional HTML output
    """)