import csv, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TRANS=ROOT/"03_transformation"; CLEAN=ROOT/"02_nettoyage"
SCRIPT=TRANS/"D2_03-transformation_D2_architect_reparer-jointures_v2.py"
TEAM="D2"
class PipelineV2Tests(unittest.TestCase):
 def test_panel_integrity_and_totals(self):
  p=TRANS/f"{TEAM}_03-transformation_D2_architect_panel-regional-education-10ans_v2.csv"
  with p.open(encoding="utf-8-sig",newline="") as f: rows=list(csv.DictReader(f,delimiter=";"))
  keys={(r["region"],r["annee_scolaire"]) for r in rows}
  self.assertEqual(len(rows),130); self.assertEqual(len(keys),130)
  self.assertTrue(all(int(r["ecoles_total"])>0 for r in rows))
  self.assertTrue(all(int(r["primaire_total"])==int(r["primaire_filles"])+int(r["primaire_garcons"]) for r in rows))
  hb=[r for r in rows if r["region"]=="HAUTS-BASSINS"]
  self.assertEqual(len(hb),10); self.assertTrue(all(r["cep_reussite_filles"] and r["cep_reussite_garcons"] for r in hb))
  milieu=TRANS/f"{TEAM}_03-transformation_D2_engineer_panel-national-milieu-10ans_v2.csv"
  with milieu.open(encoding="utf-8-sig",newline="") as f: mrows=list(csv.DictReader(f,delimiter=";"))
  self.assertEqual(len(mrows),10)
  for r in mrows:
   self.assertEqual(int(r["urbain_total"]),int(r["urbain_garcons"])+int(r["urbain_filles"]))
   self.assertEqual(int(r["rural_total"]),int(r["rural_garcons"])+int(r["rural_filles"]))
   self.assertEqual(int(r["urbain_total"])+int(r["rural_total"]),int(r["national_total"]))
 def run_isolated(self, mutate):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp); (root/"02_nettoyage").mkdir(); (root/"03_transformation").mkdir()
   for name in [f"{TEAM}_02-nettoyage_D2_engineer_ecoles-primaire-region-propre_v2.csv",f"{TEAM}_02-nettoyage_D2_engineer_indicateurs-dgess-region-propre_v3.csv"]: shutil.copy2(CLEAN/name,root/"02_nettoyage"/name)
   for name in [f"{TEAM}_03-transformation_D2_architect_panel-regional-education-10ans_v2.csv",f"{TEAM}_03-transformation_D2_engineer_panel-national-milieu-10ans_v2.csv"]: shutil.copy2(TRANS/name,root/"03_transformation"/name)
   dest=root/"03_transformation"/SCRIPT.name; shutil.copy2(SCRIPT,dest)
   csvp=root/"02_nettoyage"/f"{TEAM}_02-nettoyage_D2_engineer_ecoles-primaire-region-propre_v2.csv"
   with csvp.open(encoding="utf-8-sig",newline="") as f: rows=list(csv.DictReader(f,delimiter=";")); fields=rows[0].keys()
   mutate(rows)
   with csvp.open("w",encoding="utf-8-sig",newline="") as f: w=csv.DictWriter(f,fieldnames=fields,delimiter=";");w.writeheader();w.writerows(rows)
   return subprocess.run([sys.executable,str(dest)],capture_output=True,text=True)
 def test_missing_school_join_fails_explicitly(self):
  result=self.run_isolated(lambda rows: rows.pop())
  self.assertNotEqual(result.returncode,0); self.assertIn("Jointure",result.stderr)
 def test_nan_school_total_fails(self):
  result=self.run_isolated(lambda rows: rows[0].__setitem__("ecoles_total","NaN"))
  self.assertNotEqual(result.returncode,0); self.assertIn("invalide",result.stderr)
if __name__=="__main__": unittest.main(verbosity=2)
