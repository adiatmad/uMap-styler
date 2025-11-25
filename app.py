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
    """)

# Input area
input_data = st.text_area(
    "Paste your entire list here:",
    height=300,
    placeholder="Paste your data here...\n\nExamples:\n\n*Deskripsi jalan* 1. nama jalan (jalur contoh) 2. Jenis jalan (jalan aspal) 3. Lebar Jalan (5m)...\nNama PO: Contoh Facility | Desa: Contoh | Banjar: Contoh...\n<div style=\"...\">SDN 1 Contoh</div>"
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

def process_road_data(text):
    """Process road data dengan format baru"""
    # Extract data menggunakan regex untuk format yang lebih fleksibel
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
            # Standardize bahasa Indonesia
            value = standardize_indonesian(value)
            fields[field_name] = value
    
    # Jika tidak ada match dengan pola berangka, coba pattern alternatif
    if not fields:
        alt_patterns = {
            'Nama Jalan': r'nama jalan\s*\(\s*(jalur[^)]+)',
            'Jenis Jalan': r'Jenis jalan\s*\(\s*([^)]+)',
            'Lebar Jalan': r'Lebar Jalan\s*\(\s*([^)]+)',
            'Karakter Jalan': r'karakter jalan\s*\(\s*([^)]+)', 
            'Kondisi Jalan': r'Kondisi Jalan\s*\(\s*([^)]+)',
            'Keterangan Tambahan': r'Keterangan Tambahan\s*:\s*([^<]*)'
        }
        
        for field_name, pattern in alt_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                if field_name == 'Nama Jalan' and value.startswith('jalur'):
                    value = value.replace('jalur', '').strip()
                value = standardize_indonesian(value)
                fields[field_name] = value
    
    # Clean up fields - remove empty ones
    fields = {k: v for k, v in fields.items() if v and v.strip()}
    
    return create_universal_html(fields, "road")

def process_poi_data(text):
    """Process POI data dengan format baru"""
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
    }
    
    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text

def process_html_data(text):
    """Process data yang sudah dalam format HTML - return as is"""
    return text.strip()

def process_generic_data(text):
    """Process any generic data"""
    # Coba extract fields dengan pattern field: value
    fields = {}
    
    # Split by common separators
    parts = re.split(r'[|:]', text)
    
    if len(parts) > 1:
        current_field = "Informasi"
        for i, part in enumerate(parts):
            if i == 0:
                # Bagian pertama biasanya judul/field name
                current_field = part.strip()
            else:
                # Bagian selanjutnya adalah value
                if part.strip():
                    fields[current_field] = part.strip()
                    # Reset untuk field berikutnya
                    current_field = "Informasi"
    else:
        # Single part - treat as simple information
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

# Example data
with st.expander("📝 Example Input Format"):
    st.markdown("""
    **Road Data Format:**
    ```
    *Deskripsi jalan* 1. nama jalan ( jalur Ababi-tiing tali) 2. Jenis jalan (Jalan Kabupaten) 3. Lebar Jalan (4m) 4. karakter jalan ( aspal hotmix) 5. Kondisi Jalan ( bisa di lalu sepeda motor, roda 4 dan truk) 6. Keterangan Tambahan :pertigaan jalan nasinonal- Kabupaten,ababi menuju tiing tali
    ```
    
    **POI Data Format:**
    ```
    Nama PO: Tempat penyadnyan Br. dinas Kelakah Desa:pidpid Banjar:Br. Dinas kelakah Jenis Fasum: ( lapangan) Daya Tampung: +-600 Fasilitas Pendukung (Listrik, sumber air, toilet) Kontak person:082341652819 Jenis Bangunan:permanen Luas Area Terbuka: 20 are Keterangan Tambahan: di rencanakan di pakai sebagai titik kumpul
    ```
    
    **HTML Data (will be preserved as-is):**
    ```
    <div style="font-family: Arial, sans-serif; background: #f8f9fa; border: 2px solid #dee2e6; border-radius: 8px; padding: 15px;"> ... </div>
    ```
    """)
