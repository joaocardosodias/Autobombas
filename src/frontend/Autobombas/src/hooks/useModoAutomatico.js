import { http } from "@/api/api";
import { useEffect, useState } from "react";
import { toast } from "sonner";

const BOMBA_ID = 1;
const OPERADOR_ID = 1;

export function useModoAutomatico() {
    const [statusAuto, setStatusAuto] = useState({
        ativo: false,
        fase: "PARADO",
        ultimo_erro: null,
    })

    useEffect(() => {
        const fetchStatus = async () => {
            try {
                const {data} = await http.get(`/auto/${BOMBA_ID}/status`)
                setStatusAuto(data);

                if (data.fase === "ERRO" && data.ultimo_erro) {
                    toast.error("Erro ao entrar no modo automático" , {
                        description: data.ultimo_erro,
                        id:"auto_erro"
                    })
                }
            } catch(err) {
                console.error("Erro ao ler status do modo auto", err)
            }
        };

        fetchStatus();
        const interval = setInterval(fetchStatus, 3000);
        return () => clearInterval(interval)
    }, [])

    async function  toggleAuto(ligar) {
        try {
            if (ligar) {
                const {data} = await http.post(`/auto/${BOMBA_ID}/ligar`, {operador_id: OPERADOR_ID});
                if (data && data.ok === false) {
                    let msg = data.detail || "Não foi possível ativar o modo automático"
                    if (data.bloqueios && data.bloqueios.lenght > 0) {
                        msg += `${data.bloqueios.join(", ")}`;
                    }

                    toast.error("Bloqueio de segurança", {
                        description: msg,
                        duration: 6000
                    })
                    return;
                }
                toast.success("Modo Automático Ativado")
                setStatusAuto(prev => ({ ...prev, ativo: true }));
            } else {
                const { data } = await http.post(`/auto/desligar/${BOMBA_ID}`);
                
                if (data && data.ok === false) {
                    toast.error("Erro", { description: data.detail });
                    return;
                }

                toast.success("Modo Automático Desativado");
                setStatusAuto(prev => ({ ...prev, ativo: false, fase: "PARADO" })); 
            }
        } catch(err) {
            const msg = err.response?.data?.detail ?? "Erro ao alterar para o modo automático";
            toast.error("Erro no sistema", { description: msg})
        }
    }
    return {statusAuto, toggleAuto};
}