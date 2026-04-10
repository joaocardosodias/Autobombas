from datetime import timedelta
import bcrypt
from flask_jwt_extended import create_access_token, get_jwt_identity

from backend.config import settings


def verificar_senha(senha: str, hash_armazenado: str) -> bool:
    return bcrypt.checkpw(senha.encode(), hash_armazenado.encode())


def criar_token(usuario_id: int, role: str) -> str:
    return create_access_token(
        identity=str(usuario_id),
        additional_claims={"role": role},
        expires_delta=timedelta(hours=settings.JWT_EXPIRATION_HOURS),
    )

def gerar_hash_senha(senha: str) -> str:
    return bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
