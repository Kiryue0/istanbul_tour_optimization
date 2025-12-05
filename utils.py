"""
Yardımcı Fonksiyonlar
- Google Maps API entegrasyonu
- Mesafe matrisi oluşturma
- Harita görselleştirme
"""

import googlemaps
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple
import folium
from datetime import datetime


# İstanbul'daki 50 Tarihi Mekan
ISTANBUL_LOCATIONS_ALL = {
    "Sultanahmet Camii": "Sultanahmet Camii, Fatih, İstanbul",
    "Ayasofya": "Ayasofya, Sultanahmet, Fatih, İstanbul",
    "Topkapı Sarayı": "Topkapı Sarayı, Fatih, İstanbul",
    "Yerebatan Sarnıcı": "Yerebatan Sarnıcı, Alemdar, Fatih, İstanbul",
    "Kapalıçarşı": "Kapalıçarşı, Beyazıt, Fatih, İstanbul",
    "Süleymaniye Camii": "Süleymaniye Camii, Fatih, İstanbul",
    "Galata Kulesi": "Galata Kulesi, Beyoğlu, İstanbul",
    "Dolmabahçe Sarayı": "Dolmabahçe Sarayı, Beşiktaş, İstanbul",
    "Beylerbeyi Sarayı": "Beylerbeyi Sarayı, Üsküdar, İstanbul",
    "Rumeli Hisarı": "Rumeli Hisarı, Sarıyer, İstanbul",
    "Yıldız Sarayı": "Yıldız Sarayı, Beşiktaş, İstanbul",
    "Kariye Müzesi": "Kariye Müzesi, Fatih, İstanbul",
    "Eyüp Sultan Camii": "Eyüp Sultan Camii, Eyüpsultan, İstanbul",
    "Çamlıca Kulesi": "Çamlıca Kulesi, Üsküdar, İstanbul",
    "Kız Kulesi": "Kız Kulesi, Üsküdar, İstanbul",
    "İstiklal Caddesi": "İstiklal Caddesi, Beyoğlu, İstanbul",
    "Taksim Meydanı": "Taksim Meydanı, Beyoğlu, İstanbul",
    "Ortaköy Camii": "Ortaköy Camii, Beşiktaş, İstanbul",
    "Çırağan Sarayı": "Çırağan Sarayı, Beşiktaş, İstanbul",
    "Küçüksu Kasrı": "Küçüksu Kasrı, Beykoz, İstanbul",
    "Anadolu Hisarı": "Anadolu Hisarı, Beykoz, İstanbul",
    "Sarayburnu": "Sarayburnu, Fatih, İstanbul",
    "Eminönü": "Eminönü, Fatih, İstanbul",
    "Mısır Çarşısı": "Mısır Çarşısı, Eminönü, Fatih, İstanbul",
    "Rüstem Paşa Camii": "Rüstem Paşa Camii, Eminönü, Fatih, İstanbul",
    "Beyazıt Kulesi": "Beyazıt Kulesi, Fatih, İstanbul",
    "Şehzade Camii": "Şehzade Camii, Fatih, İstanbul",
    "Fatih Camii": "Fatih Camii, Fatih, İstanbul",
    "Selimiye Camii": "Selimiye Camii, Üsküdar, İstanbul",
    "Mihrimah Sultan Camii": "Mihrimah Sultan Camii, Üsküdar, İstanbul",
    "Sokollu Mehmet Paşa Camii": "Sokollu Mehmet Paşa Camii, Kadırga, Fatih, İstanbul",
    "Nuruosmaniye Camii": "Nuruosmaniye Camii, Çemberlitaş, Fatih, İstanbul",
    "Laleli Camii": "Laleli Camii, Fatih, İstanbul",
    "Valide Sultan Camii": "Valide Sultan Camii, Üsküdar, İstanbul",
    "Yeni Cami": "Yeni Cami, Eminönü, Fatih, İstanbul",
    "Pierre Loti Tepesi": "Pierre Loti Tepesi, Eyüpsultan, İstanbul",
    "Miniatürk": "Miniatürk, Beyoğlu, İstanbul",
    "Rahmi M. Koç Müzesi": "Rahmi M. Koç Müzesi, Beyoğlu, İstanbul",
    "İstanbul Arkeoloji Müzesi": "İstanbul Arkeoloji Müzesi, Fatih, İstanbul",
    "Türk İslam Eserleri Müzesi": "Türk İslam Eserleri Müzesi, Sultanahmet, Fatih, İstanbul",
    "Pera Müzesi": "Pera Müzesi, Beyoğlu, İstanbul",
    "Boğaziçi Köprüsü": "Boğaziçi Köprüsü, İstanbul",
    "Fatih Sultan Mehmet Köprüsü": "Fatih Sultan Mehmet Köprüsü, İstanbul",
    "Yavuz Sultan Selim Köprüsü": "Yavuz Sultan Selim Köprüsü, İstanbul",
    "Balat": "Balat, Fatih, İstanbul",
    "Fener": "Fener, Fatih, İstanbul",
    "Patrikhane": "Patrikhane, Fener, Fatih, İstanbul",
    "Bulgar Kilisesi": "Bulgar Kilisesi, Balat, Fatih, İstanbul",
    "Yedikule Hisarı": "Yedikule Hisarı, Fatih, İstanbul",
    "Tekfur Sarayı": "Tekfur Sarayı, Fatih, İstanbul"
}

# Varsayılan seçili mekanlar - BAŞLANGIÇTa BOŞ
DEFAULT_SELECTED_LOCATIONS = []


def get_coordinates(api_key: str, locations: Dict[str, str]) -> pd.DataFrame:
    """
    Google Maps API kullanarak lokasyonların koordinatlarını al
    
    Args:
        api_key: Google Maps API anahtarı
        locations: Lokasyon isim-adres sözlüğü
    
    Returns:
        DataFrame: İsim, adres, enlem, boylam bilgileri
    """
    gmaps = googlemaps.Client(key=api_key)
    
    data = []
    for name, address in locations.items():
        try:
            geocode_result = gmaps.geocode(address)
            if geocode_result:
                location = geocode_result[0]['geometry']['location']
                data.append({
                    'name': name,
                    'address': address,
                    'lat': location['lat'],
                    'lng': location['lng']
                })
                print(f"✓ {name} koordinatları alındı")
            else:
                print(f"✗ {name} için sonuç bulunamadı")
        except Exception as e:
            print(f"✗ {name} için hata: {e}")
    
    return pd.DataFrame(data)


def create_distance_matrix(api_key: str, coordinates_df: pd.DataFrame) -> Tuple[np.ndarray, Dict]:
    """
    Google Maps Distance Matrix API kullanarak mesafe matrisi oluştur
    API limitini aşmamak için küçük parçalara böler
    
    Args:
        api_key: Google Maps API anahtarı
        coordinates_df: Koordinatlar DataFrame'i
    
    Returns:
        tuple: (mesafe matrisi, bilgi sözlüğü)
    """
    gmaps = googlemaps.Client(key=api_key)
    n = len(coordinates_df)
    distance_matrix = np.zeros((n, n))
    
    print(f"\n📊 Mesafe matrisi oluşturuluyor ({n}x{n})...")
    
    # Koordinatları liste olarak hazırla
    origins = [(row['lat'], row['lng']) for _, row in coordinates_df.iterrows()]
    
    # API limitini aşmamak için KÜÇÜK PARÇALARA BÖL
    # Ücretsiz limit: 100 element per request
    # 10x10 = 100 element (güvenli)
    
    BATCH_SIZE = 10  # Her seferinde max 10 konum
    total_api_calls = 0
    
    try:
        # Matrisi parça parça doldur
        for i in range(0, n, BATCH_SIZE):
            end_i = min(i + BATCH_SIZE, n)
            origins_batch = origins[i:end_i]
            
            for j in range(0, n, BATCH_SIZE):
                end_j = min(j + BATCH_SIZE, n)
                destinations_batch = origins[j:end_j]
                
                print(f"  API çağrısı: [{i}:{end_i}] x [{j}:{end_j}] = {len(origins_batch)}x{len(destinations_batch)} element")
                
                try:
                    result = gmaps.distance_matrix(
                        origins=origins_batch,
                        destinations=destinations_batch,
                        mode='driving',
                        departure_time=datetime.now()
                    )
                    
                    total_api_calls += 1
                    
                    # Sonuçları matrise yerleştir
                    for row_idx, row_data in enumerate(result['rows']):
                        for col_idx, element in enumerate(row_data['elements']):
                            matrix_i = i + row_idx
                            matrix_j = j + col_idx
                            
                            if element['status'] == 'OK':
                                distance_matrix[matrix_i][matrix_j] = element['distance']['value'] / 1000.0
                            else:
                                # API'den mesafe alınamazsa Haversine kullan
                                if matrix_i != matrix_j:
                                    distance_matrix[matrix_i][matrix_j] = calculate_haversine_distance(
                                        coordinates_df.iloc[matrix_i]['lat'],
                                        coordinates_df.iloc[matrix_i]['lng'],
                                        coordinates_df.iloc[matrix_j]['lat'],
                                        coordinates_df.iloc[matrix_j]['lng']
                                    )
                
                except Exception as e:
                    print(f"  ⚠️ Parça [{i}:{end_i}]x[{j}:{end_j}] hatası: {e}")
                    # Hata durumunda bu parça için Haversine kullan
                    for row_idx in range(len(origins_batch)):
                        for col_idx in range(len(destinations_batch)):
                            matrix_i = i + row_idx
                            matrix_j = j + col_idx
                            if matrix_i != matrix_j:
                                distance_matrix[matrix_i][matrix_j] = calculate_haversine_distance(
                                    coordinates_df.iloc[matrix_i]['lat'],
                                    coordinates_df.iloc[matrix_i]['lng'],
                                    coordinates_df.iloc[matrix_j]['lat'],
                                    coordinates_df.iloc[matrix_j]['lng']
                                )
        
        print(f"✓ Mesafe matrisi başarıyla oluşturuldu ({total_api_calls} API çağrısı)")
        
        info = {
            'total_locations': n,
            'status': 'OK',
            'api_calls': total_api_calls
        }
        
        return distance_matrix, info
        
    except Exception as e:
        print(f"⚠️ Genel API hatası: {e}")
        print("Tüm matris için Haversine kullanılıyor...")
        
        # Tam hata durumunda tüm matris için Haversine
        for i in range(n):
            for j in range(n):
                if i != j:
                    distance_matrix[i][j] = calculate_haversine_distance(
                        coordinates_df.iloc[i]['lat'],
                        coordinates_df.iloc[i]['lng'],
                        coordinates_df.iloc[j]['lat'],
                        coordinates_df.iloc[j]['lng']
                    )
        
        info = {
            'total_locations': n,
            'status': 'FALLBACK_HAVERSINE',
            'api_calls': 0
        }
        
        return distance_matrix, info


def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    İki koordinat arasındaki kuş uçuşu mesafeyi hesapla (Haversine formülü)
    
    Returns:
        float: Mesafe (km)
    """
    R = 6371  # Dünya'nın yarıçapı (km)
    
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    
    return R * c


def create_route_map(coordinates_df: pd.DataFrame, route: List[int], 
                     center_lat: float = 41.0082, center_lng: float = 28.9784) -> folium.Map:
    """
    Optimum rotayı harita üzerinde görselleştir
    
    Args:
        coordinates_df: Koordinatlar DataFrame'i
        route: Rota (şehir indeksleri listesi)
        center_lat: Harita merkez enlem
        center_lng: Harita merkez boylam
    
    Returns:
        folium.Map: Görselleştirilmiş harita
    """
    # Haritayı oluştur (İstanbul merkez)
    m = folium.Map(
        location=[center_lat, center_lng],
        zoom_start=11,
        tiles='OpenStreetMap'
    )
    
    # Rota üzerindeki her nokta için marker ekle
    for idx, city_idx in enumerate(route[:-1]):  # Son nokta başlangıçla aynı
        row = coordinates_df.iloc[city_idx]
        
        # Başlangıç noktası yeşil, diğerleri mavi, bitiş kırmızı
        if idx == 0:
            color = 'green'
            icon = 'play'
            popup_text = f"🚀 BAŞLANGIÇ: {row['name']}"
        elif idx == len(route) - 2:
            color = 'red'
            icon = 'stop'
            popup_text = f"🏁 BİTİŞ: {row['name']}"
        else:
            color = 'blue'
            icon = 'info-sign'
            popup_text = f"{idx}. {row['name']}"
        
        folium.Marker(
            location=[row['lat'], row['lng']],
            popup=folium.Popup(popup_text, max_width=200),
            tooltip=row['name'],
            icon=folium.Icon(color=color, icon=icon)
        ).add_to(m)
    
    # Rota çizgisini ekle
    route_coordinates = [
        [coordinates_df.iloc[i]['lat'], coordinates_df.iloc[i]['lng']] 
        for i in route
    ]
    
    folium.PolyLine(
        route_coordinates,
        color='red',
        weight=3,
        opacity=0.8,
        popup='Optimum Rota'
    ).add_to(m)
    
    return m


def format_route_info(coordinates_df: pd.DataFrame, route: List[int], 
                     total_distance: float) -> str:
    """
    Rota bilgilerini formatla
    
    Returns:
        str: Formatlanmış rota bilgisi
    """
    info = f"### 🗺️ Optimum Rota Detayları\n\n"
    info += f"**Toplam Mesafe:** {total_distance:.2f} km\n\n"
    info += "**Rota Sırası:**\n\n"
    
    for idx, city_idx in enumerate(route[:-1], 1):
        name = coordinates_df.iloc[city_idx]['name']
        info += f"{idx}. {name}\n"
    
    return info