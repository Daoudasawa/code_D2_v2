"""Corrige dans de nouvelles sorties v2 l'alias DGESS HAUT-BASSINS.
Entrees en lecture seule : classeur brut et tables propres v1.
"""
import csv
from pathlib import Path
import openpyxl

ROOT = Path(__file__).resolve().parents[1]
TEAM = "D2"
D = ROOT / "02_nettoyage"
RAW = ROOT / "01_collecte" / f"{TEAM}_01-collecte_D2_engineer_dgess-prescolaire-primaire-brut_v1.xlsx"

def read_csv(name):
    with (D / name).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))

def write_csv(name, rows):
    with (D / name).open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter=";", extrasaction="raise")
        w.writeheader(); w.writerows(rows)

schools = read_csv(f"{TEAM}_02-nettoyage_D2_engineer_ecoles-primaire-region-propre_v1.csv")
for r in schools:
    if r["region"] == "HAUT-BASSINS": r["region"] = "HAUTS-BASSINS"
assert len(schools) == 130 and sum(r["region"] == "HAUTS-BASSINS" for r in schools) == 10
write_csv(f"{TEAM}_02-nettoyage_D2_engineer_ecoles-primaire-region-propre_v2.csv", schools)

indicators = read_csv(f"{TEAM}_02-nettoyage_D2_architect_indicateurs-dgess-region-propre_v1.csv")
wb = openpyxl.load_workbook(RAW, data_only=True, read_only=True)
ws = wb["Feuil9"]
source = {}
current_region = ""
for r in range(1, ws.max_row + 1):
    raw_region = str(ws.cell(r, 1).value or "").strip().upper()
    if raw_region:
        current_region = raw_region
    if current_region in {"HAUT-BASSINS", "HAUTS-BASSINS"}:
        sex = str(ws.cell(r, 2).value or "").strip().upper()
        if sex.startswith("GAR") or sex in {"FILLES", "TOTAL"}:
            normalized_sex = "GARCONS" if sex.startswith("GAR") else sex
            source[normalized_sex] = {int(ws.cell(2, c).value): ws.cell(r, c).value for c in range(3, 13)}
assert set(source) >= {"GARCONS", "FILLES", "TOTAL"}, f"Lignes CEP sources manquantes: {source.keys()}"
for r in indicators:
    if r["region"] == "HAUT-BASSINS": r["region"] = "HAUTS-BASSINS"
    if r["region"] == "HAUTS-BASSINS":
        year = int(r["annee_fin"])
        for col, sex in (("cep_reussite_garcons", "GARCONS"), ("cep_reussite_filles", "FILLES"), ("cep_reussite_total", "TOTAL")):
            val = source[sex][year]
            r[col] = "" if val is None else str(val)
assert len(indicators) == 130
hb = [r for r in indicators if r["region"] == "HAUTS-BASSINS"]
assert len(hb) == 10 and all(r["cep_reussite_filles"] and r["cep_reussite_garcons"] for r in hb)
write_csv(f"{TEAM}_02-nettoyage_D2_architect_indicateurs-dgess-region-propre_v2.csv", indicators)
print("OK: 130 lignes ecoles et indicateurs; alias canonise; CEP Hauts-Bassins restaure depuis Feuil9.")
