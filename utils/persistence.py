"""
Module de gestion de la persistance des projets (Sauvegarde/Chargement)
"""
import json
import os
from datetime import datetime

class ProjectManager:
    """Gère la sauvegarde et le chargement des projets"""
    
    @staticmethod
    def save_project(data: dict, filepath: str) -> bool:
        """
        Sauvegarde les données du projet dans un fichier JSON
        
        :param data: Dictionnaire des données à sauvegarder
        :param filepath: Chemin du fichier de destination
        :return: True si succès, False sinon
        """
        try:
            # Ajouter des métadonnées
            save_data = {
                'metadata': {
                    'version': '2.0',
                    'date': datetime.now().isoformat(),
                    'software': 'Mononobe-Okabe Calculator'
                },
                'inputs': data
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=4, ensure_ascii=False)
            return True
            
        except Exception as e:
            print(f"Erreur lors de la sauvegarde : {e}")
            return False
    
    @staticmethod
    def load_project(filepath: str) -> dict:
        """
        Charge un projet depuis un fichier JSON
        
        :param filepath: Chemin du fichier source
        :return: Dictionnaire des données d'entrée ou None si erreur
        """
        try:
            if not os.path.exists(filepath):
                return None
                
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Vérification basique du format
            if 'inputs' in data:
                return data['inputs']
            else:
                # Support rétrocompatible si format plat (v1)
                return data
                
        except Exception as e:
            print(f"Erreur lors du chargement : {e}")
            return None
