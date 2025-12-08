"""
Module de vérification de la stabilité externe (Glissement, Renversement, Portance)
"""
import math

class StabilityVerifier:
    """Vérifie la stabilité externe du mur"""
    
    def __init__(self, wall_params: dict, forces: dict, seismic_params: dict):
        """
        Initialise le vérificateur
        
        :param wall_params: Dict contenant B (largeur), W (poids), delta_base (frottement base)
        :param forces: Dict contenant Pae, Pw, Pae_h, Pae_v, etc.
        :param seismic_params: Dict contenant kh, kv
        """
        self.B = wall_params.get('width_B', 3.0)  # Largeur semelle
        self.W = wall_params.get('weight_W', 100.0)  # Poids mur
        self.delta_base = wall_params.get('friction_base', 30.0)  # Angle frottement base
        self.cohesion = wall_params.get('cohesion_base', 0.0)  # Cohésion base
        
        self.forces = forces
        self.kh = seismic_params.get('kh', 0.0)
        self.kv = seismic_params.get('kv', 0.0)
        
        # Géométrie simplifiée pour bras de levier (à affiner selon forme réelle)
        # On suppose le poids appliqué au centre de gravité (ex: B/2 pour mur rectangulaire)
        self.xg = wall_params.get('xg', self.B / 2.0)
        self.yg = wall_params.get('yg', wall_params.get('height', 5.0) / 2.0)
        
    def check_sliding(self) -> dict:
        """
        Vérifie le glissement sur la base
        Fs = Forces résistantes / Forces motrices
        """
        # Forces verticales (Stabilisantes pour frottement)
        # N = W(1-kv) + Pae_v
        # Note: kv vers le haut défavorable pour frottement (réduit N)
        # Mais EC8 dit souvent de prendre 1 +/- kv
        
        # Composante verticale Pae
        Pae_v = self.forces.get('Pae_v', 0.0)
        
        # Force normale totale
        # On considère le cas défavorable où le séisme soulève le mur (1 - kv)
        N_tot = self.W * (1 - self.kv) + Pae_v
        
        # Résistance au glissement (Coulomb)
        # R = N * tan(delta_base) + c * B
        tan_delta = math.tan(math.radians(self.delta_base))
        R_sliding = N_tot * tan_delta + self.cohesion * self.B
        
        # Forces motrices (Horizontales)
        # H = Pae_h + Pw + F_inertie
        Pae_h = self.forces.get('Pae_h', 0.0)
        Pw = self.forces.get('Pw', 0.0)
        F_inertie = self.W * self.kh
        
        H_tot = Pae_h + Pw + F_inertie
        
        # Facteur de sécurité
        if H_tot <= 0:
            Fs = 999.0  # Infini
        else:
            Fs = R_sliding / H_tot
            
        return {
            'Fs': Fs,
            'R_sliding': R_sliding,
            'H_tot': H_tot,
            'status': 'OK' if Fs >= 1.5 else 'NOK' # Seuil usuel 1.5 (ou 1.1~1.2 sous séisme selon normes)
        }
        
    def check_overturning(self) -> dict:
        """
        Vérifie le renversement autour de l'arête aval (point O en bas à droite)
        Fr = Moment stabilisant / Moment renversant
        """
        # Point de rotation O = (B, 0) si origine en bas à gauche
        # Ou simplement on calcule moments par rapport à l'arête aval
        
        # Moments Stabilisants (Ms)
        # Poids W (bras de levier B - xg)
        # Pae_v (bras de levier B - x_pae ~ B car appliqué au dos)
        # On simplifie : Pae appliqué au dos du mur
        
        # Bras de levier poids (par rapport à l'arête aval)
        d_W = self.B - self.xg
        M_W = self.W * (1 - self.kv) * d_W
        
        # Bras de levier Pae_v (appliqué au dos du mur, donc à distance B de l'arête aval ? Non, à 0 si mur vertical)
        # Si mur vertical dos, Pae appliqué en x=B (si origine gauche). Donc bras levier = 0 ?
        # Si fruit, bras levier > 0.
        # Simplification conservatrice : on néglige le moment stabilisant de Pae_v si incertain
        # Ou on suppose application au tiers inférieur du parement arrière
        
        # Pour faire simple et robuste :
        # On suppose mur poids rectangulaire ou trapèze
        # Pae_v aide à stabiliser si appliqué sur le fruit arrière
        
        # On prend Pae_v appliqué à l'arrière de la semelle (bras de levier 0 ou petit)
        # Prenons 0 pour être conservateur (sécurité)
        M_Pae_v = self.forces.get('Pae_v', 0.0) * 0.0 
        
        Ms = M_W + M_Pae_v
        
        # Moments Renversants (Mr)
        # Pae_h * h_app
        # Pw * h_w_app
        # F_inertie * yg
        
        h_Pae = self.forces.get('h_Pae', self.forces.get('height', 0)/3.0)
        M_Pae_h = self.forces.get('Pae_h', 0.0) * h_Pae
        
        # Pw (résultante)
        # On a besoin du point d'application exact de Pw
        # Simplification : Pw appliqué à ~0.4 hw (Housner donne hi et hc)
        # Si on a Pw total, on prend une hauteur moyenne pondérée ou conservatrice
        h_Pw = self.forces.get('h_Pw', self.forces.get('hw', 0) * 0.4)
        M_Pw = self.forces.get('Pw', 0.0) * h_Pw
        
        # Inertie
        M_Inertie = (self.W * self.kh) * self.yg
        
        Mr = M_Pae_h + M_Pw + M_Inertie
        
        if Mr <= 0:
            Fr = 999.0
        else:
            Fr = Ms / Mr
            
        return {
            'Fr': Fr,
            'Ms': Ms,
            'Mr': Mr,
            'status': 'OK' if Fr >= 1.5 else 'NOK' # Seuil usuel sous séisme souvent réduit à 1.1 ou 1.2
        }
        
    def check_bearing(self) -> dict:
        """
        Vérifie la contrainte au sol (Meyerhof)
        sigma_ref = N / (B - 2e)  (Distribution uniforme rectangulaire équivalente)
        ou sigma_max = N/B * (1 + 6e/B) (Distribution triangulaire/trapézoïdale)
        """
        # Somme des forces verticales
        N_tot = self.W * (1 - self.kv) + self.forces.get('Pae_v', 0.0)
        
        # Somme des moments / Centre de la base (B/2)
        # M_net_center = M_renversant_center - M_stabilisant_center
        # C'est plus simple de passer par l'excentrement e
        # e = B/2 - (Ms - Mr) / N
        
        res_sliding = self.check_sliding()
        res_overturning = self.check_overturning()
        
        Ms = res_overturning['Ms']
        Mr = res_overturning['Mr']
        
        # Position de la résultante R par rapport à l'arête aval (point O)
        # x_R = (Ms - Mr) / N
        if N_tot <= 0:
            return {'status': 'Error', 'msg': 'Soulèvement total'}
            
        x_R = (Ms - Mr) / N_tot
        
        # Excentrement par rapport au centre
        # e = B/2 - x_R
        e = (self.B / 2.0) - x_R
        
        # Vérification Tiers Central (e < B/6) pour statique, souvent élargi pour séisme
        # Sous séisme, on accepte souvent e < B/3 (décollement partiel admis)
        
        # Contrainte de référence (Meyerhof - charge excentrée)
        # B_eff = B - 2e
        B_eff = self.B - 2 * e
        
        if B_eff <= 0:
            sigma_ref = 9999.0 # Rupture équilibre
        else:
            sigma_ref = N_tot / B_eff
            
        # Contrainte max élastique (Navier)
        # sigma_max = N/B (1 + 6e/B)
        sigma_max = (N_tot / self.B) * (1 + 6 * abs(e) / self.B)
        
        return {
            'e': e,
            'B_eff': B_eff,
            'sigma_ref': sigma_ref,
            'sigma_max': sigma_max,
            'N_tot': N_tot,
            'status': 'OK' if e < self.B/3 else 'NOK' # Critère décollement
        }
