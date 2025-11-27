"""
Streamlit app: GeoJSON ↔ CSV bulk properties editor workflow
Includes all steps with bulk HTML styling
"""

import streamlit as st
import pandas as pd
import json
import io
import re
from typing import List, Dict, Any

st.set_page_config(page_title="GeoJSON ↔ CSV Bulk Editor", layout="wide")
st.title("GeoJSON ↔ CSV Bulk Editor — Complete Workflow")

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
        if field_value and field_value.strip():
            fields_html += f'''
  <div style="display: flex; align-items: start; margin-bottom: 8px;">
  <div style="min-width: 160px; font-weight: bold; color: #2c3e50;">{field_name}</div>
  <div style="flex: 1;">: {field_value}</div>
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
