// Vercel 서버리스 함수. 열쇠(API 키)를 서버에만 두고 대신 물어봐 주는 창구.
// 환경 변수 ANTHROPIC_API_KEY 를 설정해야 한다.
export default async function handler(req, res) {
  if (req.method !== "POST") return res.status(405).json({ error: "POST만 받습니다" });

  const key = process.env.ANTHROPIC_API_KEY;
  if (!key) return res.status(500).json({ error: "ANTHROPIC_API_KEY 가 설정되지 않았습니다" });

  const term = String((req.body && req.body.term) || "").trim().slice(0, 40);
  if (!term) return res.status(400).json({ error: "찾을 낱말이 없습니다" });

  const prompt = `너는 러시아어–한국어 학습 사전의 편찬자다. 찾는 말: "${term}"

한국어로 입력되면 그에 해당하는 가장 대표적인 러시아어 낱말을 표제어로 삼는다.
초·중급 학습자(청소년)가 읽을 수준으로, 예문은 짧고 쉽게.
뜻은 자주 쓰이는 순서로 최대 4개, 각 뜻마다 예문 1~2개.

아래 JSON만 출력한다. 서문·마크다운·설명 없이 JSON 객체 하나만.
{
 "found": true,
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
낱말을 찾을 수 없으면 {"found":false,"suggest":"가장 비슷한 낱말","msg":"짧은 안내"}`;

  try {
    const r = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-api-key": key,
        "anthropic-version": "2023-06-01"
      },
      body: JSON.stringify({
        model: "claude-sonnet-4-6",
        max_tokens: 2000,
        messages: [{ role: "user", content: prompt }]
      })
    });
    const data = await r.json();
    return res.status(r.status).json(data);
  } catch (e) {
    return res.status(502).json({ error: String(e) });
  }
}
