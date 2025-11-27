""")

# Option 1: Use data from previous steps
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

# Process styling if we have data
if current_df is not None:
    st.subheader("🎯 Pilih Kolom untuk Styling")
    
    # Show dataframe preview
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
            help="Pilih kolom yang berisi data dengan format: Field1: Value1 | Field2: Value2 | ..."
        )
        
        if selected_columns:
            st.write(f"Selected {len(selected_columns)} columns for styling")
            
            # Preview before and after
            st.subheader("👁️ Preview Sebelum & Sesudah Styling")
            
            preview_row = st.slider("Pilih baris untuk preview:", 0, min(5, len(current_df)-1), 0)
            
            for col in selected_columns[:2]:  # Show first 2 columns
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
                        
                        # Show original vs styled comparison
                        comparison_cols = []
                        for col in selected_columns[:3]:  # Show first 3 for comparison
                            comparison_cols.extend([col, f"{col}_styled"])
                        
                        if comparison_cols:
                            st.dataframe(df_styled[comparison_cols].head(5))
                        
                        # Download options
                        st.subheader("💾 Download Hasil")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            # Full CSV with all columns
                            csv_full = io.StringIO()
                            df_styled.to_csv(csv_full, index=False, encoding='utf-8')
                            st.download_button(
                                "📥 Download Full CSV", 
                                csv_full.getvalue().encode("utf-8"), 
                                "styled_data_full.csv", 
                                "text/csv",
                                help="Semua kolom termasuk yang sudah di-styling"
                            )
                        
                        with col2:
                            # Only styled columns
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
                                    "text/csv",
                                    help="Hanya kolom yang sudah di-styling"
                                )
                        
                        with col3:
                            # GeoJSON export if applicable
                            if '_feature_id' in df_styled.columns and 'geometry_json' in df_styled.columns:
                                geojson_output = dataframe_to_geojson(df_styled)
                                geo_str = json.dumps(geojson_output, indent=2, ensure_ascii=False)
                                st.download_button(
                                    "🗺️ Download as GeoJSON", 
                                    geo_str.encode("utf-8"), 
                                    "styled_data.geojson", 
                                    "application/json"
                                )
                        
                        # Show statistics
                        st.subheader("📈 Statistics")
                        total_cells = len(current_df) * len(selected_columns)
                        styled_cols_count = len([col for col in df_styled.columns if col.endswith('_styled')])
                        st.write(f"- Total records: {len(current_df)}")
                        st.write(f"- Columns styled: {styled_cols_count}")
                        st.write(f"- Total cells processed: {total_cells}")
                        
    else:
        st.warning("⚠️ Tidak ditemukan kolom teks untuk di-styling")

# Standalone HTML converter for quick testing
st.markdown("---")
st.header("🔧 Quick HTML Converter")

st.write("Coba konversi data pipe-separated ke HTML:")

test_input = st.text_area(
    "Masukkan data pipe-separated:",
    value="Nama Fasilitas: Kantor Perbekel Desa Pidpid | Kecamatan: Abang | Desa: Pidpid | Banjar: Pidpid Kelod | Jenis Fasum: Wantilan | Daya Tampung: 300 orang | Fasilitas Pendukung: toilet, listrik, sumber air, dapur umum | Kontak Person: | Jenis Bangunan: Permanen | Luas Area Terbuka: 10x15 meter persegi | Jaringan Komunikasi: internet | Keterangan Tambahan: dekat dengan jalan kabupaten",
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
