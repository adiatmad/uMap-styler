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
    
    The app automatically detects:
    - 🛣️ **Road descriptions** (starts with '*Deskripsi jalan*')
    - 🏢 **POI/Facilities** (starts with 'Nama PO')
    - 🔄 **Other entries** (kept as-is)
    """)

# Input area
input_data = st.text_area(
    "Paste your entire list here:",
    height=300,
    placeholder="Paste your data here...\n\nExample:\n*Deskripsi jalan* 1. nama jalan (jalur contoh)...\nNama POI : Contoh Facility..."
)

# Process button
if st.button("🚀 Process Data", type="primary"):
    if not input_data.strip():
        st.warning("Please paste some data first!")
    else:
        def process_road_data(text):
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

        def process_poi_data(poi_lines):
            """Process multi-line POI data"""
            poi_text = "\n".join(poi_lines)
            
            # Extract fields with better regex patterns
            nama_match = re.search(r'Nama POI?\s*:?\s*([^\n]+)', poi_text, re.IGNORECASE)
            desa_match = re.search(r'Desa\s*:\s*([^\n]+)', poi_text, re.IGNORECASE)
            banjar_match = re.search(r'Banjar\s*:\s*([^\n]+)', poi_text, re.IGNORECASE)
            jenis_match = re.search(r'Jenis Fasum:\s*\(([^)]+)', poi_text, re.IGNORECASE)
            daya_match = re.search(r'Daya Tampung:\s*([^\n]+)', poi_text, re.IGNORECASE)
            fasilitas_match = re.search(r'Fasilitas Pendukung\s*\(([^)]+)', poi_text, re.IGNORECASE)
            luas_match = re.search(r'Luas Area Terbuka:\s*([^\n]+)', poi_text, re.IGNORECASE)
            keterangan_match = re.search(r'Keterangan Tambahan:\s*([^\n]+)', poi_text, re.IGNORECASE)
            
            # Clean and format the values
            nama = nama_match.group(1).strip() if nama_match else ""
            desa = desa_match.group(1).strip() if desa_match else ""
            banjar = banjar_match.group(1).strip() if banjar_match else ""
            jenis = jenis_match.group(1).strip() if jenis_match else "Fasilitas Umum"
            daya = daya_match.group(1).strip() if daya_match else ""
            fasilitas = fasilitas_match.group(1).strip() if fasilitas_match else ""
            luas = luas_match.group(1).strip() if luas_match else ""
            keterangan = keterangan_match.group(1).strip() if keterangan_match else "tempat pengungsian"
            
            # Clean up daya tampung (remove +- and format)
            if daya:
                daya = daya.replace('+-', '±').strip()
            
            html_template = f'''
<div style="font-family: Arial, sans-serif; background: #e8f4fd; border: 2px solid #b8daff; border-radius: 8px; padding: 12px;">
<div style="display: grid; gap: 6px;">
<div style="display: flex; align-items: start;">
<div style="min-width: 140px; font-weight: bold; color: #2c3e50;">Nama Fasilitas:</div>
<div>{nama}</div>
</div>
<div style="display: flex; align-items: start;">
<div style="min-width: 140px; font-weight: bold; color: #2c3e50;">Desa:</div>
<div>{desa}</div>
</div>
<div style="display: flex; align-items: start;">
<div style="min-width: 140px; font-weight: bold; color: #2c3e50;">Banjar:</div>
<div>{banjar}</div>
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
<div style="display: flex; align-items: start;">
<div style="min-width: 140px; font-weight: bold; color: #2c3e50;">Luas Area:</div>
<div>{luas}</div>
</div>
<div style="background: #fff3cd; padding: 8px; border-radius: 5px; margin-top: 5px;">
<strong>Keterangan:</strong> {keterangan}
</div>
</div>
</div>
'''
            return html_template.strip()

        # Process data with improved multi-line handling
        lines = input_data.strip().split('\n')
        results = []
        stats = {"roads": 0, "pois": 0, "other": 0}
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
                
            if '*Deskripsi jalan*' in line:
                html = process_road_data(line)
                results.append(("🛣️ ROAD", html))
                stats["roads"] += 1
                i += 1
                
            elif 'Nama PO' in line:
                # Collect all lines for this POI (until next entry or empty line)
                poi_lines = [line]
                i += 1
                while i < len(lines) and lines[i].strip() and not ('*Deskripsi jalan*' in lines[i] or 'Nama PO' in lines[i]):
                    poi_lines.append(lines[i].strip())
                    i += 1
                
                html = process_poi_data(poi_lines)
                results.append(("🏢 POI", html))
                stats["pois"] += 1
                
            else:
                results.append(("📌 OTHER", line))
                stats["other"] += 1
                i += 1

        # Display results
        st.success(f"✅ Processed {len(results)} entries: {stats['roads']} roads, {stats['pois']} POIs, {stats['other']} others")
        
        # Create tabs for better organization
        tab1, tab2, tab3 = st.tabs(["📋 All Results", "🛣️ Roads Only", "🏢 POIs Only"])
        
        with tab1:
            for i, (entry_type, result) in enumerate(results, 1):
                with st.expander(f"{entry_type} - Entry {i}", expanded=True):
                    if entry_type in ["🛣️ ROAD", "🏢 POI"]:
                        st.components.v1.html(result, height=400)
                        st.code(result, language='html')
                    else:
                        st.text(result)
        
        with tab2:
            roads = [r for t, r in results if t == "🛣️ ROAD"]
            for i, road in enumerate(roads, 1):
                with st.expander(f"Road {i}", expanded=True):
                    st.components.v1.html(road, height=400)
                    st.code(road, language='html')
        
        with tab3:
            pois = [r for t, r in results if t == "🏢 POI"]
            for i, poi in enumerate(pois, 1):
                with st.expander(f"POI {i}", expanded=True):
                    st.components.v1.html(poi, height=400)
                    st.code(poi, language='html')

        # Download option
        st.markdown("### 💾 Download Results")
        all_html = "\n\n".join([f"<!-- {t} -->\n{r}" for t, r in results])
        st.download_button(
            label="📥 Download All HTML",
            data=all_html,
            file_name="umap_descriptions.html",
            mime="text/html"
        )