import { cn } from "@/lib/utils";
import { ArrowDown, ArrowUp, Loader2 } from "lucide-react";
import { useState } from "react";

export function DephControl({ depth_cm = 0, maxDepth = null, onDeslocar, isMoving }) {
  const [inputCm, setInputCm] = useState("5");

  const temLimite   = maxDepth != null && maxDepth > 0;
  const depthPct    = temLimite ? Math.min(100, Math.max(0, (depth_cm / maxDepth) * 100)) : 0;
  const restante    = temLimite ? Math.max(0, maxDepth - depth_cm) : Infinity;
  const inputVal    = parseFloat(inputCm) || 0;
  const excedido    = temLimite && inputVal > restante;
  const excedidoSubir = inputVal > depth_cm

  function handleDescer() {
    if (excedido || isMoving) return;
    const val = parseFloat(inputCm);
    if (!isNaN(val) && val > 0) onDeslocar?.(val);
  }
  function handleSubir() {
    if (excedidoSubir || isMoving) return;
    const val = parseFloat(inputCm);
    if (!isNaN(val) && val > 0) onDeslocar?.(-val);
  }

  // Cores dinâmicas pelo nível de profundidade
  const waterColor  = depthPct < 30  ? "#22c55e"   // verde raso
    : depthPct < 65 ? "#f59e0b"  // amarelo médio
    : "#ef4444";                 // vermelho profundo


  return (
    <div className={cn(
      "bg-card rounded-2xl border shadow-sm h-full flex flex-col overflow-hidden relative transition-colors duration-300",
      isMoving ? "border-blue-500/50" : "border-primary/10"
    )}>

      
      <div className={cn(
        "w-full bg-[#234a2b] text-white text-xs font-semibold flex items-center justify-center gap-2 overflow-hidden transition-all duration-300",
        isMoving ? "py-1.5 opacity-100" : "h-0 opacity-0"
      )}>
        <Loader2 size={12} className="animate-spin" />
        Motor em movimento...
      </div>

      <div className="p-5 flex flex-col flex-1 gap-4">

        {/* Header */}
        <div className="flex items-center justify-center gap-2 mb-4 pb-3 border-b border-primary/10">
          <div>
            <h3 className="text-lg font-manrope font-semibold text-[#234a2b]">Controle de Profundidade</h3>
          </div>
        </div>

        {/* ── Visualização central ─────────────────── */}
        <div className="flex gap-4 flex-1 min-h-0">

          {/* Poço animado (Mantido intacto!) */}
          <div className="relative shrink-0" style={{ width: 56 }}>
            {/* Parede do poço */}
            <div
              className="absolute inset-0 rounded-2xl border-2 border-primary/15 overflow-hidden"
              style={{ background: "rgba(0,0,0,0.03)" }}
            >
              {/* Rope fill */}
              <div
                className="absolute top-0 left-0 right-0 transition-all duration-700 ease-in-out"
                style={{
                  height: `${depthPct}%`,
                  background: `linear-gradient(180deg, ${waterColor}99 0%, ${waterColor}55 100%)`,
                }}
              >
                {/* Ondulação na borda inferior */}
                {depthPct > 2 && depthPct < 99 && (
                  <div
                    className="absolute bottom-0 left-0 right-0"
                    style={{ height: 6, overflow: "hidden" }}
                  >
                    <svg viewBox="0 0 56 6" preserveAspectRatio="none" width="100%" height="6">
                      <path
                        d="M0 3 Q14 6 28 3 Q42 0 56 3 L56 6 L0 6 Z"
                        fill={waterColor}
                        opacity="0.4"
                      >
                        <animateTransform
                          attributeName="transform"
                          type="translate"
                          from="-56 0"
                          to="0 0"
                          dur="2s"
                          repeatCount="indefinite"
                        />
                      </path>
                    </svg>
                  </div>
                )}
              </div>

              {/* Corda / cabo */}
              <div
                className="absolute left-1/2 -translate-x-1/2 top-0 transition-all duration-700 ease-in-out"
                style={{
                  width: 3,
                  height: `${depthPct}%`,
                  background: "repeating-linear-gradient(180deg, #78716c 0px, #a8a29e 4px, #78716c 8px)",
                  borderRadius: 2,
                }}
              />

              {/* Bomba no final da corda */}
              <div
                className={cn(
                  "absolute left-1/2 -translate-x-1/2 transition-all duration-700 ease-in-out flex items-center justify-center",
                  isMoving && "animate-pulse" 
                )}
                style={{
                  top: `calc(${depthPct}% - 10px)`,
                  width: 28,
                  height: 20,
                  background: "#234a2b",
                  borderRadius: 6,
                  zIndex: 10,
                  boxShadow: "0 2px 8px rgba(0,0,0,0.3)",
                }}
              >
                <div style={{ width: 10, height: 10, background: "#86efac", borderRadius: "50%" }} />
              </div>

              {/* Marcas de escala */}
              {[25, 50, 75].map(pct => (
                <div
                  key={pct}
                  className="absolute left-0 right-0"
                  style={{ bottom: `${pct}%`, height: 1, background: "rgba(0,0,0,0.07)" }}
                />
              ))}
            </div>

            {/* Cabeça do poço */}
            <div
              className="absolute -top-1 left-1/2 -translate-x-1/2 rounded-sm"
              style={{ width: 40, height: 6, background: "#234a2b", borderRadius: 3 }}
            />
          </div>

          {/* Dados numéricos à direita da visualização */}
          <div className="flex flex-col justify-between flex-1 py-0.5">
            <span className="text-xs text-muted-foreground">0 cm</span>

            <div className="text-center">
              <div className={cn(
                "text-4xl font-light tabular-nums transition-opacity",
                isMoving && "opacity-60" 
              )} style={{ color: waterColor }}>
                {Math.round(depth_cm)}
              </div>
              <div className="text-xs text-muted-foreground">cm atual</div>

              {temLimite && (
                <div className="mt-2 space-y-0.5">
                  <div className="text-xs text-muted-foreground">
                    Máx: <span className="font-semibold text-primary">{maxDepth} cm</span>
                  </div>
                  <div className="text-xs text-muted-foreground">
                    Disponível:{" "}
                    <span className={cn("font-semibold", restante <= 0 ? "text-red-500" : "text-primary")}>
                      {restante.toFixed(0)} cm
                    </span>
                  </div>
                </div>
              )}
            </div>

            <span className="text-xs text-muted-foreground text-right">
              {temLimite ? `${maxDepth} cm` : <span className="italic">Sem limite</span>}
            </span>
          </div>
        </div>

        {/* ── Controles ─────────────────────────────── */}
        <div className="space-y-3 pt-1 border-t border-primary/8 mt-4">
          
          <div className="flex items-center gap-2">
            <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider whitespace-nowrap">
              Deslocar
            </label>
            <div className="relative flex-1">
              <input
                type="number"
                min={1}
                max={temLimite ? Math.max(0, restante) : undefined}
                step={1}
                value={inputCm}
                onChange={(e) => setInputCm(e.target.value)}
                disabled={isMoving} 
                className={cn(
                  "w-full bg-background border rounded-xl px-3 py-2 text-sm font-medium pr-9",
                  "focus:outline-none focus:ring-2 transition-all duration-200",
                  "disabled:opacity-50 disabled:bg-slate-50 disabled:cursor-not-allowed", 
                  excedido && !isMoving
                    ? "border-red-300 focus:ring-red-200 text-red-600"
                    : "border-border focus:ring-[#234a2b]/30 focus:border-[#234a2b]/50"
                )}
              />
              <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-muted-foreground">cm</span>
            </div>
          </div>
          {excedido && !isMoving && (
            <p className="text-xs text-red-500"> Excede {restante.toFixed(0)} cm disponíveis</p>
          )}

          {/* Botões */}
          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={handleSubir}
              disabled={excedidoSubir || depth_cm <= 0 || isMoving} 
              className={cn(
                "flex items-center justify-center gap-1.5 py-2 rounded-xl border-2 text-sm font-semibold transition-all duration-150",
                excedidoSubir || depth_cm <= 0 || isMoving
                ? "border-primary/20 bg-secondary text-primary/50 cursor-not-allowed" 
                : "hover:bg-primary/5 hover:border-primary/30 active:scale-95"
              )}
            >
              <ArrowUp size={15} strokeWidth={2.5} />
              Subir
            </button>
            <button
              onClick={handleDescer}
              disabled={excedido || (temLimite && restante <= 0) || isMoving} 
              className={cn(
                "flex items-center justify-center gap-1.5 py-2 rounded-xl border-2 text-sm font-semibold transition-all duration-150",
                excedido || (temLimite && restante <= 0) || isMoving
                  ? "border-primary/20 bg-secondary text-primary/50 cursor-not-allowed" 
                  : "border-[#234a2b]/30 bg-[#234a2b]/5 text-[#234a2b] hover:bg-[#234a2b]/10 hover:border-[#234a2b]/50 active:scale-95"
              )}
            >
              <ArrowDown size={15} strokeWidth={2.5} />
              Descer
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}
