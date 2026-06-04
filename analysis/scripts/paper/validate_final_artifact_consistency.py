#!/usr/bin/env python3
from __future__ import annotations
import csv,re
from pathlib import Path

SCEN=Path(__file__).resolve().parents[3]
AN=SCEN/'analysis'
DATA=AN/'data'
REPORTS=AN/'reports'
FIG=AN/'figures'
WIKI=SCEN/'.wiki-clone'

def count_settings(d:Path)->int:
    return sum(1 for _ in d.rglob('*.settings')) if d.exists() else 0

def csv_rows(p:Path)->int:
    if not p.exists(): return -1
    with p.open(newline='',encoding='utf-8',errors='replace') as f:
        return sum(1 for _ in csv.DictReader(f))

def search_active_refs(pattern:str)->int:
    n=0
    for p in SCEN.rglob('*'):
        if not p.is_file() or p.suffix.lower() not in {'.py','.md','.txt','.csv'}: continue
        rel=str(p.relative_to(SCEN))
        if rel.startswith('_archive/'): continue
        txt=p.read_text(encoding='utf-8',errors='replace')
        if re.search(pattern,txt): n+=1
    return n

checks=[]
def add(cid,name,expected,observed,status,severity,fix):
    checks.append({'check_id':cid,'check_name':name,'expected':expected,'observed':str(observed),'status':status,'severity':severity,'recommended_fix':fix})

# counts
base=count_settings(SCEN/'base_scenarios')
corp=count_settings(SCEN/'corpus_v1')
comb=csv_rows(DATA/'corpus_v1_combined_manifest.csv')
outm=csv_rows(DATA/'output_metrics.csv')
feat=csv_rows(DATA/'features.csv')
spat=csv_rows(DATA/'spatial_occupancy_metrics.csv')
stress_refs=search_active_refs(r'|07_|')

add('C001','base_scenarios_count','45',base,'PASS' if base==45 else 'FAIL','BLOCKER','regenerate base_scenarios')
add('C002','corpus_v1_count','540',corp,'PASS' if corp==540 else 'FAIL','BLOCKER','verify corpus_v1 split')
add('C003','combined_manifest_rows','540',comb,'PASS' if comb==540 else 'FAIL','BLOCKER','rebuild combined manifest from corpus_v1')
add('C004','output_metrics_rows','540',outm,'PASS' if outm==540 else 'WARN','MAJOR','rerun output_metrics for missing reports')
add('C005','features_rows','540',feat,'PASS' if feat==540 else 'WARN','MAJOR','rerun features phase')
if spat in (540, -1):
    st='PASS'; sev='INFO'; fix='none'
elif spat==720:
    st='WARN'; sev='MAJOR'; fix='legacy 720 spatial metrics; regenerate or archive as legacy'
else:
    st='WARN'; sev='MAJOR'; fix='verify spatial occupancy scope'
add('C006','spatial_metrics_scope','540 or missing',spat,st,sev,fix)
add('C007','no__refs','0',stress_refs,'PASS' if stress_refs==0 else 'FAIL','BLOCKER','remove  references from active tree')

# references
c2=search_active_refs(r'\bcorpus_v2\b')
c3=search_active_refs(r'\bcorpus_v3\b')
refs720=search_active_refs(r'\b720\b')
add('C008','active corpus_v2 refs outside archive','0 (except legacy context)',c2,'PASS' if c2==0 else 'WARN','MAJOR','review docs/scripts and keep only legacy context')
add('C009','active corpus_v3 refs outside archive','0 (except legacy context)',c3,'PASS' if c3==0 else 'WARN','MINOR','review historical mentions')
add('C010','active 720 refs outside archive','historical context only',refs720,'WARN' if refs720>0 else 'PASS','MINOR','mark as historical or update to 540')

# paper-ready artifacts
required=[
 ('C011','resultados_actuales',REPORTS/'RESULTADOS_ACTUALES.md'),
 ('C012','paper_freeze_checklist',REPORTS/'paper_freeze_checklist.md'),
 ('C013','message_analysis_window_policy',REPORTS/'canonical'/'message_analysis_window_policy.md'),
 ('C014','protocol_benchmark_kpi_policy',REPORTS/'canonical'/'protocol_benchmark_kpi_policy.md'),
 ('C015','traffic_profile_kpi_analysis',REPORTS/'canonical'/'traffic_profile_kpi_analysis.md'),
 ('C016','corpus_benchmark_validation',REPORTS/'canonical'/'corpus_benchmark_validation.md'),
 ('C017','paper_figures_main_dir',FIG/'paper'/'main'),
 ('C018','paper_tables_dir',FIG/'paper'/'tables'),
]
for cid,name,path in required:
    ok=path.exists()
    add(cid,name,str(path.relative_to(SCEN)),path.exists(),'PASS' if ok else 'FAIL','BLOCKER' if not ok else 'INFO','generate missing artifact')

out_csv=DATA/'final_artifact_consistency.csv'
with out_csv.open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['check_id','check_name','expected','observed','status','severity','recommended_fix'])
    w.writeheader(); w.writerows(checks)

out_md=REPORTS/'project'/'final_artifact_consistency_report.md'
out_md.parent.mkdir(parents=True,exist_ok=True)
with out_md.open('w',encoding='utf-8') as f:
    f.write('# Final artifact consistency report\n\n')
    f.write('| check_id | check_name | expected | observed | status | severity | recommended_fix |\n')
    f.write('|---|---|---|---|---|---|---|\n')
    for r in checks:
        f.write(f"| {r['check_id']} | {r['check_name']} | {r['expected']} | {r['observed']} | {r['status']} | {r['severity']} | {r['recommended_fix']} |\n")
print('wrote',out_csv)
print('wrote',out_md)