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
    # Clean the fields
    nama = fields.get('nama', 'Fasilitas').strip()
    desa = fields.get('desa', '').strip()
    banjar = fields.get('banjar', '').strip()
    jenis_fasum = fields.get('jenis_fasum', '').strip()
    daya_tampung = fields.get('daya_tampung', '').strip()
    fasilitas = fields.get('fasilitas', '').strip()
    kontak_person = fields.get('kontak_person', '').strip()
    jenis_bangunan = fields.get('jenis_bangunan', '').strip()
    luas_area = fields.get('luas_area', '').strip()
    keterangan = fields.get('keterangan', '').strip()

    html_template = f'''
<div style="font-family: Arial, sans-serif; background: #e8f4fd; border: 2px solid #b8daff; border-radius: 8px; padding: 15px; margin: 10px 0;">
<h3 style="margin: 0 0 15px 0; color: #2c3e50; text-align: center;">🏢 {nama}</h3>
<table style="width: 100%; border-collapse: collapse;">
<tr><td style="padding: 8px; border-bottom: 1px solid #dee2e6; font-weight: bold; width: 35%;">Nama Fasilitas</td><td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{nama}</td></tr>
<tr><td style="padding: 8px; border-bottom: 1px solid #dee2e6; font-weight: bold;">Lokasi</td><td style="padding: 8px; border-bottom: 1px solid #dee2e6;">Desa {desa}, Banjar {banjar}</td></tr>
<tr><td style="padding: 8px; border-bottom: 1px solid #dee2e6; font-weight: bold;">Jenis Fasilitas</td><td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{jenis_fasum}</td></tr>
<tr><td style="padding: 8px; border-bottom: 1px solid #dee2e6; font-weight: bold;">Daya Tampung</td><td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{daya_tampung}</td></tr>
<tr><td style="padding: 8px; border-bottom: 1px solid #dee2e6; font-weight: bold;">Fasilitas Pendukung</td><td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{fasilitas}</td></tr>
<tr><td style="padding: 8px; border-bottom: 1px solid #dee2e6; font-weight: bold;">Kontak Person</td><td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{kontak_person}</td></tr>
<tr><td style="padding: 8px; border-bottom: 1px solid #dee2e6; font-weight: bold;">Jenis Bangunan</td><td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{jenis_bangunan}</td></tr>
<tr><td style="padding: 8px; border-bottom: 1px solid #dee2e6; font-weight: bold;">Luas Area Terbuka</td><td style="padding: 8px; border-bottom: 1px solid #dee2e6;">{luas_area}</td></tr>
<tr><td style="padding: 8px; font-weight: bold; background: #fff3cd;">Keterangan</td><td style="padding: 8px; background: #fff3cd;">{keterangan}</td></tr>
</table>
</div>
'''
    return html_template.strip()

def parse_comma_separated_poi(text):
    """Parse comma-separated POI data with better field extraction"""
    fields = {}
    
    # Clean the text first
    text = text.strip()
    
    # Extract Nama POI first (handle both "Nama POI :" and "Nama PO:")
    nama_match = re.search(r'Nama POI?\s*:?\s*([^,]+)', text, re.IGNORECASE)
    if nama_match:
        fields['nama'] = nama_match.group(1).strip()
    
    # Define patterns for each field with better regex
    patterns = {
        'desa': r'Desa:\s*([^,]+)',
        'banjar': r'Banjar:\s*([^,]+)',
        'jenis_fasum': r'Jenis Fasum:\s*\(([^)]+)\)',
        'daya_tampung': r'Daya Tampung:\s*([^,]+)',
        'fasilitas': r'Fasilitas Pendukung\s*\(([^)]+)\)',
        'kontak_person': r'Kontak person:\s*([^,]+)',
        'jenis_bangunan': r'Jenis Bangunan:\s*([^,]+)',
        'luas_area': r'Luas Area Terbuka:\s*([^,]+)',
        'keterangan': r'Keterangan Tambahan:\s*([^,]+)'
    }
    
    for field, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            fields[field] = match.group(1).strip()
        else:
            fields[field] = ""
    
    return fields

def process_poi_data(text):
    """Process POI data"""
    fields = parse_comma_separated_poi(text)
    
    # Create structured text with proper formatting
    structured_text = f"""Nama Fasilitas: {fields.get('nama', '')}
Desa: {fields.get('desa', '')}
Banjar: {fields.get('banjar', '')}
Jenis Fasum: {fields.get('jenis_fasum', '')}
Daya Tampung: {fields.get('daya_tampung', '')}
Fasilitas Pendukung: {fields.get('fasilitas', '')}
Kontak Person: {fields.get('kontak_person', '')}
Jenis Bangunan: {fields.get('jenis_bangunan', '')}
Luas Area Terbuka: {fields.get('luas_area', '')}
Keterangan Tambahan: {fields.get('keterangan', '')}"""
    
    # Create HTML
    html_code = create_poi_html(fields)
    
    return structured_text, html_code, fields

if st.button("🚀 Process Comma-Separated Data", type="primary"):
    if not input_data.strip():
        st.warning("Please paste some data first!")
    else:
        lines = input_data.strip().split('\n')
        results = []
        
        for line in lines:
            if not line.strip():
                continue
                
            if 'Nama PO' in line:
                # POI entry
                try:
                    structured, html, fields = process_poi_data(line)
                    results.append(("🏢 POI", line, structured, html, fields))
                except Exception as e:
                    st.error(f"Error processing line: {line}")
                    st.error(f"Error details: {str(e)}")
        
        # Display results
        if results:
            st.success(f"✅ Processed {len(results)} POI entries")
            
            # Show results
            for i, (entry_type, original, structured, html, fields) in enumerate(results, 1):
                with st.expander(f"{entry_type} - Entry {i}: {fields.get('nama', 'Unknown')}"):
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.text("Original Data:")
                        st.code(original, language='text')
                        
                        st.text("Structured Data:")
                        st.code(structured, language='text')
                        
                        st.text("Extracted Fields:")
                        for key, value in fields.items():
                            if value:
                                st.text(f"• {key}: {value}")
                    
                    with col2:
                        if html:
                            st.text("HTML Table Preview:")
                            st.components.v1.html(html, height=450)
                            
                            st.text("HTML Code (Copy this for uMap):")
                            st.code(html, language='html')
                            
                            # Copy button
                            if st.button(f"📋 Copy HTML to Clipboard", key=f"copy_{i}"):
                                st.code(html, language='html')
                                st.success("✅ HTML copied! Paste this into uMap description field.")

            # Download all HTML
            st.markdown("### 💾 Download All HTML Tables")
            all_html = "\n\n".join([f"<!-- {fields.get('nama', 'POI')} -->\n{h}" for t, o, s, h, fields in results if h])
            st.download_button(
                label="📥 Download All HTML Tables",
                data=all_html,
                file_name="umap_tables.html",
                mime="text/html"
            )
        else:
            st.warning("No POI entries found in the input data.")

# Instructions
with st.expander("📋 How to use this tool"):
    st.markdown("""
    1. **Paste your comma-separated POI data** in the text area above
    2. **Click 'Process Comma-Separated Data'**
    3. **Check the HTML Preview** to see how it will look in uMap
    4. **Copy the HTML Code** using the copy button
    5. **Paste into uMap** in the description field of your point

    **Expected Input Format:**
    ```
    Nama POI : SDN 1 Tiyingtali, Desa: Tiing tali, Banjar: Banjar dinas Tiyingtali kelod, Jenis Fasum: (Gedung sekolah), Daya Tampung: +-600, Fasilitas Pendukung (listrik,sumber air, toilet), Kontak person:, Jenis Bangunan: permanen, Luas Area Terbuka: 25 are, Keterangan Tambahan: di rencanakan sebagai tempat pengungsian
    ```
    """)

st.markdown("---")
st.markdown("**✨ Tip:** The HTML tables work perfectly in uMap when pasted into the description field!")