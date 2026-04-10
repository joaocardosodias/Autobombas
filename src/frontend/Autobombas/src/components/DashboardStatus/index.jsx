import { Wifi, WifiOff, AlertTriangle } from "lucide-react";
import { cn } from "@/lib/utils";

const config = {
  connected: {
    border: "border-green-500",
    bg: "bg-green-500",
    Icon: Wifi,
    label: "Conectado",
    labelColor: "text-green-600",
  },
  disconnected: {
    border: "border-red-500",
    bg: "bg-red-500",
    Icon: WifiOff,
    label: "Desconectado",
    labelColor: "text-red-600",
  },
  warning: {
    border: "border-yellow-500",
    bg: "bg-yellow-500",
    Icon: AlertTriangle,
    label: "Atenção",
    labelColor: "text-yellow-600",
  },
};

export function StatusIndicator({ status }) {
  const { border, bg, label, labelColor } =
    config[status] || config.connected;
  return (
    <div className="flex items-center gap-3 bg-card/80 backdrop-blur-sm px-4 py-2 rounded-full border border-primary/10 shadow-sm">
      <div
        className={cn(
          "relative w-10 h-10 rounded-full border-[3px] flex items-center justify-center",
          border,
        )}
      >
        <div className={cn("w-4 h-4 rounded-full animate-pulse", bg)} />
        <div
          className={cn(
            "absolute inset-0 rounded-full border-2 animate-ping opacity-30",
            border,
          )}
        />
      </div>
          <div className="pr-2">
            <p className={cn("text-sm font-medium", labelColor)}> 
                {label}
            </p>
            <p className="text-xs text-muted-foreground">
                Sistema
            </p>
          </div>
    </div>
  );
}
