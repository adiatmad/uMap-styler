import streamlit as st
import re

st.set_page_config(page_title="uMap HTML Generator", page_icon="🗺️", layout="wide")

st.title("🗺️ uMap HTML Generator")
st.subheader("Transform your data into uMap-ready HTML")

# Input area
input_data = st.text_area(
    "Paste your data here:",
    height=300,
    placeholder="Paste your POI data here...\n\nExample:\nNama POI : SDN 1 Tiyingtali, Desa: Tiing tali, Jenis Fasum: (Gedung sekolah), Daya Tampung: +-600..."
)

def create_simple_poi_html(fields):
    """Create simple, clean HTML for POI entries"""
    # Ensure all fields have values
    nama = fields.get('nama', 'Fasilitas').strip()
    desa = fields.get('desa', '').strip()
    banjar = fields.get('banjar', '').strip()
    jenis = fields.get('jenis_fasum', '').strip()
    daya = fields.get('daya_tampung', '').strip()
    fasilitas = fields.get('fasilitas', '').strip()
    kontak = fields.get('kontak_person', '').strip()
    bangunan = fields.get('jenis_bangunan', '').strip()
    luas = fields.get('luas_area', '').strip()
    keterangan = fields.get('keterangan', '').strip()

    html = f'''
<div style="font-family: Arial, sans-serif; background: #f8f9fa; border: 2px solid #dee2e6; border-radius: 8px; padding: 15px;">
<h3 style="margin: 0 0 15px 0; color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">🏢 {nama}</h3>
<div style="line-height: 1.6;">
'''
    
    # Add fields only if they have values
    if desa:
        html += f'<div><strong>Desa:</strong> {desa}</div>'
    if banjar:
        html += f'<div><strong>Banjar:</strong> {banjar}</div>'
    if jenis:
        html += f'<div><strong>Jenis Fasilitas:</strong> {jenis}</div>'
    if daya:
        html += f'<div><strong>Daya Tampung:</strong> {daya}</div>'
    if fasilitas:
        html += f'<div><strong>Fasilitas:</strong> {fasilitas}</div>'
    if kontak:
        html += f'<div><strong>Kontak Person:</strong> {kontak}</div>'
    if bangunan:
        html += f'<div><strong>Jenis Bangunan:</strong> {bangunan}</div>'
    if luas:
        html += f'<div><strong>Luas Area:</strong> {luas}</div>'
    if keterangan:
        html += f'<div style="margin-top: 10px; padding: 10px; background: #e8f4fd; border-radius: 5px;"><strong>Keterangan:</strong> {keterangan}</div>'
    
    html += '''
</div>
</div>
'''
    return html.strip()

def manual_parse_poi(text):
    """Manual parsing for POI data - more reliable"""
    fields = {}
    
    # Simple manual extraction
    parts = text.split(',')
    
    for part in parts:
        part = part.strip()
        
        # Nama POI
        if 'Nama PO' in part:
            if ':' in part:
                fields['nama'] = part.split(':', 1)[1].strip()
            else:
                fields['nama'] = part.replace('Nama POI', '').replace('Nama PO', '').strip()
        
        # Desa
        elif 'Desa:' in part:
            fields['desa'] = part.split(':', 1)[1].strip()
        
        # Banjar
        elif 'Banjar:' in part:
            fields['banjar'] = part.split(':', 1)[1].strip()
        
        # Jenis Fasum
        elif 'Jenis Fasum:' in part:
            value = part.split(':', 1)[1].strip()
            # Remove parentheses if present
            if value.startswith('(') and value.endswith(')'):
                value = value[1:-1]
            fields['jenis_fasum'] = value
        
        # Daya Tampung
        elif 'Daya Tampung:' in part:
            fields['daya_tampung'] = part.split(':', 1)[1].strip()
        
        # Fasilitas Pendukung
        elif 'Fasilitas Pendukung' in part:
            if '(' in part and ')' in part:
                start = part.find('(') + 1
                end = part.find(')')
                fields['fasilitas'] = part[start:end].strip()
        
        # Kontak person
        elif 'Kontak person:' in part:
            fields['kontak_person'] = part.split(':', 1)[1].strip()
        
        # Jenis Bangunan
        elif 'Jenis Bangunan:' in part:
            fields['jenis_bangunan'] = part.split(':', 1)[1].strip()
        
        # Luas Area Terbuka
        elif 'Luas Area Terbuka:' in part:
            fields['luas_area'] = part.split(':', 1)[1].strip()
        
        # Keterangan Tambahan
        elif 'Keterangan Tambahan:' in part:
            fields['keterangan'] = part.split(':', 1)[1].strip()
    
    return fields

if st.button("🚀 Generate uMap HTML", type="primary"):
    if not input_data.strip():
        st.warning("Please paste some data first!")
    else:
        lines = [line.strip() for line in input_data.split('\n') if line.strip()]
        
        for i, line in enumerate(lines, 1):
            if 'Nama PO' in line:
                with st.expander(f"POI {i}", expanded=True):
                    st.text("Input Data:")
                    st.code(line, language='text')
                    
                    # Parse the data
                    fields = manual_parse_poi(line)
                    
                    st.text("Parsed Fields:")
                    for key, value in fields.items():
                        if value:
                            st.text(f"• {key}: {value}")
                    
                    # Generate HTML
                    html = create_simple_poi_html(fields)
                    
                    st.text("HTML Preview:")
                    st.components.v1.html(html, height=400)
                    
                    st.text("HTML Code (Copy this for uMap):")
                    st.code(html, language='html')
                    
                    # Copy button
                    if st.button(f"📋 Copy HTML", key=f"copy_{i}"):
                        st.success("✅ HTML copied! Paste this into uMap description field.")

# Instructions
st.markdown("---")
st.markdown("""
### 📋 Cara Penggunaan:

1. **Paste data POI** Anda di text area atas
2. **Klik tombol "Generate uMap HTML"**
3. **Copy HTML code** yang dihasilkan
4. **Paste di uMap** pada field "description"

### 📝 Format Input yang Didukung: