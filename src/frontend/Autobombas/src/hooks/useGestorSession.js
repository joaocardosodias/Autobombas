import { useEffect, useMemo, useState } from "react";
import { http } from "@/api/api";
import { calcularFasesOperacao } from "@/lib/calcularFasesOperacao";

function formatPtBRDate(date) {
  return date.toLocaleDateString("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
}

function formatPtBRDayMonth(date) {
  return date.toLocaleDateString("pt-BR", {
    weekday: "long",
    day: "numeric",
    month: "long",
  });
}

function formatHourMinute(value) {
  if (!value) return "--:--";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "--:--";
  return date.toLocaleTimeString("pt-BR", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

function calcularDuracao(inicio, fim) {
  if (!inicio || !fim) return "--";
  const diffMs = fim.getTime() - inicio.getTime();
  if (diffMs < 0) return "--";
  
  const horas = Math.floor(diffMs / (1000 * 60 * 60));
  const minutos = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
  
  if (horas > 0) return `${horas}h ${minutos}m`;
  return `${minutos}m`;
}

export function useGestorSession(id) {
  const [session, setSession] = useState(null);
  const [cardsError, setCardsError] = useState("");
  const [phaseResult, setPhaseResult] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let active = true;

    async function carregarResumoCards() {
      setCardsError("");
      setIsLoading(true);
      try {
        const { data } = await http.get(`/gestao/atividades/${id}`);
        if (!active) return;

        const started = data.timestamp ? new Date(data.timestamp) : null;
        const validStarted =
          started && !Number.isNaN(started.getTime()) ? started : null;

        const ended = data.timestamp_fim ? new Date(data.timestamp_fim) : null;
        const validEnded =
          ended && !Number.isNaN(ended.getTime()) ? ended : null;

        const numeroSessao = id ? id.replace(/\D/g, '') : "0";

        const alertasTratados = data.perigoso
          ? [
              {
                time: validStarted ? formatHourMinute(validStarted) : "00:00",
                title: "Alerta de Risco/Movimento Anormal",
                percent: 100,
                tag: "Crítico",
              },
            ]
          : [];

        setSession({
          sessionNumber: numeroSessao,
          bombaId: data.bomba_id,
          startedAt: data.timestamp || null,
          endedAt: data.timestamp_fim || null,
          operationDate: validStarted ? formatPtBRDate(validStarted) : "-",
          operationDayMonth: validStarted ? formatPtBRDayMonth(validStarted) : "-",
          
          operationTime: validStarted && validEnded
            ? `${formatHourMinute(validStarted)} - ${formatHourMinute(validEnded)}`
            : validStarted ? formatHourMinute(validStarted) : "--:--",
            
          operator: data.operador || "Operador Desconhecido",
          
          duration: calcularDuracao(validStarted, validEnded),
          
          status: data.status || "Desconhecido",
          descricao: data.descricao,
          alerts: alertasTratados,
          timelineStart: validStarted ? formatHourMinute(validStarted) : "--:--",
          timelineEnd: validEnded ? formatHourMinute(validEnded) : "--:--",
        });
      } catch (err) {
        if (!active) return;
        console.error("Erro ao carregar dados: ", err);
        setSession(null);
        setCardsError("Não foi possível carregar os cards da atividade.");
      } finally {
        if (active) setIsLoading(false);
      }
    }

    if (id) carregarResumoCards();

    return () => {
      active = false;
    };
  }, [id]);

  useEffect(() => {
    let active = true;

    async function carregarFasesOperacao() {
      if (!session?.bombaId) {
        setPhaseResult(null);
        return;
      }

      try {
        const [leiturasResp, movZResp, movXYResp] = await Promise.all([
          http.get(`/leituras-corrente/bomba/${session.bombaId}?limite=200`),
          http.get(`/movimentacao-z/bomba/${session.bombaId}?limite=200`),
          http.get(`/movimentacao-xy/bomba/${session.bombaId}?limite=200`),
        ]);

        if (!active) return;

        const inicioMs = session.startedAt
          ? new Date(session.startedAt).getTime()
          : null;
        const fimMs = session.endedAt
          ? new Date(session.endedAt).getTime()
          : null;

        const leiturasSessao = (leiturasResp.data || []).filter((leitura) => {
          const ts = new Date(leitura.timestamp_leitura).getTime();
          if (Number.isNaN(ts)) return false;
          if (inicioMs !== null && ts < inicioMs) return false;
          if (fimMs !== null && ts > fimMs) return false;
          return true;
        });

        const resultado = calcularFasesOperacao(
          leiturasSessao,
          movZResp.data || [],
          movXYResp.data || [],
        );
        setPhaseResult(resultado);
      } catch (err) {
        if (!active) return;
        console.error("Erro ao carregar os dados das fases", err);
        setPhaseResult(null);
      }
    }

    carregarFasesOperacao();

    return () => {
      active = false;
    };
  }, [session?.bombaId, session?.startedAt, session?.endedAt]);

  const phases = useMemo(() => {
    const sourcePhases = phaseResult?.phases || [];
    const total = sourcePhases.reduce((acc, p) => acc + p.percent, 0) || 1;

    return sourcePhases.map((phase, index) => {
      const width = (phase.percent / total) * 100;
      const percentualAnterior = sourcePhases
        .slice(0, index)
        .reduce((sum, p) => sum + p.percent, 0);

      const left = (percentualAnterior / total) * 100;
      return { ...phase, width, left };
    });
  }, [phaseResult]);

  return { session, phases, cardsError, isLoading };
}