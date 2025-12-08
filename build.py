import PyInstaller.__main__
import customtkinter
import os
import sys

# Récupérer le chemin de CustomTkinter
ctk_path = os.path.dirname(customtkinter.__file__)

print(f"CustomTkinter path: {ctk_path}")

# Définir les arguments PyInstaller
args = [
    'main.py',                       # Script principal
    '--name=MK_OKABE_HOUSNER',       # Nom de l'exécutable
    '--noconfirm',                   # Ne pas demander confirmation pour écraser
    '--windowed',                    # Mode fenêtre (pas de console)
    '--clean',                       # Nettoyer le cache
    # Inclure CustomTkinter (dossier source -> destination dans l'exe)
    f'--add-data={ctk_path}{os.pathsep}customtkinter',
    # Inclure les dossiers du projet
    f'--add-data=core{os.pathsep}core',
    f'--add-data=gui{os.pathsep}gui',
    f'--add-data=utils{os.pathsep}utils',
    # Icône
    '--icon=icone.ico',
]

print("Lancement du build PyInstaller...")
print(f"Arguments: {args}")

# Lancer le build
PyInstaller.__main__.run(args)

print("\nBuild terminé ! L'exécutable se trouve dans le dossier 'dist'.")
