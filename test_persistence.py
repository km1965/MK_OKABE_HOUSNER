"""
Test de la persistance (Sauvegarde/Chargement)
"""
import os
import json
from utils.persistence import ProjectManager

def test_persistence():
    print("="*70)
    print(" TEST PERSISTANCE (JSON)")
    print("="*70)
    
    # Données de test
    test_data = {
        'height': 8.5,
        'beta': 5.0,
        'phi': 32.0,
        'seismic_code': 'RPS2011',
        'has_water': True,
        'hw': 4.0
    }
    
    filename = "test_project.json"
    
    # 1. Test Sauvegarde
    print("\n1. Test Sauvegarde...")
    if ProjectManager.save_project(test_data, filename):
        print("✅ Sauvegarde réussie")
    else:
        print("❌ Échec sauvegarde")
        return
        
    # Vérifier existence fichier
    if os.path.exists(filename):
        print(f"✅ Fichier {filename} créé")
    else:
        print("❌ Fichier non trouvé")
        return
        
    # 2. Test Chargement
    print("\n2. Test Chargement...")
    loaded_data = ProjectManager.load_project(filename)
    
    if loaded_data:
        print("✅ Données chargées")
        print(f"Données: {loaded_data}")
        
        # Vérifier contenu
        if loaded_data['height'] == 8.5 and loaded_data['seismic_code'] == 'RPS2011':
            print("✅ Contenu conforme")
        else:
            print("❌ Contenu incorrect")
    else:
        print("❌ Échec chargement")
        
    # Nettoyage
    try:
        os.remove(filename)
        print("\n✅ Fichier test nettoyé")
    except:
        pass

    print("\n" + "="*70)
    print(" TEST TERMINÉ")
    print("="*70)

if __name__ == "__main__":
    test_persistence()
