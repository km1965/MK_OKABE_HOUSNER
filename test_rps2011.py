"""
Test de validation du module RPS 2011 Maroc
"""
from core.mononobe import MononobeOkabe, WallGeometry, SoilParameters, SeismicParameters
from core.rps2011_maroc import RPS2011Maroc
from core.ec8_france import EC8France

def test_rps2011():
    print("="*70)
    print(" TEST RPS 2011 MAROC - Calcul Mononobe-Okabe")
    print("="*70)
    
    # Cas test: Mur de 6m à Casablanca (Zone 2)
    print("\n📍 CAS TEST: Mur de soutènement à Casablanca")
    print("-" * 70)
    
    wall = WallGeometry(height=6.0, batter_angle=0, backfill_slope=0)
    soil = SoilParameters(phi=35, delta=23, gamma=19)
    
    # Paramètres RPS 2011
    zone = "2"
    classe = "II"
    site = "S3"
    r_factor = 2.0
    
    print(f"\nParamètres géométriques:")
    print(f"  - H = {wall.H} m")
    print(f"  - β = {wall.beta:.1f}° (vertical)")
    print(f"  - i = {wall.i:.1f}° (horizontal)")
    
    print(f"\nParamètres du sol:")
    print(f"  - φ = 35°")
    print(f"  - δ = 23°")
    print(f"  - γ = 19 kN/m³")
    
    print(f"\nParamètres sismiques RPS 2011:")
    print(f"  - Zone: {zone} ({RPS2011Maroc.get_zone_name(zone)})")
    print(f"  - Classe d'importance: {classe}")
    print(f"  - Site: {site}")
    print(f"  - Coefficient R: {r_factor}")
    
    # Calcul des coefficients
    kh = RPS2011Maroc.calculate_kh(zone, classe, site, r_factor)
    kv = RPS2011Maroc.calculate_kv(kh)
    
    print(f"\n📊 Coefficients sismiques calculés:")
    print(f"  - kh = {kh:.4f}")
    print(f"  - kv = {kv:.4f} (= 0.3 × kh)")
    
    # Calcul Mononobe-Okabe
    seismic = SeismicParameters(kh=kh, kv=kv)
    
    print(f"  - θ (angle sismique) = {seismic.theta * 180/3.14159:.2f}°")
    
    kae = MononobeOkabe.calculate_kae(wall, soil, seismic)
    pae = MononobeOkabe.calculate_pae(kae, wall, soil, seismic)
    
    print(f"\n🎯 RÉSULTATS:")
    print(f"  - Kae (coefficient dynamique) = {kae:.4f}")
    print(f"  - Pae (poussée totale)        = {pae:.2f} kN/m")
    print(f"  - Point d'application         = {wall.H/3:.2f} m depuis la base")
    
    # Comparaison avec EC8 pour la même configuration
    print("\n" + "="*70)
    print(" COMPARAISON EC8 France (Zone 3)")
    print("="*70)
    
    kh_ec8 = EC8France.calculate_kh(zone="3", category="II", soil_class="C", r_factor=2.0)
    kv_ec8 = EC8France.calculate_kv(kh_ec8, "3")
    
    seismic_ec8 = SeismicParameters(kh=kh_ec8, kv=kv_ec8)
    kae_ec8 = MononobeOkabe.calculate_kae(wall, soil, seismic_ec8)
    pae_ec8 = MononobeOkabe.calculate_pae(kae_ec8, wall, soil, seismic_ec8)
    
    print(f"\nEC8 France (Zone 3, Cat II, Sol C):")
    print(f"  - kh = {kh_ec8:.4f}")
    print(f"  - kv = {kv_ec8:.4f}")
    print(f"  - Kae = {kae_ec8:.4f}")
    print(f"  - Pae = {pae_ec8:.2f} kN/m")
    
    print(f"\nÉcart relatif:")
    print(f"  - Δkh = {abs(kh - kh_ec8):.4f} ({abs(kh - kh_ec8)/kh_ec8*100:.1f}%)")
    print(f"  - ΔKae = {abs(kae - kae_ec8):.4f}")
    print(f"  - ΔPae = {abs(pae - pae_ec8):.2f} kN/m ({abs(pae - pae_ec8)/pae_ec8*100:.1f}%)")
    
    print("\n" + "="*70)
    print(" ✅ TEST TERMINÉ AVEC SUCCÈS")
    print("="*70)

if __name__ == "__main__":
    test_rps2011()
