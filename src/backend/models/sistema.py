from pydantic import BaseModel
from typing import Optional
from datetime import datetime
 
 
class SensorAtivo(BaseModel):
    tipo: str               
    bomba_id: int
    ultima_leitura: Optional[datetime] = None
    ativo: bool
 
 
class SistemaStatusResponse(BaseModel):
    conectado: bool
    timestamp: datetime
    total_sensores_ativos: int
    sensores: list[SensorAtivo]
    bomba_id: int
    bomba_nome: str
    bomba_localizacao: Optional[str] = None
 