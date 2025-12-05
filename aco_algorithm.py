"""
Karınca Kolonisi Algoritması (Ant Colony Optimization - ACO)
Gezgin Satıcı Problemi (TSP) için optimize edilmiş versiyon
"""

import numpy as np
import random
from typing import List, Tuple, Dict


class AntColonyOptimizer:
    """
    Karınca Kolonisi Optimizasyon Algoritması
    
    Parametreler:
    - distance_matrix: Şehirler arası mesafe matrisi
    - n_ants: Karınca sayısı
    - n_iterations: İterasyon sayısı
    - alpha: Feromon önem katsayısı (α)
    - beta: Mesafe önem katsayısı (β)
    - evaporation_rate: Feromon buharlaşma oranı (ρ)
    - Q: Feromon yoğunluğu sabiti
    """
    
    def __init__(
        self,
        distance_matrix: np.ndarray,
        n_ants: int = 20,
        n_iterations: int = 100,
        alpha: float = 1.0,
        beta: float = 2.0,
        evaporation_rate: float = 0.5,
        Q: float = 100
    ):
        self.distance_matrix = distance_matrix
        self.n_cities = len(distance_matrix)
        self.n_ants = n_ants
        self.n_iterations = n_iterations
        self.alpha = alpha
        self.beta = beta
        self.evaporation_rate = evaporation_rate
        self.Q = Q
        
        # Feromon matrisini başlat (başlangıçta tüm yollar eşit feromon)
        self.pheromone = np.ones((self.n_cities, self.n_cities)) / self.n_cities
        
        # En iyi sonuçları sakla
        self.best_path = None
        self.best_distance = float('inf')
        self.distance_history = []
        
    def _calculate_probabilities(self, current_city: int, unvisited: List[int]) -> np.ndarray:
        """
        Bir sonraki şehre gitme olasılıklarını hesapla
        
        Formül: P(i,j) = [τ(i,j)^α * η(i,j)^β] / Σ[τ(i,k)^α * η(i,k)^β]
        τ: feromon yoğunluğu
        η: görünürlük (1/mesafe)
        """
        pheromone_values = np.array([self.pheromone[current_city][j] for j in unvisited])
        visibility = np.array([1.0 / self.distance_matrix[current_city][j] 
                              if self.distance_matrix[current_city][j] > 0 else 0 
                              for j in unvisited])
        
        # Feromon ve görünürlük katkılarını hesapla
        pheromone_contribution = np.power(pheromone_values, self.alpha)
        visibility_contribution = np.power(visibility, self.beta)
        
        # Olasılıkları hesapla
        probabilities = pheromone_contribution * visibility_contribution
        probabilities_sum = probabilities.sum()
        
        if probabilities_sum == 0:
            # Eğer tüm olasılıklar 0 ise, uniform dağılım kullan
            probabilities = np.ones(len(unvisited)) / len(unvisited)
        else:
            probabilities = probabilities / probabilities_sum
            
        return probabilities
    
    def _construct_solution(self) -> Tuple[List[int], float]:
        """
        Bir karınca için çözüm oluştur (rastgele başlangıç şehrinden)
        """
        # Rastgele başlangıç şehri seç
        start_city = random.randint(0, self.n_cities - 1)
        path = [start_city]
        unvisited = list(range(self.n_cities))
        unvisited.remove(start_city)
        
        current_city = start_city
        
        # Tüm şehirler ziyaret edilene kadar devam et
        while unvisited:
            probabilities = self._calculate_probabilities(current_city, unvisited)
            
            # Olasılıklara göre bir sonraki şehri seç
            next_city_idx = np.random.choice(len(unvisited), p=probabilities)
            next_city = unvisited[next_city_idx]
            
            path.append(next_city)
            unvisited.remove(next_city)
            current_city = next_city
        
        # Başlangıç şehrine geri dön (kapalı tur)
        path.append(start_city)
        
        # Toplam mesafeyi hesapla
        total_distance = sum(self.distance_matrix[path[i]][path[i+1]] 
                           for i in range(len(path) - 1))
        
        return path, total_distance
    
    def _update_pheromones(self, all_paths: List[List[int]], all_distances: List[float]):
        """
        Feromon matrisini güncelle
        
        1. Buharlaşma: τ(i,j) = (1-ρ) * τ(i,j)
        2. Feromon ekleme: τ(i,j) = τ(i,j) + Σ(Q/L_k)
        """
        # Buharlaşma
        self.pheromone *= (1 - self.evaporation_rate)
        
        # Her karıncanın bıraktığı feromonları ekle
        for path, distance in zip(all_paths, all_distances):
            feromon_deposit = self.Q / distance
            for i in range(len(path) - 1):
                self.pheromone[path[i]][path[i+1]] += feromon_deposit
                self.pheromone[path[i+1]][path[i]] += feromon_deposit  # Simetrik
    
    def optimize(self) -> Dict:
        """
        ACO algoritmasını çalıştır ve en iyi rotayı bul
        
        Returns:
            dict: En iyi yol, mesafe ve iterasyon geçmişi
        """
        print(f"🐜 ACO Algoritması Başlatılıyor...")
        print(f"   Karınca sayısı: {self.n_ants}")
        print(f"   İterasyon sayısı: {self.n_iterations}")
        print(f"   Alpha (α): {self.alpha}, Beta (β): {self.beta}")
        print(f"   Buharlaşma oranı (ρ): {self.evaporation_rate}")
        
        for iteration in range(self.n_iterations):
            all_paths = []
            all_distances = []
            
            # Her karınca için çözüm oluştur
            for ant in range(self.n_ants):
                path, distance = self._construct_solution()
                all_paths.append(path)
                all_distances.append(distance)
                
                # En iyi çözümü güncelle
                if distance < self.best_distance:
                    self.best_distance = distance
                    self.best_path = path
            
            # Feromonları güncelle
            self._update_pheromones(all_paths, all_distances)
            
            # Bu iterasyondaki en iyi mesafeyi kaydet
            iteration_best = min(all_distances)
            self.distance_history.append(self.best_distance)
            
            # İlerleme raporu
            if (iteration + 1) % 10 == 0 or iteration == 0:
                print(f"   İterasyon {iteration + 1}/{self.n_iterations}: "
                      f"En iyi mesafe = {self.best_distance:.2f} km")
        
        print(f"\n✅ Optimizasyon tamamlandı!")
        print(f"   En kısa mesafe: {self.best_distance:.2f} km")
        
        return {
            'best_path': self.best_path,
            'best_distance': self.best_distance,
            'distance_history': self.distance_history
        }
    
    def get_path_with_names(self, location_names: List[str]) -> List[str]:
        """
        Şehir indekslerini isimlerine çevir
        """
        if self.best_path is None:
            return []
        return [location_names[i] for i in self.best_path]