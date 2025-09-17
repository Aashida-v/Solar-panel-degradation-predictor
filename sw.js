self.addEventListener('install', e => {
  e.waitUntil(
    caches.open('solar-cache').then(cache => cache.addAll([
      '/Solar-panel-degradation-predictor/',
      '/Solar-panel-degradation-predictor/index.html',
      '/Solar-panel-degradation-predictor/style.css',
      '/Solar-panel-degradation-predictor/script.js'
    ]))
  );
});

self.addEventListener('fetch', e => {
  e.respondWith(
    caches.match(e.request).then(r => r || fetch(e.request))
  );
});
