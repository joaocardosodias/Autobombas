import { cn } from "@/lib/utils";
import { Zap, TrendingUp, AlertTriangle } from "lucide-react"
import { useState, useEffect } from "react";

export function AmperageMeter({ currentValue, maxValue}) {
  const [animated, setAnimated] = useState(0);

  useEffect(() => {
    const t = setTimeout(() => setAnimated(currentValue), 100);
    return () => clearTimeout(t);
  }, [currentValue]);

  const percentage = Math.min(100, (animated / maxValue) * 100);
  const angle = -90 + (percentage * 180) / 100;

  const gaugeColor =
    percentage < 50 ? "#22c55e" : percentage < 75 ? "#eab308" : "#ef4444";

  const status =
    percentage < 50
      ? { text: "Normal", style: "bg-green-500/10 text-green-600" }
      : percentage < 75
        ? { text: "Elevado", style: "bg-yellow-500/10 text-yellow-600" }
        : { text: "Crítico", style: "bg-red-500/10 text-red-600" };

  // Marcações do arco
  const ticks = [];
  for (let i = 0; i <= 10; i++) {
    const tickAngle = -162 + i * 18;
    const isMain = i % 2 === 0;
    // const r1 = isMain ? 58 : 62;
    // const r2 = 68;
    const rad = (tickAngle * Math.PI) / 180;
    // const x1 = 50 + r1 * Math.cos(rad);
    // const y1 = 50 + r1 * Math.sin(rad);
    // const x2 = 50 + r2 * Math.cos(rad);
    // const y2 = 50 + r2 * Math.sin(rad);

    if (isMain) {
      const lr = 48;
      const lx = 50 + lr * Math.cos(rad);
      const ly = 50 + lr * Math.sin(rad);
      ticks.push(
        <text
          key={`l-${i}`}
          x={lx}
          y={ly}
          textAnchor="middle"
          dominantBaseline="middle"
          fontSize="5"
          className="fill-muted-foreground font-medium"
        >
          {Math.round((i / 10) * maxValue)}
        </text>,
      );
    }
  }

  return (
    <div className="bg-card rounded-2xl p-5 shadow-sm border border-primary/10 h-full flex flex-col">
      {/* Header */}
      
      <div className="flex items-center justify-center gap-2 mb-4 pb-3 border-b border-primary/10">
        <div>
          <h3 className="text-lg font-manrope font-semibold text-[#234a2b]">Amperagem</h3>
        </div>
      </div>
     {/* Gauge SVG */}
     <div className="flex-1 flex flex-col justify-center">
      <div className="relative mx-auto w-44">
        <svg viewBox="0 0 100 58" className="w-full">
          {/* Trilho de fundo */}
          <path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" className="stroke-secondary" strokeWidth="10" strokeLinecap="round" />
          {/* Zonas */}
          <path d="M 10 50 A 40 40 0 0 1 50 10"   fill="none" stroke="#22c55e" strokeWidth="10" strokeLinecap="round" opacity="0.2" />
          <path d="M 50 10 A 40 40 0 0 1 75 20"   fill="none" stroke="#eab308" strokeWidth="10" opacity="0.2" />
          <path d="M 75 20 A 40 40 0 0 1 90 50"   fill="none" stroke="#ef4444" strokeWidth="10" strokeLinecap="round" opacity="0.2" />
          {/* Progresso */}
          <path
            d="M 10 50 A 40 40 0 0 1 90 50"
            fill="none"
            stroke={gaugeColor}
            strokeWidth="10"
            strokeLinecap="round"
            strokeDasharray={`${(percentage / 100) * 125.6} 125.6`}
            className="transition-all duration-700 ease-out"
          />
          {ticks}
          {/* Ponteiro */}
          <g
            className="transition-transform duration-700 ease-out"
            style={{ transformOrigin: "50px 50px", transform: `rotate(${angle}deg)` }}
          >
            <line x1="50" y1="50" x2="50" y2="20" className="stroke-primary" strokeWidth="2.5" strokeLinecap="round" />
            <circle cx="50" cy="50" r="5" className="fill-primary" />
            <circle cx="50" cy="50" r="2" className="fill-card" />
          </g>
        </svg>
      </div>

      {/* Valor */}
      <div className="text-center mt-2">
        <div className="flex items-baseline justify-center gap-1">
          <span className="text-3xl font-bold text-primary tracking-tight">
            {animated.toFixed(1)}
          </span>
          <span className="text-lg text-muted-foreground">A</span>
        </div>
        <p className="text-xs text-muted-foreground mt-0.5">de {maxValue}A máximo</p>
      </div>
    </div>
      {/* Status */}
      <div className="mt-auto pt-3 border-t border-primary/10">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5">
            {percentage >= 75 ? (
              <AlertTriangle className="w-3.5 h-3.5 text-red-500" />
            ) : (
              <TrendingUp className="w-3.5 h-3.5 text-muted-foreground" />
            )}
            <span className="text-xs text-muted-foreground">Status</span>
          </div>
          <span className={cn("text-xs font-medium px-2 py-0.5 rounded-full", status.style)}>
            {status.text}
          </span>
        </div>
      </div>
    </div>
  );
}
