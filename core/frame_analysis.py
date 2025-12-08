import numpy as np
from dataclasses import dataclass
from enum import Enum, auto
import math

class LoadCase(Enum):
    EMPTY = "Vide"
    FULL = "Plein"
    SEISMIC_EMPTY = "Séisme (Vide)"
    SEISMIC_FULL = "Séisme (Plein)"

@dataclass
class FrameGeometry:
    """Géométrie du cadre (dimensions entraxes et épaisseurs)"""
    width: float      # Largeur entraxe (Lx) [m]
    height: float     # Hauteur entraxe (H) [m]
    th_top: float     # Épaisseur dalle supérieure [m]
    th_bot: float     # Épaisseur radier [m]
    th_wall: float    # Épaisseur voiles [m]
    depth: float = 1.0 # Profondeur de calcul (bande de 1m)

@dataclass
class FrameResults:
    """Résultats aux nœuds principaux (A: Haut-Gauche, B: Haut-Droite, C: Bas-Droite, D: Bas-Gauche)"""
    # Moments aux coins (positif = fibre intérieure tendue)
    M_A: float = 0.0
    M_B: float = 0.0
    M_C: float = 0.0
    M_D: float = 0.0
    
    # Moments en travée (approx)
    M_top_mid: float = 0.0
    M_bot_mid: float = 0.0
    M_wall_left_mid: float = 0.0
    M_wall_right_mid: float = 0.0
    
    # Efforts tranchants aux extrémités des barres
    V_top_left: float = 0.0
    V_top_right: float = 0.0
    V_bot_left: float = 0.0
    V_bot_right: float = 0.0
    
    # Efforts normaux
    N_top: float = 0.0
    N_bot: float = 0.0
    N_wall_left: float = 0.0
    N_wall_right: float = 0.0

class RectangularFrame:
    """
    Calcul d'un cadre rectangulaire fermé rigide.
    Hypothèse : Comportement élastique linéaire.
    Méthode : Formules de Kleinlogel pour cadre symétrique ou méthode des déplacements simplifiée.
    """
    def __init__(self, geometry: FrameGeometry, E: float = 30e6):
        """
        :param geometry: Géométrie du cadre
        :param E: Module d'Young du béton [kN/m²] (défaut 30 GPa)
        """
        self.geo = geometry
        self.E = E
        
        # Calcul des inerties (I = b*h^3 / 12)
        # b = 1.0m (bande de calcul)
        self.I_top = 1.0 * self.geo.th_top**3 / 12
        self.I_bot = 1.0 * self.geo.th_bot**3 / 12
        self.I_wall = 1.0 * self.geo.th_wall**3 / 12
        
        # Raideurs relatives (K = I / L)
        self.k_top = self.I_top / self.geo.width
        self.k_bot = self.I_bot / self.geo.width
        self.k_wall = self.I_wall / self.geo.height

    def solve_uniform_load_top(self, q: float) -> FrameResults:
        """
        Charge uniforme q [kN/m] sur la traverse supérieure (vers le bas).
        """
        # Coefficients de répartition (Méthode de Cross simplifiée pour cadre symétrique)
        # Mais utilisons des formules exactes pour cadre rectangulaire simple
        # Source : Formules de Kleinlogel ou RDM
        
        k1 = self.k_top
        k2 = self.k_wall
        k3 = self.k_bot
        
        # Facteurs de rigidité
        N1 = k1 + k2
        N2 = k2 + k3
        
        # Moments d'encastrement parfait (Fixed End Moments)
        FEM_top = q * self.geo.width**2 / 12
        
        # Distribution simplifiée (Approximation acceptable pour avant-projet)
        # Pour être plus précis, on devrait résoudre le système 2x2 des rotations aux nœuds
        # theta_A = -theta_B (symétrie)
        # theta_D = -theta_C (symétrie)
        
        # Système :
        # 2(k1+k2)theta_A + k2*theta_D = FEM_top
        # k2*theta_A + 2(k2+k3)theta_D = 0
        
        # Matrice [ 2(k1+k2)   k2      ] [theta_A] = [FEM_top]
        #         [ k2         2(k2+k3)] [theta_D] = [0]
        
        det = 4*(k1+k2)*(k2+k3) - k2**2
        
        theta_A = (FEM_top * 2*(k2+k3)) / det
        theta_D = (-FEM_top * k2) / det
        
        # Calcul des moments finaux M = FEM + 2EI/L (2theta_i + theta_j)
        # M_AB (Coin haut gauche, sur traverse)
        # M_AB = -FEM_top + 2E*k1 * (2theta_A + theta_B) -> theta_B = -theta_A
        # M_AB = -FEM_top + 2E*k1 * theta_A
        # Note: Les formules ci-dessus sont sans E si on considère k = I/L relatif
        # On va travailler directement avec les moments nodaux
        
        # M_noeud_A = M_AB_final (doit être équilibré avec M_AD)
        # M_AB = -FEM_top + 2*k1*theta_A  (Attention aux signes convention RDM)
        # Convention : Moment anti-horaire positif
        
        # Recalculons proprement avec K relatifs
        # Matrice de rigidité K * Theta = M_fixe
        # [ 4(k1+k2)   2k2      ] [theta_A] = [FEM_top]  <-- Facteur 4E et 2E simplifiés en 2 et 1 ? Non standard 4EI/L
        # Standard : M_ij = 2EI/L (2th_i + th_j) + FEM_ij
        # M_AB = 2E k1 (2th_A + th_B) - FEM
        # M_AD = 2E k2 (2th_A + th_D)
        # Equilibre A : M_AB + M_AD = 0
        # 2E [ k1(2th_A - th_A) + k2(2th_A + th_D) ] = FEM
        # 2E [ k1*th_A + 2*k2*th_A + k2*th_D ] = FEM
        # 2E [ (k1 + 2k2)th_A + k2*th_D ] = FEM
        
        # Equilibre D : M_DA + M_DC = 0
        # M_DA = 2E k2 (2th_D + th_A)
        # M_DC = 2E k3 (2th_D + th_C) -> th_C = -th_D
        # 2E [ k2(2th_D + th_A) + k3(2th_D - th_D) ] = 0
        # 2E [ k2*th_A + (2k2 + k3)th_D ] = 0
        
        # Système à résoudre (sans le facteur 2E qui s'annule si FEM divisé par 2E)
        # A = k1 + 2k2
        # B = k2
        # C = 2k2 + k3
        
        # [ A  B ] [th_A] = [FEM / 2E]
        # [ B  C ] [th_D] = [0]
        
        det = (self.k_top + 2*self.k_wall)*(2*self.k_wall + self.k_bot) - self.k_wall**2
        rhs = FEM_top # On garde le facteur 2E implicite dans le résultat M
        
        # Solutions (proportionnelles à 2E*theta)
        X_A = (rhs * (2*self.k_wall + self.k_bot)) / det
        X_D = (-rhs * self.k_wall) / det
        
        # Moments aux nœuds (sur les barres horizontales)
        # M_A (sur traverse) = -FEM + k1 * X_A  (car th_B = -th_A -> 2th_A - th_A = th_A)
        # Attention formule : M_AB = 2E k1 (2th_A + th_B) - FEM = 2E k1 (th_A) - FEM
        M_A_traverse = self.k_top * X_A - FEM_top
        
        # M_D (sur radier) = k3 * X_D (car th_C = -th_D -> 2th_D - th_D = th_D)
        M_D_radier = self.k_bot * X_D
        
        # Par symétrie
        M_B = -M_A_traverse
        M_C = -M_D_radier
        
        # Résultats
        res = FrameResults()
        res.M_A = abs(M_A_traverse) # Moment dans l'angle
        res.M_B = abs(M_B)
        res.M_C = abs(M_C)
        res.M_D = abs(M_D_radier)
        
        # Moments en travée (isostatique + hyperstatique)
        # M(x) = M_iso(x) + M_hyp(x)
        # M_top_mid = qL^2/8 - M_A
        res.M_top_mid = (q * self.geo.width**2 / 8) - res.M_A
        res.M_bot_mid = -res.M_D # Radier tendu en haut si M_D positif
        
        # Efforts tranchants (V = V_iso + (Ma+Mb)/L)
        # Symétrie -> V = qL/2
        res.V_top_left = q * self.geo.width / 2
        res.V_top_right = -q * self.geo.width / 2
        
        # Efforts normaux dans les voiles = Réaction d'appui de la traverse
        res.N_wall_left = q * self.geo.width / 2
        res.N_wall_right = q * self.geo.width / 2
        
        return res

    def solve_hydrostatic_load_walls(self, q_base: float) -> FrameResults:
        """
        Charge triangulaire sur les voiles (0 en haut, q_base en bas).
        Symétrique (poussée interne des deux côtés).
        """
        # FEM pour charge triangulaire (0 en haut A, q en bas D)
        # M_AD_fixe = qL^2 / 20 (en haut)
        # M_DA_fixe = qL^2 / 30 (en bas)
        # Attention signes : Poussée vers l'extérieur (interne)
        # Barre AD (gauche) : Poussée vers gauche.
        # Moment anti-horaire positif.
        # En A : Moment réactionnel Horaire (-) -> FEM_AD = -qH^2/20 ?
        # Vérifions tables : Poussée vers gauche sur barre verticale.
        # Encastrement A : Moment anti-horaire (+) pour retenir.
        # Encastrement D : Moment horaire (-) pour retenir.
        # Donc FEM_AD = + qH^2 / 30 (le 0 est en haut) -> Non, tables :
        # Charge triangulaire max en B (bas) : M_top = qL^2/30, M_bot = qL^2/20
        
        H = self.geo.height
        FEM_AD = q_base * H**2 / 30  # Haut (0 pression)
        FEM_DA = -q_base * H**2 / 20 # Bas (max pression)
        
        # Symétrie gauche/droite (poussée interne éclatante)
        # Les déformées sont symétriques par rapport à l'axe vertical
        # theta_B = -theta_A
        # theta_C = -theta_D
        
        # Système d'équations (Mêmes coefficients A, B, C que précédemment)
        # A = k1 + 2k2
        # B = k2
        # C = 2k2 + k3
        
        # Termes de charge (Somme des FEM aux noeuds)
        # Noeud A : M_AB + M_AD = 0
        # M_AB = k1 * th_A (car th_B = -th_A)
        # M_AD = 2k2(2th_A + th_D) + FEM_AD
        # Eq A : (k1 + 4k2)th_A + 2k2*th_D = -FEM_AD  <-- Erreur coeff 2E
        # Reprenons avec la formulation 2E factorisée
        # M_AB = 2E [ k1(th_A) ]
        # M_AD = 2E [ k2(2th_A + th_D) ] + FEM_AD
        # Somme = 2E [ (k1 + 2k2)th_A + k2*th_D ] + FEM_AD = 0
        # -> A*X_A + B*X_D = -FEM_AD
        
        # Noeud D : M_DA + M_DC = 0
        # M_DA = 2E [ k2(2th_D + th_A) ] + FEM_DA
        # M_DC = 2E [ k3(th_D) ]
        # Somme = 2E [ k2*th_A + (2k2 + k3)th_D ] + FEM_DA = 0
        # -> B*X_A + C*X_D = -FEM_DA
        
        det = (self.k_top + 2*self.k_wall)*(2*self.k_wall + self.k_bot) - self.k_wall**2
        
        R1 = -FEM_AD
        R2 = -FEM_DA
        
        X_A = (R1 * (2*self.k_wall + self.k_bot) - R2 * self.k_wall) / det
        X_D = (R2 * (self.k_top + 2*self.k_wall) - R1 * self.k_wall) / det
        
        # Calcul des moments finaux
        # M_A (sur traverse) = k1 * X_A
        M_A_traverse = self.k_top * X_A
        
        # M_D (sur radier) = k3 * X_D
        M_D_radier = self.k_bot * X_D
        
        # M_AD (haut du voile) = 2k2(2X_A + X_D) + FEM_AD
        M_AD = 2*self.k_wall * (2*X_A + X_D) + FEM_AD
        
        # M_DA (bas du voile) = 2k2(2X_D + X_A) + FEM_DA
        M_DA = 2*self.k_wall * (2*X_D + X_A) + FEM_DA
        
        res = FrameResults()
        res.M_A = abs(M_A_traverse)
        res.M_D = abs(M_D_radier)
        res.M_B = res.M_A
        res.M_C = res.M_D
        
        # Moments en travée des voiles
        # M(y) = M_iso(y) + M_A + (M_D - M_A)*y/H
        # M_iso(y) pour triangle = q y^3 / (6H)  (y depuis haut)
        # Non, M_iso poutre sur 2 appuis avec charge triangulaire
        # C'est plus complexe. On prendra une approx ou M_max numérique.
        # Pour l'instant, on laisse 0 ou on estime à mi-hauteur.
        
        # Traction dans traverse et radier (due à la poussée sur les voiles)
        # Réaction totale sur le voile = qH/2
        # Réaction haut (A) = qH/10 (iso) + (Ma+Mb)/H
        # Réaction bas (D) = qH * 4/10 ...
        # R_A_iso = qH * (1/3 * H) / H ? Centre de gravité à 2/3 depuis haut.
        # R_A_iso = qH/2 * 1/3 = qH/6
        # R_D_iso = qH/2 * 2/3 = qH/3
        # V_A = R_A_iso + (M_AD + M_DA)/H
        
        V_A = (q_base * H / 6) + (M_AD + M_DA)/H
        V_D = (q_base * H / 3) - (M_AD + M_DA)/H  # Signes à vérifier
        
        res.N_top = abs(V_A) # Traction
        res.N_bot = abs(V_D) # Traction
        
        return res

    def solve_uniform_load_walls(self, q: float) -> FrameResults:
        """
        Charge uniforme q [kN/m] sur les deux voiles (vers l'intérieur).
        """
        # FEM = qH^2/12
        FEM = q * self.geo.height**2 / 12
        
        # Symétrie
        # M_AD_fixe = FEM
        # M_DA_fixe = -FEM
        
        # Système (A, B, C)
        # Noeud A : M_AB + M_AD = 0
        # M_AB = k1 * th_A
        # M_AD = 2k2(2th_A + th_D) + FEM
        # Eq A : (k1 + 4k2)th_A + 2k2*th_D = -FEM
        
        # Noeud D : M_DA + M_DC = 0
        # M_DA = 2k2(2th_D + th_A) - FEM
        # M_DC = k3 * th_D
        # Eq D : 2k2*th_A + (4k2 + k3)th_D = FEM
        
        det = (self.k_top + 4*self.k_wall)*(4*self.k_wall + self.k_bot) - (2*self.k_wall)**2
        
        R1 = -FEM
        R2 = FEM
        
        X_A = (R1 * (4*self.k_wall + self.k_bot) - R2 * 2*self.k_wall) / det
        X_D = (R2 * (self.k_top + 4*self.k_wall) - R1 * 2*self.k_wall) / det
        
        # Moments
        M_A = self.k_top * X_A
        M_D = self.k_bot * X_D
        
        res = FrameResults()
        res.M_A = abs(M_A)
        res.M_D = abs(M_D)
        res.M_B = res.M_A
        res.M_C = res.M_D
        
        # Traction dans traverse/radier
        # Réaction totale qH
        # V_A = qH/2
        res.N_top = q * self.geo.height / 2
        res.N_bot = q * self.geo.height / 2
        
        return res

    def solve_earth_pressure(self, q_top: float, q_bot: float) -> FrameResults:
        """
        Poussée des terres (Trapèze).
        Décomposition en Rectangle (q_top) + Triangle (q_bot - q_top).
        """
        # 1. Partie Rectangulaire
        res_rect = self.solve_uniform_load_walls(q_top)
        
        # 2. Partie Triangulaire
        res_tri = self.solve_hydrostatic_load_walls(q_bot - q_top)
        
        # Superposition
        res = FrameResults()
        res.M_A = res_rect.M_A + res_tri.M_A
        res.M_B = res_rect.M_B + res_tri.M_B
        res.M_C = res_rect.M_C + res_tri.M_C
        res.M_D = res_rect.M_D + res_tri.M_D
        
        res.N_top = res_rect.N_top + res_tri.N_top
        res.N_bot = res_rect.N_bot + res_tri.N_bot
        
        # Moments en travée (approx superposition)
        # Pour le rectangle : M_max = qH^2/8 - (Ma+Md)/2 approx
        # Pour le triangle : M_max approx
        # On laisse à 0 pour l'instant ou on raffine plus tard
        
        return res

    def solve_point_load_walls(self, F: float, h: float) -> FrameResults:
        """
        Charges ponctuelles F [kN] symétriques sur les deux voiles (vers l'extérieur).
        Application à la hauteur h [m] depuis le bas (Node D).
        """
        H = self.geo.height
        a = H - h # Distance du haut
        b = h     # Distance du bas
        
        # FEM (Fixed End Moments) pour charge ponctuelle
        # Sur barre verticale gauche (AD)
        # M_AD_fixe = -P * a * b^2 / L^2 (Haut)
        # M_DA_fixe = +P * a^2 * b / L^2 (Bas)
        # Signes : Poussée vers l'extérieur (gauche).
        # En A : Moment réactionnel Horaire (-) -> FEM_AD négatif ?
        # Vérif RDM : Charge vers gauche. Encastrement A : Moment Anti-Horaire (+) pour retenir.
        # Donc FEM_AD > 0.
        # Formule standard RDM (charge P vers bas) : M_left = -Pab^2/L^2.
        # Ici charge vers gauche (équivalent vers haut si on tourne).
        # On va dire : FEM_AD = + F * a * b**2 / H**2
        #              FEM_DA = - F * a**2 * b / H**2
        
        FEM_AD = F * a * b**2 / H**2
        FEM_DA = -F * a**2 * b / H**2
        
        # Symétrie (theta_B = -theta_A, theta_C = -theta_D)
        # Système d'équations identique aux autres cas symétriques
        
        det = (self.k_top + 2*self.k_wall)*(2*self.k_wall + self.k_bot) - self.k_wall**2
        
        # Termes de charge (Somme des FEM aux noeuds)
        # Noeud A : M_AB + M_AD = 0 -> (k1 + 2k2)th_A + k2*th_D = -FEM_AD / 2E
        # Noeud D : M_DA + M_DC = 0 -> k2*th_A + (2k2 + k3)th_D = -FEM_DA / 2E
        
        R1 = -FEM_AD
        R2 = -FEM_DA
        
        X_A = (R1 * (2*self.k_wall + self.k_bot) - R2 * self.k_wall) / det
        X_D = (R2 * (self.k_top + 2*self.k_wall) - R1 * self.k_wall) / det
        
        # Moments finaux
        M_A_traverse = self.k_top * X_A
        M_D_radier = self.k_bot * X_D
        
        M_AD = 2*self.k_wall * (2*X_A + X_D) + FEM_AD
        M_DA = 2*self.k_wall * (2*X_D + X_A) + FEM_DA
        
        res = FrameResults()
        res.M_A = abs(M_A_traverse)
        res.M_D = abs(M_D_radier)
        res.M_B = res.M_A
        res.M_C = res.M_D
        
        # Efforts normaux dans traverse/radier (Traction)
        # V_A = R_A_iso + (M_AD + M_DA)/H
        # R_A_iso pour charge ponctuelle à b du bas = F * b / H
        # R_D_iso = F * a / H
        
        V_A = (F * b / H) + (M_AD + M_DA)/H
        V_D = (F * a / H) - (M_AD + M_DA)/H
        
        res.N_top = abs(V_A)
        res.N_bot = abs(V_D)
        
        return res

    def check_flotation(self, water_level_out: float, gamma_concrete: float = 25.0) -> dict:
        """
        Vérification de la flottaison (Archimède).
        :param water_level_out: Hauteur d'eau extérieure depuis le bas du radier [m]
        """
        # Dimensions extérieures
        W_ext = self.geo.width + self.geo.th_wall # Entraxe + 1/2 ep + 1/2 ep ? 
        # Non, width est entraxe. W_ext = width + th_wall
        # H_ext = height + th_top/2 + th_bot/2
        
        W_ext = self.geo.width + self.geo.th_wall
        H_ext = self.geo.height + (self.geo.th_top + self.geo.th_bot) / 2
        
        # Volume immergé
        h_submerged = min(water_level_out, H_ext)
        V_submerged = W_ext * h_submerged * self.geo.depth
        
        # Poussée d'Archimède
        U = 10.0 * V_submerged # gamma_w = 10
        
        # Poids propre
        # Traverse
        W_top = (self.geo.width + self.geo.th_wall) * self.geo.th_top * self.geo.depth * gamma_concrete
        # Radier
        W_bot = (self.geo.width + self.geo.th_wall) * self.geo.th_bot * self.geo.depth * gamma_concrete
        # Voiles (hauteur libre = H - th_top/2 - th_bot/2)
        h_wall_net = self.geo.height - (self.geo.th_top + self.geo.th_bot)/2
        W_walls = 2 * h_wall_net * self.geo.th_wall * self.geo.depth * gamma_concrete
        
        Total_Weight = W_top + W_bot + W_walls
        
        # Facteur de sécurité
        Fs = Total_Weight / U if U > 0 else 999.0
        
        return {
            "weight": Total_Weight,
            "buoyancy": U,
            "Fs": Fs,
            "status": "OK" if Fs >= 1.1 else "INSTABLE"
        }

