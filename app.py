import streamlit as st
import re

# Page config
st.set_page_config(page_title="Universal HTML Styler", page_icon="✨", layout="wide")

# Initialize session state
if 'input_data' not in st.session_state:
    st.session_state.input_data = ""
if 'processed_results' not in st.session_state:
    st.session_state.processed_results = None
if 'show_preview' not in st.session_state:
    st.session_state.show_preview = False

# Title
st.title("✨ Universal HTML Styler")
st.subheader("Transform any text into beautiful styled HTML cards")

# Sidebar for customization
with st.sidebar:
    st.header("🎨 Customization")
    card_bg_color = st.color_picker("Card Background", "#e8f4fd")
    card_border_color = st.color_picker("Card Border", "#b8daff")
    info_box_color = st.color_picker("Info Box Background", "#fff3cd")
    
    st.divider()
    st.header("⚙️ Settings")
    show_stats = st.checkbox("Show Statistics", value=True)
    auto_expand = st.checkbox("Auto-expand all entries", value=False)

# Instructions
with st.expander("📋 How to use", expanded=True):
    st.markdown("""
    ### Quick Start:
    1. Click **"📝 Load Example"** to see how it works
    2. **Paste any text** with colon-separated fields
    3. **Click 'Preview'** to see live preview
    4. **Click 'Process Data'** to generate HTML
    5. **Copy or download** the HTML output
    
    ### Features:
    - ✨ **Universal parser** - Works with any colon-separated format
    - 📄 **Page breaks after colons** - Each field on new line
    - 🎨 **Clean table layout** - Professional styling
    - 📋 **Copy & Download** - Easy export
    """)

# Example data button
col1, col2, col3 = st.columns([1, 1, 4])
with col1:
    if st.button("📝 Load Example", use_container_width=True):
        st.session_state.input_data = """SDN 1 Tiyingtali Desa: Tiling tali Banjar: Banjar dinas Tiyingtali kelod Jenis Fasum: Gedung sekolah Daya Tampung: +-600 Fasilitas Pendukung (listrik,sumber air, toilet) Kontak person: Jenis Bangunan:permanen Luas Area Terbuka: 25 are Keterangan Tambahan: di rencanakan sebagai tempat pengungsian
Jalan Raya Utara Jenis: Aspal Lebar: 4 meter Kondisi: Baik Karakteristik: Lurus dan landai Keterangan: Jalan evakuasi utama
Lapangan Olahraga Desa Kapasitas: 500 orang Fasilitas: Toilet, Lampu penerangan Akses: Mudah dijangkau Keterangan: Titik kumpul darurat"""
        st.rerun()

with col2:
    if st.button("🗑️ Clear All", use_container_width=True):
        st.session_state.input_data = ""
        st.session_state.processed_results = None
        st.session_state.show_preview = False
        st.rerun()

# Input area
input_data = st.text_area(
    "📝 Paste your text here:",
    value=st.session_state.input_data,
    height=300,
    placeholder="Paste any text with colon-separated fields...\n\nExample:\nNama Tempat: Gedung Serbaguna Lokasi: Desa Maju Kapasitas: 200 orang\n\nThe parser will automatically detect fields!",
    key="input_area"
)

# Update session state
st.session_state.input_data = input_data

# Universal processing function
def parse_text_to_fields(text):
    """Parse any text and extract key-value pairs separated by colons"""
    fields = []
    
    # Split by colons but preserve the structure
    parts = re.split(r':\s*', text)
    
    if len(parts) < 2:
        # No colons found, treat as single field
        return [("Content", text.strip())]
    
    # First part is the title/name
    title = parts[0].strip()
    
    # Process remaining parts
    for i in range(1, len(parts)):
        if i == len(parts) - 1:
            # Last part - just value
            key = "Info" if i == 1 else prev_key
            value = parts[i].strip()
            if value:
                fields.append((key, value))
        else:
            # Split this part to get value and next key
            # Find where the next key starts (usually after whitespace and before capital letter or keyword)
            match = re.search(r'(.+?)\s+((?:[A-Z][a-z]*|Jenis|Nama|Daya|Fasilitas|Kontak|Luas|Keterangan|Lokasi|Kapasitas|Akses|Lebar|Kondisi|Karakteristik|Desa|Banjar)\b.*)$', parts[i])
            
            if match:
                value = match.group(1).strip()
                next_key_with_value = match.group(2).strip()
                
                # Extract the key from the next part
                key_match = re.match(r'^([^:]+)', next_key_with_value)
                if key_match:
                    prev_key = key_match.group(1).strip()
                else:
                    prev_key = "Field"
                
                if value:
                    fields.append((prev_key if i > 1 else "Info", value))
                
                # Update for next iteration
                parts[i+1] = next_key_with_value.replace(prev_key, '', 1).strip()
            else:
                # Can't split, use whole thing as value
                value = parts[i].strip()
                if value:
                    fields.append(("Field", value))
    
    return [(title, None)] + fields

def create_styled_html(text, bg_color, border_color, info_color):
    """Create styled HTML card from any text input"""
    try:
        fields = parse_text_to_fields(text)
        
        if not fields:
            return "<p>No data to display</p>", []
        
        # First field is the title
        title = fields[0][0] if fields else "Entry"
        
        html_template = f'''<div style="font-family: Arial, sans-serif; background: {bg_color}; border: 2px solid {border_color}; border-radius: 8px; padding: 16px; max-width: 600px; margin: 10px 0;">
<table style="width: 100%; border-collapse: collapse; font-size: 14px;">
<tr style="border-bottom: 2px solid {border_color};">
<td colspan="2" style="padding: 8px 0; font-size: 16px; font-weight: bold; color: #2c3e50;">📌 {title}</td>
</tr>'''
        
        # Add all fields
        for i, (key, value) in enumerate(fields[1:], 1):
            if value:
                # Check if this is a "Keterangan" or info field
                if re.search(r'keterangan|info|catatan|note', key, re.IGNORECASE):
                    html_template += f'''
<tr>
<td colspan="2" style="padding-top: 12px;">
<div style="background: {info_color}; padding: 10px; border-radius: 5px; border-left: 4px solid #ffc107;">
<strong style="color: #856404;">ℹ️ {key}:</strong><br>
<span style="color: #856404;">{value}</span>
</div>
</td>
</tr>'''
                else:
                    html_template += f'''
<tr>
<td style="padding: 8px 0; width: 140px; font-weight: bold; color: #2c3e50; vertical-align: top;">{key}:</td>
<td style="padding: 8px 0; color: #34495e;">{value}</td>
</tr>'''
        
        html_template += '''
</table>
</div>'''
        
        return html_template.strip(), []
    except Exception as e:
        return f"<p style='color: red;'>Error processing data: {str(e)}</p>", [str(e)]

# Preview and Process buttons
col1, col2 = st.columns(2)

with col1:
    if st.button("👁️ Preview", type="secondary", use_container_width=True):
        if not input_data.strip():
            st.warning("⚠️ Please paste some text first!")
        else:
            st.session_state.show_preview = True

with col2:
    if st.button("🚀 Process Data", type="primary", use_container_width=True):
        if not input_data.strip():
            st.warning("⚠️ Please paste some text first, or click 'Load Example' to try it out!")
        else:
            with st.spinner("Processing your data..."):
                # Process data
                lines = input_data.strip().split('\n')
                results = []
                stats = {"entries": 0, "errors": 0}
                
                # Progress bar
                progress_bar = st.progress(0)
                
                for i, line in enumerate(lines):
                    if not line.strip():
                        continue
                    
                    try:
                        html, warnings = create_styled_html(line, card_bg_color, card_border_color, info_box_color)
                        results.append(("📄 ENTRY", html, warnings))
                        stats["entries"] += 1
                    except Exception as e:
                        results.append(("❌ ERROR", f"Error: {str(e)}\nOriginal: {line}", [str(e)]))
                        stats["errors"] += 1
                    
                    # Update progress
                    progress_bar.progress((i + 1) / len(lines))
                
                progress_bar.empty()
                st.session_state.processed_results = (results, stats)
                st.session_state.show_preview = False

# Show preview
if st.session_state.show_preview and input_data.strip():
    st.divider()
    st.subheader("👁️ Live Preview")
    
    lines = input_data.strip().split('\n')
    for i, line in enumerate(lines, 1):
        if line.strip():
            with st.expander(f"Preview Entry {i}", expanded=True):
                html, _ = create_styled_html(line, card_bg_color, card_border_color, info_box_color)
                st.components.v1.html(html, height=400)

# Display processed results
if st.session_state.processed_results:
    results, stats = st.session_state.processed_results
    
    # Success message and stats
    st.success(f"✅ Successfully processed {stats['entries']} entries!")
    
    if show_stats:
        col1, col2 = st.columns(2)
        col1.metric("📄 Total Entries", stats["entries"])
        col2.metric("❌ Errors", stats["errors"])
    
    # Download button for all HTML
    html_results = [result for entry_type, result, _ in results if entry_type == "📄 ENTRY"]
    if html_results:
        all_html = "\n\n<!-- ===== NEXT ENTRY ===== -->\n\n".join(html_results)
        st.download_button(
            label="📥 Download All HTML",
            data=all_html,
            file_name="styled_cards.html",
            mime="text/html",
            use_container_width=True
        )
    
    st.divider()
    
    # Display individual results
    st.subheader("📋 Individual Entries")
    
    for i, (entry_type, result, warnings) in enumerate(results, 1):
        with st.expander(f"{entry_type} {i}", expanded=auto_expand):
            if warnings:
                st.warning(f"⚠️ Issues: {', '.join(warnings)}")
            
            if entry_type == "📄 ENTRY":
                # Preview
                st.markdown("**Preview:**")
                st.components.v1.html(result, height=400)
                
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
    <p>💡 <strong>Tip:</strong> This universal styler works with ANY colon-separated text format!</p>
    <p>Made with ❤️ for easy HTML formatting</p>
</div>
""", unsafe_allow_html=True)