"""
Report Cache Utility
=====================
Uses Django's built-in cache framework so it works with any backend:
  - LocMemCache (current dev setup) — works out of the box
  - Redis         — just change CACHES in settings.py to django-redis, no code change needed

Cache key format:
    report:{module}:{report_type}:{db_alias}:{params_hash}

TTL strategy (configurable per report via cache_ttl on the view):
    - Real-time reports (pending orders, payment collection): cache_ttl = 0  → no cache
    - Standard reports (register, analysis): cache_ttl = 300  → 5 minutes
    - Heavy aggregate reports (aging, profitability, tax): cache_ttl = 900  → 15 minutes
"""

import hashlib
import json
import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)

MODULE_PREFIX = "report"


def _make_cache_key(module: str, report_type: str, db_alias: str, params: dict) -> str:
    """
    Build a deterministic cache key from report identity + filter params.
    Params are sorted before hashing so ?a=1&b=2 and ?b=2&a=1 hit the same key.
    """
    params_str = json.dumps(params, sort_keys=True, default=str)
    params_hash = hashlib.md5(params_str.encode()).hexdigest()[:12]
    return f"{MODULE_PREFIX}:{module}:{report_type}:{db_alias}:{params_hash}"


def get_cached(module: str, report_type: str, db_alias: str, params: dict):
    """Return cached report payload or None."""
    key = _make_cache_key(module, report_type, db_alias, params)
    result = cache.get(key)
    if result is not None:
        logger.debug("Cache HIT: %s", key)
    return result


def set_cached(module: str, report_type: str, db_alias: str, params: dict, payload: dict, ttl: int):
    """Store report payload in cache with the given TTL (seconds)."""
    if ttl <= 0:
        return
    key = _make_cache_key(module, report_type, db_alias, params)
    cache.set(key, payload, timeout=ttl)
    logger.debug("Cache SET: %s (ttl=%ds)", key, ttl)


def invalidate(module: str, report_type: str = None):
    """
    Best-effort invalidation.
    With LocMemCache: clears all cache (no prefix delete support).
    With Redis + django-redis: deletes only matching keys via pattern delete.
    """
    try:
        # django-redis supports cache.delete_pattern()
        pattern = f"{MODULE_PREFIX}:{module}:{report_type or '*'}:*"
        if hasattr(cache, "delete_pattern"):
            cache.delete_pattern(pattern)
            logger.debug("Cache INVALIDATE pattern: %s", pattern)
        else:
            cache.clear()
            logger.debug("Cache CLEAR (no pattern delete support)")
    except Exception as exc:
        logger.warning("Cache invalidation failed: %s", exc)
