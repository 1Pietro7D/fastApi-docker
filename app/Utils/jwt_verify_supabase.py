from jose import jwt
from jose.backends.cryptography_backend import CryptographyRSAKey
from typing import Any, Dict
from app.Infrastructure.jwks import get_jwks
from app.config import settings

class JWKSKeyNotFound(Exception): ...
class JWTInvalid(Exception): ...

def _select_key(jwks: Dict[str, Any], kid: str) -> Dict[str, Any]:
    for k in jwks.get("keys", []):
        if k.get("kid") == kid:
            return k
    raise JWKSKeyNotFound(f"kid {kid} non trovato")

def verify_supabase_jwt(token: str) -> Dict[str, Any]:
    header = jwt.get_unverified_header(token)
    kid = header.get("kid")
    if not kid:
        raise JWTInvalid("kid mancante nell'header JWT")
    alg = header.get("alg", "RS256")

    key_dict = _select_key(get_jwks(), kid)
    pub_key = CryptographyRSAKey(key_dict, algorithm=alg)

    claims = jwt.decode(
        token,
        pub_key,
        algorithms=[alg],
        audience=settings.TOKEN_AUDIENCE,
        issuer=settings.TOKEN_ISSUER,
        options={"verify_at_hash": False},
    )
    return claims
