/**
 * calcularFasesOperacao.js
 *
 * Lógica pura para calcular a distribuição de tempo por fase de operação
 * com base nas leituras de corrente e movimentações registradas.
 *
 * ── Como integrar ──────────────────────────────────────────────────────
 *
 *   import { calcularFasesOperacao } from "@/lib/calcularFasesOperacao";
 *
 *   // 1. Busque os dados da API (axios / fetch):
 *   //    GET /leituras-corrente/bomba/<bomba_id>        → leituras
 *   //    GET /movimentacao-z/bomba/<bomba_id>           → movimentacoesZ
 *   //    GET /movimentacao-xy/bomba/<bomba_id>          → movimentacoesXY
 *
 *   // 2. Chame a função:
 *   const resultado = calcularFasesOperacao(leituras, movimentacoesZ, movimentacoesXY);
 *
 *   // 3. Use no componente:
 *   //    resultado.phases → [{ label, percent, tone }]  (compatível com o JSX existente)
 *   //    resultado.totalOperatingMs → tempo total em ms
 *   //    resultado.timelineStart / timelineEnd → timestamps ISO
 *
 *   // Exemplo com useMemo:
 *   // const resultado = useMemo(
 *   //   () => calcularFasesOperacao(leituras, movZ, movXY),
 *   //   [leituras, movZ, movXY]
 *   // );
 *
 * ───────────────────────────────────────────────────────────────────────
 */

// ── Tipos (JSDoc) ──────────────────────────────────────────────────────

/**
 * Leitura de corrente vinda de GET /leituras-corrente/bomba/<id>
 * @typedef {Object} LeituraCorrente
 * @property {number}  corrente_a          - Amperes medidos
 * @property {number}  percentual          - 0 a 100
 * @property {string}  classificacao       - "baixa" | "normal" | "elevada"
 * @property {string}  timestamp_leitura   - ISO 8601
 * @property {number}  bomba_id
 * @property {number}  operador_id
 */

/**
 * Movimentação vertical vinda de GET /movimentacao-z/bomba/<id>
 * @typedef {Object} MovimentacaoZ
 * @property {string}      status              - "EM_ANDAMENTO" | "CONCLUIDO" | "ABORTADO" | "INTERROMPIDO"
 * @property {string}      timestamp_inicio    - ISO 8601
 * @property {string|null} timestamp_fim
 * @property {number}      posicao_inicial_cm
 * @property {number}      posicao_final_cm
 * @property {number}      deslocamento_real_cm
 */

/**
 * Movimentação horizontal vinda de GET /movimentacao-xy/bomba/<id>
 * @typedef {Object} MovimentacaoXY
 * @property {string}      direcao          - "esquerda" | "direita"
 * @property {number}      duracao_ms
 * @property {string}      status           - "EM_ANDAMENTO" | "CONCLUIDO" | "INTERROMPIDO"
 * @property {string}      timestamp_inicio - ISO 8601
 * @property {string|null} timestamp_fim
 */

/**
 * Opções de configuração dos limiares de classificação.
 * @typedef {Object} OpcoesCalculo
 * @property {number} [limiarDragandoPercent=85]      - percentual >= isso → "dragando"
 * @property {number} [limiarIntermediarioPercent=40]  - percentual >= isso (e < dragando) → "intermediario"
 * @property {number} [maxIntervaloMs=300000]          - cap de 5 min entre leituras (ignora gaps de sensor)
 */

/**
 * Resultado retornado — compatível direto com o JSX de DashGestorSessions.
 * @typedef {Object} ResultadoFases
 * @property {Array<{label: string, percent: number, tone: string}>} phases
 * @property {number}  totalOperatingMs
 * @property {string}  timelineStart  - ISO 8601
 * @property {string}  timelineEnd    - ISO 8601
 */

// ── Constantes ─────────────────────────────────────────────────────────

const DEFAULTS = {
    limiarDragandoPercent: 85,
    limiarIntermediarioPercent: 40,
    maxIntervaloMs: 5 * 60 * 1000, // 5 minutos
};

const FASES_VAZIAS = Object.freeze({
    phases: [
        { label: "Buscando", percent: 0, tone: "search" },
        { label: "Intermediário", percent: 0, tone: "mid" },
        { label: "Dragando", percent: 0, tone: "drag" },
    ],
    totalOperatingMs: 0,
    timelineStart: "",
    timelineEnd: "",
});

// ── Funções auxiliares ─────────────────────────────────────────────────

/**
 * Classifica uma leitura de corrente em uma fase de operação.
 *
 * Regras:
 *   - "elevada" ou percentual >= 85%  →  "dragando"   (bomba dragando ativamente)
 *   - "normal"  ou percentual >= 40%  →  "intermediario" (subindo/descendo/movimentando na água)
 *   - "baixa"   ou percentual <  40%  →  "buscando"   (preparação, bomba fora d'água)
 *
 * @param {LeituraCorrente} leitura
 * @param {OpcoesCalculo}   [opcoes]
 * @returns {"dragando" | "intermediario" | "buscando"}
 */
export function classificarLeitura(leitura, opcoes = {}) {
    const limiarDragando = opcoes.limiarDragandoPercent ?? DEFAULTS.limiarDragandoPercent;
    const limiarInter = opcoes.limiarIntermediarioPercent ?? DEFAULTS.limiarIntermediarioPercent;

    if (leitura.classificacao === "elevada" || leitura.percentual >= limiarDragando) {
        return "dragando";
    }
    if (leitura.classificacao === "normal" || leitura.percentual >= limiarInter) {
        return "intermediario";
    }
    return "buscando";
}

/**
 * Verifica se um timestamp cai dentro de alguma movimentação Z ativa.
 * Usado para refinar intervalos "buscando" → "intermediario" quando há
 * movimentação vertical simultânea (a bomba está na água se movendo).
 *
 * @param {number} tsMs - timestamp em milissegundos
 * @param {MovimentacaoZ[]} movimentacoesZ
 * @returns {boolean}
 */
function estaDuranteMovimentacaoZ(tsMs, movimentacoesZ) {
    for (const mov of movimentacoesZ) {
        const inicio = new Date(mov.timestamp_inicio).getTime();
        const fim = mov.timestamp_fim ? new Date(mov.timestamp_fim).getTime() : Date.now();

        if (tsMs >= inicio && tsMs <= fim) {
            return true;
        }
    }
    return false;
}

// ── Função principal ───────────────────────────────────────────────────

/**
 * Calcula a distribuição de tempo por fase de operação.
 *
 * Recebe arrays de dados vindos da API e retorna um objeto com `phases`
 * no formato esperado pelo componente DashGestorSessions:
 *   [{ label: "Buscando", percent: 25, tone: "search" }, ...]
 *
 * @param {LeituraCorrente[]}  leituras         - Leituras de corrente da sessão
 * @param {MovimentacaoZ[]}    [movimentacoesZ]  - Movimentações verticais (opcional)
 * @param {MovimentacaoXY[]}   [movimentacoesXY] - Movimentações horizontais (opcional)
 * @param {OpcoesCalculo}      [opcoes]           - Limiares configuráveis
 * @returns {ResultadoFases}
 */
export function calcularFasesOperacao(
    leituras,
    movimentacoesZ = [],
    movimentacoesXY = [],
    opcoes = {},
) {
    if (!leituras || leituras.length === 0) {
        return { ...FASES_VAZIAS, phases: [...FASES_VAZIAS.phases] };
    }

    const maxIntervalo = opcoes.maxIntervaloMs ?? DEFAULTS.maxIntervaloMs;

    // Ordenar por timestamp
    const sorted = [...leituras].sort(
        (a, b) => new Date(a.timestamp_leitura) - new Date(b.timestamp_leitura),
    );

    // Caso de leitura única: 100% na fase correspondente
    if (sorted.length === 1) {
        const fase = classificarLeitura(sorted[0], opcoes);
        return {
            phases: [
                { label: "Buscando", percent: fase === "buscando" ? 100 : 0, tone: "search" },
                { label: "Intermediário", percent: fase === "intermediario" ? 100 : 0, tone: "mid" },
                { label: "Dragando", percent: fase === "dragando" ? 100 : 0, tone: "drag" },
            ],
            totalOperatingMs: 0,
            timelineStart: sorted[0].timestamp_leitura,
            timelineEnd: sorted[0].timestamp_leitura,
        };
    }

    // Filtrar movimentações Z ativas (em andamento ou concluídas) para refinamento
    const movZAtivas = movimentacoesZ.filter(
        (m) => m.status === "EM_ANDAMENTO" || m.status === "CONCLUIDO",
    );

    // Acumular tempo por fase
    const acumulado = { dragando: 0, intermediario: 0, buscando: 0 };

    for (let i = 0; i < sorted.length - 1; i++) {
        const atual = sorted[i];
        const proximo = sorted[i + 1];

        const tsAtualMs = new Date(atual.timestamp_leitura).getTime();
        const tsProximoMs = new Date(proximo.timestamp_leitura).getTime();
        const deltaMs = tsProximoMs - tsAtualMs;

        // Ignorar intervalos negativos ou zero
        if (deltaMs <= 0) continue;

        // Cap para não inflar gaps de sensor
        const intervalo = Math.min(deltaMs, maxIntervalo);

        // Classificar pela leitura de corrente
        let fase = classificarLeitura(atual, opcoes);

        // Refinamento: se está "buscando" mas há movimentação Z ativa,
        // reclassificar como "intermediario" (bomba na água, se movimentando)
        if (fase === "buscando" && movZAtivas.length > 0) {
            if (estaDuranteMovimentacaoZ(tsAtualMs, movZAtivas)) {
                fase = "intermediario";
            }
        }

        acumulado[fase] += intervalo;
    }

    const totalMs = acumulado.dragando + acumulado.intermediario + acumulado.buscando;

    if (totalMs === 0) {
        return { ...FASES_VAZIAS, phases: [...FASES_VAZIAS.phases] };
    }

    return {
        phases: [
            {
                label: "Buscando",
                percent: (acumulado.buscando / totalMs) * 100,
                tone: "search",
            },
            {
                label: "Intermediário",
                percent: (acumulado.intermediario / totalMs) * 100,
                tone: "mid",
            },
            {
                label: "Dragando",
                percent: (acumulado.dragando / totalMs) * 100,
                tone: "drag",
            },
        ],
        totalOperatingMs: totalMs,
        timelineStart: sorted[0].timestamp_leitura,
        timelineEnd: sorted[sorted.length - 1].timestamp_leitura,
    };
}
