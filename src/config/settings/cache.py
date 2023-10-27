CACHE_HOST = 'cache'
CACHE_PORT = 6379

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': f'redis://{CACHE_HOST}:{CACHE_PORT}',
        'OPTIONS': {
            'db': 1,
        },
    }
}
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_CACHE_ALIAS = "default"

CACHE_TTL = 60 * 15

SESSION_CART_ID = 'cart'
SESSION_COUPON_ID = 'coupon_id'

SUCCESS_ORDER_CACHE_EXPIRATION = 86400  # 1 day
COUPON_ID_CACHE_EXPIRATION = 2592000    # 30 days

