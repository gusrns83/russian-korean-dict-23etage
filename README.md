# 러한사전 — 홈 화면 앱(PWA) 올리는 법

아이 폰 홈 화면에 사전 아이콘을 두고, 누르면 주소창 없이 전체 화면으로 열리게 하는 방법입니다.
스토어 등록도, 심사도, 등록비도 없습니다.

## 들어 있는 것

| 파일 | 하는 일 |
|---|---|
| `index.html` | 사전 본체 |
| `manifest.webmanifest` | 앱 이름·아이콘·색을 알려 주는 명찰 |
| `sw.js` | 껍데기와 글꼴을 담아 두어 인터넷 없이도 열리게 함 |
| `icon-192.png` `icon-512.png` `apple-touch-icon.png` | 홈 화면 아이콘 |
| `api/lookup.js` | 열쇠(API 키)를 서버에만 두고 대신 물어봐 주는 창구 |

## 왜 창구(`api/lookup.js`)가 필요한가

지금 사전은 뜻풀이를 그때그때 AI에게 물어봅니다. 물어보려면 열쇠가 필요한데,
그 열쇠를 `index.html` 안에 적어 두면 그 주소에 들어온 누구나 꺼내 쓸 수 있습니다.
그래서 열쇠는 서버에만 두고, 사전은 서버에게 부탁만 하는 구조로 만들어 두었습니다.

## 올리는 순서 (Vercel 기준, 무료)

1. [vercel.com](https://vercel.com) 가입 (GitHub 계정으로 하면 편합니다)
2. 이 폴더를 통째로 GitHub에 올리거나, Vercel CLI로 `vercel` 한 줄 실행
3. Vercel 프로젝트 화면 → **Settings → Environment Variables** 에서 추가
   - 이름: `ANTHROPIC_API_KEY`
   - 값: [console.anthropic.com](https://console.anthropic.com) 에서 발급받은 키
4. 다시 배포(Redeploy). 끝입니다. `https://무언가.vercel.app` 주소가 나옵니다.

> Cloudflare Pages를 쓰신다면 `api/lookup.js` 를 `functions/api/lookup.js` 로 옮기고
> `export async function onRequestPost({request, env})` 형태로 조금 바꾸면 됩니다.

## 폰에 앉히기

- **아이폰/아이패드** — Safari로 그 주소를 열고, 아래 공유 단추 → **홈 화면에 추가**.
  (크롬 말고 Safari로 해야 합니다.)
- **안드로이드** — 크롬으로 열면 화면 아래쪽에 **홈 화면에 추가** 단추가 나옵니다.

앉히고 나면 아이콘을 눌러 여는 순간 주소창 없이 전체 화면으로 뜹니다.

## 인터넷이 없을 때

한 번 찾아본 낱말은 그 기기에 남아, 지하철이나 비행기에서도 그대로 열립니다.
새 낱말만 인터넷이 필요합니다. 화면 오른쪽 위에 **오프라인** 이라고 뜹니다.

## 고칠 만한 곳

- 사전 이름·색: `index.html` 맨 위 `:root` 안의 색값, `manifest.webmanifest` 의 이름
- 뜻풀이 방식: `api/lookup.js` 안의 `prompt` 문장 (예문 수, 난이도 등)
- 아이콘: `icon-512.png` 를 같은 크기의 다른 그림으로 바꾸면 됩니다

## 다음에 할 만한 일

자주 쓰는 낱말 2~3천 개를 미리 만들어 `words.json` 으로 굳혀 두면,
서버도 열쇠도 필요 없어지고 모든 낱말이 즉시, 인터넷 없이 열립니다.
교과서나 단어장 목록이 있으면 그걸로 시작하면 됩니다.
