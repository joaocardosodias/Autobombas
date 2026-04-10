from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MovimentacaoXYCreate(BaseModel):
    bomba_id: int
    operador_id: int
    direcao: str                             # esquerda, direita


class MovimentacaoXYUpdate(BaseModel):
    status: str                              # CONCLUIDO, INTERROMPIDO
    duracao_ms: Optional[int] = None


class MovimentacaoXYResponse(BaseModel):
    id: int
    bomba_id: int
    operador_id: int
    operador_nome: Optional[str] = None
    direcao: str
    duracao_ms: Optional[int] = None
    status: str
    timestamp_inicio: Optional[datetime] = None
    timestamp_fim: Optional[datetime] = None
