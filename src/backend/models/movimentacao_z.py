from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


class MovimentacaoZCreate(BaseModel):
    bomba_id: int
    operador_id: int
    comando_bruto: str
    posicao_inicial_cm: Decimal
    deslocamento_solicitado_cm: Decimal
    voltas_mqtt: Decimal


class MovimentacaoZUpdate(BaseModel):
    status: str                              # CONCLUIDO, ABORTADO
    deslocamento_real_cm: Optional[Decimal] = None
    posicao_final_cm: Optional[Decimal] = None


class MovimentacaoZResponse(BaseModel):
    id: int
    bomba_id: int
    operador_id: int
    operador_nome: Optional[str] = None
    comando_bruto: str
    posicao_inicial_cm: Decimal
    deslocamento_solicitado_cm: Decimal
    deslocamento_real_cm: Optional[Decimal] = None
    posicao_final_cm: Optional[Decimal] = None
    voltas_mqtt: Decimal
    status: str
    timestamp_inicio: Optional[datetime] = None
    timestamp_fim: Optional[datetime] = None
