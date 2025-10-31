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
    """)

# Input area
input_data = st.text_area(
    "Paste your entire list here (use | as separator):",
    height=300,
    placeholder="Paste your data here...\n\nExample:\nnama jalan:jalur kelakah melingkar| Jenis jalan:Jalan desa| Lebar Jalan:2m| karakter jalan:beton..."
)

# Universal styling function
def create_universal_html(fields, style_type="default"):
    """
    Create HTML for any type of data with universal styling
    Tanpa title di dalam HTML
    """
    
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
        if field_value:
            # Capitalize first letter of field name
            capitalized_field_name = field_name[0].upper() + field_name[1:] if field_name else ""
            
            fields_html += f'''
<div style="display: flex; align-items: start; margin-bottom: 8px;">
<div style="min-width: 160px; font-weight: bold; color: {style['title_color']};">{capitalized_field_name}</div>
<div style="flex: 1;">{field_value}</div>
</div>
'''
    
    html_template = f'''
<div style="font-family: Arial, sans-serif; background: {style['background']}; border: {style['border']}; border-radius: 8px; padding: 15px; margin-bottom: 20px;">
<div style="display: grid; gap: 8px;">
{fields_html}
</div>
</div>
'''
    return html_template.strip()

def extract_field_name_value(part):
    """
    Extract field name and value from a part.
    Removes colon from field name and adds ": " to the beginning of value.
    """
    # Remove "Info X:" patterns
    cleaned_part = re.sub(r'^Info\s*\d+\s*:\s*', '', part.strip())
    
    # Split by first colon to separate field name and value
    if ':' in cleaned_part:
        field_name, field_value = cleaned_part.split(':', 1)
        field_name = field_name.strip()  # No colon here
        field_value = f": {field_value.strip()}"  # Add colon with space to value
    else:
        # If no colon, use generic field name
        field_name = "Informasi"
        field_value = cleaned_part
    
    return field_name, field_value

def process_road_data(text):
    """Process road data with pipe separator support"""
    parts = [part.strip() for part in text.split('|')]
    
    fields = {}
    
    # If we have pipe-separated parts, use them
    if len(parts) > 1:
        for i, part in enumerate(parts[1:], 1):
            field_name, field_value = extract_field_name_value(part)
            if field_value:
                fields[field_name] = field_value
    
    # Fallback to regex parsing
    if not fields:
        nama_match = re.search(r'nama jalan\s*\(\s*(jalur[^)]+)', text, re.IGNORECASE)
        jenis_match = re.search(r'Jenis jalan\s*\(\s*([^)]+)', text, re.IGNORECASE)
        lebar_match = re.search(r'Lebar Jalan\s*\(\s*([^)]+)', text, re.IGNORECASE)
        karakter_match = re.search(r'karakter jalan\s*\(\s*([^)]+)', text, re.IGNORECASE)
        kondisi_match = re.search(r'Kondisi Jalan\s*\(\s*([^)]+)', text, re.IGNORECASE)
        keterangan_match = re.search(r'Keterangan Tambahan\s*:([^<]*)', text, re.IGNORECASE)
        
        if nama_match:
            fields['Nama Jalan'] = f": {nama_match.group(1).strip()}"
        if jenis_match:
            fields['Jenis Jalan'] = f": {jenis_match.group(1).strip()}"
        if lebar_match:
            fields['Lebar Jalan'] = f": {lebar_match.group(1).strip()}"
        if karakter_match:
            fields['Karakter Jalan'] = f": {karakter_match.group(1).strip()}"
        if kondisi_match:
            fields['Kondisi Jalan'] = f": {kondisi_match.group(1).strip()}"
        if keterangan_match:
            fields['Keterangan'] = f": {keterangan_match.group(1).strip()}"
    
    return create_universal_html(fields, "road")

def process_poi_data(text):
    """Process POI data with pipe separator support"""
    parts = [part.strip() for part in text.split('|')]
    
    fields = {}
    
    # If we have pipe-separated parts, use them
    if len(parts) > 1:
        for i, part in enumerate(parts[1:], 1):
            field_name, field_value = extract_field_name_value(part)
            if field_value:
                fields[field_name] = field_value
    
    # Fallback to regex parsing
    if not fields:
        nama_match = re.search(r'Nama POI?\s*:?\s*([^\n\(]+)', text, re.IGNORECASE)
        jenis_match = re.search(r'Jenis Fasum:\s*\(([^)]+)', text, re.IGNORECASE)
        daya_match = re.search(r'Daya Tampung:\s*([^\n]+)', text, re.IGNORECASE)
        fasilitas_match = re.search(r'Fasilitas Pendukung\s*\(([^)]+)', text, re.IGNORECASE)
        keterangan_match = re.search(r'Keterangan Tambahan:\s*([^\n]+)', text, re.IGNORECASE)
        
        if nama_match:
            fields['Nama Fasilitas'] = f": {nama_match.group(1).strip()}"
        if jenis_match:
            fields['Jenis'] = f": {jenis_match.group(1).strip()}"
        if daya_match:
            fields['Daya Tampung'] = f": {daya_match.group(1).strip()}"
        if fasilitas_match:
            fields['Fasilitas'] = f": {fasilitas_match.group(1).strip()}"
        if keterangan_match:
            fields['Keterangan'] = f": {keterangan_match.group(1).strip()}"
    
    return create_universal_html(fields, "poi")

def process_generic_data(text):
    """Process any generic data with pipe separator"""
    parts = [part.strip() for part in text.split('|')]
    
    fields = {}
    
    if len(parts) == 1:
        field_name, field_value = extract_field_name_value(parts[0])
        fields = {field_name: field_value}
    else:
        # Skip the first part (title) for processing, but use it for expander title
        for i, part in enumerate(parts[1:], 1):
            field_name, field_value = extract_field_name_value(part)
            if field_value:
                fields[field_name] = field_value
    
    return create_universal_html(fields, "default")

def get_expander_title(text):
    """Get title for expander from the first part of the text - ambil text SETELAH colon"""
    parts = [part.strip() for part in text.split('|')]
    if parts:
        first_part = parts[0]
        # Extract text AFTER colon untuk judul
        if ':' in first_part:
            title = first_part.split(':', 1)[1].strip()  # Ambil bagian setelah colon
        else:
            title = first_part
        
        # Capitalize first letter
        title = title[0].upper() + title[1:] if title else "Entry"
        
        # Add appropriate emoji based on content
        if '*deskripsi jalan*' in text.lower() or 'nama jalan' in text.lower():
            return f"🛣️ {title}"
        elif 'nama po' in text.lower():
            return f"🏢 {title}"
        else:
            return f"📌 {title}"
    
    return "📌 Entry"

# Process button
if st.button("🚀 Process Data", type="primary"):
    if not input_data.strip():
        st.warning("Please paste some data first!")
    else:
        lines = input_data.strip().split('\n')
        results = []
        stats = {"roads": 0, "pois": 0, "other": 0}
        
        for line in lines:
            if not line.strip():
                continue
            
            line_lower = line.lower()
            
            if '*deskripsi jalan*' in line_lower or 'deskripsi jalan' in line_lower:
                html = process_road_data(line)
                expander_title = get_expander_title(line)
                results.append(("🛣️ ROAD", expander_title, html))
                stats["roads"] += 1
            elif 'nama po' in line_lower:
                html = process_poi_data(line)
                expander_title = get_expander_title(line)
                results.append(("🏢 POI", expander_title, html))
                stats["pois"] += 1
            else:
                html = process_generic_data(line)
                expander_title = get_expander_title(line)
                results.append(("📌 OTHER", expander_title, html))
                stats["other"] += 1

        # Display results
        st.success(f"✅ Processed {len(results)} entries (Roads: {stats['roads']}, POIs: {stats['pois']}, Other: {stats['other']})")
        
        st.markdown("""
        <style>
        .page-break {
            page-break-after: always;
            break-after: page;
        }
        </style>
        """, unsafe_allow_html=True)
        
        for i, (entry_type, expander_title, result) in enumerate(results, 1):
            with st.expander(f"{expander_title} - Entry {i}"):
                st.components.v1.html(result, height=400)
                st.code(result, language='html')
                
                if i < len(results):
                    st.markdown('<div class="page-break"></div>', unsafe_allow_html=True)