import { cn } from "@/lib/utils";
import {
  ChevronUp,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  Square,
  Power,
} from "lucide-react";

/**
 * DirectionalControl — controle direcional em cruz.
 *
 * @param {object}   props
 * @param {Function} props.onForward   — mover para frente
 * @param {Function} props.onBackward  — mover para trás
 * @param {Function} props.onLeft      — mover para esquerda
 * @param {Function} props.onRight     — mover para direita
 * @param {Function} props.onStop      — parar movimento
 */

export function DirectionalControl({
  onForward,
  onBackward,
  onLeft,
  onRight,
  onStop,
  onTogglePower,
  isPowerOn,
}) {
  const btnBase =
    "w-12 h-12 rounded-xl flex items-center justify-center transition-all duration-200 shadow-sm hover:shadow-md active:scale-95";
  const btnPrimary = cn(
    btnBase,
    "bg-secondary border-2 border-primary/20 text-primary",
    isPowerOn
    ? "hover:bg-primary hover:text-primary-foreground hover:border-primary cursor-pointer"
    : "opacity-40 cursor-not-allowed"
  );
  const btnStop = cn(
    btnBase,
    "bg-accent/20 border-2 border-accent/30 text-accent-foreground",
    isPowerOn ? "hover:bg-accent hover:border-accent" : "opacity-40 cursor-not-allowed"
  );

  return (
    <div className="bg-card rounded-2xl p-5 shadow-sm border border-primary/10 h-full flex flex-col">
      {/* Header com o botao de Power */}
      <div className="flex items-center justify-center gap-2 mb-4 pb-3 border-b border-primary/10">
          <h3 className="text-lg font-manrope font-semibold text-[#234a2b]">
            Controle Direcional
          </h3>
          {/* Botao de Power */}
          <button
          onClick={onTogglePower}
          className={cn(
            "p-2 rounded-lg border transition-all duration-300",
            isPowerOn 
              ? "bg-emerald-500/10 border-emerald-500/50 text-emerald-600" 
              : "bg-red-500/10 border-red-500/50 text-red-600"
          )}
          title={isPowerOn ? "Desativar Motores" : "Ativar Motores"}
          >
            <Power size={18} strokeWidth={2.5} className={isPowerOn ? "animate-pulse" : ""} />
          </button>
      </div>
      {/* Cruz direcional */}
      <div className="flex flex-col mt-4 items-center justify-center gap-2">
        <button
          onClick={onForward}
          className={btnPrimary}
          aria-label="Mover para frente"
        >
          <ChevronUp size={24} strokeWidth={2.5} />
        </button>
        <div className="flex items-center gap-2">
          <button
            onClick={onLeft}
            className={btnPrimary}
            aria-label="Mover para esquerda"
          >
            <ChevronLeft size={24} strokeWidth={2.5} />
          </button>
          <button
            onClick={onStop}
            className={btnStop}
            aria-label="Parar movimento"
          >
            <Square size={16} strokeWidth={2.5} />
          </button>
          <button
            onClick={onRight}
            className={btnPrimary}
            aria-label="Mover para direita"
          >
            <ChevronRight size={24} strokeWidth={2.5} />
          </button>
        </div>
        <button
          onClick={onBackward}
          className={btnPrimary}
          aria-label="Mover para trás"
        >
          <ChevronDown size={24} strokeWidth={2.5} />
        </button>
      </div>
      <div className="mt-auto pt-3 border-t border-primary/10 text-center">
        <span className={cn(
          "text-xs font-medium transition-colors",
          isPowerOn ? "text-emerald-600" : "text-red-500"
        )}>
          {isPowerOn ? "● Sistema Pronto" : "○ Sistema Travado"}
        </span>
      </div>
    </div>
  );
}
