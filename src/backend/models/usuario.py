from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class LoginRequest(BaseModel):
    email: str
    senha: str


class LoginResponse(BaseModel):
    token: str
    usuario_id: int
    nome: str
    role: str


class UsuarioResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    created_at: Optional[datetime] = None

class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    role: str
