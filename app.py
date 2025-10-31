import streamlit as st
import re

st.set_page_config(page_title="uMap HTML Generator", page_icon="🗺️", layout="wide")

st.title("🗺️ uMap HTML Generator")
st.subheader("Transform your data into beautiful uMap descriptions with copy buttons")

# Input area
input_data = st.text_area(
    "Paste your entire data here:",
    height=400,
    placeholder="Paste your data here...\n\nExample:\nNama POI : Contoh Facility...\n*Deskripsi jalan* 1. nama jalan (jalur contoh)..."
)

def create_poi_html(nama, jenis, daya, fasilitas, keterangan):
    """Create HTML for POI entries"""
    html_template = f'''
<div style="font-family: Arial, sans-serif; background: #e8f4fd; border: 2px solid #b8daff; border-radius: 8px; padding: 12px;">
<div style="display: grid; gap: 8px;">
<div style="display: flex; align-items: start;">
<div style="min-width: 140px; font-weight: bold; color: #2c3e50;">Nama Fasilitas:</div>
<div>{nama}</div>
</div>
<div style="display: flex; align-items: start;">
<div style="min-width: 140px; font-weight: bold; color: #2c3e50;">Jenis:</div>
<div>{jenis}</div>
</div>
<div style="display: flex; align-items: start;">
<div style="min-width: 140px; font-weight: bold; color: #2c3e50;">Daya Tampung:</div>
<div>{daya}</div>
</div>
<div style="display: flex; align-items: start;">
<div style="min-width: 140px; font-weight: bold; color: #2c3e50;">Fasilitas:</div>
<div>{fasilitas}</div>
</div>
<div style="background: #fff3cd; padding: 8px; border-radius: 5px; margin-top: 5px;">
<strong>Keterangan:</strong> {keterangan}
</div>
</div>
</div>
'''
    return html_template.strip()

def create_road_html(nama, jenis, lebar, karakter, kondisi, keterangan):
    """Create HTML for road entries"""
    html_template = f'''
<div style="font-family: Arial, sans-serif; background: #fff3cd; border: 2px solid #ffeaa7; border-radius: 8px; padding: 12px;">
<div style="display: grid; gap: 8px;">
<div style="display: flex; align-items: start;">
<div style="min-width: 120px; font-weight: bold; color: #2c3e50;">Nama Jalan:</div>
<div>{nama}</div>
</div>
<div style="display: flex; align-items: start;">
<div style="min-width: 120px; font-weight: bold; color: #2c3e50;">Jenis Jalan:</div>
<div>{jenis}</div>
</div>
<div style="display: flex; align-items: start;">
<div style="min-width: 120px; font-weight: bold; color: #2c3e50;">Lebar Jalan:</div>
<div>{lebar}</div>
</div>
<div style="display: flex; align-items: start;">
<div style="min-width: 120px; font-weight: bold; color: #2c3e50;">Karakter Jalan:</div>
<div>{karakter}</div>
</div>
<div style="display: flex; align-items: start;">
<div style="min-width: 120px; font-weight: bold; color: #2c3e50;">Kondisi Jalan:</div>
<div>✅ {kondisi}</div>
</div>
<div style="background: #d4edda; padding: 8px; border-radius: 5px; margin-top: 5px;">
<strong>Keterangan:</strong> {keterangan}
</div>
</div>
</div>
'''
    return html_template.strip()

def process_poi_data(text):
    """Process POI entries"""
    # Extract basic info
    nama_match = re.search(r'Nama POI?\s*:?\s*([^\n\(]+)', text, re.IGNORECASE)
    
    # Extract detailed info
    jenis_match = re.search(r'Jenis Fasum:\s*\(([^)]+)', text, re.IGNORECASE)
    daya_match = re.search(r'Daya Tampung:\s*([^\n]+)', text, re.IGNORECASE)
    fasilitas_match = re.search(r'Fasilitas Pendukung\s*\(([^)]+)', text, re.IGNORECASE)
    keterangan_match = re.search(r'Keterangan Tambahan:\s*([^\n]+)', text, re.IGNORECASE)
    
    nama = nama_match.group(1).strip() if nama_match else "Fasilitas"
    jenis = jenis_match.group(1).strip() if jenis_match else "Fasilitas Umum"
    daya = daya_match.group(1).strip() if daya_match else ""
    fasilitas = fasilitas_match.group(1).strip() if fasilitas_match else ""
    keterangan = keterangan_match.group(1).strip() if keterangan_match else "tempat pengungsian"
    
    # Create structured text
    structured_text = f"""Nama Fasilitas: {nama}
Jenis: {jenis}
Daya Tampung: {daya}
Fasilitas: {fasilitas}
Keterangan: {keterangan}"""
    
    # Create HTML
    html_code = create_poi_html(nama, jenis, daya, fasilitas, keterangan)
    
    return structured_text, html_code

def process_road_data(text):
    """Process road entries"""
    # Extract road info
    nama_match = re.search(r'nama jalan\s*\(\s*(jalur[^)]+)', text, re.IGNORECASE)
    jenis_match = re.search(r'Jenis jalan\s*\(\s*([^)]+)', text, re.IGNORECASE)
    lebar_match = re.search(r'Lebar Jalan\s*\(\s*([^)]+)', text, re.IGNORECASE)
    karakter_match = re.search(r'karakter jalan\s*\(\s*([^)]+)', text, re.IGNORECASE)
    kondisi_match = re.search(r'Kondisi Jalan\s*\(\s*([^)]+)', text, re.IGNORECASE)
    keterangan_match = re.search(r'Keterangan Tambahan\s*:([^<]*)', text, re.IGNORECASE)
    
    nama = nama_match.group(1).strip() if nama_match else "jalur"
    jenis = jenis_match.group(1).strip() if jenis_match else ""
    lebar = lebar_match.group(1).strip() if lebar_match else ""
    karakter = karakter_match.group(1).strip() if karakter_match else ""
    kondisi = kondisi_match.group(1).strip() if kondisi_match else ""
    keterangan = keterangan_match.group(1).strip() if keterangan_match else "jalan evakuasi"
    
    # Create structured text
    structured_text = f"""Nama Jalan: {nama}
Jenis Jalan: {jenis}
Lebar Jalan: {lebar}
Karakter Jalan: {karakter}
Kondisi Jalan: {kondisi}
Keterangan: {keterangan}"""
    
    # Create HTML
    html_code = create_road_html(nama, jenis, lebar, karakter, kondisi, keterangan)
    
    return structured_text, html_code

if st.button("🚀 Process Data", type="primary"):
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
                structured, html = process_poi_data(line)
                results.append(("🏢 POI", line, structured, html))
                stats["pois"] += 1
            elif '*Deskripsi jalan*' in line:
                if 'nama jalan' in line:
                    # Detailed road entry
                    structured, html = process_road_data(line)
                    results.append(("🛣️ ROAD", line, structured, html))
                    stats["roads"] += 1
                else:
                    # Simple road entry
                    results.append(("📍 SIMPLE", line, line, ""))
                    stats["simple"] += 1
            else:
                # Other entries
                results.append(("📌 OTHER", line, line, ""))
                stats["simple"] += 1
        
        # Display results
        st.success(f"✅ Processed {len(results)} entries: {stats['pois']} POIs, {stats['roads']} Roads, {stats['simple']} Others")
        
        # Results in tabs
        tab1, tab2, tab3 = st.tabs(["📋 All Results", "🏢 POIs Only", "🛣️ Roads Only"])
        
        with tab1:
            for i, (entry_type, original, structured, html) in enumerate(results, 1):
                with st.expander(f"{entry_type} - Entry {i}"):
                    st.text("Original Data:")
                    st.code(original, language='text')
                    
                    if structured != original:
                        st.text("Structured Data:")
                        st.code(structured, language='text')
                    
                    if html:
                        st.text("HTML Preview:")
                        st.components.v1.html(html, height=250)
                        
                        st.text("HTML Code (Copy this for uMap):")
                        st.code(html, language='html')
                        
                        # Copy button
                        if st.button(f"📋 Copy HTML", key=f"copy_{i}"):
                            st.code(html, language='html')
                            st.success("HTML copied to clipboard!")
        
        with tab2:
            pois = [r for r in results if r[0] == "🏢 POI"]
            for i, (entry_type, original, structured, html) in enumerate(pois, 1):
                with st.expander(f"POI {i}: {original[:50]}..."):
                    st.text("Structured Data:")
                    st.code(structured, language='text')
                    
                    st.text("HTML Preview:")
                    st.components.v1.html(html, height=250)
                    
                    st.text("HTML Code:")
                    st.code(html, language='html')
                    
                    if st.button(f"📋 Copy HTML", key=f"copy_poi_{i}"):
                        st.code(html, language='html')
                        st.success("HTML copied to clipboard!")
        
        with tab3:
            roads = [r for r in results if r[0] == "🛣️ ROAD"]
            for i, (entry_type, original, structured, html) in enumerate(roads, 1):
                with st.expander(f"Road {i}: {original[:50]}..."):
                    st.text("Structured Data:")
                    st.code(structured, language='text')
                    
                    st.text("HTML Preview:")
                    st.components.v1.html(html, height=250)
                    
                    st.text("HTML Code:")
                    st.code(html, language='html')
                    
                    if st.button(f"📋 Copy HTML", key=f"copy_road_{i}"):
                        st.code(html, language='html')
                        st.success("HTML copied to clipboard!")

        # Download all HTML
        st.markdown("### 💾 Download All HTML")
        all_html = "\n\n".join([f"<!-- {t} -->\n{h}" for t, o, s, h in results if h])
        st.download_button(
            label="📥 Download All HTML",
            data=all_html,
            file_name="umap_descriptions.html",
            mime="text/html"
        )

st.markdown("---")
st.markdown("*Paste your data and get beautiful uMap HTML with copy buttons!*")