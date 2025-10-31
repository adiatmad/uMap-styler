import streamlit as st
import re

st.set_page_config(page_title="Universal uMap Formatter", page_icon="🗺️", layout="wide")

st.title("🗺️ Universal uMap Formatter")
st.subheader("Convert any text data into beautiful uMap descriptions")

# Input area
input_data = st.text_area(
    "Paste your mixed data here:",
    height=400,
    placeholder="Paste any data here... POI, road descriptions, simple text, etc."
)

def create_universal_html(content, title="Information", style="default"):
    """Create HTML for any type of content with page breaks after commas and bold title"""
    
    # Add page breaks after commas
    content_with_breaks = content.replace(',', ',<br>')
    
    # Choose style based on content type
    if style == "poi":
        bg_color = "#e8f4fd"
        border_color = "#b8daff"
        icon = "🏢"
    elif style == "road":
        bg_color = "#fff3cd"
        border_color = "#ffeaa7"
        icon = "🛣️"
    else:
        bg_color = "#f8f9fa"
        border_color = "#dee2e6"
        icon = "📌"
    
    html_template = f'''
<div style="font-family: Arial, sans-serif; background: {bg_color}; border: 2px solid {border_color}; border-radius: 8px; padding: 15px; margin: 10px 0;">
<h3 style="margin: 0 0 15px 0; color: #2c3e50; border-bottom: 2px solid {border_color}; padding-bottom: 10px;"><strong>{icon} {title}</strong></h3>
<div style="line-height: 1.6; white-space: pre-line;">{content_with_breaks}</div>
</div>
'''
    return html_template.strip()

def detect_content_type(text):
    """Detect what type of content this is"""
    text_lower = text.lower()
    
    if 'nama po' in text_lower:
        return "poi"
    elif 'deskripsi jalan' in text_lower:
        return "road"
    elif any(keyword in text_lower for keyword in ['desa:', 'banjar:', 'daya tampung:', 'fasilitas']):
        return "poi"
    elif any(keyword in text_lower for keyword in ['nama jalan', 'jenis jalan', 'lebar jalan']):
        return "road"
    else:
        return "general"

def extract_poi_info(text):
    """Extract structured info from POI text"""
    fields = {}
    
    # Simple patterns for common fields
    patterns = {
        'nama': r'Nama POI?\s*:?\s*([^\n,]+)',
        'desa': r'Desa:\s*([^\n,]+)',
        'banjar': r'Banjar:\s*([^\n,]+)',
        'jenis_fasum': r'Jenis Fasum:\s*\(([^)]+)\)',
        'daya_tampung': r'Daya Tampung:\s*([^\n,]+)',
        'fasilitas': r'Fasilitas Pendukung\s*\(([^)]+)\)',
        'kontak_person': r'Kontak person:\s*([^\n,]+)',
        'jenis_bangunan': r'Jenis Bangunan:\s*([^\n,]+)',
        'luas_area': r'Luas Area Terbuka:\s*([^\n,]+)',
        'keterangan': r'Keterangan Tambahan:\s*([^\n]+)'
    }
    
    for field, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            fields[field] = match.group(1).strip()
    
    # If no structured data found, return original text
    if not fields:
        return text
    
    # Create formatted text
    formatted = ""
    if fields.get('nama'):
        formatted += f"Nama: {fields['nama']}\n"
    if fields.get('desa'):
        formatted += f"Desa: {fields['desa']}\n"
    if fields.get('banjar'):
        formatted += f"Banjar: {fields['banjar']}\n"
    if fields.get('jenis_fasum'):
        formatted += f"Jenis: {fields['jenis_fasum']}\n"
    if fields.get('daya_tampung'):
        formatted += f"Daya Tampung: {fields['daya_tampung']}\n"
    if fields.get('fasilitas'):
        formatted += f"Fasilitas: {fields['fasilitas']}\n"
    if fields.get('kontak_person'):
        formatted += f"Kontak: {fields['kontak_person']}\n"
    if fields.get('jenis_bangunan'):
        formatted += f"Bangunan: {fields['jenis_bangunan']}\n"
    if fields.get('luas_area'):
        formatted += f"Luas Area: {fields['luas_area']}\n"
    if fields.get('keterangan'):
        formatted += f"Keterangan: {fields['keterangan']}\n"
    
    return formatted.strip()

def extract_road_info(text):
    """Extract structured info from road descriptions"""
    fields = {}
    
    patterns = {
        'nama_jalan': r'nama jalan\s*\(\s*(jalur[^)]+)',
        'jenis_jalan': r'Jenis jalan\s*\(\s*([^)]+)',
        'lebar_jalan': r'Lebar Jalan\s*\(\s*([^)]+)',
        'karakter_jalan': r'karakter jalan\s*\(\s*([^)]+)',
        'kondisi_jalan': r'Kondisi Jalan\s*\(\s*([^)]+)',
        'keterangan': r'Keterangan Tambahan\s*:([^\n<]+)'
    }
    
    for field, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            fields[field] = match.group(1).strip()
    
    if not fields:
        return text
    
    formatted = ""
    if fields.get('nama_jalan'):
        formatted += f"Nama Jalan: {fields['nama_jalan']}\n"
    if fields.get('jenis_jalan'):
        formatted += f"Jenis: {fields['jenis_jalan']}\n"
    if fields.get('lebar_jalan'):
        formatted += f"Lebar: {fields['lebar_jalan']}\n"
    if fields.get('karakter_jalan'):
        formatted += f"Permukaan: {fields['karakter_jalan']}\n"
    if fields.get('kondisi_jalan'):
        formatted += f"Kondisi: {fields['kondisi_jalan']}\n"
    if fields.get('keterangan'):
        formatted += f"Keterangan: {fields['keterangan']}\n"
    
    return formatted.strip()

def process_line(line):
    """Process a single line of data"""
    line = line.strip()
    if not line:
        return None
    
    content_type = detect_content_type(line)
    
    if content_type == "poi":
        title = "Fasilitas"
        content = extract_poi_info(line)
        style = "poi"
        # Extract name for title
        nama_match = re.search(r'Nama POI?\s*:?\s*([^\n,]+)', line, re.IGNORECASE)
        if nama_match:
            title = nama_match.group(1).strip()
            
    elif content_type == "road":
        title = "Jalan"
        content = extract_road_info(line)
        style = "road"
        # Extract road name for title
        nama_match = re.search(r'nama jalan\s*\(\s*(jalur[^)]+)', line, re.IGNORECASE)
        if nama_match:
            title = f"Jalan {nama_match.group(1).strip()}"
    else:
        title = "Information"
        content = line
        style = "general"
    
    html = create_universal_html(content, title, style)
    
    return {
        "type": content_type,
        "title": title,
        "original": line,
        "content": content,
        "html": html
    }

if st.button("🚀 Process All Data", type="primary"):
    if not input_data.strip():
        st.warning("Please paste some data first!")
    else:
        lines = input_data.strip().split('\n')
        results = []
        stats = {"poi": 0, "road": 0, "general": 0}
        
        for line in lines:
            result = process_line(line)
            if result:
                results.append(result)
                stats[result["type"]] += 1
        
        # Display summary
        st.success(f"✅ Processed {len(results)} entries: {stats['poi']} POIs, {stats['road']} Roads, {stats['general']} Others")
        
        # Show all results
        for i, result in enumerate(results, 1):
            with st.expander(f"{result['type'].upper()} - {result['title']}", expanded=(i <= 3)):
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.text("Original Data:")
                    st.code(result['original'], language='text')
                    
                    if result['content'] != result['original']:
                        st.text("Structured Content:")
                        st.code(result['content'], language='text')
                
                with col2:
                    st.text("HTML Preview:")
                    st.components.v1.html(result['html'], height=300)
                    
                    st.text("HTML Code:")
                    st.code(result['html'], language='html')
                    
                    if st.button(f"📋 Copy HTML", key=f"copy_{i}"):
                        st.code(result['html'], language='html')
                        st.success("✅ HTML copied! Paste into uMap description.")

        # Download all
        st.markdown("### 💾 Download All HTML")
        all_html = "\n\n".join([f"<!-- {r['type']} - {r['title']} -->\n{r['html']}" for r in results])
        st.download_button(
            label="📥 Download All HTML",
            data=all_html,
            file_name="umap_descriptions.html",
            mime="text/html"
        )

# Instructions
st.markdown("---")
st.markdown("""
### 🎯 Universal Formatter Features:

**Supports ALL these formats:**
- ✅ **POI Data** (`Nama POI : ..., Desa: ..., Banjar: ...`)
- ✅ **Road Descriptions** (`*Deskripsi jalan* 1. nama jalan (...)`)
- ✅ **Simple Text** (`(Location only)`, `*Deskripsi jalan*`)
- ✅ **Mixed Formats** - Any combination!

**How it works:**
1. **Detects content type** automatically
2. **Extracts structured data** when possible  
3. **Creates beautiful HTML** with appropriate styling
4. **Provides copy buttons** for easy uMap integration

**New Features:**
- **Page breaks after commas** for better readability
- **Bold titles** for emphasis

**Perfect for your 124 mixed-format points!**
""")