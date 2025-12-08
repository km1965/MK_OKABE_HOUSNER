"""
Règlement Parasismique Marocain (RPS 2011)
Paramètres pour le calcul de la poussée dynamique selon Mononobe-Okabe
"""

class RPS2011Maroc:
    """
    Classe pour les paramètres sismiques selon RPS 2011 (Maroc)
    """
    
    # Zones sismiques (0 à 5) - Accélération zonale en g
    # RPS 2011 Version 2011 - Tableau 4.1
    ZONES = {
        "0": 0.00,   # Zone de sismicité négligeable
        "1": 0.08,   # Zone de sismicité faible
        "2": 0.10,   # Zone de sismicité moyenne
        "3": 0.12,   # Zone de sismicité élevée
        "4": 0.16,   # Zone de sismicité très élevée
        "5": 0.18    # Zone de sismicité exceptionnelle (Al Hoceima, etc.)
    }
    
    # Classes d'importance (I, II, III) - Facteur d'importance I
    # RPS 2011 - Article 4.3.2
    IMPORTANCE = {
        "I": 1.3,    # Bâtiments de grande importance
        "II": 1.2,   # Bâtiments d'importance moyenne
        "III": 1.0   # Bâtiments d'importance modérée
    }
    
    # Classes de sol (Sites S1 à S5)
    # Facteur d'amplification dynamique moyen D
    # RPS 2011 - Tableau 4.4
    SOIL_D = {
        "S1": 1.0,   # Rocher ou sol ferme
        "S2": 1.2,   # Sol ferme
        "S3": 1.15,  # Sol meuble d'épaisseur moyenne
        "S4": 1.35,  # Sol meuble d'épaisseur importante
        "S5": 1.45   # Sol très meuble
    }
    
    # Coefficient de site S (selon période)
    # Pour les murs de soutènement, on utilise généralement les valeurs courtes périodes
    # RPS 2011 - Tableau 4.5
    SOIL_S = {
        "S1": 1.0,
        "S2": 1.2,
        "S3": 1.5,
        "S4": 1.7,
        "S5": 1.8
    }
    
    @staticmethod
    def get_acceleration(zone: str) -> float:
        """Retourne l'accélération zonale A pour une zone donnée"""
        return RPS2011Maroc.ZONES.get(zone, 0.0)
    
    @staticmethod
    def get_importance_factor(classe: str) -> float:
        """Retourne le facteur d'importance I pour une classe donnée"""
        return RPS2011Maroc.IMPORTANCE.get(classe, 1.0)
    
    @staticmethod
    def get_amplification_factor(site: str) -> float:
        """Retourne le facteur d'amplification dynamique D"""
        return RPS2011Maroc.SOIL_D.get(site, 1.0)
    
    @staticmethod
    def get_site_coefficient(site: str) -> float:
        """Retourne le coefficient de site S"""
        return RPS2011Maroc.SOIL_S.get(site, 1.0)
    
    @staticmethod
    def calculate_kh(zone: str, classe: str, site: str, r_factor: float = 2.0) -> float:
        """
        Calcule le coefficient sismique horizontal kh selon RPS 2011.
        
        Formule RPS 2011 (Article 7.4.3) :
        kh = (A × I × D × S) / R
        
        Où :
        - A = Accélération zonale (en g)
        - I = Facteur d'importance
        - D = Facteur d'amplification dynamique moyen
        - S = Coefficient de site
        - R = Facteur de comportement
        
        Pour les murs de soutènement (RPS 2011 - 7.4.3.2) :
        - R = 2.0 pour murs gravitaires libres de se déplacer
        - R = 1.5 pour murs semi-rigides
        - R = 1.0 pour murs encastrés
        
        :param zone: Zone sismique (0 à 5)
        :param classe: Classe d'importance (I, II, III)
        :param site: Classe de sol (S1 à S5)
        :param r_factor: Facteur de comportement R (défaut: 2.0)
        :return: Coefficient sismique horizontal kh
        """
        A = RPS2011Maroc.get_acceleration(zone)
        I = RPS2011Maroc.get_importance_factor(classe)
        D = RPS2011Maroc.get_amplification_factor(site)
        S = RPS2011Maroc.get_site_coefficient(site)
        
        # Calcul de kh
        # Note: Pour les murs, on utilise généralement D×S ou juste S selon l'interprétation
        # Ici on prend A × I × S / R (approche simplifiée courante)
        kh = (A * I * S) / r_factor
        
        return kh
    
    @staticmethod
    def calculate_kv(kh: float) -> float:
        """
        Calcule le coefficient sismique vertical kv selon RPS 2011.
        
        RPS 2011 recommande :
        kv = ± 0.3 × kh (pour les régions de forte sismicité)
        
        On prend la valeur positive (composante verticale ascendante) 
        qui est généralement la plus défavorable pour la poussée.
        
        :param kh: Coefficient sismique horizontal
        :return: Coefficient sismique vertical kv
        """
        return 0.3 * kh
    
    @staticmethod
    def get_zone_name(zone: str) -> str:
        """Retourne le nom descriptif de la zone"""
        names = {
            "0": "Sismicité négligeable",
            "1": "Sismicité faible",
            "2": "Sismicité moyenne",
            "3": "Sismicité élevée",
            "4": "Sismicité très élevée",
            "5": "Sismicité exceptionnelle"
        }
        return names.get(zone, "Inconnue")
