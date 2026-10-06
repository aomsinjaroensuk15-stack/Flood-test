const C='flood-v1';
self.addEventListener('install',e=>{self.skipWaiting()});
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==C).map(x=>caches.delete(x)))).then(()=>self.clients.claim())));
// network-first: ได้ข้อมูลล่าสุดเสมอ ถ้าออฟไลน์ค่อยใช้ที่เก็บไว้
self.addEventListener('fetch',e=>{
 const u=new URL(e.request.url);
 if(e.request.method!=='GET'||u.origin!==location.origin)return;
 e.respondWith(fetch(e.request).then(r=>{const c=r.clone();caches.open(C).then(x=>x.put(e.request,c));return r}).catch(()=>caches.match(e.request)));
});
