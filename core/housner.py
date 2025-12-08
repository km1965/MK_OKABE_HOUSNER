"""
Méthode de Housner pour la poussée hydrodynamique
Décomposition en pressions impulsive et convective
"""
import math

class WaterParameters:
    def __init__(self, hw: float, L: float, gamma_w: float = 10.0):
        """
        Paramètres de l'eau
        
        :param hw: Hauteur d'eau (m)
        :param L: Largeur du réservoir (m)
        :param gamma_w: Poids volumique de l'eau (kN/m³)
        """
        self.hw = hw
        self.L = L
        self.gamma_w = gamma_w
        self.rho_w = gamma_w / 9.81  # Masse volumique (t/m³)
        self.g = 9.81  # Accélération gravitationnelle (m/s²)

class Housner:
    """
    Méthode de Housner pour réservoir rectangulaire
    Référence: Housner, G.W. (1963) - "The dynamic behavior of water tanks"
    """
    
    @staticmethod
    def calculate_impulsive_mass(water: WaterParameters) -> float:
        """
        Calcule la masse impulsive par unité de longueur (t/m)
        
        mi = ρw × L × hw × tanh(0.866 × L/hw)
        
        :param water: Paramètres de l'eau
        :return: Masse impulsive mi (t/m)
        """
        ratio = water.L / water.hw
        tanh_term = math.tanh(0.866 * ratio)
        mi = water.rho_w * water.L * water.hw * tanh_term
        return mi
    
    @staticmethod
    def calculate_convective_mass(water: WaterParameters) -> float:
        """
        Calcule la masse convective par unité de longueur (t/m)
        
        mc = ρw × L × hw × 0.230 × (L/hw) × tanh(3.16 × hw/L)
        
        :param water: Paramètres de l'eau
        :return: Masse convective mc (t/m)
        """
        ratio_L_hw = water.L / water.hw
        ratio_hw_L = water.hw / water.L
        tanh_term = math.tanh(3.16 * ratio_hw_L)
        mc = water.rho_w * water.L * water.hw * 0.230 * ratio_L_hw * tanh_term
        return mc
    
    @staticmethod
    def calculate_convective_period(water: WaterParameters) -> float:
        """
        Calcule la période de ballottement (sloshing) Tc (s)
        
        Tc = 2π √(L / (2g × tanh(3.16 × hw/L)))
        
        :param water: Paramètres de l'eau
        :return: Période convective Tc (s)
        """
        ratio_hw_L = water.hw / water.L
        tanh_term = math.tanh(3.16 * ratio_hw_L)
        
        if tanh_term == 0:
            return float('inf')
        
        Tc = 2 * math.pi * math.sqrt(water.L / (2 * water.g * tanh_term))
        return Tc
    
    @staticmethod
    def calculate_impulsive_pressure(water: WaterParameters, Ai: float) -> float:
        """
        Calcule la pression impulsive Pi (kN/m)
        
        Pi = (7/12) × (Ai/g) × γw × hw²
        
        :param water: Paramètres de l'eau
        :param Ai: Accélération spectrale impulsive (m/s²)
        :return: Pression impulsive Pi (kN/m)
        """
        Pi = (7.0/12.0) * (Ai / water.g) * water.gamma_w * (water.hw ** 2)
        return Pi
    
    @staticmethod
    def calculate_convective_pressure(water: WaterParameters, Ac: float) -> float:
        """
        Calcule la pression convective Pc (kN/m)
        
        Formule simplifiée pour réservoir rectangulaire:
        Pc = 0.55 × (Ac/g) × γw × hw²
        
        :param water: Paramètres de l'eau
        :param Ac: Accélération spectrale convective (m/s²)
        :return: Pression convective Pc (kN/m)
        """
        # Formule simplifiée conservatrice
        Pc = 0.55 * (Ac / water.g) * water.gamma_w * (water.hw ** 2)
        return Pc
    
    @staticmethod
    def calculate_total_pressure(Pi: float, Pc: float, method: str = "SRSS") -> float:
        """
        Combine les pressions impulsive et convective
        
        SRSS: Pw = √(Pi² + Pc²)
        Sommation: Pw = Pi + Pc (conservatif)
        
        :param Pi: Pression impulsive (kN/m)
        :param Pc: Pression convective (kN/m)
        :param method: "SRSS" ou "SUM"
        :return: Pression totale Pw (kN/m)
        """
        if method == "SRSS":
            Pw = math.sqrt(Pi**2 + Pc**2)
        else:  # SUM
            Pw = Pi + Pc
        
        return Pw
    
    @staticmethod
    def get_impulsive_height(water: WaterParameters) -> float:
        """
        Hauteur d'application de la pression impulsive depuis le fond
        
        Pour réservoir rectangulaire: hi ≈ 0.375 × hw
        
        :param water: Paramètres de l'eau
        :return: Hauteur hi (m)
        """
        return 0.375 * water.hw
    
    @staticmethod
    def get_convective_height(water: WaterParameters) -> float:
        """
        Hauteur d'application de la pression convective depuis le fond
        
        Pour réservoir rectangulaire: hc ≈ 0.75 × hw (approximation)
        Valeur plus précise dépend de hw/L
        
        :param water: Paramètres de l'eau
        :return: Hauteur hc (m)
        """
        # Formule approximative
        ratio = water.hw / water.L
        
        if ratio < 0.5:
            hc = 0.8 * water.hw
        elif ratio < 1.0:
            hc = 0.75 * water.hw
        else:
            hc = 0.7 * water.hw
        
        return hc
    
    @staticmethod
    def calculate_impulsive_moment(Pi: float, water: WaterParameters) -> float:
        """
        Calcule le moment de la pression impulsive par rapport à la base
        
        Mi = Pi × hi
        
        :param Pi: Pression impulsive (kN/m)
        :param water: Paramètres de l'eau
        :return: Moment Mi (kN·m/m)
        """
        hi = Housner.get_impulsive_height(water)
        return Pi * hi
    
    @staticmethod
    def calculate_convective_moment(Pc: float, water: WaterParameters) -> float:
        """
        Calcule le moment de la pression convective par rapport à la base
        
        Mc = Pc × hc
        
        :param Pc: Pression convective (kN/m)
        :param water: Paramètres de l'eau
        :return: Moment Mc (kN·m/m)
        """
        hc = Housner.get_convective_height(water)
        return Pc * hc
