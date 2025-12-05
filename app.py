"""
İstanbul Tarihi Mekanlar Tur Optimizasyonu
Karınca Kolonisi Algoritması (ACO) ile Rota Optimizasyonu
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from streamlit_folium import folium_static
import os
from dotenv import load_dotenv

# Kendi modüllerimizi import et
from aco_algorithm import AntColonyOptimizer
from utils import (
    ISTANBUL_LOCATIONS_ALL,
    DEFAULT_SELECTED_LOCATIONS,
    get_coordinates,
    create_distance_matrix,
    create_route_map,
    format_route_info,
    calculate_haversine_distance
)

# Sayfa konfigürasyonu
st.set_page_config(
    page_title="İstanbul Tur Optimizasyonu",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Düzeltmesi - Görünürlük için
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
    }
    div[data-testid="stMarkdownContainer"] p {
        color: white !important;
    }
    .stSelectbox label {
        color: white !important;
    }
    .stMultiSelect label {
        color: white !important;
    }
    h1, h2, h3, h4, h5, h6 {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# API KEY - Uygulama içine gömülü
load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')


def main():
    """Ana uygulama fonksiyonu"""
    
    # Başlık
    st.title("🏛️ İstanbul Tarihi Mekanlar Tur Optimizasyonu")
    st.subheader("Karınca Kolonisi Algoritması (ACO) ile Minimum Mesafe Rotası")
    
    # Sidebar - Parametreler
    with st.sidebar:
        st.header("⚙️ Algoritma Parametreleri")
        
        st.write("### 🐜 Karınca Kolonisi Ayarları")
        
        n_ants = st.slider(
            "Karınca Sayısı",
            min_value=10,
            max_value=100,
            value=30,
            step=5,
            help="Her iterasyonda kaç karınca çözüm arayacak"
        )
        
        n_iterations = st.slider(
            "İterasyon Sayısı",
            min_value=50,
            max_value=500,
            value=100,
            step=25,
            help="Algoritma kaç tur çalışacak"
        )
        
        st.write("### 🔬 ACO Parametreleri")
        
        alpha = st.slider(
            "Alpha (α) - Feromon Önemi",
            min_value=0.0,
            max_value=5.0,
            value=1.0,
            step=0.1,
            help="Feromon izi ne kadar önemli"
        )
        
        beta = st.slider(
            "Beta (β) - Mesafe Önemi",
            min_value=0.0,
            max_value=5.0,
            value=2.0,
            step=0.1,
            help="Mesafe bilgisi ne kadar önemli"
        )
        
        evaporation_rate = st.slider(
            "Buharlaşma Oranı (ρ)",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.05,
            help="Feromon buharlaşma hızı"
        )
    
    # Ana içerik - 2 sekme
    tab1, tab2 = st.tabs(["📍 Mekan Seçimi & Veri Hazırlama", "🚀 Optimizasyon"])
    
    # Session state'i başlat
    if 'selected_locations' not in st.session_state:
        st.session_state.selected_locations = DEFAULT_SELECTED_LOCATIONS.copy()
    if 'coordinates_df' not in st.session_state:
        st.session_state.coordinates_df = None
    if 'distance_matrix' not in st.session_state:
        st.session_state.distance_matrix = None
    if 'optimization_done' not in st.session_state:
        st.session_state.optimization_done = False
    
    # TAB 1: Mekan Seçimi + Koordinatlar + Mesafe Matrisi
    with tab1:
        st.header("🏛️ İstanbul'daki Tarihi Mekanlar")
        
        st.info("📌 50 mekan içinden en az 15, en fazla 30 mekan seçmelisiniz. Klavyeden yazarak arama yapabilirsiniz.")
        
        # Mekan seçimi
        selected = st.multiselect(
            "🔍 Gezilecek Mekanları Seçin (Klavyeden yazarak arayabilirsiniz):",
            options=list(ISTANBUL_LOCATIONS_ALL.keys()),
            default=st.session_state.selected_locations,
            help="Yazmaya başladığınızda otomatik filtreleme yapılır. Ctrl/Cmd ile çoklu seçim yapabilirsiniz.",
            placeholder="Mekan adı yazın..."
        )
        
        # Seçim kontrolü
        if len(selected) == 0:
            st.warning("⚠️ Lütfen en az 15 mekan seçin!")
        elif len(selected) < 15:
            st.warning(f"⚠️ En az 15 mekan seçmelisiniz! Şu an {len(selected)} mekan seçildi, {15-len(selected)} mekan daha eklemelisiniz.")
        elif len(selected) > 30:
            st.warning("⚠️ En fazla 30 mekan seçebilirsiniz!")
        else:
            st.success(f"✅ {len(selected)} mekan seçildi")
            st.session_state.selected_locations = selected
            
            # Seçili mekanları tablo olarak göster
            st.write("### 📋 Seçili Mekanlar")
            selected_df = pd.DataFrame([
                {"Sıra": i+1, "Mekan": name, "Adres": ISTANBUL_LOCATIONS_ALL[name]}
                for i, name in enumerate(selected)
            ])
            st.dataframe(selected_df, use_container_width=True, hide_index=True)
            
            # API Key kontrolü
            if not GOOGLE_MAPS_API_KEY:
                st.error("❌ Google Maps API anahtarı bulunamadı!")
                st.info("""
                **Çözüm:**
                1. `.env` dosyasını oluşturun (proje klasöründe)
                2. İçine şunu yazın: `GOOGLE_MAPS_API_KEY=your_api_key`
                3. Uygulamayı yeniden başlatın
                """)
            else:
                st.write("---")
                
                # ADIM 1: Koordinatları Al
                st.write("### 📍 Adım 1: Koordinatları Al")
                
                selected_locations_dict = {k: ISTANBUL_LOCATIONS_ALL[k] for k in st.session_state.selected_locations}
                
                if st.button("📍 Koordinatları Al (Google Maps API)", use_container_width=True, type="primary", key="coord_btn"):
                    with st.spinner("Google Maps API'den koordinatlar alınıyor..."):
                        try:
                            st.session_state.coordinates_df = get_coordinates(GOOGLE_MAPS_API_KEY, selected_locations_dict)
                            
                            if len(st.session_state.coordinates_df) == 0:
                                st.error("❌ Hiçbir mekan koordinatı alınamadı! API key'inizi kontrol edin.")
                            else:
                                st.success(f"✅ {len(st.session_state.coordinates_df)} mekan koordinatı Google Maps'ten alındı!")
                                
                        except Exception as e:
                            st.error(f"❌ API hatası: {str(e)}")
                            st.info("API key'inizi ve internet bağlantınızı kontrol edin.")
                
                # Koordinatları göster
                if st.session_state.coordinates_df is not None:
                    st.write("#### 📍 Mekan Koordinatları:")
                    coords_display = st.session_state.coordinates_df[['name', 'lat', 'lng']].copy()
                    coords_display.columns = ['Mekan', 'Enlem', 'Boylam']
                    coords_display.index = range(1, len(coords_display) + 1)
                    st.dataframe(coords_display, use_container_width=True)
                    
                    st.write("---")
                    
                    st.write("---")
                    
                    # ADIM 2: Mesafe Matrisi
                    st.write("### 📊 Adım 2: Mesafe Matrisini Oluştur")
                    
                    if st.button("📊 Mesafe Matrisini Oluştur (Google Maps API)", use_container_width=True, type="primary", key="dist_btn"):
                        with st.spinner("Google Maps API'den gerçek yol mesafeleri hesaplanıyor... (Bu işlem biraz zaman alabilir)"):
                            try:
                                st.session_state.distance_matrix, info = create_distance_matrix(
                                    GOOGLE_MAPS_API_KEY,
                                    st.session_state.coordinates_df
                                )
                                
                                if info['status'] == 'OK':
                                    st.success(f"✅ Gerçek yol mesafeleri Google Maps'ten alındı! ({info['api_calls']} API çağrısı)")
                                else:
                                    st.warning(f"⚠️ {info['status']} - Kuş uçuşu mesafeler kullanıldı")
                                
                            except Exception as e:
                                st.error(f"❌ API hatası: {str(e)}")
                                st.info("💡 Fallback: Kuş uçuşu mesafeler (Haversine) kullanılıyor...")
                                
                                # Fallback - Haversine
                                n = len(st.session_state.coordinates_df)
                                st.session_state.distance_matrix = np.zeros((n, n))
                                for i in range(n):
                                    for j in range(n):
                                        if i != j:
                                            st.session_state.distance_matrix[i][j] = calculate_haversine_distance(
                                                st.session_state.coordinates_df.iloc[i]['lat'],
                                                st.session_state.coordinates_df.iloc[i]['lng'],
                                                st.session_state.coordinates_df.iloc[j]['lat'],
                                                st.session_state.coordinates_df.iloc[j]['lng']
                                            )
                                st.success("✅ Kuş uçuşu mesafeler hesaplandı!")
                    
                            # Mesafe matrisini göster - SADECE TABLO
                    if st.session_state.distance_matrix is not None and st.session_state.distance_matrix.sum() > 0:
                        st.write("---")
                        st.write("### 📊 Mesafe Matrisi (km)")
                        
                        # DataFrame olarak göster
                        df_matrix = pd.DataFrame(
                            st.session_state.distance_matrix,
                            columns=st.session_state.coordinates_df['name'],
                            index=st.session_state.coordinates_df['name']
                        )
                        
                        # Formatla (2 ondalık basamak)
                        st.dataframe(
                            df_matrix.round(2).style.background_gradient(cmap='RdYlGn_r', axis=None),
                            use_container_width=True,
                            height=min(600, len(df_matrix) * 35 + 38)
                        )
                        
                        # Özet bilgiler
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            non_zero = st.session_state.distance_matrix[st.session_state.distance_matrix > 0]
                            st.metric("📏 Ortalama Mesafe", f"{non_zero.mean():.2f} km")
                        with col2:
                            st.metric("📉 En Kısa Mesafe", f"{non_zero.min():.2f} km")
                        with col3:
                            st.metric("📈 En Uzun Mesafe", f"{non_zero.max():.2f} km")
                        
                        st.success("✅ Veri hazırlama tamamlandı! Şimdi 'Optimizasyon' sekmesine geçebilirsiniz.")

    # TAB 2: Optimizasyon
    with tab2:
        st.header("🚀 Karınca Kolonisi Optimizasyonu")
        
        # Veri kontrolü
        if st.session_state.distance_matrix is None:
            st.error("❌ Lütfen önce 'Mekan Seçimi & Veri Hazırlama' sekmesinden koordinatları ve mesafe matrisini oluşturun!")
            return
        
        if len(st.session_state.coordinates_df) < 15:
            st.error(f"❌ En az 15 mekan koordinatı gerekli! Şu an {len(st.session_state.coordinates_df)} mekan var.")
            return
        
        # ADIM 3: Optimizasyon
        st.write("### 🚀 Adım 3: Rotayı Optimize Et")
        
        if st.button("🚀 Rotayı Optimize Et (ACO)", use_container_width=True, type="primary", key="opt_btn"):
            with st.spinner(f"🐜 {n_ants} karınca, {n_iterations} iterasyon boyunca en iyi rotayı arıyor..."):
                # ACO algoritması
                aco = AntColonyOptimizer(
                    distance_matrix=st.session_state.distance_matrix,
                    n_ants=n_ants,
                    n_iterations=n_iterations,
                    alpha=alpha,
                    beta=beta,
                    evaporation_rate=evaporation_rate
                )
                
                progress_bar = st.progress(0)
                result = aco.optimize()
                progress_bar.progress(100)
                
                # Sonuçları kaydet
                st.session_state.best_path = result['best_path']
                st.session_state.best_distance = result['best_distance']
                st.session_state.distance_history = result['distance_history']
                st.session_state.optimization_done = True
            
            st.success(f"✅ Optimizasyon tamamlandı! En kısa mesafe: {st.session_state.best_distance:.2f} km")
        
        # SONUÇLAR
        if st.session_state.optimization_done:
            st.write("---")
            st.write("## 📊 Optimizasyon Sonuçları")
            
            # Metrikler
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🏁 Toplam Mesafe", f"{st.session_state.best_distance:.2f} km")
            with col2:
                st.metric("📍 Ziyaret Edilen Mekan", f"{len(st.session_state.best_path)-1}")
            with col3:
                avg_distance = st.session_state.best_distance / (len(st.session_state.best_path)-1)
                st.metric("📏 Ortalama Mekan Arası", f"{avg_distance:.2f} km")
            
            st.write("---")
            
            # Harita ve Rota
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write("### 🗺️ Optimum Rota Haritası")
                route_map = create_route_map(
                    st.session_state.coordinates_df,
                    st.session_state.best_path
                )
                folium_static(route_map, width=700, height=500)
            
            with col2:
                st.write("### 📋 Rota Detayları")
                for idx, city_idx in enumerate(st.session_state.best_path[:-1], 1):
                    name = st.session_state.coordinates_df.iloc[city_idx]['name']
                    if idx == 1:
                        st.write(f"🚀 **{idx}. {name}** (Başlangıç)")
                    elif idx == len(st.session_state.best_path)-1:
                        st.write(f"🏁 **{idx}. {name}** (Bitiş)")
                    else:
                        st.write(f"📍 {idx}. {name}")
            
            # Performans grafiği
            st.write("---")
            st.write("### 📈 Algoritma Performansı")
            
            fig, ax = plt.subplots(figsize=(12, 5))
            ax.plot(st.session_state.distance_history, linewidth=2.5, color='#1f77b4')
            ax.fill_between(range(len(st.session_state.distance_history)), 
                           st.session_state.distance_history, 
                           alpha=0.3, color='#1f77b4')
            ax.set_xlabel('İterasyon', fontsize=13, fontweight='bold')
            ax.set_ylabel('En İyi Mesafe (km)', fontsize=13, fontweight='bold')
            ax.set_title('ACO - İterasyon Başına En İyi Mesafe', fontsize=15, fontweight='bold')
            ax.grid(True, alpha=0.3, linestyle='--')
            
            # Arka plan rengi
            fig.patch.set_facecolor('#0e1117')
            ax.set_facecolor('#0e1117')
            ax.tick_params(colors='white')
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
            ax.title.set_color('white')
            
            st.pyplot(fig)
            
            # İstatistikler
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📉 Başlangıç", f"{st.session_state.distance_history[0]:.2f} km")
            with col2:
                st.metric("🎯 Final", f"{st.session_state.distance_history[-1]:.2f} km")
            with col3:
                improvement = ((st.session_state.distance_history[0] - st.session_state.distance_history[-1]) / 
                             st.session_state.distance_history[0] * 100)
                st.metric("📊 İyileştirme", f"{improvement:.1f}%")
            with col4:
                st.metric("🔄 İterasyon", len(st.session_state.distance_history))


if __name__ == "__main__":
    main()