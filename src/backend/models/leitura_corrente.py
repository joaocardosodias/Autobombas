from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


class LeituraCorrenteCreate(BaseModel):
    bomba_id: int
    operador_id: Optional[int] = None
    corrente_a: Decimal


class LeituraCorrenteResponse(BaseModel):
    id: int
    bomba_id: int
    operador_id: Optional[int] = None
    operador_nome: Optional[str] = None
    corrente_a: Decimal
    timestamp_leitura: Optional[datetime] = None
