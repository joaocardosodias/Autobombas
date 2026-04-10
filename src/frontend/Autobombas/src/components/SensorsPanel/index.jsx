import { cn } from "@/lib/utils";
import { X, CheckCircle2, AlertCircle, XCircle, Cpu } from "lucide-react";

const STATUS_CONFIG = {
  online: {
    color: "text-green-600",
    bg: "bg-green-500/10",
    Icon: CheckCircle2,
    label: "Operante",
  },
  warning: {
    color: "text-yellow-600",
    bg: "bg-yellow-500/10",
    Icon: AlertCircle,
    label: "Atenção",
  },
  offline: {
    color: "text-red-600",
    bg: "bg-red-500/10",
    Icon: XCircle,
    label: "Offline",
  },
};

/**
 * SensorsPanel — painel lateral com lista de sensores e componentes.
 *
 * @param {object}   props
 * @param {boolean}  props.isOpen      — controla visibilidade do painel
 * @param {Function} props.onClose     — chamado ao fechar
 * @param {Array}    props.sensors     — lista de sensores
 * @param {string}   props.lastUpdated — texto de última atualização (ex: "há 2s")
 *
 * Estrutura esperada de cada sensor:
 * { id, name, type, status: "online"|"warning"|"offline", value?: string, icon: ReactNode }
 */

export function SensorsPanel({
  isOpen,
  onClickClose,
  sensors = [],
  lastUpdated = "agora",
}) {
  if (!isOpen) return null;

  const getSafeStatus = (status) => {
    const s = status?.toLowerCase();
    return STATUS_CONFIG[s] ? s : "offline";
  }

  const counts = sensors.reduce(
    (acc, s) => {
      const safeStatus = getSafeStatus(s.status);
      acc[safeStatus] = (acc[safeStatus] || 0) + 1;
      return acc;
    },
    { online: 0, warning: 0, offline: 0 },
  );

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-end">
      <div className="h-full w-full max-w-lg bg-card shadow-2xl flex flex-col animate-in slide-in-from-right duration-300">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-primary/10 shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
              <Cpu className="w-5 h-5 text-primary" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-primary">
                Sensores e Componentes
              </h2>
              <p className="text-sm text-muted-foreground">
                {sensors.length} dispositivos monitorados
              </p>
            </div>
          </div>
          <button
            onClick={onClickClose}
            className="p-2 rounded-xl hover:bg-secondary transition-colors text-muted-foreground hover:text-primary"
            aria-label="Fechar painel de sensores"
          >
            <X size={20} />
          </button>
        </div>
        {/* Resumo */}
        <div className="p-6 border-b border-primary/10 bg-secondary/30 shrink-0">
          <div className="grid grid-cols-3 gap-4">
            {[
              { key: "online", label: "Online", valueColor: "text-green-600" },
              {
                key: "warning",
                label: "Atenção",
                valueColor: "text-yellow-600",
              },
              { key: "offline", label: "Offline", valueColor: "text-red-600" },
            ].map(({ key, label, valueColor }) => (
              <div
                key={key}
                className="text-center p-3 bg-card rounded-xl border border-primary/5"
              >
                <div className={cn("text-2xl font-bold", valueColor)}>
                  {counts[key]}
                </div>
                <div className="text-xs text-muted-foreground mt-1">
                  {label}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Lista */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="space-y-3">
            {sensors.map((sensor) => {
              const safeStatus = getSafeStatus(sensor.status)
              const cfg = STATUS_CONFIG[safeStatus]
              const StatusIcon = cfg.Icon;

              const hasValue = sensor.value !== undefined && sensor.value !== null && sensor.value !== "";

              return (
                <div
                  key={sensor.id}
                  className="flex items-center gap-4 p-4 bg-secondary/50 rounded-xl border border-primary/5 hover:border-primary/20 transition-colors"
                >
                  <div
                    className={cn(
                      "w-10 h-10 rounded-xl flex items-center justify-center",
                      cfg.bg,
                    )}
                  >
                    <span className={cfg.color}>{sensor.icon}</span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-primary text-sm truncate">
                        {sensor.name}
                      </span>
                      <StatusIcon size={14} className={cfg.color} />
                    </div>
                    <span className="text-xs text-muted-foreground">
                      {sensor.type}
                    </span>
                  </div>
                  <div className="text-right shrink-0">
                    <div className={cn("text-xs font-medium", cfg.color)}>
                      {cfg.label}
                    </div>
                    {hasValue && (
                      <div className="text-sm font-semibold text-primary mt-0.5">
                        {sensor.value}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}

            {sensors.length === 0 && (
              <p className="text-center text-sm text-muted-foreground py-8">
                Nenhum sensor conectado.
              </p>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-primary/10 bg-card shrink-0">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              <span className="text-sm font-medium text-green-600">
                Sistema Operacional
              </span>
            </div>
            <span className="text-xs text-muted-foreground">
              Última atualização: {lastUpdated}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
