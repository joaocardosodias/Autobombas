import { http } from "@/api/api";
import { useEffect, useState, useCallback } from "react";

const POLLING_INTERVAL_MS = 3000;
const BOMBA_ID = 1;

// ── Nomes amigáveis dos módulos (chave = tópico MQTT real do heartbeat) ────
const MODULO_INFO = {
  "motor/1":    { nome: "Motor Z — Içamento",         descricao: "Módulo 1-A: controla a descida e subida da motobomba" },
  "corrente/1": { nome: "Sensor de Corrente",          descricao: "Módulo 1-B: mede a corrente elétrica da bomba" },
  "balsa/1":    { nome: "Balsa XY — Propulsão",        descricao: "Módulo 2-A: controla os motores de direção da balsa" },
  "sensor/1":   { nome: "Radar de Proximidade",         descricao: "Módulo 2-C: mede a distância a obstáculos nas 4 direções" },
};

export function useSensoresPage() {
  const [heartbeat, setHeartbeat]       = useState([]);
  const [statusSistema, setStatusSistema] = useState(null);
  const [ultimaLeituraCorrente, setUltimaLeituraCorrente] = useState(null);
  const [ultimaLeituraRadar, setUltimaLeituraRadar]       = useState(null);
  const [lastUpdated, setLastUpdated]   = useState(null);
  const [loading, setLoading]           = useState(true);
  const [erro, setErro]                 = useState(null);

  const fetchTudo = useCallback(async () => {
    try {
      const [hbRes, statusRes, correnteRes, radarRes] = await Promise.allSettled([
        http.get("/sistema/heartbeat"),
        http.get(`/sistema/status/${BOMBA_ID}`),
        http.get(`/leituras-corrente/bomba/${BOMBA_ID}/ultima`),
        http.get(`/leituras-distancia/bomba/${BOMBA_ID}/ultima`),
      ]);

      if (hbRes.status === "fulfilled") setHeartbeat(hbRes.value.data);
      if (statusRes.status === "fulfilled") setStatusSistema(statusRes.value.data);
      if (correnteRes.status === "fulfilled") setUltimaLeituraCorrente(correnteRes.value.data);
      if (radarRes.status === "fulfilled") setUltimaLeituraRadar(radarRes.value.data);

      setLastUpdated(new Date());
      setErro(null);
    } catch (err) {
      setErro(err.response?.data?.detail ?? "Erro ao buscar dados dos sensores");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTudo();
    const interval = setInterval(fetchTudo, POLLING_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [fetchTudo]);

  // Enriquece heartbeat com info amigável
  const modulos = heartbeat.map((m) => ({
    ...m,
    ...(MODULO_INFO[m.modulo] ?? { nome: m.modulo, descricao: "" }),
  }));

  return {
    modulos,
    statusSistema,
    ultimaLeituraCorrente,
    ultimaLeituraRadar,
    lastUpdated,
    loading,
    erro,
    recarregar: fetchTudo,
  };
}
