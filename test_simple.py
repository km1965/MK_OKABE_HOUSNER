"""
Test simple pour vérifier le calcul
"""
from core.mononobe import MononobeOkabe, WallGeometry, SoilParameters, SeismicParameters
from core.ec8_france import EC8France

try:
    print("Test calcul simple...")
    
    # Créer objets
    wall = WallGeometry(height=5.0, batter_angle=0, backfill_slope=0)
    soil = SoilParameters(phi=30, delta=20, gamma=18)
    
    # EC8
    kh = EC8France.calculate_kh(zone="3", category="II", soil_class="C", r_factor=2.0)
    kv = 0.0
    
    seismic = SeismicParameters(kh=kh, kv=kv)
    
    # Calculer
    kae = MononobeOkabe.calculate_kae(wall, soil, seismic)
    pae = MononobeOkabe.calculate_pae(kae, wall, soil, seismic)
    
    print(f"kh = {kh:.4f}")
    print(f"Kae = {kae:.4f}")
    print(f"Pae = {pae:.2f} kN/m")
    print("\n[OK] Calcul fonctionne!")
    
except Exception as e:
    print(f"\n[ERREUR] {e}")
    import traceback
    traceback.print_exc()
