"""
Validador de Movimentação da Balsa (Módulo 2-A).

Garante que o comando de movimentação da balsa (XY) nunca seja executado
quando a motobomba (Módulo 1-A) estiver fora do ponto de origem.

Regra de negócio: A balsa só pode se movimentar quando a motobomba
estiver no ponto de origem (posição Z = 0 cm, sem movimento em andamento).
"""

from backend.repositories import movimentacao_z_repo

# Ações que efetivamente movimentam a balsa (bloqueadas se motobomba fora da origem)
ACOES_MOVIMENTO_BALSA = {"esquerda", "direita", "frente", "tras"}

# Tolerância em cm para considerar "na origem" (erro de precisão)
TOLERANCIA_ORIGEM_CM = 0.1


def motobomba_esta_na_origem(bomba_id: int) -> tuple[bool, str]:
    """
    Verifica se a motobomba está no ponto de origem, permitindo
    a movimentação segura da balsa.

    Returns:
        Tuple (permitido: bool, mensagem: str)
        - (True, "ok") quando a motobomba está na origem
        - (False, motivo) quando o movimento da balsa deve ser bloqueado
    """
    # 1. Verificar se há movimento Z em andamento
    em_andamento = movimentacao_z_repo.tem_movimento_em_andamento(bomba_id)
    if em_andamento:
        return (
            False,
            "Motobomba em movimento (eixo Z). Aguarde a conclusão antes de movimentar a balsa.",
        )

    # 2. Verificar posição atual (posicao_final_cm da última operação concluída)
    posicao = movimentacao_z_repo.recuperar_posicao(bomba_id)
    if posicao is None:
        # Nunca houve movimento Z registrado → considera-se na origem (0 cm)
        return True, "ok"

    posicao_cm = float(posicao.get("posicao_final_cm", 0) or 0)
    if posicao_cm > TOLERANCIA_ORIGEM_CM:
        return (
            False,
            f"Motobomba fora do ponto de origem (posição atual: {posicao_cm:.1f} cm). "
            "Retorne a motobomba à origem (0 cm) antes de movimentar a balsa.",
        )

    return True, "ok"


def acao_exige_validacao(acao: str) -> bool:
    """Retorna True se a ação é de movimentação da balsa e precisa de validação."""
    return (acao or "").lower().strip() in ACOES_MOVIMENTO_BALSA
