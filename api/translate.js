// 사진에서 사용자가 지정한 구간(잘린 이미지)을 받아, 러시아어 원문을 읽고
// 한국어로 번역해 돌려준다. 열쇠는 서버에만: 환경 변수 ANTHROPIC_API_KEY.

const ALLOWED = ["image/jpeg", "image/png", "image/webp", "image/gif"];

export default async function handler(req, res) {
  if (req.method !== "POST") return res.status(405).json({ error: "POST만 받습니다" });

  const key = process.env.ANTHROPIC_API_KEY;
  if (!key) return res.status(500).json({ error: "ANTHROPIC_API_KEY 가 설정되지 않았습니다" });

  const image = req.body && req.body.image;
  let media = (req.body && req.body.media) || "image/jpeg";
  if (!image) return res.status(400).json({ error: "사진 구간이 없습니다" });
  if (!ALLOWED.includes(media)) media = "image/jpeg";

  const prompt = `이 이미지에는 러시아어 글이 담겨 있다(사용자가 사진에서 잘라 낸 구간).
이미지 속 러시아어를 그대로 읽어 원문을 만들고, 자연스러운 한국어로 번역하라.

아래 JSON만 출력한다. 서문·마크다운·설명 없이 JSON 객체 하나만.
{
 "found": true,
 "ru": "원문(강세 부호 U+0301 포함, 줄바꿈은 공백 하나로)",
 "ko": "한국어 번역"
}
러시아어 글자를 읽을 수 없으면 {"found":false,"msg":"이 구간에서 러시아어를 읽지 못했습니다"}`;

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
        max_tokens: 1200,
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
    return res.status(r.status).json({ ...data, ms });
  } catch (e) {
    return res.status(502).json({ error: String(e) });
  }
}
