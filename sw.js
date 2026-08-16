/* 조군 러한사전 서비스 워커 — 앱 껍데기와 글꼴을 담아두어 인터넷 없이도 열리게 한다. */
const CACHE = "ruko-v23";
const SHELL = [
  "./", "./index.html", "./manifest.webmanifest",
  "./icon-192.png", "./icon-512.png", "./apple-touch-icon.png", "./words.json"
];

self.addEventListener("install", e=>{
  e.waitUntil(caches.open(CACHE).then(c=>c.addAll(SHELL)).then(()=>self.skipWaiting()));
});

self.addEventListener("activate", e=>{
  e.waitUntil(
    caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k))))
      .then(()=>self.clients.claim())
  );
});

self.addEventListener("fetch", e=>{
  const req = e.request;
  if(req.method !== "GET") return;                  // 낱말 조회(POST)는 건드리지 않는다
  const url = new URL(req.url);
  const cacheable = url.origin === location.origin
    || url.host === "fonts.googleapis.com" || url.host === "fonts.gstatic.com";
  if(!cacheable) return;

  e.respondWith(
    caches.match(req).then(hit=>{
      const net = fetch(req).then(res=>{
        if(res && (res.ok || res.type === "opaque")){
          const copy = res.clone();
          caches.open(CACHE).then(c=>c.put(req, copy));
        }
        return res;
      }).catch(()=>hit);
      return hit || net;                             // 있으면 먼저 보여 주고 뒤에서 갱신
    })
  );
});
