# 🏛️ İstanbul Tarihi Mekanlar Tur Optimizasyonu

**Karınca Kolonisi Algoritması (ACO) ile Minimum Mesafe Rotası**

---

## 👨‍🎓 Öğrenci Bilgileri

- **Ad:** Melih
- **Soyad:** Kılıç
- **Okul Numarası:** 2012721026
- **GitHub:** [https://github.com/Kiryue0/istanbul_tour_optimization](https://github.com/Kiryue0/istanbul_tour_optimization)

---
<img width="1868" height="1053" alt="image" src="https://github.com/user-attachments/assets/5234a336-6d78-47ce-b6f7-24e60594894c" />


Proje Hakkında

Bu proje, İstanbul'daki 50 tarihi mekan arasından kullanıcının seçtiği 15-30 mekan için **Karınca Kolonisi Optimizasyonu (ACO)** algoritması kullanarak en kısa turu hesaplayan bir Streamlit web uygulamasıdır.

### Amaç
- İstanbul'daki tarihi mekanlar arasında en kısa rotayı bulmak
- Google Maps API ile gerçek yol mesafelerini kullanmak
- ACO algoritması parametrelerini dinamik olarak ayarlayabilmek
- Sonuçları interaktif harita ve grafiklerle görselleştirmek

---

## Özellikler

###  Mekan Seçimi
- 50 tarihi mekan (Sultanahmet, Ayasofya, Topkapı, Galata Kulesi, vb.)
- Klavyeden arama yaparak seçim
- Minimum 15, maksimum 30 mekan
- Seçilen mekanları tablo halinde görüntüleme
- <img width="1868" height="1053" alt="image" src="https://github.com/user-attachments/assets/cf61d42d-0a93-42d5-9359-15db73b348a9" />
<img width="1468" height="883" alt="image" src="https://github.com/user-attachments/assets/431863ad-9606-4809-afe8-12e86a0ff0cc" />

### Optimizasyon Ekranı
<img width="1491" height="960" alt="image" src="https://github.com/user-attachments/assets/0db2e383-3e4e-4caf-9b07-5da355f4b111" />
<img width="1461" height="879" alt="image" src="https://github.com/user-attachments/assets/54093759-9927-4f05-acaf-57b0508c24c5" />



###  Google Maps API Entegrasyonu
- Gerçek koordinat bilgisi (Geocoding API)
- Gerçek yol mesafeleri (Distance Matrix API)
- API limit aşımında Haversine formülü ile fallback

###  Karınca Kolonisi Algoritması
**Ayarlanabilir Parametreler:**
- Karınca sayısı (10-100)
- İterasyon sayısı (50-500)
- Alpha (α) - Feromon önemi (0-5)
- Beta (β) - Mesafe önemi (0-5)
- Buharlaşma oranı (ρ) (0-1)
- <img width="330" height="758" alt="image" src="https://github.com/user-attachments/assets/08215ac8-bbca-4655-a854-01a67baf68e6" />


###
