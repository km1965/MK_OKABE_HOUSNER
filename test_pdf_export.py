"""
Test de l'export PDF
"""
from core.mononobe import MononobeOkabe, WallGeometry, SoilParameters, SeismicParameters
from core.housner import Housner, WaterParameters
from core.ec8_france import EC8France
from utils.report_generator import PDFReportGenerator
from datetime import datetime

def test_pdf_export():
    print("="*70)
    print(" TEST EXPORT PDF")
    print("="*70)
    
    # Cas test avec eau
    wall = WallGeometry(height=8.0, batter_angle=0, backfill_slope=0)
    soil = SoilParameters(phi=35, delta=23, gamma=19)
    
    zone, category, soil_class = "3", "II", "C"
    r_factor = 2.0
    
    kh = EC8France.calculate_kh(zone, category, soil_class, r_factor)
    kv = 0.0
    
    seismic = SeismicParameters(kh=kh, kv=kv)
    
    # Mononobe-Okabe
    kae = MononobeOkabe.calculate_kae(wall, soil, seismic)
    pae = MononobeOkabe.calculate_pae(kae, wall, soil, seismic)
    
    # Housner
    water = WaterParameters(hw=6.0, L=12.0, gamma_w=10.0)
    mi = Housner.calculate_impulsive_mass(water)
    mc = Housner.calculate_convective_mass(water)
    Tc = Housner.calculate_convective_period(water)
    
    Ai = kh * 9.81
    Ac_g = EC8France.get_spectral_acceleration(Tc, zone, category, soil_class)
    Ac = Ac_g * 9.81
    
    Pi = Housner.calculate_impulsive_pressure(water, Ai)
    Pc = Housner.calculate_convective_pressure(water, Ac)
    Pw = Housner.calculate_total_pressure(Pi, Pc, "SRSS")
    
    hi = Housner.get_impulsive_height(water)
    hc = Housner.get_convective_height(water)
    
    # Préparer les résultats
    results = {
        'height': 8.0,
        'beta': 0.0,
        'backfill_slope': 0.0,
        'phi': 35,
        'delta': 23,
        'gamma': 19,
        'zone': zone,
        'importance': category,
        'soil_class': soil_class,
        'r_factor': r_factor,
        'seismic_code': 'EC8',
        'kh': kh,
        'kv': kv,
        'theta': seismic.theta * 180/3.14159,
        'kae': kae,
        'pae': pae,
        'has_water': True,
        'hw': 6.0,
        'L': 12.0,
        'gamma_w': 10.0,
        'combination_method': 'SRSS',
        'mi': mi,
        'mc': mc,
        'Tc': Tc,
        'Pi': Pi,
        'Pc': Pc,
        'Pw': Pw,
        'hi': hi,
        'hc': hc,
        'Ptotal': pae + Pw
    }
    
    # Générer le PDF
    filename = f"Test_Note_Calcul_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    print(f"\n[PDF] Generation du PDF : {filename}")
    
    generator = PDFReportGenerator(filename)
    
    # Page de garde
    project_info = {
        'title': 'NOTE DE CALCUL - TEST',
        'date': datetime.now().strftime('%d/%m/%Y %H:%M'),
        'code': 'EC8 France 🇫🇷'
    }
    generator.add_cover_page(project_info)
    
    # Données d'entrée
    generator.add_input_section(results)
    
    # Résultats
    generator.add_results_section(results)
    
    # Références
    generator.add_references()
    
    # Génération
    pdf_path = generator.generate()
    
    print(f"\n[OK] PDF genere avec succes : {pdf_path}")
    print("\n" + "="*70)
    print(" TEST TERMINÉ")
    print("="*70)

if __name__ == "__main__":
    test_pdf_export()
