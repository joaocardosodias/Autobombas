import { http } from "@/api/api";
import { useEffect, useState } from "react";

const BOMBA_ID = 1; //customizavel nós podemos ajustar conforme o necessario
const POLLING_INTERVAL_MS = 15000 // atualiza a cada 15 segundos

export function useSistemaStatus() {
    const [status, setStatus] = useState({
        conectado: false,
        totalSensoresAtivos: 0,
        bombaLocalizacao: null,
        loading: true,
        erro: null,
    });

    useEffect(() => {
        async function fetchStatus() {
            try {
                const {data} = await http.get(`sistema/status/${BOMBA_ID}`);
                setStatus({
                    conectado: data.conectado,
                    totalSensoresAtivos: data.total_sensores_ativos,
                    bombaLocalizacao: data.bomba_localizacao,
                    loading: false,
                    erro: null
                });
            } catch (err) {
                setStatus((prev) => ({
                    ...prev,
                    loading: false,
                    erro: err.response?.data?.detail ?? "Erro ao buscar status",
                }));
            }
        }

        fetchStatus()
        const interval = setInterval(fetchStatus, POLLING_INTERVAL_MS);
        return () => clearInterval(interval);
    }, [])
    return status
}