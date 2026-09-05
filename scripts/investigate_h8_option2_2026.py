"""Investiga trajetorias temporais com vagas por curso; nao altera H8.

Vagas ofertadas positivas sao um filtro observacional, nao prova de
elegibilidade individual nem disponibilidade atual de matricula.
"""
import sys,json,csv,time,hashlib
from pathlib import Path
from collections import defaultdict
from itertools import product
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.diagnose_curriculum_conflicts_2026 import collide
from src.solve.direct_objective import groups_for_item
root=Path(__file__).resolve().parents[1]
import os
os.chdir(root)
output=root/'dados/processados/investigacao_h8_opcao2_2026'
output.mkdir(parents=True,exist_ok=True)
p=json.load(open('dados/processados/instancia_sintetica_2026_v1.json'))
cur=list(csv.DictReader(open('dados/processados/curriculos_cc_si.csv')))
web=list(csv.DictReader(open('webscrap/turmas_2026_raw.csv',encoding='utf-8-sig')))
courseid={'CC':'31','SI':'83'}
def seats(c,course):
 return sum(int(v.get('vagas') or 0) for v in c.get('vagas_por_curso',[]) if v['codigo_curso']==courseid[course])
groups=defaultdict(list)
for c in p['classes']:
 for g in groups_for_item(c):groups[c['semestre'],g].append(c)
results=[]
t0=time.perf_counter()
for (sem,g),items in sorted(groups.items()):
 course=g[:2]
 codes=sorted(set(c['codigo'] for c in items))
 expected={r['codigo'] for r in cur if r['tipo']=='obrigatoria' and r['grupo']==g}
 choices=[[c for c in items if c['codigo']==code and seats(c,course)>0] for code in codes]
 n=0; witness=None;best=-1;cartesian=1
 for ch in choices:cartesian*=len(ch)
 for combo in product(*choices):
  if all(not collide(a,b) for i,a in enumerate(combo) for b in combo[i+1:]):
   n+=1
   bottleneck=min(seats(c,course) for c in combo)
   if bottleneck>best:best=bottleneck;witness=[c['id'] for c in combo]
 missing=sorted(expected-set(codes)); extra=sorted(set(codes)-expected)
 web_available={code:sum(1 for r in web if r['semestre']==sem and r['codigo']==code and int(r['vagas_'+course.lower()] or 0)>0) for code in missing}
 results.append(dict(semestre=sem,grupo=g,codigos_recorte=len(codes),codigos_grade=len(expected),sem_vaga_curso=[code for code,ch in zip(codes,choices) if not ch],combinacoes=cartesian,viaveis=n,gargalo_melhor_trajetoria=best,testemunha=witness,ausentes=missing,extras=extra,ausentes_com_oferta_web=web_available))
(output/'recorte.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
print('duracao_s',time.perf_counter()-t0)
print('grupos',len(results),'viaveis',sum(r['viaveis']>0 for r in results),'com_grade_coberta',sum(not r['ausentes'] for r in results))
for r in results:
 print(r)
from scripts.match_qh_web_2026 import web_meetings
extended=[]
for row in results:
 sem,g=row['semestre'],row['grupo'];course=g[:2]
 expected={r['codigo'] for r in cur if r['tipo']=='obrigatoria' and r['grupo']==g}
 choices={code:[c for c in groups[sem,g] if c['codigo']==code and seats(c,course)>0] for code in sorted(expected)}
 unknown=[]
 for code,ch in choices.items():
  if ch:continue
  for r in web:
   if r['semestre']==sem and r['codigo']==code and int(r['vagas_'+course.lower()] or 0)>0:
    sl=web_meetings(r['horario'])
    if not sl:unknown.append(code);continue
    ch.append(dict(id=f"web:{sem}:{code}:{r['turma']}",encontros=[dict(dia=d,inicio=s,fim=e) for d,s,e in sorted(sl)]))
 missing=[code for code,ch in choices.items() if not ch]
 from scripts.diagnose_curriculum_conflicts_2026 import choose_sections
 witness=choose_sections(choices) if not missing else None
 extended.append(dict(semestre=sem,grupo=g,ausentes=sorted(missing),horario_desconhecido=sorted(set(unknown)),status='incompleto' if missing or unknown else ('viavel' if witness else 'sem_trajetoria'),testemunha=[c['id'] for c in witness] if witness else []))
print('AMPLIADO')
for r in extended:print(r)
(output/'ampliado.json').write_text(json.dumps(extended,ensure_ascii=False,indent=2))

manifest={str(path.relative_to(root)):hashlib.sha256(path.read_bytes()).hexdigest() for path in [root/'dados/processados/instancia_sintetica_2026_v1.json',root/'dados/processados/curriculos_cc_si.csv',root/'webscrap/turmas_2026_raw.csv',Path(__file__),root/'scripts/diagnose_curriculum_conflicts_2026.py',root/'scripts/match_qh_web_2026.py',root/'src/solve/direct_objective.py']}
(output/'manifesto.json').write_text(json.dumps(manifest,indent=2)+'\n')
