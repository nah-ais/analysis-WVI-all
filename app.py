import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# ==========================================
# NOTES: PENGATURAN DATASET
# ==========================================
# Pastikan semua file .csv ini ada di folder yang sama dengan script ini.
# Jika nama file lo berbeda, ubah daftar di bawah ini:
FILES = {
    "main": "tbl_main.csv",
    "kpi": "tbl_kpi.csv",
    "sentiment": "tbl_sentimen.csv",
    "sub": "tbl_sub.csv",
    "word_freq": "tbl_word_freq.csv",
    "dim_gender": "tbl_dim_gender.csv",
    "dim_summary": "tbl_dim_summary.csv",
    "dim_umur": "tbl_dim_umur.csv",
    "dim_wilayah": "tbl_dim_wilayah.csv"
}
# ==========================================

st.set_page_config(page_title="Dashboard Suara Anak 2024", layout="wide")

# Fungsi Load Data
@st.cache_data
def load_all_data():
    data = {}
    for key, path in FILES.items():
        data[key] = pd.read_csv(path)
    return data

try:
    data = load_all_data()
    
    # --- SIDEBAR FILTER ---
    st.sidebar.image("https://via.placeholder.com/150x50?text=LOGO+PROJECT", use_column_width=True)
    st.sidebar.title("Filter Global")
    
    # Filter Wilayah menggunakan data dari tbl_main
    list_wilayah = ["Semua"] + sorted(data['main']['Wilayah'].unique().tolist())
    sel_wilayah = st.sidebar.selectbox("Pilih Wilayah", list_wilayah)

    # Filter data berdasarkan wilayah
    if sel_wilayah != "Semua":
        df_main = data['main'][data['main']['Wilayah'] == sel_wilayah]
        df_sub = data['sub'][data['sub']['Wilayah'] == sel_wilayah]
    else:
        df_main = data['main']
        df_sub = data['sub']

    # --- HEADER & KPI ---
    st.title("🚀 Analisis Dampak Banjir terhadap Anak")
    st.markdown(f"**Lokasi:** {sel_wilayah} | **Total Data:** {len(df_main)} Tanggapan")
    
    # KPI Cards dari tbl_kpi
    cols = st.columns(4)
    kpi_data = data['kpi'].set_index('Metrik')['Nilai']
    cols[0].metric("Total Responden", f"{len(df_main)}")
    cols[1].metric("Perempuan", f"{len(df_main[df_main['Jenis Kelamin']=='Perempuan'])}")
    cols[2].metric("Laki-laki", f"{len(df_main[df_main['Jenis Kelamin']=='Laki laki'])}")
    cols[3].metric("Sentimen Positif", f"{len(df_main[df_main['Sentimen']=='Positif'])}")

    st.write("---")

    # --- TABS DIMENSI ---
    tab_titles = ["Ringkasan", "1. Pendidikan", "2. Kesehatan", "3. Pengetahuan", "4. Perlindungan", "5. Kesejahteraan", "6. Harapan"]
    tabs = st.tabs(tab_titles)

    # --- TAB 0: RINGKASAN ---
    with tabs[0]:
        c1, c2 = st.columns([2, 1])
        with c1:
            st.subheader("Sebaran Isu per Dimensi")
            fig_dim = px.bar(data['dim_summary'], x='Dimensi', y='Jumlah', color='Dimensi', text_auto=True)
            st.plotly_chart(fig_dim, use_container_width=True)
        with c2:
            st.subheader("Proporsi Sentimen")
            fig_sent = px.pie(df_main, names='Sentimen', color='Sentimen', 
                              color_discrete_map={'Negatif':'#EF553B', 'Netral':'#636EFA', 'Positif':'#00CC96'})
            st.plotly_chart(fig_sent, use_container_width=True)

    # --- FUNGSI GENERATOR HALAMAN DIMENSI ---
    def render_dimension_page(dim_name, color_theme):
        st.header(f"Analisis {dim_name}")
        
        # Subset Data
        df_dim = df_sub[df_sub['Dimensi_Utama'].str.contains(dim_name.split(".")[1].strip())]
        
        if df_dim.empty:
            st.warning("Data untuk dimensi ini tidak ditemukan dalam filter saat ini.")
            return

        # Row 1: Bubble Chart (Sesuai instruksi: Pengganti Treemap)
        st.subheader(f"Intensitas Sub-Dimensi {dim_name}")
        sub_counts = df_dim['Sub_Dimensi'].value_counts().reset_index()
        sub_counts.columns = ['Kategori', 'Jumlah']
        fig_bubble = px.scatter(sub_counts, x='Kategori', y='Jumlah', size='Jumlah', color='Kategori',
                                size_max=70, title=f"Visualisasi Gelembung {dim_name}")
        st.plotly_chart(fig_bubble, use_container_width=True)

        # Row 2: Demografi Breakdown
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("#### Berdasarkan Gender")
            fig_gen = px.bar(df_dim, x='Jenis Kelamin', color='Sub_Dimensi', barmode='stack')
            st.plotly_chart(fig_gen, use_container_width=True)
        with col_b:
            st.markdown("#### Berdasarkan Kelompok Umur")
            fig_age = px.bar(df_dim, x='Umur_Group', color='Sub_Dimensi', barmode='group')
            st.plotly_chart(fig_age, use_container_width=True)

        # Row 3: Raw Data Detail
        with st.expander("Lihat Detail Tanggapan Anak"):
            st.table(df_dim[['Wilayah', 'Sub_Dimensi', 'Tanggapan_Final']].head(20))

    # Render tiap tab (1-6)
    dims = ["1. Pendidikan", "2. Kesehatan", "3. Pengetahuan", "4. Perlindungan", "5. Kesejahteraan", "6. Harapan"]
    colors = ["blue", "red", "green", "orange", "purple", "brown"]
    
    for i in range(1, 7):
        with tabs[i]:
            render_dimension_page(dims[i-1], colors[i-1])

    # --- WORD CLOUD FOOTER ---
    st.write("---")
    st.subheader("☁️ Awan Kata: Apa yang Paling Sering Diucapkan Anak?")
    # Generate WC dari tbl_word_freq
    wc_dict = dict(zip(data['word_freq']['Kata'], data['word_freq']['Frekuensi']))
    wordcloud = WordCloud(width=1200, height=400, background_color='white').generate_from_frequencies(wc_dict)
    
    fig_wc, ax = plt.subplots(figsize=(15, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")
    st.pyplot(fig_wc)

except Exception as e:
    st.error(f"Terjadi kesalahan: {e}")
    st.info("Tips: Pastikan ke-10 file CSV ada di folder yang sama dan format kolomnya sesuai.")
