import math

class WallGeometry:
    def __init__(self, height: float, batter_angle: float = 0.0, backfill_slope: float = 0.0):
        """
        :param height: Hauteur du mur (H) [m]
        :param batter_angle: Angle d'inclinaison du parement arrière par rapport à la verticale (beta) [deg]
                             Positif si le mur penche vers le remblai.
        :param backfill_slope: Angle du talus (i) [deg]
        """
        self.H = height
        self.beta = math.radians(batter_angle)
        self.i = math.radians(backfill_slope)

class SoilParameters:
    def __init__(self, phi: float, delta: float, gamma: float, cohesion: float = 0.0):
        """
        :param phi: Angle de frottement interne (phi) [deg]
        :param delta: Angle de frottement sol-mur (delta) [deg]
        :param gamma: Poids volumique du sol (gamma) [kN/m3]
        :param cohesion: Cohésion du sol (c) [kPa] (Note: Mononobe-Okabe classique suppose c=0)
        """
        self.phi = math.radians(phi)
        self.delta = math.radians(delta)
        self.gamma = gamma
        self.c = cohesion

class SeismicParameters:
    def __init__(self, kh: float, kv: float = 0.0):
        """
        :param kh: Coefficient sismique horizontal
        :param kv: Coefficient sismique vertical
        """
        self.kh = kh
        self.kv = kv
        # Angle sismique theta
        # theta = atan(kh / (1 - kv))
        # Attention: si 1-kv est proche de 0 ou négatif, cela peut poser problème.
        # EC8 impose généralement kv <= 0.5 kh ou similaire, donc 1-kv > 0.
        try:
            self.theta = math.atan(self.kh / (1 - self.kv))
        except ZeroDivisionError:
             self.theta = math.radians(90) # Cas extrême peu probable en pratique courante

class MononobeOkabe:
    @staticmethod
    def calculate_kae(wall: WallGeometry, soil: SoilParameters, seismic: SeismicParameters) -> float:
        """
        Calcule le coefficient de poussée dynamique active Kae selon Mononobe-Okabe.
        """
        phi = soil.phi
        delta = soil.delta
        beta = wall.beta
        i = wall.i
        theta = seismic.theta

        # Vérification de la condition de validité (phi - beta - theta >= i)
        # Si (phi - beta - theta < i), la formule peut donner des racines complexes.
        # En pratique, on sature ou on lève une erreur.
        
        # Terme A (numérateur)
        # cos^2(phi - theta - beta)
        num = math.cos(phi - theta - beta)**2

        # Terme B (dénominateur partie 1)
        # cos(theta) * cos^2(beta) * cos(delta + beta + theta)
        denom_part1 = math.cos(theta) * (math.cos(beta)**2) * math.cos(delta + beta + theta)

        # Terme C (racine carrée)
        # sqrt( (sin(phi + delta) * sin(phi - theta - i)) / (cos(delta + beta + theta) * cos(i - beta)) )
        
        try:
            term_sqrt_num = math.sin(phi + delta) * math.sin(phi - theta - i)
            term_sqrt_denom = math.cos(delta + beta + theta) * math.cos(i - beta)
            
            if term_sqrt_denom == 0:
                 raise ValueError("Division par zéro dans le terme racine de Kae")
            
            ratio = term_sqrt_num / term_sqrt_denom
            if ratio < 0:
                # Cela arrive si la pente du talus est trop forte par rapport au frottement + séisme
                # Pour l'instant on retourne une valeur indicative ou on raise
                # EC8 dit que si i > phi - theta, le talus est instable.
                return float('nan') 

            sqrt_val = math.sqrt(ratio)
        except ValueError:
            return float('nan')

        denom = denom_part1 * (1 + sqrt_val)**2

        if denom == 0:
            return float('inf')

        Kae = num / denom
        return Kae

    @staticmethod
    def calculate_pae(kae: float, wall: WallGeometry, soil: SoilParameters, seismic: SeismicParameters) -> float:
        """
        Calcule la poussée totale active P_ae.
        P_ae = 0.5 * gamma * H^2 * (1 - kv) * Kae
        """
        return 0.5 * soil.gamma * (wall.H**2) * (1 - seismic.kv) * kae

    @staticmethod
    def calculate_delta_pae(pae: float, wall: WallGeometry, soil: SoilParameters) -> float:
        """
        Calcule l'incrément dynamique.
        Souvent défini comme P_ae - P_a_statique.
        Ici on retourne juste P_ae car c'est la valeur totale qui intéresse pour le dimensionnement.
        Si on veut le delta, il faut calculer Ka statique (kh=0, kv=0) et soustraire.
        """
        # Pour cet outil, on se concentre sur P_ae total.
        return pae
