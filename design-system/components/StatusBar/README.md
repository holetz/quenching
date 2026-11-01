# StatusBar

The honest state of the data: connection, freshness, pause, refresh, notifications.

`.conn-state` takes `live`, `unstable` or `offline`; the word is always shown beside the dot. `.fresh.stale` warns when the data has aged past the TTL. The bar is one 30px row and is never hidden on desktop.
