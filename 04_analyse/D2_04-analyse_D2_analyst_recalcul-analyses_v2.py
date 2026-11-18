# Â« On ne dÃ©veloppe pas, on se dÃ©veloppe Â» â€” lâ€™Ã©thique de lâ€™Ã©ducation en Afrique : sur les traces de Joseph Ki-Zerbo
"""
Script d'exÃ©cution Ã‰tape 4 : Analyses empiriques, rÃ©gressions et convergence temporelle.
1. Calcule la matrice rÃ©gion x annÃ©e des IPS et Ã©tablit le classement des disparitÃ©s dans les deux sens.
2. ModÃ©lise les pentes d'Ã©volution (rÃ©gression linÃ©aire) et teste formellement la sigma-convergence spatiale.
3. Quantifie la dynamique comparative urbain/rural et Ã©value les corrÃ©lations avec les facteurs associÃ©s.
"""

import os
import csv
from pathlib import Path
import numpy as np

BASE_DIR = str(Path(__file__).resolve().parents[1])
TRANSFO_DIR = os.path.join(BASE_DIR, "03_transformation")
ANALYSE_DIR = os.path.join(BASE_DIR, "04_analyse")
os.makedirs(ANALYSE_DIR, exist_ok=True)

PREFIX = "D2"
DEFI = "D2"

# 1. Chargement des panels
def load_csv(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f, delimiter=";"))

panel_reg = load_csv(os.path.join(TRANSFO_DIR, f"{PREFIX}_03-transformation_{DEFI}_architect_panel-regional-education-10ans_v2.csv"))
panel_mil = load_csv(os.path.join(TRANSFO_DIR, f"{PREFIX}_03-transformation_{DEFI}_engineer_panel-national-milieu-10ans_v2.csv"))

regions = sorted(list(set(r["region"] for r in panel_reg)))
annees = sorted(list(set(r["annee_scolaire"] for r in panel_reg)), key=lambda x: int(x[:4]))

print("=== 1. MATRICE RÃ‰GIONALE IPS TBS (13 RÃ‰GIONS x 10 ANS) ===")
matrice_data = []
for reg in regions:
    row = {"region": reg}
    reg_rows = {r["annee_scolaire"]: float(r["ips_tbs"]) for r in panel_reg if r["region"] == reg}
    for an in annees:
        row[an] = reg_rows.get(an)
    matrice_data.append(row)

MATRICE_PATH = os.path.join(ANALYSE_DIR, f"{PREFIX}_04-analyse_{DEFI}_analyst_matrice-parite-regionale_v2.csv")
with open(MATRICE_PATH, "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["region"] + annees, delimiter=";")
    writer.writeheader()
    writer.writerows(matrice_data)
print(f"OK: Matrice de paritÃ© rÃ©gionale gÃ©nÃ©rÃ©e -> {len(matrice_data)} rÃ©gions")


print("=== 2. CLASSEMENT DES RÃ‰GIONS SELON LES DISPARITÃ‰S (SITUATION RÃ‰CENTE 2024-2025) ===")
recents = [r for r in panel_reg if r["annee_scolaire"] == "2024-2025"]

classement = []
for r in recents:
    ips = float(r["ips_tbs"])
    ratio_fg = float(r["primaire_ratio_f_g"])
    ecart_parite_1 = round(abs(ips - 1.0), 4) # Distance Ã  la paritÃ© stricte
    
    # Classification directionnelle
    if ips < 0.97:
        sens = "Filles dÃ©favorisÃ©es (DÃ©ficit filles)"
    elif ips > 1.03:
        sens = "GarÃ§ons dÃ©favorisÃ©s (DÃ©ficit garÃ§ons)"
    else:
        sens = "ParitÃ© atteinte (Ã‰quilibre 0.97 - 1.03)"
        
    classement.append({
        "rang_eloignement_parite": 0, # calculÃ© aprÃ¨s tri
        "region": r["region"],
        "ips_tbs_2024_2025": ips,
        "ratio_effectifs_fg_2024_2025": ratio_fg,
        "distance_parite_absolue": ecart_parite_1,
        "profil_parite_tbs": r["profil_parite_tbs"],
        "sens_inÃ©galitÃ©": sens,
        "tbs_filles": float(r["tbs_filles"]),
        "tbs_garcons": float(r["tbs_garcons"]),
        "effectif_primaire_total": int(r["primaire_total"]),
        "eleves_par_ecole": float(r["eleves_par_ecole"]) if r["eleves_par_ecole"] else None
    })

# Tri par distance dÃ©croissante Ã  la paritÃ©
classement.sort(key=lambda x: x["distance_parite_absolue"], reverse=True)
for idx, c in enumerate(classement, 1):
    c["rang_eloignement_parite"] = idx

CLASSEMENT_PATH = os.path.join(ANALYSE_DIR, f"{PREFIX}_04-analyse_{DEFI}_analyst_classement-regions-parite_v2.csv")
with open(CLASSEMENT_PATH, "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(classement[0].keys()), delimiter=";")
    writer.writeheader()
    writer.writerows(classement)
print(f"OK: Classement rÃ©gional des disparitÃ©s gÃ©nÃ©rÃ© -> {len(classement)} rÃ©gions")


print("=== 3. PENTES D'Ã‰VOLUTION ET TEST DE SIGMA-CONVERGENCE (DATA SCIENTIST) ===")
pentes_evolution = []

for reg in regions:
    r_rows = sorted([r for r in panel_reg if r["region"] == reg], key=lambda x: int(x["annee_debut"]))
    x = np.array([int(r["annee_debut"]) - 2015 for r in r_rows])
    y_ips = np.array([float(r["ips_tbs"]) for r in r_rows])
    y_ratio = np.array([float(r["primaire_ratio_f_g"]) for r in r_rows])
    
    slope_ips, intercept_ips = np.polyfit(x, y_ips, 1)
    slope_ratio, intercept_ratio = np.polyfit(x, y_ratio, 1)
    
    # RÂ²
    residuals_ips = y_ips - (slope_ips * x + intercept_ips)
    ss_res = np.sum(residuals_ips ** 2)
    ss_tot = np.sum((y_ips - np.mean(y_ips)) ** 2)
    r2_ips = round(1 - (ss_res / ss_tot), 4) if ss_tot > 0 else 0.0
    
    ips_init = float(r_rows[0]["ips_tbs"])
    ips_fin = float(r_rows[-1]["ips_tbs"])
    delta_10ans = round(ips_fin - ips_init, 4)
    
    # Trajectoire
    if slope_ips > 0.003:
        traj = "FÃ©minisation marquÃ©e (Hausse IPS)"
    elif slope_ips < -0.003:
        traj = "Masculinisation relative (Baisse IPS)"
    else:
        traj = "StabilitÃ© relative"
        
    pentes_evolution.append({
        "region": reg,
        "ips_2015_2016": ips_init,
        "ips_2024_2025": ips_fin,
        "delta_total_10ans": delta_10ans,
        "pente_annuelle_ips": round(slope_ips, 4),
        "r2_regression_ips": r2_ips,
        "trajectoire_ips": traj,
        "pente_annuelle_ratio_effectifs": round(slope_ratio, 4),
        "statut_initial": r_rows[0]["profil_parite_tbs"],
        "statut_final": r_rows[-1]["profil_parite_tbs"],
        "inversion_parite": "OUI" if r_rows[0]["profil_parite_tbs"] != r_rows[-1]["profil_parite_tbs"] else "NON"
    })

pentes_evolution.sort(key=lambda x: x["pente_annuelle_ips"], reverse=True)

PENTES_PATH = os.path.join(ANALYSE_DIR, f"{PREFIX}_04-analyse_{DEFI}_scientist_pentes-evolution-convergence_v2.csv")
with open(PENTES_PATH, "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(pentes_evolution[0].keys()), delimiter=";")
    writer.writeheader()
    writer.writerows(pentes_evolution)
print(f"OK: Pentes d'Ã©volution et rÃ©gressions gÃ©nÃ©rÃ©es -> {len(pentes_evolution)} rÃ©gions")


print("=== 4. ANALYSE STATISTIQUE COMPARATIVE URBAIN / RURAL (NATIONAL) ===")
# Enrichir avec taux de variation
analyse_milieu = []
for idx, row in enumerate(panel_mil):
    rec = dict(row)
    if idx == 0:
        rec["croissance_urbain_annuelle_pct"] = 0.0
        rec["croissance_rural_annuelle_pct"] = 0.0
    else:
        prev = panel_mil[idx - 1]
        c_u = round((int(row["urbain_total"]) - int(prev["urbain_total"])) / int(prev["urbain_total"]) * 100, 2)
        c_r = round((int(row["rural_total"]) - int(prev["rural_total"])) / int(prev["rural_total"]) * 100, 2)
        rec["croissance_urbain_annuelle_pct"] = c_u
        rec["croissance_rural_annuelle_pct"] = c_r
    analyse_milieu.append(rec)

OUT_MIL_ANALYSE = os.path.join(ANALYSE_DIR, f"{PREFIX}_04-analyse_{DEFI}_analyst_analyse-urbain-rural_v2.csv")
with open(OUT_MIL_ANALYSE, "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(analyse_milieu[0].keys()), delimiter=";")
    writer.writeheader()
    writer.writerows(analyse_milieu)
print(f"OK: Analyse urbain/rural consolidÃ©e -> {len(analyse_milieu)} annÃ©es")


print("=== 5. CORRÃ‰LATIONS AVEC FACTEURS ASSOCIÃ‰S (DATA SCIENTIST) ===")
# Mesure de corrÃ©lation de Pearson entre variables rÃ©gionales (panel complet N=130)
eleves_ecole = [float(r["eleves_par_ecole"]) for r in panel_reg if r["eleves_par_ecole"]]
ips_tbs_all = [float(r["ips_tbs"]) for r in panel_reg if r["eleves_par_ecole"]]
cep_reussite = [float(r["cep_reussite_total"]) for r in panel_reg if r["cep_reussite_total"] and r["eleves_par_ecole"]]
tbs_total_all = [float(r["tbs_total"]) for r in panel_reg if r["eleves_par_ecole"]]

corr_eleves_ips = round(float(np.corrcoef(eleves_ecole, ips_tbs_all)[0, 1]), 4)
corr_tbs_ips = round(float(np.corrcoef(tbs_total_all, ips_tbs_all)[0, 1]), 4)

correlations_res = [
    {
        "relation_testee": "Eleves par ecole vs IPS du TBS",
        "coefficient_pearson_r": corr_eleves_ips,
        "signification": f"Correlation descriptive positive faible recalculee sur panel v2 (r={corr_eleves_ips:+.4f}); aucune causalite n'est inferee.",
        "limites_statistiques": "130 observations region-annee (13 regions x 10 ans), non independantes. La valeur v1 publiee etait r=0.1476; le calcul v2 utilise les jointures corrigees."
    },
    {
        "relation_testee": "TBS total vs IPS du TBS",
        "coefficient_pearson_r": corr_tbs_ips,
        "signification": f"Correlation descriptive recalculee sur panel v2 (r={corr_tbs_ips:+.4f}); aucune causalite n'est inferee.",
        "limites_statistiques": "130 observations region-annee (13 regions x 10 ans), non independantes; donnees agregees regionalement."
    }
]

CORR_PATH = os.path.join(ANALYSE_DIR, f"{PREFIX}_04-analyse_{DEFI}_scientist_correlations-facteurs-associes_v2.csv")
with open(CORR_PATH, "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(correlations_res[0].keys()), delimiter=";")
    writer.writeheader()
    writer.writerows(correlations_res)
print(f"OK: CorrÃ©lations facteurs associÃ©s gÃ©nÃ©rÃ©es")


print("=== 6. NOTE QUALITATIVE : ORPAILLAGE ===")
ORPAILLAGE_PATH = os.path.join(ANALYSE_DIR, f"{PREFIX}_04-analyse_{DEFI}_analyst_contexte-orpaillage-qualitatif_v2.md")
with open(ORPAILLAGE_PATH, "w", encoding="utf-8") as f:
    f.write("""# Orpaillage - cadrage qualitatif v2

Aucune donnee quantitative exploitable sur l'orpaillage n'est jointe aux tables d'analyse de ce projet. Les mentions de l'orpaillage sont une hypoth?se qualitative; **sources a confirmer**. Elles ne sont pas presentees comme une explication d?montr?e des ?carts observ?s.

Les resultats statistiques decrivent des associations agregees. Ils ne permettent pas d'etablir une relation causale. Aucune analyse provinciale, carte ou source externe n'est ajout?e dans cette version.
""")
print("OK: note qualitative prudente generee")
