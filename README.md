# Code D2 v2

Cette archive contient le tableau de bord, les tables necessaires, les scripts v2/v3 et les tests. Les donnees brutes des organisateurs ne sont pas jointes. La preparation depuis le classeur brut ne peut pas etre reproduite depuis cette archive seule; les transformations a partir des tables propres livrees sont relancables.

## Installation (Python 3.14)
Depuis la racine de l'archive decompressee :
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Ordre d'execution
```powershell
python 03_transformation/D2_03-transformation_D2_architect_reparer-jointures_v2.py
python 04_analyse/D2_04-analyse_D2_analyst_recalcul-analyses_v2.py
python 04_analyse/D2_04-analyse_D2_scientist_tests-formules_v2.py
python scripts/D2_scripts_D2_scientist_tests-pipeline_v2.py
python -m streamlit run 04_analyse/dashboard_app/D2_04-analyse_D2_analyst_tableau-de-bord_v2.py
```
L'echantillon de 30 cellules a graine 42 est documente a part; son script exige le classeur brut absent du ZIP. Les tables de reference sont fournies dans 02_nettoyage, 03_transformation et 04_analyse. Dependances epinglees. Tests avec unittest; pytest non requis.
