const CACHE_NAME = 'busao-static-v1';
const RUNTIME_CACHE = 'busao-runtime-v1';

const PRECACHE_URLS = [
  '/',
  '/templates/home.html',
  '/static/css/home.min.css',
  '/static/javascript/config.min.js',
  '/static/javascript/api.min.js',
  '/static/javascript/modais.min.js',
  '/static/javascript/ui.min.js',
  '/static/javascript/home.min.js',
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(PRECACHE_URLS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.filter(key => key !== CACHE_NAME && key !== RUNTIME_CACHE).map(key => caches.delete(key))
    ))
  );
  self.clients.claim();
});

function isStaticRequest(request) {
  return request.destination === 'script' || request.destination === 'style' || request.destination === 'image' || request.url.match(/\.(?:js|css|png|jpg|jpeg|svg|woff2?|gif)$/i);
}

self.addEventListener('fetch', event => {
  const { request } = event;

  if (isStaticRequest(request)) {
    // Cache-first for static assets
    event.respondWith(
      caches.match(request).then(cachedResponse => {
        if (cachedResponse) return cachedResponse;
        return caches.open(RUNTIME_CACHE).then(cache =>
          fetch(request).then(response => {
            if (response && response.status === 200) cache.put(request, response.clone());
            return response;
          }).catch(() => cachedResponse)
        );
      })
    );
    return;
  }

  // Network-first for API/data requests
  event.respondWith(
    fetch(request).then(response => {
      return caches.open(RUNTIME_CACHE).then(cache => {
        if (response && response.status === 200 && request.method === 'GET') {
          cache.put(request, response.clone());
        }
        return response;
      });
    }).catch(() => caches.match(request))
  );
});
