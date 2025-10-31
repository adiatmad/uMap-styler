import streamlit as st
import re

st.set_page_config(page_title="uMap HTML Generator", page_icon="🗺️", layout="wide")

st.title("🗺️ uMap HTML Generator")
st.subheader("Transform comma-separated data into beautiful uMap tables")

# Input area
input_data = st.text_area(
    "Paste your comma-separated data here:",
    height=400,
    placeholder="Paste your data here...\n\nExample:\nNama POI : SDN 1 Tiyingtali, Desa: Tiing tali, Jenis Fasum: (Gedung sekolah), Daya Tampung: +-600..."
)

def create_poi_html(fields):
    """Create HTML for POI entries with table layout"""
    html_template = f'''
<div style="font-family: Arial, sans-serif; background: #e8f4fd; border: 2px solid #b8daff; border-radius: 8px; padding: 15px; margin: 10px 0;">
<h3 style="margin: 0 0 15px 0; color: #2c3e50; text-align: center;">🏢 {fields.get("nama", "Fasilitas")}</h3>
<table style="width: 100%; border-collapse: collapse;">
<tr><td style="padding: 8px; border-bottom: 1px solid #dee2e6; font-weight: bold; width: 30%;">Nama Fasilitas</td><td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{fields.get('nama', '')}</td></tr>
<tr><td style="padding: 8px; border-bottom: 1px solid #dee2e6; font-weight: bold;">Lokasi</td><td style="padding: 8px; border-bottom: 1px solid #dee2e6;">Desa {fields.get('desa', '')}, Banjar {fields.get('banjar', '')}</td></tr>
<tr><td style="padding: 8px; border-bottom: 1px solid #dee2e6; font-weight: bold;">Jenis Fasilitas</td><td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{fields.get('jenis_fasum', '')}</td></tr>
<tr><td style="padding: 8px; border-bottom: 1px solid #dee2e6; font-weight: bold;">Daya Tampung</td><td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{fields.get('daya_tampung', '')}</td></tr>
<tr><td style="padding: 8px; border-bottom: 1px solid #dee2e6; font-weight: bold;">Fasilitas</td><td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{fields.get('fasilitas', '')}</td></tr>
<tr><td style="padding: 8px; border-bottom: 1px solid #dee2e6; font-weight: bold;">Kontak Person</td><td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{fields.get('kontak_person', '')}</td></tr>
<tr><td style="padding: 8px; border-bottom: 1px solid #dee2e6; font-weight: bold;">Jenis Bangunan</td><td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{fields.get('jenis_bangunan', '')}</td></tr>
<tr><td style="padding: 8px; border-bottom: 1px solid #dee2e6; font-weight: bold;">Luas Area</td><td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{fields.get('luas_area', '')}</td></tr>
<tr><td style="padding: 8px; font-weight: bold; background: #fff3cd;">Keterangan</td><td style="padding: 8px; background: #fff3cd;">{fields.get('keterangan', '')}</td></tr>
</table>
</div>
'''
    return html_template.strip()

def create_road_html(fields):
    """Create HTML for road entries with table layout"""
    html_template = f'''
<div style="font-family: Arial, sans-serif; background: #fff3cd; border: 2px solid #ffeaa7; border-radius: 8px; padding: 15px; margin: 10px 0;">
<h3 style="margin: 0 0 15px 0; color: #2c3e50; text-align: center;">🛣️ Jalan Evakuasi</h3>
<table style="width: 100%; border-collapse: collapse;">
<tr><td style="padding: 8px; border-bottom: 1px solid #dee2e6; font-weight: bold; width: 30%;">Nama Jalan</td><td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{fields.get('nama_jalan', '')}</td></tr>
<tr><td style="padding: 8px; border-bottom: 1px solid #dee2e6; font-weight: bold;">Jenis Jalan</td><td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{fields.get('jenis_jalan', '')}</td></tr>
<tr><td style="padding: 8px; border-bottom: 1px solid #dee2e6; font-weight: bold;">Lebar Jalan</td><td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{fields.get('lebar_jalan', '')}</td></tr>
<tr><td style="padding: 8px; border-bottom: 1px solid #dee2e6; font-weight: bold;">Karakter Jalan</td><td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{fields.get('karakter_jalan', '')}</td></tr>
<tr><td style="padding: 8px; border-bottom: 1px solid #dee2e6; font-weight: bold;">Kondisi Jalan</td><td style="padding: 8px; border-bottom: 1px solid #dee2e6;">✅ {fields.get('kondisi_jalan', '')}</td></tr>
<tr><td style="padding: 8px; font-weight: bold; background: #d4edda;">Keterangan</td><td style="padding: 8px; background: #d4edda;">{fields.get('keterangan', '')}</td></tr>
</table>
</div>
'''
    return html_template.strip()

def parse_comma_separated_poi(text):
    """Parse comma-separated POI data"""
    # Split by commas but be careful with commas inside parentheses
    segments = []
    current_segment = ""
    paren_count = 0
    
    for char in text:
        if char == '(':
            paren_count += 1
        elif char == ')':
            paren_count -= 1
        
        if char == ',' and paren_count == 0:
            segments.append(current_segment.strip())
            current_segment = ""
        else:
            current_segment += char
    
    if current_segment:
        segments.append(current_segment.strip())
    
    fields = {}
    
    for segment in segments:
        # Extract field name and value
        if ':' in segment:
            field_parts = segment.split(':', 1)
            field_name = field_parts[0].strip().lower()
            field_value = field_parts[1].strip()
            
            # Map field names to standardized keys
            field_mapping = {
                'nama poi': 'nama',
                'nama po': 'nama',
                'desa': 'desa',
                'banjar': 'banjar',
                'jenis fasum': 'jenis_fasum',
                'daya tampung': 'daya_tampung',
                'fasilitas pendukung': 'fasilitas',
                'kontak person': 'kontak_person',
                'jenis bangunan': 'jenis_bangunan',
                'luas area terbuka': 'luas_area',
                'keterangan tambahan': 'keterangan'
            }
            
            for key, value in field_mapping.items():
                if field_name.startswith(key):
                    # Remove parentheses from jenis_fasum if present
                    if value == 'jenis_fasum' and field_value.startswith('(') and field_value.endswith(')'):
                        field_value = field_value[1:-1]
                    fields[value] = field_value
                    break
            else:
                # If no mapping found, use the original field name
                fields[field_name] = field_value
    
    return fields

def parse_comma_separated_road(text):
    """Parse comma-separated road data"""
    # For road data, we need to handle the numbered format
    fields = {}
    
    # Extract nama jalan
    nama_match = re.search(r'nama jalan\s*\(\s*(jalur[^)]+)', text, re.IGNORECASE)
    if nama_match:
        fields['nama_jalan'] = nama_match.group(1).strip()
    
    # Extract other fields
    patterns = {
        'jenis_jalan': r'Jenis jalan\s*\(\s*([^)]+)',
        'lebar_jalan': r'Lebar Jalan\s*\(\s*([^)]+)',
        'karakter_jalan': r'karakter jalan\s*\(\s*([^)]+)',
        'kondisi_jalan': r'Kondisi Jalan\s*\(\s*([^)]+)',
        'keterangan': r'Keterangan Tambahan\s*:([^,]*)'
    }
    
    for field, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            fields[field] = match.group(1).strip()
    
    return fields

def process_poi_data(text):
    """Process POI data"""
    fields = parse_comma_separated_poi(text)
    
    # Create structured text
    structured_text = f"""Nama Fasilitas: {fields.get('nama', '')}
Desa: {fields.get('desa', '')}
Banjar: {fields.get('banjar', '')}
Jenis Fasilitas: {fields.get('jenis_fasum', '')}
Daya Tampung: {fields.get('daya_tampung', '')}
Fasilitas: {fields.get('fasilitas', '')}
Kontak Person: {fields.get('kontak_person', '')}
Jenis Bangunan: {fields.get('jenis_bangunan', '')}
Luas Area: {fields.get('luas_area', '')}
Keterangan: {fields.get('keterangan', '')}"""
    
    # Create HTML
    html_code = create_poi_html(fields)
    
    return structured_text, html_code, fields

def process_road_data(text):
    """Process road data"""
    fields = parse_comma_separated_road(text)
    
    # Create structured text
    structured_text = f"""Nama Jalan: {fields.get('nama_jalan', '')}
Jenis Jalan: {fields.get('jenis_jalan', '')}
Lebar Jalan: {fields.get('lebar_jalan', '')}
Karakter Jalan: {fields.get('karakter_jalan', '')}
Kondisi Jalan: {fields.get('kondisi_jalan', '')}
Keterangan: {fields.get('keterangan', '')}"""
    
    # Create HTML
    html_code = create_road_html(fields)
    
    return structured_text, html_code, fields

if st.button("🚀 Process Comma-Separated Data", type="primary"):
    if not input_data.strip():
        st.warning("Please paste some data first!")
    else:
        lines = input_data.strip().split('\n')
        results = []
        stats = {"pois": 0, "roads": 0, "simple": 0}
        
        for line in lines:
            if not line.strip():
                continue
                
            if 'Nama PO' in line:
                # POI entry
                try:
                    structured, html, fields = process_poi_data(line)
                    results.append(("🏢 POI", line, structured, html, fields))
                    stats["pois"] += 1
                except Exception as e:
                    results.append(("❌ ERROR", line, f"Error processing: {str(e)}", "", {}))
                    stats["simple"] += 1
                    
            elif '*Deskripsi jalan*' in line:
                # Road entry
                try:
                    structured, html, fields = process_road_data(line)
                    results.append(("🛣️ ROAD", line, structured, html, fields))
                    stats["roads"] += 1
                except Exception as e:
                    results.append(("❌ ERROR", line, f"Error processing: {str(e)}", "", {}))
                    stats["simple"] += 1
            else:
                # Other entries
                results.append(("📌 OTHER", line, line, "", {}))
                stats["simple"] += 1
        
        # Display results
        st.success(f"✅ Processed {len(results)} entries: {stats['pois']} POIs, {stats['roads']} Roads, {stats['simple']} Others")
        
        # Show results
        for i, (entry_type, original, structured, html, fields) in enumerate(results, 1):
            with st.expander(f"{entry_type} - Entry {i}"):
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.text("Original Data:")
                    st.code(original, language='text')
                    
                    st.text("Parsed Fields:")
                    for key, value in fields.items():
                        if value:  # Only show non-empty fields
                            st.text(f"• {key}: {value}")
                
                with col2:
                    if html:
                        st.text("HTML Table Preview:")
                        st.components.v1.html(html, height=400)
                        
                        st.text("HTML Code:")
                        st.code(html, language='html')
                        
                        # Copy button
                        if st.button(f"📋 Copy HTML", key=f"copy_{i}"):
                            st.code(html, language='html')
                            st.success("HTML copied to clipboard! (Use Ctrl+C to copy)")

        # Download all HTML
        st.markdown("### 💾 Download All HTML Tables")
        all_html = "\n\n".join([f"<!-- {t} -->\n{h}" for t, o, s, h, f in results if h])
        st.download_button(
            label="📥 Download All HTML Tables",
            data=all_html,
            file_name="umap_tables.html",
            mime="text/html"
        )

st.markdown("---")
st.markdown("""
**📝 Expected Input Format:**