"""
Tests unitaires pour le module tank_verifications
"""
import unittest
import math
from core.tank_verifications import (
    TankVerifications, 
    ConcreteProperties, 
    SteelProperties, 
    SectionProperties,
    LoadCombinations
)

class TestTankVerifications(unittest.TestCase):
    """Tests pour les vérifications de bâches à eau"""
    
    def test_check_sliding_ok(self):
        """Test glissement avec marge suffisante"""
        result = TankVerifications.check_sliding(
            V_horizontal=50.0,
            W_total=200.0,
            friction_coef=0.5
        )
        self.assertGreaterEqual(result['Fs_glissement'], 1.5)
        self.assertEqual(result['status'], "OK")
    
    def test_check_sliding_fail(self):
        """Test glissement insuffisant"""
        result = TankVerifications.check_sliding(
            V_horizontal=100.0,
            W_total=100.0,
            friction_coef=0.5
        )
        self.assertLess(result['Fs_glissement'], 1.5)
        self.assertEqual(result['status'], "NON VÉRIFIÉ")
    
    def test_check_bearing_trapeze(self):
        """Test portance avec excentrement faible (trapèze)"""
        result = TankVerifications.check_bearing_capacity(
            N_total=500.0,
            M_total=50.0,
            L=5.0,
            B=4.0,
            sigma_adm=200.0
        )
        self.assertLess(result['sigma_max'], 200.0)
        self.assertEqual(result['status'], "OK")
    
    def test_check_bearing_triangle(self):
        """Test portance avec fort excentrement (triangle)"""
        result = TankVerifications.check_bearing_capacity(
            N_total=100.0,
            M_total=100.0,  # Fort moment
            L=5.0,
            B=2.0,
            sigma_adm=200.0
        )
        # Excentricité > B/6, distribution triangulaire
        self.assertGreater(result['excentricite'], result['e_limite'])
    
    def test_reinforcement_simple_flexure(self):
        """Test ferraillage flexion simple"""
        concrete = ConcreteProperties(fc28=25.0)
        steel = SteelProperties(fyk=500.0)
        section = SectionProperties(h=0.25, enrobage=0.04)
        
        result = TankVerifications.calculate_flexural_reinforcement(
            M_Ed=50.0,  # kNm
            section=section,
            concrete=concrete,
            steel=steel
        )
        
        # As doit être positif et raisonnable
        self.assertGreater(result['As_required_cm2'], 0)
        self.assertLess(result['As_required_cm2'], 50)  # < 50 cm²/m
        self.assertEqual(result['status'], "OK")
    
    def test_reinforcement_minimum(self):
        """Test ferraillage minimum (faible moment)"""
        concrete = ConcreteProperties(fc28=25.0)
        steel = SteelProperties(fyk=500.0)
        section = SectionProperties(h=0.30, enrobage=0.04)
        
        result = TankVerifications.calculate_flexural_reinforcement(
            M_Ed=5.0,  # Très faible moment
            section=section,
            concrete=concrete,
            steel=steel
        )
        
        # Doit retourner au moins As_min
        self.assertGreaterEqual(result['As_required'], result['As_min'])
    
    def test_shear_no_reinforcement(self):
        """Test effort tranchant sans armatures"""
        concrete = ConcreteProperties(fc28=25.0)
        section = SectionProperties(h=0.25, enrobage=0.04)
        
        result = TankVerifications.check_shear(
            V_Ed=30.0,  # kN
            section=section,
            concrete=concrete,
            As_long=500  # mm²
        )
        
        self.assertIn(result['status'], ["OK", "Armatures transversales requises"])

class TestLoadCombinations(unittest.TestCase):
    """Tests pour les combinaisons de charges"""
    
    def test_uls_fundamental(self):
        """Test ELU fondamental"""
        result = LoadCombinations.get_uls_fundamental(G=100, Q=50)
        expected = 1.35 * 100 + 1.5 * 50
        self.assertAlmostEqual(result, expected)
    
    def test_uls_seismic(self):
        """Test ELU sismique"""
        result = LoadCombinations.get_uls_seismic(G=100, E=50, Q=30, psi_2=0.3)
        expected = 100 + 50 + 0.3 * 30
        self.assertAlmostEqual(result, expected)
    
    def test_sls_qp(self):
        """Test ELS quasi-permanent"""
        result = LoadCombinations.get_sls_qp(G=100, Q=50, psi_2=0.3)
        expected = 100 + 0.3 * 50
        self.assertAlmostEqual(result, expected)

class TestConcreteProperties(unittest.TestCase):
    """Tests pour les propriétés béton"""
    
    def test_fcd_calculation(self):
        """Test résistance de calcul fcd"""
        concrete = ConcreteProperties(fc28=25.0)
        expected_fcd = 0.85 * 25.0 / 1.5
        self.assertAlmostEqual(concrete.fcd, expected_fcd)
    
    def test_fctm_calculation(self):
        """Test résistance traction fctm"""
        concrete = ConcreteProperties(fc28=25.0)
        expected_fctm = 0.30 * 25.0**(2/3)
        self.assertAlmostEqual(concrete.fctm, expected_fctm, places=2)

if __name__ == '__main__':
    unittest.main()
