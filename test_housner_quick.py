"""
Test rapide du module Housner
"""
from core.housner import Housner, WaterParameters

def quick_test():
    print("Test Housner - Masses et Périodes")
    print("="*50)
    
    # Cas test: Réservoir 10m × 6m d'eau
    water = WaterParameters(hw=6.0, L=10.0, gamma_w=10.0)
    
    print(f"\nParamètres:")
    print(f"  hw = {water.hw} m")
    print(f"  L = {water.L} m")
    print(f"  γw = {water.gamma_w} kN/m³")
    
    mi = Housner.calculate_impulsive_mass(water)
    mc = Housner.calculate_convective_mass(water)
    m_total = mi + mc
    m_theorie = water.rho_w * water.L * water.hw
    
    print(f"\nMasses:")
    print(f"  mi (impulsive) = {mi:.2f} t/m")
    print(f"  mc (convective) = {mc:.2f} t/m")
    print(f"  Total = {m_total:.2f} t/m")
    print(f"  Théorie (ρ×L×hw) = {m_theorie:.2f} t/m")
    print(f"  Vérification: {abs(m_total - m_theorie) < 0.01}")
    
    Tc = Housner.calculate_convective_period(water)
    print(f"\nPériode:")
    print(f"  Tc = {Tc:.3f} s")
    
    # Calcul des pressions avec kh = 0.15
    Ai = 0.15 * 9.81  # m/s²
    Ac = 0.05 * 9.81  # m/s² (exemple longue période)
    
    Pi = Housner.calculate_impulsive_pressure(water, Ai)
    Pc = Housner.calculate_convective_pressure(water, Ac)
    Pw_SRSS = Housner.calculate_total_pressure(Pi, Pc, "SRSS")
    Pw_SUM = Housner.calculate_total_pressure(Pi, Pc, "SUM")
    
    print(f"\nPressions (Ai={Ai/9.81:.2f}g, Ac={Ac/9.81:.2f}g):")
    print(f"  Pi = {Pi:.2f} kN/m")
    print(f"  Pc = {Pc:.2f} kN/m")
    print(f"  Pw (SRSS) = {Pw_SRSS:.2f} kN/m")
    print(f"  Pw (SUM) = {Pw_SUM:.2f} kN/m")
    
    hi = Housner.get_impulsive_height(water)
    hc = Housner.get_convective_height(water)
    
    print(f"\nHauteurs d'application:")
    print(f"  hi = {hi:.2f} m")
    print(f"  hc = {hc:.2f} m")
    
    print("\n" + "="*50)
    print("✅ Test réussi !")

if __name__ == "__main__":
    quick_test()
