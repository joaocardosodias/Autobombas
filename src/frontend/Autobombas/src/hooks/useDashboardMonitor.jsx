import { http } from "@/api/api";
import { useEffect, useState } from "react";
import { Waves, Zap, Navigation, Radar, Cpu } from "lucide-react";

const POLLING_INTERVAL_MS = 3000;
const BOMBA_ID = 1;

const MODULO_INFO = {
  "motor/1":    { name: "Motor Z (Içamento)", type: "Controle de Posição", icon: <Waves /> },
  "corrente/1": { name: "Sensor de Corrente", type: "Leitura Elétrica", icon: <Zap /> },
  "balsa/1":    { name: "Balsa XY", type: "Propulsão", icon: <Navigation /> },
  "sensor/1":   { name: "Radar Proximidade", type: "Prevenção Colisão", icon: <Radar /> },
};

export function useDashboardMonitor() {
  const [sensorsList, setSensorsList] = useState([]);
  const [isSystemOnline, setIsSystemOnline] = useState(false);
  const [lastUpdated, setLastUpdated] = useState("aguardando...");
  const [activeSensorsCount, setActiveSensorsCount] = useState(0);

  useEffect(() => {
    let isMounted = true; 

    const fetchMonitor = async () => {
      try {
        const [hbRes, statusRes] = await Promise.allSettled([
          http.get("/sistema/heartbeat"),
          http.get(`/sistema/status/${BOMBA_ID}`),
        ]);

        if (!isMounted) return; 

        let estaOnline = false;

        // ── 1. Lógica do Header (Lê o "conectado: true/false")
        if (statusRes.status === "fulfilled") {
          const data = statusRes.value.data;
          // Agora lê o booleano exato do backend
          if (data?.conectado === true) {
            estaOnline = true;
          }
        }

        // ── 2. Lógica da Sidebar (Lê o "online: true/false" do array)
        if (hbRes.status === "fulfilled") {
          const modulos = hbRes.value.data || [];
          const qtdAtivos = modulos.filter(m => m.online === true).length;
          setActiveSensorsCount(qtdAtivos);
          
          // Verifica se ALGUM módulo da lista está com online: true
          const temSensorRodando = modulos.some(m => m.online === true);
          if (temSensorRodando) {
            estaOnline = true;
          }

          const formattedSensors = modulos.map((m, index) => {
            const info = MODULO_INFO[m.modulo] || { name: m.modulo, type: "Desconhecido", icon: <Cpu /> };
            return {
              id: index,
              name: info.name,
              type: info.type,
              // Transforma o true/false do backend no texto que a sua interface espera
              status: m.online ? "online" : "offline",
              // Usa a chave correta para ver se houve comunicação
              value: m.ultimo_ping ? "OK" : ""
            };
          });
          setSensorsList(formattedSensors);
        }

        // Atualiza o estado consolidado
        setIsSystemOnline(estaOnline);
        
        // Atualiza relógio
        const agora = new Date();
        setLastUpdated(`${agora.getHours().toString().padStart(2, '0')}:${agora.getMinutes().toString().padStart(2, '0')}`);

      } catch (err) {
        if (isMounted) console.error("Falha no monitoramento do Dashboard", err);
      }
    };

    fetchMonitor();
    const interval = setInterval(fetchMonitor, POLLING_INTERVAL_MS);

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []); 

  return {
    sensorsList,
    isSystemOnline,
    lastUpdated,
    activeSensorsCount
  };
}