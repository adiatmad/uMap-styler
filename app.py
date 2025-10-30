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

        def process_poi_data(text):
            nama_match = re.search(r'Nama POI?\s*:?\s*([^\n\(]+)', text, re.IGNORECASE)
            jenis_match = re.search(r'Jenis Fasum:\s*\(([^)]+)', text, re.IGNORECASE)
            daya_match = re.search(r'Daya Tampung:\s*([^\n]+)', text, re.IGNORECASE)
            fasilitas_match = re.search(r'Fasilitas Pendukung\s*\(([^)]+)', text, re.IGNORECASE)
            keterangan_match = re.search(r'Keterangan Tambahan:\s*([^\n]+)', text, re.IGNORECASE)
            
            nama = nama_match.group(1).strip() if nama_match else ""
            jenis = jenis_match.group(1).strip() if jenis_match else "Fasilitas Umum"
            daya = daya_match.group(1).strip() if daya_match else ""
            fasilitas = fasilitas_match.group(1).strip() if fasilitas_match else ""
            keterangan = keterangan_match.group(1).strip() if keterangan_match else "tempat pengungsian"
            
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

        # Process data
        lines = input_data.strip().split('\n')
        results = []
        stats = {"roads": 0, "pois": 0, "other": 0}
        
        for line in lines:
            if not line.strip():
                continue
            if '*Deskripsi jalan*' in line:
                html = process_road_data(line)
                results.append(("🛣️ ROAD", html))
                stats["roads"] += 1
            elif 'Nama PO' in line:
                html = process_poi_data(line)
                results.append(("🏢 POI", html))
                stats["pois"] += 1
            else:
                results.append(("📌 OTHER", line))
                stats["other"] += 1

        # Display results
        st.success(f"✅ Processed {len(results)} entries")
        
        for i, (entry_type, result) in enumerate(results, 1):
            with st.expander(f"{entry_type} - Entry {i}"):
                if entry_type in ["🛣️ ROAD", "🏢 POI"]:
                    st.components.v1.html(result, height=300)
                    st.code(result, language='html')
                else:
                    st.text(result)