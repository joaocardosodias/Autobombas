import { http } from "@/api/api";
import { useEffect, useState } from "react";
import { toast } from "sonner";

const BOMBA_ID = 1;
const OPERADOR_ID = 1;

export function useProfundidade() {
    const [posicao, setPosicao] = useState({
        posicao_cm: 0,
        status: null,
        comprimento_corda_cm: null,
        diametro_carretel_cm: null,
        loading: true,
        erro: null,
    });
    const [isDeslocando, setIsDeslocando] = useState(false);

    // Busca configuração da bomba (corda, diamâmetro) — uma vez ao montar
    useEffect(() => {
        http.get(`/bombas/${BOMBA_ID}`)
            .then(({ data }) => {
                setPosicao(prev => ({
                    ...prev,
                    comprimento_corda_cm: data.comprimento_corda_cm ?? null,
                    diametro_carretel_cm: data.diametro_carretel_cm ?? null,
                }));
            })
            .catch(() => {}); // falha silenciosa — restrição apenas não é aplicada
    }, []);

    // Polling de posição a cada 3s
    useEffect(() => {
        async function fetchPosicao() {
            try {
                const { data } = await http.get(`/movimentacao-z/posicao/${BOMBA_ID}`);
                setPosicao(prev => ({
                    ...prev,
                    posicao_cm: data.posicao_cm ?? 0,
                    status: data.status,
                    comprimento_corda_cm: data.comprimento_corda_cm ?? prev.comprimento_corda_cm,
                    loading: false,
                    erro: null,
                }));
            } catch (err) {
                setPosicao(prev => ({
                    ...prev,
                    loading: false,
                    erro: err.response?.data?.detail ?? "Erro ao buscar posição",
                }));
            }
        }
        fetchPosicao();
        const interval = setInterval(fetchPosicao, 3000);
        return () => clearInterval(interval);
    }, []);

    const isMoving = isDeslocando || posicao.status === "EM_ANDAMENTO";

    async function deslocar(deslocamento_cm) {
        if (isMoving) return;
        setIsDeslocando(true);
        setPosicao(prev => ({...prev, erro:null}))
        try {
        const diam = posicao.diametro_carretel_cm ?? 0.852;
        const voltas = deslocamento_cm / (Math.PI * diam);
        await http.post("/movimentacao-z/", {
            bomba_id: BOMBA_ID,
            operador_id: OPERADOR_ID,
            comando_bruto: deslocamento_cm > 0 ? "DESCER" : "SUBIR",
            posicao_inicial_cm: posicao.posicao_cm,
            deslocamento_solicitado_cm: Math.abs(deslocamento_cm),
            voltas_mqtt: parseFloat(voltas.toFixed(4)),
        });
    } catch (err) {
            const msgErro = err.response?.data?.detail
            ?? err.response?.data?.message
            ?? "Operação Bloqueada por medidas de segurança"

            toast.error("Movimento Bloqueado", {
                description:msgErro,
                duration:6000,

            });

            setIsDeslocando(false);
            return;
    } finally {
        setTimeout(() => {
                setIsDeslocando(false);
            }, 4000);
    }
    }
    return { ...posicao, deslocar, isMoving };
}