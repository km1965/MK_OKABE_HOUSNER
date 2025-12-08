from core.mononobe import MononobeOkabe, WallGeometry, SoilParameters, SeismicParameters
from core.ec8_france import EC8France

def test_calc():
    print("Testing Mononobe-Okabe Calculation...")
    
    # Cas 1: Statique (kh=0, kv=0)
    # Mur de 5m, phi=30, delta=0, beta=0, i=0, gamma=18
    # Ka (Rankine) = (1-sin(30))/(1+sin(30)) = 0.5/1.5 = 1/3 ~= 0.333
    wall = WallGeometry(height=5.0)
    soil = SoilParameters(phi=30, delta=0, gamma=18)
    seismic = SeismicParameters(kh=0.0, kv=0.0)
    
    kae = MononobeOkabe.calculate_kae(wall, soil, seismic)
    print(f"Cas Statique (Rankine): Kae = {kae:.4f} (Attendu: 0.3333)")
    
    # Cas 2: Dynamique EC8 Zone 3, Sol C, Cat II
    # agr = 0.11g, gamma_I = 1.0, S = 1.5
    # kh = 0.11 * 1.0 * 1.5 / 2 = 0.0825
    kh = EC8France.calculate_kh(zone="3", category="II", soil_class="C", r_factor=2.0)
    print(f"EC8 Zone 3, Sol C, Cat II -> kh = {kh:.4f}")
    
    seismic_dyn = SeismicParameters(kh=kh, kv=0.0)
    kae_dyn = MononobeOkabe.calculate_kae(wall, soil, seismic_dyn)
    print(f"Cas Dynamique (kh={kh:.4f}): Kae = {kae_dyn:.4f}")
    
    pae = MononobeOkabe.calculate_pae(kae_dyn, wall, soil, seismic_dyn)
    print(f"Poussée totale Pae = {pae:.2f} kN/m")

if __name__ == "__main__":
    test_calc()
