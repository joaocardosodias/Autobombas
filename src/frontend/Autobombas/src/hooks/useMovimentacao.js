import { http } from "@/api/api";
import { toast } from "sonner";

const BOMBA_ID = 1;
const OPERADOR_ID = 1;


export function useMovimentacaoXY() {
    const dispararErro = (err) => {
        const msg = err.response?.data?.detail ?? err.message ?? "Operação bloqueada";
        toast.error("Movimento Bloqueado", {
            description:msg,
            duration:6000,
        })
        
    }
    async function mover(direcao) {
        try {
            await http.post("/movimentacao-xy/", {
                bomba_id: BOMBA_ID,
                operador_id: OPERADOR_ID,
                direcao,
            });
        } catch(err) {
            dispararErro(err);
        }
    }
    async function alternarEnergia(ligar) {
        try {
            await http.post(`/movimentacao-xy/comando/${BOMBA_ID}`, {
                acao: ligar ? "ligar" : "parar",
                operador_id: OPERADOR_ID
            })
            return true
        } catch (err) {
            dispararErro(err)
            return false
        }
    }
    async function parar() {
        try {
            await http.post(`/movimentacao-xy/comando/${BOMBA_ID}`, {
                acao: "parar",
                operador_id: OPERADOR_ID
            });
        } catch(err) {
            dispararErro(err)
        }
    }
    return {mover, parar, alternarEnergia}
}