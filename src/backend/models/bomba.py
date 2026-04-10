from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


class BombaResponse(BaseModel):
    id: int
    nome: str
    localizacao: Optional[str] = None
    operador_id: int
    diametro_carretel_cm: Decimal
    comprimento_corda_cm: Decimal
    limite_inferior: Optional[Decimal] = None
    limite_superior: Optional[Decimal] = None
    passo_auto_cm: Optional[Decimal] = None
    limite_prox_frente_m: Optional[Decimal] = None
    limite_prox_tras_m: Optional[Decimal] = None
    limite_prox_esq_m: Optional[Decimal] = None
    limite_prox_dir_m: Optional[Decimal] = None
    created_at: Optional[datetime] = None
    total_operacoes_z: Optional[int] = 0
    total_operacoes_xy: Optional[int] = 0


class BombaConfigUpdate(BaseModel):
    """Campos configuráveis da bomba — todos opcionais (partial update)."""
    diametro_carretel_cm: Optional[Decimal] = None
    comprimento_corda_cm: Optional[Decimal] = None
    limite_inferior: Optional[Decimal] = None       # corrente mínima (abaixo = descer)
    limite_superior: Optional[Decimal] = None       # corrente máxima (acima = subir)
    passo_auto_cm: Optional[Decimal] = None
    # Limites de proximidade por direção (módulo 2-C)
    limite_prox_frente_m: Optional[Decimal] = None  # bloqueio obst. à frente (m)
    limite_prox_tras_m: Optional[Decimal] = None    # bloqueio obst. atrás (m)
    limite_prox_esq_m: Optional[Decimal] = None     # bloqueio obst. à esquerda (m)
    limite_prox_dir_m: Optional[Decimal] = None     # bloqueio obst. à direita (m)
