// 사진으로 낱말 찾기. 이미지를 Claude 비전에 보내 가장 뚜렷한 러시아어 낱말을
// 골라 사전 표제어로 삼고, 뜻풀이 JSON을 돌려준다.
// 열쇠(API 키)는 서버에만 둔다: 환경 변수 ANTHROPIC_API_KEY.

// ── Redis 공용 캐시 (lookup.js와 동일 방식) — 인식된 표제어로 저장해 재사용 ──
function redisEnv() {
  const url = process.env.KV_REST_API_URL || process.env.UPSTASH_REDIS_REST_URL;
  const token = process.env.KV_REST_API_TOKEN || process.env.UPSTASH_REDIS_REST_TOKEN;
  return url && token ? { url, token } : null;
}
async function redisCmd(cmd) {
  const env = redisEnv();
  if (!env) return null;
  try {
    const r = await fetch(env.url, {
      method: "POST",
      headers: { authorization: "Bearer " + env.token, "content-type": "application/json" },
      body: JSON.stringify(cmd)
    });
    if (!r.ok) return null;
    const j = await r.json();
    return j && "result" in j ? j.result : null;
  } catch (_) { return null; }
}
const norm = (s) => String(s || "").replace(/́/g, "").trim().toLowerCase();
const cacheSet = (term, value) =>
  redisCmd(["SET", "dict:" + norm(term), value, "EX", 31536000]);

function extractJson(text) {
  const raw = String(text || "").replace(/```json|```/g, "").trim();
  const s = raw.indexOf("{"), e = raw.lastIndexOf("}");
  if (s < 0 || e < 0) return null;
  try { return JSON.parse(raw.slice(s, e + 1)); } catch (_) { return null; }
}
function worthCaching(obj) {
  return obj && obj.found !== false && Array.isArray(obj.senses) && obj.senses.length > 0;
}

const ALLOWED = ["image/jpeg", "image/png", "image/webp", "image/gif"];

export default async function handler(req, res) {
  if (req.method !== "POST") return res.status(405).json({ error: "POST만 받습니다" });

  const key = process.env.ANTHROPIC_API_KEY;
  if (!key) return res.status(500).json({ error: "ANTHROPIC_API_KEY 가 설정되지 않았습니다" });

  const image = req.body && req.body.image;
  let media = (req.body && req.body.media) || "image/jpeg";
  if (!image) return res.status(400).json({ error: "사진이 없습니다" });
  if (!ALLOWED.includes(media)) media = "image/jpeg";

  const prompt = `이 사진에는 러시아어 글자가 담겨 있다. 사진에서 가장 크고 뚜렷한 러시아어 낱말 하나를 골라, 그 낱말의 사전 원형(기본형)을 표제어로 삼아라. 활용형으로 보이면 원형으로 되돌려라.
초·중급 학습자(청소년)가 읽을 수준으로, 예문은 짧고 쉽게.
뜻은 자주 쓰이는 순서로 최대 3개, 각 뜻마다 예문 1~2개.

아래 JSON만 출력한다. 서문·마크다운·설명 없이 JSON 객체 하나만.
{
 "found": true,
 "seen": "사진에서 실제로 보인 형태(강세 부호 없이)",
 "headword": "강세 부호 없는 원형",
 "stressed": "강세 부호(U+0301)를 넣은 표제어",
 "pron": "한글 근사 발음",
 "pos": "러시아 사전식 약어(сущ., гл., прил., нареч. 등)",
 "pos_ko": "한국어 품사",
 "gram": "문법 정보 한 줄(성·수, 동사면 상 짝과 활용 유형 등)",
 "senses": [{"gloss":"한국어 뜻","note":"쓰임 설명(없으면 빈 문자열)","examples":[{"ru":"러시아어 예문(강세 부호 포함)","ko":"한국어 번역"}]}],
 "idioms": [{"ru":"관용구","ko":"뜻"}],
 "forms": [{"label":"변화형 이름","value":"형태"}],
 "etym": "어원이나 기억에 도움되는 한 줄(없으면 빈 문자열)"
}
러시아어 낱말을 찾을 수 없으면 {"found":false,"msg":"사진에서 러시아어 낱말을 찾지 못했습니다"}`;

  try {
    const t0 = Date.now();
    const r = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-api-key": key,
        "anthropic-version": "2023-06-01"
      },
      body: JSON.stringify({
        model: "claude-sonnet-4-6",
        max_tokens: 1400,
        thinking: { type: "disabled" },
        output_config: { effort: "low" },
        messages: [{
          role: "user",
          content: [
            { type: "image", source: { type: "base64", media_type: media, data: image } },
            { type: "text", text: prompt }
          ]
        }]
      })
    });
    const data = await r.json();
    const ms = Date.now() - t0;
    if (!r.ok) return res.status(r.status).json(data);

    // 인식된 표제어를 공용 캐시에 저장 → 다음부터 글자 검색도 무료.
    const text = (data.content || []).filter((b) => b.type === "text").map((b) => b.text).join("");
    const obj = extractJson(text);
    if (worthCaching(obj)) {
      const clean = JSON.stringify(obj);
      if (obj.headword) await cacheSet(obj.headword, clean);
    }
    return res.status(r.status).json({ ...data, ms });
  } catch (e) {
    return res.status(502).json({ error: String(e) });
  }
}
