"""
Módulo de caché distribuido con soporte para Redis y fallback a memoria.
Optimiza rendimiento y reduce llamadas a servicios externos (OpenAI, ElevenLabs).
"""

import json
import logging
import os
from functools import wraps
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)

# Intentar importar dependencias opcionales
try:
    from cachetools import TTLCache

    CACHETOOLS_AVAILABLE = True
except ImportError:
    CACHETOOLS_AVAILABLE = False
    logger.warning("[CACHE] cachetools no disponible, usando dict simple")

try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("[CACHE] Redis no disponible, usando caché en memoria")


class SimpleTTLCache:
    """Implementación simple de TTL cache como fallback."""

    def __init__(self, maxsize: int = 1000, ttl: int = 3600):
        self._cache: dict = {}
        self._maxsize = maxsize
        self._ttl = ttl

    @property
    def maxsize(self):
        return self._maxsize

    def __contains__(self, key):
        return key in self._cache

    def __getitem__(self, key):
        return self._cache[key]

    def __setitem__(self, key, value):
        if len(self._cache) >= self._maxsize:
            # Eliminar primera entrada (FIFO simple)
            first_key = next(iter(self._cache))
            del self._cache[first_key]
        self._cache[key] = value

    def __delitem__(self, key):
        del self._cache[key]

    def __len__(self):
        return len(self._cache)


class CacheManager:
    """
    Gestor de caché con soporte para Redis (distribuido) y fallback a memoria.
    Especialmente útil para cachear respuestas de TTS y prompts de IA.
    """

    def __init__(self):
        self.redis_client = None

        # Usar TTLCache si está disponible, sino fallback simple
        if CACHETOOLS_AVAILABLE:
            self.memory_cache = TTLCache(maxsize=1000, ttl=3600)
        else:
            self.memory_cache = SimpleTTLCache(maxsize=1000, ttl=3600)

        # Intentar conectar a Redis si está disponible
        if REDIS_AVAILABLE:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            try:
                self.redis_client = redis.from_url(
                    redis_url,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                    health_check_interval=30,
                )
                # Verificar conexión
                self.redis_client.ping()
                logger.info(f"[CACHE] Redis conectado: {redis_url}")
            except Exception as e:
                logger.warning(f"[CACHE] No se pudo conectar a Redis: {e}")
                self.redis_client = None

    def get(self, key: str) -> Optional[Any]:
        """
        Obtiene valor del caché.
        Intenta Redis primero, luego memoria.
        """
        # Intentar Redis
        if self.redis_client:
            try:
                value = self.redis_client.get(key)
                if value:
                    logger.debug(f"[CACHE] Hit en Redis: {key}")
                    return json.loads(value)
            except Exception as e:
                logger.warning(f"[CACHE] Error leyendo de Redis: {e}")

        # Fallback a memoria
        if key in self.memory_cache:
            logger.debug(f"[CACHE] Hit en memoria: {key}")
            return self.memory_cache[key]

        logger.debug(f"[CACHE] Miss: {key}")
        return None

    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """
        Guarda valor en caché con TTL.
        Intenta Redis primero, siempre guarda en memoria.
        """
        # Intentar Redis
        if self.redis_client:
            try:
                serialized = json.dumps(value)
                self.redis_client.setex(key, ttl, serialized)
                logger.debug(f"[CACHE] Set en Redis: {key} (TTL: {ttl}s)")
            except Exception as e:
                logger.warning(f"[CACHE] Error escribiendo en Redis: {e}")

        # Siempre guardar en memoria como backup
        self.memory_cache[key] = value
        logger.debug(f"[CACHE] Set en memoria: {key}")
        return True

    def delete(self, key: str) -> bool:
        """
        Elimina valor del caché.
        """
        deleted = False

        # Eliminar de Redis
        if self.redis_client:
            try:
                self.redis_client.delete(key)
                deleted = True
            except Exception as e:
                logger.warning(f"[CACHE] Error eliminando de Redis: {e}")

        # Eliminar de memoria
        if key in self.memory_cache:
            del self.memory_cache[key]
            deleted = True

        return deleted

    def clear_pattern(self, pattern: str) -> int:
        """
        Elimina todas las claves que coinciden con el patrón.
        Solo funciona con Redis.
        """
        if not self.redis_client:
            logger.warning("[CACHE] clear_pattern solo funciona con Redis")
            return 0

        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                deleted = self.redis_client.delete(*keys)
                logger.info(
                    f"[CACHE] Eliminadas {deleted} claves con patrón: {pattern}"
                )
                return deleted
        except Exception as e:
            logger.error(f"[CACHE] Error eliminando patrón: {e}")

        return 0

    def get_stats(self) -> dict:
        """
        Obtiene estadísticas del caché.
        """
        stats = {
            "redis_available": self.redis_client is not None,
            "memory_cache_size": len(self.memory_cache),
            "memory_cache_maxsize": self.memory_cache.maxsize,
        }

        if self.redis_client:
            try:
                info = self.redis_client.info("stats")
                stats["redis_keys"] = self.redis_client.dbsize()
                stats["redis_hits"] = info.get("keyspace_hits", 0)
                stats["redis_misses"] = info.get("keyspace_misses", 0)
            except Exception as e:
                logger.warning(f"[CACHE] Error obteniendo stats de Redis: {e}")

        return stats


# Instancia global del gestor de caché
cache_manager = CacheManager()


# Funciones de conveniencia
def get_cached(key: str) -> Optional[Any]:
    """Obtiene valor del caché."""
    return cache_manager.get(key)


def set_cached(key: str, value: Any, ttl: int = 3600) -> bool:
    """Guarda valor en caché."""
    return cache_manager.set(key, value, ttl)


def delete_cached(key: str) -> bool:
    """Elimina valor del caché."""
    return cache_manager.delete(key)


def clear_cache_pattern(pattern: str) -> int:
    """Elimina claves por patrón."""
    return cache_manager.clear_pattern(pattern)


def get_cache_stats() -> dict:
    """Obtiene estadísticas del caché."""
    return cache_manager.get_stats()


# Decorador para cachear funciones
def cached(ttl: int = 3600, key_prefix: str = ""):
    """
    Decorador para cachear resultados de funciones.

    Uso:
        @cached(ttl=600, key_prefix="tts")
        def generate_speech(text: str):
            return expensive_tts_call(text)
    """

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generar clave de caché
            cache_key = f"{key_prefix}:{func.__name__}" if key_prefix else func.__name__
            if args:
                cache_key += f":{':'.join(str(a) for a in args)}"
            if kwargs:
                cache_key += (
                    f":{':'.join(f'{k}={v}' for k, v in sorted(kwargs.items()))}"
                )

            # Intentar obtener del caché
            try:
                cached_value = cache_manager.get(cache_key)
                if cached_value is not None:
                    return cached_value
            except Exception:
                pass  # Si falla el caché, ejecutar función normalmente

            # Ejecutar función y cachear resultado
            result = func(*args, **kwargs)
            try:
                cache_manager.set(cache_key, result, ttl)
            except Exception:
                pass  # Si falla guardar en caché, retornar resultado igual
            return result

        return wrapper

    return decorator


# Decorador async para cachear funciones asíncronas
def async_cached(ttl: int = 3600, key_prefix: str = ""):
    """
    Decorador para cachear resultados de funciones asíncronas.

    Uso:
        @async_cached(ttl=600, key_prefix="ai")
        async def get_ai_response(prompt: str):
            return await expensive_ai_call(prompt)
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generar clave de caché
            cache_key = f"{key_prefix}:{func.__name__}" if key_prefix else func.__name__
            if args:
                cache_key += f":{':'.join(str(a) for a in args)}"
            if kwargs:
                cache_key += (
                    f":{':'.join(f'{k}={v}' for k, v in sorted(kwargs.items()))}"
                )

            # Intentar obtener del caché
            cached_value = cache_manager.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Ejecutar función y cachear resultado
            result = await func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            return result

        return wrapper

    return decorator
