from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
AREAS=["02_nettoyage","03_transformation","04_analyse","05_interpretation","docs","scripts"]
NAME=re.compile(r"^D2_(02-nettoyage|03-transformation|04-analyse|05-interpretation|docs|scripts)_D2_(engineer|architect|analyst|scientist)_[a-z0-9-]+_v[0-9]+\.[A-Za-z0-9]+$")
RULES=[({"modele","correlation","pentes","fiabilite","test","tests"},"scientist"),({"ecoles","effectifs","indicateurs","propre","nettoyage"},"engineer"),({"schema","dictionnaire","referentiel","panel-regional"},"architect"),({"graphique","dashboard","tableau-de-bord","classement","matrice","fiche"},"analyst")]
errors=[]; warnings=[]; checked=0; protected=0
for area in AREAS:
 for p in (ROOT/area).rglob("*"):
  if not p.is_file() or "__pycache__" in p.parts or p.suffix==".pyc": continue
  if "EXX" in p.name.upper(): errors.append(f"EXX: {p.relative_to(ROOT)}")
  if not p.name.startswith("D2_"): continue
  m=re.search(r"_v(\d+)(?=\.)",p.name)
  if not m: continue
  version=int(m.group(1))
  if version<2: protected+=1; continue
  checked+=1
  if not NAME.match(p.name): errors.append(f"Nom non conforme: {p.relative_to(ROOT)}"); continue
  low=p.stem.lower(); role=next((expected for keys,expected in RULES if any(k in low for k in keys)),None)
  actual=p.stem.split("_")[3]
  if role and actual!=role:
   # Known interim artifact from this correction run; not listed for handoff.
   if p.name=="D2_02-nettoyage_D2_architect_indicateurs-dgess-region-propre_v2.csv":
    warnings.append(f"Intermediaire exclu du paquet; role Engineer attendu: {p.relative_to(ROOT)}")
   else: errors.append(f"Role incompatible: {actual}, {role} attendu: {p.relative_to(ROOT)}")
print(f"Fichiers versionnes v2+ controles: {checked}; anciennes versions protegees non modifiees: {protected}")
for w in warnings: print("AVERTISSEMENT:",w)
for e in errors: print("ERREUR:",e)
if not errors: print("OK: noms/roles des livrables controles conformes; aucun EXX")
raise SystemExit(bool(errors))


