# 상위 3000 낱말 목록 생성기. 아래 소스를 tools/ 에 두고 실행한다.
#   ru_50k.txt : https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/ru/ru_50k.txt
#   nouns.csv, verbs.csv, adjectives.csv, others.csv :
#     https://raw.githubusercontent.com/Badestrand/russian-dictionary/master/<이름>
#   (OpenRussian 파생, CC BY-SA 4.0)
import csv, json
from collections import Counter, defaultdict

def deacc(s): return s.replace("'","").replace("\u0301","").strip().lower()
def stress(s): return s.replace("'","\u0301").strip()
def norm(s):  return deacc(s).replace("ё","е")

# ── 빈도 자료 (자막 말뭉치) ──
freq = Counter()
for line in open("ru_50k.txt", encoding="utf-8"):
    p = line.split()
    if len(p)==2: freq[p[0].lower().replace("ё","е")] += int(p[1])

FORM_COLS = {
 "nouns":["sg_nom","sg_gen","sg_dat","sg_acc","sg_inst","sg_prep",
          "pl_nom","pl_gen","pl_dat","pl_acc","pl_inst","pl_prep"],
 "verbs":["imperative_sg","imperative_pl","past_m","past_f","past_n","past_pl",
          "presfut_sg1","presfut_sg2","presfut_sg3","presfut_pl1","presfut_pl2","presfut_pl3"],
 "adjectives":["comparative","short_m","short_f","short_n","short_pl",
               "decl_m_nom","decl_m_gen","decl_m_dat","decl_m_acc","decl_m_inst","decl_m_prep",
               "decl_f_nom","decl_f_gen","decl_f_dat","decl_f_acc","decl_f_inst","decl_f_prep",
               "decl_n_nom","decl_n_gen","decl_n_dat","decl_n_acc","decl_n_inst","decl_n_prep",
               "decl_pl_nom","decl_pl_gen","decl_pl_dat","decl_pl_acc","decl_pl_inst","decl_pl_prep"],
 "others":[],
}
FORM_KO = {
 "sg_nom":"주격","sg_gen":"생격","sg_dat":"여격","sg_acc":"대격","sg_inst":"조격","sg_prep":"전치격",
 "pl_nom":"복수 주격","pl_gen":"복수 생격","pl_dat":"복수 여격","pl_acc":"복수 대격",
 "pl_inst":"복수 조격","pl_prep":"복수 전치격",
 "imperative_sg":"명령형","imperative_pl":"명령형(복수)",
 "past_m":"과거 남성","past_f":"과거 여성","past_n":"과거 중성","past_pl":"과거 복수",
 "presfut_sg1":"я","presfut_sg2":"ты","presfut_sg3":"он/она",
 "presfut_pl1":"мы","presfut_pl2":"вы","presfut_pl3":"они",
 "comparative":"비교급","short_m":"단어미 남성","short_f":"단어미 여성",
 "short_n":"단어미 중성","short_pl":"단어미 복수",
 "decl_m_nom":"남성 주격","decl_m_gen":"남성 생격","decl_m_dat":"남성 여격",
 "decl_m_acc":"남성 대격","decl_m_inst":"남성 조격","decl_m_prep":"남성 전치격",
 "decl_f_nom":"여성 주격","decl_f_gen":"여성 생격","decl_f_dat":"여성 여격",
 "decl_f_acc":"여성 대격","decl_f_inst":"여성 조격","decl_f_prep":"여성 전치격",
 "decl_n_nom":"중성 주격","decl_n_gen":"중성 생격","decl_n_dat":"중성 여격",
 "decl_n_acc":"중성 대격","decl_n_inst":"중성 조격","decl_n_prep":"중성 전치격",
 "decl_pl_nom":"복수 주격","decl_pl_gen":"복수 생격","decl_pl_dat":"복수 여격",
 "decl_pl_acc":"복수 대격","decl_pl_inst":"복수 조격","decl_pl_prep":"복수 전치격",
}
POS_KO={"nouns":"명사","verbs":"동사","adjectives":"형용사","others":"기타"}
POS_RU={"nouns":"сущ.","verbs":"гл.","adjectives":"прил.","others":""}

entries={}; order=0
for src in ["others","nouns","verbs","adjectives"]:
    with open(src+".csv",encoding="utf-8",newline="") as fh:
        for i,row in enumerate(csv.DictReader(fh,delimiter="\t")):
            bare=(row.get("bare") or "").strip()
            if not bare or " " in bare: continue
            k=deacc(bare)
            if k in entries:
                entries[k].setdefault("alt",[]).append({"pos":POS_RU[src],"pos_ko":POS_KO[src],"rank_in_pos":i,
                    "s":stress(row.get("accented") or bare),"src":src,
                    "gender":(row.get("gender") or "").strip(),
                    "aspect":(row.get("aspect") or "").strip(),
                    "forms":[[FORM_KO[c],stress((row.get(c) or "").strip())]
                             for c in FORM_COLS[src] if (row.get(c) or "").strip()]})
                continue
            e={"w":k,"s":stress(row.get("accented") or bare),
               "pos":POS_RU[src],"pos_ko":POS_KO[src],
               "en":(row.get("translations_en") or "").strip(),
               "src":src,"rank_in_pos":i,"order":order,
               "own":freq[norm(bare)]}
            order+=1
            fl=[]
            for c in FORM_COLS[src]:
                v=(row.get(c) or "").strip()
                if v: fl.append([FORM_KO[c], stress(v), norm(v)])
            e["forms"]=fl
            if src=="nouns":  e["gender"]=(row.get("gender") or "").strip()
            if src=="verbs":  e["aspect"]=(row.get("aspect") or "").strip()
            e["partner"]=(row.get("partner") or "").strip()
            entries[k]=e

# ── 같은 철자에 품사가 여럿이면, 더 흔히 쓰이는 쪽을 대표로 올린다 ──
for k,e in list(entries.items()):
    if not e.get("alt"): continue
    best=min(e["alt"], key=lambda a:a["rank_in_pos"])
    if best["rank_in_pos"] < e["rank_in_pos"]:
        demoted={kk:e[kk] for kk in ("pos","pos_ko","s","src","rank_in_pos","gender","aspect","forms") if kk in e}
        demoted["forms"]=[[a,b] for a,b,_ in e["forms"]]
        e.update({"pos":best["pos"],"pos_ko":best["pos_ko"],"s":best["s"],"src":best["src"],
                  "rank_in_pos":best["rank_in_pos"],
                  "gender":best.get("gender",""),"aspect":best.get("aspect",""),
                  "forms":[[l,v,norm(v)] for l,v in best.get("forms",[])]})
        e["alt"]=[a for a in e["alt"] if a is not best]+[demoted]

# ── 굴절형 빈도는 '가장 흔한 표제어 하나'에만 준다 (동형 충돌 방지) ──
claim=defaultdict(list)
for e in entries.values():
    allf = list(e["forms"])
    for a in e.get("alt",[]):                    # 같은 철자의 다른 품사 변화형도 함께 센다
        allf += [[l,v,norm(v)] for l,v in a.get("forms",[])]
    e["forms_all"] = allf
    for _,_,nf in allf:
        if nf!=norm(e["w"]): claim[nf].append(e)
for nf,cands in claim.items():
    cands.sort(key=lambda e:(e["w"].endswith(("ся","сь")), e["rank_in_pos"], e["order"]))
    winner=cands[0]
    winner.setdefault("extra",0)
    winner["extra"]+=freq[nf]

for e in entries.values():
    e["freq"]=e["own"]+e.get("extra",0)

for e in entries.values():
    # 자기 형태는 안 쓰이면서 굴절형 빈도만 잔뜩 물려받은 표제어는 뺀다.
    # 다만 원형이 드물게 쓰이는 동사(мочь, хоте́ть)는 남긴다.
    ghost = e["own"] < e["freq"]*0.02 and e["rank_in_pos"] > 700
    if ghost: e["freq"]=0
ranked=sorted(entries.values(), key=lambda e:(-e["freq"], e["order"]))
top=[e for e in ranked if e["freq"]>0][:3000]
print("상위 40:", " ".join(e["w"] for e in top[:40]))
print("품사:", Counter(e["pos_ko"] for e in top))
print("900~920:", " ".join(e["w"] for e in top[900:920]))
for e in top:
    e["forms"]=[[a,b] for a,b,_ in e["forms"]]
    for k in ("rank_in_pos","order","own","extra"): e.pop(k,None)
json.dump(top, open("top3000.json","w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("저장(3000):", len(top))
