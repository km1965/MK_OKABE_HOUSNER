"""
Test de l'analyse paramétrique
"""
from core.analysis import ParametricAnalyzer

def test_analysis():
    print("="*70)
    print(" TEST ANALYSE PARAMÉTRIQUE")
    print("="*70)
    
    # Inputs de base
    base_inputs = {
        'height': 10.0,
        'beta': 0.0,
        'backfill_slope': 0.0,
        'phi': 30.0,
        'delta': 20.0,
        'gamma': 18.0,
        'seismic_code': 'EC8',
        'zone': '3',
        'importance': 'II',
        'soil_class': 'C',
        'r_factor': 2.0,
        'has_water': True,
        'hw': 5.0,
        'L': 10.0,
        'gamma_w': 10.0,
        'combination_method': 'SRSS'
    }
    
    analyzer = ParametricAnalyzer(base_inputs)
    
    # Test 1: Variation Hauteur d'eau
    print("\n1. Variation Hauteur d'eau (0 à 10m)")
    results = analyzer.run_analysis('hw', 0.0, 10.0, steps=5)
    
    print(f"{'hw (m)':<10} | {'Pae (kN/m)':<12} | {'Pw (kN/m)':<12} | {'Ptotal (kN/m)':<12}")
    print("-" * 55)
    
    for i in range(len(results['x_values'])):
        print(f"{results['x_values'][i]:<10.2f} | {results['pae'][i]:<12.2f} | {results['pw'][i]:<12.2f} | {results['ptotal'][i]:<12.2f}")
        
    # Vérification
    if results['pw'][-1] > results['pw'][0]:
        print("\n✅ Pw augmente avec hw (Correct)")
    else:
        print("\n❌ Erreur: Pw n'augmente pas")
        
    # Test 2: Variation Angle de frottement
    print("\n2. Variation Angle de frottement (20° à 40°)")
    results_phi = analyzer.run_analysis('phi', 20.0, 40.0, steps=5)
    
    print(f"{'phi (°)':<10} | {'Pae (kN/m)':<12}")
    print("-" * 30)
    
    for i in range(len(results_phi['x_values'])):
        print(f"{results_phi['x_values'][i]:<10.2f} | {results_phi['pae'][i]:<12.2f}")
        
    if results_phi['pae'][-1] < results_phi['pae'][0]:
        print("\n✅ Pae diminue quand phi augmente (Correct)")
    else:
        print("\n❌ Erreur: Pae ne diminue pas")

    print("\n" + "="*70)
    print(" TEST TERMINÉ")
    print("="*70)

if __name__ == "__main__":
    test_analysis()
