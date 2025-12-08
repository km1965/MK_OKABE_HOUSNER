# Diagnostic de Problème - GUI Calcul

## Symptôme
L'application s'ouvre mais les calculs ne s'exécutent pas quand on clique sur CALCULER.

## Tests Effectués

### ✅ Test Calcul de Base
```bash
python test_simple.py
```
**Résultat** : ✅ Fonctionne parfaitement
- kh = 0.0825
- Kae = 0.3527
- Pae = 79.36 kN/m

→ Le moteur de calcul fonctionne !

## Hypothèses

### 1. Problème de récupération des valeurs
La méthode `get_values()` existe bien dans `inputs.py` (lignes 261-280)

### 2. Exception silencieuse
Le try/except dans `calculate()` pourrait masquer une erreur

### 3. Widgets non créés
Certains widgets n'existent peut-être pas, causant KeyError

## Actions de Debug Nécessaires

Besoin de savoir **exactement** ce qui se passe quand on clique sur CALCULER :

1. ❓ Rien ne se passe ?
2. ❓ Message d'erreur affiché ?
3. ❓ L'app se fige ?
4. ❓ Les résultats ne s'affichent pas ?

**Vérifier** : Y a-t-il des messages dans le terminal où `python main.py` est lancé ?

## Solutions Potentielles

### Option 1 : Ajouter des prints de debug
```python
def calculate(self):
    print("[DEBUG] Bouton cliqué")
    try:
        values = self.input_frame.get_values()
        print(f"[DEBUG] Valeurs: {values}")
        # ...
    except Exception as e:
        print(f"[ERROR] {e}")
```

### Option 2 : Vérifier les widgets requis
S'assurer que tous les widgets utilisés dans `get_values()` existent bien.

### Option 3 : Tester avec valeurs par défaut
Créer un test qui appelle directement `calculate()` avec des valeurs fixes.

---

**En attente de retour utilisateur pour diagnostiquer précisément le problème.**
