"""
Vérifications Structurelles et Stabilité pour Bâches à Eau
Selon RPS 2011 / BAEL 91 mod. 99 / EC2
"""
import math
from dataclasses import dataclass
from typing import Optional

@dataclass
class ConcreteProperties:
    """Propriétés du béton"""
    fc28: float = 25.0      # Résistance caractéristique [MPa]
    gamma_c: float = 1.5    # Coefficient partiel béton
    fcd: float = 0.0        # Résistance de calcul [MPa]
    fctm: float = 0.0       # Résistance traction moyenne [MPa]
    
    def __post_init__(self):
        self.fcd = 0.85 * self.fc28 / self.gamma_c
        self.fctm = 0.30 * self.fc28**(2/3) if self.fc28 <= 50 else 2.12 * math.log(1 + self.fc28/10)

@dataclass
class SteelProperties:
    """Propriétés de l'acier"""
    fyk: float = 500.0      # Limite élastique [MPa]
    gamma_s: float = 1.15   # Coefficient partiel acier
    Es: float = 200000.0    # Module d'Young [MPa]
    
    @property
    def fyd(self) -> float:
        return self.fyk / self.gamma_s

@dataclass 
class SectionProperties:
    """Propriétés de la section"""
    b: float = 1.0          # Largeur [m] (bande de 1m)
    h: float = 0.25         # Hauteur [m]
    d: float = 0.0          # Hauteur utile [m]
    enrobage: float = 0.04  # Enrobage [m]
    
    def __post_init__(self):
        if self.d == 0:
            self.d = self.h - self.enrobage - 0.01  # -1cm pour demi-diamètre barre

class TankVerifications:
    """Classe principale pour les vérifications de bâches à eau"""
    
    @staticmethod
    def check_sliding(V_horizontal: float, W_total: float, 
                     friction_coef: float = 0.5, 
                     cohesion: float = 0.0, 
                     A_base: float = 1.0,
                     Fs_required: float = 1.5) -> dict:
        """
        Vérification au glissement du radier.
        
        :param V_horizontal: Force horizontale totale [kN]
        :param W_total: Poids total stabilisant [kN]
        :param friction_coef: Coefficient de frottement sol/béton (tan φ')
        :param cohesion: Cohésion du sol [kPa]
        :param A_base: Surface du radier [m²]
        :param Fs_required: Facteur de sécurité requis
        :return: Dictionnaire avec résultats
        """
        # Force résistante
        F_friction = friction_coef * W_total
        F_cohesion = cohesion * A_base
        F_resistant = F_friction + F_cohesion
        
        # Facteur de sécurité
        Fs = F_resistant / V_horizontal if V_horizontal > 0 else 999.0
        
        return {
            "V_horizontal": V_horizontal,
            "F_resistant": F_resistant,
            "Fs_glissement": Fs,
            "Fs_required": Fs_required,
            "status": "OK" if Fs >= Fs_required else "NON VÉRIFIÉ"
        }
    
    @staticmethod
    def check_bearing_capacity(N_total: float, 
                               M_total: float,
                               L: float, 
                               B: float,
                               sigma_adm: float = 200.0) -> dict:
        """
        Vérification de la capacité portante (pression au sol).
        
        :param N_total: Charge verticale totale [kN]
        :param M_total: Moment total à la base [kNm]
        :param L: Longueur du radier [m]
        :param B: Largeur du radier [m]
        :param sigma_adm: Contrainte admissible du sol [kPa]
        :return: Dictionnaire avec résultats
        """
        A = L * B
        W = L * B**2 / 6  # Module de flexion
        
        # Excentricité
        e = M_total / N_total if N_total > 0 else 0
        
        # Contraintes (Meyerhof simplifié)
        if e <= B / 6:
            # Répartition trapézoïdale
            sigma_max = N_total / A + M_total / W
            sigma_min = N_total / A - M_total / W
        else:
            # Répartition triangulaire (décollement)
            B_eff = B - 2 * e
            sigma_max = 2 * N_total / (L * B_eff) if B_eff > 0 else 999
            sigma_min = 0
        
        return {
            "N_total": N_total,
            "M_total": M_total,
            "excentricite": e,
            "e_limite": B / 6,
            "sigma_max": sigma_max,
            "sigma_min": sigma_min,
            "sigma_adm": sigma_adm,
            "status": "OK" if sigma_max <= sigma_adm else "NON VÉRIFIÉ"
        }
    
    @staticmethod
    def calculate_flexural_reinforcement(M_Ed: float, 
                                          section: SectionProperties,
                                          concrete: ConcreteProperties,
                                          steel: SteelProperties) -> dict:
        """
        Calcul du ferraillage en flexion simple (BAEL / EC2).
        
        :param M_Ed: Moment de calcul [kNm]
        :param section: Propriétés de la section
        :param concrete: Propriétés du béton
        :param steel: Propriétés de l'acier
        :return: Dictionnaire avec résultats
        """
        # Conversion en N.mm
        M_Ed_Nmm = abs(M_Ed) * 1e6
        b_mm = section.b * 1000
        d_mm = section.d * 1000
        
        # Moment réduit
        mu = M_Ed_Nmm / (b_mm * d_mm**2 * concrete.fcd)
        
        # Limite pivot A/B (sans aciers comprimés)
        mu_lim = 0.372  # Pour fe500
        
        if mu <= mu_lim:
            # Pas d'aciers comprimés nécessaires
            alpha = 1.25 * (1 - math.sqrt(1 - 2 * mu))
            z = d_mm * (1 - 0.4 * alpha)
            As = M_Ed_Nmm / (z * steel.fyd)  # mm²
        else:
            # Aciers comprimés nécessaires (simplifié)
            alpha = 0.617
            z = d_mm * (1 - 0.4 * alpha)
            As = M_Ed_Nmm / (z * steel.fyd) * 1.2  # Majoré
        
        # Ferraillage minimum (fissuration)
        As_min = 0.26 * (concrete.fctm / steel.fyk) * b_mm * d_mm
        As_min = max(As_min, 0.0013 * b_mm * d_mm)
        
        As_final = max(As, As_min)
        
        return {
            "M_Ed": M_Ed,
            "mu": mu,
            "mu_lim": mu_lim,
            "As_calc": As,
            "As_min": As_min,
            "As_required": As_final,  # cm²/m
            "As_required_cm2": As_final / 100,  # cm²/m
            "status": "OK" if mu <= mu_lim else "Aciers comprimés"
        }
    
    @staticmethod
    def check_shear(V_Ed: float,
                    section: SectionProperties,
                    concrete: ConcreteProperties,
                    steel: SteelProperties = None,
                    As_long: float = 0) -> dict:
        """
        Vérification de l'effort tranchant (EC2 6.2).
        Calcule Asw si armatures transversales requises.
        
        :param V_Ed: Effort tranchant de calcul [kN]
        :param section: Propriétés de la section
        :param concrete: Propriétés du béton
        :param steel: Propriétés de l'acier (pour calcul Asw)
        :param As_long: Section d'aciers longitudinaux [mm²]
        :return: Dictionnaire avec résultats
        """
        if steel is None:
            steel = SteelProperties()
            
        b_mm = section.b * 1000
        d_mm = section.d * 1000
        
        # Taux d'armatures longitudinales
        rho_l = min(As_long / (b_mm * d_mm), 0.02) if As_long > 0 else 0.002
        
        # Coefficient k (effet d'échelle)
        k = min(1 + math.sqrt(200 / d_mm), 2.0)
        
        # VRd,c (résistance sans armatures) - EC2 6.2.2
        CRd_c = 0.18 / 1.5  # gamma_c = 1.5
        k1 = 0.15
        sigma_cp = 0  # Pas de précontrainte
        
        VRd_c = (CRd_c * k * (100 * rho_l * concrete.fc28)**(1/3) + k1 * sigma_cp) * b_mm * d_mm / 1000
        
        # Valeur minimale
        v_min = 0.035 * k**(3/2) * concrete.fc28**0.5
        VRd_c_min = v_min * b_mm * d_mm / 1000
        VRd_c = max(VRd_c, VRd_c_min)
        
        # Résultats de base
        result = {
            "V_Ed": abs(V_Ed),
            "VRd_c": VRd_c,
            "ratio": abs(V_Ed) / VRd_c if VRd_c > 0 else 999,
            "Asw_required": 0,
            "Asw_min": 0,
            "spacing_max": 0,
            "status": "OK"
        }
        
        # Si VEd > VRd,c : calcul des armatures transversales
        if abs(V_Ed) > VRd_c:
            # VRd,max (bielle comprimée) - EC2 6.2.3
            alpha_cw = 1.0
            nu1 = 0.6 * (1 - concrete.fc28 / 250)
            z = 0.9 * d_mm
            theta = 21.8  # Angle bielles (cot θ = 2.5, économique)
            cot_theta = 2.5
            
            VRd_max = alpha_cw * b_mm * z * nu1 * concrete.fcd / (cot_theta + 1/cot_theta) / 1000
            
            if abs(V_Ed) > VRd_max:
                result["status"] = "NON VÉRIFIÉ (Bielle)"
                result["VRd_max"] = VRd_max
                return result
            
            # Asw/s requis - EC2 6.2.3
            # VEd = Asw/s * z * fywd * cot(θ)
            fywd = steel.fyd  # MPa
            Asw_s = abs(V_Ed) * 1000 / (z * fywd * cot_theta)  # mm²/mm
            
            # Asw minimum - EC2 9.2.2
            rho_w_min = 0.08 * math.sqrt(concrete.fc28) / steel.fyk
            Asw_s_min = rho_w_min * b_mm  # mm²/mm
            
            Asw_s = max(Asw_s, Asw_s_min)
            
            # Espacement max - EC2 9.2.2
            s_max = min(0.75 * d_mm, 600)  # mm
            
            # Asw pour espacement courant (200mm)
            s_courant = 200  # mm
            Asw_required = Asw_s * s_courant  # mm² (2 brins)
            
            result.update({
                "Asw_s": Asw_s,  # mm²/mm
                "Asw_required": Asw_required / 100,  # cm² pour espacement de 200mm
                "Asw_min": Asw_s_min * s_courant / 100,  # cm²
                "spacing_max": s_max,
                "VRd_max": VRd_max,
                "status": "Armatures transversales requises"
            })
        
        return result
    
    @staticmethod
    def check_cracking(M_ser: float,
                       section: SectionProperties,
                       concrete: ConcreteProperties,
                       steel: SteelProperties = None,
                       As_provided: float = 0,
                       phi_bar: float = 12,
                       w_max: float = 0.2) -> dict:
        """
        Vérification de la fissuration selon EC2 7.3.4.
        Pour bâches à eau : w_max = 0.2 mm (étanchéité).
        
        :param M_ser: Moment de service [kNm]
        :param section: Propriétés de la section
        :param As_provided: Section d'aciers fournie [mm²]
        :param phi_bar: Diamètre des armatures [mm]
        :param w_max: Ouverture de fissure maximale [mm]
        :return: Dictionnaire avec résultats wk
        """
        if steel is None:
            steel = SteelProperties()
            
        b_mm = section.b * 1000
        h_mm = section.h * 1000
        d_mm = section.d * 1000
        c_mm = section.enrobage * 1000  # Enrobage
        
        if As_provided <= 0:
            return {"wk": 0, "status": "N/A - Pas d'aciers"}
        
        # 1. Contrainte acier ELS
        z = 0.9 * d_mm
        sigma_s = abs(M_ser) * 1e6 / (As_provided * z) if As_provided > 0 else 0
        
        # 2. Hauteur efficace de béton tendu (EC2 7.3.2)
        hc_eff = min(2.5 * (h_mm - d_mm), (h_mm - d_mm/2) / 3, h_mm / 2)
        Ac_eff = b_mm * hc_eff  # mm²
        
        # 3. Taux d'acier efficace
        rho_p_eff = As_provided / Ac_eff
        
        # 4. Espacement maximal des fissures sr,max (EC2 7.3.4 - Formule 7.11)
        k1 = 0.8  # Barres HA
        k2 = 0.5  # Flexion
        k3 = 3.4
        k4 = 0.425
        
        sr_max = k3 * c_mm + k1 * k2 * k4 * phi_bar / rho_p_eff
        
        # 5. Déformation différentielle (EC2 7.3.4 - Formule 7.9)
        Es = steel.Es  # MPa
        kt = 0.4  # Charge de longue durée
        fct_eff = concrete.fctm  # MPa
        
        eps_sm_eps_cm = (sigma_s - kt * fct_eff / rho_p_eff * (1 + steel.Es / 30000 * rho_p_eff)) / Es
        eps_min = 0.6 * sigma_s / Es
        eps_diff = max(eps_sm_eps_cm, eps_min)
        
        # 6. Ouverture de fissure wk (EC2 7.3.4 - Formule 7.8)
        wk = sr_max * eps_diff  # mm
        
        # Statut
        if wk <= w_max:
            status = "OK"
        else:
            status = f"NON VÉRIFIÉ (wk={wk:.2f} > {w_max}mm)"
        
        return {
            "M_ser": M_ser,
            "sigma_s": sigma_s,
            "sr_max": sr_max,
            "eps_diff": eps_diff,
            "wk": wk,
            "wk_lim": w_max,
            "status": status
        }


class LoadCombinations:
    """Combinaisons de charges selon RPS 2011 / EC0"""
    
    @staticmethod
    def get_uls_fundamental(G: float, Q: float = 0, 
                            gamma_G: float = 1.35, 
                            gamma_Q: float = 1.5) -> float:
        """ELU Fondamental : 1.35G + 1.5Q"""
        return gamma_G * G + gamma_Q * Q
    
    @staticmethod
    def get_uls_seismic(G: float, E: float, Q: float = 0,
                        psi_2: float = 0.3) -> float:
        """ELU Sismique : G + E + ψ₂Q"""
        return G + E + psi_2 * Q
    
    @staticmethod
    def get_sls_qp(G: float, Q: float = 0, psi_2: float = 0.3) -> float:
        """ELS Quasi-Permanent : G + ψ₂Q"""
        return G + psi_2 * Q


class RPS2011SeismicVerifications:
    """Vérifications sismiques selon RPS 2011 (Art. 9.2)"""
    
    # Coefficients d'accélération par zone
    ZONE_ACCELERATION = {
        '1': 0.01, '2': 0.08, '3': 0.14, '4': 0.18, '5': 0.23
    }
    
    # Coefficients de site
    SITE_COEFFICIENTS = {
        'S1': 1.0, 'S2': 1.2, 'S3': 1.4, 'S4': 1.8
    }
    
    # Classes d'importance
    IMPORTANCE_COEFFICIENTS = {
        'I': 1.3, 'II': 1.0, 'III': 0.85
    }
    
    @staticmethod
    def calculate_base_shear(W_total: float, 
                             zone: str, 
                             site: str, 
                             classe_importance: str,
                             K: float = 2.0,
                             D: float = 2.5) -> dict:
        """
        Calcul de l'effort tranchant de base selon RPS 2011 Art. 6.2.
        V = (A × D × Q / K) × W
        
        :param W_total: Poids total de la structure [kN]
        :param zone: Zone sismique (1-5)
        :param site: Classe de site (S1-S4)
        :param classe_importance: Classe d'importance (I, II, III)
        :param K: Coefficient de comportement (réservoirs = 2.0)
        :param D: Coefficient d'amplification dynamique (2.5 par défaut)
        :return: Dictionnaire avec résultats
        """
        # Coefficients
        A = RPS2011SeismicVerifications.ZONE_ACCELERATION.get(zone, 0.14)
        S = RPS2011SeismicVerifications.SITE_COEFFICIENTS.get(site, 1.2)
        I = RPS2011SeismicVerifications.IMPORTANCE_COEFFICIENTS.get(classe_importance, 1.0)
        
        # Effort tranchant de base
        V_base = (A * D * I * S / K) * W_total
        
        # Effort tranchant minimal (RPS 2011 Art. 6.2.5)
        V_min = 0.12 * A * I * W_total
        
        V_design = max(V_base, V_min)
        
        return {
            "V_base": V_base,
            "V_min": V_min,
            "V_design": V_design,
            "W_total": W_total,
            "A": A, "D": D, "S": S, "I": I, "K": K,
            "formula": "V = (A × D × I × S / K) × W",
            "status": "V_min gouverne" if V_min > V_base else "V_base gouverne"
        }
    
    @staticmethod
    def check_overturning(W_total: float, 
                          V_design: float, 
                          B: float, 
                          H_app: float,
                          Fs_required: float = 1.5) -> dict:
        """
        Vérification au renversement (RPS 2011 Art. 9.2.1).
        
        :param W_total: Poids total stabilisant [kN]
        :param V_design: Effort tranchant de calcul [kN]
        :param B: Largeur de la base [m]
        :param H_app: Hauteur d'application de V [m]
        :param Fs_required: Facteur de sécurité requis
        :return: Dictionnaire avec résultats
        """
        # Moment stabilisant
        M_stab = W_total * B / 2
        
        # Moment renversant
        M_renverse = V_design * H_app
        
        # Facteur de sécurité
        Fs = M_stab / M_renverse if M_renverse > 0 else 999.0
        
        return {
            "M_stab": M_stab,
            "M_renverse": M_renverse,
            "Fs_renversement": Fs,
            "Fs_required": Fs_required,
            "status": "OK" if Fs >= Fs_required else "NON VÉRIFIÉ"
        }
    
    @staticmethod
    def check_displacement(V_design: float, 
                           H: float, 
                           E: float, 
                           I_section: float,
                           limit_ratio: float = 200) -> dict:
        """
        Vérification des déplacements (RPS 2011 Art. 7.5).
        δ_max = V × H³ / (3 × E × I)
        Limite: H/200 pour structures rigides
        
        :param V_design: Effort tranchant [kN]
        :param H: Hauteur de la structure [m]
        :param E: Module d'élasticité [kN/m²] 
        :param I_section: Inertie de la section [m⁴]
        :param limit_ratio: H/ratio comme limite (200 par défaut)
        :return: Dictionnaire avec résultats
        """
        # Déplacement en tête (console encastrée)
        delta = (V_design * H**3) / (3 * E * I_section) if E * I_section > 0 else 0
        
        # Limite
        delta_lim = H / limit_ratio
        
        # Ratio inter-étage (drift)
        drift = delta / H if H > 0 else 0
        drift_percent = drift * 100
        
        return {
            "delta_max": delta * 1000,  # en mm
            "delta_lim": delta_lim * 1000,  # en mm
            "drift_percent": drift_percent,
            "limit_ratio": limit_ratio,
            "status": "OK" if delta <= delta_lim else "DÉPLACEMENT EXCESSIF"
        }
    
    @staticmethod
    def check_raft_rigidity(L: float, B: float, e: float, Es: float = 30000000) -> dict:
        """
        Vérification de la rigidité du radier.
        Critère: radier rigide si L/e < 10
        
        :param L: Longueur du radier [m]
        :param B: Largeur du radier [m]
        :param e: Épaisseur du radier [m]
        :param Es: Module d'élasticité [kPa]
        :return: Dictionnaire avec classification
        """
        ratio = L / e if e > 0 else 999
        
        if ratio < 10:
            classification = "Radier Rigide"
        elif ratio < 20:
            classification = "Radier Semi-Rigide"
        else:
            classification = "Radier Souple"
        
        # Inertie du radier
        I_radier = B * e**3 / 12
        
        return {
            "L": L, "B": B, "e": e,
            "ratio_L_e": ratio,
            "classification": classification,
            "I_radier": I_radier,
            "status": "OK" if ratio < 10 else "À VÉRIFIER"
        }
    
    @staticmethod
    def check_punching(N_Ed: float, 
                       d: float, 
                       u_1: float, 
                       concrete: ConcreteProperties,
                       A_sw: float = 0) -> dict:
        """
        Vérification au poinçonnement (EC2 6.4).
        
        :param N_Ed: Charge de poinçonnement [kN]
        :param d: Hauteur utile [m]
        :param u_1: Périmètre critique à 2d [m]
        :param concrete: Propriétés du béton
        :param A_sw: Armatures de poinçonnement [mm²]
        :return: Dictionnaire avec résultats
        """
        d_mm = d * 1000
        u_mm = u_1 * 1000
        
        # Contrainte de poinçonnement
        v_Ed = N_Ed * 1000 / (u_mm * d_mm) if u_mm * d_mm > 0 else 0  # MPa
        
        # Résistance sans armatures
        k = min(1 + math.sqrt(200 / d_mm), 2.0)
        rho_l = 0.005  # Taux moyen
        CRd_c = 0.18 / 1.5
        
        v_Rd_c = CRd_c * k * (100 * rho_l * concrete.fc28)**(1/3)
        v_min = 0.035 * k**(3/2) * concrete.fc28**0.5
        v_Rd_c = max(v_Rd_c, v_min)
        
        # Résistance maximale (bielle)
        v_Rd_max = 0.5 * 0.6 * (1 - concrete.fc28 / 250) * concrete.fcd
        
        return {
            "v_Ed": v_Ed,
            "v_Rd_c": v_Rd_c,
            "v_Rd_max": v_Rd_max,
            "ratio": v_Ed / v_Rd_c if v_Rd_c > 0 else 999,
            "status": "OK" if v_Ed <= v_Rd_c else "Armatures requises"
        }
    
    @staticmethod
    def check_combined_bending(N_Ed: float, M_Ed: float,
                               section: SectionProperties,
                               concrete: ConcreteProperties,
                               steel: SteelProperties) -> dict:
        """
        Vérification en flexion composée (EC2 6.1).
        
        :param N_Ed: Effort normal de calcul [kN] (+ = compression)
        :param M_Ed: Moment fléchissant de calcul [kNm]
        :param section: Propriétés de la section
        :param concrete: Propriétés du béton
        :param steel: Propriétés de l'acier
        :return: Dictionnaire avec résultats
        """
        b_mm = section.b * 1000
        h_mm = section.h * 1000
        d_mm = section.d * 1000
        
        # Excentricité
        e_0 = abs(M_Ed / N_Ed) * 1000 if N_Ed != 0 else 999  # mm
        e_min = max(20, h_mm / 30)  # Excentricité minimale
        e = max(e_0, e_min)
        
        # Type de flexion
        if e > h_mm / 2:
            flexion_type = "Flexion avec grand excentrement"
        else:
            flexion_type = "Flexion avec petit excentrement"
        
        # Moment équivalent
        M_eq = abs(N_Ed) * e / 1000  # kNm
        
        # Calcul simplifié des armatures (flexion simple majorée)
        mu = M_eq * 1e6 / (b_mm * d_mm**2 * concrete.fcd)
        
        if mu <= 0.372:  # mu_lim pour acier HA500
            alpha = 1.25 * (1 - math.sqrt(1 - 2 * mu))
            z = d_mm * (1 - 0.4 * alpha)
            As_flexion = M_eq * 1e6 / (z * steel.fyd)
            
            # Ajustement pour effort normal
            if N_Ed > 0:  # Compression
                As_required = max(0, As_flexion - N_Ed * 1000 / steel.fyd)
            else:  # Traction
                As_required = As_flexion + abs(N_Ed) * 1000 / steel.fyd
        else:
            As_required = -1  # Section insuffisante
        
        return {
            "N_Ed": N_Ed,
            "M_Ed": M_Ed,
            "excentricite": e,
            "flexion_type": flexion_type,
            "As_required": As_required,
            "As_required_cm2": As_required / 100 if As_required >= 0 else -1,
            "status": "OK" if As_required >= 0 else "Section insuffisante"
        }
    
    @staticmethod
    def check_interface_sliding(V_Ed: float,
                                b_i: float,
                                z: float,
                                concrete: ConcreteProperties,
                                steel: SteelProperties,
                                mu: float = 0.6,
                                c: float = 0.35) -> dict:
        """
        Vérification au glissement à l'interface voile-radier (EC2 6.2.5).
        
        :param V_Ed: Effort tranchant à l'interface [kN]
        :param b_i: Largeur de l'interface [m]
        :param z: Bras de levier [m]
        :param concrete: Propriétés du béton
        :param steel: Propriétés de l'acier
        :param mu: Coefficient de frottement (0.6 pour surface rugueuse)
        :param c: Coefficient de cohésion (0.35 pour surface rugueuse)
        :return: Dictionnaire avec résultats
        """
        b_mm = b_i * 1000
        z_mm = z * 1000
        
        # Contrainte de cisaillement à l'interface
        v_Edi = V_Ed * 1000 / (b_mm * z_mm) if b_mm * z_mm > 0 else 0  # MPa
        
        # Résistance sans armatures de couture (EC2 6.2.5)
        # v_Rdi = c × fctd + μ × σn
        fctd = concrete.fctm / 1.5
        sigma_n = 0  # Pas de contrainte normale de compression
        
        v_Rdi_min = c * fctd + mu * sigma_n
        
        # Résistance maximale
        nu = 0.6 * (1 - concrete.fc28 / 250)
        v_Rdi_max = 0.5 * nu * concrete.fcd
        
        # Armatures de couture requises si v_Edi > v_Rdi_min
        if v_Edi > v_Rdi_min:
            # Asv = (v_Edi - c×fctd) × b × s / (μ × fyd)
            # Pour 1m de longueur
            Asv_per_m = (v_Edi - c * fctd) * b_mm * 1000 / (mu * steel.fyd)  # mm²/m
            Asv_per_m = max(0, Asv_per_m)
        else:
            Asv_per_m = 0
        
        # Vérification limite
        if v_Edi > v_Rdi_max:
            status = "SECTION INSUFFISANTE"
        elif Asv_per_m > 0:
            status = "Armatures de couture requises"
        else:
            status = "OK (pas d'armatures de couture)"
        
        return {
            "v_Edi": v_Edi,
            "v_Rdi_min": v_Rdi_min,
            "v_Rdi_max": v_Rdi_max,
            "Asv_required": Asv_per_m,
            "Asv_required_cm2": Asv_per_m / 100,  # cm²/m
            "mu": mu,
            "c": c,
            "status": status
        }
    
    @staticmethod
    def check_column(N_Ed: float,
                     L_0: float,
                     a: float,
                     b: float,
                     concrete: ConcreteProperties,
                     steel: SteelProperties,
                     M_Ed: float = 0) -> dict:
        """
        Vérification poteau en compression avec flambement (EC2 5.8).
        
        :param N_Ed: Effort normal de calcul [kN]
        :param L_0: Longueur de flambement [m]
        :param a: Dimension section a [m]
        :param b: Dimension section b [m]
        :param concrete: Propriétés du béton
        :param steel: Propriétés de l'acier
        :param M_Ed: Moment de calcul éventuel [kNm]
        :return: Dictionnaire avec résultats
        """
        a_mm = a * 1000
        b_mm = b * 1000
        L_0_mm = L_0 * 1000
        
        # Section
        Ac = a_mm * b_mm  # mm²
        
        # Inertie (selon direction la plus défavorable)
        i_min = min(a, b) / math.sqrt(12) * 1000  # mm (rayon de giration)
        I_min = b_mm * a_mm**3 / 12 if a < b else a_mm * b_mm**3 / 12  # mm⁴
        
        # Élancement
        lambda_calc = L_0_mm / i_min
        
        # Élancement limite (EC2 5.8.3.1)
        # λ_lim = 20 × A × B × C / √n
        n = N_Ed * 1000 / (Ac * concrete.fcd)  # effort normal réduit
        A_coef = 0.7  # Fluage
        B_coef = 1.1  # Coefficient d'excentricité
        C_coef = 0.7  # Moment
        
        lambda_lim = 20 * A_coef * B_coef * C_coef / math.sqrt(n) if n > 0 else 200
        lambda_lim = min(max(lambda_lim, 25), 75)  # Limites pratiques
        
        # Vérification flambement
        needs_second_order = lambda_calc > lambda_lim
        
        # Excentricité minimale
        e_0 = max(20, a_mm / 30)  # mm
        
        # Excentricité du 1er ordre
        if N_Ed > 0:
            e_1 = abs(M_Ed) * 1e6 / (N_Ed * 1000) if M_Ed != 0 else 0  # mm
        else:
            e_1 = 0
        e_1 = max(e_1, e_0)
        
        # Excentricité du 2nd ordre (méthode simplifiée EC2 5.8.8)
        if needs_second_order:
            # e_2 = (1/r) × L_0² / c
            # Approx: e_2 ≈ L_0² / (10 × d × (2/f_yd + 1))
            d_mm = min(a_mm, b_mm) - 40 - 6  # Hauteur utile approx
            e_2 = L_0_mm**2 / (10 * d_mm * (2000 / steel.fyd + 1))
        else:
            e_2 = 0
        
        e_tot = e_1 + e_2
        
        # Moment de calcul amplifié
        M_Ed_amp = N_Ed * e_tot / 1000  # kNm
        
        # Calcul armatures (flexion composée simplifiée)
        d_mm = min(a_mm, b_mm) - 40 - 6
        mu = M_Ed_amp * 1e6 / (b_mm * d_mm**2 * concrete.fcd) if N_Ed > 0 else 0
        
        if mu <= 0.372:
            alpha = 1.25 * (1 - math.sqrt(max(0, 1 - 2 * mu)))
            z = d_mm * (1 - 0.4 * alpha)
            As_calc = max(0, M_Ed_amp * 1e6 / (z * steel.fyd) - N_Ed * 1000 / steel.fyd)
        else:
            As_calc = -1  # Section insuffisante
        
        # Armatures minimales poteaux (EC2 9.5.2)
        As_min = max(0.1 * N_Ed * 1000 / steel.fyd, 0.002 * Ac)
        As_required = max(As_calc, As_min) if As_calc >= 0 else -1
        
        # Statut
        if As_required < 0:
            status = "Section insuffisante"
        elif needs_second_order:
            status = f"Flambement à considérer (λ={lambda_calc:.0f} > λ_lim={lambda_lim:.0f})"
        else:
            status = "OK (λ < λ_lim)"
        
        return {
            "N_Ed": N_Ed,
            "L_0": L_0,
            "section": f"{a*100:.0f}×{b*100:.0f} cm",
            "lambda": lambda_calc,
            "lambda_lim": lambda_lim,
            "e_1": e_1,
            "e_2": e_2,
            "e_tot": e_tot,
            "M_Ed_amp": M_Ed_amp,
            "As_required": As_required,
            "As_required_cm2": As_required / 100 if As_required >= 0 else -1,
            "As_min_cm2": As_min / 100,
            "needs_second_order": needs_second_order,
            "status": status
        }
