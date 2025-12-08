"""
Test complet Housner - Mur avec nappe phréatique
"""
from core.mononobe import MononobeOkabe, WallGeometry, SoilParameters, SeismicParameters
from core.housner import Housner, WaterParameters
from core.ec8_france import EC8France

def test_housner_complet():
    print("="*70)
    print(" TEST COMPLET HOUSNER - Mur avec eau")
    print("="*70)
    
    # Cas: Mur de quai H=8m, nappe hw=6m, L=12m
    print("\n📍 CAS: Mur de quai portuaire")
    print("-" * 70)
    
    wall = WallGeometry(height=8.0, batter_angle=0, backfill_slope=0)
    soil = SoilParameters(phi=35, delta=23, gamma=19)
    
    # Paramètres sismiques EC8 Zone 3
    zone, category, soil_class = "3", "II", "C"
    r_factor = 2.0
    
    kh = EC8France.calculate_kh(zone, category, soil_class, r_factor)
    kv = 0.0  # Simplifié
    
    seismic = SeismicParameters(kh=kh, kv=kv)
    
    # Calcul Mononobe-Okabe
    kae = MononobeOkabe.calculate_kae(wall, soil, seismic)
    pae = MononobeOkabe.calculate_pae(kae, wall, soil, seismic)
    
    print(f"\n🌍 Paramètres géométriques:")
    print(f"  H (mur) = {wall.H} m")
    print(f"  φ = 35°, δ = 23°, γ = 19 kN/m³")
    
    print(f"\n⚡ Séisme EC8 Zone 3, Cat II, Sol C:")
    print(f"  kh = {kh:.4f}")
    
    print(f"\n🏔️ POUSSÉE DES TERRES (Mononobe-Okabe):")
    print(f"  Kae = {kae:.4f}")
    print(f"  Pae = {pae:.2f} kN/m")
    
    # Calcul Housner
    water = WaterParameters(hw=6.0, L=12.0, gamma_w=10.0)
    
    print(f"\n💧 Paramètres eau:")
    print(f"  hw = {water.hw} m")
    print(f"  L = {water.L} m")
    
    mi = Housner.calculate_impulsive_mass(water)
    mc = Housner.calculate_convective_mass(water)
    Tc = Housner.calculate_convective_period(water)
    
    print(f"\n📊 Masses Housner:")
    print(f"  mi (impulsive) = {mi:.2f} t/m")
    print(f"  mc (convective) = {mc:.2f} t/m")
    print(f"  Tc (période convective) = {Tc:.2f} s")
    
    # Accélérations
    Ai = kh * 9.81
    Ac_g = EC8France.get_spectral_acceleration(Tc, zone, category, soil_class)
    Ac = Ac_g * 9.81
    
    print(f"\n⚡ Accélérations spectrales:")
    print(f"  Ai = {kh:.3f} g = {Ai:.2f} m/s²")
    print(f"  Ac (T={Tc:.2f}s) = {Ac_g:.3f} g = {Ac:.2f} m/s²")
    
    # Pressions
    Pi = Housner.calculate_impulsive_pressure(water, Ai)
    Pc = Housner.calculate_convective_pressure(water, Ac)
    Pw_SRSS = Housner.calculate_total_pressure(Pi, Pc, "SRSS")
    Pw_SUM = Housner.calculate_total_pressure(Pi, Pc, "SUM")
    
    hi = Housner.get_impulsive_height(water)
    hc = Housner.get_convective_height(water)
    
    print(f"\n🌊 POUSSÉE HYDRODYNAMIQUE (Housner):")
    print(f"\n  Impulsive:")
    print(f"    Pi = {Pi:.2f} kN/m à hi = {hi:.2f} m")
    print(f"\n  Convective:")
    print(f"    Pc = {Pc:.2f} kN/m à hc = {hc:.2f} m")
    print(f"\n  Total (SRSS): Pw = {Pw_SRSS:.2f} kN/m")
    print(f"  Total (SUM):  Pw = {Pw_SUM:.2f} kN/m (conservatif)")
    
    # Total
    Ptotal_SRSS = pae + Pw_SRSS
    Ptotal_SUM = pae + Pw_SUM
    
    print(f"\n🏆 POUSSÉE TOTALE SISMIQUE:")
    print(f"  Pae (terres) = {pae:.2f} kN/m")
    print(f"  Pw (eau SRSS) = {Pw_SRSS:.2f} kN/m")
    print(f"  ────────────────────────────")
    print(f"  Ptotal = {Ptotal_SRSS:.2f} kN/m")
    print(f"\n  (Méthode conservatrice SUM: {Ptotal_SUM:.2f} kN/m)")
    
    augmentation = ((Ptotal_SRSS - pae) / pae) * 100
    print(f"\n💡 Augmentation due à l'eau: +{augmentation:.1f}%")
    
    print("\n" + "="*70)
    print(" ✅ TEST TERMINÉ AVEC SUCCÈS")
    print("="*70)

if __name__ == "__main__":
    test_housner_complet()
