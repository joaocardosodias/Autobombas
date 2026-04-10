import { http } from "@/api/api";
import { useEffect, useState } from "react";

const BOMBA_ID = 1;
const POLLING_INTERVAL_MS = 3000; // 3 segundos para a corrente atualizar

export function useAmperagem(conectado) {
    const [amperagem, setAmperagem] = useState({
        corrente_a: 0,
        percentual: 0,
        classificacao: null,
        sugestao: null,
        loading: true,
        erro: null,
    })

    useEffect(() => {
        if (!conectado) {
            setAmperagem((prev) => ({...prev, loading:false}))
        }
        async function fetchAmperagem() {
        try {
            const {data} = await http.get(`/leituras-corrente/bomba/${BOMBA_ID}/ultima`);
            setAmperagem((prev) => {
                if (parseFloat(data.corrente_a) === prev.corrente_a) return prev;
                return {
                corrente_a: parseFloat(data.corrente_a) ?? 0,
                percentual: parseFloat(data.percentual) ?? 0,
                classificacao: data.classificacao,
                sugestao: data.sugestao,
                loading: false,
                erro: null,
                }
            });
        } catch(err) {
            setAmperagem((prev) => ({
                ...prev,
                loading: false,
                erro: err.response?.data?.detail ?? "Erro ao buscar amperagem",
            }));
        }
    }
    fetchAmperagem();
    const interval = setInterval(fetchAmperagem, POLLING_INTERVAL_MS)
    return () => clearInterval(interval);
    }, [conectado])
    return amperagem;
}