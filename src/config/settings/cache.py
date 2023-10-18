CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://redis:6379',
        'OPTIONS': {
            'db': 1
        },
    }
}
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_CACHE_ALIAS = "default"

SESSION_CART_ID = 'cart'

SUCCESS_ORDER_CACHE_EXPIRATION = 86400  # 1 day
