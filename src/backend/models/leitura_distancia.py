from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


class LeituraDistanciaCreate(BaseModel):
    bomba_id: int
    operador_id: int
    distancia_frente_m: Decimal
    distancia_tras_m: Decimal
    distancia_esq_m: Decimal
    distancia_dir_m: Decimal


class LeituraDistanciaResponse(BaseModel):
    id: int
    bomba_id: int
    operador_id: int
    operador_nome: Optional[str] = None
    distancia_frente_m: Decimal
    distancia_tras_m: Decimal
    distancia_esq_m: Decimal
    distancia_dir_m: Decimal
    timestamp_leitura: Optional[datetime] = None
