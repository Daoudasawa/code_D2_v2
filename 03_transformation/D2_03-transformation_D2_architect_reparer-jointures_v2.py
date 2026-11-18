"""Reconstruit le panel regional v2 en imposant l'integrite des jointures."""
import csv
import math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TEAM="D2"; N=ROOT/"02_nettoyage"; T=ROOT/"03_transformation"
def read(path):
    with path.open(encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f,delimiter=";"))
def write(path,rows):
    with path.open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter=";",extrasaction="raise");w.writeheader();w.writerows(rows)
base=read(T/f"{TEAM}_03-transformation_D2_architect_panel-regional-education-10ans_v2.csv")
schools=read(N/f"{TEAM}_02-nettoyage_D2_engineer_ecoles-primaire-region-propre_v2.csv")
indicators=read(N/f"{TEAM}_02-nettoyage_D2_engineer_indicateurs-dgess-region-propre_v3.csv")
def index(rows,label):
    out={}
    for row in rows:
        key=(row["region"],row["annee_scolaire"])
        if key in out: raise ValueError(f"Cle dupliquee dans {label}: {key}")
        out[key]=row
    return out
school_idx=index(schools,"ecoles"); ind_idx=index(indicators,"indicateurs")
keys=[(r["region"],r["annee_scolaire"]) for r in base]
missing_s=[k for k in keys if k not in school_idx]
missing_i=[k for k in keys if k not in ind_idx]
if missing_s or missing_i: raise ValueError(f"Jointure incomplete: ecoles absentes={missing_s}; indicateurs absents={missing_i}")
if len(keys)!=130 or len(set(keys))!=130: raise ValueError(f"Panel attendu 130 cles uniques, observe {len(keys)} lignes/{len(set(keys))} cles")
for row,key in zip(base,keys):
    eco=school_idx[key]; ind=ind_idx[key]
    raw_count=eco.get("ecoles_total", "")
    try:
        parsed=float(raw_count)
        if not math.isfinite(parsed) or not parsed.is_integer(): raise ValueError
        total=int(parsed)
    except (TypeError, ValueError):
        raise ValueError(f"Nombre d'ecoles invalide pour {key}: {raw_count!r}")
    if total<=0: raise ValueError(f"Nombre d'ecoles nul ou negatif pour {key}: {total}")
    row.update({"ecoles_public":eco["ecoles_public"],"ecoles_prive":eco["ecoles_prive"],"ecoles_total":str(total),"eleves_par_ecole":str(round(int(row["primaire_total"])/total,1))})
    for col in ("cep_reussite_garcons","cep_reussite_filles","cep_reussite_total"):
        row[col]=ind[col]
out=T/f"{TEAM}_03-transformation_D2_architect_panel-regional-education-10ans_v2.csv"
write(out,base)
# Le panel national urbain-rural ne depend pas des jointures regionales reparees;
# il est neanmoins versionne pour que les analyses v2 consomment des entr?es v2.
mil=read(T/f"{TEAM}_03-transformation_D2_engineer_panel-national-milieu-10ans_v2.csv")
write(T/f"{TEAM}_03-transformation_D2_engineer_panel-national-milieu-10ans_v2.csv",mil)
hb=[r for r in base if r["region"]=="HAUTS-BASSINS"]
assert len(hb)==10 and all(int(r["ecoles_total"])>0 for r in hb)
assert all(r["cep_reussite_filles"] and r["cep_reussite_garcons"] for r in hb)
assert all(int(r["ecoles_total"])>0 for r in base)
print(f"OK: {len(base)} cles uniques jointes; aucune valeur ?cole nulle; Hauts-Bassins ecoles et CEP presents.")
