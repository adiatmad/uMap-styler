"""
Streamlit app: GeoJSON ↔ CSV bulk properties editor workflow
Includes all steps with bulk HTML styling
"""

import streamlit as st
import pandas as pd
import json
import io
import re
import html as html_lib
from typing import List, Dict, Any

st.set_page_config(page_title="uMap Styler | ChatMap Review", page_icon="🗺️", layout="wide")
st.markdown(
    """
    <style>
    .block-container {padding-top: 1.7rem; padding-bottom: 3rem; max-width: 1500px;}
    [data-testid="stSidebar"] {border-right: 1px solid rgba(128,128,128,.22);}
    [data-testid="stMetric"] {background: rgba(128,128,128,.07); padding: .8rem 1rem; border-radius: .75rem;}
    div[data-testid="stButton"] > button[kind="primary"] {border-radius: .55rem; font-weight: 600;}
    div[data-testid="stDownloadButton"] > button {border-radius: .55rem;}
    div[data-testid="stFileUploader"] {border-radius: .65rem;}
    .umap-subtitle {font-size: 1.02rem; opacity: .86; max-width: 900px;}
    </style>
    """,
    unsafe_allow_html=True,
)
st.title("🗺️ uMap Styler")
st.markdown('<p class="umap-subtitle">Prepare community mapping data, review corrections, and export only records approved for publication.</p>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## Workspace")
    active_workspace = st.radio(
        "Choose a workflow",
        options=["Beginner guide", "Review ChatMap reports", "Prepare map for uMap", "Advanced tools"],
        index=0,
        help="New here? Start with Beginner guide. It explains each step and which file to use.",
        label_visibility="collapsed",
    )
    st.divider()
    st.caption("**Publishing rule**")
    st.caption("Only verified, conflict-free records are included in the ChatMap export.")
    st.caption("Publishing to uMap remains a manual step; nothing is auto-published.")


# --------------------------
# --- IMPROVED Helper functions -----
# --------------------------

def read_csv_with_fallback(file_buffer):
    try:
        file_buffer.seek(0)
        df = pd.read_csv(file_buffer, encoding='utf-8', dtype=str, keep_default_na=False)
        st.success("✅ CSV dibaca dengan encoding: UTF-8")
        return df
    except UnicodeDecodeError:
        st.warning("❌ UTF-8 gagal, mencoba Latin-1...")
    try:
        file_buffer.seek(0)
        df = pd.read_csv(file_buffer, encoding='latin-1', dtype=str, keep_default_na=False)
        st.success("✅ CSV dibaca dengan encoding: Latin-1")
        return df
    except UnicodeDecodeError:
        st.warning("❌ Latin-1 gagal, mencoba CP1252...")
    try:
        file_buffer.seek(0)
        df = pd.read_csv(file_buffer, encoding='cp1252', dtype=str, keep_default_na=False)
        st.success("✅ CSV dibaca dengan encoding: CP1252")
        return df
    except Exception as e:
        st.error(f"❌ Semua encoding gagal: {e}")
        return None

def read_xlsx_with_fallback(file_buffer):
    try:
        file_buffer.seek(0)
        df = pd.read_excel(file_buffer, dtype=str, keep_default_na=False)
        st.success("✅ XLSX berhasil dibaca")
        return df
    except Exception as e:
        st.error(f"❌ Gagal membaca XLSX: {e}")
        return None

def geojson_to_dataframe(geojson: Dict[str, Any]) -> pd.DataFrame:
    features = geojson.get("features", [])
    rows = []
    for i, feat in enumerate(features):
        props = feat.get("properties", {}) or {}
        geom = feat.get("geometry", None)
        fid = feat.get("id", f"feature_{i}")
        
        row = {"_feature_id": fid, "geometry_json": json.dumps(geom) if geom else ""}
        
        for k, v in props.items():
            row[k] = v
            
        rows.append(row)
    
    if not rows:
        return pd.DataFrame()
        
    df = pd.DataFrame(rows)
    cols = ["_feature_id", "geometry_json"] + [c for c in df.columns if c not in ("_feature_id", "geometry_json")]
    return df[cols]

def dataframe_to_geojson(df: pd.DataFrame) -> Dict[str, Any]:
    features = []
    for _, row in df.iterrows():
        geom_json = row.get("geometry_json", "")
        try:
            geom = json.loads(geom_json) if pd.notna(geom_json) and geom_json and geom_json.strip() else None
        except:
            geom = None
            
        props = {}
        for col in df.columns:
            if col not in ("geometry_json", "_feature_id"):
                value = row[col]
                if pd.notna(value) and value != "":
                    props[col] = value
        
        features.append({
            "type": "Feature",
            "properties": props,
            "geometry": geom,
            "id": row.get("_feature_id")
        })
    
    return {"type": "FeatureCollection", "features": features}

def combine_geojson_files(geojson_files: List[Dict[str, Any]]) -> Dict[str, Any]:
    all_features = []
    feature_ids = set()
    for geojson_obj in geojson_files:
        for feature in geojson_obj.get("features", []):
            original_id = feature.get("id")
            if original_id and original_id in feature_ids:
                counter = 1
                new_id = f"{original_id}_{counter}"
                while new_id in feature_ids:
                    counter += 1
                    new_id = f"{original_id}_{counter}"
                feature["id"] = new_id
                st.warning(f"⚠️ Duplicate ID '{original_id}' renamed to '{new_id}'")
            if feature.get("id"):
                feature_ids.add(feature["id"])
            all_features.append(feature)
    return {"type":"FeatureCollection","features":all_features}

def clean_dataframe(df):
    if df is None:
        return None
        
    df = df.copy()
    df = df.replace(['', 'NaN', 'NaT', 'None', 'nan', 'N/A'], None)
    df = df.fillna('')
    
    for col in df.columns:
        df[col] = df[col].astype(str)
        
    return df

def join_attributes(main_df, add_df, join_key):
    if main_df is None or add_df is None:
        return None
        
    main_df = clean_dataframe(main_df)
    add_df = clean_dataframe(add_df)
    
    if join_key not in main_df.columns:
        st.error(f"❌ Key '{join_key}' tidak ditemukan di file utama. Kolom yang tersedia: {list(main_df.columns)}")
        return None
        
    if join_key not in add_df.columns:
        st.error(f"❌ Key '{join_key}' tidak ditemukan di file tambahan. Kolom yang tersedia: {list(add_df.columns)}")
        return None
    
    main_df[join_key] = main_df[join_key].astype(str).str.strip()
    add_df[join_key] = add_df[join_key].astype(str).str.strip()
    
    joined = pd.merge(main_df, add_df, on=join_key, how="left", suffixes=('', '_add'))
    
    for col in joined.columns:
        if col.endswith('_add'):
            original_col = col[:-4]
            if original_col in joined.columns:
                joined = joined.drop(columns=[col])
    
    st.success(f"✅ Join berhasil! {len(main_df)} records digabung dengan {len(add_df)} records")
    return joined

# --------------------------
# --- STEP D: BULK HTML STYLING FOR PIPE-SEPARATED DATA
# --------------------------

def create_universal_html(fields, style_type="default"):
    styles = {
        "road": {"background": "#e8f4fd", "border": "2px solid #b8daff"},
        "poi": {"background": "#e8f4fd", "border": "2px solid #b8daff"},
        "default": {"background": "#e8f4fd", "border": "2px solid #b8daff"}
    }
    
    style = styles.get(style_type, styles["default"])
    
    fields_html = ""
    for field_name, field_value in fields.items():
        if field_value and str(field_value).strip():
            safe_name = html_lib.escape(str(field_name), quote=True)
            safe_value = html_lib.escape(str(field_value), quote=True)
            fields_html += f'''
  <div style="display: flex; align-items: start; margin-bottom: 8px;">
  <div style="min-width: 160px; font-weight: bold; color: #2c3e50;">{safe_name}</div>
  <div style="flex: 1;">: {safe_value}</div>
  </div>
'''
    
    html_template = f'''
<div style="font-family: Arial, sans-serif; background: {style['background']}; border: {style['border']}; border-radius: 8px; padding: 15px; margin-bottom: 20px;">
<div style="display: grid; gap: 8px;">
{fields_html}
</div>
</div>
'''
    return html_template.strip()

def standardize_indonesian(text):
    if not text or pd.isna(text):
        return ""
        
    text = str(text)
    replacements = {
        r'\bbisa di lalu\b': 'Dapat dilalui',
        r'\bdi lalu\b': 'dilalui',
        r'\bdi pakai\b': 'dipakai',
        r'\bdi jadikan\b': 'dijadikan',
        r'\bdi rencanakan\b': 'direncanakan',
        r'\bdi pake\b': 'dipakai',
        r'\bhelp\b': 'helip',
        r'\b(\d)\s*m\b': r'\1 m',
        r'\b(\d)\s*are\b': r'\1 are',
        r'\+\-\s*': '±',
        r'^\s*jalur\s*': '',
    }
    
    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text.strip()

def extract_fields_from_pipe(text):
    fields = {}
    
    if not text or pd.isna(text):
        return fields
        
    text = str(text)
    parts = [part.strip() for part in text.split('|') if part.strip()]
    
    for part in parts:
        if ':' in part:
            field_parts = part.split(':', 1)
            field_name = field_parts[0].strip()
            field_value = field_parts[1].strip() if len(field_parts) > 1 else ""
            
            field_name = field_name.replace('Nama PO', 'Nama Fasilitas')
            field_name = field_name.replace('Kontak person', 'Kontak Person')
            
            if field_value:
                fields[field_name] = standardize_indonesian(field_value)
        else:
            if 'Informasi' not in fields:
                fields['Informasi'] = standardize_indonesian(part)
            else:
                fields['Informasi'] += f", {standardize_indonesian(part)}"
    
    return fields

def process_pipe_separated_data(text):
    if not text or pd.isna(text):
        return ""
        
    fields = extract_fields_from_pipe(text)
    
    if not fields:
        return "<div style='padding: 10px; background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 4px;'>No data to display</div>"
    
    return create_universal_html(fields, "poi")

def bulk_apply_html_styling(df, columns_to_style):
    if df is None or df.empty:
        return df
        
    df_styled = df.copy()
    
    for col in columns_to_style:
        if col in df_styled.columns:
            new_col_name = f"{col}_styled"
            df_styled[new_col_name] = df_styled[col].apply(process_pipe_separated_data)
            st.write(f"✅ Styled column: {col} → {new_col_name} ({len(df_styled)} cells processed)")
    
    return df_styled

# --------------------------
if active_workspace == "Advanced tools":
    # --- STEP 0: Combine GeoJSON
    # --------------------------
    st.header("🔄 Step 0 — Combine Multiple GeoJSON Files")
    multi_geojson_files = st.file_uploader(
        "Upload multiple GeoJSON files", 
        type=["geojson", "json"], 
        key="multi_geo",
        accept_multiple_files=True
    )
    if multi_geojson_files and len(multi_geojson_files) > 1:
        geojson_objects = []
        valid_files = True
        for uploaded_file in multi_geojson_files:
            try:
                geojson_obj = json.load(uploaded_file)
                if geojson_obj.get("type") == "FeatureCollection":
                    geojson_objects.append(geojson_obj)
                else:
                    st.error(f"❌ File {uploaded_file.name} bukan FeatureCollection")
                    valid_files = False
            except Exception as e:
                st.error(f"❌ File {uploaded_file.name} error: {e}")
                valid_files = False
        if valid_files and geojson_objects:
            combined_geojson = combine_geojson_files(geojson_objects)
            st.success(f"✅ Combined {len(geojson_objects)} files ({len(combined_geojson['features'])} features)")
            st.session_state.combined_geojson = combined_geojson
    
    # --------------------------
    # --- STEP A: GeoJSON → CSV
    # --------------------------
    st.header("📥 Step A — Convert GeoJSON → CSV")
    col1, col2 = st.columns([1,1])
    with col1:
        uploaded_geojson = st.file_uploader("Upload GeoJSON", type=["geojson", "json"], key="upload_geo")
        paste_geo_text = st.text_area("Atau paste GeoJSON di sini (optional)", height=120)
    with col2:
        st.write("Upload GeoJSON asli → CSV untuk bulk edit")
    
    geojson_obj = None
    if 'combined_geojson' in st.session_state:
        geojson_obj = st.session_state.combined_geojson
    elif uploaded_geojson is not None:
        try: 
            geojson_obj = json.load(uploaded_geojson)
            st.success("✅ GeoJSON berhasil dimuat")
        except Exception as e: 
            st.error(f"❌ Gagal parse GeoJSON: {e}")
    elif paste_geo_text.strip() != "":
        try: 
            geojson_obj = json.loads(paste_geo_text)
            st.success("✅ GeoJSON dari teks berhasil dimuat")
        except Exception as e: 
            st.error(f"❌ Gagal parse GeoJSON dari teks: {e}")
    
    if geojson_obj:
        df_out = geojson_to_dataframe(geojson_obj)
        if not df_out.empty:
            st.dataframe(df_out.head(10))
            csv_buffer = io.StringIO()
            df_out.to_csv(csv_buffer, index=False, encoding='utf-8')
            st.download_button("💾 Download CSV untuk diedit", csv_buffer.getvalue().encode("utf-8"), "export_properties.csv", "text/csv")
        else:
            st.warning("⚠️ GeoJSON tidak mengandung features atau kosong")
    
    # --------------------------
    # --- STEP B: CSV → Merge → GeoJSON
    # --------------------------
    st.markdown("---")
    st.header("📤 Step B — Upload CSV hasil edit → Merge → Download GeoJSON")
    edited_csv = st.file_uploader("Upload CSV hasil edit (Step A)", type=["csv"], key="upload_csv")
    if edited_csv:
        df_edited = read_csv_with_fallback(edited_csv)
        if df_edited is not None:
            df_edited = df_edited.replace(['','NaN','NaT','None'], None)
            geo_out = dataframe_to_geojson(df_edited)
            st.download_button("💾 Download merged GeoJSON", json.dumps(geo_out, indent=2, ensure_ascii=False).encode("utf-8"), "merged.geojson", "application/json")
    
    # --------------------------
    # --- STEP C: IMPROVED Stand-alone Join Attributes
    # --------------------------
    st.markdown("---")
    st.header("🧩 Step C — Stand-alone Join Attributes")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("File Utama")
        main_file = st.file_uploader("Upload MAIN file", type=["csv","xlsx","geojson","json"], key="main_file")
    with col2:
        st.subheader("File Tambahan") 
        add_file = st.file_uploader("Upload ADDITIONAL file", type=["csv","xlsx","geojson","json"], key="add_file")
    
    join_key_options = ["id", "_feature_id", "name", "ID", "Id"]
    join_key_c = st.selectbox("Pilih kolom untuk join:", options=join_key_options, index=0, key="join_key_c")
    custom_join_key = st.text_input("Atau masukkan nama kolom manual:", key="custom_join_key")
    final_join_key = custom_join_key if custom_join_key else join_key_c
    
    if 'df_joined_c' not in st.session_state:
        st.session_state.df_joined_c = None
    
    if st.button("🔗 Join Attributes (Step C)", type="primary", key="join_button_improved"):
        if not main_file or not add_file:
            st.error("❌ Both files must be uploaded")
        else:
            try:
                main_df = None
                if main_file.name.lower().endswith(".csv"):
                    main_df = read_csv_with_fallback(main_file)
                elif main_file.name.lower().endswith(".xlsx"):
                    main_df = read_xlsx_with_fallback(main_file)
                else:
                    main_geo = json.load(main_file)
                    main_df = geojson_to_dataframe(main_geo)
    
                add_df = None
                if add_file.name.lower().endswith(".csv"):
                    add_df = read_csv_with_fallback(add_file)
                elif add_file.name.lower().endswith(".xlsx"):
                    add_df = read_xlsx_with_fallback(add_file)
                else:
                    add_geo = json.load(add_file)
                    add_df = geojson_to_dataframe(add_geo)
    
                if main_df is None or main_df.empty:
                    st.error("❌ File utama tidak dapat dibaca atau kosong")
                elif add_df is None or add_df.empty:
                    st.error("❌ File tambahan tidak dapat dibaca atau kosong")
                else:
                    st.write(f"✅ File utama: {len(main_df)} records")
                    st.write(f"✅ File tambahan: {len(add_df)} records")
                    
                    df_joined_c = join_attributes(main_df, add_df, final_join_key)
                    
                    if df_joined_c is not None:
                        st.session_state.df_joined_c = df_joined_c
                        st.subheader("📋 Hasil Join")
                        st.dataframe(df_joined_c.head(10))
                        
                        csv_buffer_c = io.StringIO()
                        df_joined_c.to_csv(csv_buffer_c, index=False, encoding='utf-8')
                        st.download_button(
                            "💾 Download CSV after join", 
                            csv_buffer_c.getvalue().encode("utf-8"), 
                            "joined_attributes_stepC.csv", 
                            "text/csv"
                        )
    
            except Exception as e:
                st.error(f"❌ Failed to join attributes: {e}")
    
    # --------------------------
    # --- STEP D: BULK HTML STYLING FOR PIPE-SEPARATED DATA
    # --------------------------
    st.markdown("---")
    st.header("🎨 Step D — Bulk HTML Styling for Pipe-Separated Data")
    
    st.info("Bulk styling untuk data pipe-separated: Upload CSV, pilih kolom, setiap cell akan di-styling otomatis")
    
    # Pilih sumber data
    st.subheader("📁 Pilih Sumber Data")
    
    data_source = st.radio(
        "Pilih sumber data:",
        ["Gunakan data dari Step C", "Upload CSV baru"],
        index=0
    )
    
    current_df = None
    
    if data_source == "Gunakan data dari Step C":
        if 'df_joined_c' in st.session_state and st.session_state.df_joined_c is not None:
            current_df = st.session_state.df_joined_c
            st.success(f"✅ Menggunakan data dari Step C ({len(current_df)} records)")
        else:
            st.warning("⚠️ Tidak ada data dari Step C. Silakan upload CSV baru.")
            data_source = "Upload CSV baru"
    
    if data_source == "Upload CSV baru" or current_df is None:
        uploaded_csv = st.file_uploader("Upload CSV file untuk styling", type=["csv"], key="html_styling_csv")
        if uploaded_csv:
            current_df = read_csv_with_fallback(uploaded_csv)
            if current_df is not None:
                st.success(f"✅ CSV berhasil dimuat ({len(current_df)} records)")
    
    # Process styling jika ada data
    if current_df is not None:
        st.subheader("🎯 Pilih Kolom untuk Styling")
        
        st.write("**Preview Data:**")
        st.dataframe(current_df.head(5))
        
        # Get text columns
        text_columns = [col for col in current_df.columns 
                       if col not in ['_feature_id', 'geometry_json', 'geometry'] 
                       and current_df[col].dtype == 'object']
        
        if text_columns:
            selected_columns = st.multiselect(
                "Pilih kolom yang berisi data pipe-separated:",
                options=text_columns,
                help="Pilih kolom dengan format: Field1: Value1 | Field2: Value2 | ..."
            )
            
            if selected_columns:
                st.write(f"Selected {len(selected_columns)} columns for styling")
                
                # Preview
                st.subheader("👁️ Preview Sebelum & Sesudah Styling")
                
                preview_row = st.slider("Pilih baris untuk preview:", 0, min(5, len(current_df)-1), 0)
                
                for col in selected_columns[:2]:
                    st.write(f"**Kolom:** `{col}`")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        original_value = current_df.iloc[preview_row][col]
                        st.text_area(
                            "Data Asli:", 
                            value=original_value, 
                            height=100, 
                            key=f"orig_{col}_{preview_row}"
                        )
                    
                    with col2:
                        html_output = process_pipe_separated_data(current_df.iloc[preview_row][col])
                        if html_output:
                            st.components.v1.html(html_output, height=200, scrolling=True)
                            with st.expander("Lihat HTML Code"):
                                st.code(html_output, language='html')
                        else:
                            st.info("Tidak ada data untuk di-styling")
                
                # Bulk processing
                if st.button("🚀 APPLY BULK HTML STYLING", type="primary"):
                    with st.spinner(f"Memproses {len(current_df)} records..."):
                        df_styled = bulk_apply_html_styling(current_df, selected_columns)
                        
                        if df_styled is not None:
                            st.session_state.df_styled_final = df_styled
                            st.success(f"✅ Berhasil memproses {len(current_df)} records!")
                            
                            # Show results
                            st.subheader("📊 Hasil Styling")
                            
                            # Show comparison
                            comparison_cols = []
                            for col in selected_columns[:3]:
                                comparison_cols.extend([col, f"{col}_styled"])
                            
                            if comparison_cols:
                                st.dataframe(df_styled[comparison_cols].head(5))
                            
                            # Download options
                            st.subheader("💾 Download Hasil")
                            
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                csv_full = io.StringIO()
                                df_styled.to_csv(csv_full, index=False, encoding='utf-8')
                                st.download_button(
                                    "📥 Download Full CSV", 
                                    csv_full.getvalue().encode("utf-8"), 
                                    "styled_data_full.csv", 
                                    "text/csv"
                                )
                            
                            with col2:
                                styled_cols = [col for col in df_styled.columns if col.endswith('_styled')]
                                original_ids = [col for col in ['_feature_id', 'id'] if col in df_styled.columns]
                                
                                if styled_cols:
                                    df_only_styled = df_styled[original_ids + styled_cols]
                                    csv_styled = io.StringIO()
                                    df_only_styled.to_csv(csv_styled, index=False, encoding='utf-8')
                                    st.download_button(
                                        "🎨 Download Styled Columns Only", 
                                        csv_styled.getvalue().encode("utf-8"), 
                                        "only_styled_columns.csv", 
                                        "text/csv"
                                    )
                            
                            with col3:
                                if '_feature_id' in df_styled.columns and 'geometry_json' in df_styled.columns:
                                    geojson_output = dataframe_to_geojson(df_styled)
                                    geo_str = json.dumps(geojson_output, indent=2, ensure_ascii=False)
                                    st.download_button(
                                        "🗺️ Download as GeoJSON", 
                                        geo_str.encode("utf-8"), 
                                        "styled_data.geojson", 
                                        "application/json"
                                    )
        else:
            st.warning("⚠️ Tidak ditemukan kolom teks untuk di-styling")
    
    # Quick HTML converter
    st.markdown("---")
    st.header("🔧 Quick HTML Converter")
    
    test_input = st.text_area(
        "Test konversi data pipe-separated ke HTML:",
        value="Nama Fasilitas: Kantor Perbekel Desa Pidpid | Kecamatan: Abang | Desa: Pidpid | Banjar: Pidpid Kelod | Jenis Fasum: Wantilan | Daya Tampung: 300 orang | Fasilitas Pendukung: toilet, listrik, sumber air, dapur umum",
        height=150
    )
    
    if st.button("🔄 Convert to HTML"):
        if test_input.strip():
            html_result = process_pipe_separated_data(test_input)
            st.components.v1.html(html_result, height=400, scrolling=True)
            with st.expander("Lihat HTML Code"):
                st.code(html_result, language='html')
        else:
            st.warning("Masukkan data terlebih dahulu")
    
    st.markdown("---")
    st.write("**✨ Complete GeoJSON ↔ CSV Editor with Bulk HTML Styling**")
    
    
    # --------------------------
    

# ChatMap → reviewed uMap publishing workflow
# --------------------------
import copy
import hashlib

REVIEW_STATUSES = ("New", "Needs correction", "Verified", "Rejected")
_REVIEW_KEYS = {"_review_id", "_review_status", "_review_notes", "_source_fingerprint", "_source_snapshot", "_reviewed_properties"}

def _canonical_json(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str)

def _fingerprint(value):
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()

def _source_properties(feature):
    return {k: v for k, v in (feature.get("properties") or {}).items() if k not in _REVIEW_KEYS}

def _source_snapshot(feature):
    return {"geometry": feature.get("geometry"), "properties": _source_properties(feature)}

def _review_id(feature, index=0):
    props = _source_properties(feature)
    for key in ("report_id", "message_id", "chatmap_id", "uuid", "id"):
        value = props.get(key)
        if value not in (None, ""):
            return str(value)
    if feature.get("id") not in (None, ""):
        return str(feature["id"])
    # Geometry is a useful stable fallback for repeated exports. If several reports
    # share a location, the importer adds a deterministic suffix rather than dropping one.
    return "cm-" + _fingerprint(_source_snapshot(feature))[:20]

def import_chatmap_geojson(geojson, existing_records=None):
    """Merge a ChatMap GeoJSON export into a saved review progress without overwriting edits."""
    if not isinstance(geojson, dict) or geojson.get("type") != "FeatureCollection":
        raise ValueError("Expected a GeoJSON FeatureCollection.")
    incoming = geojson.get("features")
    if not isinstance(incoming, list):
        raise ValueError("FeatureCollection must contain a features array.")
    existing_records = existing_records or {}
    records = copy.deepcopy(existing_records)
    counts = {"new": 0, "unchanged": 0, "changed": 0, "invalid": 0}
    seen_in_import = set()
    for index, raw in enumerate(incoming):
        if not isinstance(raw, dict) or raw.get("type") != "Feature":
            counts["invalid"] += 1
            continue
        geometry = raw.get("geometry")
        valid_geometry_types = {
            "Point", "MultiPoint", "LineString", "MultiLineString",
            "Polygon", "MultiPolygon", "GeometryCollection"
        }
        if (
            "geometry" not in raw
            or (geometry is not None and (
                not isinstance(geometry, dict)
                or geometry.get("type") not in valid_geometry_types
            ))
            or not isinstance(raw.get("properties", {}) or {}, dict)
        ):
            counts["invalid"] += 1
            continue
        feature = copy.deepcopy(raw)
        props = _source_properties(feature)
        source = {"type": "Feature", "geometry": feature.get("geometry"), "properties": props}
        rid = _review_id(feature, index)
        if rid in seen_in_import:
            rid = rid + "-" + _fingerprint(source)[:8]
        seen_in_import.add(rid)
        fingerprint = _fingerprint(source)
        has_explicit_id = (
            feature.get("id") not in (None, "")
            or any(props.get(key) not in (None, "") for key in ("report_id", "message_id", "chatmap_id", "uuid", "id"))
        )
        if rid not in records and not has_explicit_id:
            # ChatMap exports may omit stable feature IDs. Match an otherwise-unmatched
            # report at the same geometry so changed text/media is flagged as a conflict
            # rather than imported as a second report. Ambiguous shared locations are
            # deliberately not auto-matched.
            geometry_matches = [
                existing_id for existing_id, existing in records.items()
                if existing.get("source", {}).get("geometry") == source.get("geometry")
                and not existing.get("conflict")
            ]
            if source.get("geometry") is not None and len(geometry_matches) == 1:
                rid = geometry_matches[0]
        if rid not in records:
            records[rid] = {
                "id": rid, "source": source, "source_fingerprint": fingerprint,
                "reviewed_properties": copy.deepcopy(props), "status": "New",
                "notes": "", "conflict": False
            }
            counts["new"] += 1
            continue
        current = records[rid]
        if current.get("source_fingerprint") == fingerprint:
            counts["unchanged"] += 1
            continue
        # Incoming changes are staged as a conflict. Never replace a human-reviewed
        # version or silently promote changed content into the publication set.
        current["incoming_source"] = source
        current["incoming_fingerprint"] = fingerprint
        current["conflict"] = True
        if current.get("status") == "Verified":
            current["status"] = "Needs correction"
        counts["changed"] += 1
    return records, counts

def promote_incoming_source(records, rid):
    record = records[rid]
    if not record.get("conflict") or not record.get("incoming_source"):
        return False
    record["source"] = copy.deepcopy(record["incoming_source"])
    record["source_fingerprint"] = record["incoming_fingerprint"]
    record["reviewed_properties"] = copy.deepcopy(record["source"].get("properties") or {})
    record.pop("incoming_source", None)
    record.pop("incoming_fingerprint", None)
    record["conflict"] = False
    record["status"] = "Needs correction"
    return True

def reviewed_geojson(records):
    features = []
    for rid, record in records.items():
        if record.get("status") != "Verified" or record.get("conflict"):
            continue
        source = record.get("source") or {}
        props = copy.deepcopy(record.get("reviewed_properties") or {})
        features.append({
            "type": "Feature",
            "id": str(rid),
            "geometry": copy.deepcopy(source.get("geometry")),
            "properties": props
        })
    return {"type": "FeatureCollection", "features": features}

def working_ledger_geojson(records):
    """Portable backup format: review metadata stays outside publishable properties."""
    return {"type": "ChatMapReviewLedger", "version": 1, "records": records}

def load_working_ledger(data):
    if not isinstance(data, dict) or data.get("type") != "ChatMapReviewLedger" or data.get("version") != 1:
        raise ValueError("Not a supported uMap Styler review-ledger file (version 1).")
    records = data.get("records")
    if not isinstance(records, dict):
        raise ValueError("Saved review progress records must be an object.")
    for rid, record in records.items():
        if not isinstance(record, dict) or record.get("status") not in REVIEW_STATUSES:
            raise ValueError(f"Invalid review record or status for {rid!r}.")
        if not isinstance(record.get("source"), dict) or not isinstance(record.get("reviewed_properties"), dict):
            raise ValueError(f"Invalid source or reviewed properties for {rid!r}.")
    return copy.deepcopy(records)


def normalize_review_text(value):
    """Conservative whitespace-only normalization; preserve spelling and casing."""
    if not isinstance(value, str):
        return value
    return re.sub(r"\s+", " ", value).strip()


def inspect_text_quality(properties):
    """Return possible whitespace issues without mutating the source properties."""
    if not isinstance(properties, dict):
        return []
    findings = []
    for field, value in properties.items():
        if not isinstance(value, str):
            continue
        suggestion = normalize_review_text(value)
        if value != suggestion:
            findings.append({
                "field": str(field),
                "issue": "blank_text" if not suggestion and value else "whitespace",
                "original": value,
                "suggestion": suggestion,
                "severity": "review"
            })
    return findings


def find_text_inconsistencies(records, threshold=0.88):
    """Suggest same-field text variants; similarity is not semantic proof."""
    import difflib
    from collections import Counter, defaultdict

    if not isinstance(threshold, (int, float)) or threshold < 0.5 or threshold > 1:
        raise ValueError("Similarity threshold must be between 0.5 and 1.0.")
    values_by_field = defaultdict(list)
    for record in (records or {}).values():
        properties = record.get("reviewed_properties") or {}
        if record.get("conflict") or record.get("status") == "Rejected" or not isinstance(properties, dict):
            continue
        for field, value in properties.items():
            if isinstance(value, str) and normalize_review_text(value):
                values_by_field[str(field)].append(value)

    findings = []
    for field, values in values_by_field.items():
        counts = Counter(values)
        unique_values = sorted(counts)
        formatting_groups = defaultdict(list)
        for value in unique_values:
            formatting_groups[normalize_review_text(value).casefold()].append(value)
        consumed_pairs = set()
        for group in formatting_groups.values():
            if len(group) < 2:
                continue
            canonical = sorted(group, key=lambda item: (-counts[item], item.casefold(), item))[0]
            findings.append({
                "field": field, "kind": "formatting", "values": group,
                "counts": {item: counts[item] for item in group},
                "canonical": canonical, "similarity": 1.0
            })
            for i, left in enumerate(group):
                for right in group[i + 1:]:
                    consumed_pairs.add(tuple(sorted((left, right))))

        for i, left in enumerate(unique_values):
            left_norm = normalize_review_text(left).casefold()
            if len(left_norm) < 5:
                continue
            for right in unique_values[i + 1:]:
                right_norm = normalize_review_text(right).casefold()
                pair = tuple(sorted((left, right)))
                if pair in consumed_pairs or len(right_norm) < 5:
                    continue
                similarity = difflib.SequenceMatcher(None, left_norm, right_norm).ratio()
                if similarity < threshold:
                    continue
                canonical = sorted((left, right), key=lambda item: (-counts[item], item.casefold(), item))[0]
                findings.append({
                    "field": field, "kind": "possible_typo", "values": [left, right],
                    "counts": {left: counts[left], right: counts[right]},
                    "canonical": canonical, "similarity": round(similarity, 3)
                })
    findings.sort(key=lambda item: (item["field"].casefold(), item["kind"], -item["similarity"], item["values"]))
    return findings


def apply_approved_text_replacements(records, field, replacements):
    """Apply an explicitly approved exact-value mapping to review copies only."""
    if not isinstance(field, str) or not field.strip():
        raise ValueError("A non-empty property field is required.")
    if not isinstance(replacements, dict) or not replacements:
        raise ValueError("Provide at least one approved old-value to new-value mapping.")
    for old, new in replacements.items():
        if not isinstance(old, str) or not isinstance(new, str) or not old or not new.strip():
            raise ValueError("Replacement values must be non-empty text.")
    changed_records = 0
    for record in (records or {}).values():
        if record.get("conflict") or record.get("status") == "Rejected":
            continue
        properties = record.get("reviewed_properties")
        if not isinstance(properties, dict):
            continue
        old_value = properties.get(field)
        if isinstance(old_value, str) and old_value in replacements:
            new_value = replacements[old_value]
            if new_value != old_value:
                properties[field] = new_value
                record["status"] = "Needs correction"
                changed_records += 1
    return changed_records


def apply_approved_whitespace_cleanup(records):
    """Apply only whitespace cleanup after explicit user approval."""
    changed_records = 0
    for record in (records or {}).values():
        if record.get("conflict") or record.get("status") == "Rejected":
            continue
        properties = record.get("reviewed_properties")
        if not isinstance(properties, dict):
            continue
        changed = False
        for field, value in list(properties.items()):
            if isinstance(value, str):
                cleaned = normalize_review_text(value)
                if cleaned != value:
                    properties[field] = cleaned
                    changed = True
        if changed:
            record["status"] = "Needs correction"
            changed_records += 1
    return changed_records

def load_spellcheck_engines():
    """Load local Indonesian Hunspell and bundled English spellcheck engines."""
    from pathlib import Path
    from spylls.hunspell import Dictionary
    from spellchecker import SpellChecker
    dictionary_prefix = Path(__file__).resolve().parent / "dictionaries" / "id_ID"
    if not dictionary_prefix.with_suffix(".dic").is_file() or not dictionary_prefix.with_suffix(".aff").is_file():
        raise FileNotFoundError("Indonesian Hunspell dictionary files are missing.")
    return Dictionary.from_files(str(dictionary_prefix)), SpellChecker(language="en")


def spellcheck_text(value, id_dictionary, english_checker, custom_words=None):
    """Return conservative spelling suggestions without mutating text."""
    if not isinstance(value, str) or not value.strip():
        return []
    safe_words = {str(word).strip().casefold() for word in (custom_words or []) if str(word).strip()}
    token_pattern = re.compile(r"(?<![\w])([^\W\d_][^\W\d_'-]*)(?![\w])", re.UNICODE)
    # URLs, email addresses, and common structured reference IDs are not prose.
    protected_pattern = re.compile(
        r"(?:https?://|www\.)[^\s<>]+"
        r"|\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b"
        r"|\b(?:id|uuid|ref|code|ticket|task)[\s:_#-]*[A-Z0-9][A-Z0-9_-]{2,}\b",
        re.IGNORECASE,
    )
    protected_spans = [match.span() for match in protected_pattern.finditer(value)]
    findings = []
    for match in token_pattern.finditer(value):
        if any(start <= match.start(1) and match.end(1) <= end for start, end in protected_spans):
            continue
        token = match.group(1)
        folded = token.casefold()
        if len(token) < 4 or folded in safe_words or token.isupper() or token[0].isupper():
            continue
        try:
            known_id = bool(id_dictionary.lookup(token))
        except Exception:
            known_id = False
        try:
            known_en = bool(english_checker.known([token]))
        except Exception:
            known_en = False
        if known_id or known_en:
            continue
        # Small domain lexicon fallback covers common waste-mapping terms even
        # when a Hunspell suggestion list is empty. This is a suggestion source,
        # never an automatic correction rule.
        candidates = [
            "plastik", "sungai", "sampah", "limbah", "organik", "anorganik",
            "pembuangan", "tumpukan", "bersih", "kotor", "terbuka", "tercemar",
            "plastic", "river", "waste", "dumping", "rubbish", "garbage",
            "collection", "recycling", "community", "location"
        ]
        try:
            candidates.extend(id_dictionary.suggest(token)[:5])
        except Exception:
            pass
        try:
            candidate = english_checker.correction(token)
            if candidate:
                candidates.append(candidate)
        except Exception:
            pass
        unique = []
        for candidate in candidates:
            if isinstance(candidate, str) and candidate.casefold() != folded and candidate.casefold() not in safe_words and candidate.casefold() not in {x.casefold() for x in unique}:
                unique.append(candidate)
        if not unique:
            continue
        import difflib
        ranked = sorted(unique, key=lambda item: difflib.SequenceMatcher(None, folded, item.casefold()).ratio(), reverse=True)
        suggestion = ranked[0]
        similarity = difflib.SequenceMatcher(None, folded, suggestion.casefold()).ratio()
        if similarity < 0.72:
            continue
        findings.append({"token": token, "suggestion_token": suggestion, "similarity": round(similarity, 3), "start": match.start(1), "end": match.end(1)})
    return findings


def spellcheck_properties(properties, id_dictionary, english_checker, custom_words=None):
    """Return field-level suggestions without changing input properties."""
    if not isinstance(properties, dict):
        return []
    findings = []
    for field, value in properties.items():
        if not isinstance(value, str) or not value.strip():
            continue
        tokens = spellcheck_text(value, id_dictionary, english_checker, custom_words)
        if not tokens:
            continue
        corrected = value
        for item in reversed(tokens):
            corrected = corrected[:item["start"]] + item["suggestion_token"] + corrected[item["end"]:]
        findings.append({"field": str(field), "original": value, "suggestion": corrected, "tokens": [item["token"] for item in tokens], "token_suggestions": [item["suggestion_token"] for item in tokens]})
    return findings


def apply_approved_spellcheck_finding(records, rid, field, original, suggestion):
    """Apply one explicit correction to one review copy, never the source."""
    if not isinstance(field, str) or not field.strip():
        raise ValueError("A field name is required.")
    if not isinstance(original, str) or not isinstance(suggestion, str) or not suggestion.strip():
        raise ValueError("Original and non-empty suggestion text are required.")
    record = (records or {}).get(rid)
    if not isinstance(record, dict) or record.get("conflict") or record.get("status") == "Rejected":
        return False
    properties = record.get("reviewed_properties")
    if not isinstance(properties, dict) or properties.get(field) != original or original == suggestion:
        return False
    properties[field] = suggestion
    record["status"] = "Needs correction"
    return True


def merge_project_vocabulary(existing_text, additions):
    """Merge reviewer-approved vocabulary terms without duplicates."""
    existing = [word.strip() for word in re.split(r"[\n,;]+", str(existing_text or "")) if word.strip()]
    seen = {word.casefold() for word in existing}
    for raw_word in additions or []:
        word = str(raw_word).strip()
        if word and word.casefold() not in seen:
            existing.append(word)
            seen.add(word.casefold())
    return "\n".join(existing)


def _add_spellcheck_words_to_vocabulary(words):
    """Update vocabulary widget state in Streamlit's pre-rerun callback."""
    current = st.session_state.get("chatmap_project_vocabulary_editor", "")
    merged = merge_project_vocabulary(current, words)
    st.session_state["chatmap_project_vocabulary_editor"] = merged
    st.session_state["chatmap_project_vocabulary_text"] = merged


def _parse_chatmap_geojson(upload):
    try:
        data = json.loads(upload.getvalue().decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Could not parse UTF-8 JSON: {exc}") from exc
    if not isinstance(data, dict) or data.get("type") != "FeatureCollection":
        raise ValueError("ChatMap download must be a GeoJSON FeatureCollection.")
    return data

if active_workspace == "Beginner guide":
    st.markdown("---")
    st.header("Welcome — start here")
    st.write("Use this tool to check reports from ChatMap before adding them to your community map. Follow the steps in order. You do not need to understand technical terms.")
    st.subheader("Before you begin")
    st.markdown("""
    - Have the latest report file you downloaded from ChatMap.
    - If you reviewed reports before, find your **saved review progress** file.
    - Make sure you can open and edit the uMap map where these reports belong.
    """)
    st.subheader("Follow these steps")
    with st.container(border=True):
        st.markdown("### 1. Load your reports")
        st.write("Choose **Review ChatMap reports** in the menu on the left. If this is your first time, upload the latest file you downloaded from ChatMap and click **Load and check reports**.")
        st.write("If you are returning, first upload your **saved review progress** file, then load the newest report file from ChatMap.")
    with st.container(border=True):
        st.markdown("### 2. Check and correct each report")
        st.write("Choose a report from the list. Read the original information, then update the details in the text box if needed. The box contains formatted text, so keep the punctuation in place. If you are unsure how to change it, leave it unchanged and write a note for the next person. Choose the review result and click **Save this report**.")
        st.write("Do not guess. If you are unsure, add a note and do not approve the report. If a warning says the report has changed, check the new information before approving it.")
    with st.container(border=True):
        st.markdown("### 3. Prepare the map file")
        st.write("Open **Prepare your map**. This page shows how many reports are approved and ready. Download **approved reports for uMap**. Only approved reports without unresolved warnings are included.")
    with st.container(border=True):
        st.markdown("### 4. Add the file to uMap")
        st.write("Open your uMap map and enter edit mode. Choose **Import data**, select the approved reports file you downloaded, check that the points or areas and details look right, then save the map.")
    with st.container(border=True):
        st.markdown("### 5. Save your progress for next time")
        st.write("On **Prepare your map**, download **saved review progress** and keep it somewhere safe. Next time, upload it in **Review ChatMap reports** before loading the newest ChatMap file.")
    st.warning("This tool does not update uMap by itself. You choose what to approve, import the approved file, check the result, and save the map.")
    st.subheader("What do these words mean?")
    st.markdown("""
    - **Original information:** what came from ChatMap; it is kept so you can compare it with your edits.
    - **Your edited copy:** the version you can correct.
    - **Needs checking:** this report is not ready for the map yet.
    - **Changed since your last check:** a newer ChatMap file has different information; check it again.
    - **Verified:** you checked the report and approve it for the map.
    - **Saved review progress:** a backup of your corrections and decisions. It is not the map file.
    """)

if active_workspace in ("Review ChatMap reports", "Prepare map for uMap"):
    st.markdown("---")
    if active_workspace == "Review ChatMap reports":
        st.header("Review ChatMap reports")
        st.write("Load reports, check and correct their details, and save your decisions. When finished, open **Prepare your map**.")
    else:
        st.header("Prepare map for uMap")
        st.caption("Download only approved reports, then import the file into your uMap map yourself.")
    
    
    if "chatmap_review_records" not in st.session_state:
        st.session_state.chatmap_review_records = {}
    
    if active_workspace == "Review ChatMap reports":
        with st.expander("Step 1 — Load saved review progress (only if you have used this tool before)", expanded=not bool(st.session_state.chatmap_review_records)):
            ledger_upload = st.file_uploader("Choose your saved review progress file (optional)", type=["json"], key="chatmap_ledger_upload")
            if ledger_upload and st.button("Load my saved progress", key="restore_chatmap_ledger"):
                try:
                    restored = load_working_ledger(json.loads(ledger_upload.getvalue().decode("utf-8-sig")))
                    st.session_state.chatmap_review_records = restored
                    st.success(f"Restored {len(restored)} review records.")
                except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                    st.error(f"Could not load saved progress: {exc}")
        
        with st.expander("Step 2 — Load reports from ChatMap", expanded=True):
            chatmap_upload = st.file_uploader("Choose the report file downloaded from ChatMap", type=["geojson", "json"], key="chatmap_geojson_upload")
            if chatmap_upload and st.button("Load and check reports", type="primary", key="import_chatmap"):
                try:
                    parsed = _parse_chatmap_geojson(chatmap_upload)
                    records, counts = import_chatmap_geojson(parsed, st.session_state.chatmap_review_records)
                    st.session_state.chatmap_review_records = records
                    st.success(f"Import checked: {counts['new']} new, {counts['unchanged']} unchanged, {counts['changed']} changed/conflicting, {counts['invalid']} invalid feature(s) skipped.")
                except ValueError as exc:
                    st.error(f"Import failed: {exc}")
        
    records = st.session_state.chatmap_review_records
    if active_workspace == "Review ChatMap reports" and records:
        status_counts = {status: sum(1 for r in records.values() if r.get("status") == status) for status in REVIEW_STATUSES}
        status_labels = {
            "New": "Not checked yet",
            "Needs correction": "Needs more checking",
            "Verified": "Approved for map",
            "Rejected": "Do not use",
        }
        metric_cols = st.columns(4)
        for col, status in zip(metric_cols, REVIEW_STATUSES):
            col.metric(status_labels.get(status, status), status_counts[status])
        conflict_count = sum(1 for r in records.values() if r.get("conflict"))
        st.caption(f"{conflict_count} report(s) have newer information that needs checking. These reports cannot be included in the map file until the warning is resolved.")
    
    
        with st.expander("C. Detect text-quality issues and inconsistent labels", expanded=False):
            st.caption("Local checks only: whitespace, case/format variants, and similar values within the same field. Similarity is a clue, not proof. No report text is sent to an external service.")
            if st.button("Scan reviewed text", key="chatmap_text_quality_scan"):
                issue_rows = []
                for rid, rec in records.items():
                    for issue in inspect_text_quality(rec.get("reviewed_properties") or {}):
                        issue_rows.append({
                            "Report ID": rid, "Field": issue["field"], "Issue": issue["issue"],
                            "Original": issue["original"], "Suggestion": issue["suggestion"]
                        })
                st.session_state.chatmap_text_quality_issues = issue_rows
                st.session_state.chatmap_text_quality_findings = find_text_inconsistencies(records)

            st.markdown("**Indonesian + English spelling suggestions**")
            st.caption("Local dictionary checks only. Capitalized words, acronyms, and project-vocabulary terms are skipped conservatively. Nothing changes until you approve a suggestion.")
            vocabulary_text = st.text_area(
                "Project vocabulary (one word per line)",
                value=st.session_state.get("chatmap_project_vocabulary_text", "Kaliwlingi\nBrebes\nChatMap\nuMap\nWhatsApp\nMangrovesari"),
                height=100, key="chatmap_project_vocabulary_editor",
                help="Add place names, local terms, abbreviations, and valid regional words to reduce false positives."
            )
            st.session_state.chatmap_project_vocabulary_text = vocabulary_text
            custom_words = [word.strip() for word in re.split(r"[\n,;]+", vocabulary_text) if word.strip()]
            scan_spelling = st.button("Scan Indonesian + English spelling", key="chatmap_spellcheck_scan", type="primary")
            clear_spelling = st.button("Clear spelling results", key="chatmap_spellcheck_clear")
            if clear_spelling:
                st.session_state.pop("chatmap_spellcheck_findings", None)
                st.rerun()
            if scan_spelling:
                try:
                    if "chatmap_spellcheck_engines" not in st.session_state:
                        st.session_state.chatmap_spellcheck_engines = load_spellcheck_engines()
                    id_dictionary, english_checker = st.session_state.chatmap_spellcheck_engines
                    spell_rows = []
                    for rid, rec in records.items():
                        if rec.get("conflict") or rec.get("status") == "Rejected":
                            continue
                        for finding in spellcheck_properties(rec.get("reviewed_properties") or {}, id_dictionary, english_checker, custom_words):
                            spell_rows.append({"report_id": rid, **finding})
                    st.session_state.chatmap_spellcheck_findings = spell_rows
                    st.success(f"Spelling scan complete: {len(spell_rows)} field(s) need human review. No data was changed.")
                except Exception as exc:
                    st.error(f"Local spelling engine could not start: {exc}")
            if "chatmap_spellcheck_findings" in st.session_state:
                spell_rows = st.session_state.chatmap_spellcheck_findings
                if not spell_rows:
                    st.success("No spelling suggestions found. This does not guarantee spelling or grammar is correct.")
                else:
                    st.write(f"**Spelling suggestions awaiting review: {len(spell_rows)}**")
                    for row_index, row in enumerate(spell_rows):
                        rid = row["report_id"]
                        with st.container(border=True):
                            st.markdown(f"**Report:** {rid} · **Field:** {row['field']}")
                            st.write("Original")
                            st.code(row["original"], language=None)
                            st.write("Suggested")
                            st.code(row["suggestion"], language=None)
                            st.caption("Possible tokens: " + ", ".join(row["tokens"]))
                            if st.button("Approve this correction", key=f"approve_spell_{row_index}_{_fingerprint([rid, row['field'], row['original']])[:8]}"):
                                applied = apply_approved_spellcheck_finding(records, rid, row["field"], row["original"], row["suggestion"])
                                if applied:
                                    st.session_state.chatmap_review_records = records
                                    st.session_state.chatmap_spellcheck_findings = [item for item in spell_rows if not (item["report_id"] == rid and item["field"] == row["field"] and item["original"] == row["original"])]
                                    st.success("Correction applied to this review copy only. The record is now Needs correction.")
                                    st.rerun()
                                else:
                                    st.warning("Not applied: record changed, conflicted/rejected, or no longer eligible. Scan again.")
                            st.button(
                                "Add flagged words to vocabulary",
                                key=f"vocab_spell_{row_index}_{_fingerprint([rid, row['field'], row['original']])[:8]}",
                                on_click=_add_spellcheck_words_to_vocabulary,
                                args=(row["tokens"],),
                                help="Adds the flagged tokens to the editable vocabulary above."
                            )

            if "chatmap_text_quality_issues" in st.session_state:
                issue_rows = st.session_state.chatmap_text_quality_issues
                if issue_rows:
                    st.write(f"**Whitespace findings:** {len(issue_rows)}")
                    st.dataframe(pd.DataFrame(issue_rows), use_container_width=True)
                    st.warning("Whitespace cleanup is proposed, not applied automatically.")
                    if st.button("Approve and apply whitespace-only cleanup", key="approve_whitespace_cleanup"):
                        changed = apply_approved_whitespace_cleanup(records)
                        st.session_state.chatmap_review_records = records
                        st.success(f"Applied whitespace cleanup to {changed} eligible record(s). Changed records are now Needs correction and must be reviewed again.")
                        st.rerun()
                else:
                    st.success("No whitespace issues found in reviewed text.")
            if "chatmap_text_quality_findings" in st.session_state:
                findings = st.session_state.chatmap_text_quality_findings
                if findings:
                    st.write(f"**Potential inconsistent labels / typos:** {len(findings)}")
                    options = list(range(len(findings)))
                    selected_finding = st.selectbox(
                        "Choose a suggested cluster",
                        options=options,
                        format_func=lambda idx: (
                            f"{findings[idx]['field']}: {' ↔ '.join(findings[idx]['values'])} "
                            f"({findings[idx]['kind']}, similarity {findings[idx]['similarity']:.3f})"
                        ),
                        key="chatmap_text_cluster_choice"
                    )
                    finding = findings[selected_finding]
                    st.write("Values and counts in this cluster:")
                    st.dataframe(pd.DataFrame([
                        {"Value": value, "Count": finding["counts"].get(value, 0)}
                        for value in finding["values"]
                    ]), use_container_width=True)
                    st.caption("Review the context before merging. Similar spelling can represent different places, objects, or meanings.")
                    approved_value = st.text_input(
                        "Approved canonical value (editable)",
                        value=finding["canonical"],
                        key=f"chatmap_canonical_{selected_finding}"
                    )
                    if st.button("Approve this mapping across eligible records", key="apply_text_cluster"):
                        if not approved_value.strip():
                            st.error("Canonical value cannot be empty.")
                        else:
                            mapping = {value: approved_value for value in finding["values"] if value != approved_value}
                            try:
                                changed = apply_approved_text_replacements(records, finding["field"], mapping)
                                st.session_state.chatmap_review_records = records
                                st.success(f"Applied the approved mapping to {changed} eligible record(s). Changed records are now Needs correction and must be reviewed again.")
                                st.rerun()
                            except ValueError as exc:
                                st.error(f"Mapping not applied: {exc}")
                else:
                    st.success("No likely same-field text variants found at the current similarity threshold.")
            else:
                st.info("Run the scan to inspect whitespace issues and likely text variants.")
    
        with st.expander("D. Review and correct one report", expanded=True):
            ids = list(records.keys())
            status_labels = {"New": "Not checked yet", "Needs correction": "Needs more checking", "Verified": "Approved for map", "Rejected": "Do not use"}
            labels = {rid: f"{rid} — {status_labels.get(records[rid].get('status', 'New'), records[rid].get('status', 'New'))}" + (" ⚠ needs another check" if records[rid].get("conflict") else "") for rid in ids}
            selected_id = st.selectbox("Report", options=ids, format_func=lambda rid: labels[rid], key="selected_chatmap_report")
            record = records[selected_id]
            st.write("**Original information from ChatMap (kept unchanged)**")
            st.json(record.get("source", {}))
            if record.get("conflict"):
                st.warning("A newer ChatMap file contains different information for this report. Your earlier edits are safe. Check the new information before approving it.")
                st.json(record.get("incoming_source", {}))
                if st.button("Use the updated information and check this report again", key="accept_chatmap_incoming"):
                    promote_incoming_source(records, selected_id)
                    st.session_state.chatmap_review_records = records
                    st.rerun()
            properties_text = st.text_area(
                "Your corrected report details",
                value=json.dumps(record.get("reviewed_properties") or {}, ensure_ascii=False, indent=2),
                height=220,
                key=f"review_props_{selected_id}",
                help="This box shows the report details as structured text. Change only the information you need and keep the punctuation around it. If you are unsure, leave it unchanged and write a note below."
            )
            status_labels = {"New": "Not checked yet — I have not reviewed this report", "Needs correction": "Needs more checking — not ready for the map", "Verified": "Approved for map — I checked this report", "Rejected": "Do not use — this report should not appear on the map"}
            status = st.selectbox("What is the review result?", options=REVIEW_STATUSES, format_func=lambda value: status_labels.get(value, value), index=REVIEW_STATUSES.index(record.get("status", "New")), key=f"review_status_{selected_id}")
            notes = st.text_area("Notes for the next person (optional)", value=record.get("notes", ""), key=f"review_notes_{selected_id}")
            if st.button("Save this report", type="primary", key="save_chatmap_review"):
                try:
                    corrected = json.loads(properties_text)
                    if not isinstance(corrected, dict):
                        raise ValueError("The report details are not in the expected format. Undo the last change or restore the punctuation, then try again.")
                    if status == "Verified" and record.get("conflict"):
                        raise ValueError("Resolve the incoming-source conflict before marking this record Verified.")
                    record["reviewed_properties"] = corrected
                    record["status"] = status
                    record["notes"] = notes
                    st.session_state.chatmap_review_records = records
                    st.success("Your changes are saved for this session. On **Prepare your map**, download **saved review progress** so you can continue another time.")
                except json.JSONDecodeError:
                    st.error("Could not save because the report details are not in the expected format. Undo the last change or restore the punctuation, then try again.")
                except ValueError as exc:
                    st.error(f"Could not save this report: {exc}")

if active_workspace == "Prepare map for uMap":
    st.header("Prepare your map")
    st.write("Use this page to make a file of approved reports for your uMap map. Nothing is sent to uMap automatically.")
    if not records:
        st.info("**No reports loaded yet.** First open **Review ChatMap reports**, load your ChatMap report file, and check the reports. Then return here.")
    else:
        publishable = reviewed_geojson(records)
        ready_count = len(publishable["features"])
        st.subheader("Step 1 — Check what is ready")
        st.write(f"**Reports ready for your map: {ready_count} of {len(records)}**")
        if ready_count:
            st.dataframe(pd.DataFrame([
                {"Report": rid, "Review result": {"New": "Not checked yet", "Needs correction": "Needs more checking", "Verified": "Approved for map", "Rejected": "Do not use"}.get(rec.get("status"), rec.get("status")), "Needs another check": "Yes" if rec.get("conflict") else "No", "Notes": rec.get("notes", "")}
                for rid, rec in records.items()
            ]), use_container_width=True)
            st.caption("Only reports marked **Verified** with no unresolved change warning are included.")
            with st.expander("Preview the approved reports"):
                st.json(publishable)
        else:
            st.warning("No reports are ready yet. Return to **Review ChatMap reports**, check each report, choose **Verified**, and save it. Resolve any change warnings first.")
        st.subheader("Step 2 — Download reports for uMap")
        st.write("Save the approved reports file to your computer. You will add this file to uMap yourself.")
        st.download_button(
            "Download approved reports for uMap",
            data=json.dumps(publishable, ensure_ascii=False, indent=2).encode("utf-8"),
            file_name="verified_for_umap.geojson",
            mime="application/geo+json",
            disabled=not bool(publishable["features"]),
            key="download_verified_chatmap_geojson"
        )
        st.subheader("Step 3 — Save your progress for next time")
        st.write("Keep this backup safe. It remembers your corrections and review decisions. It is not the file you import into your map.")
        st.download_button(
            "Download saved review progress",
            data=json.dumps(working_ledger_geojson(records), ensure_ascii=False, indent=2).encode("utf-8"),
            file_name="chatmap_review_progress.json",
            mime="application/json",
            key="download_chatmap_review_ledger"
        )
        st.subheader("Step 4 — Add the approved file to uMap")
        st.markdown("""
        1. Open your uMap map and enter edit mode.
        2. Choose **Import data** and select the file named verified_for_umap.geojson.
        3. Check that the points or areas appear in the right places and their details look correct.
        4. Save your uMap map.
        
        If you cannot find **Import data**, make sure you are editing the map. The button position can vary.
        """)
        st.warning("Downloading does not update uMap. Check the map before saving. Reports that are not approved are not included.")
