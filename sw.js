const CACHE_NAME = 'backlog-studio-v1';
const ASSETS = ['./', './index.html', './styles.css', './app.js', './assets/icon.svg', './manifest.webmanifest'];
self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', event => {
  event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k.startsWith('backlog-studio-') && k !== CACHE_NAME).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET' || new URL(event.request.url).origin !== self.location.origin) return;
  event.respondWith(fetch(event.request).then(response => {
    if (response.ok) { const cloned = response.clone(); caches.open(CACHE_NAME).then(cache => cache.put(event.request, cloned)); }
    return response;
  }).catch(() => caches.match(event.request)));
});
