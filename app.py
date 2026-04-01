import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# --- CONFIG DATASET ---
FILES = {
    "main": "tbl_main.csv", "kpi": "tbl_kpi.csv", "sentiment": "tbl_sentimen.csv",
    "sub": "tbl_sub.csv", "word_freq": "tbl_word_freq.csv", "dim_summary": "tbl_dim_summary.csv"
}

st.set_page_config(page_title="Executive Dashboard - Suara Anak", layout="wide")

# --- CUSTOM CSS UNTUK TAMPILAN MEWAH ---
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    .metric-card {
        background-color: white; padding: 20px; border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 5px solid #007bff;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: white; border-radius: 5px 5px 0 0; padding: 10px 20px;
    }
    </style>
    """, unsafe_all_with_debug=True)

@st.cache_data
def load_data():
    return {k: pd.read_csv(v) for k, v in FILES.items()}

try:
    data = load_data()
    df_main = data['main']
    
    # --- SIDEBAR & GLOBAL FILTER ---
    st.sidebar.title("🧭 Navigation")
    list_wilayah = ["Seluruh Wilayah"] + sorted(df_main['Wilayah'].unique().tolist())
    sel_wilayah = st.sidebar.selectbox("Filter Wilayah", list_wilayah)
    
    df_filtered = df_main if sel_wilayah == "Seluruh Wilayah" else df_main[df_main['Wilayah'] == sel_wilayah]
    df_sub_filtered = data['sub'] if sel_wilayah == "Seluruh Wilayah" else data['sub'][data['sub']['Wilayah'] == sel_wilayah]

    # --- ROW 1: KPI CARDS (Berdasarkan Screenshot lo) ---
    st.title("📊 Disaster Impact Analysis: Child Voice")
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown(f"<div class='metric-card'><b>Total Responden</b><h2>{len(df_filtered)}</h2></div>", unsafe_allow_html=True)
    with c2:
        p_count = len(df_filtered[df_filtered['Jenis Kelamin'] == 'Perempuan'])
        st.markdown(f"<div class='metric-card' style='border-left-color: #E83E8C;'><b>Responden Perempuan</b><h2>{p_count}</h2></div>", unsafe_allow_html=True)
    with c3:
        l_count = len(df_filtered[df_filtered['Jenis Kelamin'] == 'Laki laki'])
        st.markdown(f"<div class='metric-card' style='border-left-color: #17A2B8;'><b>Responden Laki-laki</b><h2>{l_count}</h2></div>", unsafe_allow_html=True)
    with c4:
        neg_count = len(df_filtered[df_filtered['Sentimen'] == 'Negatif'])
        st.markdown(f"<div class='metric-card' style='border-left-color: #DC3545;'><b>Keluhan Negatif</b><h2>{neg_count}</h2></div>", unsafe_allow_html=True)

    st.write("##")

    # --- TABS ---
    tabs = st.tabs(["🏠 Ringkasan", "📚 Pendidikan", "🏥 Kesehatan", "🛡️ Perlindungan", "💰 Kesejahteraan", "🌟 Harapan"])

    # --- TAB 0: RINGKASAN (Donut & Bar) ---
    with tabs[0]:
        col_left, col_right = st.columns([1, 1])
        with col_left:
            st.subheader("Proporsi Dimensi Masalah")
            fig_donut = px.pie(data['dim_summary'], values='Jumlah', names='Dimensi', hole=.6,
                               color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_donut.update_layout(showlegend=True, margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_donut, use_container_width=True)
        
        with col_right:
            st.subheader("Sentimen per Dimensi")
            fig_sent = px.bar(data['sentimen'], x="Dimensi", y="Jumlah", color="Sentimen",
                              color_discrete_map={'Negatif':'#EF553B', 'Netral':'#636EFA', 'Positif':'#00CC96'},
                              barmode="group")
            st.plotly_chart(fig_sent, use_container_width=True)

    # --- TAB CUSTOM: PERLINDUNGAN (TREEMAP & BAR) ---
    with tabs[3]:
        st.subheader("Analisis Mendalam: Perlindungan Anak")
        df_p = df_sub_filtered[df_sub_filtered['Dimensi_Utama'].str.contains("Perlindungan", case=False)]
        
        if not df_p.empty:
            c_p1, c_p2 = st.columns([3, 2])
            with c_p1:
                # TREEMAP (Sesuai Screenshot lo)
                st.markdown("#### Hierarki Sub-Dimensi")
                fig_tree = px.treemap(df_p, path=['Dimensi_Utama', 'Sub_Dimensi'], 
                                      color='Sub_Dimensi', color_discrete_sequence=px.colors.qualitative.Safe)
                st.plotly_chart(fig_tree, use_container_width=True)
            with c_p2:
                # BAR CHART GENDER
                st.markdown("#### Isu Berdasarkan Gender")
                fig_bar_p = px.bar(df_p, x="Jenis Kelamin", color="Sub_Dimensi", barmode="stack")
                st.plotly_chart(fig_bar_p, use_container_width=True)
        else:
            st.info("Data Perlindungan tidak ditemukan untuk filter ini.")

    # --- FOOTER WORD CLOUD ---
    st.write("---")
    st.subheader("🗨️ Top Keywords")
    wc_data = dict(zip(data['word_freq']['Kata'], data['word_freq']['Frekuensi']))
    wc = WordCloud(width=1000, height=300, background_color="white", colormap="tab20").generate_from_frequencies(wc_data)
    fig_wc, ax = plt.subplots(figsize=(12, 4))
    ax.imshow(wc, interpolation="bilinear"); ax.axis("off")
    st.pyplot(fig_wc)

except Exception as e:
    st.error(f"Error loading dashboard: {e}")
