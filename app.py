import streamlit as st
import re

# Page config
st.set_page_config(page_title="uMap HTML Generator", page_icon="🗺️", layout="wide")

# Initialize session state
if 'input_data' not in st.session_state:
    st.session_state.input_data = ""
if 'processed_results' not in st.session_state:
    st.session_state.processed_results = None

# Title
st.title("🗺️ uMap HTML Generator")
st.subheader("Transform your road & POI data into beautiful uMap descriptions")

# Sidebar for customization
with st.sidebar:
    st.header("🎨 Customization")
    road_bg_color = st.color_picker("Road Background", "#fff3cd")
    road_border_color = st.color_picker("Road Border", "#ffeaa7")
    poi_bg_color = st.color_picker("POI Background", "#e8f4fd")
    poi_border_color = st.color_picker("POI Border", "#b8daff")
    
    st.divider()
    st.header("⚙️ Settings")
    show_stats = st.checkbox("Show Statistics", value=True)
    auto_expand = st.checkbox("Auto-expand all entries", value=False)

# Instructions
with st.expander("📋 How to use", expanded=True):
    st.markdown("""
    ### Quick Start:
    1. Click **"📝 Load Example"** to see how it works
    2. **Paste your raw data** in the text area
    3. **Click 'Process Data'** 
    4. **Copy or download** the HTML output
    5. **Paste into uMap** description fields
    
    ### Supported Formats:
    - 🛣️ **Road descriptions** (starts with '*Deskripsi jalan*')
    - 🏢 **POI/Facilities** (starts with 'Nama PO')
    - 📄 **Other entries** (kept as-is)
    """)

# Input format guide
with st.expander("📖 Input Format Guide"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🛣️ Road Format:
        ```
        *Deskripsi jalan* 1. nama jalan (Jalur Utara) 
        2. Jenis jalan (aspal) 3. Lebar Jalan (4 meter) 
        4. karakter jalan (lurus, sedikit menanjak) 
        5. Kondisi Jalan (baik) 
        Keterangan Tambahan: jalan evakuasi utama
        ```
        """)
    
    with col2:
        st.markdown("""
        ### 🏢 POI Format:
        ```
        Nama POI: Gedung Serbaguna Desa 
        Jenis Fasum: (aula) 
        Daya Tampung: 200 orang 
        Fasilitas Pendukung (toilet, dapur umum, listrik)
        Keterangan Tambahan: tempat pengungsian darurat
        ```
        """)

# Example data button
col1, col2, col3 = st.columns([1, 1, 4])
with col1:
    if st.button("📝 Load Example", use_container_width=True):
        st.session_state.input_data = """*Deskripsi jalan* 1. nama jalan (jalur utara) 2. Jenis jalan (aspal) 3. Lebar Jalan (4 meter) 4. karakter jalan (lurus, sedikit menanjak) 5. Kondisi Jalan (baik) Keterangan Tambahan: jalan evakuasi utama
*Deskripsi jalan* 1. nama jalan (jalur selatan) 2. Jenis jalan (beton) 3. Lebar Jalan (3 meter) 4. karakter jalan (berkelok) 5. Kondisi Jalan (cukup baik) Keterangan Tambahan: jalur alternatif
Nama POI: Gedung Serbaguna Desa Jenis Fasum: (aula) Daya Tampung: 200 orang Fasilitas Pendukung (toilet, dapur umum, listrik) Keterangan Tambahan: tempat pengungsian darurat
Nama POI: Lapangan Olahraga Jenis Fasum: (lapangan terbuka) Daya Tampung: 500 orang Fasilitas Pendukung (toilet, lampu penerangan) Keterangan Tambahan: titik kumpul evakuasi"""
        st.rerun()

with col2:
    if st.button("🗑️ Clear All", use_container_width=True):
        st.session_state.input_data = ""
        st.session_state.processed_results = None
        st.rerun()

# Input area
input_data = st.text_area(
    "📝 Paste your entire list here:",
    value=st.session_state.input_data,
    height=300,
    placeholder="Paste your data here...\n\nOr click 'Load Example' above to see how it works!",
    key="input_area"
)

# Update session state
st.session_state.input_data = input_data

# Processing functions
def process_road_data(text, road_bg, road_border):
    """Process road description data with error handling"""
    try:
        # More flexible regex patterns
        nama_match = re.search(r'nama\s+jalan\s*[\(:]\s*([^)\n]+)', text, re.IGNORECASE)
        jenis_match = re.search(r'Jenis\s+jalan\s*[\(:]\s*([^)\n]+)', text, re.IGNORECASE)
        lebar_match = re.search(r'Lebar\s+Jalan\s*[\(:]\s*([^)\n]+)', text, re.IGNORECASE)
        karakter_match = re.search(r'karakter\s+jalan\s*[\(:]\s*([^)\n]+)', text, re.IGNORECASE)
        kondisi_match = re.search(r'Kondisi\s+Jalan\s*[\(:]\s*([^)\n]+)', text, re.IGNORECASE)
        keterangan_match = re.search(r'Keterangan\s+Tambahan\s*:?\s*([^\n]+)', text, re.IGNORECASE)
        
        nama = nama_match.group(1).strip() if nama_match else "jalur"
        jenis = jenis_match.group(1).strip() if jenis_match else "tidak diketahui"
        lebar = lebar_match.group(1).strip() if lebar_match else "tidak diketahui"
        karakter = karakter_match.group(1).strip() if karakter_match else "tidak diketahui"
        kondisi = kondisi_match.group(1).strip() if kondisi_match else "tidak diketahui"
        keterangan = keterangan_match.group(1).strip() if keterangan_match else "jalan evakuasi"
        
        # Clean up nama - take first part if multiple colons
        nama_parts = re.split(r'\s*:\s*', nama)
        if len(nama_parts) > 1:
            nama = nama_parts[0]
        
        # Check for missing critical fields
        warnings = []
        if not nama_match:
            warnings.append("nama jalan")
        if not jenis_match:
            warnings.append("jenis jalan")
        
        html_template = f'''<div style="font-family: Arial, sans-serif; background: {road_bg}; border: 2px solid {road_border}; border-radius: 8px; padding: 16px; max-width: 600px;">
<table style="width: 100%; border-collapse: collapse; font-size: 14px;">
<tr style="border-bottom: 2px solid {road_border};">
<td colspan="2" style="padding: 8px 0; font-size: 16px; font-weight: bold; color: #2c3e50;">🛣️ {nama}</td>
</tr>
<tr>
<td style="padding: 8px 0; width: 140px; font-weight: bold; color: #2c3e50; vertical-align: top;">Jenis Jalan:</td>
<td style="padding: 8px 0; color: #34495e;">{jenis}</td>
</tr>
<tr>
<td style="padding: 8px 0; font-weight: bold; color: #2c3e50; vertical-align: top;">Lebar Jalan:</td>
<td style="padding: 8px 0; color: #34495e;">{lebar}</td>
</tr>
<tr>
<td style="padding: 8px 0; font-weight: bold; color: #2c3e50; vertical-align: top;">Karakter Jalan:</td>
<td style="padding: 8px 0; color: #34495e;">{karakter}</td>
</tr>
<tr>
<td style="padding: 8px 0; font-weight: bold; color: #2c3e50; vertical-align: top;">Kondisi Jalan:</td>
<td style="padding: 8px 0; color: #34495e;">✅ {kondisi}</td>
</tr>
<tr>
<td colspan="2" style="padding-top: 12px;">
<div style="background: #d4edda; padding: 10px; border-radius: 5px; border-left: 4px solid #28a745;">
<strong style="color: #155724;">ℹ️ Keterangan:</strong><br>
<span style="color: #155724;">{keterangan}</span>
</div>
</td>
</tr>
</table>
</div>'''
        
        return html_template.strip(), warnings
    except Exception as e:
        return f"<p style='color: red;'>Error processing road data: {str(e)}</p>", [str(e)]

def process_poi_data(text, poi_bg, poi_border):
    """Process POI/facility data with error handling"""
    try:
        # More flexible regex patterns
        nama_match = re.search(r'Nama\s+POI?\s*:?\s*([^\n\(]+)', text, re.IGNORECASE)
        jenis_match = re.search(r'Jenis\s+Fasum\s*:?\s*[\(:]\s*([^)\n]+)', text, re.IGNORECASE)
        daya_match = re.search(r'Daya\s+Tampung\s*:?\s*([^\n]+)', text, re.IGNORECASE)
        fasilitas_match = re.search(r'Fasilitas\s+Pendukung\s*[\(:]\s*([^)\n]+)', text, re.IGNORECASE)
        keterangan_match = re.search(r'Keterangan\s+Tambahan\s*:?\s*([^\n]+)', text, re.IGNORECASE)
        
        nama = nama_match.group(1).strip() if nama_match else "Fasilitas"
        jenis = jenis_match.group(1).strip() if jenis_match else "Fasilitas Umum"
        daya = daya_match.group(1).strip() if daya_match else "tidak diketahui"
        fasilitas = fasilitas_match.group(1).strip() if fasilitas_match else "tidak diketahui"
        keterangan = keterangan_match.group(1).strip() if keterangan_match else "tempat pengungsian"
        
        # Clean up data - split on colons and extract clean values
        # Handle cases like "Desa: Tiling tali Banjar: Banjar dinas Tiyingtali kelod"
        nama_parts = re.split(r'\s*:\s*', nama)
        if len(nama_parts) > 1:
            nama = nama_parts[0]  # Take first part as main name
        
        # Extract additional info from Daya Tampung field
        daya_clean = daya
        kontak = ""
        luas_area = ""
        
        # Look for contact person
        kontak_match = re.search(r'Kontak\s+person\s*:\s*([^:]+?)(?:\s+Jenis|$)', daya, re.IGNORECASE)
        if kontak_match:
            kontak = kontak_match.group(1).strip()
        
        # Look for Luas Area
        luas_match = re.search(r'Luas\s+Area\s+Terbuka\s*:\s*([^:]+?)(?:\s+Keterangan|$)', daya, re.IGNORECASE)
        if luas_match:
            luas_area = luas_match.group(1).strip()
        
        # Extract just the number for Daya Tampung
        daya_number = re.search(r'([+\-]?\d+[\d\s]*(?:orang|people)?)', daya, re.IGNORECASE)
        if daya_number:
            daya_clean = daya_number.group(1).strip()
        
        # Check for missing critical fields
        warnings = []
        if not nama_match:
            warnings.append("nama POI")
        if not jenis_match:
            warnings.append("jenis fasum")
        
        html_template = f'''<div style="font-family: Arial, sans-serif; background: {poi_bg}; border: 2px solid {poi_border}; border-radius: 8px; padding: 16px; max-width: 600px;">
<table style="width: 100%; border-collapse: collapse; font-size: 14px;">
<tr style="border-bottom: 2px solid {poi_border};">
<td colspan="2" style="padding: 8px 0; font-size: 16px; font-weight: bold; color: #2c3e50;">📍 {nama}</td>
</tr>
<tr>
<td style="padding: 8px 0; width: 140px; font-weight: bold; color: #2c3e50; vertical-align: top;">Jenis:</td>
<td style="padding: 8px 0; color: #34495e;">{jenis}</td>
</tr>
<tr>
<td style="padding: 8px 0; font-weight: bold; color: #2c3e50; vertical-align: top;">Daya Tampung:</td>
<td style="padding: 8px 0; color: #34495e;">{daya_clean}</td>
</tr>'''
        
        # Add optional fields if available
        if kontak:
            html_template += f'''
<tr>
<td style="padding: 8px 0; font-weight: bold; color: #2c3e50; vertical-align: top;">Kontak Person:</td>
<td style="padding: 8px 0; color: #34495e;">{kontak}</td>
</tr>'''
        
        if luas_area:
            html_template += f'''
<tr>
<td style="padding: 8px 0; font-weight: bold; color: #2c3e50; vertical-align: top;">Luas Area:</td>
<td style="padding: 8px 0; color: #34495e;">{luas_area}</td>
</tr>'''
        
        html_template += f'''
<tr>
<td style="padding: 8px 0; font-weight: bold; color: #2c3e50; vertical-align: top;">Fasilitas:</td>
<td style="padding: 8px 0; color: #34495e;">{fasilitas}</td>
</tr>
<tr>
<td colspan="2" style="padding-top: 12px;">
<div style="background: #fff3cd; padding: 10px; border-radius: 5px; border-left: 4px solid #ffc107;">
<strong style="color: #856404;">ℹ️ Keterangan:</strong><br>
<span style="color: #856404;">{keterangan}</span>
</div>
</td>
</tr>
</table>
</div>'''
        
        return html_template.strip(), warnings
    except Exception as e:
        return f"<p style='color: red;'>Error processing POI data: {str(e)}</p>", [str(e)]

# Process button
if st.button("🚀 Process Data", type="primary", use_container_width=True):
    if not input_data.strip():
        st.warning("⚠️ Please paste some data first, or click 'Load Example' to try it out!")
    else:
        with st.spinner("Processing your data..."):
            # Process data
            lines = input_data.strip().split('\n')
            results = []
            stats = {"roads": 0, "pois": 0, "other": 0, "errors": 0}
            all_warnings = []
            
            # Progress bar
            progress_bar = st.progress(0)
            
            for i, line in enumerate(lines):
                if not line.strip():
                    continue
                
                try:
                    if '*Deskripsi jalan*' in line:
                        html, warnings = process_road_data(line, road_bg_color, road_border_color)
                        results.append(("🛣️ ROAD", html, warnings))
                        stats["roads"] += 1
                        if warnings:
                            all_warnings.append(f"Road entry {stats['roads']}: missing {', '.join(warnings)}")
                    elif 'Nama PO' in line:
                        html, warnings = process_poi_data(line, poi_bg_color, poi_border_color)
                        results.append(("🏢 POI", html, warnings))
                        stats["pois"] += 1
                        if warnings:
                            all_warnings.append(f"POI entry {stats['pois']}: missing {', '.join(warnings)}")
                    else:
                        results.append(("📄 OTHER", line, []))
                        stats["other"] += 1
                except Exception as e:
                    results.append(("❌ ERROR", f"Error: {str(e)}\nOriginal: {line}", [str(e)]))
                    stats["errors"] += 1
                
                # Update progress
                progress_bar.progress((i + 1) / len(lines))
            
            progress_bar.empty()
            st.session_state.processed_results = (results, stats, all_warnings)

# Display results
if st.session_state.processed_results:
    results, stats, all_warnings = st.session_state.processed_results
    
    # Success message and stats
    st.success(f"✅ Successfully processed {len(results)} entries!")
    
    if show_stats:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🛣️ Roads", stats["roads"])
        col2.metric("🏢 POIs", stats["pois"])
        col3.metric("📄 Other", stats["other"])
        col4.metric("❌ Errors", stats["errors"])
    
    # Show warnings if any
    if all_warnings:
        with st.expander("⚠️ Warnings", expanded=False):
            for warning in all_warnings:
                st.warning(warning)
    
    # Download button for all HTML
    html_results = [result for entry_type, result, _ in results if entry_type in ["🛣️ ROAD", "🏢 POI"]]
    if html_results:
        all_html = "\n\n<!-- ===== NEXT ENTRY ===== -->\n\n".join(html_results)
        st.download_button(
            label="📥 Download All HTML",
            data=all_html,
            file_name="umap_descriptions.html",
            mime="text/html",
            use_container_width=True
        )
    
    st.divider()
    
    # Display individual results
    st.subheader("📋 Individual Entries")
    
    for i, (entry_type, result, warnings) in enumerate(results, 1):
        with st.expander(f"{entry_type} - Entry {i}", expanded=auto_expand):
            if warnings:
                st.warning(f"⚠️ Missing fields: {', '.join(warnings)}")
            
            if entry_type in ["🛣️ ROAD", "🏢 POI"]:
                # Preview
                st.markdown("**Preview:**")
                st.components.v1.html(result, height=300)
                
                # HTML code with copy button
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown("**HTML Code:**")
                with col2:
                    if st.button("📋 Copy", key=f"copy_{i}"):
                        st.toast("Click the copy button in the code block below!", icon="💡")
                
                st.code(result, language='html')
            else:
                st.text(result)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>💡 <strong>Tip:</strong> Customize colors in the sidebar to match your uMap theme!</p>
    <p>Made with ❤️ for easy uMap formatting</p>
</div>
""", unsafe_allow_html=True)