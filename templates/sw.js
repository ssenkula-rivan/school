// Service Worker for School Management System - Offline Support
const CACHE_NAME = 'school-management-v1';
const urlsToCache = [
    '/',
    '/accounts/login/',
    '/accounts/register-school/',
    '/static/core/css/offline.css',
    '/static/core/js/offline.js',
    '/static/bootstrap/css/bootstrap.min.css',
    '/static/bootstrap/js/bootstrap.bundle.min.js'
];

// Install event - cache critical resources
self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function(cache) {
                console.log('School Management: Service Worker installing');
                return cache.addAll(urlsToCache);
            })
            .then(function() {
                console.log('School Management: Critical resources cached');
                return self.skipWaiting();
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', function(event) {
    event.waitUntil(
        caches.keys().then(function(cacheNames) {
            return Promise.all(
                cacheNames.map(function(cacheName) {
                    if (cacheName !== CACHE_NAME) {
                        console.log('School Management: Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
        .then(function() {
            console.log('School Management: Service Worker activated');
            return self.clients.claim();
        })
    );
});

// Fetch event - serve from cache when offline
self.addEventListener('fetch', function(event) {
    event.respondWith(
        caches.match(event.request)
            .then(function(response) {
                // Cache hit - return response
                if (response) {
                    console.log('School Management: Serving from cache:', event.request.url);
                    return response;
                }

                // Network request
                return fetch(event.request).then(
                    function(response) {
                        // Check if valid response
                        if(!response || response.status !== 200 || response.type !== 'basic') {
                            return response;
                        }

                        // Clone the response
                        var responseToCache = response.clone();

                        // Cache successful responses
                        if (event.request.url.includes('/static/') || 
                            event.request.url.includes('/accounts/login/') ||
                            event.request.url.includes('/accounts/register-school/')) {
                            caches.open(CACHE_NAME)
                                .then(function(cache) {
                                    cache.put(event.request, responseToCache);
                                });
                        }

                        return response;
                    }
                ).catch(function(error) {
                    console.log('School Management: Network failed, serving offline fallback');
                    
                    // Offline fallbacks
                    if (event.request.url.includes('/accounts/login/')) {
                        return caches.match('/accounts/login/');
                    }
                    
                    if (event.request.url.includes('/accounts/register-school/')) {
                        return caches.match('/accounts/register-school/');
                    }
                    
                    // Generic offline response
                    return new Response(`
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <title>Offline - School Management</title>
                            <meta name="viewport" content="width=device-width, initial-scale=1.0">
                            <style>
                                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f8f9fa; }
                                .offline-icon { font-size: 48px; margin-bottom: 20px; }
                                h1 { color: #dc3545; }
                                p { color: #6c757d; }
                                .btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; text-decoration: none; display: inline-block; margin-top: 20px; }
                            </style>
                        </head>
                        <body>
                            <div class="offline-icon">📡</div>
                            <h1>You're Offline</h1>
                            <p>Please check your internet connection. Some features may not be available until you're back online.</p>
                            <button class="btn" onclick="window.location.reload()">Try Again</button>
                        </body>
                        </html>
                    `, {
                        status: 200,
                        statusText: 'OK',
                        headers: new Headers({
                            'Content-Type': 'text/html'
                        })
                    });
                });
            })
    );
});

// Background sync for offline operations
self.addEventListener('sync', function(event) {
    if (event.tag === 'background-sync') {
        event.waitUntil(doBackgroundSync());
    }
});

function doBackgroundSync() {
    console.log('School Management: Background sync started');
    // This would sync any pending operations
    return Promise.resolve();
}

// Push notifications (if implemented later)
self.addEventListener('push', function(event) {
    const options = {
        body: event.data ? event.data.text() : 'New notification from School Management',
        icon: '/static/icons/icon-192x192.png',
        badge: '/static/icons/badge.png'
    };
    
    event.waitUntil(
        self.registration.showNotification('School Management', options)
    );
});
