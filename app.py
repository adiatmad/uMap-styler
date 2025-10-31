import streamlit as st
import re

st.set_page_config(page_title="uMap Data Processor", page_icon="🗺️", layout="wide")

st.title("🗺️ uMap Data Processor")
st.subheader("Process your POI and Road data into beautiful uMap descriptions")

# Input area
input_data = st.text_area(
    "Paste your entire data here:",
    height=400,
    placeholder="Paste your data here...\n\nExample:\nNama POI : Contoh Facility...\n*Deskripsi jalan* 1. nama jalan (jalur contoh)..."
)

def process_poi_data(text):
    """Process POI entries into structured format"""
    # Extract basic info
    nama_match = re.search(r'Nama POI?\s*:?\s*([^\n\(]+)', text, re.IGNORECASE)
    
    # Extract detailed info if available
    desa_match = re.search(r'Desa:\s*([^\n]+)', text, re.IGNORECASE)
    banjar_match = re.search(r'Banjar:\s*([^\n]+)', text, re.IGNORECASE)
    jenis_match = re.search(r'Jenis Fasum:\s*\(([^)]+)', text, re.IGNORECASE)
    daya_match = re.search(r'Daya Tampung:\s*([^\n]+)', text, re.IGNORECASE)
    fasilitas_match = re.search(r'Fasilitas Pendukung\s*\(([^)]+)', text, re.IGNORECASE)
    keterangan_match = re.search(r'Keterangan Tambahan:\s*([^\n]+)', text, re.IGNORECASE)
    
    nama = nama_match.group(1).strip() if nama_match else ""
    desa = desa_match.group(1).strip() if desa_match else ""
    banjar = banjar_match.group(1).strip() if banjar_match else ""
    jenis = jenis_match.group(1).strip() if jenis_match else "Fasilitas Umum"
    daya = daya_match.group(1).strip() if daya_match else ""
    fasilitas = fasilitas_match.group(1).strip() if fasilitas_match else ""
    keterangan = keterangan_match.group(1).strip() if keterangan_match else "tempat pengungsian/titik kumpul"
    
    # Create structured output
    structured_output = f"""Nama Fasilitas: {nama}
Jenis: {jenis}
Lokasi: Desa {desa}, Banjar {banjar}
Daya Tampung: {daya}
Fasilitas: {fasilitas}
Keterangan: {keterangan}"""
    
    return structured_output

def process_road_data(text):
    """Process road entries into structured format"""
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
    
    # Create structured output
    structured_output = f"""Nama Jalan: {nama}
Jenis Jalan: {jenis}
Lebar Jalan: {lebar}
Karakter Jalan: {karakter}
Kondisi Jalan: {kondisi}
Keterangan: {keterangan}"""
    
    return structured_output

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
                processed = process_poi_data(line)
                results.append(("🏢 POI", processed))
                stats["pois"] += 1
            elif '*Deskripsi jalan*' in line:
                if 'nama jalan' in line:
                    # Detailed road entry
                    processed = process_road_data(line)
                    results.append(("🛣️ ROAD", processed))
                    stats["roads"] += 1
                else:
                    # Simple road entry
                    results.append(("📍 SIMPLE", line))
                    stats["simple"] += 1
            else:
                # Other entries
                results.append(("📌 OTHER", line))
                stats["simple"] += 1
        
        # Display results
        st.success(f"✅ Processed {len(results)} entries: {stats['pois']} POIs, {stats['roads']} Roads, {stats['simple']} Others")
        
        # Results in tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📋 All Results", "🏢 POIs", "🛣️ Roads", "📊 Summary"])
        
        with tab1:
            for i, (entry_type, result) in enumerate(results, 1):
                with st.expander(f"{entry_type} - Entry {i}"):
                    st.text_area("Structured Data:", value=result, height=200, key=f"all_{i}")
        
        with tab2:
            pois = [r for t, r in results if t == "🏢 POI"]
            for i, poi in enumerate(pois, 1):
                with st.expander(f"POI {i}"):
                    st.text_area("POI Data:", value=poi, height=200, key=f"poi_{i}")
        
        with tab3:
            roads = [r for t, r in results if t == "🛣️ ROAD"]
            for i, road in enumerate(roads, 1):
                with st.expander(f"Road {i}"):
                    st.text_area("Road Data:", value=road, height=200, key=f"road_{i}")
        
        with tab4:
            st.metric("Total POIs", stats["pois"])
            st.metric("Total Roads", stats["roads"])
            st.metric("Other Entries", stats["simple"])
            
            # Show sample of processed data
            st.subheader("Sample Processed Entry")
            if pois:
                st.text(pois[0])
            elif roads:
                st.text(roads[0])
        
        # Download option
        st.markdown("### 💾 Download Processed Data")
        all_processed = "\n\n".join([f"// {t} //\n{r}" for t, r in results])
        st.download_button(
            label="📥 Download All Processed Data",
            data=all_processed,
            file_name="processed_umap_data.txt",
            mime="text/plain"
        )

st.markdown("---")
st.markdown("*Paste your data and click the button to get structured table format!*")