# OpenRussian 전체(nouns/verbs/adjectives/others)에서 '강세 교정 전용' 대조표를 만든다.
#   출력: ../stress.json  =  { 정규형(강세X, 소문자) : 강세형 }
#   - 강세가 정확히 하나인 순수 키릴 낱말만.
#   - 한 정규형에 강세형이 여러 갈래면(동음이의) 제외 → 오교정 방지.
import csv, json, re, os
CYR = re.compile("^[а-яё́]+$")
def acc(s): return (s or "").replace("'", "́").strip()
def deacc(s): return s.replace("́", "")

FILES = ["nouns.csv","verbs.csv","adjectives.csv","others.csv"]
SKIP = {"bare","accented","translations_en","translations_de","gender","partner",
        "animate","indeclinable","sg_only","pl_only","aspect","superlative"}

# 실제로 쓰이는 어휘만 남기기 위한 빈도 목록(자막 말뭉치, ё→е 정규화)
freq = set()
for line in open("ru_50k.txt", encoding="utf-8"):
    p = line.split()
    if len(p) == 2: freq.add(p[0].lower().replace("ё","е"))
def common(key): return key.replace("ё","е") in freq

m = {}   # key -> set(accented)
def add(tok):
    tok = acc(tok).lower()
    if not tok or tok.count("́") != 1 or not CYR.match(tok):
        return
    key = deacc(tok)
    if not common(key):        # 빈도 목록에 있는 낱말만
        return
    m.setdefault(key, set()).add(tok)

for fn in FILES:
    with open(fn, encoding="utf-8") as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            add(row.get("accented",""))
            for col, val in row.items():
                if col in SKIP or not isinstance(val, str) or not val: continue
                # 한 칸에 대안형이 여럿일 수 있어 키릴 낱말 단위로 쪼갠다
                for piece in re.findall("[а-яёА-ЯЁ'́]+", val):
                    add(piece)

out = {k: next(iter(v)) for k, v in m.items() if len(v) == 1}   # 유일한 것만
json.dump(out, open("../stress.json","w",encoding="utf-8"),
          ensure_ascii=False, separators=(",",":"))
amb = sum(1 for v in m.values() if len(v) > 1)
print("정규형 후보:", len(m), " 유일(수록):", len(out), " 동음이의 제외:", amb)
print("파일 크기:", os.path.getsize("../stress.json"), "바이트")
