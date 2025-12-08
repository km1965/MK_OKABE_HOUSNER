# 📐 MK_OKABE_HOUSNER - Application de Calcul Sismique

## 🎯 Description

Application Python professionnelle pour le calcul de la **poussée sismique** et le **dimensionnement de bâches à eau / réservoirs enterrés** selon les normes EC8 et RPS 2011.

![Version](https://img.shields.io/badge/version-3.0-blue)
![Python](https://img.shields.io/badge/Python-3.10+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

---

## ✨ Fonctionnalités

### 🧱 Module Mur de Soutènement
| Méthode | Description |
|---------|-------------|
| **Mononobe-Okabe** | Poussée dynamique des terres |
| **Housner** | Poussée hydrodynamique (impulsive + convective) |
| **Stabilité** | Glissement, renversement, portance |

### 🏗️ Module Bâche à Eau / Cadre BA
| Fonctionnalité | Description |
|----------------|-------------|
| **Analyse Structurale** | Cadre fermé avec enveloppe de cas de charges |
| **Structure Semi-Enterrée** | Voiles enterrés + poteaux émergents |
| **Vérifications RPS 2011** | Effort tranchant base, renversement, déplacements |
| **Vérifications EC2** | Flexion, cisaillement, fissuration, poinçonnement |
| **Export PDF** | Rapport complet avec diagrammes des moments |

### 📋 Normes Sismiques
- 🇫🇷 **EC8 France** (Eurocode 8 - Annexe Nationale)
- 🇲🇦 **RPS 2011 Maroc** (Règlement Parasismique Marocain)

---

## 🚀 Installation

### Prérequis
- Python 3.10 ou supérieur
- pip

### Installation
```bash
git clone https://github.com/VOTRE_USERNAME/MK_OKABE_HOUSNER.git
cd MK_OKABE_HOUSNER
pip install -r requirements.txt
```

### Lancement
```bash
python main.py
```

### Exécutable Windows
L'exécutable `MK_OKABE_HOUSNER.exe` est disponible dans le dossier `dist/`.

---

## 📊 Vérifications Implémentées

### Analyse Sismique RPS 2011
```
V_base = (A × D × I × S / K) × W
```
- Effort tranchant de base
- Renversement (Fs ≥ 1.5)
- Déplacements (δ ≤ H/200)

### Vérifications Radier (EC2)
- Rigidité (L/e → Rigide/Semi-rigide/Souple)
- Poinçonnement (vEd ≤ vRd,c)
- Soulèvement / Flottaison

### Vérifications Voiles (EC2)
- Flexion composée (N + M)
- Cisaillement (VEd ≤ VRd,c + Asw si nécessaire)
- Fissuration (wk ≤ 0.2mm pour étanchéité)
- Interface voile-radier (armatures de couture)

### Vérifications Poteaux (EC2 5.8)
- Élancement λ et λ_lim
- Effets du 2nd ordre (e₂)
- Armatures en flexion composée

---

## 📁 Structure du Projet

```
MK_OKABE_HOUSNER/
├── main.py                     # Point d'entrée
├── requirements.txt            # Dépendances
├── README.md                   # Documentation
│
├── core/                       # 🧮 Moteur de calcul
│   ├── mononobe.py            # Mononobe-Okabe
│   ├── housner.py             # Housner (hydrodynamique)
│   ├── ec8_france.py          # EC8 France + Spectre
│   ├── rps2011_maroc.py       # RPS 2011 Maroc
│   ├── frame_analysis.py      # Analyse cadre BA
│   ├── tank_verifications.py  # Vérifications complètes
│   └── stability.py           # Stabilité globale
│
├── gui/                        # 🎨 Interface graphique
│   ├── app.py                 # Fenêtre principale
│   ├── inputs.py              # Formulaire mur
│   ├── tank_inputs.py         # Formulaire bâche
│   └── results.py             # Affichage résultats
│
├── utils/                      # 🛠️ Utilitaires
│   ├── report_generator.py    # Génération PDF
│   └── persistence.py         # Sauvegarde/Chargement
│
├── tests/                      # 🧪 Tests unitaires
│
└── dist/                       # 📦 Exécutable
    └── MK_OKABE_HOUSNER.exe
```

---

## 🖼️ Captures d'Écran

### Interface Principale
- Onglet **Mur de Soutènement** : Calcul Mononobe-Okabe + Housner
- Onglet **Bâche à Eau / Cadre** : Analyse structurale complète

### Rapport PDF
- Données d'entrée
- Poussée dynamique (Mononobe-Okabe)
- Pression hydrodynamique (Housner)
- Ferraillage et vérifications
- Diagramme des moments

---

## 📚 Références

### Normes
- **EN 1998-1:2004** - Eurocode 8 : Spectre de réponse
- **EN 1998-4:2006** - Eurocode 8 : Réservoirs (Housner)
- **EN 1998-5:2004** - Eurocode 8 : Murs de soutènement
- **EN 1992-1-1** - Eurocode 2 : Béton armé
- **RPS 2011** - Règlement Parasismique Marocain

### Publications
- **Housner, G.W. (1963)** - "The dynamic behavior of water tanks"
- **Mononobe & Matsuo (1929)** - Earthquake resistant design of earth dams
- **Okabe (1926)** - General theory on earth pressure

---

## 🛠️ Technologies

- **Python 3.10+**
- **CustomTkinter** - Interface graphique moderne
- **NumPy** - Calculs numériques
- **Matplotlib** - Visualisations
- **ReportLab** - Génération PDF
- **PyInstaller** - Création exécutable

---

## 📝 Licence

MIT License - Voir [LICENSE](LICENSE)

---

**Version** : 3.0  
**Date** : Décembre 2024  
**Auteur** : Développé avec ❤️ pour les ingénieurs génie civil

---

⚠️ **Note** : Cette application est un outil d'aide au calcul. Les résultats doivent être vérifiés par un ingénieur qualifié.
