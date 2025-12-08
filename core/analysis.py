"""
Module d'analyse paramétrique pour l'étude de sensibilité
"""
import numpy as np
from core.mononobe import MononobeOkabe, WallGeometry, SoilParameters, SeismicParameters
from core.housner import Housner, WaterParameters
from core.ec8_france import EC8France

class ParametricAnalyzer:
    """Gère l'exécution des analyses paramétriques"""
    
    def __init__(self, base_inputs: dict):
        """
        Initialise l'analyseur avec les paramètres de base
        
        :param base_inputs: Dictionnaire des entrées actuelles de l'application
        """
        self.base_inputs = base_inputs.copy()
        
    def run_analysis(self, param_name: str, min_val: float, max_val: float, steps: int = 20) -> dict:
        """
        Exécute l'analyse en faisant varier un paramètre
        
        :param param_name: Nom du paramètre à faire varier ('height', 'hw', 'phi', 'kh')
        :param min_val: Valeur minimale
        :param max_val: Valeur maximale
        :param steps: Nombre de points de calcul
        :return: Dictionnaire des résultats (listes)
        """
        # Générer les valeurs du paramètre
        x_values = np.linspace(min_val, max_val, steps)
        
        results = {
            'x_values': x_values,
            'param_name': param_name,
            'pae': [],
            'pw': [],
            'ptotal': [],
            'kae': []
        }
        
        for val in x_values:
            # Créer une copie des inputs pour ce pas de calcul
            current_inputs = self.base_inputs.copy()
            current_inputs[param_name] = val
            
            # Si on varie H, on doit vérifier hw (hw ne peut pas dépasser H)
            if param_name == 'height' and current_inputs.get('has_water'):
                if current_inputs['hw'] > val:
                    current_inputs['hw'] = val
            
            # Si on varie hw, on doit s'assurer que has_water est True
            if param_name == 'hw':
                current_inputs['has_water'] = True
                # hw ne peut pas dépasser H
                if val > current_inputs['height']:
                    # On pourrait clipper, mais ici on laisse le calcul se faire 
                    # (Housner gère théoriquement, mais physiquement impossible)
                    pass
            
            # Exécuter le calcul pour ce point
            res = self._calculate_point(current_inputs)
            
            results['pae'].append(res['pae'])
            results['pw'].append(res['Pw'])
            results['ptotal'].append(res['Ptotal'])
            results['kae'].append(res['kae'])
            
        return results
    
    def _calculate_point(self, inputs: dict) -> dict:
        """Effectue un calcul unique pour un jeu de paramètres"""
        
        # 1. Objets Core
        wall = WallGeometry(
            height=inputs['height'],
            batter_angle=inputs['beta'],
            backfill_slope=inputs['backfill_slope']
        )
        
        soil = SoilParameters(
            phi=inputs['phi'],
            delta=inputs['delta'],
            gamma=inputs['gamma']
        )
        
        # 2. Sismique
        # Si on varie kh directement (analyse de sensibilité sismique)
        if 'kh_manual' in inputs:
            kh = inputs['kh_manual']
            kv = inputs.get('kv_manual', 0.0)
        else:
            # Sinon calcul standard selon norme
            # Note: Ici on simplifie en recalculant kh à chaque fois si nécessaire
            # Mais pour l'analyse paramétrique, souvent on fixe kh ou on le laisse varier avec la zone
            
            # Pour simplifier, on recalcule kh si les paramètres sismiques changent
            # Mais si on fait varier H, phi, etc., kh reste constant (sauf si T change pour spectre)
            
            # On récupère kh déjà calculé ou on le recalcule
            if inputs.get('seismic_code') == 'EC8':
                kh = EC8France.calculate_kh(
                    inputs['zone'], inputs['importance'], 
                    inputs['soil_class'], inputs['r_factor']
                )
            else:
                # Pour RPS, on suppose kh déjà dans inputs ou on utilise une valeur par défaut
                kh = inputs.get('kh', 0.1) # Fallback
                
            kv = 0.3 * kh if inputs.get('use_kv', True) else 0.0
            
        # Override si c'est le paramètre variable
        if 'kh' in inputs: # Si kh est passé explicitement (cas variation kh)
             # Attention: inputs['kh'] est écrasé par le calcul ci-dessus si on ne fait pas attention
             # Dans run_analysis, on met à jour inputs[param_name].
             # Si param_name est 'kh', alors inputs['kh'] contient la valeur variable.
             pass
             
        seismic = SeismicParameters(kh=inputs.get('kh', kh), kv=inputs.get('kv', kv))
        
        # 3. Mononobe-Okabe
        kae = MononobeOkabe.calculate_kae(wall, soil, seismic)
        pae = MononobeOkabe.calculate_pae(kae, wall, soil, seismic)
        
        # 4. Housner (si eau)
        Pw = 0.0
        if inputs.get('has_water', False):
            water = WaterParameters(
                hw=inputs['hw'],
                L=inputs['L'],
                gamma_w=inputs['gamma_w']
            )
            
            # Calculs masses/périodes
            Tc = Housner.calculate_convective_period(water)
            
            # Accélérations
            Ai = seismic.kh * 9.81
            
            # Spectre pour Ac
            if inputs.get('seismic_code') == 'EC8':
                Ac_g = EC8France.get_spectral_acceleration(
                    Tc, inputs['zone'], inputs['importance'], inputs['soil_class']
                )
            else:
                # Approx RPS
                Ac_g = seismic.kh * (0.4 if Tc > 1.0 else 0.7)
                
            Ac = Ac_g * 9.81
            
            # Pressions
            Pi = Housner.calculate_impulsive_pressure(water, Ai)
            Pc = Housner.calculate_convective_pressure(water, Ac)
            
            # Combinaison
            method = inputs.get('combination_method', 'SRSS')
            Pw = Housner.calculate_total_pressure(Pi, Pc, method)
            
        return {
            'kae': kae,
            'pae': pae,
            'Pw': Pw,
            'Ptotal': pae + Pw
        }
