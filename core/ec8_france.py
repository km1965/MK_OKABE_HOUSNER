import math

class EC8France:
    # Accélération de référence agr [m/s2] (Zones 1 à 5)
    # 1: Très faible, 2: Faible, 3: Modérée, 4: Moyenne, 5: Forte
    # Valeurs en g: 0.04, 0.07, 0.11, 0.16, 0.30
    ZONES = {
        "1": 0.04,
        "2": 0.07,
        "3": 0.11,
        "4": 0.16,
        "5": 0.30
    }

    # Coefficient d'importance gamma_I (Catégories I à IV)
    IMPORTANCE = {
        "I": 0.8,
        "II": 1.0,
        "III": 1.2,
        "IV": 1.4
    }

    # Paramètre de sol S selon la classe de sol (A, B, C, D, E)
    # Arrêté du 22 octobre 2010
    # Pour les zones 1 à 4 (sismicité faible à moyenne) -> Spectre de réponse élastique type 1 (ou spécifique France)
    # En France, les valeurs de S sont définies comme suit (pour spectre horizontal):
    SOIL_S = {
        "A": 1.0,
        "B": 1.35,
        "C": 1.5,
        "D": 1.6, # Attention, peut varier. EC8 standard est 1.35 pour D. France a des valeurs spécifiques.
        # Vérification Arrêté 2010:
        # A: 1.0
        # B: 1.35
        # C: 1.5
        # D: 1.6
        # E: 1.8
        "E": 1.8
    }
    
    # Note: Pour la zone 5 (Antilles), les valeurs peuvent être différentes (Spectre Type 1 EC8 standard souvent utilisé).
    # Ici on implémente les valeurs courantes France métropolitaine (Zones 1-4).
    # Pour simplifier, on utilisera ces valeurs par défaut, modifiables si besoin.

    @staticmethod
    def get_agr(zone: str) -> float:
        return EC8France.ZONES.get(zone, 0.04)

    @staticmethod
    def get_gamma_i(category: str) -> float:
        return EC8France.IMPORTANCE.get(category, 1.0)

    @staticmethod
    def get_soil_factor(soil_class: str) -> float:
        return EC8France.SOIL_S.get(soil_class, 1.0)

    @staticmethod
    def calculate_kh(zone: str, category: str, soil_class: str, r_factor: float = 2.0) -> float:
        """
        Calcule le coefficient sismique horizontal kh.
        kh = alpha * S / r
        alpha = ag / g = gamma_I * agr / g
        (Note: agr est souvent donné en g, donc agr_val est directement le ratio par rapport à g si on considère g=1g)
        
        Si ZONES stocke des valeurs en 'g', alors agr_g = ZONES[z].
        ag_g = gamma_I * agr_g
        alpha = ag_g
        
        Donc kh = (gamma_I * agr_g) * S / r
        """
        agr_g = EC8France.get_agr(zone)
        gamma_i = EC8France.get_gamma_i(category)
        s = EC8France.get_soil_factor(soil_class)
        
        # Calcul de alpha (rapport d'accélération au sol de calcul)
        alpha = agr_g * gamma_i
        
        # Calcul de kh
        # r est le coefficient de comportement (ou facteur q pour les murs ?)
        # Pour les murs de soutènement, EC8-5 art 7.3.2.2:
        # kh = alpha * S / r
        # r = 2 pour murs gravitaires libres de se déplacer
        # r = 1.5 pour murs gravitaires moins libres
        # r = 1 pour murs encastrés
        
        kh = alpha * s / r_factor
        return kh
    @staticmethod
    def calculate_kv(kh: float, zone: str) -> float:
        """
        Calcule le coefficient sismique vertical kv.
        EC8-5: kv = 0.5 * kh si avg/ag > 0.6
        En France, souvent on prend kv = +/- 0.5 kh ou 0.33 kh.
        Par défaut on peut prendre 0.5 * kh pour être conservateur si demandé, 
        ou 0 si on considère que l'effet vertical est négligeable (souvent le cas pour murs gravitaires sauf cas spéciaux).
        
        L'annexe nationale peut imposer avg/ag.
        Pour ce calculateur, on proposera kv = 0.5 * kh par défaut si l'utilisateur active le séisme vertical.
        Mais ici on retourne une valeur par défaut.
        """
        # Par défaut, on retourne 0.5 * kh (montant ou descendant)
        return 0.5 * kh

    # Périodes caractéristiques du spectre selon la classe de sol
    # EC8-1 Tableau 3.2 pour spectre Type 1 (France métropolitaine)
    SPECTRUM_PERIODS = {
        "A": (0.15, 0.4, 2.0),   # (TB, TC, TD)
        "B": (0.15, 0.5, 2.0),
        "C": (0.20, 0.6, 2.0),
        "D": (0.20, 0.8, 2.0),
        "E": (0.15, 0.5, 2.0)
    }

    @staticmethod
    def get_spectrum_periods(soil_class: str) -> tuple:
        """Retourne les périodes TB, TC, TD pour une classe de sol"""
        return EC8France.SPECTRUM_PERIODS.get(soil_class, (0.15, 0.4, 2.0))

    @staticmethod
    def get_spectral_acceleration(T: float, zone: str, category: str, soil_class: str, 
                                  damping: float = 0.05) -> float:
        """
        Retourne l'accélération spectrale Sa pour une période T donnée
        selon le spectre de réponse élastique EC8 Type 1
        
        :param T: Période (s)
        :param zone: Zone sismique
        :param category: Catégorie d'importance
        :param soil_class: Classe de sol
        :param damping: Coefficient d'amortissement (défaut: 5%)
        :return: Accélération spectrale Sa en g
        """
        # Accélération au sol de calcul
        agr_g = EC8France.get_agr(zone)
        gamma_i = EC8France.get_gamma_i(category)
        ag_g = agr_g * gamma_i  # en g
        
        # Facteur de sol
        S = EC8France.get_soil_factor(soil_class)
        
        # Facteur d'amortissement (EC8-1 §3.2.2.2)
        # η = sqrt(10 / (5 + ξ)) avec ξ en %
        eta = math.sqrt(10.0 / (5.0 + damping * 100))
        
        # Périodes caractéristiques
        TB, TC, TD = EC8France.get_spectrum_periods(soil_class)
        
        # Calcul selon la branche du spectre (EC8-1 §3.2.2.2)
        if T <= TB:
            # Branche ascendante
            Sa_g = ag_g * S * (1.0 + T/TB * (eta * 2.5 - 1.0))
        elif T <= TC:
            # Plateau
            Sa_g = ag_g * S * eta * 2.5
        elif T <= TD:
            # Branche descendante
            Sa_g = ag_g * S * eta * 2.5 * (TC / T)
        else:
            # Longues périodes
            Sa_g = ag_g * S * eta * 2.5 * (TC * TD / (T ** 2))
        
        return Sa_g

import math
