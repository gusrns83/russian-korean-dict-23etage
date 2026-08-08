# OpenRussian 자료(강세·변화형) + 손으로 쓴 한국어 뜻풀이 → words.json
import json, glob, os

top = {e["w"]: e for e in json.load(open("top5000.json", encoding="utf-8"))}
GENDER = {"m":"남성","f":"여성","n":"중성"}

ko = {}
for p in sorted(glob.glob("ko/ko*.json")):
    ko.update(json.load(open(p, encoding="utf-8")))

def pick(w, gram):
    """같은 철자에 품사가 여럿이면, 한국어 문법 설명과 맞는 쪽을 고른다."""
    o = top.get(w)
    if not o: return {}
    cands = [o] + o.get("alt", [])
    if len(cands) > 1:
        want = next((p for p in ("동사","형용사","명사") if p in gram), None)
        if want:
            for c in cands:
                if c.get("pos_ko") == want: return c
    return o

out = {}
for w, k in ko.items():
    o = pick(w, k.get("gram",""))
    gram = k.get("gram","")
    if not gram and o.get("gender"): gram = f'명사 {GENDER.get(o["gender"],"")}'
    forms = [[a,b] for a,b in o.get("forms",[])][:12] + k.get("forms_extra",[])
    out[w] = {
        "found": True,
        "headword": w,
        "stressed": o.get("s", w),
        "pron": k.get("pron",""),
        "pos": o.get("pos",""),
        "pos_ko": o.get("pos_ko",""),
        "gram": gram,
        "senses": [{"gloss":s["gloss"], "note":s.get("note",""),
                    "examples":[{"ru":a,"ko":b} for a,b in s.get("ex",[])]}
                   for s in k["senses"]],
        "idioms": [{"ru":a,"ko":b} for a,b in k.get("idioms",[])],
        "forms":  [{"label":a,"value":b} for a,b in forms],
        "etym":   k.get("etym",""),
    }

# 굴절형에서도 찾아지도록 이어 놓는다 (예: "кни́ги" -> "книга")
alias = {}
for w, o in top.items():
    if w not in out: continue
    allforms = list(o.get("forms", []))
    for a in o.get("alt", []): allforms += a.get("forms", [])
    for _, form in allforms:
        f = form.replace("\u0301","").lower()
        if f and f != w and f not in out and f not in alias:
            alias[f] = w

json.dump({"entries":out, "alias":alias,
           "credit":"변화형·강세 자료: OpenRussian.org (CC BY-SA 4.0)"},
          open("../words.json","w",encoding="utf-8"), ensure_ascii=False, separators=(",",":"))
print("표제어:", len(out), " 굴절형 연결:", len(alias))
print("파일 크기:", os.path.getsize("../words.json"), "바이트")
