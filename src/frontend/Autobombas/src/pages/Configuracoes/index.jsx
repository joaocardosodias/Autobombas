import { SideBar } from "@/components/Sidebar";
import { DashboardHeader } from "@/components/DashboardHeader";
import { StatusIndicator } from "@/components/DashboardStatus";
import { SensorsPanel } from "@/components/SensorsPanel";
import { useDashboardMonitor } from "@/hooks/useDashboardMonitor"; 
import { useConfiguracoes } from "@/hooks/useConfiguracoes";
import { useState, useEffect } from "react";
import {
  Settings,
  Zap,
  Ruler,
  ArrowDown,
  ArrowUp,
  Navigation,
  Save,
  RotateCcw,
  CheckCircle,
  AlertCircle,
  Loader2,
  ChevronRight,
} from "lucide-react";
import { cn } from "@/lib/utils";

// ── Helpers ────────────────────────────────────────────────────────

function InputField({ label, value, onChange, unit, min, max, step = "0.01", description }) {
  return (
    <div className="space-y-1.5">
      <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
        {label}
      </label>
      <div className="relative">
        <input
          type="number"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          min={min}
          max={max}
          step={step}
          className={cn(
            "w-full bg-background border border-border rounded-xl px-4 py-3 text-sm font-medium",
            "text-primary placeholder:text-muted-foreground/50",
            "focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary/50",
            "transition-all duration-200",
            unit && "pr-14"
          )}
        />
        {unit && (
          <span className="absolute right-4 top-1/2 -translate-y-1/2 text-xs text-muted-foreground font-medium">
            {unit}
          </span>
        )}
      </div>
      {description && (
        <p className="text-xs text-muted-foreground/70">{description}</p>
      )}
    </div>
  );
}

function SectionCard({ title, subtitle, accent = "green", icon: Icon, children }) {
  const accentClasses = {
    green:  { bar: "bg-[#234a2b]", badge: "bg-[#234a2b]/10 text-[#234a2b]" },
    yellow: { bar: "bg-[#e4bc34]", badge: "bg-[#e4bc34]/10 text-[#b08d00]" },
    blue:   { bar: "bg-blue-500",  badge: "bg-blue-500/10 text-blue-600"   },
    red:    { bar: "bg-red-500",   badge: "bg-red-500/10 text-red-600"     },
  };
  const cls = accentClasses[accent] || accentClasses.green;

  return (
    <div className="bg-card border border-border rounded-2xl overflow-hidden shadow-sm hover:shadow-md transition-shadow duration-200">
      <div className={cn("h-1 w-full", cls.bar)} />
      <div className="p-6">
        <div className="flex items-start gap-4 mb-6">
          <div className={cn("p-2.5 rounded-xl", cls.badge)}>
            {Icon && <Icon size={20} />} 
          </div>
          <div>
            <h3 className="font-semibold text-primary text-base">{title}</h3>
            {subtitle && <p className="text-xs text-muted-foreground mt-0.5">{subtitle}</p>}
          </div>
        </div>
        <div className="space-y-4">{children}</div>
      </div>
    </div>
  );
}

function ProximityRow({ direcao, label, value, onChange }) {
  const icons = {
    frente: "▲",
    tras:   "▼",
    esq:    "◄",
    dir:    "►",
  };
  return (
    <div className="flex items-center gap-4">
      <div className="flex items-center gap-2 w-24 shrink-0">
        <span className="text-base">{icons[direcao]}</span>
        <span className="text-sm font-medium text-primary">{label}</span>
      </div>
      <div className="relative flex-1">
        <input
          type="number"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          min={0.05}
          max={5}
          step={0.05}
          className={cn(
            "w-full bg-background border border-border rounded-xl px-4 py-2.5 text-sm font-medium pr-10",
            "text-primary focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary/50",
            "transition-all duration-200"
          )}
        />
        <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-muted-foreground">m</span>
      </div>
    </div>
  );
}

// ── Page ────────────────────────────────────────────────────────────

export default function Configuracoes() {
  const { sensorsList, isSystemOnline, lastUpdated, activeSensorsCount } = useDashboardMonitor();
  const { config, loading, saving, erro, sucesso, salvar } = useConfiguracoes();

  const [isSensorOpen, setIsSensorOpen] = useState(false);

  const [diametro, setDiametro]   = useState("");
  const [corda, setCorda]         = useState("");
  const [inf, setInf]             = useState("");
  const [sup, setSup]             = useState("");
  const [passo, setPasso]         = useState("");
  const [proxFrente, setProxFrente] = useState("");
  const [proxTras, setProxTras]     = useState("");
  const [proxEsq, setProxEsq]       = useState("");
  const [proxDir, setProxDir]       = useState("");

  // Sync form with loaded config
  useEffect(() => {
    if (!config) return;
    setDiametro(config.diametro_carretel_cm ?? "");
    setCorda(config.comprimento_corda_cm ?? "");
    setInf(config.limite_inferior ?? "");
    setSup(config.limite_superior ?? "");
    setPasso(config.passo_auto_cm ?? "");
    setProxFrente(config.limite_prox_frente_m ?? "0.30");
    setProxTras(config.limite_prox_tras_m   ?? "0.30");
    setProxEsq(config.limite_prox_esq_m     ?? "0.30");
    setProxDir(config.limite_prox_dir_m     ?? "0.30");
  }, [config]);

  // Validation
  const bandaValida = !inf || !sup || parseFloat(sup) > parseFloat(inf);

  function handleSalvar() {
    if (!bandaValida) return;

    const payload = {};
    if (diametro) payload.diametro_carretel_cm = parseFloat(diametro);
    if (corda)    payload.comprimento_corda_cm  = parseFloat(corda);
    if (inf)      payload.limite_inferior        = parseFloat(inf);
    if (sup)      payload.limite_superior        = parseFloat(sup);
    if (passo)    payload.passo_auto_cm          = parseFloat(passo);
    if (proxFrente) payload.limite_prox_frente_m = parseFloat(proxFrente);
    if (proxTras)   payload.limite_prox_tras_m   = parseFloat(proxTras);
    if (proxEsq)    payload.limite_prox_esq_m    = parseFloat(proxEsq);
    if (proxDir)    payload.limite_prox_dir_m    = parseFloat(proxDir);

    salvar(payload);
  }

  function handleReset() {
    if (!config) return;
    setDiametro(config.diametro_carretel_cm ?? "");
    setCorda(config.comprimento_corda_cm ?? "");
    setInf(config.limite_inferior ?? "");
    setSup(config.limite_superior ?? "");
    setPasso(config.passo_auto_cm ?? "");
    setProxFrente(config.limite_prox_frente_m ?? "0.30");
    setProxTras(config.limite_prox_tras_m   ?? "0.30");
    setProxEsq(config.limite_prox_esq_m     ?? "0.30");
    setProxDir(config.limite_prox_dir_m     ?? "0.30");
  }

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      <SideBar
        onSensorsClick={() => setIsSensorOpen(true)} // AJUSTE: Função que abre o painel
        systemStatusCount={`${activeSensorsCount ?? 0} sensores ativos`} // AJUSTE: Variável do hook novo
        isOnline={isSystemOnline} // AJUSTE: Variável do hook novo
      />

      <main className="flex-1 flex flex-col min-h-0">
        <DashboardHeader
          statusSlot={<StatusIndicator status={isSystemOnline ? "connected" : "disconnected"} />} // AJUSTE: Hook novo
          title="Configurações"
        />

        <div className="flex-1 overflow-auto p-6">
          {/* Page title */}
          <div className="flex items-center gap-2 mb-1">
            <Settings size={20} className="text-[#234a2b]" />
            <h2 className="text-lg font-semibold text-primary">Configurações da Bomba</h2>
            <ChevronRight size={16} className="text-muted-foreground" />
            <span className="text-sm text-muted-foreground">Bomba #1</span>
          </div>
          <p className="text-sm text-muted-foreground mb-8">
            Ajuste os parâmetros operacionais de hardware e segurança do sistema.
          </p>

          {/* Loading skeleton */}
          {loading && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="bg-card border border-border rounded-2xl h-52 animate-pulse" />
              ))}
            </div>
          )}

          {!loading && (
            <>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                {/* Hardware */}
                <SectionCard
                  icon={Ruler}
                  title="Hardware da Bomba"
                  subtitle="Dimensões físicas do sistema de içamento"
                  accent="green"
                >
                  <InputField
                    label="Diâmetro do Carretel"
                    value={diametro}
                    onChange={setDiametro}
                    unit="cm"
                    min={0.1}
                    max={100}
                    description="Diâmetro externo do carretel de enrolamento da corda."
                  />
                  <InputField
                    label="Comprimento da Corda"
                    value={corda}
                    onChange={setCorda}
                    unit="cm"
                    min={1}
                    max={10000}
                    description="Comprimento total da corda — define a profundidade máxima."
                  />
                </SectionCard>

                {/* Corrente */}
                <SectionCard
                  icon={Zap}
                  title="Banda de Corrente"
                  subtitle="Limites para controle automático de dragagem"
                  accent="yellow"
                >
                  <InputField
                    label="Limite Inferior"
                    value={inf}
                    onChange={setInf}
                    unit="A"
                    min={0}
                    step="0.001"
                    description="Corrente mínima — abaixo disso, a bomba desce automaticamente."
                  />
                  <InputField
                    label="Limite Superior"
                    value={sup}
                    onChange={setSup}
                    unit="A"
                    min={0}
                    step="0.001"
                    description="Corrente máxima — acima disso, a bomba sobe de volta."
                  />
                  {!bandaValida && (
                    <div className="flex items-center gap-2 bg-red-50 border border-red-200 text-red-600 text-xs px-3 py-2 rounded-xl">
                      <AlertCircle size={14} />
                      Limite superior deve ser maior que o inferior.
                    </div>
                  )}
                </SectionCard>

                {/* Modo automático */}
                <SectionCard
                  icon={ArrowDown}
                  title="Modo Automático"
                  subtitle="Parâmetros do ciclo de descida automática"
                  accent="blue"
                >
                  <InputField
                    label="Passo de Descida"
                    value={passo}
                    onChange={setPasso}
                    unit="cm"
                    min={0.1}
                    max={100}
                    step="0.1"
                    description="Distância a descer por iteração quando a corrente está abaixo do limite inferior."
                  />
                </SectionCard>

                {/* Proximidade */}
                <SectionCard
                  icon={Navigation}
                  title="Limites de Proximidade"
                  subtitle="Distância mínima segura por direção (Módulo 2-C)"
                  accent="red"
                >
                  <div className="space-y-3">
                    <ProximityRow direcao="frente" label="Frente"    value={proxFrente} onChange={setProxFrente} />
                    <ProximityRow direcao="tras"   label="Trás"      value={proxTras}   onChange={setProxTras}   />
                    <ProximityRow direcao="esq"    label="Esquerda"  value={proxEsq}    onChange={setProxEsq}    />
                    <ProximityRow direcao="dir"    label="Direita"   value={proxDir}    onChange={setProxDir}    />
                  </div>
                  <p className="text-xs text-muted-foreground/70 mt-1">
                    Abaixo desta distância a balsa será bloqueada nessa direção.
                  </p>
                </SectionCard>
              </div>

              {/* Feedback banner */}
              {sucesso && (
                <div className="flex items-center gap-3 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-xl mb-6 animate-in fade-in slide-in-from-top-1 duration-300">
                  <CheckCircle size={18} />
                  <span className="text-sm font-medium">Configurações salvas com sucesso!</span>
                </div>
              )}
              {erro && (
                <div className="flex items-center gap-3 bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-xl mb-6">
                  <AlertCircle size={18} />
                  <span className="text-sm font-medium">{erro}</span>
                </div>
              )}

              {/* Actions */}
              <div className="flex items-center justify-end gap-3">
                <button
                  onClick={handleReset}
                  disabled={saving}
                  className={cn(
                    "flex items-center gap-2 px-5 py-2.5 rounded-xl border border-border text-sm font-medium",
                    "text-muted-foreground hover:text-primary hover:bg-primary/5 hover:border-primary/20",
                    "transition-all duration-200 disabled:opacity-50"
                  )}
                >
                  <RotateCcw size={16} />
                  Descartar
                </button>
                <button
                  onClick={handleSalvar}
                  disabled={saving || !bandaValida}
                  className={cn(
                    "flex items-center gap-2 px-6 py-2.5 rounded-xl text-sm font-semibold",
                    "bg-[#234a2b] text-white hover:bg-[#1a3820]",
                    "shadow-md hover:shadow-lg transition-all duration-200",
                    "disabled:opacity-50 disabled:cursor-not-allowed"
                  )}
                >
                  {saving ? (
                    <Loader2 size={16} className="animate-spin" />
                  ) : (
                    <Save size={16} />
                  )}
                  {saving ? "Salvando…" : "Salvar Configurações"}
                </button>
              </div>
            </>
          )}
        </div>
      </main>

      <SensorsPanel
        isOpen={isSensorOpen}
        onClickClose={() => setIsSensorOpen(false)}
        sensors={sensorsList}
        lastUpdated={lastUpdated}
      />
    </div>
  );
}