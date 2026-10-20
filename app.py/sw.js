
const CACHE_NAME = "nexa-ai-v2";

self.addEventListener("install", (event) => {
    self.skipWaiting();
});

self.addEventListener("activate", (event) => {
    event.waitUntil(
        (async () => {
            const keys = await caches.keys();

            await Promise.all(
                keys
                    .filter((key) => key.startsWith("nexa-ai-"))
                    .map((key) => caches.delete(key))
            );

            await self.clients.claim();
        })()
    );
});

self.addEventListener("fetch", (event) => {
    // Streamlit requests ko cache nahi karna.
});
