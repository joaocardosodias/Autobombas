import { http } from "@/api/api";
import { useEffect, useRef, useState } from "react";

export function useSensores(conectado) {
    const [sensores, setSensores] = useState([])
    const [lastUpdated, setLastUpdate] = useState("nunca")
    const falhasConsecutivas = useRef(0);

    useEffect(() => {
        if (!conectado) return

        let interval;
        async function fetchSensores() {
            if (falhasConsecutivas.current >= 3) {
                clearInterval(interval);
                return;
            }

            try {
                const {data} = await http.get(`/sistema/sensores`);
                falhasConsecutivas.current = 0;
                setSensores(data)

                const agora = new Date()
                setLastUpdate(`${agora.getHours()}:${agora.getMinutes().toString().padStart(2, '0')}`);

            } catch (err) {
                falhasConsecutivas.current += 1;
                console.error("Erro ao buscar sensores: ", err);
            }
        }
        fetchSensores()
        interval = setInterval(fetchSensores, 5000)

        return () => clearInterval(interval)

    }, [conectado])

    return{ sensoresApi: sensores, lastUpdated}
}