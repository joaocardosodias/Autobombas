import { SideBar } from "@/components/Sidebar";
import { DashboardHeader } from "@/components/DashboardHeader";
import { StatusIndicator } from "@/components/DashboardStatus";
import { useSistemaStatus } from "@/hooks/useSistemaStatus";
import { useSensoresPage } from "@/hooks/useSensoresPage";
import { cn } from "@/lib/utils";
import {
  Cpu,
  Wifi,
  WifiOff,
  Zap,
  Navigation,
  Radio,
  Activity,
  RefreshCw,
  Clock,
  CheckCircle2,
  XCircle,
  ChevronRight,
  ArrowDown,
  ArrowUp,
  ArrowLeft,
  ArrowRight,
} from "lucide-react";

// ── Helpers ────────────────────────────────────────────────────────────

function formatTs(date) {
  if (!date) return "—";
  return date.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}



// ── Sub-components ─────────────────────────────────────────────────────

function ModuloCard({ modulo }) {
  const online = modulo.online;

  const ICONES = {
    "motor/1":    <Activity size={22} />,
    "corrente/1": <Zap size={22} />,
    "balsa/1":    <Navigation size={22} />,
    "sensor/1":   <Radio size={22} />,
  };

  const icone = ICONES[modulo.modulo] ?? <Cpu size={22} />;

  return (
    <div
      className={cn(
        "bg-card border rounded-2xl overflow-hidden shadow-sm hover:shadow-md transition-all duration-200",
        online ? "border-green-200" : "border-red-200"
      )}
    >
      {/* accent bar */}
      <div className={cn("h-1 w-full", online ? "bg-green-500" : "bg-red-500")} />

      <div className="p-5">
        {/* Header row */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div
              className={cn(
                "p-2.5 rounded-xl",
                online ? "bg-green-500/10 text-green-600" : "bg-red-500/10 text-red-500"
              )}
            >
              {icone}
            </div>
            <div>
              <div className="font-semibold text-primary text-sm leading-tight">{modulo.nome}</div>
              <div className="text-xs text-muted-foreground mt-0.5">{modulo.descricao}</div>
            </div>
          </div>

          {/* Badge online/offline */}
          <div
            className={cn(
              "flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold",
              online
                ? "bg-green-500/10 text-green-700"
                : "bg-red-500/10 text-red-600"
            )}
          >
            {online ? <CheckCircle2 size={12} /> : <XCircle size={12} />}
            {online ? "ONLINE" : "OFFLINE"}
          </div>
        </div>

        {/* Último PING — ou placeholder se nunca pingou */}
        {modulo.ultimo_ping ? (
          <div className="bg-secondary/50 rounded-xl p-3">
            <div className="text-xs text-muted-foreground mb-1">Último PING</div>
            <div className="text-sm font-medium text-primary">
              {new Date(modulo.ultimo_ping).toLocaleTimeString("pt-BR")}
            </div>
          </div>
        ) : (
          <div className="bg-secondary/30 rounded-xl p-3 text-xs text-muted-foreground italic">
            Aguardando primeiro PING do módulo…
          </div>
        )}

        {/* Pulse indicator */}
        {online && (
          <div className="flex items-center gap-2 mt-3 pt-3 border-t border-border">
            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            <span className="text-xs text-green-600 font-medium">Comunicação ativa</span>
          </div>
        )}
        {!online && (
          <div className="flex items-center gap-2 mt-3 pt-3 border-t border-border">
            <WifiOff size={12} className="text-red-400" />
            <span className="text-xs text-red-500 font-medium">Sem sinal de heartbeat</span>
          </div>
        )}
      </div>
    </div>
  );
}

function LeituraCorrenteCard({ leitura }) {
  if (!leitura) return (
    <div className="bg-card border border-border rounded-2xl p-6 flex items-center justify-center h-full">
      <p className="text-sm text-muted-foreground">Sem leitura disponível</p>
    </div>
  );

  const corrente = parseFloat(leitura.corrente_a ?? 0);
  const ts = leitura.timestamp_leitura
    ? new Date(leitura.timestamp_leitura).toLocaleTimeString("pt-BR")
    : "—";

  return (
    <div className="bg-card border border-yellow-200 rounded-2xl overflow-hidden shadow-sm">
      <div className="h-1 w-full bg-[#e4bc34]" />
      <div className="p-5">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2.5 rounded-xl bg-[#e4bc34]/10 text-[#b08d00]">
            <Zap size={20} />
          </div>
          <div>
            <div className="font-semibold text-primary text-sm">Última Leitura de Corrente</div>
            <div className="text-xs text-muted-foreground">Módulo 1-B · Sensor de Corrente</div>
          </div>
        </div>
        <div className="text-4xl font-bold text-primary mb-1">
          {corrente.toFixed(3)} <span className="text-xl font-medium text-muted-foreground">A</span>
        </div>
        <div className="flex items-center gap-1.5 text-xs text-muted-foreground mt-3">
          <Clock size={12} />
          Registrado às {ts}
        </div>
      </div>
    </div>
  );
}

function LeituraRadarCard({ leitura }) {
  if (!leitura) return (
    <div className="bg-card border border-border rounded-2xl p-6 flex items-center justify-center h-full">
      <p className="text-sm text-muted-foreground">Sem leitura disponível</p>
    </div>
  );

  const ts = leitura.timestamp_leitura
    ? new Date(leitura.timestamp_leitura).toLocaleTimeString("pt-BR")
    : "—";

  const dirs = [
    { icon: <ArrowUp size={14} />,    label: "Frente",   val: leitura.distancia_frente_m },
    { icon: <ArrowDown size={14} />,  label: "Trás",     val: leitura.distancia_tras_m   },
    { icon: <ArrowLeft size={14} />,  label: "Esquerda", val: leitura.distancia_esq_m    },
    { icon: <ArrowRight size={14} />, label: "Direita",  val: leitura.distancia_dir_m    },
  ];

  return (
    <div className="bg-card border border-blue-200 rounded-2xl overflow-hidden shadow-sm">
      <div className="h-1 w-full bg-blue-500" />
      <div className="p-5">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2.5 rounded-xl bg-blue-500/10 text-blue-600">
            <Radio size={20} />
          </div>
          <div>
            <div className="font-semibold text-primary text-sm">Última Leitura de Radar</div>
            <div className="text-xs text-muted-foreground">Módulo 2-C · Radar de Proximidade</div>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-3">
          {dirs.map(({ icon, label, val }) => {
            const metros = parseFloat(val ?? 0);
            const alertar = metros < 0.5;
            return (
              <div
                key={label}
                className={cn(
                  "flex items-center gap-2.5 p-3 rounded-xl",
                  alertar ? "bg-red-50 border border-red-200" : "bg-secondary/50"
                )}
              >
                <span className={alertar ? "text-red-500" : "text-muted-foreground"}>{icon}</span>
                <div>
                  <div className="text-xs text-muted-foreground">{label}</div>
                  <div className={cn("text-sm font-bold", alertar ? "text-red-600" : "text-primary")}>
                    {metros.toFixed(2)} m
                  </div>
                </div>
              </div>
            );
          })}
        </div>
        <div className="flex items-center gap-1.5 text-xs text-muted-foreground mt-3">
          <Clock size={12} />
          Registrado às {ts}
        </div>
      </div>
    </div>
  );
}

// ── Page ────────────────────────────────────────────────────────────────

export default function Sensores() {
  const { conectado } = useSistemaStatus();
  const {
    modulos,
    ultimaLeituraCorrente,
    ultimaLeituraRadar,
    lastUpdated,
    loading,
    erro,
    recarregar,
  } = useSensoresPage();

  const online = modulos.filter((m) => m.online).length;
  const offline = modulos.filter((m) => !m.online).length;

  const isSystemReallyOnline = conectado === true || online > 0;

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      <SideBar
        systemStatusCount={`${online} sensores ativos`}
        isOnline={isSystemReallyOnline}
      />

      <main className="flex-1 flex flex-col min-h-0">
        <DashboardHeader
          statusSlot={<StatusIndicator status={isSystemReallyOnline ? "connected" : "disconnected"} />}
          title="Sensores"
        />

        <div className="flex-1 overflow-auto p-6">
          {/* Title row */}
          <div className="flex items-center justify-between mb-1">
            <div className="flex items-center gap-2">
              <Cpu size={20} className="text-[#234a2b]" />
              <h2 className="text-lg font-semibold text-primary">Módulos e Conexões</h2>
              <ChevronRight size={16} className="text-muted-foreground" />
              <span className="text-sm text-muted-foreground">Bomba #1</span>
            </div>
            <button
              onClick={recarregar}
              className="flex items-center gap-2 text-xs text-muted-foreground hover:text-primary px-3 py-1.5 rounded-xl hover:bg-primary/5 border border-transparent hover:border-primary/10 transition-all duration-200"
            >
              <RefreshCw size={13} />
              Atualizar
            </button>
          </div>
          <p className="text-sm text-muted-foreground mb-6">
            Status em tempo real de todos os ESP e sensores conectados. Atualiza a cada 3s.
          </p>

          {/* Summary bar */}
          <div className="grid grid-cols-3 gap-4 mb-8">
            {[
              { label: "Total de Módulos", value: modulos.length, color: "text-primary",   bg: "bg-secondary/60" },
              { label: "Online",            value: online,          color: "text-green-600", bg: "bg-green-50 border border-green-200" },
              { label: "Offline",           value: offline,         color: "text-red-600",   bg: "bg-red-50 border border-red-200" },
            ].map(({ label, value, color, bg }) => (
              <div key={label} className={cn("rounded-2xl p-4 text-center", bg)}>
                <div className={cn("text-3xl font-bold", color)}>{loading ? "—" : value}</div>
                <div className="text-xs text-muted-foreground mt-1">{label}</div>
              </div>
            ))}
          </div>

          {/* Error */}
          {erro && (
            <div className="flex items-center gap-3 bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-xl mb-6 text-sm">
              <XCircle size={16} />
              {erro}
            </div>
          )}

          {/* ESP módulos grid */}
          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="bg-card border border-border rounded-2xl h-44 animate-pulse" />
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
              {modulos.map((m) => (
                <ModuloCard key={m.modulo} modulo={m} />
              ))}
              {modulos.length === 0 && (
                <div className="col-span-2 text-center py-12 text-muted-foreground text-sm">
                  Nenhum módulo detectado. Verifique a conexão MQTT.
                </div>
              )}
            </div>
          )}

          {/* Leituras recentes */}
          <div className="mb-4">
            <h3 className="font-semibold text-primary text-base mb-1">Leituras Recentes</h3>
            <p className="text-xs text-muted-foreground">Valores registrados pelos sensores analógicos</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <LeituraCorrenteCard leitura={ultimaLeituraCorrente} />
            <LeituraRadarCard leitura={ultimaLeituraRadar} />
          </div>

          {/* Update footer */}
          {lastUpdated && (
            <div className="flex items-center justify-end gap-1.5 mt-6 text-xs text-muted-foreground">
              <Clock size={11} />
              Última atualização: {formatTs(lastUpdated)}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
