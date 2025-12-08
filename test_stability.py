"""
Test du module de stabilité
"""
from core.stability import StabilityVerifier

def test_stability():
    print("="*70)
    print(" TEST VÉRIFICATION STABILITÉ")
    print("="*70)
    
    # Cas 1: Mur stable
    print("\n1. Cas Mur Stable (Lourd et Large)")
    wall_params = {
        'width_B': 4.0,
        'weight_W': 200.0,  # Mur lourd
        'friction_base': 30.0,
        'cohesion_base': 0.0,
        'height': 5.0
    }
    
    forces = {
        'Pae_h': 50.0,  # Poussée modérée
        'Pae_v': 10.0,
        'Pw': 0.0,
        'h_Pae': 1.67,  # H/3
        'height': 5.0
    }
    
    seismic = {'kh': 0.1, 'kv': 0.0}
    
    verifier = StabilityVerifier(wall_params, forces, seismic)
    
    sliding = verifier.check_sliding()
    print(f"Glissement Fs: {sliding['Fs']:.2f} (Attendu > 1.5) -> {sliding['status']}")
    
    overturning = verifier.check_overturning()
    print(f"Renversement Fr: {overturning['Fr']:.2f} (Attendu > 1.5) -> {overturning['status']}")
    
    bearing = verifier.check_bearing()
    print(f"Excentrement e: {bearing['e']:.3f} m (Limite {4.0/3:.3f}) -> {bearing['status']}")
    
    # Cas 2: Mur Instable (Léger et Étroit)
    print("\n2. Cas Mur Instable (Léger et Étroit)")
    wall_params['width_B'] = 1.5
    wall_params['weight_W'] = 50.0
    
    verifier_unstable = StabilityVerifier(wall_params, forces, seismic)
    
    sliding = verifier_unstable.check_sliding()
    print(f"Glissement Fs: {sliding['Fs']:.2f} -> {sliding['status']}")
    
    overturning = verifier_unstable.check_overturning()
    print(f"Renversement Fr: {overturning['Fr']:.2f} -> {overturning['status']}")

    print("\n" + "="*70)
    print(" TEST TERMINÉ")
    print("="*70)

if __name__ == "__main__":
    test_stability()
