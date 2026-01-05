# YACHAI Common

Paquete compartido de utilidades para proyectos YACHAI.

## Propósito

Eliminar duplicación de código entre:
- **salud_ai-api**: Sistema de citas médicas inteligentes
- **orbe-service**: Servicio multi-tenant con TTS/STT/AI

## Módulos Incluidos

### `yachai_common.cache`
Sistema de caché distribuido con Redis y fallback a memoria.

**Características:**
- Soporte para Redis (distribuido)
- Fallback automático a memoria (TTLCache)
- Decoradores `@cached` y `@async_cached`
- Funciones helper: `get_cached`, `set_cached`, `delete_cached`

**Uso:**
```python
from yachai_common.cache import cached, async_cached, get_cached, set_cached

# Decorador síncrono
@cached(ttl=600, key_prefix="users")
def get_user(user_id: int):
    return expensive_db_query(user_id)

# Decorador asíncrono
@async_cached(ttl=300, key_prefix="api")
async def fetch_data(endpoint: str):
    return await api_call(endpoint)

# Funciones helper
set_cached("key", {"data": "value"}, ttl=3600)
result = get_cached("key")
```

### `yachai_common.security`
Utilidades de seguridad y sanitización de datos.

**Características:**
- Sanitización de logs (tokens, API keys, emails)
- Hashing seguro con salt
- Validaciones (email, tenant_id)
- SecureLogger con sanitización automática

**Uso:**
```python
from yachai_common.security import (
    sanitize_for_logging,
    get_secure_logger,
    hash_secret,
    validate_email
)

# Logger seguro
logger = get_secure_logger(__name__)
logger.info(f"User logged in: {user_data}")  # Sanitiza automáticamente

# Sanitización manual
safe_data = sanitize_for_logging(sensitive_data)

# Validaciones
if validate_email(email):
    send_email(email)
```

## Instalación

### Desarrollo Local

```bash
# Instalar en modo editable
cd yachai-common
pip install -e .

# En salud_ai-api
cd ../salud-inteligente/salud_ai-api
pip install -e ../../yachai-common

# En orbe-service
cd ../orbe-service
pip install -e ../yachai-common
```

### Producción

```bash
pip install git+https://github.com/TectopiaPeru/yachai-common.git
```

## Configuración

### Variables de Entorno

```env
# Redis (opcional, fallback a memoria si no está disponible)
REDIS_URL=redis://localhost:6379/0
```

## Testing

```bash
cd yachai-common
pytest tests/ -v
```

## Versionado

Seguimos [Semantic Versioning](https://semver.org/):
- **MAJOR**: Cambios incompatibles en la API
- **MINOR**: Nueva funcionalidad compatible
- **PATCH**: Correcciones de bugs

## Changelog

### v1.0.0 (2025-01-05)
- ✨ Módulo `cache` con Redis y decoradores
- ✨ Módulo `security` con sanitización y validaciones
- 📝 Documentación completa
- ✅ Tests unitarios

## Contribuir

1. Crear branch: `git checkout -b feature/nueva-funcionalidad`
2. Hacer cambios y tests
3. Commit: `git commit -m "feat: descripción"`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

## Licencia

Propietario - YACHAI/Tectopia
