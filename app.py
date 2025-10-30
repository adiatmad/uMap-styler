import streamlit as st
import re

# Page config
st.set_page_config(page_title="Live HTML Editor", page_icon="✨", layout="wide")

# Initialize session state
if 'input_data' not in st.session_state:
    st.session_state.input_data = ""
if 'html_output' not in st.session_state:
    st.session_state.html_output = ""
if 'current_entry' not in st.session_state:
    st.session_state.current_entry = 0

# Title
st.title("✨ Live HTML Editor & Styler")
st.subheader("Edit your text and see the HTML result in real-time")

# Sidebar for customization
with st.sidebar:
    st.header("🎨 Customization")
    card_bg_color = st.color_picker("Card Background", "#e8f4fd")
    card_border_color = st.color_picker("Card Border", "#b8daff")
    info_box_color = st.color_picker("Info Box Background", "#fff3cd")
    
    st.divider()
    st.header("⚙️ Options")
    auto_title = st.text_input("Card Title (leave empty for auto-detect)", "")
    title_icon = st.text_input("Title Icon", "📌")

# Instructions
with st.expander("📋 How to use", expanded=True):
    st.markdown("""
    ### Quick Start:
    1. Click **"📝 Load Example"** to see how it works
    2. **Type or paste** your text in the left panel
    3. **Add fields** using the format: `Label: Value`
    4. **See live preview** on the right panel automatically
    5. **Copy HTML** when you're satisfied
    
    ### Format Tips:
    - Each line with `:` becomes a table row
    - First line is used as the card title
    - Use keywords like `Keterangan`, `Catatan`, `Info` for highlighted boxes
    - Empty lines are ignored
    """)

# Example data button
col1, col2 = st.columns([1, 5])
with col1:
    if st.button("📝 Load Example", use_container_width=True):
        st.session_state.input_data = """SDN 1 Tiyingtali
Desa: Tiling tali
Banjar: Banjar dinas Tiyingtali kelod
Jenis Fasum: Gedung sekolah
Daya Tampung: +-600 orang
Fasilitas: listrik, sumber air, toilet
Kontak Person: Pak Budi
Luas Area: 25 are
Keterangan: Direncanakan sebagai tempat pengungsian"""
        st.rerun()

with col2:
    if st.button("🗑️ Clear All", use_container_width=True):
        st.session_state.input_data = ""
        st.session_state.html_output = ""
        st.rerun()

# Create two columns for live editing
left_col, right_col = st.columns([1, 1])

# Universal processing function
def parse_text_to_fields(text, title_override=""):
    """Parse text and extract key-value pairs"""
    lines = text.strip().split('\n')
    fields = []
    title = title_override
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        # Check if line contains colon
        if ':' in line:
            parts = line.split(':', 1)
            key = parts[0].strip()
            value = parts[1].strip() if len(parts) > 1 else ""
            
            if value:
                fields.append((key, value))
        else:
            # No colon - use as title if first line
            if i == 0 and not title:
                title = line
            else:
                # Treat as a field without colon
                fields.append((line, ""))
    
    # If no title found, use first field as title
    if not title and fields:
        title = fields[0][0]
        fields = fields[1:]
    elif not title:
        title = "Entry"
    
    return title, fields

def create_styled_html(text, bg_color, border_color, info_color, title_override="", icon="📌"):
    """Create styled HTML card from text input"""
    try:
        title, fields = parse_text_to_fields(text, title_override)
        
        if not fields:
            return f"<p style='color: #999; padding: 20px; text-align: center;'>Start typing to see the preview...</p>"
        
        html_template = f'''<div style="font-family: Arial, sans-serif; background: {bg_color}; border: 2px solid {border_color}; border-radius: 8px; padding: 16px; max-width: 600px; margin: 10px auto;">
<table style="width: 100%; border-collapse: collapse; font-size: 14px;">
<tr style="border-bottom: 2px solid {border_color};">
<td colspan="2" style="padding: 8px 0; font-size: 16px; font-weight: bold; color: #2c3e50;">{icon} {title}</td>
</tr>'''
        
        # Add all fields
        for key, value in fields:
            if not value:
                continue
                
            # Check if this is a "Keterangan" or info field
            if re.search(r'keterangan|info|catatan|note|informasi', key, re.IGNORECASE):
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
<td style="padding: 8px 0; width: 150px; font-weight: bold; color: #2c3e50; vertical-align: top;">{key}:</td>
<td style="padding: 8px 0; color: #34495e;">{value}</td>
</tr>'''
        
        html_template += '''
</table>
</div>'''
        
        return html_template.strip()
    except Exception as e:
        return f"<p style='color: red;'>Error: {str(e)}</p>"

# Left column - Input
with left_col:
    st.markdown("### 📝 Input Text")
    input_data = st.text_area(
        "Type or paste your text here:",
        value=st.session_state.input_data,
        height=500,
        placeholder="Example:\nSDN 1 Tiyingtali\nDesa: Tiling tali\nJenis: Gedung sekolah\nKapasitas: 600 orang\nKeterangan: Tempat pengungsian",
        key="input_area",
        label_visibility="collapsed"
    )
    
    # Update session state
    st.session_state.input_data = input_data
    
    # Generate HTML on change
    if input_data.strip():
        st.session_state.html_output = create_styled_html(
            input_data, 
            card_bg_color, 
            card_border_color, 
            info_box_color,
            auto_title,
            title_icon
        )
    else:
        st.session_state.html_output = "<p style='color: #999; padding: 20px; text-align: center;'>Start typing to see the preview...</p>"

# Right column - Preview
with right_col:
    st.markdown("### 👁️ Live Preview")
    
    # Preview container
    preview_container = st.container()
    with preview_container:
        if st.session_state.html_output:
            st.components.v1.html(st.session_state.html_output, height=550, scrolling=True)
        else:
            st.info("👈 Start typing on the left to see the preview")

# HTML Output section below
st.divider()
st.markdown("### 📋 HTML Output")

col1, col2 = st.columns([5, 1])
with col1:
    st.markdown("Copy this HTML code to use in uMap or anywhere else:")
with col2:
    if st.session_state.html_output and input_data.strip():
        st.download_button(
            label="📥 Download",
            data=st.session_state.html_output,
            file_name="styled_card.html",
            mime="text/html",
            use_container_width=True
        )

if st.session_state.html_output and input_data.strip():
    st.code(st.session_state.html_output, language='html', line_numbers=True)
else:
    st.info("HTML code will appear here once you start typing")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>💡 <strong>Tip:</strong> Use the color pickers in the sidebar to customize your card style!</p>
    <p>Made with ❤️ for easy HTML formatting</p>
</div>
""", unsafe_allow_html=True)