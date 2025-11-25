import streamlit as st
import re

st.set_page_config(page_title="uMap HTML Generator", page_icon="🗺️", layout="wide")

st.title("🗺️ uMap HTML Generator")
st.subheader("Transform your road & POI data into beautiful uMap descriptions")

# Instructions
with st.expander("📋 How to use"):
    st.markdown("""
    1. **Paste your raw data** in the text area below
    2. **Click 'Process Data'** 
    3. **Copy the HTML output** for each entry
    4. **Paste into uMap** description fields
    
    **Supported formats:**
    - 🛣️ **Road descriptions** (starts with '*Deskripsi jalan*')
    - 🏢 **POI/Facilities** (starts with 'Nama PO')
    - 🏫 **Schools & Facilities** (HTML format)
    - 🔄 **Other entries** (processed with universal styling)
    
    **Separators supported:**
    - Pipe `|` (recommended for structured data)
    - Natural text format
    - Mixed formats
    """)

# Input area
input_data = st.text_area(
    "Paste your entire list here (pipe | separator supported):",
    height=300,
    placeholder="Paste your data here...\n\nExamples with pipe separator:\n\n*Deskripsi jalan* | 1. nama jalan (jalur contoh) | 2. Jenis jalan (jalan aspal) | 3. Lebar Jalan (5m)...\nNama PO: Contoh Facility | Desa: Contoh | Banjar: Contoh | Daya Tampung: 100\n\nOr natural text:\n*Deskripsi jalan* 1. nama jalan (jalur contoh) 2. Jenis jalan (jalan aspal)..."
)

# Universal styling function dengan format yang Anda inginkan
def create_universal_html(fields, style_type="default"):
    """
    Create HTML dengan format seperti yang diinginkan
    
    Parameters:
    - fields: Dictionary of field_name: field_value pairs
    - style_type: "road", "poi", or "default"
    """
    
    # Define styles based on type
    styles = {
        "road": {
            "background": "#e8f4fd",
            "border": "2px solid #b8daff",
        },
        "poi": {
            "background": "#e8f4fd", 
            "border": "2px solid #b8daff",
        },
        "default": {
            "background": "#e8f4fd",
            "border": "2px solid #b8daff",
        }
    }
    
    style = styles.get(style_type, styles["default"])
    
    # Build fields HTML dengan format yang diinginkan
    fields_html = ""
    for field_name, field_value in fields.items():
        if field_value and field_value.strip():  # Only add if value exists
            fields_html += f'''
  <div style="display: flex; align-items: start; margin-bottom: 8px;">
  <div style="min-width: 160px; font-weight: bold; color: #2c3e50;">{field_name}</div>
  <div style="flex: 1;">: {field_value}</div>
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

def extract_fields_from_pipe(text):
    """Extract fields from pipe-separated text"""
    fields = {}
    parts = [part.strip() for part in text.split('|') if part.strip()]
    
    for part in parts:
        # Coba extract field: value pattern
        if ':' in part:
            field_parts = part.split(':', 1)
            field_name = field_parts[0].strip()
            field_value = field_parts[1].strip()
            fields[field_name] = standardize_indonesian(field_value)
        else:
            # Handle numbered format: 1. nama jalan (value)
            numbered_match = re.match(r'(\d+)\.\s*(.+?)\s*\(([^)]+)\)', part)
            if numbered_match:
                number = numbered_match.group(1)
                field_type = numbered_match.group(2).strip()
                value = numbered_match.group(3).strip()
                
                # Map numbers to field names
                field_map = {
                    '1': 'Nama Jalan',
                    '2': 'Jenis Jalan', 
                    '3': 'Lebar Jalan',
                    '4': 'Karakter Jalan',
                    '5': 'Kondisi Jalan',
                    '6': 'Keterangan Tambahan'
                }
                
                field_name = field_map.get(number, field_type)
                fields[field_name] = standardize_indonesian(value)
            else:
                # Simple text - use as information
                if 'Informasi' not in fields:
                    fields['Informasi'] = standardize_indonesian(part)
                else:
                    fields['Informasi'] += f", {standardize_indonesian(part)}"
    
    return fields

def process_road_data(text):
    """Process road data dengan support untuk pipe separator"""
    # Cek jika menggunakan pipe separator
    if '|' in text:
        fields = extract_fields_from_pipe(text)
    else:
        # Gunakan regex parsing untuk natural text
        fields = {}
        
        # Pattern untuk format: 1. nama jalan (value) 2. Jenis jalan (value) ...
        patterns = {
            'Nama Jalan': r'1\.\s*nama jalan\s*\(\s*(jalur[^)]+)',
            'Jenis Jalan': r'2\.\s*Jenis jalan\s*\(\s*([^)]+)',
            'Lebar Jalan': r'3\.\s*Lebar Jalan\s*\(\s*([^)]+)', 
            'Karakter Jalan': r'4\.\s*karakter jalan\s*\(\s*([^)]+)',
            'Kondisi Jalan': r'5\.\s*Kondisi Jalan\s*\(\s*([^)]+)',
            'Keterangan Tambahan': r'6\.\s*Keterangan Tambahan\s*:\s*([^<]*)'
        }
        
        for field_name, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                # Clean up value - remove "jalur" prefix if present
                if field_name == 'Nama Jalan' and value.startswith('jalur'):
                    value = value.replace('jalur', '').strip()
                value = standardize_indonesian(value)
                fields[field_name] = value
    
    # Clean up fields - remove empty ones
    fields = {k: v for k, v in fields.items() if v and v.strip()}
    
    return create_universal_html(fields, "road")

def process_poi_data(text):
    """Process POI data dengan support untuk pipe separator"""
    # Cek jika menggunakan pipe separator
    if '|' in text:
        fields = extract_fields_from_pipe(text)
    else:
        # Gunakan regex parsing untuk natural text
        fields = {}
        
        # Pattern untuk format: Field: value
        patterns = {
            'Nama PO': r'Nama PO:?\s*([^\n|]+)',
            'Desa': r'Desa:?\s*([^\n|]+)',
            'Banjar': r'Banjar:?\s*([^\n|]+)',
            'Jenis Fasum': r'Jenis Fasum:?\s*\(?\s*([^)|]+)',
            'Daya Tampung': r'Daya Tampung:?\s*([^\n|]+)',
            'Fasilitas Pendukung': r'Fasilitas Pendukung\s*\(?\s*([^)|]+)',
            'Kontak person': r'Kontak person:?\s*([^\n|]+)',
            'Jenis Bangunan': r'Jenis Bangunan:?\s*([^\n|]+)',
            'Luas Area Terbuka': r'Luas Area Terbuka:?\s*([^\n|]+)',
            'Keterangan Tambahan': r'Keterangan Tambahan:?\s*([^\n|]+)'
        }
        
        for field_name, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                value = standardize_indonesian(value)
                fields[field_name] = value
    
    # Clean up fields
    fields = {k: v for k, v in fields.items() if v and v.strip()}
    
    return create_universal_html(fields, "poi")

def standardize_indonesian(text):
    """Standardize Indonesian language in the text"""
    replacements = {
        r'\bbisa di lalu\b': 'Dapat dilalui',
        r'\bdi lalu\b': 'dilalui',
        r'\bdi pakai\b': 'dipakai',
        r'\bdi jadikan\b': 'dijadikan',
        r'\bdi rencanakan\b': 'direncanakan',
        r'\bdi pake\b': 'dipakai',
        r'\bhelp\b': 'helip',
        r'\b(\d)\s*m\b': r'\1 m',  # Standardize meter format
        r'\b(\d)\s*are\b': r'\1 are',  # Standardize are format
        r'\+\-\s*': '±',  # Standardize plus-minus
        r'^\s*jalur\s*': '',  # Remove leading "jalur"
    }
    
    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text.strip()

def process_html_data(text):
    """Process data yang sudah dalam format HTML - return as is"""
    return text.strip()

def process_generic_data(text):
    """Process any generic data dengan support untuk pipe separator"""
    # Cek jika menggunakan pipe separator
    if '|' in text:
        fields = extract_fields_from_pipe(text)
    else:
        # Gunakan metode sebelumnya untuk natural text
        fields = {}
        
        # Coba extract fields dengan pattern field: value
        parts = re.split(r'[|:]', text)
        
        if len(parts) > 1:
            current_field = "Informasi"
            for i, part in enumerate(parts):
                if i == 0:
                    current_field = part.strip()
                else:
                    if part.strip():
                        fields[current_field] = part.strip()
                        current_field = "Informasi"
        else:
            fields['Keterangan'] = text.strip()
    
    # Clean and standardize
    cleaned_fields = {}
    for field_name, field_value in fields.items():
        if field_value and field_value.strip():
            cleaned_value = standardize_indonesian(field_value)
            cleaned_fields[field_name] = cleaned_value
    
    return create_universal_html(cleaned_fields, "default")

# Process button
if st.button("🚀 Process Data", type="primary"):
    if not input_data.strip():
        st.warning("Please paste some data first!")
    else:
        # Process data
        lines = input_data.strip().split('\n')
        results = []
        stats = {"roads": 0, "pois": 0, "html": 0, "other": 0}
        
        for line in lines:
            if not line.strip():
                continue
            
            line_lower = line.lower()
            
            # Check if it's already HTML
            if line.strip().startswith('<div'):
                html = process_html_data(line)
                results.append(("🏛️ HTML", html))
                stats["html"] += 1
            elif '*deskripsi jalan*' in line_lower:
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
        st.success(f"✅ Processed {len(results)} entries (Roads: {stats['roads']}, POIs: {stats['pois']}, HTML: {stats['html']}, Other: {stats['other']})")
        
        # Tampilkan hasil
        for i, (entry_type, result) in enumerate(results, 1):
            with st.expander(f"{entry_type} - Entry {i}"):
                st.components.v1.html(result, height=400, scrolling=True)
                st.code(result, language='html')

# Example data dengan pipe separator
with st.expander("📝 Example Input Format with Pipe Separator"):
    st.markdown("""
    **Road Data with Pipe Separator:**
    ```
    *Deskripsi jalan* | 1. nama jalan (Jalur Ababi-Tiing Tali) | 2. Jenis jalan (Jalan Kabupaten) | 3. Lebar Jalan (4m) | 4. karakter jalan (Aspal Hotmix) | 5. Kondisi Jalan (Dapat dilalui sepeda motor, roda 4 dan truk) | 6. Keterangan Tambahan: Pertigaan jalan nasional-kabupaten, Ababi menuju Tiing Tali
    ```
    
    **POI Data with Pipe Separator:**
    ```
    Nama PO: Tempat penyadnyan Br. dinas Kelakah | Desa: Pidpid | Banjar: Br. Dinas kelakah | Jenis Fasum: Lapangan | Daya Tampung: ±600 | Fasilitas Pendukung: Listrik, sumber air, toilet | Kontak person: 082341652819 | Jenis Bangunan: Permanen | Luas Area Terbuka: 20 are | Keterangan Tambahan: Direncanakan dipakai sebagai titik kumpul
    ```
    
    **Simple Key-Value with Pipe:**
    ```
    Nama Fasilitas: SDN 2 Tiying Tali | Desa: Tiying Tali | Banjar: Banjar dinas Tiyingtali kaler | Jenis: Gedung sekolah | Daya Tampung: ±400 | Fasilitas: listrik, sumber air, toilet | Bangunan: permanen | Luas Area: 15 are | Keterangan: Direncanakan sebagai tempat pengungsian
    ```
    
    **Mixed Format (also supported):**
    ```
    *Deskripsi jalan* 1. nama jalan (jalur contoh) 2. Jenis jalan (jalan aspal) 3. Lebar Jalan (5m)...
    ```
    """)
